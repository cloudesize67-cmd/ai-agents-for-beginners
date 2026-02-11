import unittest
from unittest.mock import MagicMock
import json
import sys
import os

# --- MOCK SETUP START ---
# The installed version of agent_framework seems incompatible with the sample code
# (e.g., missing ChatMessage). We mock it to ensure tests can run.

# Create mocks for the module and its components
mock_af = MagicMock()
mock_af_openai = MagicMock()

# Decorators (ai_function, executor) need to be callables that return a decorator
def mock_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

mock_af.ai_function = mock_decorator
mock_af.executor = mock_decorator

# Mock classes used in type hints and instantiation
mock_af.AgentExecutor = MagicMock()
mock_af.AgentExecutorRequest = MagicMock()
mock_af.ChatMessage = MagicMock()
mock_af.Role = MagicMock()
mock_af.WorkflowBuilder = MagicMock()
mock_af.WorkflowContext = MagicMock()

# AgentExecutorResponse needs to be a class we can instantiate or check against
class MockAgentExecutorResponse:
    def __init__(self):
        self.agent_run_response = MagicMock()

mock_af.AgentExecutorResponse = MockAgentExecutorResponse

# Apply mocks to sys.modules
sys.modules["agent_framework"] = mock_af
sys.modules["agent_framework.openai"] = mock_af_openai

# --- MOCK SETUP END ---

# Ensure the current directory is in sys.path to import the module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the module under test
# This utilizes the mocks we just set up
from hotel_booking_workflow_sample import (
    hotel_booking,
    has_availability_condition,
    no_availability_condition,
    BookingCheckResult
)

class TestHotelBookingWorkflow(unittest.TestCase):
    """Tests for the hotel booking workflow sample."""

    def test_hotel_booking_available_cities(self):
        """Test hotel_booking tool with cities that have availability."""
        available_cities = ["Stockholm", "Seattle", "Tokyo", "London", "Amsterdam"]

        for city in available_cities:
            with self.subTest(city=city):
                result_json = hotel_booking(city)
                result = json.loads(result_json)

                self.assertTrue(result["has_availability"], f"{city} should have availability")
                self.assertEqual(result["destination"], city)

    def test_hotel_booking_unavailable_cities(self):
        """Test hotel_booking tool with cities that do not have availability."""
        unavailable_cities = ["Paris", "Berlin", "New York", "Mars"]

        for city in unavailable_cities:
            with self.subTest(city=city):
                result_json = hotel_booking(city)
                result = json.loads(result_json)

                self.assertFalse(result["has_availability"], f"{city} should NOT have availability")
                self.assertEqual(result["destination"], city)

    def test_hotel_booking_case_insensitivity(self):
        """Test that city matching is case-insensitive."""
        city = "TOKYO"
        result_json = hotel_booking(city)
        result = json.loads(result_json)
        self.assertTrue(result["has_availability"])
        self.assertEqual(result["destination"], "TOKYO")

    def test_has_availability_condition_true(self):
        """Test has_availability_condition returns True when availability exists."""
        # Create a mock response using our MockAgentExecutorResponse
        mock_response = MockAgentExecutorResponse()

        check_result = BookingCheckResult(
            destination="Seattle",
            has_availability=True,
            message="Rooms available"
        )

        # Set the text on the inner mock
        mock_response.agent_run_response.text = check_result.model_dump_json()

        self.assertTrue(has_availability_condition(mock_response))

    def test_has_availability_condition_false(self):
        """Test has_availability_condition returns False when NO availability."""
        mock_response = MockAgentExecutorResponse()

        check_result = BookingCheckResult(
            destination="Paris",
            has_availability=False,
            message="No rooms"
        )

        mock_response.agent_run_response.text = check_result.model_dump_json()

        self.assertFalse(has_availability_condition(mock_response))

    def test_has_availability_condition_invalid_input(self):
        """Test has_availability_condition handles invalid input gracefully."""
        # Case 1: Not an AgentExecutorResponse
        # The function explicitly returns True if the input is not an AgentExecutorResponse
        # This is the current implementation behavior we are verifying.
        self.assertTrue(has_availability_condition("not a response"))

        # Case 2: Invalid JSON in text
        mock_response = MockAgentExecutorResponse()
        mock_response.agent_run_response.text = "invalid json"

        self.assertFalse(has_availability_condition(mock_response))

    def test_no_availability_condition_true(self):
        """Test no_availability_condition returns True when NO availability."""
        mock_response = MockAgentExecutorResponse()

        check_result = BookingCheckResult(
            destination="Paris",
            has_availability=False,
            message="No rooms"
        )

        mock_response.agent_run_response.text = check_result.model_dump_json()

        self.assertTrue(no_availability_condition(mock_response))

    def test_no_availability_condition_false(self):
        """Test no_availability_condition returns False when availability exists."""
        mock_response = MockAgentExecutorResponse()

        check_result = BookingCheckResult(
            destination="Seattle",
            has_availability=True,
            message="Rooms available"
        )

        mock_response.agent_run_response.text = check_result.model_dump_json()

        self.assertFalse(no_availability_condition(mock_response))

if __name__ == '__main__':
    unittest.main()
