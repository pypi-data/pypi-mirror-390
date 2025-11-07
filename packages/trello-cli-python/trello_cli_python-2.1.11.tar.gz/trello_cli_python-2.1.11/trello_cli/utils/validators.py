"""
Input validation utilities
"""

import sys
from datetime import datetime


VALID_COLORS = [
    'yellow', 'purple', 'blue', 'red', 'green',
    'orange', 'black', 'sky', 'pink', 'lime'
]


def validate_date(date_string):
    """
    Validate and parse date string

    Args:
        date_string: Date in format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS

    Returns:
        datetime object

    Raises:
        SystemExit if invalid
    """
    try:
        if 'T' in date_string:
            return datetime.fromisoformat(date_string)
        else:
            # If only date, set to 17:00 (end of work day)
            return datetime.fromisoformat(f"{date_string}T17:00:00")
    except ValueError:
        print(f"❌ Invalid date format: {date_string}")
        print("   Expected: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
        sys.exit(1)


def validate_color(color):
    """
    Validate Trello label color

    Args:
        color: Color name

    Returns:
        color if valid

    Raises:
        SystemExit if invalid
    """
    if color not in VALID_COLORS:
        print(f"❌ Invalid color: {color}")
        print(f"   Valid colors: {', '.join(VALID_COLORS)}")
        sys.exit(1)
    return color


def validate_non_empty(value, field_name):
    """
    Validate that a value is not empty

    Args:
        value: Value to check
        field_name: Name of field for error message

    Returns:
        value if valid

    Raises:
        SystemExit if empty
    """
    if not value or not value.strip():
        print(f"❌ {field_name} cannot be empty")
        sys.exit(1)
    return value.strip()
