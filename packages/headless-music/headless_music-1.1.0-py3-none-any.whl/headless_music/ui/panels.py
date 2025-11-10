from rich.panel import Panel
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich.layout import Layout
from utils.helpers import format_time, truncate_string

_CONTROLS_PANEL = None


def create_controls_panel():
    global _CONTROLS_PANEL
    if _CONTROLS_PANEL is None:
        _CONTROLS_PANEL = Panel(
            Text.from_markup(
                "[bold cyan]n[/bold cyan] next  •  [bold cyan]p[/bold cyan] prev  •  "
                "[bold cyan]space[/bold cyan] pause/play  •  [bold cyan]q[/bold cyan] quit  •  "
                "[bold cyan]c[/bold cyan] config",
                justify="center"
            ),
            border_style="dim"
        )
    return _CONTROLS_PANEL


def create_now_playing_panel(title, artist, source):
    source_color = "red" if source == "YouTube" else "green"

    title = truncate_string(title, 60)
    artist = truncate_string(artist, 40)

    display_text = Text.from_markup(
        f"\n[bold]{title}[/bold]\n[dim]{artist}[/dim]\n"
        f"Source: [{source_color}]{source}[/{source_color}]\n"
    )
    return Panel(display_text, title="Now Playing",
                 padding=(0, 2, 0, 2), border_style="dim")


def create_queue_panel(master_playlist, current_index):
    lines = []

    if 0 <= current_index < len(master_playlist):
        title, artist, _, _ = master_playlist[current_index]
        title = truncate_string(title, 30)
        artist = truncate_string(artist, 30)

        lines.append(Text.from_markup(f"[bold green] > {title}[/bold green]"))
        lines.append(Text.from_markup(f"   [dim]{artist}[/dim]"))
        lines.append(Text.from_markup("---"))

    end_idx = min(current_index + 11, len(master_playlist))

    if end_idx == current_index + 1 and len(master_playlist) > 0:
        lines.append(Text.from_markup("  [dim]Fetching more tracks...[/dim]"))
    else:
        for i in range(current_index + 1, end_idx):
            title, artist, _, _ = master_playlist[i]
            title = truncate_string(title, 30)
            artist = truncate_string(artist, 30)

            lines.append(Text.from_markup(f"   {i - current_index}. {title}"))
            lines.append(Text.from_markup(f"      [dim]{artist}[/dim]"))

    if not lines:
        return Panel(Text("  [dim]Loading queue...[/dim]"),
                     title="Queue", border_style="dim", padding=(1,1))

    return Panel(Text("\n").join(lines), title="Queue",
                 border_style="dim", padding=(1,1))

_progress_layout = None


def create_progress_panel(player):
    global _progress_layout

    try:
        time_pos = player.time_pos or 0
        duration = player.duration or 0
        percent = (time_pos / duration * 100) if duration else 0

        bar = ProgressBar(total=100, completed=percent, width=None,
                         complete_style="green", pulse=duration == 0)
        time_display = Text(f"{format_time(time_pos)} / {format_time(duration)}",
                           justify="right")
        icon = "⏸" if player.pause else "▶"

        if _progress_layout is None:
            _progress_layout = Layout()
            _progress_layout.split_row(
                Layout(name="icon", size=3),
                Layout(name="bar"),
                Layout(name="time", size=15)
            )

        _progress_layout["icon"].update(Text(f" {icon} "))
        _progress_layout["bar"].update(bar)
        _progress_layout["time"].update(time_display)

        return _progress_layout
    except Exception:
        return Layout(Text(""))

