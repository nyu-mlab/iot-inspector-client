import unittest
import datetime
import time
from iot_inspector.server.pcap_check import make_pcap_filename

class TestCollector(unittest.TestCase):

    def test_pcap_name_generation(self):
        # 1. Capture the current epoch once
        start_time = int(time.time())
        duration = 600
        end_time = start_time + duration

        # 2. Generate the filename
        generated_name = make_pcap_filename(start_time, end_time)
        print(f"Testing with: {generated_name}")

        # 3. Calculate local expectations based on THAT specific start_time
        # This ensures the test passes regardless of the timezone it runs in.
        expected_dt = datetime.datetime.fromtimestamp(start_time).astimezone()

        expected_year = expected_dt.strftime("%Y")
        expected_month = expected_dt.strftime("%b")
        expected_day = expected_dt.strftime("%d")
        # Format the duration to match the 2 decimal places in your function
        expected_duration_str = f"{duration:.2f}s"

        # 4. Assertions
        self.assertIn(expected_year, generated_name)
        self.assertIn(expected_month, generated_name)
        self.assertIn(expected_day, generated_name)
        self.assertIn(expected_duration_str, generated_name)
        self.assertTrue(generated_name.endswith(".pcap"))