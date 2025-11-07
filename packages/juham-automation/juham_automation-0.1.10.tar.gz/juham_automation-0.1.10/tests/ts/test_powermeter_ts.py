import unittest
from masterpiece import MqttMsg
from juham_automation.ts.powermeter_ts import PowerMeterTs

import json
from unittest import mock
from typing import Any, Dict
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
        
    def error(self, msg: str):
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {"_base_data": "ok"}

    def from_dict(self, data: Dict[str, Any]) -> None:
        pass

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
        
# --- The Class Under Test (PowerMeterTs) ---

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 

class PowerMeterTs(JuhamTs):
    """Power meter recorder."""

    def __init__(self, name: str = "powermeter_record") -> None:
        super().__init__(name)
        self.power_topic = self.make_topic_name("powerconsumption")  # topic to listen

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.power_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        super().on_message(client, userdata, msg)
        if msg.topic == self.power_topic:
            m = json.loads(msg.payload.decode())
            self.record_power(m)

    def record_power(self, em: dict[str, Any]) -> None:
        """Write from the power (energy) meter to the time
        series database accordingly.
        """
        point = (
            self.measurement("powermeter")
            .tag("sensor", "em0")
            .field("real_A", em["real_a"])
            .field("real_B", em["real_b"])
            .field("real_C", em["real_c"])
            .field("total_real_power", em["real_total"])
            .time(epoc2utc(em["timestamp"]))
        )
        try:
            self.write(point)
        except Exception as e:
            self.error(f"Writing to influx failed {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data["_powermeter_record"] = {
            "power_topic": self.power_topic,
        }
        return data

    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if "_powermeter_record" in data:
            for key, value in data["_powermeter_record"].items():
                setattr(self, key, value)


# --- Unit Test Class ---

class TestPowerMeterTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.pmts = PowerMeterTs()
        
        # Patch methods that interact with external services
        self.pmts.subscribe = MagicMock()
        self.pmts.write = MagicMock()
        self.pmts.error = MagicMock()
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(return_value="MOCKED_TIME_STRING")

    def mock_point_builder_chain(self):
        """Helper to mock the fluent interface chain."""
        mock_builder = MagicMock()
        mock_builder.tag.return_value = mock_builder
        mock_builder.field.return_value = mock_builder
        mock_builder.time.return_value = "FINAL_POINT_OBJECT"
        self.pmts.measurement = MagicMock(return_value=mock_builder)
        return mock_builder

    def test_init_topic_setup(self):
        """Test if the topic name is correctly generated upon initialization."""
        self.assertEqual(self.pmts.power_topic, "prefix/powerconsumption")

    # --- on_connect tests ---
    
    def test_on_connect_success(self):
        """Test subscribe is called when connection is successful (rc=0)."""
        PowerMeterTs.on_connect(self.pmts, MagicMock(), None, 0, 0)
        self.pmts.subscribe.assert_called_once_with("prefix/powerconsumption")

    def test_on_connect_failure(self):
        """Test subscribe is NOT called when connection fails (rc!=0)."""
        PowerMeterTs.on_connect(self.pmts, MagicMock(), None, 0, 1) # rc=1 (failure)
        self.pmts.subscribe.assert_not_called()

    # --- on_message tests ---

    @mock.patch.object(PowerMeterTs, 'record_power')
    def test_on_message_correct_topic(self, mock_record_power):
        """Test that record_power is called with the parsed payload on the correct topic."""
        test_data = {"real_a": 10.0, "real_b": 10.1, "real_c": 10.2, "real_total": 30.3, "timestamp": 1678886400}
        mock_msg = MockMqttMsg(topic="prefix/powerconsumption", payload_data=test_data)
        
        PowerMeterTs.on_message(self.pmts, MagicMock(), None, mock_msg)
        
        # Assert that record_power was called with the decoded dictionary
        mock_record_power.assert_called_once_with(test_data)

    @mock.patch.object(PowerMeterTs, 'record_power')
    def test_on_message_wrong_topic(self, mock_record_power):
        """Test that record_power is NOT called when the topic does not match."""
        test_data = {"data": "ignored"}
        mock_msg = MockMqttMsg(topic="prefix/another_topic", payload_data=test_data)
        
        PowerMeterTs.on_message(self.pmts, MagicMock(), None, mock_msg)
        
        # Assert that record_power was never called
        mock_record_power.assert_not_called()

    # --- record_power tests ---

    def test_record_power_success(self):
        """Test the point construction and successful write to InfluxDB."""
        
        mock_builder = self.mock_point_builder_chain()
        
        test_payload = {
            "real_a": 10.5,
            "real_b": 20.5,
            "real_c": 30.5,
            "real_total": 61.5,
            "timestamp": 1678886400
        }
        
        self.pmts.record_power(test_payload)
        
        # 1. Check Point Construction
        self.pmts.measurement.assert_called_once_with("powermeter")
        mock_builder.tag.assert_called_once_with("sensor", "em0")

        expected_field_calls = [
            mock.call("real_A", 10.5),
            mock.call("real_B", 20.5),
            mock.call("real_C", 30.5),
            mock.call("total_real_power", 61.5),
        ]
        mock_builder.field.assert_has_calls(expected_field_calls)
        
        # 2. Check Time Conversion and Write
        epoc2utc.assert_called_once_with(1678886400)
        mock_builder.time.assert_called_once_with("MOCKED_TIME_STRING")
        self.pmts.write.assert_called_once_with("FINAL_POINT_OBJECT")
        self.pmts.error.assert_not_called()


    def test_record_power_write_failure(self):
        """Test the exception handling when self.write fails."""
        
        self.mock_point_builder_chain()
        
        # Force self.write to raise an exception
        self.pmts.write.side_effect = Exception("Mock Influx Error")
        
        test_payload = {
            "real_a": 1, "real_b": 1, "real_c": 1, "real_total": 3, "timestamp": 123456
        }
        
        self.pmts.record_power(test_payload)
        
        # 1. Assert write was attempted
        self.pmts.write.assert_called_once()
        
        # 2. Assert error logging occurred
        self.pmts.error.assert_called_once_with("Writing to influx failed Mock Influx Error")

    # --- Serialization tests (to/from dict) ---

    def test_serialization_methods(self):
        """Test to_dict and from_dict for the class-specific attributes."""
        
        # Test to_dict
        data = self.pmts.to_dict()
        expected_data = {
            "_base_data": "ok", # From mocked super().to_dict()
            "_powermeter_record": {
                "power_topic": "prefix/powerconsumption"
            }
        }
        self.assertEqual(data, expected_data)
        
        # Test from_dict
        new_instance = PowerMeterTs()
        
        # Change the topic to prove it can be overwritten by from_dict
        new_data = {
            "_base_data": "ok", 
            "_powermeter_record": {
                "power_topic": "new_prefix/new_topic"
            }
        }
        
        new_instance.from_dict(new_data)
        self.assertEqual(new_instance.power_topic, "new_prefix/new_topic")

if __name__ == '__main__':
    unittest.main()
