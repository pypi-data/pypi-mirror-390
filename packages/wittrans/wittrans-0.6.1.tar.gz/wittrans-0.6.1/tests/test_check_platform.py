import sys

from wittrans.functions import check_platform


def test_check_platform_linux(monkeypatch):
    """Test that check_platform() runs without exiting on Linux."""
    monkeypatch.setattr(sys, "platform", "linux")
    check_platform()  # Should not exit

    monkeypatch.setattr(sys, "platform", "linux2")
    check_platform()  # Should not exit


def test_check_platform_darwin(monkeypatch, capsys):
    """Test that check_platform() exits with the correct message on macOS."""
    monkeypatch.setattr(sys, "platform", "darwin")

    # Mock sys.exit to prevent actual exit
    exit_called = False

    def mock_exit(code):
        nonlocal exit_called
        exit_called = True
        assert code == 1

    monkeypatch.setattr(sys, "exit", mock_exit)

    check_platform()

    assert exit_called, "sys.exit() was not called"

    captured = capsys.readouterr()
    expected_message = (
        "wittrans must be run on a Linux distribution, macOS is not supported. Exiting."
    )
    assert expected_message in captured.out or expected_message in captured.err


def test_check_platform_windows(monkeypatch, capsys):
    """Test that check_platform() exits with the correct message on Windows."""
    monkeypatch.setattr(sys, "platform", "win32")

    # Mock sys.exit to prevent actual exit
    exit_called = False

    def mock_exit(code):
        nonlocal exit_called
        exit_called = True
        assert code == 1

    monkeypatch.setattr(sys, "exit", mock_exit)

    check_platform()

    assert exit_called, "sys.exit() was not called"

    captured = capsys.readouterr()
    expected_message = "wittrans must be run on a Linux distribution, Windows is not supported. Exiting."
    assert expected_message in captured.out or expected_message in captured.err
