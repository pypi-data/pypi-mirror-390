from functools import lru_cache


@lru_cache(maxsize=128)
def format_time(seconds):
    if seconds is None or seconds < 0:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    return f"{m:02}:{s:02}"


def truncate_string(text, max_length, suffix="..."):
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix
