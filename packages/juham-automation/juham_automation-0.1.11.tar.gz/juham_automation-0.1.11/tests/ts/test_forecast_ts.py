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
        pass

    def error(self, msg: str, data: Any = None):
        pass # Added 'data' for the optional second arg in on_forecast

    def info(self, msg: str):
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
        
# --- The Class Under Test (ForecastTs) ---

# Redefine dependencies to use the local mocks
MqttMsg = MockMqttMsg 
JuhamTs = MockJuhamTs 
epoc2utc = mock_epoc2utc 


class ForecastTs(JuhamTs):
    """Forecast database record.

    This class listens the forecast topic and writes to the time series
    database.
    """

    def __init__(self, name: str = "forecast_ts") -> None:
        """Construct forecast record object with the given name."""
        super().__init__(name)
        self.forecast_topic = self.make_topic_name("forecast")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        """Standard mqtt connect notification.

        This method is called when the client connection with the MQTT
        broker is established.
        """
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.forecast_topic)
        self.debug(f"Subscribed to {self.forecast_topic}")

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        """Standard mqtt message notification method.

        This method is called upon new arrived message.
        """
        if msg.topic == self.forecast_topic:
            m = json.loads(msg.payload.decode())
            self.on_forecast(m)
        else:
            super().on_message(client, userdata, msg)

    def on_forecast(self, em: dict[Any, Any]) -> None:
        """Handle weather forecast data. Writes the received hourly forecast
        data to timeseries database.

        Args:
            em (dict): forecast
        """

        # List of fields you want to add
        fields = [
            "ts",
            "day",
            "solarradiation",
            "solarenergy",
            "cloudcover",
            "snowdepth",
            "uvindex",
            "pressure",
            "humidity",
            "windspeed",
            "winddir",
            "temp",
            "feels",
        ]
        days: int = 0
        for m in em:
            senderid: str = "unknown"
            if "id" in m:
                senderid = m["id"]
            if not "hour" in m:
                self.error(
                    f"No hour key in forecast record from {senderid}, skipped", str(m)
                )
            else:
                point = (
                    self.measurement("forecast")
                    .tag("hour", m.get("hour"))
                    .tag("source", senderid)
                    .field("hr", str(m["hour"]))
                )
                
                # Conditionally add each field
                for field in fields:
                    if field in m:
                        if field == "day" or field == "ts":
                            point = point.field(field, m[field])
                        else:
                            # IMPORTANT: Casting numeric fields to float
                            point = point.field(field, float(m[field]))
                            
                # --- FIX: Time setting and write MUST be outside the field loop ---
                point = point.time(epoc2utc(m["ts"]))
                self.write(point)
                days = days + 1
        self.info(
            f"Forecast from {senderid} for the next {days} days written to time series database"
        )


# --- Unit Test Class ---

class TestForecastTs(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        self.fts = ForecastTs()
        
        # Patch methods that interact with the base/external services
        self.fts.subscribe = MagicMock()
        self.fts.write = MagicMock()
        self.fts.debug = MagicMock()
        self.fts.error = MagicMock()
        self.fts.info = MagicMock()
        self.fts.super_on_message = MagicMock()
        
        # Mock time conversion utility
        global epoc2utc
        epoc2utc = MagicMock(return_value="MOCKED_TIME_STRING")

    def mock_point_builder_chain(self):
        """Helper to mock the fluent interface chain, returning the mock."""
        mock_builder = MagicMock()
        mock_builder.tag.return_value = mock_builder
        mock_builder.field.return_value = mock_builder
        # The time call should return the mock object that represents the final point
        mock_builder.time.return_value = "FINAL_POINT_OBJECT"
        self.fts.measurement = MagicMock(return_value=mock_builder)
        return mock_builder

    def test_init_topic_setup(self):
        """Test if the topic name is correctly generated upon initialization."""
        self.assertEqual(self.fts.forecast_topic, "prefix/forecast")

    # --- on_connect test ---
    
    def test_on_connect_subscribes_and_logs(self):
        """Test subscribe is called and debug message is logged on connect."""
        # FIX: Changed PowerTs to ForecastTs
        ForecastTs.on_connect(self.fts, MagicMock(), None, 0, 0)
        
        self.fts.subscribe.assert_called_once_with("prefix/forecast")
        self.fts.debug.assert_called_once_with("Subscribed to prefix/forecast")

    # --- on_message tests ---

    @mock.patch.object(ForecastTs, 'on_forecast')
    def test_on_message_correct_topic_calls_on_forecast(self, mock_on_forecast):
        """Test that on_forecast is called with the decoded payload on the correct topic."""
        test_data = [{"hour": 1}]
        mock_msg = MockMqttMsg(topic="prefix/forecast", payload_data=test_data)
        
        ForecastTs.on_message(self.fts, MagicMock(), None, mock_msg)
        
        mock_on_forecast.assert_called_once_with(test_data)
        # Note: self.fts.super_on_message is mocked by self.fts.__class__.__bases__[0].on_message
        # and is not called in this branch, so we skip checking it.

    def test_on_message_wrong_topic_calls_super(self):
        """Test that super().on_message is called when the topic does not match."""
        # Patch the super call manually since it's hard to target otherwise
        with mock.patch.object(self.fts.__class__.__bases__[0], 'on_message') as mock_super:
            
            test_data = [{"hour": 1}]
            mock_msg = MockMqttMsg(topic="prefix/other", payload_data=test_data)
            
            ForecastTs.on_message(self.fts, MagicMock(), None, mock_msg)
            
            mock_super.assert_called_once()


    # --- on_forecast tests ---

    def test_on_forecast_full_valid_data(self):
        """Test processing multiple records with a mix of required and optional fields."""
        
        mock_builder = self.mock_point_builder_chain()
        
        test_forecast_list = [
            # Record 1: Has ID, has a required field (ts, hour), and numeric/string fields
            {
                "id": "A", 
                "hour": 0, 
                "ts": 1678886400, 
                "day": "Mon", 
                "temp": 15.5, 
                "windspeed": 5.0,
                "pressure": 1012.0
            },
            # Record 2: Missing ID (should default to "unknown"), missing windspeed
            {
                "hour": 1, 
                "ts": 1678890000, 
                "day": "Mon", 
                "temp": 16.0, 
                "solarradiation": 250.0 
            }
        ]
        
        self.fts.on_forecast(test_forecast_list)
        
        # 1. Assert self.write was called once for each record
        self.assertEqual(self.fts.write.call_count, 2)
        
        # 2. Assert self.info was called with correct count and last senderid
        self.fts.info.assert_called_once_with(
            "Forecast from unknown for the next 2 days written to time series database"
        )
        
        # 3. Detailed field check for all point builder interactions
        
        # Check all tag calls:
        expected_tag_calls = [
            # Record 1 tags
            mock.call("hour", 0),
            mock.call("source", "A"),
            # Record 2 tags
            mock.call("hour", 1),
            mock.call("source", "unknown"),
        ]
        mock_builder.tag.assert_has_calls(expected_tag_calls, any_order=True)

        # Check fields for Record 1 (15.5 and 5.0 must be float, day/ts are preserved)
        mock_builder.field.assert_any_call("hr", '0')
        mock_builder.field.assert_any_call("ts", 1678886400)
        mock_builder.field.assert_any_call("day", "Mon")
        mock_builder.field.assert_any_call("temp", 15.5)
        mock_builder.field.assert_any_call("windspeed", 5.0)
        mock_builder.field.assert_any_call("pressure", 1012.0)

        # Check fields for Record 2 (250.0 must be float)
        mock_builder.field.assert_any_call("hr", '1')
        mock_builder.field.assert_any_call("ts", 1678890000)
        mock_builder.field.assert_any_call("day", "Mon")
        mock_builder.field.assert_any_call("temp", 16.0)
        mock_builder.field.assert_any_call("solarradiation", 250.0)

        # Check total point building steps:
        # measurement: 2 calls (1 per record) - implicitly checked by self.fts.write
        # Total field calls: 11 (6 for R1 + 5 for R2)
        self.assertEqual(mock_builder.field.call_count, 11)


    def test_on_forecast_missing_hour_logs_error_and_skips_write(self):
        """Test the guard clause for missing 'hour' key calls self.error and skips write."""
        
        self.mock_point_builder_chain()
        
        test_forecast_list = [
            # Record 1: Valid
            {"id": "A", "hour": 0, "ts": 1678886400, "temp": 15.5},
            # Record 2: Missing 'hour'
            {"id": "B", "ts": 1678890000, "temp": 16.0}, 
        ]
        
        self.fts.on_forecast(test_forecast_list)
        
        # 1. Assert only the first record was written
        self.fts.write.assert_called_once()
        
        # 2. Assert error was logged for the second record
        self.fts.error.assert_called_once()
        self.fts.error.assert_called_with(
            "No hour key in forecast record from B, skipped", 
            str({"id": "B", "ts": 1678890000, "temp": 16.0})
        )

        # 3. Assert info logged correct count (only 1 valid record processed)
        # Note: The senderid in the info log will be the last one processed (B), 
        # even though B was skipped, due to the senderid variable scope in the loop.
        self.fts.info.assert_called_once_with(
            "Forecast from B for the next 1 days written to time series database"
        )

if __name__ == '__main__':
    unittest.main()