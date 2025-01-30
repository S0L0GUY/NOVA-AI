"""
A HTTP server implementation that handles various commands through GET
requests. This module implements a threaded HTTP server that can handle
different commands like adding messages to history, checking mood, viewing
logs, and checking status. The server runs on port 8080 and processes commands
through URL paths.
Functions:
    run_http_server(): Initializes and starts the HTTP server in a daemon
    thread.
Internal Functions:
    add_message(message): Adds a message to the history file.
    mood(): Retrieves the current mood from a JSON file.
    logs(): Retrieves the log history.
    status(): Returns the server status.
    remove_leading_space(s): Utility function to remove leading spaces from
    strings.
    reset_logs(): Clears the log history.
    handle_command(user_command, *args): Routes commands to appropriate
    handlers.
    start_server(): Initializes and starts the HTTP server.
Classes:
    RequestHandler: Handles HTTP GET requests and processes commands.
The server supports the following commands:
    - add_message: Adds a message to history
    - logs: Retrieves all logs
    - status: Checks server status
    - mood: Retrieves current mood
    - restart: Clears all logs
Usage:
    Simply call run_http_server() to start the server.
    Access commands via HTTP GET requests to localhost:8080/<command>/<args>
Dependencies:
    - http.server
    - constants
    - classes.json_wrapper
    - urllib.parse
    - threading
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse
import threading
import classes.json_wrapper as json_wrapper
import constants as constant


def run_http_server():
    """
    Sets up and runs an HTTP server that handles various commands through HTTP
    GET requests. The server runs on port 8080 and supports the following
    commands:
    - add_message: Adds a message to the history file
    - logs: Retrieves logs from history
    - status: Returns server status
    - mood: Returns current mood
    - restart: Resets/clears the logs
    The server is run in a separate daemon thread to allow concurrent
    operation.
        None
    Raises:
        Exception: For any errors during command handling or server operation
    """

    def add_message(message):
        """
        Adds a message to the history file.
        Args:
            message (str): The message to be added to the history.
        Returns:
            str: A confirmation message indicating that the message was added
            to the history.
        """

        json_wrapper.JsonWrapper.write(
            constant.FilePaths.HISTORY_PATH,
            message
        )

        return f"Added '{message}' to history."

    def logs():
        """
        Reads the logs from the specified history path and returns them as a
        string.
        Returns:
            str: The logs read from the history path.
        """

        history = json_wrapper.JsonWrapper.read_json(
            constant.FilePaths.HISTORY_PATH)
        logs = history.toString()

        return logs

    def status():
        return "online"

    def remove_leading_space(s):
        if s and s[0] == " ":
            return s[1:]
        return s

    def reset_logs():
        """
        Clears the log history by writing an empty list to the history file.
        This function uses the JsonWrapper to write an empty list to the file
        specified by HISTORY_PATH in the constant module, effectively clearing
        any existing log entries.
        Returns:
            str: A confirmation message indicating that the logs have been
            cleared.
        """

        json_wrapper.JsonWrapper.write(constant.FilePaths.HISTORY_PATH, [])

        return "Logs Cleared"

    def handle_command(user_command, *args):
        command = remove_leading_space(user_command)

        if command == "add_message":
            return add_message(" ".join(args))
        elif command == "logs":
            return logs()
        elif command == "status":
            return status()
        elif command == "restart":
            return reset_logs()
        else:
            return "Command Not Found."

    class RequestHandler(BaseHTTPRequestHandler):
        """A handler for HTTP requests extending BaseHTTPRequestHandler.
        This class handles incoming HTTP requests, specifically GET requests,
        by parsing the URL path into commands and arguments, executing them,
        and returning the results.
        Methods:
            _send_response(message): Sends an HTTP response with a given
            message
            do_GET(): Handles GET requests by parsing the path and executing
            commands
        Attributes:
            Inherits all attributes from BaseHTTPRequestHandler
        Example:
            When receiving a GET request to "/command/arg1/arg2", it will:
            1. Parse into command="command", args=["arg1", "arg2"]
            2. Execute handle_command(command, arg1, arg2)
            3. Return the result or error message
        """

        def _send_response(self, message):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(message.encode())

        def do_get(self):
            """
            Handle GET requests sent to the HTTP server.
            This method parses the request path, extracts the command and its
            arguments, and then attempts to handle the command using the
            `handle_command` function. The result of the command is sent back
            as the HTTP response. If an error occurs during command handling,
            an error message is sent as the response. The expected format of
            the request path is:
            /<command>/<arg1>/<arg2>/...
            Example:
            /echo/hello/world
            Raises:
                Exception: If an error occurs during command handling.
            """

            path = self.path[1:]
            parsed_path = urllib.parse.unquote(path)
            command_parts = parsed_path.split("/")
            command = command_parts[0]
            args = command_parts[1:]

            try:
                result = handle_command(command, *args)
                self._send_response(result)
            except (ValueError, KeyError, TypeError) as e:
                self._send_response(f"Error: {str(e)}")

    def start_server():
        server_class = ThreadingHTTPServer
        handler_class = RequestHandler
        port = 8080
        server_address = ("", port)
        httpd = server_class(server_address, handler_class)
        print(f"Starting httpd server on port {port}...")
        httpd.serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()


# Call run_http_server() to start the server
run_http_server()
