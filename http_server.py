from http.server import ThreadingHTTPServer
import urllib.parse
import threading
import classes.json_wrapper as json_wrapper
import constants as constant


def run_http_server() -> None:
    """
    Sets up and runs an HTTP server that handles various commands through HTTP
    GET requests. The server runs on the configured HTTP port and supports
    the following
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

    def add_message(message: str) -> None:
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

    def logs() -> str:
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

    def status() -> str:
        """
        Returns the status of the server.
        """
        return "online"

    def remove_leading_space(s: str) -> str:
        """
        Removes leading spaces from a string.
        Args:
            s (str): The string from which to remove leading spaces.
        Returns:
            str: The string with leading spaces removed.
        """
        if s and s[0] == " ":
            return s[1:]
        return s

    def reset_logs() -> str:
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

    def handle_command(user_command: str, *args: str) -> str:
        """
        Handles a user command by executing the corresponding function.
        Args:
            user_command (str): The command string provided by the user.
            *args: Additional arguments required by the command.
        Returns:
            str: The result of the executed command or an error message if the
            command is not found.
        Supported Commands:
            - "add_message": Adds a message. Requires additional arguments to
            form the message.
            - "logs": Retrieves logs.
            - "status": Retrieves the current status.
            - "restart": Resets the logs.
            - Any other command will return "Command Not Found."
        """

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

    class RequestHandler():
        def _send_response(self, message: str) -> None:
            """
            Sends an HTTP response with a 200 status code, a "Content-type"
            header set to "text/plain", and the provided message as the
            response body.
            Args:
                message (str): The message to include in the response body.
            """

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(message.encode())

        def do_get(self) -> None:
            """
            Handles HTTP GET requests by parsing the request path, extracting
            the command and its arguments, and invoking the appropriate
            handler function.
            The method performs the following steps:
            1. Extracts the path from the request and decodes it.
            2. Splits the path into a command and its arguments.
            3. Calls the `handle_command` function with the command and
            arguments.
            4. Sends the result back to the client as a response.
            5. If an error occurs (e.g., ValueError, KeyError, or TypeError),
            sends an
               error message as the response.
            Raises:
                ValueError: If the command or arguments are invalid.
                KeyError: If the command is not recognized.
                TypeError: If the arguments do not match the expected types.
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

    def start_server() -> None:
        """
        Starts an HTTP server using ThreadingHTTPServer and a custom request
        handler. This function initializes and starts an HTTP server on a
        specified port (from constants). It uses the ThreadingHTTPServer
        class to handle requests in a multithreaded manner and a custom
        RequestHandler class to process incoming HTTP requests. The server
        runs indefinitely until manually stopped.
        Prints:
            A message indicating that the server has started and the port it is
            listening on.
        """

        server_class = ThreadingHTTPServer
        handler_class = RequestHandler
        port = constant.Network.HTTP_SERVER_PORT
        server_address = ("", port)
        httpd = server_class(server_address, handler_class)
        print(f"Starting httpd server on port {port}...")
        httpd.serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()


run_http_server()
