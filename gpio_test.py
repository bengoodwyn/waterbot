import pytest
from unittest.mock import patch

import gpio

@patch("os.system")
def test_mode_out(mock_system):
    mock_system.return_value = 0
    gpio.mode_out(7)
    mock_system.assert_called_once_with("gpio mode 7 out")

@patch("os.system")
def test_mode_out_handles_errors(mock_system):
    mock_system.return_value = 1
    with pytest.raises(Exception):
        gpio.mode_out(7)
    mock_system.assert_called_once_with("gpio mode 7 out")

@patch("os.system")
def test_mode_in(mock_system):
    mock_system.return_value = 0
    gpio.mode_in(5)
    mock_system.assert_called_once_with("gpio mode 5 in")

@patch("os.system")
def test_mode_in_handles_errors(mock_system):
    mock_system.return_value = 1
    with pytest.raises(Exception):
        gpio.mode_in(5)
    mock_system.assert_called_once_with("gpio mode 5 in")

@patch("os.system")
def test_on(mock_system):
    mock_system.return_value = 0
    gpio.on(3)
    mock_system.assert_called_once_with("gpio write 3 0")

@patch("os.system")
def test_on_handles_errors(mock_system):
    mock_system.return_value = 1
    with pytest.raises(Exception):
        gpio.on(3)
    mock_system.assert_called_once_with("gpio write 3 0")

@patch("os.system")
def test_off(mock_system):
    mock_system.return_value = 0
    gpio.off(2)
    mock_system.assert_called_once_with("gpio write 2 1")

@patch("os.system")
def test_off_handles_errorrs(mock_system):
    mock_system.return_value = 1
    with pytest.raises(Exception):
        gpio.off(2)
    mock_system.assert_called_once_with("gpio write 2 1")

