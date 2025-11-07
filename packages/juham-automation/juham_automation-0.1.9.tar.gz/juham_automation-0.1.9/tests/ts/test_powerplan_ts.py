import unittest
from masterpiece import MqttMsg
from juham_automation.ts.powerplan_ts import PowerPlanTs
import unittest
import json
from unittest import mock
from typing import Any
# Mocking 'typing_extensions' is necessary for the @override decorator to work without the actual library
from unittest.mock import MagicMock

# --- Mocking External Dependencies and Structure ---

# 1. Mock the base class and related imports (juham_core)
class MockJuhamTs:
    """Mock for the base class JuhamTs."""
    def __init__(self, name: str) -> None:
        pass # Don't run the actual init logic

    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        pass

    def on_message(self, client: object, userdata: Any, msg: object) -> None:
        pass
        
    def subscribe(self, topic: str) -> None:
        pass

    def make_topic_name(self, suffix: str) -> str:
        return f"prefix/{suffix}"

    def measurement(self, name: str):
        # This will be replaced by a mock in the test, but needed for class definition
        return self

    def tag(self, key: str, value: Any):
        return self

    def field(self, key: str, value: Any):
        return self

    def time(self, value: Any):
        return self

    def write(self, point):
        pass

# 2. Mock time conversion utility
def mock_epoc2utc(ts: int):
    """Simple mock for time conversion."""
    return f"Time({ts})"

# 3. Mock the MQTT Message
class MockMqttMsg:
    """Mock for the MqttMsg object."""
    def __init__(self, payload_data: dict):
        self.payload_data = payload_data
        self.payload = self  # Self-referencing to mimic a 'bytes-like' object
        self.topic = "prefix/powerplan"

    def decode(self):
        """Simulate bytes payload decoding."""
        return json.dumps(self.payload_data)

# 4. Mock the @override decorator if it doesn't exist
try:
    from typing_extensions import override
except ImportError:
    def override(func):
        return func
        
# --- The Class Under Test (Copied from User's Request) ---

# We need to explicitly redefine the dependencies for this local execution context
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 

class PowerPlanTs(JuhamTs):
    """Power plan time series record."""

    def __init__(self, name: str = "powerplan_ts") -> None:
        super().__init__(name)
        self.powerplan_topic = self.make_topic_name("powerplan")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.powerplan_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        super().on_message(client, userdata, msg)
        m = json.loads(msg.payload.decode())
        schedule = m["Schedule"]
        uoi = m["UOI"]
        ts = m["Timestamp"]

        tempForecast : float = float(m.get("TempForecast", 0.0))
        solarForecast : float = float(m.get("SolarForecast", 0.0))

        point = (
            self.measurement("powerplan")
            .tag("unit", m["Unit"])
            .field("state", m["State"])  # 1 on, 0 off
            .field("name", m["Unit"])  # e.g main_boiler
            .field("type", "C")  # C=consumption, S = supply
            .field("power", 16.0)  # kW
            .field("Schedule", schedule)  # figures of merit
            .field("UOI", float(uoi))  # Utilitzation Optimizing Index
            .field("TempForecast", tempForecast)  # next day temp forecast
            .field("SolarForecast", solarForecast) # next day solar forecast
            .time(epoc2utc(ts))
        )
        self.write(point)


# --- Unit Test Class ---

# We use patch.object to replace methods on the class/instance being tested.
class TestPowerPlanTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        # 1. Instantiate the class under test
        self.ppts = PowerPlanTs()

        # 2. Patch the parent class methods that are called directly
        self.ppts.subscribe = MagicMock()
        self.ppts.on_connect = MagicMock()
        self.ppts.on_message = MagicMock()
        self.ppts.write = MagicMock()
        
        # 3. Patch the time utility (needed for on_message)
        global epoc2utc
        epoc2utc = MagicMock(return_value="MOCKED_TIME_STRING")


    def test_init_and_topic_setup(self):
        """Test if the topic name is correctly generated upon initialization."""
        # Note: We must re-init here because setUp patches the instance methods.
        instance = PowerPlanTs(name="test_ts")
        self.assertEqual(instance.powerplan_topic, "prefix/powerplan")

    def test_on_connect(self):
        """Test if on_connect subscribes to the correct topic."""
        # Reset to the actual on_connect method for testing
        PowerPlanTs.on_connect(self.ppts, MagicMock(), None, 0, 0)

        # Assert subscribe was called with the topic generated in __init__
        self.ppts.subscribe.assert_called_once_with("prefix/powerplan")

    def test_on_message_full_payload(self):
        """Test handling a payload where all optional fields are present."""
        
        # 1. Mock the Fluent Interface Chain (measurement -> tag -> field -> time)
        # We need a long chain of return values that are all the same mock object.
        mock_point_builder = MagicMock()
        mock_point_builder.tag.return_value = mock_point_builder
        mock_point_builder.field.return_value = mock_point_builder
        mock_point_builder.time.return_value = "FINAL_POINT_OBJECT"

        # Patch the entry point: self.measurement()
        self.ppts.measurement = MagicMock(return_value=mock_point_builder)

        # 2. Define the Test Data
        test_payload = {
            "Schedule": "schedule_A",
            "UOI": "99.5", # String in JSON, should be float in point
            "Timestamp": 1678886400,
            "Unit": "main_boiler",
            "State": 1,
            "TempForecast": 22.1,
            "SolarForecast": 3.4
        }
        mock_msg = MockMqttMsg(test_payload)

        # 3. Run the method under test
        PowerPlanTs.on_message(self.ppts, MagicMock(), None, mock_msg)

        # 4. Assertions

        # A. Check Point Construction Start
        self.ppts.measurement.assert_called_once_with("powerplan")
        mock_point_builder.tag.assert_called_once_with("unit", "main_boiler")

        # B. Check all field calls, including the optional ones
        expected_field_calls = [
            # Base fields
            mock.call("state", 1),
            mock.call("name", "main_boiler"),
            mock.call("type", "C"),
            mock.call("power", 16.0),
            mock.call("Schedule", "schedule_A"),
            mock.call("UOI", 99.5), # Asserted as float
            # Optional fields
            mock.call("TempForecast", 22.1),
            mock.call("SolarForecast", 3.4)
        ]
        mock_point_builder.field.assert_has_calls(expected_field_calls, any_order=False)
        
        # C. Check time conversion and final write
        self.ppts.write.assert_called_once_with("FINAL_POINT_OBJECT")
        epoc2utc.assert_called_once_with(1678886400)
        mock_point_builder.time.assert_called_once_with("MOCKED_TIME_STRING")


    def test_on_message_missing_optional_keys(self):
        """Test handling a payload where optional forecast fields are missing (defaulting to 0.0)."""
        
        # 1. Setup Mock Chain
        mock_point_builder = MagicMock()
        mock_point_builder.tag.return_value = mock_point_builder
        mock_point_builder.field.return_value = mock_point_builder
        mock_point_builder.time.return_value = "FINAL_POINT_OBJECT"
        self.ppts.measurement = MagicMock(return_value=mock_point_builder)

        # 2. Define the Test Data (Missing TempForecast and SolarForecast)
        test_payload_missing = {
            "Schedule": "schedule_B",
            "UOI": "50.0",
            "Timestamp": 1678886500,
            "Unit": "aux_heater",
            "State": 0
        }
        mock_msg = MockMqttMsg(test_payload_missing)

        # 3. Run the method under test
        PowerPlanTs.on_message(self.ppts, MagicMock(), None, mock_msg)

        # 4. Assertions for the default values (0.0)
        expected_field_calls = [
            # ... (other fields)
            mock.call("UOI", 50.0), 
            mock.call("TempForecast", 0.0), # Asserted default
            mock.call("SolarForecast", 0.0) # Asserted default
        ]
        
        # Check that the necessary calls were made, specifically the defaults
        # We check the total number of calls to ensure no extra calls were made
        self.assertEqual(mock_point_builder.field.call_count, 8) 
        
        # Check the default calls specifically
        mock_point_builder.field.assert_any_call("TempForecast", 0.0)
        mock_point_builder.field.assert_any_call("SolarForecast", 0.0)
        
        self.ppts.write.assert_called_once_with("FINAL_POINT_OBJECT")

if __name__ == '__main__':
    unittest.main()







if __name__ == "__main__":
    unittest.main()
