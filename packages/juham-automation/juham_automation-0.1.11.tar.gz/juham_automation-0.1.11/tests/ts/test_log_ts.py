import unittest
import json
from masterpiece import MqttMsg
from juham_automation.ts.log_ts import LogTs

from unittest import mock
from typing import Any, Dict, List
from unittest.mock import MagicMock, call
from typing_extensions import override
from typing_extensions import override

# --- Mocking External Dependencies and Structure ---

# 1. Mock the base class and related imports (juham_core)
class MockJuhamTs:
    """Mock for the base class JuhamTs, which includes logging functionality."""
    def __init__(self, name: str) -> None:
        self.name = name
        # Placeholder for the actual method used in the class under test
        self.log_message = self._mock_log_message_placeholder 
        pass

    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        pass

    def on_message(self, client: object, userdata: Any, msg: object) -> None:
        pass
        
    def subscribe(self, topic: str) -> None:
        pass

    def make_topic_name(self, suffix: str) -> str:
        # Simulates the base class's topic prefixing
        return f"prefix/{self.name}/{suffix}" 

    # Fluent Interface Mocks (for point construction)
    def measurement(self, name: str):
        pass # Actual mock done in setUp

    def write(self, point):
        pass # Actual mock done in setUp
        
    # Logging Mocks
    def _mock_log_message_placeholder(self, level: str, msg: str, data: Any = None):
        """Placeholder for log_message before it's replaced by MagicMock."""
        print(f"[{level}] {msg} - Data: {data}")


# 2. Mock time conversion utility
def mock_epoc2utc(ts: int):
    """Simple mock for time conversion."""
    return f"Time({ts})"

# 3. Mock the MQTT Message
class MockMqttMsg:
    """Mock for the MqttMsg object."""
    def __init__(self, topic: str, payload_data: Dict[str, Any]):
        self.topic = topic
        # The payload_data is a single dict for log events
        self.payload_data = payload_data
        self.payload = self
    
    # Simulates bytes payload decoding for json.loads()
    def decode(self):
        return json.dumps(self.payload_data)

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 


# --- The Class Under Test (LogTs) ---

class LogTs(JuhamTs):
    """Class recording application events, such as warnings and errors,
    to time series database."""

    def __init__(self, name: str = "log_ts") -> None:
        """Creates mqtt client for recording log events to time series
        database.

        Args:
            name (str): name for the client
        """
        super().__init__(name)
        self.topic_name = self.make_topic_name("log")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        """Connects the client to mqtt broker.

        Args:
            client (obj): client to be connected
            userdata (any): caller specific data
            flags (int): implementation specific shit

        Returns:
            rc (bool): True if successful
        """
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_name)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        m = json.loads(msg.payload.decode())
        ts = epoc2utc(m["Timestamp"])

        point = (
            self.measurement("log")
            .tag("class", m["Class"])
            .field("source", m["Source"])
            .field("msg", m["Msg"])
            .field("details", m["Details"])
            .field("Timestamp", m["Timestamp"])
            .time(ts)
        )
        try:
            self.write(point)
        except Exception as e:
            self.log_message("Error", f"Cannot write log event {m['Msg']}", str(e))


# --- Unit Test Class ---

class TestLogTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        # Initialize LogTs (which calls JuhamTs.__init__)
        self.lts = LogTs()
        
        # Patch external methods
        self.lts.subscribe = MagicMock()
        self.lts.write = MagicMock()
        # Mocking the base class's logging mechanism
        self.lts.log_message = MagicMock() 
        
        # Mock point builder to capture calls using the fluent interface pattern
        self.point_builder = MagicMock()
        self.point_builder.tag.return_value = self.point_builder
        self.point_builder.field.return_value = self.point_builder
        self.point_builder.time.return_value = "FINAL_POINT_OBJECT" 
        self.lts.measurement = MagicMock(return_value=self.point_builder, side_effect=lambda name: self.point_builder)
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(side_effect=lambda ts: f"Time({ts})")

        self.test_topic = f"prefix/{self.lts.name}/log"
        self.test_log_data = {
            "Timestamp": 1678886400,
            "Class": "Heating",
            "Source": "thermostat_01",
            "Msg": "Test message",
            "Details": "Temperature spike detected"
        }
        self.mock_msg = MockMqttMsg(topic=self.test_topic, payload_data=self.test_log_data)


    # --- __init__ and on_connect tests ---

    def test_init_topic_setup(self):
        """Test if the log topic name is correctly generated upon initialization."""
        self.assertEqual(self.lts.topic_name, self.test_topic)

    def test_on_connect_success_subscribes_to_log_topic(self):
        """Test subscribe is called when connection is successful (rc=0)."""
        LogTs.on_connect(self.lts, MagicMock(), None, 0, 0)
        self.lts.subscribe.assert_called_once_with(self.test_topic)

    def test_on_connect_failure_does_not_subscribe(self):
        """Test subscribe is NOT called when connection fails (rc!=0)."""
        LogTs.on_connect(self.lts, MagicMock(), None, 0, 1) # rc=1 (failure)
        self.lts.subscribe.assert_not_called()

    # --- on_message (Success Path) tests ---

    def test_on_message_writes_correct_point(self):
        """Test that a valid log message is correctly parsed and written."""
        LogTs.on_message(self.lts, MagicMock(), None, self.mock_msg)
        
        # 1. Check time conversion
        epoc2utc.assert_called_once_with(1678886400)
        
        # 2. Check measurement started
        self.lts.measurement.assert_called_once_with("log")

        # 3. Check tags and fields mapping (order matters for clarity, but not execution)
        self.point_builder.tag.assert_called_once_with("class", "Heating")
        
        self.point_builder.field.assert_has_calls([
            call("source", "thermostat_01"),
            call("msg", "Test message"),
            call("details", "Temperature spike detected"),
            call("Timestamp", 1678886400),
        ])
        
        # 4. Check time setter
        self.point_builder.time.assert_called_once_with("Time(1678886400)")
        
        # 5. Check final write
        self.lts.write.assert_called_once_with("FINAL_POINT_OBJECT")
        self.lts.log_message.assert_not_called()

    # --- on_message (Error Path) tests ---

    def test_on_message_write_failure_logs_error(self):
        """Test that if self.write fails, log_message is called correctly."""
        exception_to_raise = RuntimeError("InfluxDB connection timed out")
        self.lts.write = MagicMock(side_effect=exception_to_raise)
        
        LogTs.on_message(self.lts, MagicMock(), None, self.mock_msg)
        
        # 1. Write should still be called once (and fail)
        self.lts.write.assert_called_once()
        
        # 2. log_message should capture the error
        self.lts.log_message.assert_called_once_with(
            "Error", 
            "Cannot write log event Test message", 
            str(exception_to_raise)
        )

    # --- on_message (Robustness Check) tests ---

    def test_on_message_missing_key_raises_keyerror(self):
        """Test that if a required key (e.g., 'Source') is missing, a KeyError is raised."""
        
        # Create a payload missing the 'Source' key
        payload_missing_source = {
            "Timestamp": 1,
            "Class": "Test",
            # 'Source' is missing here
            "Msg": "Test message",
            "Details": "No details"
        }
        mock_msg = MockMqttMsg(topic=self.test_topic, payload_data=payload_missing_source)

        # The code attempts to access m["Source"] directly, causing a KeyError
        with self.assertRaises(KeyError) as cm:
            LogTs.on_message(self.lts, MagicMock(), None, mock_msg)
            
        self.assertIn("'Source'", str(cm.exception))
        
        # Ensure nothing was written, and no internal error was logged (because the exception propagates)
        self.lts.write.assert_not_called()
        self.lts.log_message.assert_not_called()

if __name__ == "__main__":
    unittest.main()
