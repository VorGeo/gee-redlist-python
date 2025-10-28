import pytest
from main import main


def test_main(capsys):
    """Test that main() prints the expected message."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from gee-redlist-python!\n"
