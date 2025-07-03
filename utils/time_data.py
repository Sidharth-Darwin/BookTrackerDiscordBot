import re


def parse_time_to_minutes(time_str: str) -> int:
    time_str = time_str.strip().lower()

    if time_str.isdigit():
        total_minutes = int(time_str)
    else:
        match = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?', time_str)
        if not match:
            raise ValueError("Invalid time format")

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        total_minutes = hours * 60 + minutes

    if total_minutes > 10000:
        raise ValueError("Time too large to be valid")

    return total_minutes
