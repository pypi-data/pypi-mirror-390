# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.4] - 2025-11-07

This release is more about the user experience and robustness.

### Added

- /history and /full-history commands
- /clear to start a new conversation
- /goto to navigate in the histories
- /pass to cancel undo
- pageup and pagedown keybindings for history navigation
- color for the logger
- --log-file
- --no-foo options for all boolean options
- --dummy
- vibe README

### Changed

- tool confimation: enter=ok, something=cancel
- better batch/nonbatch tty/nontty handling
- better tool calls in markdown mode
- better benchmark reporting with token and time metrics
- libified Spinner
- renamed /retry to /redo
- better main loop
- better exception and error handling
- really improved the command line test suite
- refactorized test/utils.sh

### Fixed

- Not that much bugs in fact, things are chill now.


## [v0.1.3] - 2025-10-31

### Added

- Slash commands
- Native tool mode (new default). See --tool-mode
- Plugin system with --plugin
- Tool system with user-defined tools (--list-tools)
- White listed safe commands (cat, ls, etc.)
- Non-streaming mode for debugging API (--bulk)
- Better metrics (--export-metrics)
- Other new flags: --temperature, --version
- Test tasks `tests/debug_fib.sh` and `tests/crapto.sh`

### Changed

- Improved tool handling and error catching
- Refactored a lot of code
- Enhanced test suite with better error handling
- Enhanced tests analysis with better reporting and easier way to rerun tests
- Improved `tests/run_all_*.sh` helpers

### Fixed

- A lot of bugs

### Removed

- Old benchmark reporting mechanisms (crappy shell)


## [v0.1.2] - 2025-10-21

### Added

- Option `--list-models` to list available models
- Benchmark infrastructure with useful reporting
- `tests/analyseresults.py` for better test results and benchmark analysis
- `benchmark.md` the aggregation of benchmark results
- Test tasks: `tests/patch_file.sh` and `tests/smokeimages.sh`
- `tests/clitests.sh` to (black-box) test command line options
- Added `tests/rmlog.sh` tool to remove stale/broken test results

### Changed

- Move the main program to `llme/main.py`

### Fixed

- A lot of bugs

### Removed

- Option `--quiet`


## [v0.1.1] - 2025-10-18

### Added

- `--quit` to quit after processed all arguments prompts
- `--batch` to run non-interactively.
- `--plain` for no colors or tty fanciness.
- `--chat-output` and `--chat-input` to save and load chat sessions
- `--dump-config` to dump current config
- Support for multiple explicit configuration files (repeated `--config` option)
- Environment variable support for configuration
- Basic test and benchmark infrastructure

- Added basic test and benchmark infrastructure
- Added support for reasoning in messages
- Added `--dump-config` option
- Added `--chat-output` and `--chat-input` options
- Added configuration file precedence handling
- Added support for multiple explicit configuration files
- Added support for assets after prompts
- Added more logging capabilities

### Changed

- Move the main program to `llme/__init__.py`
- Enhanced server error reporting

### Fixed

- A lot of bugs


## [v0.1.0] - 2025-09-24

### Added

- Configuration file support
- Stream support (and remove non-streaming)
- Support for assets and file handling (including images)
- Basic command support with markdown
- `--yolo` to disable user confirmation
- `pyproject.toml` for build and packaging
- Logging system

### Changed

- Refactoring: classes and methods

### Removed

- Dropped rich because it's annoying
- `--hide-thinking` (unused)


[Unreleased]: https://github.com/example/project/compare/v0.1.2...HEAD
[v0.1.2]: https://github.com/example/project/compare/v0.1.1...v0.1.2
[v0.1.1]: https://github.com/example/project/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/example/project/commits/v0.1.0
