import sys
from unittest.mock import MagicMock

# Mock rich before importing utils
mock_rich = MagicMock()
sys.modules["rich"] = mock_rich
sys.modules["rich.console"] = mock_rich

import pytest
# We need to use absolute import or adjust path if running with pytest from root
try:
    from .utils import cast_input_value, identify_tool_for_task
except ImportError:
    import os
    sys.path.append(os.path.dirname(__file__))
    from utils import cast_input_value, identify_tool_for_task

def test_cast_input_value_integer():
    assert cast_input_value("123", {"type": "integer"}) == 123
    assert cast_input_value("-5", {"type": "integer"}) == -5
    assert cast_input_value("abc", {"type": "integer"}) == "abc"  # Fails casting, returns original

def test_cast_input_value_number():
    assert cast_input_value("123.45", {"type": "number"}) == 123.45
    assert cast_input_value("1e3", {"type": "number"}) == 1000.0
    assert cast_input_value("abc", {"type": "number"}) == "abc"  # Fails casting, returns original

def test_cast_input_value_boolean():
    # Truthy values
    assert cast_input_value("true", {"type": "boolean"}) is True
    assert cast_input_value("TRUE", {"type": "boolean"}) is True
    assert cast_input_value("t", {"type": "boolean"}) is True
    assert cast_input_value("yes", {"type": "boolean"}) is True
    assert cast_input_value("y", {"type": "boolean"}) is True
    assert cast_input_value("1", {"type": "boolean"}) is True

    # Falsy values
    assert cast_input_value("false", {"type": "boolean"}) is False
    assert cast_input_value("no", {"type": "boolean"}) is False
    assert cast_input_value("0", {"type": "boolean"}) is False
    assert cast_input_value("foo", {"type": "boolean"}) is False

def test_cast_input_value_string():
    assert cast_input_value("hello", {"type": "string"}) == "hello"
    assert cast_input_value("123", {"type": "string"}) == "123"
    assert cast_input_value("true", {"type": "string"}) == "true"

def test_cast_input_value_default_type():
    # Defaults to string if type is missing
    assert cast_input_value("123", {}) == "123"

def test_cast_input_value_empty():
    assert cast_input_value("", {"type": "integer"}) == ""
    assert cast_input_value(None, {"type": "integer"}) is None

def test_identify_tool_for_task():
    class MockTool:
        def __init__(self, name):
            self.name = name

    tools = [MockTool("travel_agent"), MockTool("research_agent"), MockTool("long_running_agent")]

    # Keyword matching
    assert identify_tool_for_task("book a flight to Paris", tools) == "travel_agent"
    assert identify_tool_for_task("research AI trends", tools) == "research_agent"
    assert identify_tool_for_task("run a long test", tools) == "long_running_agent"

    # Name matching
    assert identify_tool_for_task("call travel_agent", tools) == "travel_agent"

    # No match
    assert identify_tool_for_task("wash the car", tools) is None
