# Commit History

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

- **Commit:** [a787e92](https://github.com/S0L0GUY/NOVA-AI/commit/a787e9218b87f26106c4e1438518b681b1318c9d)
  **Author:** Evan Grinnell
  **Message:** Refactor WhisperTranscriber class; update audio input index and improve silence detection

- **Commit:** [d812229](https://github.com/S0L0GUY/NOVA-AI/commit/d812229ae79940acbcd2e658371c86115c21d2fc)
  **Author:** Evan Grinnell
  **Message:** Refactor requirements and update network configurations; suppress warnings in main.py

- **Commit:** [ce73fcd](https://github.com/S0L0GUY/NOVA-AI/commit/ce73fcddc09b8f3496df4af744dacde6f84122dc)
  **Author:** Evan Grinnell
  **Message:** Created a Vertual Envionment

- **Commit:** [17bdb6e](https://github.com/S0L0GUY/NOVA-AI/commit/17bdb6e2cfb8c07c12b270799ec8a34f61d6c348)
  **Author:** Evan Grinnell
  **Message:** 29 update constants format (#30)

* Refactor constants into classes for better organization and clarity

* Fix method signature in JsonWrapper and update error handling in HTTP server

* Refactor constants into classes for better organization and clarity

* Fix method signature in JsonWrapper and update error handling in HTTP server

* Enhance documentation and improve code readability across multiple modules

* Remove redundant methods and comments from VRChatOSC class for improved clarity

* Refactor WhisperTranscriber initialization and silence duration; update constant references in main and add static methods to configuration classes

* Refactor constant references to improve code organization and readability across multiple modules

- **Commit:** [ce3bde3](https://github.com/S0L0GUY/NOVA-AI/commit/ce3bde31a7a69c49f34355c960ded541d5bb4729)
  **Author:** Evan Grinnell
  **Message:** 31 add pylance cli check (#32)

* Enhance documentation and improve code readability across multiple modules

* Reorder import statements for consistency and clarity

* Enhance Python linting workflow to include score evaluation and exit status based on pylint results

- **Commit:** [4910f94](https://github.com/S0L0GUY/NOVA-AI/commit/4910f942b7b713bb7ccc5975befda0b70d3a99f5)
  **Author:** Evan Grinnell
  **Message:** Update audio settings and add voice selection in TTS function (#25)

- **Commit:** [ae2d905](https://github.com/S0L0GUY/NOVA-AI/commit/ae2d9050ccad051f1a1e655a071bafbc2e10ee50)
  **Author:** Evan Grinnell
  **Message:** Fix Audio Playback Issues (#17)

* Fix Audio Playback Issues

Fixes #16

Update `play_audio` function to maintain original channel configuration.

* Change `play_audio` function in `nova.py` to read the audio file with `always_2d=False`.
* Update `play_tts` function to use the updated `play_audio` function.

---

For more details, open the [Copilot Workspace session](https://copilot-workspace.githubnext.com/S0L0GUY/NOVA-AI/issues/16?shareId=XXXX-XXXX-XXXX-XXXX).

* Update audio settings and enhance device listing

* Format output for audio device listing to improve readability

- **Commit:** [89b773f](https://github.com/S0L0GUY/NOVA-AI/commit/89b773f71980d186a4eec93dd7bb5204ee7f08b9)
  **Author:** Evan Grinnell
  **Message:** Added Re-Factoring Form (#24)

- **Commit:** [580db32](https://github.com/S0L0GUY/NOVA-AI/commit/580db32ef64d756a70b50786cad77206fa84dd01)
  **Author:** Evan Grinnell
  **Message:** Update commits.md

:yippie:

- **Commit:** [72f70e0](https://github.com/S0L0GUY/NOVA-AI/commit/72f70e079664b5792c6d59e3010bbe033ed00790)
  **Author:** Evan Grinnell
  **Message:** 11 delete and re code nova (#14)

* Got Started on Re-Coding Nova

* Finished Creating Basic Code (Needs to be Tested)

* Imported Bad Words

Co-Authored-By: DuckSong510 <179771719+DuckSong510@users.noreply.github.com>

* Updated Goals

* Updated README.md

* Updated Constants

* Fixed Issues in Code

* Added Ability to Get Recent Commits

* Updated TTS Command

* Updated OSC and TTS

TTS still does not work, but OSC does.

* Made attempts toward making tts work

* audio output still does not work -_-

* Flake8

Formatted code to flake 8 specifications.

* Removed Cross Class Contamination

'system_prompt.py' was trying to use 'JsonWrapper' and the program did not like that.

* Added 'Start Xvfb' to 'python-lint.yml'

* Update python-lint.yml

* Spelling Errors.

Updated a spelling error.

* Update requirements.txt

* Update python-lint.yml

Lessoned the rules.

* Update python-lint.yml

* Removed 'pylint'

pylint makes me so sad

---------

Co-authored-by: DuckSong510 <179771719+DuckSong510@users.noreply.github.com>

