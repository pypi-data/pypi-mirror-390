"""A module for reading and writing TUFLOW FV restart files"""

import os
import numpy as np
from netCDF4 import Dataset
from pathlib import Path
from tqdm import tqdm, trange
import pandas as pd
from typing import Union

def write_restart_file(nc2, nc3, time_stamp, cell_Zb, fv_data, out_file):
    """
    Creates a new restart file from data.

    Parameters
    ----------
    nc2 : int
        Number of 2d cells.
    nc3 : int
        Number of 3d cells.
    time_stamp : float
        Time as TUFLOW FV time stamp (hours from 1/1/1990).
    cell_Zb : ndarray
        Cell elevation as (nc2,) array.
    fv_data : ndarray
        Conserved 3D variables as (nc3, n) array (depth, V_x, V_y, SAL, TEMP, SED_1, .... , SED_N)
    out_file : str
        Output path of restart file.
    """

    # get some basic parameters
    t = np.array(time_stamp * 3600)  # time in seconds since 01/01/1990 00:00:00
    nv = fv_data.shape[1]  # number of conserved variables
    dims = np.array([nc2, nc3, nv])  # array of dimensions

    # scale data by depth and transpose
    fv_data = fv_data.copy()  
    good = fv_data[:, 0] > 1e-6
    fv_data[good, 1:] = fv_data[good, 1:] * fv_data[good, :1]
    
    # write the data in binary format as shown
    with open(out_file, 'wb') as f:
        t.astype(np.float64).tofile(f)
        dims.astype(np.int32).tofile(f)
        cell_Zb.astype(np.float32).tofile(f)
        fv_data.astype(np.float32).tofile(f)

def read_restart_file(restart_file, precision='single'):
    """Reads data from a TUFLOW FV restart file
    
    Parameters
    ----------
    restart_file : str
        Path of result file from which restart is being generated.
    """
    with open(restart_file, 'rb') as f:
        time_stamp = np.fromfile(f, np.float64, 1)[0]/3600
        nc2 = np.fromfile(f, np.int32, 1)[0]
        nc3 = np.fromfile(f, np.int32, 1)[0]
        nv = np.fromfile(f, np.int32, 1)[0]

        cell_Zb = np.fromfile(f, np.float32, nc2)

        if precision == 'single':
            fv_data = np.fromfile(f, np.float32).reshape((nc3, nv))
        elif precision == 'double':
            fv_data = np.fromfile(f, np.float64).reshape((nc3, nv))
        else:
            raise ValueError('Only `single` or `double` precision are supported!')
        
        good = fv_data[:, 0] > 1e-6
        fv_data[good, 1:] = fv_data[good, 1:] / fv_data[good, :1]

    return nc2, nc3, time_stamp, cell_Zb, fv_data

def restart_from_result(old_result_file, new_result_file, out_file, n_sigma, time_stamp, variables):
    """
    Creates a restart file from an existing TUFLOW FV result file, using a separate result file for geometry input.

    Parameters
    ----------
    old_result_file : str
        Path of result file from which restart is being generated.
    new_result_file : str
        Path of result file from which to use geometry data (mesh and cell elevations).
    out_file : str
        Output path of restart file.
    n_sigma : int
        Number of sigma layers being used in new model.
    time_stamp : float
        Time as TUFLOW FV time stamp (hours from 1/1/1990).
    variables : list
        List of conserved variables to include in the restart file (V_x, V_y, SAL, TEMP, SED_1, ...).
    """

    # get old result file netCDF handle
    old = Dataset(old_result_file)

    # get new result file netCDF handle
    new = Dataset(new_result_file)

    # get time index from target result file
    tt = np.argmin(np.abs(old['ResTime'][:] - time_stamp))

    # find the nearest 3D index for each cell
    index3D = np.array([], dtype=np.int32)  # maps new 3D to old 3D
    for aa in range(new.dimensions['NumCells2D'].size):

        # get the distance to each 2D cell
        dx = old['cell_X'] - new['cell_X'][aa]
        dy = old['cell_Y'] - new['cell_Y'][aa]
        distance = np.hypot(dx, dy)

        # get the index of the nearest old 2D cell
        nearest2D = np.argmin(distance)

        # get the new water level and bed level
        wl, bl = old['H'][tt, nearest2D].data, new['cell_Zb'][aa].data

        # check if old and new cell is\isn't dry
        dryDepth = new.getncattr('Dry depth')
        newDry = (wl - bl) < dryDepth
        oldDry = (old['stat'][tt, nearest2D] == 0)

        # if new cell is wet but old cell is dry, remap, otherwise bad data
        if (not newDry) and oldDry:
            distance[old['stat'][tt, :] == 0] = np.inf
            nearest2D = np.argmin(distance)
            wl = old['H'][tt, nearest2D].data

        # get the NEW layer face Z for current cell
        idx3 = new['idx3'][aa] - 1
        nlfz = new['NL'][aa] + 1
        idx4 = idx3 + aa

        lfzNew = new['layerface_Z'][tt, idx4:idx4 + nlfz].data

        # update the sigma layers using new water level
        dzTop = (wl - lfzNew[n_sigma]) / n_sigma
        lfzNew[0:n_sigma] = wl - dzTop * np.arange(n_sigma)

        # get the OLD layer face Z for current cell
        idx3 = old['idx3'][nearest2D] - 1
        nlfz = old['NL'][nearest2D] + 1
        idx4 = idx3 + nearest2D

        lfzOld = old['layerface_Z'][tt, idx4:idx4 + nlfz].data

        # get the centres to do a minimum distance search
        zcNew = 0.5 * (lfzNew[:-1] + lfzNew[1:])
        zcOld = 0.5 * (lfzOld[:-1] + lfzOld[1:])

        zcOld = np.tile(zcOld, (zcNew.size, 1)).transpose()

        nearest3D = np.argmin(np.abs(zcOld - zcNew), axis=0)

        index3D = np.hstack((index3D, idx3 + nearest3D))

    # get the 2D depth at each 3D cell (used to scale variables for some reason)
    depth = old['H'][tt, (old['idx2'][index3D] - 1)] - new['cell_Zb'][new['idx2'][:] - 1]

    # create empty array for data
    fvData = np.zeros((len(index3D), len(variables) + 1))

    # always set first column to depth
    fvData[:, 0] = depth

    # fill with other conserved variables
    for aa in range(len(variables)):
        if variables[aa] in old.variables:
            fvData[:, aa + 1] = old[variables[aa]][tt, index3D]

    write_restart_file(new.dimensions['NumCells2D'].size, new.dimensions['NumCells3D'].size,
                       time_stamp, new['cell_Zb'][:].data, fvData, out_file)
    

def read_bed_restart_file(restart_file, precision='single'):
    ''' Read TUFLOW FV Bed Restart File

    Function to read a bed restart binary file, returning contents as a dict

    Args:
        restart_file (str | Path): Full path to the sediment restart file   

    Returns:
        nc2 (int): Number of 2D cells in the model
        nc3 (int): Number of 3D cells in the model
        time_stamp (float): Timestamp in hours since 1990-01-01
        ng (int): Number of sediment fractions in the model
        maxnl (int): Maximum number of sediment layers in the model
        bed_mass (np.ndarray): Bed mass numpy array with shape (Num2DCells, MaxNumBedlayers, SedFractions)
            Note: cells may have varying numbers of bed layers. The returned array will represent empty bedlayers with
            zero bed mass in the sediment fractions dimension.

    '''
    with open(restart_file, 'rb') as f:
        time_stamp = np.fromfile(f, np.float64, 1)[0]/3600
        nc2 = np.fromfile(f, np.int32, 1)[0]
        nc3 = np.fromfile(f, np.int32, 1)[0]
        ng = np.fromfile(f, np.int32, 1)[0]
        maxnl = 1 # default
        #print(nc2)
        #print(nc3)
        #print(f'NG: {ng}')
        
        if precision == 'single':
            dtype = np.float32
        elif precision == 'double':
            dtype = np.float64
        else:
            print('Only `single` or `double` precision is expected. Using `single`')
            dtype = np.float32
        
        # Unknown max bed layers - assume up to 100 and cut down afterwards.
        bed_mass = np.zeros((nc2, 100, ng))
        for c in tqdm(range(nc2), unit='cell', desc='reading bed restart file...'):
            tmp = np.fromfile(f, np.int32, 1)[0] # First is dummy.
            nl = np.fromfile(f, np.int32, 1)[0] # Number of sed layers in this cell
            maxnl = max(maxnl, nl)
            for l in range(nl):
                for g in range(ng):
                    bed_mass[c, l, g] = np.fromfile(f, dtype, 1)[0]
                    
    # Cut down bed layers based on maxnl
    bed_mass = bed_mass[:, :maxnl, :]
    
    return nc2, nc3, time_stamp, ng, maxnl, bed_mass


def write_bed_restart_file(
    restart_file: Union[str, Path], 
    bed_mass: np.ndarray, 
    time=pd.Timestamp(1990,1,1), 
    nc3=999999,
    precision='single'):
    ''' Write TUFLOW FV Bed Restart File

    Function to write a bed restart binary file for sediment transport runs
    
    Note: 
        - If a cell bed layer has zero mass in it, the bed layer will be removed. If you are appending a new bed layer on
        that has zero mass in ALL cells, that layer will be removed for compatability  with TUFLOW FV. 
        To get around this, you may use `np.clip(bed_mass, 1e-4, None)` to set a small amount of mass in every cell. 

    Args:
        restart_file (str | Path): Full path to where the sediment restart file should be written
        bed_mass (np.ndarray): Bed mass numpy array with shape (Num2DCells, MaxNumBedlayers, SedFractions)
        t (pd.Timestamp, optional): Timestamp for the restart file. Not directly used by TFV. Defaults to 1990-01-01.
        nc3 (int, optional): Tag for number of 3D cells. Not directly used by TFV. Defaults to 99999. 
        precision (str, optional): Flag for whether to use `single` or `double` precision. Defaults to `single`. 
        
    Returns:
        None 
    '''
    nc2 = bed_mass.shape[0]
    ng = bed_mass.shape[2]
    t = (time - pd.Timestamp(1990,1,1)).total_seconds()

    if precision == 'single':
        dtype = np.float32
    elif precision == 'double':
        dtype = np.float64
    else:
        print('Only `single` or `double` precision is expected. Using `single`')
        dtype = np.float32
    
    with open(restart_file, 'wb') as f:
        np.array(t).astype(np.float64).tofile(f)
        np.array(nc2).astype(np.int32).tofile(f)
        np.array(nc3).astype(np.int32).tofile(f) # nc3 - irrelevant, so lets make it clear. 
        np.array(ng).astype(np.int32).tofile(f)
    
        # Cycle through cells
        for c in trange(nc2):
            np.array(c+1).astype(np.int32).tofile(f)
    
            # Find number of layers in this cell
            nl = (bed_mass[c, :, :].sum(axis=1) > 0).sum()
            np.array(nl).astype(np.int32).tofile(f)
            # Cycle through layers then seds 
            for l in range(nl):
                for g in range(ng):
                    bm = bed_mass[c, l, g]
                    bm.astype(dtype).tofile(f)


def _restart_from_result_beta(old_result_file, new_fvc_file, out_file, time_stamp, variables):
    """
    An untested version in the making which directly reads from a .fvc file the new geometry.

    Limited because it does not read for elevation limits set based on material type or shape file.

    This could one day be improved.
    """

    # set default geometry parameters
    cellFile = None
    numSigma = None
    layerFile = None
    minThick = None

    # read parameters from .fvc file
    with open(new_fvc_file, 'r') as f:
        # get start line
        line = f.readline()
        while line != '':
            if 'cell elevation file' in line:
                cellFile = line.split('==')[-1].strip()
            if 'sigma layers' in line:
                numSigma = int(line.split('==')[-1].strip())
            if 'layer faces' in line:
                layerFile = line.split('==')[-1].strip()
            if 'min bottom layer thickness' in line:
                minThick = float(line.split('==')[-1].strip())

            # read the next line
            line = f.readline()

    # get path to .fvc file folder
    fvcFolder = os.path.split(new_fvc_file)[0]

    # set paths to absolute, assume they are relative in the .fvc file
    cellFile = os.path.abspath(os.path.join(fvcFolder, cellFile))
    layerFile = os.path.abspath(os.path.join(fvcFolder, layerFile))

    # read the cell centred elevations
    data = np.loadtxt(cellFile, skiprows=1, delimiter=',', dtype=np.float64)
    cellX, cellY, cellZb = data[:, 0], data[:, 1], data[:, 2]

    # read the fixed elevation layers
    zLayers = np.loadtxt(layerFile, skiprows=1, delimiter=',', dtype=np.float64)

    # get result file netCDF handle
    old = Dataset(old_result_file)

    # get time index from target result file
    tt = np.argmin(np.abs(old['ResTime'] - time_stamp))

    # find the nearest 3D index for each cell
    index3D = np.array([], dtype=np.int32)  # maps new 3D to old 3D
    idx2 = np.array([], dtype=np.int32)  # maps new 2D to 3D
    for aa in range(cellZb.size):

        # get the distance to each 2D cell
        dx = old['cell_X'] - cellX[aa]
        dy = old['cell_Y'] - cellY[aa]
        distance = np.hypot(dx, dy)

        # get the index of the nearest old 2D cell
        nearest2D = np.argmin(distance)

        # check if old and new cell is\isn't dry
        dryDepth = old.getncattr('Dry depth')
        newDry = (old['H'][tt, nearest2D] - cellZb[aa]) < dryDepth
        oldDry = (old['stat'][tt, nearest2D] == 0)

        # if new cell is wet but old cell is dry, remap
        if (not newDry) and oldDry:
            distance[old['stat'][tt, :] == 0] = np.inf
            nearest2D = np.argmin(distance)

        # get the new water level and bed level
        wl, bl = old['H'][tt, nearest2D].data, cellZb[aa]

        # start from the top with the sigma layers
        dzTop = (wl - zLayers[0]) / numSigma
        lfzNew = wl - dzTop * np.arange(numSigma)

        # add in the elevation layers above the bed
        aboveBed = zLayers > bl
        botThick = zLayers - bl
        goodThick = botThick > minThick

        lgi = aboveBed & goodThick

        lfzNew = np.hstack((lfzNew, zLayers[lgi], bl))

        idx2 = np.hstack((idx2, np.repeat(aa, len(lfzNew) - 1)))

        # use layer faces to map new to old 3D points
        idx3 = old['idx3'][nearest2D] - 1
        nlfz = old['NL'][nearest2D] + 1
        idx4 = idx3 + nearest2D

        lfzOld = old['layerface_Z'][tt, idx4:idx4 + nlfz].data

        zcNew = 0.5 * (lfzNew[:-1] + lfzNew[1:])
        zcOld = 0.5 * (lfzOld[:-1] + lfzOld[1:])

        zcOld = np.tile(zcOld, (zcNew.size, 1)).transpose()

        nearest3D = np.argmin(np.abs(zcOld - zcNew), axis=0)

        index3D = np.hstack((index3D, idx3 + nearest3D))

    # get the 2D depth at each 3D cell (used to scale variables for some reason)
    depth = old['H'][tt, (old['idx2'][index3D] - 1)] - cellZb[idx2]

    # create empty array for data
    fvData = np.zeros((len(index3D), len(variables) + 1))

    # always set first column to depth
    fvData[:, 0] = depth

    # fill with other conserved variables
    for aa in range(len(variables)):
        if variables[aa] in old.variables:
            fvData[:, aa + 1] = old[variables[aa]][tt, index3D]

    write_restart_file(cellZb.size, idx2.size, time_stamp, cellZb, fvData, out_file)

