from masterpiece import MqttMsg
from juham_automation.ts.energycostcalculator_ts import EnergyCostCalculatorTs
import unittest
import json
from unittest import mock
from typing import Any, Dict, List
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

    # Adding the write_point method used by EnergyCostCalculatorTs
    def write_point(self, measurement: str, tags: Dict[str, Any], fields: Dict[str, Any], timestamp: str):
        pass
        
    def debug(self, msg: str):
        pass
    
    def error(self, msg: str, data: Any = None):
        pass 

    def info(self, msg: str):
        pass

# 2. Mock time conversion utilities
def mock_timestampstr(ts: int):
    """Mock for the timestampstr utility."""
    return f"ISO_TIME({ts})"

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
        
# --- The Class Under Test (EnergyCostCalculatorTs) ---

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
timestampstr = mock_timestampstr 


class EnergyCostCalculatorTs(JuhamTs):
    """The EnergyCostCalculator recorder."""

    def __init__(self, name: str = "ecc_ts") -> None:
        super().__init__(name)
        self.topic_net_energy_balance = self.make_topic_name("net_energy_cost")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        """Standard mqtt connect notification. Subscribes on successful connection."""
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_net_energy_balance)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        """Processes incoming MQTT messages, calling record_powerconsumption for the correct topic."""
        # Call super method first for base class logging/processing
        super().on_message(client, userdata, msg) 
        if msg.topic == self.topic_net_energy_balance:
            m = json.loads(msg.payload.decode())
            self.record_powerconsumption(m)

    def record_powerconsumption(self, m: dict[str, Any]) -> None:
        """Record energy cost data to time series database.
        
        Note: Requires 'name' for the tag and 'ts' for the timestamp.
        """
        self.write_point(
            "energycost", 
            {"site": m["name"]}, 
            m, 
            timestampstr(m["ts"])
        )


# --- Unit Test Class ---

class TestEnergyCostCalculatorTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.eccts = EnergyCostCalculatorTs()
        
        # Patch methods that interact with external services
        self.eccts.subscribe = MagicMock()
        self.eccts.write_point = MagicMock()
        
        # Mock time conversion utility
        global timestampstr
        timestampstr = MagicMock(side_effect=mock_timestampstr)
        

    def test_init_topic_setup(self):
        """Test if the topic name is correctly generated upon initialization."""
        self.assertEqual(self.eccts.topic_net_energy_balance, "prefix/net_energy_cost")

    # --- on_connect tests ---
    
    def test_on_connect_success_subscribes(self):
        """Test subscribe is called when connection is successful (rc=0)."""
        EnergyCostCalculatorTs.on_connect(self.eccts, MagicMock(), None, 0, 0)
        self.eccts.subscribe.assert_called_once_with("prefix/net_energy_cost")

    def test_on_connect_failure_does_not_subscribe(self):
        """Test subscribe is NOT called when connection fails (rc!=0)."""
        EnergyCostCalculatorTs.on_connect(self.eccts, MagicMock(), None, 0, 1) # rc=1 (failure)
        self.eccts.subscribe.assert_not_called()

    # --- on_message tests ---

    @mock.patch.object(EnergyCostCalculatorTs, 'record_powerconsumption')
    def test_on_message_correct_topic_calls_record_powerconsumption(self, mock_record_powerconsumption):
        """Test that record_powerconsumption is called with the parsed payload on the correct topic."""
        test_data = {"ts": 1678886400, "name": "home", "cost": 10.5}
        mock_msg = MockMqttMsg(topic="prefix/net_energy_cost", payload_data=test_data)
        
        # Patch the super call to prevent errors and verify its execution
        with mock.patch.object(self.eccts.__class__.__bases__[0], 'on_message') as mock_super_on_message:
            EnergyCostCalculatorTs.on_message(self.eccts, MagicMock(), None, mock_msg)
            
            # 1. Assert record_powerconsumption was called with the decoded dictionary
            mock_record_powerconsumption.assert_called_once_with(test_data)
            
            # 2. Assert super on_message was called
            mock_super_on_message.assert_called_once()


    @mock.patch.object(EnergyCostCalculatorTs, 'record_powerconsumption')
    def test_on_message_wrong_topic_calls_super_only(self, mock_record_powerconsumption):
        """Test that record_powerconsumption is NOT called when the topic does not match."""
        test_data = {"data": "ignored"}
        mock_msg = MockMqttMsg(topic="prefix/another_topic", payload_data=test_data)
        
        with mock.patch.object(self.eccts.__class__.__bases__[0], 'on_message') as mock_super_on_message:
            EnergyCostCalculatorTs.on_message(self.eccts, MagicMock(), None, mock_msg)
            
            # 1. Assert that record_powerconsumption was never called
            mock_record_powerconsumption.assert_not_called()
            
            # 2. Assert super on_message was called
            mock_super_on_message.assert_called_once()

    # --- record_powerconsumption tests ---

    def test_record_powerconsumption_success(self):
        """Test the correct arguments are passed to self.write_point for a successful write."""
        
        test_payload = {
            "name": "site_A",
            "ts": 1700000000,
            "net_cost": 5.25,
            "consumption": 100.0,
            "production": 50.0
        }
        
        self.eccts.record_powerconsumption(test_payload)
        
        # 1. Assert timestampstr was called correctly
        timestampstr.assert_called_once_with(1700000000)
        
        # 2. Assert write_point was called with correct arguments
        expected_tags = {"site": "site_A"}
        expected_fields = test_payload # The entire payload is passed as fields
        expected_timestamp = "ISO_TIME(1700000000)" # From mock_timestampstr
        
        self.eccts.write_point.assert_called_once_with(
            "energycost", 
            expected_tags, 
            expected_fields, 
            expected_timestamp
        )

    def test_record_powerconsumption_missing_name_raises_keyerror(self):
        """Test that missing 'name' raises a KeyError."""
        
        test_payload_missing_name = {
            "ts": 1700000000,
            "net_cost": 5.25,
        }
        
        # The method accesses m["name"], so it should raise KeyError
        with self.assertRaises(KeyError):
            self.eccts.record_powerconsumption(test_payload_missing_name)

    def test_record_powerconsumption_missing_ts_raises_keyerror(self):
        """Test that missing 'ts' raises a KeyError."""
        
        test_payload_missing_ts = {
            "name": "site_A",
            "net_cost": 5.25,
        }
        
        # The method accesses m["ts"], so it should raise KeyError
        with self.assertRaises(KeyError):
            self.eccts.record_powerconsumption(test_payload_missing_ts)

if __name__ == '__main__':
    unittest.main()
