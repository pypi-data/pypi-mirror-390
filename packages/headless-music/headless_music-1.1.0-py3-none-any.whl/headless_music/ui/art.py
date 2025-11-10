import io
import logging
import requests
from functools import lru_cache
from PIL import Image
from rich.text import Text
from rich.panel import Panel


@lru_cache(maxsize=32)
def generate_ascii_art(image_url, height):
    try:
        height = max(1, min(height, 30))
        width = height * 2

        response = requests.get(image_url, timeout=3)
        response.raise_for_status()

        with Image.open(io.BytesIO(response.content)) as img:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img = img.convert("RGB")

            ascii_lines = [None] * height

            for y in range(height):
                line_parts = []
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    line_parts.append(f"[rgb({r},{g},{b}) on rgb({r},{g},{b})]▀[/]")
                ascii_lines[y] = ''.join(line_parts)

            return Text.from_markup("\n".join(ascii_lines), justify="center")

    except Exception as e:
        logging.warning(f"Failed to generate ASCII art: {e}")
        return None

_PLACEHOLDER_CACHE = {}


def get_placeholder_art(height=8):
    if height in _PLACEHOLDER_CACHE:
        return _PLACEHOLDER_CACHE[height]

    base_art = [
        "╔══════════════╗",
        "║              ║",
        "║    [bold]🎵[/bold]        ║",
        "║              ║",
        "║   [dim]headless[/dim]   ║",
        "║   [dim]_music[/dim]    ║",
        "║              ║",
        "╚══════════════╝",
    ]
    base_height = len(base_art)
    scaled_art_lines = []

    if height <= 0:
        result = Text("")
    elif height < base_height:
        start_index = (base_height - height) // 2
        for i in range(height):
            scaled_art_lines.append(f"  [green]{base_art[start_index + i]}[/green]")
        result = Text.from_markup("\n".join(scaled_art_lines), justify="center")
    else:
        top_padding = (height - base_height) // 2
        bottom_padding = height - base_height - top_padding
        scaled_art_lines.extend([""] * top_padding)
        for line in base_art:
            scaled_art_lines.append(f"  [green]{line}[/green]")
        scaled_art_lines.extend([""] * bottom_padding)
        result = Text.from_markup("\n".join(scaled_art_lines), justify="center")

    _PLACEHOLDER_CACHE[height] = result
    return result


def create_ascii_art_panel(image_url, height, cache):
    cache_key = f"{image_url}_{height}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    if image_url:
        try:
            art = generate_ascii_art(image_url, height)
            if art:
                panel = Panel(art, border_style="dim", padding=(0, 0))
                cache.set(cache_key, panel)
                return panel
        except Exception:
            pass

    panel = Panel(get_placeholder_art(height), border_style="dim")
    return panel
