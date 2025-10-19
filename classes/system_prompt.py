import os
import constants as constant


class SystemPrompt:
    @staticmethod
    def get_prompt_directory() -> dict:
        """
        Retrieves a dictionary of prompt files from the 'prompts' directory.
        This function scans the 'prompts' directory for files, extracts the
        first word from each file name (assuming the file name is separated by
        underscores), and creates a dictionary where the keys are the first
        words and the values are the file paths.
        Returns:
            dict: A dictionary where the keys are the first words from the
            file names and the values are the corresponding file paths.
        """

        prompt_directory = "prompts"
        prompt_files = os.listdir(prompt_directory)
        prompt_dict = {}

        for file_name in prompt_files:
            if os.path.isfile(os.path.join(prompt_directory, file_name)):
                first_word = file_name.split("_")[0]
                prompt_path = os.path.join(prompt_directory, file_name).replace("\\", "/")
                prompt_dict[first_word] = prompt_path

        return prompt_dict

    @staticmethod
    def get_full_prompt() -> str:
        """
        Reads and combines the contents of two prompt files: the normal system
        prompt and the additional prompt. The combined prompt is returned as a
        single string.
        Returns:
            str: A string containing the concatenated contents of the
            additional prompt file followed by the normal system prompt file,
            separated by a newline.
        Raises:
            FileNotFoundError: If either of the prompt files cannot be found.
            IOError: If there is an error reading the files.
        """

        with open(constant.FilePaths.NORMAL_SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as mood_file:
            normal_prompt = mood_file.read()

        return normal_prompt
