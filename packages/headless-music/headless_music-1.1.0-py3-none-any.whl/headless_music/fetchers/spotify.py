import os
import logging
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheFileHandler


cache_path = os.path.join(os.path.expanduser("~"), ".cache_headless_music")
cache_handler = CacheFileHandler(cache_path=cache_path)


class SpotifyFetcher:
    """Handle all Spotify API interactions."""

    def __init__(self, client_id, client_secret):
        self.client = None
        self.client_id = client_id
        self.client_secret = client_secret
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Spotify client with credentials."""
        try:
            self.client = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    cache_handler=cache_handler
                ),
                requests_timeout=5
            )
            logging.info("Spotify client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Spotify: {e}")
            self.client = None

    def get_playlist_tracks(self, playlist_url):
        """Fetch all tracks from a Spotify playlist."""
        if not self.client:
            return []

        try:
            playlist_id = self._extract_playlist_id(playlist_url)
            results = []
            offset = 0

            while True:
                response = self.client.playlist_tracks(playlist_id, offset=offset, limit=100)
                for item in response['items']:
                    if item['track']:
                        track = item['track']
                        image_url = (track['album']['images'][-1]['url']
                                   if track['album']['images'] else None)
                        results.append((
                            track['name'],
                            track['artists'][0]['name'],
                            "Spotify",
                            image_url
                        ))

                if not response['next']:
                    break
                offset += 100

            logging.info(f"Fetched {len(results)} tracks from Spotify")
            return results
        except Exception as e:
            logging.error(f"Error fetching Spotify playlist: {e}")
            return []

    def get_recommendations(self, seed_tracks, limit=20):
        """Get Spotify recommendations based on seed tracks."""
        if not self.client:
            return []

        results = []
        seen_ids = set()

        sample_size = min(len(seed_tracks), 5)
        sampled = random.sample(seed_tracks, sample_size)

        for title, artist, _, _ in sampled:
            if len(results) >= limit:
                break

            try:
                search_results = self.client.search(
                    q=f"{title} {artist}", type="track", limit=1
                )
                if search_results['tracks']['items']:
                    seed_id = search_results['tracks']['items'][0]['id']
                    try:
                        recs = self.client.recommendations(seed_tracks=[seed_id], limit=5)
                        for track in recs['tracks']:
                            track_id = track['id']
                            if track_id not in seen_ids:
                                image_url = (track['album']['images'][-1]['url']
                                           if track['album']['images'] else None)
                                results.append((
                                    track['name'],
                                    track['artists'][0]['name'],
                                    "Spotify",
                                    image_url
                                ))
                                seen_ids.add(track_id)
                    except Exception:
                        pass
            except Exception:
                continue

        # Fallback: related artists
        if len(results) < limit:
            results.extend(self._get_related_artist_tracks(
                sampled, limit - len(results), seen_ids
            ))

        logging.info(f"Generated {len(results)} recommendations")
        return results

    def _get_related_artist_tracks(self, seed_tracks, limit, seen_ids):
        """Get tracks from related artists."""
        results = []

        for title, artist, _, _ in seed_tracks:
            if len(results) >= limit:
                break

            try:
                artist_results = self.client.search(
                    q=f"artist:{artist}", type="artist", limit=1
                )
                if artist_results['artists']['items']:
                    artist_id = artist_results['artists']['items'][0]['id']
                    related = self.client.artist_related_artists(artist_id)

                    for rel_artist in related['artists'][:3]:
                        top_tracks = self.client.artist_top_tracks(rel_artist['id'])
                        for track in top_tracks['tracks'][:2]:
                            track_id = track['id']
                            if track_id not in seen_ids:
                                image_url = (track['album']['images'][-1]['url']
                                           if track['album']['images'] else None)
                                results.append((
                                    track['name'],
                                    track['artists'][0]['name'],
                                    "Spotify",
                                    image_url
                                ))
                                seen_ids.add(track_id)
                                if len(results) >= limit:
                                    return results
            except Exception:
                continue

        return results

    @staticmethod
    def _extract_playlist_id(playlist_url):
        """Extract playlist ID from various URL formats."""
        if 'spotify.com' in playlist_url:
            return playlist_url.split('playlist/')[-1].split('?')[0]
        elif 'spotify:playlist:' in playlist_url:
            return playlist_url.split('spotify:playlist:')[-1]
        return playlist_url

