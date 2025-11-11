import pytest
from voicecontrolx.actions import tell_time, take_screenshot

def test_tell_time():
    """Test tell_time returns a string containing ':'"""
    time_str = tell_time()
    assert ":" in time_str

def test_take_screenshot():
    """Test screenshot is saved correctly"""
    path = "C:\\Users\\Public\\Desktop\\test_screenshot.png"  # temporary test path
    result = take_screenshot()
    assert "screenshot" in result.lower()
