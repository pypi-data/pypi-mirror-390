import unittest
from tfv.timeseries import FvTimeSeries
import numpy as np
import re
from pathlib import Path
import pandas as pd

path = Path(__file__).parent / 'data'
ts = FvTimeSeries(path / 'HYD_001_time_series.nc')

class TestFvTimeSeries(unittest.TestCase):
    def test_get_data(self):
        tsx = ts.get_data('V_x', 'Point_9', datum='depth')
        self.assertEqual(tsx.shape[0], 145)
    
    def test_get_timeseries(self):
        tsx = ts.get_timeseries('Point_9', ['V_x', 'TEMP'], slice(5))
        self.assertEqual(tsx.sizes['Time'], 5)
        
if __name__ == '__main__':
    unittest.main()
