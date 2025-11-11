import unittest
from tfv.extractor import FvExtractor
import numpy as np
import re
from pathlib import Path
import pandas as pd

path = Path(__file__).parent / 'data'
xtr = FvExtractor(path / 'HYD_002_mini.nc')

class TestFvExtractor(unittest.TestCase):
    def test_get_sheet_cell_V_defaults(self):
        var = 'V' # magic var
        time = 1
        
        data = xtr.get_sheet_cell(var, time)
        print(data.shape)
        self.assertEqual(data.shape[0], xtr.nc2)
    
    def test_get_sheet_cell_TEMP_dave(self):
        var = 'TEMP'
        time = 0
        
        data = xtr.get_sheet_cell(var, time, datum='depth', limits=(0,2.1))      
        
        self.assertEqual(data.shape[0], xtr.nc2)
        
    def test_get_sheet_node_SAL_agg(self):
        var = 'SAL' 
        time = 0
        
        data = xtr.get_sheet_node(var, time, agg='max')
        
        self.assertEqual(data.shape[0], xtr.nv2)
        
    def test_get_sheet_grid(self):
        var = 'V' # magic var
        time = 2
        
        bbox = '159.07645908,-31.40185855,159.11088280,-31.37972153'
        xl, yl, xu, yu = [float(x) for x in bbox.split(',')]
        xg = np.linspace(xl, xu, 19)
        yg = np.linspace(yl, yu, 21)
        
        data = xtr.get_sheet_grid(var, time, xg, yg, datum='height', agg='max')
        
        self.assertEqual(data.shape, (21,19))
        
    def test_get_curtain_grid(self):
        ''' covers pretty much all the curtain functions - if it works, they work '''
        var = 'V' # magic var
        time = '2011-02-01 03:00:43.868682'
        
        with open(path / 'HYD002_Shapely_polyline.txt', 'r') as f:
            ls = f.readline()
        
        polyline = np.asarray([float(x) for x in re.findall(r'-?\d+.\d+', ls)])
        polyline = polyline.reshape([polyline.shape[0]//2, -1])
        
        xg = np.linspace(0, 2400, 20)  # Rough length of polyline
        zg = np.linspace(0, 10, 5)  # Rough depth? 
        
        data = xtr.get_curtain_grid(var, time, polyline, xg, -zg)
        
        data_check = data.sum() > 0
        dim_check = data.shape == (5,20)
        self.assertTrue(all([data_check, dim_check]))
        
    def test_get_profile_cell(self):
        ''' legacy function, that DOUBLES each pt (to create discrete "cells")'''
        
        var = 'V_y'
        time = pd.Timestamp('2011-02-01 02:00:00.263494800')
        lat, lon = -31.37719201, 159.08970821
        
        ii = xtr._timestep_index(time)
        idx = xtr.get_cell_index(lon, lat)
        idx_lfz = xtr.idx4 == idx
        lfz = xtr.get_z_layer_faces(ii)[idx_lfz]
        ndims = int((len(lfz) - 1) * 2)
        
        data = xtr.get_profile_cell(var, time, (lon, lat))
        
        self.assertEqual(data.shape[0], ndims)
        
    def test_extractor_misc_vectors(self):
        ''' test to try extracting data in a variety of forms to prove that the 
        miscellaneous hook is working. '''
        
        data = xtr.get_sheet_cell(['V_x', 'V_y', 'V', 'VDir'], 0)
        
        v = np.hypot(data[0], data[1])
        
        # NAUTICAL TOWARDS
        vdir = (90 - np.arctan2(data[1], data[0]) * 180/np.pi) % 360
        
        self.assertTrue(np.all(np.isclose(data[2], v)))
        self.assertTrue(np.all(np.isclose(data[3], vdir)))

    
    def test_extractor_misc_combos(self):
        ''' test to try extracting data in a variety of forms to prove that the 
        miscellaneous hook is working. '''
        
        data = xtr.get_sheet_cell(['V_x', 'V_y', 'V', 'VDir'], 0)        
        self.assertEqual(data.shape, (4, xtr.nc2))
        
        data = xtr.get_sheet_cell(['V_x', 'TEMP'], 0)        
        self.assertEqual(data.shape, (2, xtr.nc2))
        
        data = xtr.get_sheet_cell(['V', 'SAL'], 0)        
        self.assertEqual(data.shape, (2, xtr.nc2))
        
        v = xtr.get_sheet_cell('V', 0)        
        self.assertEqual(v.shape, (xtr.nc2, ))
        
        vdir = xtr.get_sheet_cell('VDir', 0)
        self.assertEqual(vdir.shape, (xtr.nc2, ))

        
if __name__ == '__main__':
    unittest.main()
