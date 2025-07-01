"""
VRChat API integration for NOVA-AI.
This module handles VRChat API authentication, friend request management,
and periodic API checks.
"""
import threading
import time
import logging
from typing import Optional, List

import vrchatapi
from vrchatapi.api import authentication_api, friends_api, notifications_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

import constants as constant


class VRChatAPIManager:
    """
    Manages VRChat API interactions including authentication and friend
    requests.
    """

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

    def initialize(self) -> bool:
        """
        Initialize the VRChat API connection and authenticate.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
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
            self.auth_api = authentication_api.AuthenticationApi(
                self.api_client
            )
            self.friends_api = friends_api.FriendsApi(self.api_client)
            self.notifications_api = notifications_api.NotificationsApi(
                self.api_client
            )

            # Authenticate
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
            return True

        except UnauthorizedException as e:
            if e.status == 200:
                try:
                    if "Email 2 Factor Authentication" in e.reason:
                        # Handle email 2FA
                        code = input("VRChat Email 2FA Code: ")
                        self.auth_api.verify2_fa_email_code(
                            two_factor_email_code=TwoFactorEmailCode(code)
                        )
                    elif "2 Factor Authentication" in e.reason:
                        # Handle TOTP 2FA
                        code = input("VRChat 2FA Code: ")
                        self.auth_api.verify2_fa(
                            two_factor_auth_code=TwoFactorAuthCode(code)
                        )

                    # Try to get current user again after 2FA
                    self.current_user = self.auth_api.get_current_user()
                    self.is_authenticated = True
                    name = self.current_user.display_name
                    print(f"\033[92mVRChat API: Logged in as {name}\033[0m")
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
        self.check_thread = threading.Thread(
            target=self._periodic_check_loop, daemon=True
        )
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
                friend_interval = (
                    constant.VRChatAPI.FRIEND_REQUEST_CHECK_INTERVAL
                )
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

            # Get friend requests (notifications of type 'friendRequest')
            notifications = self.notifications_api.get_notifications()

            friend_requests = []
            for notif in notifications:
                if notif.type == 'friendRequest':
                    # Debug logging to understand the structure
                    logging.debug(f"Friend request notification details: "
                                  f"{type(notif.details)} - {notif.details}")
                    
                    # Check if details is a dict and has the expected structure
                    if (hasattr(notif, 'details') and
                        isinstance(notif.details, dict) and
                        notif.details.get('request', {}).get('state') ==
                            'pending'):
                        friend_requests.append(notif)
                    elif (hasattr(notif, 'details') and
                          notif.details == 'request'):
                        # Some friend requests might have details as string
                        friend_requests.append(notif)
                    else:
                        # Add all friend request notifications for now
                        # to ensure we don't miss any
                        friend_requests.append(notif)

            if friend_requests:
                count = len(friend_requests)
                print(f"\033[93mVRChat API: Found {count} pending"
                      f" friend request(s)\033[0m")

                if constant.VRChatAPI.AUTO_ACCEPT_FRIEND_REQUESTS:
                    for request in friend_requests:
                        self._accept_friend_request(request)
                else:
                    print(f"\033[93mVRChat API: Auto-accept disabled, "
                          f"{count} requests pending\033[0m")

        except Exception as e:
            logging.error(f"Error checking friend requests: {e}")
            # Add more detailed error information
            logging.error(f"Exception type: {type(e)}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")

    def _accept_friend_request(self, notification) -> None:
        """
        Accept a friend request.

        Args:
            notification: The friend request notification object.
        """
        try:
            # Check if notification has required attributes
            if not hasattr(notification, 'sender_user_id'):
                logging.error(f"Notification missing sender_user_id: "
                              f"{notification}")
                return

            user_id = notification.sender_user_id
            username = getattr(notification, 'sender_username', "Unknown")

            # Accept the friend request
            self.friends_api.friend(user_id=user_id)
            print(f"\033[92mVRChat API: Accepted friend request "
                  f"from {username}\033[0m")

            # Mark notification as seen if it has an ID
            if hasattr(notification, 'id'):
                self.notifications_api.mark_notification_as_read(
                    notification_id=notification.id
                )

        except Exception as e:
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

            notifications = self.notifications_api.get_notifications()

            # Filter for unread notifications
            unread_notifications = [
                notif for notif in notifications if not notif.seen
            ]

            if unread_notifications:
                count = len(unread_notifications)
                print(f"\033[96mVRChat API: {count} unread"
                      f" notification(s)\033[0m")

                for notif in unread_notifications:
                    # Friend requests are handled separately
                    if notif.type not in ['friendRequest']:
                        username = notif.sender_username or 'Unknown'
                        print(f"\033[96mVRChat API: {notif.type} "
                              f"from {username}\033[0m")

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
