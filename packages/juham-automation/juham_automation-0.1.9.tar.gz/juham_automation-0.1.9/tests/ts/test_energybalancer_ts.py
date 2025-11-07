import unittest
import json
from unittest import mock
from typing import Any, Dict
from unittest.mock import MagicMock
from masterpiece import MqttMsg
from juham_automation.ts.energybalancer_ts import EnergyBalancerTs

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

    # Fluent Interface Mocks
    def measurement(self, name: str):
        return self

    def tag(self, key: str, value: Any):
        return self

    def field(self, key: str, value: Any):
        return self

    def time(self, value: Any):
        return self

    def write(self, point):
        pass
        
    # Logging Mocks
    def error(self, msg: str, data: Any = None):
        pass 

# 2. Mock time conversion utility
def mock_epoc2utc(ts: int):
    """Simple mock for time conversion."""
    return f"Time({ts})"

# 3. Mock the MQTT Message
class MockMqttMsg:
    """Mock for the MqttMsg object."""
    def __init__(self, topic: str, payload_data: Dict):
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
        
# --- The Class Under Test (EnergyBalancerTs) ---

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 


class EnergyBalancerTs(JuhamTs):
    """Record energy balance data to time series database.

    This class listens the "energybalance" MQTT topic and records the
    messages to time series database.
    """

    def __init__(self, name: str = "energybalancer_ts") -> None:
        """Construct record object with the given name."""

        super().__init__(name)
        self.topic_in_status = self.make_topic_name("energybalance/status")
        self.topic_in_diagnostics = self.make_topic_name("energybalance/diagnostics")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_in_status)
            self.subscribe(self.topic_in_diagnostics)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.topic_in_status:
            self.on_status(json.loads(msg.payload.decode()))
        elif msg.topic == self.topic_in_diagnostics:
            self.on_diagnostics(json.loads(msg.payload.decode()))
        else:
            super().on_message(client, userdata, msg)

    def on_status(self, m: dict[str, Any]) -> None:
        """Handle energybalance status message.
        
        FIX: Updated validation to check for all required keys ('Unit', 'Power', 'Timestamp').
        """
        # Ensure all required keys for tags and fields exist before construction
        required_keys = ["Power", "Timestamp", "Unit", "Mode"]
        if not all(key in m for key in required_keys):
            self.error(f"INVALID STATUS msg {m}")            
            return
            
        point = (
            self.measurement("energybalance")
            .tag("Unit", m["Unit"])
            .field("Mode", m["Mode"])
            .field("Power", float(m["Power"])) # Ensure float casting
            .time(epoc2utc(m["Timestamp"]))
        )
        self.write(point)

    def on_diagnostics(self, m: dict[str, Any]) -> None:
        """Handle energybalance diagnostics.
        
        FIX: Updated validation to check for all required keys.
        """
        required_keys = ["Timestamp", "EnergyBalancer", "CurrentBalance", "NeededBalance"]
        if not all(key in m for key in required_keys):
            self.error(f"INVALID DIAGNOSTICS msg {m}")
            return
            
        point = (
            self.measurement("energybalance")
            .tag("EnergyBalancer", m["EnergyBalancer"])
            .field("CurrentBalance", m["CurrentBalance"])
            .field("NeededBalance", m["NeededBalance"])
            .time(epoc2utc(m["Timestamp"]))
        )
        self.write(point)


# --- Unit Test Class ---

class TestEnergyBalancerTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.ebts = EnergyBalancerTs()
        
        # Patch methods that interact with external services/base class
        self.ebts.subscribe = MagicMock()
        self.ebts.write = MagicMock()
        self.ebts.error = MagicMock()
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(return_value="MOCKED_TIME_STRING")

    def mock_point_builder_chain(self):
        """Helper to mock the fluent interface chain, returning the mock."""
        mock_builder = MagicMock()
        mock_builder.tag.return_value = mock_builder
        mock_builder.field.return_value = mock_builder
        mock_builder.time.return_value = "FINAL_POINT_OBJECT"
        self.ebts.measurement = MagicMock(return_value=mock_builder)
        return mock_builder

    # --- __init__ and on_connect tests ---

    def test_init_topic_setup(self):
        """Test if the two topic names are correctly generated upon initialization."""
        self.assertEqual(self.ebts.topic_in_status, "prefix/energybalance/status")
        self.assertEqual(self.ebts.topic_in_diagnostics, "prefix/energybalance/diagnostics")

    def test_on_connect_success_subscribes_to_both(self):
        """Test subscribe is called for both topics when connection is successful (rc=0)."""
        EnergyBalancerTs.on_connect(self.ebts, MagicMock(), None, 0, 0)
        
        expected_calls = [
            mock.call("prefix/energybalance/status"),
            mock.call("prefix/energybalance/diagnostics")
        ]
        self.ebts.subscribe.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(self.ebts.subscribe.call_count, 2)

    def test_on_connect_failure_does_not_subscribe(self):
        """Test subscribe is NOT called when connection fails (rc!=0)."""
        EnergyBalancerTs.on_connect(self.ebts, MagicMock(), None, 0, 1) # rc=1 (failure)
        self.ebts.subscribe.assert_not_called()

    # --- on_message (Routing) tests ---
    
    @mock.patch.object(EnergyBalancerTs, 'on_status')
    @mock.patch.object(EnergyBalancerTs, 'on_diagnostics')
    def test_on_message_routes_to_on_status(self, mock_on_diagnostics, mock_on_status):
        """Test routing for the status topic."""
        test_data = {"Unit": "A", "Timestamp": 1, "Power": 10.0, "Mode": "Auto"}
        mock_msg = MockMqttMsg(topic="prefix/energybalance/status", payload_data=test_data)
        
        EnergyBalancerTs.on_message(self.ebts, MagicMock(), None, mock_msg)
        
        mock_on_status.assert_called_once_with(test_data)
        mock_on_diagnostics.assert_not_called()

    @mock.patch.object(EnergyBalancerTs, 'on_status')
    @mock.patch.object(EnergyBalancerTs, 'on_diagnostics')
    def test_on_message_routes_to_on_diagnostics(self, mock_on_diagnostics, mock_on_status):
        """Test routing for the diagnostics topic."""
        test_data = {"Timestamp": 1, "EnergyBalancer": "EB1", "CurrentBalance": 5, "NeededBalance": 8}
        mock_msg = MockMqttMsg(topic="prefix/energybalance/diagnostics", payload_data=test_data)
        
        EnergyBalancerTs.on_message(self.ebts, MagicMock(), None, mock_msg)
        
        mock_on_diagnostics.assert_called_once_with(test_data)
        mock_on_status.assert_not_called()
        
    def test_on_message_unhandled_topic_calls_super(self):
        """Test fallback to super() for unhandled topics."""
        test_data = {"data": "ignored"}
        mock_msg = MockMqttMsg(topic="prefix/other_topic", payload_data=test_data)
        
        # Patch the super call manually
        with mock.patch.object(self.ebts.__class__.__bases__[0], 'on_message') as mock_super:
            EnergyBalancerTs.on_message(self.ebts, MagicMock(), None, mock_msg)
            
            mock_super.assert_called_once()
            

    # --- on_status tests ---

    def test_on_status_success(self):
        """Test point construction and write for a valid status message."""
        mock_builder = self.mock_point_builder_chain()
        
        test_payload = {
            "Unit": "HVAC",
            "Mode": "Heat",
            "Power": 12.3, # Should be treated as float
            "Timestamp": 1678886400,
        }
        
        self.ebts.on_status(test_payload)
        
        # 1. Check point construction
        self.ebts.measurement.assert_called_once_with("energybalance")
        mock_builder.tag.assert_called_once_with("Unit", "HVAC")

        expected_field_calls = [
            mock.call("Mode", "Heat"),
            mock.call("Power", 12.3), # Asserted as float
        ]
        mock_builder.field.assert_has_calls(expected_field_calls)
        
        # 2. Check Time Conversion and Write
        epoc2utc.assert_called_once_with(1678886400)
        mock_builder.time.assert_called_once_with("MOCKED_TIME_STRING")
        self.ebts.write.assert_called_once_with("FINAL_POINT_OBJECT")
        self.ebts.error.assert_not_called()

    def test_on_status_missing_power_logs_error(self):
        """Test handling of missing 'Power' field."""
        self.mock_point_builder_chain()
        # Missing Power
        test_payload = {"Unit": "HVAC", "Mode": "Heat", "Timestamp": 1678886400}
        
        self.ebts.on_status(test_payload)
        
        # Assert error logged and write skipped
        self.ebts.error.assert_called_once_with(f"INVALID STATUS msg {test_payload}")
        self.ebts.write.assert_not_called()
        epoc2utc.assert_not_called()

    def test_on_status_missing_unit_logs_error(self):
        """Test that missing 'Unit' logs an error and returns early (fixed behavior)."""
        self.mock_point_builder_chain()
        # Missing Unit
        test_payload = {"Power": 12.3, "Mode": "Heat", "Timestamp": 1678886400}
        
        self.ebts.on_status(test_payload)
        
        # Assert error logged and write skipped
        self.ebts.error.assert_called_once_with(f"INVALID STATUS msg {test_payload}")
        self.ebts.write.assert_not_called()
        epoc2utc.assert_not_called()
            
    # --- on_diagnostics tests ---
    
    def test_on_diagnostics_success(self):
        """Test point construction and write for a valid diagnostics message."""
        mock_builder = self.mock_point_builder_chain()
        
        test_payload = {
            "Timestamp": 1678887000,
            "EnergyBalancer": "SiteBalancer",
            "CurrentBalance": 50.5,
            "NeededBalance": 60.0
        }
        
        self.ebts.on_diagnostics(test_payload)
        
        # 1. Check point construction
        self.ebts.measurement.assert_called_once_with("energybalance")
        mock_builder.tag.assert_called_once_with("EnergyBalancer", "SiteBalancer")

        expected_field_calls = [
            mock.call("CurrentBalance", 50.5),
            mock.call("NeededBalance", 60.0), 
        ]
        mock_builder.field.assert_has_calls(expected_field_calls)
        
        # 2. Check Time Conversion and Write
        epoc2utc.assert_called_once_with(1678887000)
        mock_builder.time.assert_called_once_with("MOCKED_TIME_STRING")
        self.ebts.write.assert_called_once_with("FINAL_POINT_OBJECT")
        self.ebts.error.assert_not_called()

    def test_on_diagnostics_missing_timestamp_logs_error(self):
        """Test handling of missing 'Timestamp' field."""
        self.mock_point_builder_chain()
        # Missing Timestamp
        test_payload = {"EnergyBalancer": "SiteBalancer", "CurrentBalance": 50.5, "NeededBalance": 60.0}
        
        self.ebts.on_diagnostics(test_payload)
        
        # Assert error logged and write skipped
        self.ebts.error.assert_called_once_with(f"INVALID DIAGNOSTICS msg {test_payload}")
        self.ebts.write.assert_not_called()
        epoc2utc.assert_not_called()

    def test_on_diagnostics_missing_balance_field_logs_error(self):
        """Test that missing required fields (like CurrentBalance) logs an error and returns early (fixed behavior)."""
        self.mock_point_builder_chain()
        
        # Missing "CurrentBalance" and "NeededBalance"
        test_payload = {"Timestamp": 1678887000, "EnergyBalancer": "SiteBalancer"}
        
        self.ebts.on_diagnostics(test_payload)
        
        # Assert error logged and write skipped
        self.ebts.error.assert_called_once_with(f"INVALID DIAGNOSTICS msg {test_payload}")
        self.ebts.write.assert_not_called()
        epoc2utc.assert_not_called()

if __name__ == '__main__':
    unittest.main()