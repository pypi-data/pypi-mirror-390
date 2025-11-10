import logging
import random
import yt_dlp


class YouTubeFetcher:
    def __init__(self):
        self.ydl_opts_flat = {
            'quiet': True,
            'extract_flat': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'no_color': True
        }
        self.ydl_opts_full = {
            'quiet': True,
            'extract_flat': False,
            'no_warnings': True,
            'ignoreerrors': True,
            'no_color': True
        }

    def get_playlist_titles(self, url):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_flat) as ydl:
                info = ydl.extract_info(url, download=False)
            return [(e['title'], e.get('uploader', 'Unknown'), "YouTube", None)
                    for e in info['entries'] if e]
        except Exception as e:
            logging.error(f"Error fetching YouTube playlist: {e}")
            return []

    def search_similar_tracks(self, seed_tracks, limit=10):
        results = []
        sample = random.sample(seed_tracks, min(3, len(seed_tracks)))

        for title, artist, _, _ in sample:
            try:
                search_query = f"{artist} {title} audio"
                with yt_dlp.YoutubeDL(self.ydl_opts_full) as ydl:
                    search_results = ydl.extract_info(
                        f"ytsearch5:{search_query}", download=False
                    )
                    if search_results and 'entries' in search_results:
                        for entry in search_results['entries']:
                            if entry:
                                image_url = entry.get('thumbnail')
                                results.append((
                                    entry.get('title', 'Unknown'),
                                    entry.get('uploader', 'Unknown'),
                                    "YouTube",
                                    image_url
                                ))
                            if len(results) >= limit:
                                return results
            except Exception:
                continue

        return results