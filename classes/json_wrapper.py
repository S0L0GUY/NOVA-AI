import json


class JsonWrapper:
    @staticmethod
    def read_json(file_path):
        """
        Reads a JSON file and returns its contents as a pretty-printed JSON
        string.
        Args:
            file_path (str): The path to the JSON file to be read.
        Returns:
            str: The contents of the JSON file as a pretty-printed JSON string.
        """

        with open(file_path, 'r') as file:
            data = json.load(file)
            return json.dumps(data, indent=4)

    def read_txt(self, file_path):
        """
        Reads a text file and returns its contents as a string.
        Args:
            file_path (str): The path to the text file to be read.
        Returns:
            str: The contents of the text file as a string.
        """

        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def write(file_path, data):
        """
        Writes the given data to a JSON file at the specified file path.
        Args:
            file_path (str): The path to the file where the data should be
            written.
            data (dict): The data to be written to the file.
        Raises:
            IOError: If the file cannot be opened or written to.
        """

        with open(file_path, 'a') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def delete(file_path):
        """
        Deletes the file at the specified file path.
        Args:
            file_path (str): The path to the file to be deleted.
        Raises:
            IOError: If the file cannot be deleted.
        """

        with open(file_path, 'r') as file:
            data = json.load(file)

        if isinstance(data, list):
            empty_data = []
        elif isinstance(data, dict):
            empty_data = {}
        else:
            raise ValueError(
                "The file does not contain a JSON object or array.")

        with open(file_path, 'w') as file:
            json.dump(empty_data, file, indent=4)
