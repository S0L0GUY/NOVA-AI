# Commit History

- **Commit:** [9b3ec1f](https://github.com/S0L0GUY/NOVA-AI/commit/9b3ec1f2981c1c7016894d8141770863ec9d648b)
  **Author:** Copilot
  **Message:** Refactor to use only Together AI, remove OpenAI and LMStudio support (#62)

* Initial plan

* Remove OpenAI and LMStudio references, use only Together API

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Update README.md to remove OpenAI and LMStudio references

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Remove API_TYPE references from README code examples

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Update .gitignore to exclude __pycache__ directories

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Enhance audio device listing with highlighting for VB-Audio CABLE names and update audio device indices

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>
Co-authored-by: Evan Grinnell <worldevan8@gmail.com>

- **Commit:** [972ac7b](https://github.com/S0L0GUY/NOVA-AI/commit/972ac7b43af12e0aaf149ec3480ee19bc182731e)
  **Author:** Evan Grinnell
  **Message:** Update LLM API config and add smoke test script

Changed LLM API settings in constants.py to use local OpenAI API and updated model ID. Refactored nova.py for improved initialization and type hints. Added smoke_test.py for basic startup validation. Updated requirements.txt to use openai-whisper. Minor fixes in main.py and vrchat_api.py.

- **Commit:** [06ecdca](https://github.com/S0L0GUY/NOVA-AI/commit/06ecdca4dba20a4374b54c65c0788fc4a021cf30)
  **Author:** Copilot
  **Message:** Fix Auto LLM Chooser crash on API connection failures (#60)

* Initial plan

* Initial analysis: Auto LLM Choser error identified

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Fix Auto LLM Chooser error - add graceful error handling

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

- **Commit:** [7044aaa](https://github.com/S0L0GUY/NOVA-AI/commit/7044aaae2331c63857a42ab210506b743c5236fd)
  **Author:** Evan Grinnell
  **Message:** Enhance README with detailed multilingual support section and language options (#57)

- **Commit:** [3a70bd9](https://github.com/S0L0GUY/NOVA-AI/commit/3a70bd9624055135109a70712aa898ab5c6f7745)
  **Author:** Evan Grinnell
  **Message:** Added Multilingual Support (#55)

* Added Multilingual Support

Added support for 28 different languages based on the capabilities of `Llama 3.3 70B Instruct Turbo` and `en-US-EmmaMultilingualNeural`. I then tested each language and she spoke each with minimal failure and was able to clearly speak each language.

* Update prompts/normal_system_prompt.txt

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update prompts/normal_system_prompt.txt

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Updated System Prompt

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [83716f1](https://github.com/S0L0GUY/NOVA-AI/commit/83716f1f89ae1cc9c417573d80fbe254c32891a9)
  **Author:** Evan Grinnell
  **Message:** Removed Unended Files and Updated System Prompt

- **Commit:** [d9205b6](https://github.com/S0L0GUY/NOVA-AI/commit/d9205b61cdc5215098b6cc70bf3152eb72428058)
  **Author:** Evan Grinnell
  **Message:** Add Together AI integration and update documentation (#53)

Introduces first-class support for Together AI as a language and vision model provider, making it the default API in the project. Updates the README with configuration instructions, usage tips, and troubleshooting for Together AI, OpenAI, and LM Studio. Adds the 'together' package to requirements.txt and refactors documentation to use generic LLM_API and Vision_API classes for easier provider switching.

- **Commit:** [fe99c8c](https://github.com/S0L0GUY/NOVA-AI/commit/fe99c8c399a3fa06df62f93a94eae2e87fc387bd)
  **Author:** Evan Grinnell
  **Message:** Refactor API config and client selection for LLM and Vision (#51)

Replaces OpenAI-specific API key and config with generalized LLM_API and Vision_API classes in constants.py, supporting both OpenAI and Together APIs. Updates .env.example to use new environment variable names. Refactors client instantiation in nova.py, vision_manager.py, and vision_system.py to dynamically select the appropriate client based on configuration. Cleans up and consolidates configuration classes in constants.py.

- **Commit:** [964462e](https://github.com/S0L0GUY/NOVA-AI/commit/964462e488fbab662270d2308d328e049579475e)
  **Author:** Evan Grinnell
  **Message:** Fixed Terminal Human History

- **Commit:** [6b3d1a6](https://github.com/S0L0GUY/NOVA-AI/commit/6b3d1a679d9c3ffcaaa6221d3a40ab3ed713b7a3)
  **Author:** Evan Grinnell
  **Message:** Update commits.md

- **Commit:** [e358828](https://github.com/S0L0GUY/NOVA-AI/commit/e35882891f774b6eaa070235c69af12a89f95a6f)
  **Author:** Evan Grinnell
  **Message:** Update constants.py

- **Commit:** [34269b6](https://github.com/S0L0GUY/NOVA-AI/commit/34269b663dae1fbe3f0d9a6d1db44d4d19149b59)
  **Author:** Evan Grinnell
  **Message:** 46 update all comments and logic (#48)

* Updated 'main.py' for better readabulity

* Refactor nova.py main loop and model selection

Refactored nova.py by splitting the main loop and model selection logic into separate functions for improved clarity and maintainability. Updated main.py to call nova.main() instead of nova.run_code(). Minor formatting and docstring improvements were also made.

* Refactor config and prompts; update .env.example

Removed unused InterruptionSettings and ErrorHandling classes from constants.py, updated OpenAI API key handling to use environment variables, and clarified documentation. Adjusted system prompts for consistency, and updated .env.example to include OPENAI_API_KEY. Minor sleep interval and initial message changes for improved clarity and maintainability.

* Remove unused scripts and refactor resource monitor

Deleted http_server.py, list_voices.py, and test_vision_system.py as they are no longer needed. Refactored resource_monitor.py to use ResourceMonitor constants directly and improved color and configuration handling. Cleaned up constants.py by removing unused NovaPlacement movement sequence timings.

* Remove redundant comments and docstrings from classes

Cleaned up code by removing unnecessary comments and module-level docstrings from edge_tts.py, osc.py, vision_manager.py, vision_system.py, vrchat_api.py, and whisper.py. This improves code readability and reduces clutter without affecting functionality.

* Expand README with VRChat API and setup improvements

Added detailed documentation for VRChat API integration, including configuration, security, and troubleshooting. Enhanced setup instructions for local and cloud AI models, clarified environment variable usage, and updated feature lists to reflect new capabilities such as computer vision, resource monitoring, and modular architecture. Improved troubleshooting, configuration, and advanced usage sections for better developer onboarding.

* Update main.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [dfa0e8c](https://github.com/S0L0GUY/NOVA-AI/commit/dfa0e8c2b25caa873d4e0cf857720e720b6182a9)
  **Author:** Evan Grinnell
  **Message:** VRChat API (#47)

* Add VRChat API integration and periodic friend checks

Introduces a new VRChatAPIManager class for handling VRChat API authentication, friend request management, and notification checks. Adds configuration for VRChat API credentials and settings in constants.py. Updates main.py to initialize and manage the VRChat API lifecycle, including periodic background checks for friend requests and notifications. Adds 'vrchatapi' to requirements.txt.

* Add TODO comments for VRChat API credentials in constants.py

* Add support for environment variables and update VRChat credentials handling

- Introduced .env file support for storing sensitive VRChat credentials.
- Updated VRChatAPI class to retrieve credentials from environment variables.
- Enhanced README with instructions for setting up the .env file.
- Added python-dotenv to requirements.txt for environment variable management.
- Created test_vrchat_notification_fix.py for future tests.

* Removed unneded file

* Add rate limiting and cooldowns to VRChat API manager

This still does not work perfectly do DO NOT MERGE until this code is proven to work smoothly

* Add .env.example and improve VRChat API config handling

Introduced a .env.example file for easier environment variable setup and updated the README with clearer configuration instructions. Enhanced VRChat API integration by adding a master enable/disable switch, improved credential validation, and made API initialization conditional based on configuration. Updated constants.py with more granular settings and improved main.py to respect the new API enable flag.

* Update classes/vrchat_api.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [f5c4e88](https://github.com/S0L0GUY/NOVA-AI/commit/f5c4e88f2448b4fafb5998e5b589335d32336e0d)
  **Author:** Evan Grinnell
  **Message:** Remove exception handling from main loop in nova.py

The try-except block around the main loop in run_code() was removed, so exceptions and interrupts will now propagate instead of being caught and handled locally. This change may be intended to simplify error handling or to allow for higher-level management of exceptions.

- **Commit:** [484e290](https://github.com/S0L0GUY/NOVA-AI/commit/484e2902af55707c2bdb943f50b1b25c00eeb717)
  **Author:** Evan Grinnell
  **Message:** Vision Estimates (#44)

* Add vision system integration for VRChat

Introduces a vision system for Nova AI, including new classes for vision management and analysis, configuration constants, prompt files, and test scripts. The vision system captures VRChat window screenshots, analyzes them using an AI model, and injects environment/player updates into the conversation history. Updates to main.py and nova.py integrate the vision system into the main application flow.

* Update vision system to run asynchronously

The vision system now operates in the background and continuously monitors VRChat without waiting for the AI to finish processing. Updated documentation in nova.py and clarified a comment in constants.py. Updated vision_log.json with new entries.

* Add method to clear vision history at startup

Introduced clear_vision_history() in VisionManager to reset vision log and state files at startup. Updated nova.py to call this method during initialization, ensuring a clean state for each run. Updated vision_log.json and vision_state.json to reflect the cleared state.

* Disable vision system by default and clear vision history at startup

* Add detailed documentation for the Vision System in README.md

- **Commit:** [01a6320](https://github.com/S0L0GUY/NOVA-AI/commit/01a63207e956640209090d11059ce65466f959c9)
  **Author:** Evan Grinnell
  **Message:** Fix AUDIO_OUTPUT_INDEX value in Audio class to match configuration

- **Commit:** [b438a9d](https://github.com/S0L0GUY/NOVA-AI/commit/b438a9dba99566edb47ba58013e57e995d5e56f6)
  **Author:** Evan Grinnell
  **Message:** Quick tuner (#42)

* Revise README.md for clarity and detail, enhancing project description, features, prerequisites, installation, and setup instructions.

* Enhance configuration management by centralizing settings in constants.py, refactor related classes, and update usage across the codebase for improved maintainability and customization.

* Refactor constants for improved clarity and consistency, updating frame duration and sleep intervals in Whisper and Interruption settings.

- **Commit:** [0145cfc](https://github.com/S0L0GUY/NOVA-AI/commit/0145cfc6ce110ddbd1cd2d8eb4d7766c35ed812f)
  **Author:** Evan Grinnell
  **Message:** Revise README.md for clarity and detail, enhancing project description, features, prerequisites, installation, and setup instructions.

- **Commit:** [86af28c](https://github.com/S0L0GUY/NOVA-AI/commit/86af28cd1a49b71df238c834ce4b345609e5eb12)
  **Author:** Evan Grinnell
  **Message:** Refactor system prompt handling and update identity rules in prompts

- **Commit:** [7dd4050](https://github.com/S0L0GUY/NOVA-AI/commit/7dd40507b93e35e35feeff077da27ba6f5396997)
  **Author:** Evan Grinnell
  **Message:** Local IP and Model ID (#40)

- **Commit:** [e7e2667](https://github.com/S0L0GUY/NOVA-AI/commit/e7e266799158a21ff97c97a475bf4190c57f4c8b)
  **Author:** Evan Grinnell
  **Message:** Updated Documentation (#38)

* Updated Documentation

* Add resource monitor startup in main and remove from run_code

- **Commit:** [187a5a9](https://github.com/S0L0GUY/NOVA-AI/commit/187a5a97360b361755a6f3150348d9a64fd8235b)
  **Author:** Evan Grinnell
  **Message:** Enhance console output with color coding for better visibility and add system monitor functionality (#37)

- **Commit:** [435b370](https://github.com/S0L0GUY/NOVA-AI/commit/435b3706f6bf9288236a51013ef06daffa1a9765)
  **Author:** Evan Grinnell
  **Message:** Add time module import

- **Commit:** [aa76750](https://github.com/S0L0GUY/NOVA-AI/commit/aa7675067c2313b0d3542b6d2b78b88f7a11cb65)
  **Author:** Evan Grinnell
  **Message:** Asynchronous TTS Processing (#36)

* Refactor TextToSpeechManager to improve queue processing and add VRChatOSC support; update WhisperTranscriber to remove debug print statement; enhance system prompt instructions to clarify emoji usage and instruction adherence.

* Fixed Spelling Errors

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Updated nova.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [612372c](https://github.com/S0L0GUY/NOVA-AI/commit/612372c99d69003f0f977041029d52d75927e544)
  **Author:** Evan Grinnell
  **Message:** Update default voice name to "en-US-JennyNeural" and enhance system prompt with new reference guidelines

- **Commit:** [787e342](https://github.com/S0L0GUY/NOVA-AI/commit/787e3420bb90512383dde7380d5b48fc5bdb4ebd)
  **Author:** Evan Grinnell
  **Message:** Enhance TextToSpeechManager to filter out emojis and refactor SystemPrompt to improve prompt retrieval logic

- **Commit:** [558999b](https://github.com/S0L0GUY/NOVA-AI/commit/558999b0caf23c5093f8fe1f2e91821e35c3a680)
  **Author:** Evan Grinnell
  **Message:** Fix text chunking regex and update OSC typing indicator handling

- **Commit:** [34496ec](https://github.com/S0L0GUY/NOVA-AI/commit/34496ec53f2e6f6fa752f4e86706f6cdf9acbe7a)
  **Author:** Evan Grinnell
  **Message:** Added New Contributor

- **Commit:** [02dc9c8](https://github.com/S0L0GUY/NOVA-AI/commit/02dc9c82c8a88d5e3a652ba1dbd3c6ab39404e51)
  **Author:** Evan Grinnell
  **Message:** Whisper fixes (#34)

* Refactor code structure for improved readability and maintainability

* Fixed Small Errors

* Refactor output management; remove OutputManager class and implement TextToSpeechManager for Edge TTS integration

* Refactor JsonWrapper class; update read_json method to return Python objects and add whipe_json method for clearing JSON file contents

* Remove unused audio files: temp_audio.wav and tts_output.wav

* Add pattern to ignore all .wav files in the repository

* Removed Linting

- **Commit:** [147c79a](https://github.com/S0L0GUY/NOVA-AI/commit/147c79a92b2c30c0f6cecb14983d2f81828d6248)
  **Author:** Evan Grinnell
  **Message:** Updated TTS to EdgeTTS

