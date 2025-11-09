import unittest
import json
from unittest import mock
from typing import Any, Dict, List
from unittest.mock import MagicMock, call
from typing_extensions import override
import unittest
import json
from unittest import mock
from typing import Any, Dict, List
from unittest.mock import MagicMock, call
from typing_extensions import override

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

    # Fluent Interface Mocks (for point construction)
    # NOTE: The actual implementation uses a side_effect in the test setUp.
    def measurement(self, name: str):
        # We need this placeholder method for the class definition
        pass

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
    def __init__(self, topic: str, payload_data: List[Dict]):
        self.topic = topic
        # The payload_data is expected to be a list of hourly dicts for this class
        self.payload_data = payload_data
        self.payload = self
    
    # Simulates bytes payload decoding for json.loads()
    def decode(self):
        return json.dumps(self.payload_data)

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 


# --- The Class Under Test (ElectricityPriceTs) ---

class ElectricityPriceTs(JuhamTs):
    """Spot electricity price for reading hourly electricity prices from"""

    def __init__(self, name: str = "electricityprice_ts") -> None:
        super().__init__(name)

        self.spot_topic = self.make_topic_name("spot")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.spot_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.spot_topic:
            # We assume the payload decodes to a list of dicts here
            em = json.loads(msg.payload.decode())
            self.on_spot(em)
        else:
            super().on_message(client, userdata, msg)

    def on_spot(self, m: List[Dict[Any, Any]]) -> None:
        """Write hourly spot electricity prices to time series database.

        Args:
            m (list of dicts): holding hourly spot electricity prices
        """
        grid_cost : float
        for h in m:
            if "GridCost" in h:
                grid_cost = h["GridCost"]
                point = (
                    self.measurement("spot")
                    .tag("hour", h["Timestamp"])
                    .field("value", h["PriceWithTax"])
                    .field("grid", grid_cost)
                    .time(epoc2utc(h["Timestamp"]))
                )
                self.write(point)


# --- Unit Test Class ---

class TestElectricityPriceTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.epts = ElectricityPriceTs()
        
        # Patch methods that interact with external services/base class
        self.epts.subscribe = MagicMock()
        self.epts.write = MagicMock()
        self.epts.error = MagicMock()
        
        # List to track all individual mock builders created by self.epts.measurement()
        self.point_builders: List[MagicMock] = []
        
        # Mock the measurement call to track the individual builders it returns
        def measurement_side_effect(name):
            mock_builder = self._get_mock_builder()
            self.point_builders.append(mock_builder)
            return mock_builder
            
        self.epts.measurement = MagicMock(side_effect=measurement_side_effect)
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(side_effect=lambda ts: f"Time({ts})")

    def _get_mock_builder(self):
        """Helper to create a fresh mock builder for each call to measurement()."""
        mock_builder = MagicMock()
        mock_builder.tag.return_value = mock_builder
        mock_builder.field.return_value = mock_builder
        mock_builder.time.return_value = "FINAL_POINT_OBJECT"
        return mock_builder

    # --- __init__ and on_connect tests ---

    def test_init_topic_setup(self):
        """Test if the spot topic name is correctly generated upon initialization."""
        self.assertEqual(self.epts.spot_topic, "prefix/spot")

    def test_on_connect_success_subscribes_to_spot(self):
        """Test subscribe is called for the spot topic when connection is successful (rc=0)."""
        ElectricityPriceTs.on_connect(self.epts, MagicMock(), None, 0, 0)
        self.epts.subscribe.assert_called_once_with("prefix/spot")

    def test_on_connect_failure_does_not_subscribe(self):
        """Test subscribe is NOT called when connection fails (rc!=0)."""
        ElectricityPriceTs.on_connect(self.epts, MagicMock(), None, 0, 1) # rc=1 (failure)
        self.epts.subscribe.assert_not_called()

    # --- on_message (Routing) tests ---
    
    @mock.patch.object(ElectricityPriceTs, 'on_spot')
    def test_on_message_routes_to_on_spot(self, mock_on_spot):
        """Test routing for the spot topic."""
        test_data = [{"Timestamp": 1, "PriceWithTax": 10.0, "GridCost": 2.0}]
        mock_msg = MockMqttMsg(topic="prefix/spot", payload_data=test_data)
        
        ElectricityPriceTs.on_message(self.epts, MagicMock(), None, mock_msg)
        
        mock_on_spot.assert_called_once_with(test_data)

    def test_on_message_unhandled_topic_calls_super(self):
        """Test fallback to super() for unhandled topics."""
        test_data = [{"data": "ignored"}]
        mock_msg = MockMqttMsg(topic="prefix/other_topic", payload_data=test_data)
        
        # Patch the super call manually
        with mock.patch.object(self.epts.__class__.__bases__[0], 'on_message') as mock_super:
            ElectricityPriceTs.on_message(self.epts, MagicMock(), None, mock_msg)
            
            mock_super.assert_called_once()
            

    # --- on_spot tests ---

    def test_on_spot_success_with_multiple_points(self):
        """Test that multiple valid hourly points are correctly written."""
        
        test_payload = [
            # Point 1: Valid data
            {"Timestamp": 1678886400, "PriceWithTax": 50.0, "GridCost": 1.5},
            # Point 2: Valid data
            {"Timestamp": 1678890000, "PriceWithTax": 60.5, "GridCost": 1.6},
        ]
        
        self.epts.on_spot(test_payload)
        
        # Assert that write was called twice (once for each point)
        self.assertEqual(self.epts.write.call_count, 2)
        self.assertEqual(self.epts.measurement.call_count, 2)
        self.assertEqual(len(self.point_builders), 2)
        
        builder1 = self.point_builders[0]
        builder2 = self.point_builders[1]

        # Check the construction of the first point
        builder1.tag.assert_called_once_with("hour", 1678886400)
        builder1.field.assert_has_calls([
            mock.call("value", 50.0),
            mock.call("grid", 1.5)
        ])
        epoc2utc.assert_any_call(1678886400)
        
        # Check the construction of the second point
        builder2.tag.assert_called_once_with("hour", 1678890000)
        builder2.field.assert_has_calls([
            mock.call("value", 60.5),
            mock.call("grid", 1.6)
        ])
        epoc2utc.assert_any_call(1678890000)

        self.epts.write.assert_has_calls([call("FINAL_POINT_OBJECT"), call("FINAL_POINT_OBJECT")])
        self.epts.error.assert_not_called()

    def test_on_spot_skips_point_missing_gridcost(self):
        """Test that points missing 'GridCost' are correctly skipped."""
        
        test_payload = [
            {"Timestamp": 1, "PriceWithTax": 50.0, "GridCost": 1.5}, # Valid (Builder 1)
            {"Timestamp": 2, "PriceWithTax": 60.5},                  # Missing GridCost - MUST be skipped
            {"Timestamp": 3, "PriceWithTax": 70.0, "GridCost": 1.7}, # Valid (Builder 2)
        ]
        
        self.epts.on_spot(test_payload)
        
        # Assert write and measurement were called exactly twice
        self.assertEqual(self.epts.write.call_count, 2)
        self.assertEqual(self.epts.measurement.call_count, 2)
        self.assertEqual(len(self.point_builders), 2)
        
        builder1 = self.point_builders[0]
        builder2 = self.point_builders[1]

        # Check Point 1 (Valid)
        builder1.tag.assert_called_once_with("hour", 1)
        
        # Check Point 2 (Valid, using timestamp 3)
        builder2.tag.assert_called_once_with("hour", 3)
        
        self.epts.error.assert_not_called()

    def test_on_spot_raises_keyerror_if_timestamp_is_missing(self):
        """Test that a missing 'Timestamp' raises a KeyError (due to lack of validation)."""
        test_payload = [
            {"Timestamp": 1, "PriceWithTax": 50.0, "GridCost": 1.5}, 
            {"PriceWithTax": 60.5, "GridCost": 1.6},                  # Missing Timestamp
        ]
        
        # The code will raise KeyError on h["Timestamp"] when calling .tag()
        with self.assertRaises(KeyError) as cm:
            self.epts.on_spot(test_payload)
            
        self.assertIn("'Timestamp'", str(cm.exception))
        
        # Ensure only the first point was written before the crash
        self.assertEqual(self.epts.write.call_count, 1)

    def test_on_spot_raises_keyerror_if_pricewithtax_is_missing(self):
        """Test that a missing 'PriceWithTax' raises a KeyError (due to lack of validation)."""
        test_payload = [
            {"Timestamp": 1, "PriceWithTax": 50.0, "GridCost": 1.5}, 
            {"Timestamp": 2, "GridCost": 1.6},                       # Missing PriceWithTax
        ]
        
        # The code will raise KeyError on h["PriceWithTax"] when calling .field("value", ...)
        with self.assertRaises(KeyError) as cm:
            self.epts.on_spot(test_payload)
            
        self.assertIn("'PriceWithTax'", str(cm.exception))
        
        # Ensure only the first point was written before the crash
        self.assertEqual(self.epts.write.call_count, 1)

if __name__ == '__main__':
    unittest.main()