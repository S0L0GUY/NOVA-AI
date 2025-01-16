from datetime import datetime


def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S %Y-%m-%d")


class Debug:
    @staticmethod
    def write(log_type, message):
        """
        Args:
            log_type (string): The type of message, e.g: ERROR, IMPORT.
            message (string): The message to log.

        Log a message to both the terminal, alltime_debug_log.txt, and
        current_debug_log.txt.
        """
        # Prints the log to the terminal
        log_message = f'{get_time()} {log_type}: {message}'
        print(log_message)

        # Writes the log to debug_log.txt using UTF-8 encoding
        try:
            with open('text_files/current_debug_log.txt', 'a',
                      encoding='utf-8') as file:
                file.write(log_message + '\n')
        except UnicodeEncodeError:
            print(f"Skipping message due to encoding error: {message}")

        try:
            with open('text_files/alltime_debug_log.txt', 'a',
                      encoding='utf-8') as file:
                file.write(log_message + '\n')
        except UnicodeEncodeError:
            print(f"Skipping message due to encoding error: {message}")

    @staticmethod
    def clear():
        """Delete the content in current_debug_log.txt"""
        with open('text_files/current_debug_log.txt', 'w',
                  encoding='utf-8') as file:
            file.write('')
