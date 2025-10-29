import pytest
import sys
from unittest.mock import patch
from main import main


def test_main(capsys):
    """Test that main() prints the expected message and usage."""
    with patch.object(sys, 'argv', ['main.py']):
        main()
    captured = capsys.readouterr()
    assert "Hello from gee-redlist-python!" in captured.out
    assert "Usage:" in captured.out
    assert "--test-auth" in captured.out


@patch('main.print_authentication_status')
def test_main_with_test_auth_flag(mock_print_auth, capsys):
    """Test that main() calls print_authentication_status when --test-auth is provided."""
    with patch.object(sys, 'argv', ['main.py', '--test-auth']):
        main()

    captured = capsys.readouterr()
    assert "Hello from gee-redlist-python!" in captured.out
    assert "Testing Earth Engine authentication..." in captured.out
    mock_print_auth.assert_called_once()
