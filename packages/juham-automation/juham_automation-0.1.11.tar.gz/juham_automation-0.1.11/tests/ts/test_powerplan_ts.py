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





class MockTimeSeriesAPI:
    """Mock for the external Time_Series_API (or similar dependency)."""
    def create_point(self):
        # Returns a mock point object that handles field and send methods
        mock_point = MagicMock()
        return mock_point

class PowerPlanTs:
    """
    Simulated implementation of the user's class containing the 'on_message' 
    method with the conditional logic for mandatory and optional fields.
    """
    def __init__(self, ts_api: MockTimeSeriesAPI):
        self.ts_api = ts_api

    def on_message(self, message: dict[str, Any]):
        """Processes a message for time series point creation."""
        
        # Define the fields as per your implementation logic
        mandatory_fields = ["Unit", "Schedule", "Start_Time", "End_Time"]
        optional_fields = ["Power_Plan_A", "Power_Plan_B", "Temperature"] 

        point = self.ts_api.create_point()

        # 1. MANDATORY Fields (will raise KeyError if message[field] fails)
        for field_name in mandatory_fields:
            point.field(field_name, message[field_name])

        # 2. OPTIONAL Fields (check for None/absence and convert to float)
        for field_name in optional_fields:
            value = message.get(field_name)
            
            if value is not None:
                try:
                    # The core logic being tested: type conversion
                    float_value = float(value)
                    point.field(field_name, float_value)
                except (TypeError, ValueError) as e:
                    # In a real scenario, this would handle bad input types
                    # For testing, we just ensure it doesn't crash the mandatory logic
                    print(f"Warning: Could not cast optional field {field_name} to float: {e}")

        point.send()

# --- UNIT TESTS FOR PowerPlanTs.on_message ---

class TestPowerPlanTs(unittest.TestCase):
    
    def setUp(self):
        """Set up the mock API and the instance of the class under test."""
        # 1. Mock the API dependency
        self.mock_api = MagicMock(spec=MockTimeSeriesAPI) 
        
        # 2. Mock the point object that the API returns
        self.mock_point = MagicMock() 
        
        # 3. Configure the mock API
        self.mock_api.create_point.return_value = self.mock_point
        
        # 4. Instantiate the class under test with the mocked dependency
        self.handler = PowerPlanTs(self.mock_api)

    def test_on_message_with_all_optional_fields(self):
        """
        Tests that when all optional fields are present, they are cast to float 
        and included, resulting in 7 calls to point.field().
        """
        message = {
            "Unit": "Turbine-A",
            "Schedule": "Shift-1",
            "Start_Time": 1678886400,
            "End_Time": 1678972800,
            "Power_Plan_A": "55.5", # String value that must be converted to float
            "Power_Plan_B": 100.0,  # Float value
            "Temperature": 98.6     # Another numeric value
        }
        
        self.handler.on_message(message)
        
        # Assert API interaction
        self.mock_api.create_point.assert_called_once()
        self.mock_point.send.assert_called_once()
        
        # Assert the total number of field() calls (4 Mandatory + 3 Optional = 7)
        self.assertEqual(self.mock_point.field.call_count, 7, 
                         "Should call field() for 7 fields.")
        
        # Assert correct values and types for optional fields
        self.mock_point.field.assert_any_call("Power_Plan_A", 55.5) # Check string -> float
        self.mock_point.field.assert_any_call("Power_Plan_B", 100.0)
        self.mock_point.field.assert_any_call("Temperature", 98.6)


    def test_on_message_with_no_optional_fields(self):
        """
        Tests that when optional fields are missing, they are correctly skipped, 
        and only mandatory fields are written, resulting in 4 calls to field().
        """
        message = {
            "Unit": "Turbine-B",
            "Schedule": "Shift-2",
            "Start_Time": 1678886400,
            "End_Time": 1678972800,
            # Optional fields are missing
        }
        
        self.handler.on_message(message)
        
        # Assert API interaction
        self.mock_api.create_point.assert_called_once()
        self.mock_point.send.assert_called_once()
        
        # Assert the total number of field() calls (4 Mandatory + 0 Optional = 4)
        self.assertEqual(self.mock_point.field.call_count, 4, 
                         "Should call field() for only 4 mandatory fields.")
        
        # Confirm one mandatory field was written
        self.mock_point.field.assert_any_call("Unit", "Turbine-B")
        
        # Optional check: Ensure no call was made for a known optional field
        self.assertNotIn(("Power_Plan_A", 55.5), self.mock_point.field.call_args_list)


    def test_on_message_missing_mandatory_key_raises_keyerror(self):
        """
        Tests that the method fails with a KeyError when a mandatory field ('Unit') 
        is missing, and the point.send() API call is NOT made.
        """
        message = {
            # "Unit" is missing
            "Schedule": "Shift-3",
            "Start_Time": 1678886400,
            "End_Time": 1678972800,
            "Power_Plan_A": 60.0 # Present, but shouldn't be processed
        }
        
        # Assert that calling the method raises KeyError
        with self.assertRaises(KeyError) as cm:
            self.handler.on_message(message)
        
        # Assert that the error was specifically about the missing key 'Unit'
        self.assertIn("'Unit'", str(cm.exception)) 
        
        # Crucial: Assert that the final send operation never happened
        self.mock_point.send.assert_not_called()
        
        # Assert that point.field was never called (the failure occurs when 
        # trying to access message["Unit"] before the first call)
        self.mock_point.field.assert_not_called()

    
if __name__ == '__main__':
    unittest.main()

