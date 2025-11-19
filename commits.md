# Commit History

- **Commit:** [c43192d](https://github.com/S0L0GUY/NOVA-AI/commit/c43192d3e0724b9e243477bad55ab7bfaae272a4)
  **Author:** Evan Grinnell
  **Message:** Change queued transcription model from 'genai' to 'whisper'

- **Commit:** [c30ac12](https://github.com/S0L0GUY/NOVA-AI/commit/c30ac12b01f644ebcde40e02316fb1a45a3cea5e)
  **Author:** Evan Grinnell
  **Message:** Update README with Markdown formatting (#87)

- **Commit:** [12a5f86](https://github.com/S0L0GUY/NOVA-AI/commit/12a5f8675802235727749de87fe236875fa3ee75)
  **Author:** Evan Grinnell
  **Message:** Update README with new formatting and content

- **Commit:** [2b10618](https://github.com/S0L0GUY/NOVA-AI/commit/2b10618399145136c8d539e2692c9d46d3b119e7)
  **Author:** Evan Grinnell
  **Message:** Refactor README for clarity and support details

Updated README to improve formatting and add support information.

- **Commit:** [e7e0330](https://github.com/S0L0GUY/NOVA-AI/commit/e7e0330eae9431c30a9152c7437d7768719b0294)
  **Author:** Evan Grinnell
  **Message:** Update Adapter Logic (#83)

* Refactor initialization logic into adapters for better modularity and error handling

* Update SpeechRecognitionConfig to use GenAI model and adjust VAD aggressiveness

* Condense logging configuration setup in main.py for improved readability

* Sorted Imports

* Sorted Imports (again)

- **Commit:** [615350b](https://github.com/S0L0GUY/NOVA-AI/commit/615350b5acbc7ee5b470bd44ecad79d5cea8307f)
  **Author:** Evan Grinnell
  **Message:** Add GenAI STT (#80)

* Refactor speech recognition components: remove WhisperTranscriber, introduce SpeechToTextHandler, and update configuration settings.

* Fix string formatting in SpeechToTextHandler and remove unnecessary blank line

* Fix import order in speech_to_text.py by moving genai import to the correct position

* Fix import order in nova.py by moving JsonWrapper import to the correct position

* Update constants.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Fix import order in nova.py by moving JsonWrapper import to the correct position

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [567b10e](https://github.com/S0L0GUY/NOVA-AI/commit/567b10e6ae64c3aba00da688df93896ed9a219a0)
  **Author:** Evan Grinnell
  **Message:** Mad NOVA-AI (#78)

* Refactor prompt structure by removing emojis and consolidating language rules for clarity

* Add boundary parameter to edge_tts.Communicate for improved audio generation

- **Commit:** [1be2904](https://github.com/S0L0GUY/NOVA-AI/commit/1be2904c575926255a42d8490360023436850206)
  **Author:** Evan Grinnell
  **Message:** GenAI Integration (#76)

* Refactor JSON handling and update dependencies for Google GenAI integration

* Refactor generate_content call for improved readability

* Added Clearer Documentation

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update nova.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update nova.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [0c55cbe](https://github.com/S0L0GUY/NOVA-AI/commit/0c55cbee55c31de30d039bf98cd5715163ad6ab0)
  **Author:** Evan Grinnell
  **Message:** Use Faster Whisper (#73)

* Refactor Whisper model integration to use faster-whisper and update requirements

* Sorted Imports

* Fix import order by moving WhisperModel import to the correct position

* Update VAD aggressiveness in WhisperSettings and refine system prompt formatting

* Update WhisperSettings to change model size from "tiny" to "base"

* Updated Segment Handling

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Segment Spacing

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update commit history with recent changes and enhancements

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [c6cab19](https://github.com/S0L0GUY/NOVA-AI/commit/c6cab1923b5263b732c1838ec923ca1c08f659b9)
  **Author:** Evan Grinnell
  **Message:** 69 remove resource monitor (#70)

* Remove ResourceMonitor class and related functionality from the project

* Update compiled Python files in __pycache__ directory

* Removed Unused Imports

- **Commit:** [9ed2932](https://github.com/S0L0GUY/NOVA-AI/commit/9ed293216e26dc0685672e502057a5a6ea45ff35)
  **Author:** Evan Grinnell
  **Message:** Merge branch 'main' of https://github.com/S0L0GUY/NOVA-AI

- **Commit:** [3eee96b](https://github.com/S0L0GUY/NOVA-AI/commit/3eee96b0310c6f7a04a5ffb3ee352c165198558e)
  **Author:** Evan Grinnell
  **Message:** Enhance voice input handling by passing OSC instance to get_voice_input method

- **Commit:** [4c20997](https://github.com/S0L0GUY/NOVA-AI/commit/4c20997c9d8d826da0c76da8a03dbdcfba6da849)
  **Author:** Evan Grinnell
  **Message:** Updated ReadMe (#66)

- **Commit:** [ee52442](https://github.com/S0L0GUY/NOVA-AI/commit/ee5244276b8668ad1a21ec0408892d050a4d51fd)
  **Author:** Copilot
  **Message:** Add comprehensive code quality checks with GitHub Actions workflows (#65)

* Initial plan

* Add comprehensive code quality checks with GitHub Actions workflows

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Add quick start guide for code quality checks

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Address code review feedback on documentation

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Updated With Black Formatter

* Updated Black Formatting

* Fix indentation error and apply code formatting (Black, isort)

Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>

* Update compiled Python files in __pycache__ directory

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: S0L0GUY <155865196+S0L0GUY@users.noreply.github.com>
Co-authored-by: Evan Grinnell <worldevan8@gmail.com>

- **Commit:** [6759f5a](https://github.com/S0L0GUY/NOVA-AI/commit/6759f5aba4dbbfb1c8b272f9dca6b176a92bfe7c)
  **Author:** Evan Grinnell
  **Message:** Updated Commit History

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

