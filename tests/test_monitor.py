import unittest
import pandas as pd
from src.monitor import load_config, fetch_iocs

class TestMonitor(unittest.TestCase):
    def test_load_config(self):
        config = load_config('config/config.yaml')
        self.assertIn('ioc_sources', config)

    def test_fetch_iocs(self):
        test_data1 = [
            {"type": "ip", "value": "192.168.1.1"},
            {"type": "hash", "value": "abcd1234"}
        ]
        test_data2 = [
            {"type": "ip", "value": "192.168.1.2"},
            {"type": "hash", "value": "abcd5678"}
        ]
        iocs = fetch_iocs(test_data=test_data1 + test_data2)
        self.assertIsInstance(iocs, pd.DataFrame)
        self.assertEqual(len(iocs), 4)

if __name__ == '__main__':
    unittest.main()
