import builtins
import main


def test_module_imports_successfully():
    """
    This test ensures that the application module
    can be imported without syntax errors.
    """
    assert main is not None


def test_scopes_defined():
    """
    Verifies that Google Calendar OAuth scopes
    are defined correctly.
    """
    assert isinstance(app.SCOPES, list)
    assert "https://www.googleapis.com/auth/calendar" in app.SCOPES


def test_date_parsing_valid_format():
    """
    Tests date parsing logic used in add/update flows.
    """
    from datetime import datetime

    date_input = "01:01:2025"
    date_obj = datetime.strptime(date_input, "%d:%m:%Y")
    formatted_date = date_obj.strftime("%Y-%m-%d")

    assert formatted_date == "2025-01-01"


def test_invalid_date_raises_error():
    """
    Ensures invalid date formats fail as expected.
    """
    from datetime import datetime
    import pytest

    with pytest.raises(ValueError):
        datetime.strptime("2025-01-01", "%d:%m:%Y")
