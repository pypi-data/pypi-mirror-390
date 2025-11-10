from rich.layout import Layout


def create_layout():
    layout = Layout()

    layout.split_row(
        Layout(name="sidebar", size=40),
        Layout(name="main", ratio=1)
    )

    layout["main"].split_column(
        Layout(name="art", ratio=1),
        Layout(name="now_playing", size=5),
        Layout(name="progress", size=1),
        Layout(name="footer", size=3)
    )

    return layout
