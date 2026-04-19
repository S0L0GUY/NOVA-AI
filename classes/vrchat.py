# Step 1. We begin with creating a Configuration, which contains the username and password for authentication.
from pathlib import Path

import vrchatapi
import yaml
from vrchatapi.api import authentication_api, notifications_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

config_path = Path(__file__).resolve().parents[1] / "config.yaml"
cookie_path = config_path.with_name(".vrchat_cookie")


def load_cookie() -> str:
    try:
        return cookie_path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def save_cookie(cookie: str) -> None:
    try:
        cookie_path.write_text(cookie, encoding="utf-8")
    except Exception:
        pass
with config_path.open("r", encoding="utf-8") as f:
    app_config = yaml.safe_load(f) or {}

vrchat_cfg = app_config.get("vrchat", {})
configuration = vrchatapi.Configuration(
    username=vrchat_cfg.get("username", ""),
    password=vrchat_cfg.get("password", ""),
)

# Step 2. VRChat consists of several API's (WorldsApi, UsersApi, FilesApi, NotificationsApi, FriendsApi, etc...)
# Here we enter a context of the API Client and instantiate the Authentication API which is required for logging in.

# Enter a context with an instance of the API client
loaded_cookie = load_cookie()

with vrchatapi.ApiClient(configuration, cookie=loaded_cookie or None) as api_client:
    # Set our User-Agent as per VRChat Usage Policy
    api_client.user_agent = "NOVA-AI/0.0.1 my@email.com"

    # Instantiate instances of API classes
    auth_api = authentication_api.AuthenticationApi(api_client)
    notifications = notifications_api.NotificationsApi(api_client)
    current_user = None

    try:
        # Step 3. Calling getCurrentUser on Authentication API logs you in if the user isn't already logged in.
        current_user = auth_api.get_current_user()
    except UnauthorizedException as e:
        if e.status == 200:
            reason = str(e.reason or "")
            if "Email 2 Factor Authentication" in reason:
                # Step 3.5. Calling email verify2fa if the account has 2FA disabled
                auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
            elif "2 Factor Authentication" in reason:
                # Step 3.5. Calling verify2fa if the account has 2FA enabled
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
            current_user = auth_api.get_current_user()

        # If login succeeded, capture any Set-Cookie header and persist it for later runs
        try:
            resp = getattr(api_client, "last_response", None)
            if resp is not None:
                set_cookie = None
                try:
                    set_cookie = resp.getheader("Set-Cookie")
                except Exception:
                    # fallback to headers dict-like
                    try:
                        set_cookie = resp.getheaders().get("Set-Cookie")
                    except Exception:
                        set_cookie = None

                if set_cookie:
                    # Save the raw Set-Cookie header so ApiClient can reuse it
                    save_cookie(set_cookie)
                    api_client.cookie = set_cookie
        except Exception:
            pass
        else:
            print("Exception when calling API: %s\n", e)
    except vrchatapi.ApiException as e:
        print("Exception when calling API: %s\n", e)

    display_name = getattr(current_user, "display_name", None)
    if isinstance(display_name, str):
        print("Logged in as:", display_name)
    else:
        print("Logged in, but could not read display name.")

    # Auto-accept incoming friend requests: fetch notifications and accept friendRequest types
    try:
        notifs = notifications.get_notifications(type="friendRequest", hidden=False, n=50)
        for n in notifs or []:
            try:
                # n.id is the notification id used by accept_friend_request
                notifications.accept_friend_request(n.id)
                # mark as seen/hide if desired
                try:
                    notifications.mark_notification_as_read(n.id)
                except Exception:
                    pass
            except Exception:
                # ignore individual failures
                pass
    except Exception:
        # do not crash on auto-accept errors
        pass
