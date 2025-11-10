# headless_music

A Spotify-inspired, terminal-based music player. `headless_music` brings music to your terminal with full-color ASCII album art and an endless recommendation queue.

## Features

- Spotify-inspired terminal UI with a modern 3-panel layout (built with `rich`).
- Color ASCII album art (when available from Spotify).
- Playlist-first playback for Spotify or YouTube playlists.
- Endless radio mode that queues recommendations after the playlist ends.
- Smooth, pulsing progress bar showing playback and loading status.
- First-run configuration wizard for easy setup.
- Cross-platform: runs on systems with Python and `mpv`.

## Prerequisites

`mpv` is required as the audio backend.

### macOS (Homebrew)
```bash
brew install mpv
```

### Ubuntu/Debian
```bash
sudo apt update && sudo apt install mpv
```

### Windows (Chocolatey)
```bash
choco install mpv
```

## Installation

To install, simply use the Python package manager pip:
```bash
pip install headless_music
```

## Usage

To start the player, type into your terminal
```bash
headless_music
```

On first launch a setup wizard will walk you through adding your Spotify API credentials. Obtain these from the Spotify Developer Dashboard: [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)

## Controls

| Key   | Action                                           |
| ----- | ------------------------------------------------ |
| Space | Play / Pause                                     |
| n     | Next track                                       |
| p     | Previous track                                   |
| c     | Re-run the configuration wizard (stops playback) |
| q     | Quit                                             |

## Configuration

* Spotify API credentials (Client ID, Client Secret) are required for full functionality.
* The configuration wizard writes credentials to a user config file (see `config` in repo for format).
* `mpv` path and additional mpv options can be set in the config.


## Contribution

Contributions are welcome. Please open issues for bugs or feature requests and submit pull requests against `main`. Follow the existing code style and include tests for new functionality.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

























