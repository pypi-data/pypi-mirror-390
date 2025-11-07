"""
Unit tests for validators
"""

import pytest
from datetime import datetime
from trello_cli.utils.validators import validate_date, validate_color, validate_non_empty


def test_validate_date_with_full_timestamp():
    """Test date validation with full ISO timestamp"""
    result = validate_date("2025-10-27T14:30:00")
    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 10
    assert result.day == 27
    assert result.hour == 14
    assert result.minute == 30


def test_validate_date_with_date_only():
    """Test date validation with date only (should default to 17:00)"""
    result = validate_date("2025-10-27")
    assert isinstance(result, datetime)
    assert result.year == 2025
    assert result.month == 10
    assert result.day == 27
    assert result.hour == 17
    assert result.minute == 0


def test_validate_date_invalid_format():
    """Test that invalid date format raises SystemExit"""
    with pytest.raises(SystemExit):
        validate_date("invalid-date")


def test_validate_color_valid():
    """Test valid color validation"""
    valid_colors = ['yellow', 'purple', 'blue', 'red', 'green', 'orange', 'black', 'sky', 'pink', 'lime']
    for color in valid_colors:
        assert validate_color(color) == color


def test_validate_color_invalid():
    """Test that invalid color raises SystemExit"""
    with pytest.raises(SystemExit):
        validate_color("invalid-color")


def test_validate_non_empty_valid():
    """Test non-empty validation with valid input"""
    assert validate_non_empty("  test  ", "field") == "test"


def test_validate_non_empty_invalid():
    """Test that empty string raises SystemExit"""
    with pytest.raises(SystemExit):
        validate_non_empty("", "field")

    with pytest.raises(SystemExit):
        validate_non_empty("   ", "field")
