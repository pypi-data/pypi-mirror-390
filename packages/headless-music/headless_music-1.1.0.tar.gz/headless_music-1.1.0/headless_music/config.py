import json
import logging
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

CONFIG_FILE = Path.home() / ".headless_music_config.json"
LOG_FILE = Path.home() / ".headless_music.log"


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load config: {e}")
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving config: {e}")
        console.print(f"[red]Error saving config: {e}[/red]")
        return False


def validate_config(config):
    required = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET',
                'PLAYLIST_SOURCE', 'PLAYLIST_URL']
    missing = [key for key in required if not config.get(key)]

    if missing:
        console.print(f"[red]Missing configuration: {', '.join(missing)}[/red]")
        return False
    return True


def setup_wizard():
    console.clear()
    console.print("=" * 60, style="cyan")
    console.print("🎵 Welcome to headless_music Setup!",
                  style="bold cyan", justify="center")
    console.print("=" * 60, style="cyan")
    console.print()

    config = load_config()

    console.print("📱 [bold]Spotify API Credentials[/bold]")
    console.print("   Get these from: https://developer.spotify.com/dashboard",
                  style="dim")
    console.print()

    spotify_id = Prompt.ask(
        "   Spotify Client ID",
        default=config.get('SPOTIFY_CLIENT_ID', '')
    )
    spotify_secret = Prompt.ask(
        "   Spotify Client Secret",
        default=config.get('SPOTIFY_CLIENT_SECRET', ''),
        password=True
    )

    console.print()
    console.print("🎧 [bold]Playlist Source[/bold]")
    console.print()

    source_choice = Prompt.ask(
        "   Choose your playlist source",
        choices=["spotify", "youtube"],
        default=config.get('PLAYLIST_SOURCE', 'spotify')
    )

    console.print()

    if source_choice == "spotify":
        console.print("   Enter your Spotify playlist URL or URI", style="dim")
        console.print("   Example: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
                      style="dim")
        playlist_url = Prompt.ask("   Spotify Playlist URL/URI")
    else:
        console.print("   Enter your YouTube playlist URL", style="dim")
        console.print("   Example: https://www.youtube.com/playlist?list=...",
                      style="dim")
        playlist_url = Prompt.ask("   YouTube Playlist URL")

    console.print()

    new_config = {
        'SPOTIFY_CLIENT_ID': spotify_id,
        'SPOTIFY_CLIENT_SECRET': spotify_secret,
        'PLAYLIST_SOURCE': source_choice,
        'PLAYLIST_URL': playlist_url
    }

    if save_config(new_config):
        console.print("✓ Configuration saved!", style="bold green")
        console.print(f"   Config location: {CONFIG_FILE}", style="dim")
        console.print(f"   Log location: {LOG_FILE}", style="dim")
    else:
        console.print("⚠️  Could not save configuration.", style="yellow")

    console.print()
    if Confirm.ask("Start headless_music now?", default=True):
        return new_config
    else:
        console.print("👋 Run this script again when you're ready!", style="cyan")
        return None