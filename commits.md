# Commit History

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

- **Commit:** [a8352d2](https://github.com/S0L0GUY/NOVA-AI/commit/a8352d264ccab37d5c2ba4eac26de714ba547013)
  **Author:** Evan Grinnell
  **Message:** 12 add linting on code pushpr (#13)

* Added CL Linting

* Updated YML file

* Added 'requirememts.txt'

* Removed Unneeded Requirement

* Added Needed Dependency

* Added espeak to requirements

* Update requirements.txt

* Update python-lint.yml

* Removed unused Import

* Update nova_placement.py

* Deleted unneeded files

* Update http_server.py

* Update python-lint.yml

* Update python-lint.yml

* flake8

* Flake 8 Formatting

* Flake 8 Formatting

* Flake 8 Formatting

* Update http_server.py

* Skip 'http_server.py'

* Update python-lint.yml

- **Commit:** [7c582c9](https://github.com/S0L0GUY/NOVA-AI/commit/7c582c90da9a54ab133dc11df02b6e0e506a3818)
  **Author:** Evan Grinnell
  **Message:** Added Duck Song to 'README.md' (#10)

- **Commit:** [610cc88](https://github.com/S0L0GUY/NOVA-AI/commit/610cc88718ced1ed1d484b59b86978228136ec8d)
  **Author:** DuckSong510
  **Message:** Updated Bad Words (#9)

* Updated Bad Words

* Removed Empty Line

- **Commit:** [47cf480](https://github.com/S0L0GUY/NOVA-AI/commit/47cf4801459474250a8f2552f400cbb12ed22fbf)
  **Author:** Evan Grinnell
  **Message:** Updated issue templates

- **Commit:** [5dfde79](https://github.com/S0L0GUY/NOVA-AI/commit/5dfde79461cd5bd39febe0f2485da28e8a05830f)
  **Author:** Evan Grinnell
  **Message:** Added Contributions to 'README.md'

- **Commit:** [b624035](https://github.com/S0L0GUY/NOVA-AI/commit/b624035e0071d67468c4321c0c7a8b14e8356aa4)
  **Author:** Evan Grinnell
  **Message:** Merge pull request #5 from S0L0GUY/3-create-a-constants-file

Added Constants File

- **Commit:** [7b1b739](https://github.com/S0L0GUY/NOVA-AI/commit/7b1b7394716f1f1c28ffaa7da44055b4bcb2adec)
  **Author:** Evan Grinnell
  **Message:** Added Constants File

- **Commit:** [0feca84](https://github.com/S0L0GUY/NOVA-AI/commit/0feca84a69237c34bf974839caa823ad5d730d13)
  **Author:** Evan Grinnell
  **Message:** Merge pull request #4 from S0L0GUY/Make-Auto-Placement-Better

Added Functions to Make Placement More Editable

- **Commit:** [3f719ef](https://github.com/S0L0GUY/NOVA-AI/commit/3f719ef3664aaec6e68d5ae1209b2cfebc1bb46e)
  **Author:** Evan Grinnell
  **Message:** Added Functions to Make Placement More Editable

- **Commit:** [52c7f10](https://github.com/S0L0GUY/NOVA-AI/commit/52c7f10225bd3511de0181cd32c5f6e3c45b891f)
  **Author:** Evan Grinnell
  **Message:** Make Prompts Useable

- **Commit:** [04829e4](https://github.com/S0L0GUY/NOVA-AI/commit/04829e486ecd743c0d7df6e262c599ca06d40ef5)
  **Author:** Evan Grinnell
  **Message:** Merge pull request #2 from S0L0GUY/1-make-nova-speak-more-like-a-human

Made NOVA Cooler

