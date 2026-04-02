import json
import logging
import base64
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

import aiohttp

logger = logging.getLogger(__name__)

BASE_URL = "https://api.vrchat.cloud/api/1"
COOKIE_FILE = Path("data/vrchat_cookies.json")
FRIENDS_CACHE_FILE = Path("data/vrchat_friends.json")
FRIENDS_CACHE_MAX_AGE_HOURS = 4
USER_AGENT = "NOVA-AI/1.0"


def _generate_totp(secret: str) -> str:
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.now()
    except ImportError:
        logger.error("pyotp not installed -- run: pip install pyotp")
        return ""
    except Exception as e:
        logger.error(f"Failed to generate TOTP code: {e}")
        return ""


class VRChatAPI:
    def __init__(self, config):
        self._config = config
        self._auth_cookie = None
        self._twofa_cookie = None
        self._session = None
        self._logged_in = False
        self._user_id = None
        self._load_cookies()

    def _load_cookies(self):
        if COOKIE_FILE.exists():
            try:
                data = json.loads(COOKIE_FILE.read_text(encoding="utf-8"))
                self._auth_cookie = data.get("auth")
                self._twofa_cookie = data.get("twoFactorAuth")
                if self._auth_cookie:
                    logger.info("Loaded VRChat auth cookie from disk")
            except Exception as e:
                logger.warning(f"Failed to load VRChat cookies: {e}")

    def _save_cookies(self):
        COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if self._auth_cookie:
            data["auth"] = self._auth_cookie
        if self._twofa_cookie:
            data["twoFactorAuth"] = self._twofa_cookie
        COOKIE_FILE.write_text(json.dumps(data), encoding="utf-8")

    def _build_cookie_header(self):
        parts = []
        if self._auth_cookie:
            parts.append(f"auth={self._auth_cookie}")
        if self._twofa_cookie:
            parts.append(f"twoFactorAuth={self._twofa_cookie}")
        return "; ".join(parts)

    def _extract_cookies(self, response):
        for cookie_header in response.headers.getall("Set-Cookie", []):
            if cookie_header.startswith("auth="):
                val = cookie_header.split("auth=", 1)[1].split(";")[0]
                if val:
                    self._auth_cookie = val
            elif cookie_header.startswith("twoFactorAuth="):
                val = cookie_header.split("twoFactorAuth=", 1)[1].split(";")[0]
                if val:
                    self._twofa_cookie = val
        self._save_cookies()

    def _headers(self, with_auth_basic=False):
        h = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }
        cookie = self._build_cookie_header()
        if cookie:
            h["Cookie"] = cookie
        if with_auth_basic:
            username = self._config.get("vrchat_api", "username", default="")
            password = self._config.get("vrchat_api", "password", default="")
            if username and password:
                cred = f"{quote(username, safe='')}:{quote(password, safe='')}"
                token = base64.b64encode(cred.encode()).decode()
                h["Authorization"] = f"Basic {token}"
        return h

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def login(self):
        """Login or verify existing session. Returns user data or 2FA requirement."""
        session = await self._get_session()

        need_basic = not self._auth_cookie
        headers = self._headers(with_auth_basic=need_basic)

        async with session.get(f"{BASE_URL}/auth/user", headers=headers) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                if "requiresTwoFactorAuth" in data:
                    methods = data["requiresTwoFactorAuth"]
                    logger.info(f"VRChat 2FA required, methods: {methods}")
                    return {"needs_2fa": True, "methods": methods}
                self._logged_in = True
                self._user_id = data.get("id")
                logger.info(f"VRChat logged in as {data.get('displayName', '?')}")
                return {"logged_in": True, "user": data.get("displayName")}
            elif resp.status == 401:
                logger.error("VRChat login failed: invalid credentials")
                return {"error": "Invalid credentials"}
            else:
                text = await resp.text()
                logger.error(f"VRChat login failed: {resp.status} {text}")
                return {"error": f"HTTP {resp.status}"}

    async def verify_2fa(self, code: str):
        """Verify TOTP 2FA code."""
        session = await self._get_session()
        headers = self._headers()
        payload = {"code": code}

        async with session.post(
            f"{BASE_URL}/auth/twofactorauth/totp/verify",
            headers=headers,
            json=payload,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                if data.get("verified"):
                    logger.info("VRChat 2FA verified successfully")
                    self._logged_in = True
                    return {"verified": True}
            logger.error(f"VRChat 2FA verification failed: {resp.status}")
            return {"error": "2FA verification failed"}

    async def verify_2fa_email(self, code: str):
        """Verify email OTP 2FA code."""
        session = await self._get_session()
        headers = self._headers()
        payload = {"code": code}

        async with session.post(
            f"{BASE_URL}/auth/twofactorauth/emailotp/verify",
            headers=headers,
            json=payload,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                if data.get("verified"):
                    logger.info("VRChat email 2FA verified successfully")
                    self._logged_in = True
                    return {"verified": True}
            logger.error(f"VRChat email 2FA verification failed: {resp.status}")
            return {"error": "Email 2FA verification failed"}

    async def verify_auth_token(self):
        """Check if current auth cookie is still valid."""
        session = await self._get_session()
        headers = self._headers()

        async with session.get(f"{BASE_URL}/auth", headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("ok", False)
            return False

    async def ensure_logged_in(self):
        """Ensure we have a valid session. Login if needed, auto-handle 2FA."""
        if self._logged_in:
            return True

        if self._auth_cookie:
            valid = await self.verify_auth_token()
            if valid:
                self._logged_in = True
                await self._fetch_user_id()
                return True

        result = await self.login()
        if result.get("logged_in"):
            return True
        if result.get("needs_2fa"):
            totp_secret = self._config.get("vrchat_api", "totp_secret", default="")
            if totp_secret:
                code = _generate_totp(totp_secret)
                if code:
                    methods = result.get("methods", [])
                    if "totp" in methods:
                        verify_result = await self.verify_2fa(code)
                    elif "emailOtp" in methods:
                        logger.warning("Account uses email OTP -- totp_secret won't work for email codes")
                        return False
                    else:
                        verify_result = await self.verify_2fa(code)
                    if verify_result.get("verified"):
                        await self._fetch_user_id()
                        return True
                    logger.error("Auto 2FA verification failed")
                    return False
            logger.warning("VRChat requires 2FA but no totp_secret configured in config.yml")
            return False
        return False

    async def _fetch_user_id(self):
        """Fetch and cache the current user's ID if not already known."""
        if self._user_id:
            return
        session = await self._get_session()
        headers = self._headers()
        async with session.get(f"{BASE_URL}/auth/user", headers=headers) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                self._user_id = data.get("id")
                if self._user_id:
                    logger.info(f"Cached user ID: {self._user_id}")

    async def select_avatar(self, avatar_id: str):
        """Switch to an avatar by its ID."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API. Check username/password/totp_secret in config.yml"}

        session = await self._get_session()
        headers = self._headers()

        async with session.put(
            f"{BASE_URL}/avatars/{avatar_id}/select",
            headers=headers,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                new_avatar = data.get("currentAvatar", avatar_id)
                logger.info(f"VRChat avatar switched to {new_avatar}")
                return {"result": "ok", "avatar_id": new_avatar}
            elif resp.status == 401:
                self._logged_in = False
                logger.warning("VRChat auth expired, attempting re-login...")
                relogged = await self.ensure_logged_in()
                if relogged:
                    return await self._select_avatar_inner(avatar_id)
                return {"error": "Auth expired and re-login failed"}
            elif resp.status == 404:
                return {"error": f"Avatar '{avatar_id}' not found or not accessible"}
            else:
                text = await resp.text()
                return {"error": f"Failed to switch avatar: HTTP {resp.status} - {text}"}

    async def _select_avatar_inner(self, avatar_id: str):
        """Inner select_avatar call after re-login (avoids infinite recursion)."""
        session = await self._get_session()
        headers = self._headers()

        async with session.put(
            f"{BASE_URL}/avatars/{avatar_id}/select",
            headers=headers,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                data = await resp.json()
                new_avatar = data.get("currentAvatar", avatar_id)
                logger.info(f"VRChat avatar switched to {new_avatar}")
                return {"result": "ok", "avatar_id": new_avatar}
            elif resp.status == 404:
                return {"error": f"Avatar '{avatar_id}' not found or not accessible"}
            else:
                text = await resp.text()
                return {"error": f"Failed to switch avatar: HTTP {resp.status} - {text}"}

    async def get_current_user(self):
        """Get current user info including location/instance."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()

        async with session.get(f"{BASE_URL}/auth/user", headers=headers) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                self._logged_in = False
                relogged = await self.ensure_logged_in()
                if relogged:
                    async with session.get(f"{BASE_URL}/auth/user", headers=self._headers()) as resp2:
                        self._extract_cookies(resp2)
                        if resp2.status == 200:
                            return await resp2.json()
                return {"error": "Auth expired and re-login failed"}
            else:
                return {"error": f"Failed to get current user: HTTP {resp.status}"}

    async def get_instance(self, world_id: str, instance_id: str):
        """Get instance details including user list."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()

        async with session.get(
            f"{BASE_URL}/instances/{world_id}:{instance_id}",
            headers=headers,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                self._logged_in = False
                relogged = await self.ensure_logged_in()
                if relogged:
                    async with session.get(
                        f"{BASE_URL}/instances/{world_id}:{instance_id}",
                        headers=self._headers(),
                    ) as resp2:
                        self._extract_cookies(resp2)
                        if resp2.status == 200:
                            return await resp2.json()
                return {"error": "Auth expired and re-login failed"}
            else:
                text = await resp.text()
                return {"error": f"Failed to get instance: HTTP {resp.status} - {text}"}

    async def get_avatar(self, avatar_id: str):
        """Get avatar info by ID."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()

        async with session.get(f"{BASE_URL}/avatars/{avatar_id}", headers=headers) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 404:
                return {"error": f"Avatar '{avatar_id}' not found"}
            else:
                return {"error": f"Failed to get avatar: HTTP {resp.status}"}

    async def get_own_avatar(self):
        """Get current user's equipped avatar info."""
        user = await self.get_current_user()
        if "error" in user:
            return user
        user_id = user.get("id", "")
        if not user_id:
            return {"error": "Could not determine user ID"}

        session = await self._get_session()
        headers = self._headers()

        async with session.get(f"{BASE_URL}/users/{user_id}/avatar", headers=headers) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                return await resp.json()
            else:
                return {"error": f"Failed to get own avatar: HTTP {resp.status}"}

    async def invite_user(self, user_id: str, instance_id: str):
        """Send an invite to a user to join an instance."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()
        payload = {"instanceId": instance_id}

        async with session.post(
            f"{BASE_URL}/invite/{user_id}",
            headers=headers,
            json=payload,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                logger.info(f"Invite sent to {user_id}")
                return {"result": "ok"}
            elif resp.status == 403:
                return {"error": "Cannot invite this user (not friends or privacy settings)"}
            else:
                text = await resp.text()
                return {"error": f"Failed to invite user: HTTP {resp.status} - {text}"}

    async def request_invite(self, user_id: str):
        """Request an invite from a user."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()

        async with session.post(
            f"{BASE_URL}/requestInvite/{user_id}",
            headers=headers,
            json={},
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 200:
                logger.info(f"Invite requested from {user_id}")
                return {"result": "ok"}
            elif resp.status == 403:
                return {"error": "Cannot request invite from this user"}
            else:
                text = await resp.text()
                return {"error": f"Failed to request invite: HTTP {resp.status} - {text}"}

    async def get_friends(self, offline=False):
        """Fetch all friends with pagination (max 100 per page)."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        all_friends = []
        offset = 0
        page_size = 100

        while True:
            headers = self._headers()
            params = f"?offset={offset}&n={page_size}&offline={'true' if offline else 'false'}"
            async with session.get(
                f"{BASE_URL}/auth/user/friends{params}",
                headers=headers,
            ) as resp:
                self._extract_cookies(resp)
                if resp.status != 200:
                    break
                page = await resp.json()
                if not page:
                    break
                all_friends.extend(page)
                if len(page) < page_size:
                    break
                offset += page_size

        return all_friends

    async def fetch_and_cache_friends(self):
        """Fetch friends list and cache to disk. Returns the friends list."""
        online = await self.get_friends(offline=False)
        offline = await self.get_friends(offline=True)
        if isinstance(online, dict) and "error" in online:
            return online

        all_friends = []
        seen = set()
        for f in online + (offline if isinstance(offline, list) else []):
            uid = f.get("id", "")
            if uid and uid not in seen:
                seen.add(uid)
                all_friends.append({
                    "id": uid,
                    "displayName": f.get("displayName", ""),
                })

        cache = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "count": len(all_friends),
            "friends": all_friends,
        }
        FRIENDS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        FRIENDS_CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        logger.info(f"Cached {len(all_friends)} VRChat friends to {FRIENDS_CACHE_FILE}")
        return all_friends

    @staticmethod
    def friends_cache_fresh() -> bool:
        """Check if friends cache exists and is less than 4 hours old."""
        if not FRIENDS_CACHE_FILE.exists():
            return False
        try:
            data = json.loads(FRIENDS_CACHE_FILE.read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(data["fetched_at"])
            age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600
            return age_hours < FRIENDS_CACHE_MAX_AGE_HOURS
        except Exception:
            return False

    @staticmethod
    def load_cached_friends() -> list[dict]:
        """Load friends from cache file."""
        if not FRIENDS_CACHE_FILE.exists():
            return []
        try:
            data = json.loads(FRIENDS_CACHE_FILE.read_text(encoding="utf-8"))
            return data.get("friends", [])
        except Exception:
            return []

    async def search_worlds(self, query: str, n: int = 10):
        """Search VRChat worlds by name."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()
        params = f"?search={quote(query)}&n={n}&sort=relevance&order=descending&releaseStatus=public"
        async with session.get(
            f"{BASE_URL}/worlds{params}",
            headers=headers,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 401:
                self._logged_in = False
                return {"error": "Auth expired, please retry"}
            if resp.status != 200:
                return {"error": f"API returned {resp.status}"}
            return await resp.json()

    async def update_status(self, status_description: str = None, status: str = None, bio: str = None):
        """Update the authenticated user's status description, status, and/or bio."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}
        if not self._user_id:
            return {"error": "User ID not available -- login may have failed"}

        body = {}
        if status_description is not None:
            body["statusDescription"] = status_description
        if status is not None:
            valid = ("active", "join me", "ask me", "busy", "offline")
            if status not in valid:
                return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(valid)}"}
            body["status"] = status
        if bio is not None:
            body["bio"] = bio
        if not body:
            return {"error": "Nothing to update"}

        session = await self._get_session()
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        async with session.put(
            f"{BASE_URL}/users/{self._user_id}",
            headers=headers,
            json=body,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 401:
                self._logged_in = False
                return {"error": "Auth expired, please retry"}
            if resp.status != 200:
                text = await resp.text()
                return {"error": f"API returned {resp.status}: {text}"}
            data = await resp.json()
            return {
                "result": "ok",
                "status": data.get("status", ""),
                "statusDescription": data.get("statusDescription", ""),
                "bio": data.get("bio", ""),
            }

    async def get_user(self, user_id: str):
        """Get public user information by user ID."""
        logged_in = await self.ensure_logged_in()
        if not logged_in:
            return {"error": "Not logged in to VRChat API"}

        session = await self._get_session()
        headers = self._headers()
        async with session.get(
            f"{BASE_URL}/users/{user_id}",
            headers=headers,
        ) as resp:
            self._extract_cookies(resp)
            if resp.status == 401:
                self._logged_in = False
                return {"error": "Auth expired, please retry"}
            if resp.status == 404:
                return {"error": f"User '{user_id}' not found"}
            if resp.status != 200:
                return {"error": f"API returned {resp.status}"}
            return await resp.json()
