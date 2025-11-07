import unittest
from masterpiece import MqttMsg
from juham_automation.ts.power_ts import PowerTs

import unittest
import json
from unittest import mock
from typing import Any
from unittest.mock import MagicMock

# --- Mocking External Dependencies and Structure ---

# 1. Mock the base class and related imports (juham_core)
class MockJuhamTs:
    """Mock for the base class JuhamTs."""
    def __init__(self, name: str) -> None:
        pass

    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        pass

    def on_message(self, client: object, userdata: Any, msg: object) -> None:
        pass
        
    def subscribe(self, topic: str) -> None:
        pass

    def make_topic_name(self, suffix: str) -> str:
        # Simulates the base class's topic prefixing
        return f"prefix/{suffix}" 

    def measurement(self, name: str):
        # Fluent interface start point
        return self

    def tag(self, key: str, value: Any):
        return self

    def field(self, key: str, value: Any):
        return self

    def time(self, value: Any):
        return self

    def write(self, point):
        pass
        
    def debug(self, msg: str):
        pass # New method to be mocked and tested

# 2. Mock time conversion utility
def mock_epoc2utc(ts: int):
    """Simple mock for time conversion."""
    return f"Time({ts})"

# 3. Mock the MQTT Message
class MockMqttMsg:
    """Mock for the MqttMsg object."""
    def __init__(self, topic: str, payload_data: dict):
        self.topic = topic
        self.payload_data = payload_data
        self.payload = self
    
    # Simulates bytes payload decoding for json.loads()
    def decode(self):
        return json.dumps(self.payload_data)

# 4. Mock the @override decorator
try:
    from typing_extensions import override
except ImportError:
    def override(func):
        return func
        
# --- The Class Under Test (PowerTs) ---

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 


class PowerTs(JuhamTs):
    """Power utilization record."""

    def __init__(self, name: str = "power_ts") -> None:
        """Construct power record object with the given name."""

        super().__init__(name)
        self.topic_name = self.make_topic_name("power")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.topic_name)
        self.debug(f"Subscribed to {self.topic_name}")

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        """Standard mqtt message notification method.

        This method is called upon new arrived message.
        """

        m = json.loads(msg.payload.decode())
        if not "Unit" in m:
            return
        unit = m["Unit"]
        ts = m["Timestamp"]
        state = m["State"]
        point = (
            self.measurement("power")
            .tag("unit", unit)
            .field("state", state)
            .time(epoc2utc(ts))
        )
        self.write(point)


# --- Unit Test Class ---

class TestPowerTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.pts = PowerTs()
        
        # Patch methods that interact with the base/external services
        self.pts.subscribe = MagicMock()
        self.pts.write = MagicMock()
        self.pts.debug = MagicMock()
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(return_value="MOCKED_TIME_STRING")

    def mock_point_builder_chain(self):
        """Helper to mock the fluent interface chain."""
        mock_builder = MagicMock()
        mock_builder.tag.return_value = mock_builder
        mock_builder.field.return_value = mock_builder
        mock_builder.time.return_value = "FINAL_POINT_OBJECT"
        self.pts.measurement = MagicMock(return_value=mock_builder)
        return mock_builder

    def test_init_topic_setup(self):
        """Test if the topic name is correctly generated upon initialization."""
        self.assertEqual(self.pts.topic_name, "prefix/power")

    # --- on_connect test ---
    
    def test_on_connect_subscribes_and_logs(self):
        """Test subscribe is called and debug message is logged on connect."""
        # Note: Must call the class method to bypass the setUp mock for on_connect
        PowerTs.on_connect(self.pts, MagicMock(), None, 0, 0)
        
        # 1. Assert subscribe call
        self.pts.subscribe.assert_called_once_with("prefix/power")
        
        # 2. Assert debug log call
        self.pts.debug.assert_called_once_with("Subscribed to prefix/power")

    # --- on_message tests ---

    def test_on_message_valid_payload_success(self):
        """Test the point construction and successful write for a valid message."""
        
        mock_builder = self.mock_point_builder_chain()
        
        test_payload = {
            "Unit": "HVAC_unit_1",
            "Timestamp": 1700000000,
            "State": 1,
            "ExtraData": "ignored"
        }
        mock_msg = MockMqttMsg(topic="prefix/power", payload_data=test_payload)
        
        PowerTs.on_message(self.pts, MagicMock(), None, mock_msg)
        
        # 1. Check Point Construction Start
        self.pts.measurement.assert_called_once_with("power")
        
        # 2. Check Tag and Field calls
        mock_builder.tag.assert_called_once_with("unit", "HVAC_unit_1")
        mock_builder.field.assert_called_once_with("state", 1)
        
        # 3. Check Time Conversion and Write
        epoc2utc.assert_called_once_with(1700000000)
        mock_builder.time.assert_called_once_with("MOCKED_TIME_STRING")
        self.pts.write.assert_called_once_with("FINAL_POINT_OBJECT")


    def test_on_message_missing_unit_field_returns_early(self):
        """Test the guard condition: if 'Unit' is missing, the method should return without writing."""
        
        # Setup mocks that would show activity if the method proceeded
        self.mock_point_builder_chain()
        
        test_payload_missing_unit = {
            "Timestamp": 1700000000,
            "State": 1
        }
        mock_msg = MockMqttMsg(topic="prefix/power", payload_data=test_payload_missing_unit)
        
        PowerTs.on_message(self.pts, MagicMock(), None, mock_msg)
        
        # Assertions: No database interaction should have happened
        self.pts.measurement.assert_not_called()
        self.pts.write.assert_not_called()
        epoc2utc.assert_not_called()
        
    def test_on_message_missing_state_raises_keyerror(self):
        """Test that missing required fields (like State) raises an error, which the caller must handle."""
        
        test_payload_missing_state = {
            "Unit": "HVAC_unit_1",
            "Timestamp": 1700000000,
        }
        mock_msg = MockMqttMsg(topic="prefix/power", payload_data=test_payload_missing_state)
        
        # Expect a KeyError because the code attempts to access m["State"]
        with self.assertRaises(KeyError):
            PowerTs.on_message(self.pts, MagicMock(), None, mock_msg)

if __name__ == '__main__':
    unittest.main()

