def time_str_to_seconds(time_str: str) -> float:
    """Convert 'mm:ss' string to float seconds."""
    try:
        parts = time_str.strip().split(":")
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            return float(time_str)
    except Exception as e:
        raise ValueError(f"Invalid time format: {time_str}")
