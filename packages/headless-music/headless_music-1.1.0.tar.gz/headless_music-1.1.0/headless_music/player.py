import logging
import queue
import threading
from mpv import MPV


class MusicPlayer:
    def __init__(self):
        self.mpv = MPV(
            ytdl=True,
            video=False,
            keep_open=False,
            keep_open_pause=False,
            cache=True,
            demuxer_max_bytes='50M',
            cache_secs=10
        )
        self.current_index = 0
        self.playlist = []
        self.command_queue = queue.Queue()
        self.is_running = True
        self._setup_observers()

    def _setup_observers(self):
        @self.mpv.property_observer('idle-active')
        def handle_song_end(_name, value):
            if value and self.is_running:
                self.command_queue.put("next")

    def play_track(self, index):
        if index < 0 or index >= len(self.playlist):
            if index >= len(self.playlist) and len(self.playlist) > 0:
                index = 0
            else:
                return False

        self.current_index = index
        title, artist, _, _ = self.playlist[self.current_index]

        try:
            query = f"{title} {artist} audio"
            self.mpv.play(f"ytdl://ytsearch1:{query}")
            self.mpv.pause = False
            return True
        except Exception as e:
            logging.error(f"Error playing track: {e}")
            self.command_queue.put("next")
            return False

    def next_track(self):
        return self.play_track(self.current_index + 1)

    def prev_track(self):
        return self.play_track(max(0, self.current_index - 1))

    def toggle_pause(self):
        self.mpv.pause = not self.mpv.pause

    def get_current_track(self):
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    def needs_queue_refresh(self, threshold=5):
        return len(self.playlist) - self.current_index < threshold

    def extend_playlist(self, tracks):
        self.playlist.extend(tracks)

    def quit(self):
        self.is_running = False
        try:
            self.mpv.quit()
        except Exception:
            pass