"""Common utility functions for LeapOCR SDK."""

from datetime import datetime


def parse_datetime(s: str | None) -> datetime:
    """Parse RFC3339 datetime string.

    Args:
        s: RFC3339 datetime string (e.g., "2023-12-25T10:30:00Z")

    Returns:
        datetime object (defaults to epoch if parse fails)
    """
    if s is None:
        # Return epoch as fallback
        return datetime.fromtimestamp(0)

    # Handle 'Z' timezone suffix by converting to +00:00
    # Python's fromisoformat doesn't support 'Z' directly
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # Fallback: try without timezone
        try:
            return datetime.fromisoformat(s.split("+")[0].split("Z")[0])
        except ValueError:
            # Return epoch as last resort
            return datetime.fromtimestamp(0)


def calculate_progress(status_data: dict) -> float:
    """Calculate progress percentage from status data.

    Args:
        status_data: Dictionary with 'processed_pages' and 'total_pages'

    Returns:
        Progress percentage (0-100)
    """
    processed = status_data.get("processed_pages", 0)
    total = status_data.get("total_pages", 0)

    if total <= 0:
        return 0.0

    progress = (processed / total) * 100.0
    return min(100.0, max(0.0, progress))
