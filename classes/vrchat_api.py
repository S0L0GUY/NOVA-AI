import logging
import threading
import time
from typing import List, Optional

import vrchatapi
from vrchatapi.api import authentication_api, friends_api, notifications_api
from vrchatapi.exceptions import ApiException, UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

import constants as constant


class VRChatAPIManager:
    def __init__(self):
        self.configuration = None
        self.api_client = None
        self.auth_api = None
        self.friends_api = None
        self.notifications_api = None
        self.current_user = None
        self.is_authenticated = False
        self.check_thread = None
        self.stop_checking = False

        # Rate limiting variables
        self.last_friend_request_time = 0
        self.friend_request_retry_count = 0
        self.max_friend_request_retries = 5
        self.base_retry_delay = 60
        self.max_retry_delay = 600

        self.last_api_call_time = 0

        self.processed_notifications = set()
        self.friends_cache = set()  # Cache of current friends
        self.last_friends_update = 0

    @staticmethod
    def create_vrchat_api_manager() -> "VRChatAPIManager":
        """
        Initializes the VRChat API if enabled in the configuration.
        This function checks whether the VRChat API is enabled using the
        `VRChatAPIManager.is_api_enabled()` method. If enabled, it attempts to
        initialize the API and starts periodic checks for friend requests and
        notifications. Appropriate status messages are printed to the console
        indicating the success or failure of the initialization. If the API is
        not enabled or initialization fails, the function returns None.
        Returns:
            VRChatAPIManager or None: An initialized VRChatAPIManager instance
            if successful, otherwise None.
        """

        vrchat_api = None

        if VRChatAPIManager.is_api_enabled():
            vrchat_api = VRChatAPIManager()
            print("\033[94mInitializing VRChat API...\033[0m")

            if vrchat_api.initialize():
                print("\033[92mVRChat API initialized successfully\033[0m")

                vrchat_api.start_periodic_checks()
            else:
                print("\033[91mVRChat API initialization failed, continuing " "without API features\033[0m")

                vrchat_api = None
        else:
            print("\033[93mVRChat API disabled in configuration\033[0m")

        return vrchat_api

    @staticmethod
    def is_api_enabled() -> bool:
        """
        Check if VRChat API functionality is enabled in configuration.

        Returns:
            bool: True if API is enabled, False otherwise.
        """
        return constant.VRChatAPI.USING_API

    def _validate_credentials(self) -> bool:
        """
        Validate that required credentials are available.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        if not constant.VRChatAPI.USERNAME or not constant.VRChatAPI.PASSWORD:
            logging.error(
                "VRChat API credentials not found. Please set " "VRCHAT_EMAIL and VRCHAT_PASSWORD environment " "variables."
            )

            return False

        return True

    def initialize(self) -> bool:
        """
        Initialize the VRChat API connection and authenticate.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        # Check if API is enabled
        if not self.is_api_enabled():
            logging.info("VRChat API is disabled in configuration")

            return False

        # Validate credentials
        if not self._validate_credentials():
            return False

        try:
            # Create configuration
            self.configuration = vrchatapi.Configuration(
                username=constant.VRChatAPI.USERNAME,
                password=constant.VRChatAPI.PASSWORD,
            )

            # Create API client
            self.api_client = vrchatapi.ApiClient(self.configuration)
            self.api_client.user_agent = constant.VRChatAPI.USER_AGENT

            # Initialize API instances
            self.auth_api = authentication_api.AuthenticationApi(self.api_client)
            self.friends_api = friends_api.FriendsApi(self.api_client)
            self.notifications_api = notifications_api.NotificationsApi(self.api_client)

            return self._authenticate()

        except Exception as e:
            logging.error(f"Failed to initialize VRChat API: {e}")
            return False

    def _authenticate(self) -> bool:
        """
        Authenticate with VRChat API.

        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            # Attempt to get current user (this triggers login)
            self.current_user = self.auth_api.get_current_user()
            self.is_authenticated = True
            name = self.current_user.display_name
            print(f"\033[92mVRChat API: Logged in as {name}\033[0m")

            # Initialize friends cache after successful authentication
            self._update_friends_cache()

            return True

        except UnauthorizedException as e:
            if e.status == 200:
                try:
                    if "Email 2 Factor Authentication" in e.reason:
                        # Handle email 2FA
                        code = input("VRChat Email 2FA Code: ")
                        self.auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(code))
                    elif "2 Factor Authentication" in e.reason:
                        # Handle TOTP 2FA
                        code = input("VRChat 2FA Code: ")
                        self.auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(code))

                    # Try to get current user again after 2FA
                    self.current_user = self.auth_api.get_current_user()
                    self.is_authenticated = True
                    name = self.current_user.display_name
                    print(f"\033[92mVRChat API: Logged in as {name}\033[0m")

                    # Initialize friends cache after successful authentication
                    self._update_friends_cache()

                    return True

                except Exception as auth_error:
                    logging.error(f"2FA authentication failed: {auth_error}")

                    return False
            else:
                logging.error(f"Authentication failed: {e}")

                return False

        except Exception as e:
            logging.error(f"Authentication error: {e}")

            return False

    def start_periodic_checks(self) -> None:
        """
        Start periodic checks for friend requests and notifications in a
        background thread.
        """
        if not self.is_authenticated:
            logging.warning("Cannot start checks: not authenticated")

            return

        if self.check_thread is not None and self.check_thread.is_alive():
            logging.warning("Periodic checks already running")

            return

        self.stop_checking = False
        self.check_thread = threading.Thread(target=self._periodic_check_loop, daemon=True)
        self.check_thread.start()
        print("\033[92mVRChat API: Started periodic checks\033[0m")

    def stop_periodic_checks(self) -> None:
        """
        Stop periodic checks.
        """
        self.stop_checking = True
        if self.check_thread is not None:
            self.check_thread.join(timeout=5)
        print("\033[93mVRChat API: Stopped periodic checks\033[0m")

    def _periodic_check_loop(self) -> None:
        """
        Main loop for periodic API checks.
        """
        last_friend_check = 0
        last_notification_check = 0

        while not self.stop_checking:
            try:
                current_time = time.time()

                # Check friend requests
                friend_interval = constant.VRChatAPI.FRIEND_REQUEST_CHECK_INTERVAL
                if current_time - last_friend_check >= friend_interval:
                    self._check_and_handle_friend_requests()
                    last_friend_check = current_time

                # Check notifications
                notif_interval = constant.VRChatAPI.NOTIFICATION_CHECK_INTERVAL
                if current_time - last_notification_check >= notif_interval:
                    self._check_notifications()
                    last_notification_check = current_time

                # Sleep for a short time to prevent busy waiting
                time.sleep(10)

                # Periodic cleanup of processed notifications
                if current_time % 3600 < 10:  # Every hour
                    self._cleanup_old_processed_notifications()

            except Exception as e:
                logging.error(f"Error in periodic check loop: {e}")
                time.sleep(30)  # Wait longer if there's an error

    def _check_and_handle_friend_requests(self) -> None:
        """
        Check for pending friend requests and handle them based on
        configuration.
        """
        try:
            if not self.is_authenticated:
                return

            # Wait for API cooldown before making the call
            self._wait_for_api_cooldown()

            # Update friends cache periodically (every 5 minutes)
            current_time = time.time()
            if current_time - self.last_friends_update > 300:  # 5 minutes
                self._update_friends_cache()

            # Get friend requests (notifications of type 'friendRequest')
            notifications = self.notifications_api.get_notifications()

            # Filter for unprocessed friend request notifications
            friend_requests = []
            for notif in notifications:
                if notif.type == "friendRequest" and notif.id not in self.processed_notifications:

                    # Skip if we don't have a sender_user_id
                    if not hasattr(notif, "sender_user_id"):
                        print(f"\033[93mVRChat API: Skipping notification " f"without sender_user_id: {notif.id}\033[0m")
                        continue

                    # Skip if user is already our friend
                    if notif.sender_user_id in self.friends_cache:
                        username = notif.sender_username
                        print(
                            f"\033[93mVRChat API: User {username} "
                            f"is already a friend, marking notification "
                            f"as processed\033[0m"
                        )
                        self.processed_notifications.add(notif.id)
                        self._mark_notification_as_seen(notif)
                        continue
                    else:
                        # Debug: log when user is not in cache
                        cache_size = len(self.friends_cache)
                        username = notif.sender_username
                        user_id = notif.sender_user_id
                        print(
                            f"\033[96mVRChat API: User {username} "
                            f"({user_id}) not in friends cache "
                            f"(cache size: {cache_size})\033[0m"
                        )

                    # Check if it's actually a pending friend request
                    is_pending = False
                    if hasattr(notif, "details"):
                        if isinstance(notif.details, dict):
                            # Check for pending state in request details
                            request_state = notif.details.get("request", {}).get("state")
                            if request_state == "pending":
                                is_pending = True
                        elif notif.details == "request":
                            # Some notifications might have string details
                            is_pending = True

                    # If we can't determine the state, assume it's pending
                    # but log it for debugging
                    if not is_pending and hasattr(notif, "details"):
                        username = notif.sender_username
                        details = notif.details
                        print(
                            f"\033[96mVRChat API: Unknown friend request "
                            f"state for {username}, details: "
                            f"{details}\033[0m"
                        )
                        is_pending = True  # Accept it anyway to be safe

                    if is_pending:
                        friend_requests.append(notif)

            if friend_requests:
                count = len(friend_requests)
                print(f"\033[93mVRChat API: Found {count} new pending" f" friend request(s)\033[0m")

                if constant.VRChatAPI.AUTO_ACCEPT_FRIEND_REQUESTS:
                    for request in friend_requests:
                        self._accept_friend_request(request)
                else:
                    print(f"\033[93mVRChat API: Auto-accept disabled, " f"{count} requests pending\033[0m")
                    # Mark as processed even if not auto-accepting
                    for request in friend_requests:
                        self.processed_notifications.add(request.id)

        except Exception as e:
            logging.error(f"Error checking friend requests: {e}")
            # Add more detailed error information
            logging.error(f"Exception type: {type(e)}")
            import traceback

            logging.error(f"Traceback: {traceback.format_exc()}")

    def _accept_friend_request(self, notification) -> None:
        """
        Accept a friend request with rate limiting.

        Args:
            notification: The friend request notification object.
        """
        try:
            # Check if notification has required attributes
            if not hasattr(notification, "sender_user_id"):
                logging.error(f"Notification missing sender_user_id: " f"{notification}")
                return

            user_id = notification.sender_user_id
            username = getattr(notification, "sender_username", "Unknown")

            # Rate limiting check
            current_time = time.time()
            time_since_last = current_time - self.last_friend_request_time

            # If we've been rate limited, calculate exponential backoff delay
            if self.friend_request_retry_count > 0:
                delay = min(
                    self.base_retry_delay * (2**self.friend_request_retry_count),
                    self.max_retry_delay,
                )

                if time_since_last < delay:
                    remaining_time = delay - time_since_last
                    print(
                        f"\033[93mVRChat API: Rate limited, waiting "
                        f"{remaining_time:.0f}s before accepting friend "
                        f"request from {username}\033[0m"
                    )
                    return

            # Wait for API cooldown before making the call
            self._wait_for_api_cooldown()

            # Accept the friend request
            self.friends_api.friend(user_id=user_id)
            print(f"\033[92mVRChat API: Accepted friend request " f"from {username}\033[0m")

            # Reset retry count on success
            self.friend_request_retry_count = 0
            self.last_friend_request_time = current_time

            # Mark notification as processed and seen
            self.processed_notifications.add(notification.id)
            self._mark_notification_as_seen(notification)

            # Add user to friends cache
            self.friends_cache.add(user_id)

        except ApiException as e:
            # Mark as processed to avoid retrying indefinitely
            self.processed_notifications.add(notification.id)

            if e.status == 400 and "already friends" in str(e.body).lower():
                # Users are already friends - this is expected, just log it
                print(f"\033[93mVRChat API: {username} is already a friend, " f"marking as processed\033[0m")
                # Add to friends cache and mark as seen
                self.friends_cache.add(user_id)
                self._mark_notification_as_seen(notification)
                # Force refresh friends cache since it was out of date
                print("\033[96mVRChat API: Refreshing friends cache due to " "stale data\033[0m")
                self._update_friends_cache()
            elif e.status == 429:  # Rate limited
                self.friend_request_retry_count += 1
                self.last_friend_request_time = time.time()

                max_retries = self.max_friend_request_retries
                if self.friend_request_retry_count <= max_retries:
                    delay = min(
                        self.base_retry_delay * (2**self.friend_request_retry_count),
                        self.max_retry_delay,
                    )
                    print(
                        f"\033[93mVRChat API: Rate limited (429). "
                        f"Will retry accepting friend request from "
                        f"{username} in {delay}s (attempt "
                        f"{self.friend_request_retry_count}/"
                        f"{max_retries})\033[0m"
                    )
                    # Remove from processed so it can be retried
                    self.processed_notifications.discard(notification.id)
                else:
                    print(
                        f"\033[91mVRChat API: Max retries reached for "
                        f"friend request from {username}. "
                        f"Giving up.\033[0m"
                    )
                    self.friend_request_retry_count = 0
            else:
                logging.error(f"Error accepting friend request: {e}")
                logging.error(f"Notification object: {notification}")
        except Exception as e:
            # Mark as processed to avoid retrying indefinitely
            self.processed_notifications.add(notification.id)

            # Check if this is a specific API client deserialization error
            if "Invalid value for `created_at`" in str(e):
                print(f"\033[93mVRChat API: API client deserialization error " f"for {username}, marking as processed\033[0m")
                # This is likely a VRChat API client bug, just mark as seen
                self._mark_notification_as_seen(notification)
            else:
                logging.error(f"Error accepting friend request: {e}")
                logging.error(f"Notification object: {notification}")
                import traceback

                logging.error(f"Traceback: {traceback.format_exc()}")

    def _check_notifications(self) -> None:
        """
        Check for new notifications and log them.
        """
        try:
            if not self.is_authenticated:
                return

            # Wait for API cooldown before making the call
            self._wait_for_api_cooldown()

            notifications = self.notifications_api.get_notifications()

            # Filter for unread notifications
            unread_notifications = [notif for notif in notifications if not notif.seen]

            if unread_notifications:
                count = len(unread_notifications)
                print(f"\033[96mVRChat API: {count} unread" f" notification(s)\033[0m")

                for notif in unread_notifications:
                    # Friend requests are handled separately
                    if notif.type not in ["friendRequest"]:
                        username = notif.sender_username or "Unknown"
                        print(f"\033[96mVRChat API: {notif.type} " f"from {username}\033[0m")

        except Exception as e:
            logging.error(f"Error checking notifications: {e}")

    def get_friends_list(self) -> Optional[List]:
        """
        Get the current user's friends list.

        Returns:
            Optional[List]: List of friends or None if error.
        """
        try:
            if not self.is_authenticated:
                return None

            # Wait for API cooldown before making the call
            self._wait_for_api_cooldown()

            friends = self.friends_api.get_friends()
            return friends

        except Exception as e:
            logging.error(f"Error getting friends list: {e}")
            return None

    def disconnect(self) -> None:
        """
        Clean up and disconnect from VRChat API.
        """
        self.stop_periodic_checks()

        if self.api_client:
            try:
                # Logout if possible
                if self.auth_api and self.is_authenticated:
                    self.auth_api.logout()
                    print("\033[93mVRChat API: Logged out\033[0m")
            except Exception as e:
                logging.error(f"Error during logout: {e}")
            finally:
                self.api_client.close()

        self.is_authenticated = False
        self.current_user = None

        # Clear caches
        self.processed_notifications.clear()
        self.friends_cache.clear()
        self.last_friends_update = 0

    def get_rate_limit_status(self) -> dict:
        """
        Get the current rate limiting status for debugging.

        Returns:
            dict: Current rate limiting information
        """
        current_time = time.time()
        time_since_last = current_time - self.last_friend_request_time
        time_since_last_api = current_time - self.last_api_call_time

        if self.friend_request_retry_count > 0:
            delay = min(
                self.base_retry_delay * (2**self.friend_request_retry_count),
                self.max_retry_delay,
            )
            remaining_delay = max(0, delay - time_since_last)
        else:
            remaining_delay = 0

        # Calculate remaining API cooldown
        api_cooldown = constant.VRChatAPI.API_COOLDOWN
        remaining_api_cooldown = max(0, api_cooldown - time_since_last_api)

        return {
            "retry_count": self.friend_request_retry_count,
            "last_request_time": self.last_friend_request_time,
            "time_since_last": time_since_last,
            "remaining_delay": remaining_delay,
            "is_rate_limited": remaining_delay > 0,
            "last_api_call_time": self.last_api_call_time,
            "time_since_last_api": time_since_last_api,
            "remaining_api_cooldown": remaining_api_cooldown,
            "api_cooldown_active": remaining_api_cooldown > 0,
        }

    def _wait_for_api_cooldown(self) -> None:
        """
        Wait for the API cooldown period to prevent rate limiting.
        """
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        cooldown_period = constant.VRChatAPI.API_COOLDOWN

        if time_since_last_call < cooldown_period:
            wait_time = cooldown_period - time_since_last_call
            print(f"\033[96mVRChat API: Waiting {wait_time:.1f}s " f"for cooldown\033[0m")
            time.sleep(wait_time)

        # Update the last API call time
        self.last_api_call_time = time.time()

    def _update_friends_cache(self) -> None:
        """
        Update the cache of current friends to avoid duplicate requests.
        """
        try:
            # Wait for API cooldown before making the call
            self._wait_for_api_cooldown()

            friends = self.friends_api.get_friends()
            self.friends_cache = {friend.id for friend in friends}
            self.last_friends_update = time.time()

            count = len(self.friends_cache)
            print(f"\033[96mVRChat API: Updated friends cache " f"({count} friends)\033[0m")

        except Exception as e:
            logging.error(f"Error updating friends cache: {e}")

    def _mark_notification_as_seen(self, notification) -> None:
        """
        Mark a notification as seen/read.

        Args:
            notification: The notification object to mark as seen.
        """
        try:
            if hasattr(notification, "id"):
                # Wait for API cooldown before marking as read
                self._wait_for_api_cooldown()
                self.notifications_api.mark_notification_as_read(notification_id=notification.id)
        except Exception as e:
            logging.error(f"Error marking notification as seen: {e}")

    def _cleanup_old_processed_notifications(self) -> None:
        """
        Clean up old processed notifications to prevent memory buildup.
        This should be called periodically to remove old notification IDs.
        """
        # For now, we'll clear all processed notifications on cleanup
        # In a more sophisticated implementation, you could track timestamps
        # and only remove notifications older than a certain time
        if len(self.processed_notifications) > 1000:  # Arbitrary threshold
            print("\033[96mVRChat API: Cleaning up old processed " "notifications\033[0m")
            self.processed_notifications.clear()
