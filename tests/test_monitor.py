import unittest
import pandas as pd
from src.monitor import load_config, fetch_iocs

class TestMonitor(unittest.TestCase):
    def test_load_config(self):
        config = load_config('config/config.yaml')
        self.assertIn('ioc_sources', config)

    def test_fetch_iocs(self):
        test_data = [
            {"ipAddress": "192.168.1.1"},
            {"ipAddress": "192.168.1.2"}
        ]
        iocs = fetch_iocs(test_data=test_data)
        self.assertIsInstance(iocs, pd.DataFrame)
        self.assertEqual(len(iocs), 2)

if __name__ == '__main__':
    unittest.main()
