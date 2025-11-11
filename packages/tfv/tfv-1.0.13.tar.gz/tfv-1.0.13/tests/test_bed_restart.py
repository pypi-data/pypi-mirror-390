import unittest
from tfv.restart import *
from pathlib import Path
import os
import numpy as np

path = Path(__file__).parent / 'data'

class TestRestartModule(unittest.TestCase):
    def test_rw_hdrst(self):
        ''' Test read a HD restart, write it out, read it back in and assert equality '''
        
        fname = path / 'HYD_002.rst'       
        nc2, nc3, time_stamp, cell_Zb, fv_data = read_restart_file(fname)
        
        oname = fname.as_posix().replace('.rst', 'TMP.rst')
        print(oname)
        write_restart_file(nc2, nc3, time_stamp, cell_Zb, fv_data, oname)
        
        _, _, _, _, fv_data_NEW = read_restart_file(oname)
        
        # Read back in the temp restart and assert equality 
        msk = np.isclose(fv_data, fv_data_NEW)
        self.assertEqual(msk.sum(), fv_data.size)
        
        os.remove(oname)

    def test_rw_sedrst(self):
        ''' Test read a SED bedmass restart, write it out, read it back in and assert equality '''
        
        fname = path / 'SED_002_bed.rst'       
        nc2, nc3, time_stamp, ng, maxnl, bed_mass = read_bed_restart_file(fname)
        
        oname = fname.as_posix().replace('.rst', 'TMP.rst')
        write_bed_restart_file(oname, bed_mass)
        
        _, _, _, _,_,bed_mass_NEW = read_bed_restart_file(oname)
        
        # Read back in the temp restart and assert equality 
        msk = np.isclose(bed_mass, bed_mass_NEW)
        self.assertEqual(msk.sum(), bed_mass.size)
        
        os.remove(oname)
        