import sys
import time
import select
import threading
from rich.console import Console
from rich.live import Live
import logging

# Import our modules
from config import (
    setup_logging, load_config, validate_config,
    setup_wizard, CONFIG_FILE
)
from player import MusicPlayer
from fetchers.spotify import SpotifyFetcher
from fetchers.youtube import YouTubeFetcher
from ui.layout import create_layout
from ui.panels import (
    create_controls_panel, create_now_playing_panel,
    create_queue_panel, create_progress_panel
)
from ui.art import create_ascii_art_panel
from utils.cache import panel_cache

console = Console()


def input_thread(player):
    """Handle keyboard input with adaptive polling."""
    poll_interval = 0.5

    while player.is_running:
        try:
            readable, _, _ = select.select([sys.stdin], [], [], poll_interval)
            if readable:
                char = sys.stdin.read(1)
                poll_interval = 0.1  # Fast response after input

                if char == 'n':
                    player.command_queue.put("next")
                elif char == 'p':
                    player.command_queue.put("prev")
                elif char == ' ':
                    player.command_queue.put("pause")
                elif char == 'q':
                    player.command_queue.put("quit")
                elif char == 'c':
                    player.command_queue.put("config")
            else:
                poll_interval = min(poll_interval * 1.5, 0.5)
        except Exception as e:
            logging.error(f"Input thread error: {e}")
            player.is_running = False


def refresh_queue(player, spotify_fetcher, youtube_fetcher):
    """Refresh queue with new recommendations."""
    if not player.needs_queue_refresh():
        return

    seed_tracks = player.playlist[
        max(0, player.current_index - 10):player.current_index + 1
    ]

    new_tracks = []

    if spotify_fetcher:
        new_tracks = spotify_fetcher.get_recommendations(seed_tracks, limit=15)

    if len(new_tracks) < 5 and youtube_fetcher:
        yt_tracks = youtube_fetcher.search_similar_tracks(seed_tracks, limit=10)
        new_tracks.extend(yt_tracks)

    if new_tracks:
        player.extend_playlist(new_tracks)
    else:
        # Loop playlist if no new tracks found
        player.extend_playlist(player.playlist[:20])


def main():
    """Main application loop."""
    setup_logging()

    config = load_config()
    if not validate_config(config):
        config = setup_wizard()
        if not config:
            return

    console.print("🎵 Initialising headless_music...", style="bold cyan")
    console.print(f"📡 Fetching {config['PLAYLIST_SOURCE'].title()} playlist...",
                  style="bold green")

    # Initialize fetchers
    spotify_fetcher = SpotifyFetcher(
        config['SPOTIFY_CLIENT_ID'],
        config['SPOTIFY_CLIENT_SECRET']
    )
    youtube_fetcher = YouTubeFetcher()

    # Fetch initial playlist
    if config['PLAYLIST_SOURCE'] == 'spotify':
        if not spotify_fetcher.client:
            console.print("[red]Failed to initialize Spotify. Exiting.[/red]")
            return
        initial_tracks = spotify_fetcher.get_playlist_tracks(config['PLAYLIST_URL'])
    else:
        initial_tracks = youtube_fetcher.get_playlist_titles(config['PLAYLIST_URL'])

    if not initial_tracks:
        console.print("[red]Failed to fetch playlist. Exiting.[/red]")
        return

    console.print(f"✓ Found {len(initial_tracks)} tracks", style="green")
    console.print("🎧 Fetching additional tracks...", style="bold green")

    # Fetch additional recommendations
    additional_tracks = []
    if spotify_fetcher.client:
        additional_tracks = spotify_fetcher.get_recommendations(initial_tracks, limit=30)
        if additional_tracks:
            console.print(f"✓ Added {len(additional_tracks)} tracks", style="green")

    # Initialize player
    player = MusicPlayer()
    player.playlist = initial_tracks + additional_tracks

    if not player.playlist:
        console.print("[red]No tracks available. Exiting.[/red]")
        return

    # Setup terminal
    try:
        import tty
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
    except Exception:
        old_settings = None

    # Start input thread
    input_handler = threading.Thread(
        target=input_thread,
        args=(player,),
        daemon=True
    )
    input_handler.start()

    console.print("\n✨ Starting playback...\n", style="bold magenta")
    time.sleep(0.5)

    # Create UI layout
    layout = create_layout()
    last_progress_update = time.time()
    force_refresh_counter = 0

    try:
        with Live(layout, console=console, screen=True, refresh_per_second=0.5) as live:
            # Initialize UI
            player.play_track(0)
            layout["footer"].update(create_controls_panel())

            # Initial UI update
            track = player.get_current_track()
            if track:
                title, artist, source, image_url = track
                available_height = max(1, console.height - 11)

                layout["art"].update(
                    create_ascii_art_panel(image_url, available_height, panel_cache)
                )
                layout["now_playing"].update(
                    create_now_playing_panel(title, artist, source)
                )
                layout["sidebar"].update(
                    create_queue_panel(player.playlist, player.current_index)
                )

            # Main loop
            while player.is_running:
                try:
                    cmd = player.command_queue.get(timeout=2.0)
                except:
                    cmd = None

                if cmd == "next":
                    refresh_queue(player, spotify_fetcher, youtube_fetcher)
                    if player.next_track():
                        track = player.get_current_track()
                        if track:
                            title, artist, source, image_url = track
                            available_height = max(1, console.height - 11)

                            layout["art"].update(
                                create_ascii_art_panel(image_url, available_height, panel_cache)
                            )
                            layout["now_playing"].update(
                                create_now_playing_panel(title, artist, source)
                            )
                            layout["sidebar"].update(
                                create_queue_panel(player.playlist, player.current_index)
                            )
                    force_refresh_counter = 0

                elif cmd == "prev":
                    if player.prev_track():
                        track = player.get_current_track()
                        if track:
                            title, artist, source, image_url = track
                            available_height = max(1, console.height - 11)

                            layout["art"].update(
                                create_ascii_art_panel(image_url, available_height, panel_cache)
                            )
                            layout["now_playing"].update(
                                create_now_playing_panel(title, artist, source)
                            )
                            layout["sidebar"].update(
                                create_queue_panel(player.playlist, player.current_index)
                            )
                    force_refresh_counter = 0

                elif cmd == "pause":
                    player.toggle_pause()
                    force_refresh_counter = 0

                elif cmd == "config":
                    player.is_running = False
                    player.mpv.pause = True
                    live.stop()
                    console.clear()
                    new_config = setup_wizard()
                    if new_config:
                        console.print("\n[yellow]Please restart headless_music to apply new settings.[/yellow]")
                    break

                elif cmd == "quit":
                    break

                # Update progress every 2 seconds
                current_time = time.time()
                if current_time - last_progress_update >= 2.0:
                    try:
                        layout["progress"].update(create_progress_panel(player.mpv))
                        last_progress_update = current_time
                    except Exception:
                        pass

                # Periodic forced refresh
                force_refresh_counter += 1
                if force_refresh_counter >= 10:
                    live.refresh()
                    force_refresh_counter = 0

                # Sleep when idle
                if cmd is None:
                    time.sleep(0.2)

    except KeyboardInterrupt:
        player.is_running = False

    finally:
        player.quit()

        # Restore terminal
        if old_settings:
            try:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

        console.clear()
        console.print("\nheadless_music stopped. goodbye! 👋 \n", style="bold yellow")


if __name__ == "__main__":
    main()