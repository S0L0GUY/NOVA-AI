import json


class JsonWrapper:
    @staticmethod
    def read_json(file_path: str) -> tuple:
        """
        Reads a JSON file and returns its contents as a Python object.
        Args:
            file_path (str): The path to the JSON file to be read.
        Returns:
            dict or list: The contents of the JSON file as a Python object.
        Raises:
            IOError: If the file cannot be opened or read.
            json.JSONDecodeError: If the file does not contain valid JSON.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def read_txt(self, file_path: str) -> str:
        """
        Reads a text file and returns its contents as a string.
        Args:
            file_path (str): The path to the text file to be read.
        Returns:
            str: The contents of the text file as a string.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def wipe_json(file_path: str) -> None:
        """
        Clears the contents of a JSON file by writing an empty JSON object or
        array to it.
        Args:
            file_path (str): The path to the JSON file to be cleared.
        Raises:
            IOError: If the file cannot be opened or written to.
        """

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4)

    @staticmethod
    def write(file_path: str, data: tuple) -> None:
        """
        Writes data to a JSON file. If the file already exists, it will be
        overwritten.
        Args:
            file_path (str): The path to the JSON file to be written to.
            data (dict or list): The data to be written to the JSON file.
        Raises:
            IOError: If the file cannot be opened or written to.
        """

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def delete(file_path: str) -> None:
        """
        Deletes the file at the specified file path.
        Args:
            file_path (str): The path to the file to be deleted.
        Raises:
            IOError: If the file cannot be deleted.
        """

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            empty_data = []
        elif isinstance(data, dict):
            empty_data = {}
        else:
            raise ValueError("The file does not contain a JSON object or array.")

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(empty_data, file, indent=4)
