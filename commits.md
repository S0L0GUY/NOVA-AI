# Commit History

- **Commit:** [9561dac](https://github.com/S0L0GUY/NOVA-AI/commit/9561dacb1ffa917e5e480b9eb6e0cab458caf04f)
  **Author:** Evan Grinnell
  **Message:** Add Audio Caching (#96)

* Add audio generation caching functionality and update constants

* Remove merge conflict markers from vision_log.json

* Refactor audio generation code for improved readability and maintainability

* Update json_files/vision_log.json

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [c1864be](https://github.com/S0L0GUY/NOVA-AI/commit/c1864bee87d282d45fc670436a86259dc594e85a)
  **Author:** Evan Grinnell
  **Message:** 93 use orjson instead of json (#97)

* Replace json with orjson for improved performance in JsonWrapper class

* Built Files

* Update classes/json_wrapper.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [3542b4b](https://github.com/S0L0GUY/NOVA-AI/commit/3542b4b766d26a7e4373c442264a10845d7d1e8f)
  **Author:** Evan Grinnell
  **Message:** Update README.md with new link for discord

- **Commit:** [dcef739](https://github.com/S0L0GUY/NOVA-AI/commit/dcef739ecb8d0e2587c46032f83a908db08053db)
  **Author:** Evan Grinnell
  **Message:** 85 update vision to genai (#92)

* Enable vision system and update model to Gemini 2.5; log errors during analysis

* Integrate GenAI client into VisionManager and VisionAnalyzer; update vision log with new analysis output

* Refactor VisionManager to remove direct GenAI client dependency; update vision log with new environment description

* Refactor VisionSystem to use adapter for GenAI client creation; update VisionAnalyzer to fix prompt handling

* Update classes/vision_manager.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update constants.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Sorted Imports

* Fix import order in vision_manager.py

* Refactor imports in vision_system.py for clarity and consistency

* Reorder imports in vision_system.py and update vision_log.json with initial log entries

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- **Commit:** [0fbae25](https://github.com/S0L0GUY/NOVA-AI/commit/0fbae25bb407814f6b022afadee3043c9900bb55)
  **Author:** Evan Grinnell
  **Message:** Update documentation and environment variables for GenAI integration (#90)

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

