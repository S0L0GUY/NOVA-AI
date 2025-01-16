import os


class SystemPrompt:
    @staticmethod
    def get_prompt_directory():
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

        prompt_directory = 'prompts'
        prompt_files = os.listdir(prompt_directory)
        prompt_dict = {}

        for file_name in prompt_files:
            if os.path.isfile(os.path.join(prompt_directory, file_name)):
                first_word = file_name.split('_')[0]
                prompt_path = os.path.join(prompt_directory, file_name)\
                    .replace('\\', '/')
                prompt_dict[first_word] = prompt_path

        return prompt_dict

    @staticmethod
    def get_full_prompt(mood):
        """
        Combines the prompt file content based on the given mood with the
        'additional' prompt.

        Args:
            mood (str): The mood to retrieve the prompt for.

        Returns:
            str: The combined content of the mood-specific prompt and the
            'additional' prompt.
        """
        prompt_dict = SystemPrompt.get_prompt_directory()

        if mood not in prompt_dict or 'additional' not in prompt_dict:
            raise ValueError(
                "Specified mood or 'additional' prompt not found in the "
                "prompt directory.")

        mood_prompt_path = prompt_dict[mood]
        additional_prompt_path = prompt_dict['additional']

        with open(mood_prompt_path, 'r') as mood_file:
            mood_prompt_content = mood_file.read()

        with open(additional_prompt_path, 'r') as additional_file:
            additional_prompt_content = additional_file.read()

        return mood_prompt_content + "\n" + additional_prompt_content
