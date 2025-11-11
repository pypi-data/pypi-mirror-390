import xarray as xr 
import tfv.xarray
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import dask.array as da

__all__ = ['grid_remap']

def grid_remap(
    ds, 
    x='longitude', 
    y='latitude', 
    time='time', 
    z='depth', 
    flipz=True, 
    spherical=True, 
    use_tfv_naming=True
):
    
    nt = ds.sizes[time]
    
    if z in ds.dims:
        nd = ds.sizes[z]
        zdim = True
    else:
        nd = 1
        zdim = False

    xc = ds[x].values
    yc = ds[y].values
    cells = _get_cell_centers_from_xy(xc, yc)

    nodes, cell_node, node_dim = _compute_vertices(xc, yc)
    
    # First let's only pull out conforming variables (with x, y, and time at minimum).
    # We need to get tricky because rotated grids will often use different dimension names to the coordinate.
    xd = ds[x].dims
    yd = ds[y].dims
    x, y = np.unique(np.hstack((xd, yd)))
    
    all_vars = [v for v in ds.data_vars if all([dm in ds[v].dims for dm in [x, y, time]])]
    vars_2d = [v for v in all_vars if z not in ds[v].dims]
    vars_3d = [v for v in all_vars if z in ds[v].dims]
    # print(f'Detected: {all_vars}') 
    # print(f'Detected: {vars_2d}') 
    # print(f'Detected: {vars_3d}') 
    
    # Identify and remove "dry" cells
    if len(vars_2d) > 0:
        v = vars_2d[0]
    else:
        v = vars_3d[0]
    arr = ds[v][0]
    if z in ds[v].dims:
        arr = arr[0]
    ii2d = ~np.isnan(arr.values.ravel())

    # Now we find out for each cell what the depth array is 
    NL = np.zeros(ii2d.sum(), dtype=int)
    lfzZ_uni = np.zeros(nd+1)
    if len(vars_3d) > 0:
        v = vars_3d[0]
        arr = ds[v][0]
        arr_rv = arr.values.reshape([nd, -1])

        k = 0
        for n in range(arr_rv.shape[1]):        
            if ii2d[n] == True:
                NL[k] = int(nd - np.isnan(arr_rv[:, n]).sum())
                k += 1
    else:
        NL[:] = 1

    # Build idx3, idx3 and Layerface_Z
    nc2 = ii2d.sum()
    nv2 = nodes.shape[0]
    
    if zdim == True:
        mz = ds[z].values
        if flipz == True:
            mz = -1 * mz
        dz = np.diff((-1*mz), prepend=0)/2
        lfz = np.hstack((mz+dz, mz[-1]-dz[-1]))
    else:
        mz = np.array((0, ))
        lfz = np.array((2, -2))

    layerface_Z = []
    idx2 = []
    idx3 = []
    iix3 = 1
    cell_Zb = []
    for n in range(nc2):
        nl = NL[n]
        layerface_Z.extend(lfz[:nl+1].tolist())

        iix = [n + 1 for x in range(nl)]
        
        idx2.extend(iix)
        idx3.append(iix3)
        iix3 += nl

    # Calculate cell_Zb
    cell_Zb = np.zeros((cells.shape[0]), dtype=np.float32)
    nn = 0
    for n in range(cells.shape[0]):
        if ii2d[n] == True:
            cell_Zb[n] = mz[NL[nn]-1]
            nn += 1
        else:
            cell_Zb[n] = 0
    node_Zb = _compute_vertex_z(cell_Zb, cell_node, *node_dim)

    idx3 = np.asarray(idx3).astype(int)
    idx2 = np.asarray(idx2).astype(int)
    layerface_Z = np.asarray(layerface_Z)[None, :] * np.ones(nt)[:, None]
    nc3 = idx2.shape[0]
    
    tvec = (pd.to_datetime(ds[time]) - pd.Timestamp(1990,1,1)).total_seconds() / 3600

    dst = xr.Dataset(
        coords=dict(
            Time=np.arange(nt),
        ),
        data_vars=dict(
            ResTime=(('Time'), tvec),
            cell_Nvert=(('NumCells2D'), np.ones(nc2, dtype=np.int32)*4),
            cell_node=(('NumCells2D', 'MaxNumCellVert'), (cell_node[ii2d]+1).astype(np.int32)),
            NL=(('NumCells2D'), NL.astype(np.int32)),
            idx2=(('NumCells3D'), idx2.astype(np.int32)),
            idx3=(('NumCells2D'), idx3.astype(np.int32)),
            cell_X=(('NumCells2D'), cells[ii2d, 0]), 
            cell_Y=(('NumCells2D'), cells[ii2d, 1]), 
            cell_Zb=(('NumCells2D'), cell_Zb[ii2d].astype(np.float32)),
            cell_A=(('NumCells2D'), np.zeros(nc2).astype(np.float32)),
            node_X=(('NumVert2D'), nodes[:, 0].astype(np.float32)), 
            node_Y=(('NumVert2D'), nodes[:, 1].astype(np.float32)), 
            node_Zb=(('NumVert2D'), node_Zb.astype(np.float32)), 
            layerface_Z=(('Time', 'NumLayerFaces3D'), layerface_Z.astype(np.float32)),
            stat=(('Time', 'NumCells2D'), -1*np.ones((nt, nc2), dtype=np.int32)),
        )
    )
    # Add on the TFV attributes
    dst = _add_tfv_attrs(dst)
    
    dst.attrs = {
        'Origin': 'Created by `tfv` python tools using `grid_to_tfv`',
        'Type': 'Cell-centred TUFLOWFV output',
        'spherical': str(spherical).lower(),
        'Dry depth': 0.01, 
    }

    for v in vars_2d:
        tv, ln = _get_remapped_name(ds, v, use_tfv_naming=use_tfv_naming)
        dst[tv] = (('Time', 'NumCells2D'), ds[v].data.reshape([nt, -1])[:, ii2d])
        dst[tv].attrs = ds[v].attrs
        dst[tv].attrs['long_name'] = ln

    nl2 = []
    xx = 0
    for c in range(nc2):
        for d in range(nd):
            if d <= NL[c] - 1:
                nl2.append(xx)
            xx += 1
    nl2 = np.asarray(nl2)

    for v in vars_3d:
        tv, ln = _get_remapped_name(ds, v, use_tfv_naming=use_tfv_naming)
        arr = ds[v].data.reshape([nt, nd, -1]).transpose([0, 2, 1])[:, ii2d, :].reshape([nt, -1])
        dst[tv] = (('Time', 'NumCells3D'),  arr[:, nl2])
        dst[tv].attrs = ds[v].attrs
        dst[tv].attrs['long_name'] = ln
    return dst.tfv

def _add_tfv_attrs(ds):
    ds['ResTime'].attrs = {'long_name': 'hours since 01/01/1990 00:00:00', 'units': 'hours'}
    ds['cell_Nvert'].attrs = {'long_name': 'Cell number of vertices'}
    ds['cell_node'].attrs = {'long_name': 'Cell node connectivity'}
    ds['NL'].attrs = {'long_name': 'Number of layers in profile'}
    ds['idx2'].attrs = {'long_name': 'Index from 3D to 2D arrays'}
    ds['idx3'].attrs = {'long_name': 'Index from 2D to 3D arrays'}
    ds['cell_X'].attrs = {'long_name': 'Cell Centroid X-Coordinate', 'units': 'm'}
    ds['cell_Y'].attrs = {'long_name': 'Cell Centroid Y-Coordinate', 'units': 'm'}
    ds['cell_Zb'].attrs = {'long_name': 'Cell Bed Elevation', 'units': 'm'}
    ds['cell_A'].attrs = {'long_name': 'Cell Area', 'units': 'm^2'}
    ds['node_X'].attrs = {'long_name': 'Node X-Coordinate', 'units': 'decimal degrees'}
    ds['node_Y'].attrs = {'long_name': 'Node Y-Coordinate', 'units': 'decimal degrees'}
    ds['node_Zb'].attrs = {'long_name': 'Node Bed Elevation', 'units': 'm'}
    ds['layerface_Z'].attrs = {'long_name': 'Layer Face Z-Coordinates', 'units': 'm'}
    ds['stat'].attrs = {'long_name': 'Cell wet/dry status', 'units': 'boolean'}
    return ds

def _get_remapped_name(ds, v, use_tfv_naming=True):
    name_remap = {
        'surf_el': ('H', 'water surface elevation'), 
        'salinity': ('SAL', 'salinity'), 
        'water_temp': ('TEMP', 'temperature'), 
        'water_u': ('V_x', 'x_velocity'), 
        'water_v': ('V_y', 'y_velocity'),
    }
    if (v in name_remap) & use_tfv_naming:
        tv, ln = name_remap[v]
    else:
        tv = v
        ln = _get_long_name(ds, v)
    return tv, ln

def _get_long_name(ds, v):
    if 'long_name' in ds[v].attrs:
        ln = ds[v].attrs['long_name']
    elif 'standard_name' in ds[v].attrs:
        ln = ds[v].attrs['standard_name']
    else:
        ln = v
    return ln

def _get_cell_centers_from_xy(x, y):
    Xc, Yc = np.meshgrid(x, y, indexing='xy')
    centers = np.vstack([Xc.ravel(), Yc.ravel()]).T
    return centers


def _get_cell_centers_from_xy(x, y):
    """
    Get cell centers from coordinate arrays, handling both regular and rotated grids.
    
    Parameters:
    -----------
    x : np.ndarray
        x-coordinates, can be 1D or 2D
    y : np.ndarray
        y-coordinates, can be 1D or 2D
        
    Returns:
    --------
    centers : np.ndarray
        Array of shape (n_cells, 2) containing (x,y) coordinates of cell centers
    """
    if x.ndim == 1 and y.ndim == 1:
        # Regular grid case
        Xc, Yc = np.meshgrid(x, y, indexing='xy')
    else:
        # Rotated grid case - x and y are already 2D arrays
        Xc, Yc = x, y
        
    centers = np.vstack([Xc.ravel(), Yc.ravel()]).T
    return centers

def _compute_vertices(x, y):
    """
    Compute vertex coordinates and cell-node connectivity for regular or rotated grids.
    
    Parameters:
    -----------
    x : np.ndarray
        x-coordinates, can be 1D or 2D
    y : np.ndarray
        y-coordinates, can be 1D or 2D
        
    Returns:
    --------
    vertices : np.ndarray
        Array of shape (n_vertices, 2) containing (x,y) coordinates of vertices
    cell_node : np.ndarray
        Array of shape (n_cells, 4) containing vertex indices for each cell
    shape : tuple
        Shape of the vertex grid (M+1, N+1)
    """
    if x.ndim == 1 and y.ndim == 1:
        # Regular grid case
        dx = (x[1] - x[0]) / 2.0
        dy = (y[1] - y[0]) / 2.0
        
        # Compute vertex coordinates
        vertices_x = np.concatenate(([x[0] - dx], x + dx))
        vertices_y = np.concatenate(([y[0] - dy], y + dy))
        Xv, Yv = np.meshgrid(vertices_x, vertices_y, indexing='xy')
        
    else:
        # Rotated grid case
        ny, nx = x.shape
        
        # Initialize vertex arrays with one more point in each dimension
        Xv = np.zeros((ny + 1, nx + 1))
        Yv = np.zeros((ny + 1, nx + 1))
        
        # Interior vertices (average of surrounding cell centers)
        Xv[1:-1, 1:-1] = 0.25 * (x[:-1, :-1] + x[1:, :-1] + x[:-1, 1:] + x[1:, 1:])
        Yv[1:-1, 1:-1] = 0.25 * (y[:-1, :-1] + y[1:, :-1] + y[:-1, 1:] + y[1:, 1:])
        
        # Left edge vertices
        Xv[1:-1, 0] = 2 * x[:-1, 0] - Xv[1:-1, 1]
        Yv[1:-1, 0] = 2 * y[:-1, 0] - Yv[1:-1, 1]
        
        # Right edge vertices
        Xv[1:-1, -1] = 2 * x[:-1, -1] - Xv[1:-1, -2]
        Yv[1:-1, -1] = 2 * y[:-1, -1] - Yv[1:-1, -2]
        
        # Top edge vertices
        Xv[0, 1:-1] = 2 * x[0, :-1] - Xv[1, 1:-1]
        Yv[0, 1:-1] = 2 * y[0, :-1] - Yv[1, 1:-1]
        
        # Bottom edge vertices
        Xv[-1, 1:-1] = 2 * x[-1, :-1] - Xv[-2, 1:-1]
        Yv[-1, 1:-1] = 2 * y[-1, :-1] - Yv[-2, 1:-1]
        
        # Corner vertices - extrapolate from interior vertices and edges
        # Top-left corner
        Xv[0, 0] = Xv[0, 1] + Xv[1, 0] - Xv[1, 1]
        Yv[0, 0] = Yv[0, 1] + Yv[1, 0] - Yv[1, 1]
        
        # Top-right corner
        Xv[0, -1] = Xv[0, -2] + Xv[1, -1] - Xv[1, -2]
        Yv[0, -1] = Yv[0, -2] + Yv[1, -1] - Yv[1, -2]
        
        # Bottom-left corner
        Xv[-1, 0] = Xv[-1, 1] + Xv[-2, 0] - Xv[-2, 1]
        Yv[-1, 0] = Yv[-1, 1] + Yv[-2, 0] - Yv[-2, 1]
        
        # Bottom-right corner
        Xv[-1, -1] = Xv[-1, -2] + Xv[-2, -1] - Xv[-2, -2]
        Yv[-1, -1] = Yv[-1, -2] + Yv[-2, -1] - Yv[-2, -2]

    vertices = np.vstack([Xv.ravel(), Yv.ravel()]).T
    cell_node = _cell_to_node_map(*Xv.shape)
    
    return vertices, cell_node, Xv.shape

def _cell_to_node_map(M, N):
    """
    Create cell-to-node connectivity map for a structured grid.
    Works for both regular and rotated grids.
    
    Parameters:
    -----------
    M, N : int
        Number of vertices in each dimension
        
    Returns:
    --------
    map_array : np.ndarray
        Array of shape (n_cells, 4) containing vertex indices for each cell
    """
    n_cells_x = M - 1
    n_cells_y = N - 1
    map_array = np.zeros((n_cells_x * n_cells_y, 4), dtype=int)
    idx = 0
    for i in range(n_cells_x):
        for j in range(n_cells_y):
            # Determine the vertex indices for the current cell
            bottom_left = i * N + j
            bottom_right = bottom_left + 1
            top_left = (i + 1) * N + j
            top_right = top_left + 1

            # Store indices in the map (counter-clockwise ordering)
            map_array[idx] = [top_right, top_left, bottom_left, bottom_right]
            idx += 1
    return map_array

def _compute_vertex_z(cell_centers_z, cell_to_node_map, M, N):
    # Number of nodes
    n_nodes = M * N
    node_z_values = np.zeros(n_nodes)
    count_per_node = np.zeros(n_nodes, dtype=int)

    # For each cell, update the z-values of its nodes
    for idx, (z_val) in enumerate(cell_centers_z):
        nodes = cell_to_node_map[idx]
        for node in nodes:
            node_z_values[node] += z_val
            count_per_node[node] += 1

    # Average the z-values
    node_z_values /= count_per_node

    return node_z_values