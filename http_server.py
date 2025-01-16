from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import constants as constant
import classes.json_wrapper as json_wrapper
import urllib.parse
import threading


def run_http_server():
    def add_message(message):
        """
        Adds a message to the history file.
        Args:
            message (str): The message to be added to the history.
        Returns:
            str: A confirmation message indicating that the message was added
            to the history.
        """

        json_wrapper.JsonWrapper.write(constant.HISTORY_PATH, message)

        return f"Added '{message}' to history."

    def mood():
        """
        Reads the mood from a JSON file and returns it as a formatted string.
        Returns:
            str: A string representing the mood in the format "mood:
            <mood_value>".
        """

        mood = json_wrapper.JsonWrapper.read(constant.MOOD_PATH).toString()

        return f"mood: {mood}"

    def logs():
        """
        Reads the logs from the specified history path and returns them as a
        string.
        Returns:
            str: The logs read from the history path.
        """

        logs = json_wrapper.JsonWrapper.read(constant.HISTORY_PATH).toString()

        return logs

    def status():
        return "online"

    def remove_leading_space(s):
        if s and s[0] == ' ':
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

        json_wrapper.JsonWrapper.write(constant.HISTORY_PATH, [])

        return "Logs Cleared"

    def handle_command(user_command, *args):
        command = remove_leading_space(user_command)

        if command == "add_message":
            return add_message(" ".join(args))
        elif command == "logs":
            return logs()
        elif command == "status":
            return status()
        elif command == "mood":
            return mood()
        elif command == "restart":
            return reset_logs()
        else:
            return "Command Not Found."

    class RequestHandler(BaseHTTPRequestHandler):
        def _send_response(self, message):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(message.encode())

        def do_GET(self):
            path = self.path[1:]
            parsed_path = urllib.parse.unquote(path)
            command_parts = parsed_path.split('/')
            command = command_parts[0]
            args = command_parts[1:]

            try:
                result = handle_command(command, *args)
                self._send_response(result)
            except Exception as e:
                self._send_response(f"Error: {str(e)}")

    def start_server():
        server_class = ThreadingHTTPServer
        handler_class = RequestHandler
        port = 8080
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting httpd server on port {port}...')
        httpd.serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()


# Call run_http_server() to start the server
run_http_server()
