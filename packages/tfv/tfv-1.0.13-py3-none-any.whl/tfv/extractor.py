"""A module defining all Extractor classes. Extractors are the primary objects for model result data extraction"""

from ast import Slice
import os
import re
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd
from scipy import sparse
from inspect import getdoc
from abc import ABC, abstractmethod
from typing import Union
from types import GeneratorType
from datetime import datetime as dt
from dask.diagnostics import ProgressBar
import dask.array as da
from tqdm import tqdm
import warnings

# from netCDF4 import Dataset
from tfv.geometry import Mesh
from tfv.miscellaneous import *
from tfv.mldatetime import *

time_slice_err = [
    "`time_limits` optional argument must be a slice function",
    "Examples:",
    "   slice(0, 10) for the first 10 timesteps",
    "   slice('2020-01-01', '2020-02-01') to slice between dates",
    "For more help, please refer to Pandas `.loc` or Xarray `.isel` or `.sel` methods",
]


class Extractor(ABC):
    """
    A base class that defines the API for all model result subclasses. Examples of these subclasses
    might be model results such as a TUFLOW FV NetCDF file, a Hycom NetCDF file or a TUFLOW FV .dat file.
    """

    result_type = None

    def __init__(
        self,
        file: Union[Path, str, xr.Dataset],
        is_spherical: bool,
        lazy_load: bool,
        warmup: Union[str, pd.Timedelta],
    ):
        """Initializes Extractor object with a model results file i.e A TUFLOW FV netCDF4 results file."""

        # Store file path string as attribute
        self.file = file
        self.is_spherical = is_spherical

        # Convert warmup
        if isinstance(warmup, str):
            warmup = pd.Timedelta(warmup)

        # Prepare static Extractor attributes
        self.__prep_file_handle__(lazy_load, warmup)
        self.__prep_2d_geometry__()
        self.__prep_3d_geometry__()

    @abstractmethod
    def get_raw_data(self, variable: str, ii: int):
        """
        Query to extract raw data at a time step (if time-varying).

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            The time vector index at which to extract the data.

        Returns
        -------
        data : np.ndarray
            The raw data as 1D or 2D numpy array
        """
        pass

    @abstractmethod
    def get_mask_vector(self, ii: int):
        """
        Query to extract an array that defines invalid model data.

        Parameters
        ----------
        ii : integer
            Time index at which to extract the stat array.

        Returns
        -------
        mask : np.ndarray
            Logical index, True if model cells/nodes are invalid (i.e dry cells).

        """
        pass

    @abstractmethod
    def get_z_layer_faces(self, ii: int):
        """
        Query to extract an array that defines the vertical layer faces of a 3D model.

        Parameters
        ----------
        ii : integer
            Time index at which to extract the vertical layer faces.

        Returns
        -------
        lfz : np.darray
            Vertical layer faces. If model is 2D returns None.

        """
        pass

    @abstractmethod
    def get_integral_data(self, ii: int, datum: str, limits: tuple):
        """
        Query to extract data for vertical integration at given time step. Principle data is the
        integral limit (z2 - z1) for each 2D model cell/node and dz for each 3D model cell/node.

        Parameters
        ----------
        ii : integer
            Time index at which to extract the vertical layer faces.
        datum : str
            {'sigma', 'depth', 'height', 'elevation'}
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits (z1, z2) relative to vertical datum.

        Returns
        -------
        z_data : tuple, (z2_z1, dz)
            The elevation limits (z2 - z1) for each 2D cell/node & dz for each 3D cell/node

        """
        pass

    @abstractmethod
    def get_sheet_cell(
        self, variable: str, ii: int, datum="sigma", limits=(0, 1), z_data: tuple = None
    ):
        """
        Query to extract data in a 2D map format ('sheet') at model cell centroids for a given time step. If model
        data is 3D then it is depth-averaged according to the depth-averaging vertical datum and vertical limits.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        datum : {'sigma', 'depth', 'height', 'elevation'}
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits (z1, z2) relative to vertical datum.

        Other Parameters
        ----------------
        z_data : tuple, optional
            Vertical integration data returned by ```self.get_integral_data```

        Returns
        -------
        data : np.ndarray
            A 2D spatial 'sheet' of the relevant variable at time step ii.

        """
        pass

    @abstractmethod
    def get_sheet_node(
        self, variable: str, ii: int, datum="sigma", limits=(0, 1), z_data: tuple = None
    ):
        """
        Query to extract data in a 2D map format ('sheet') at model cell vertices for a given time step. If model
        data is 3D then it is depth-averaged according to the depth-averaging vertical datum and vertical limits.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        datum : {'sigma', 'depth', 'height', 'elevation'}
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits (z1, z2) relative to vertical datum.
        z_data : tuple, optional
            Vertical integration data returned by self.get_integral_data

        Returns
        -------
        data : np.ndarray
            A 2D spatial 'sheet' of the relevant variable at time step ii.

        """
        pass

    @abstractmethod
    def get_sheet_grid(
        self,
        variable: str,
        ii: int,
        grid_x: np.ndarray,
        grid_y: np.ndarray,
        datum="sigma",
        limits=(0, 1),
        z_data: tuple = None,
        grid_index: np.ndarray = None,
    ):
        """
        Query to extract data in a 2D map format ('sheet') at fixed grid points for a given time step. If model
        data is 3D then it is depth-averaged according to the depth-averaging vertical datum and vertical limits.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        grid_x : 1D np.ndarray
            Horizontal grid point values
        grid_y : 1D np.ndarray
            Vertical grid point values
        datum : {'sigma', 'depth', 'height', 'elevation'}
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits (z1, z2) relative to vertical datum.

        Other Parameters
        ----------------
        z_data : tuple, optional
            Vertical integration data returned by self.get_integral_data
        grid_index : 2D np.ndarray
            Mesh cell index for each grid point returned by self.get_grid_index

        Returns
        -------
        data  : 2D np.ndarray
            A gridded 2D spatial 'sheet' of the relevant variable at time step ii.

        """
        pass

    @abstractmethod
    def get_curtain_cell(
        self,
        variable: str,
        ii: int,
        polyline: np.ndarray,
        x_data: tuple = None,
        index: tuple = None,
    ):
        """
        Query to extract data in a 2D slice format ('curtain') at the cell centroids for a given time step. It does
        this along the polyline specified.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        polyline : 2D np.ndarray
            Polyline as [x, y] used to slice 3D data.

        Other Parameters
        ----------------
        x_data : tuple
            Model edge intersection(x) data returned by self.get_intersections.
        index : tuple
            Curtain index data returned by self.get_curtain_cell_index.

        Returns
        -------
        data : np.ndarray
            A 2D slice 'curtain' of the relevant variable at time step ii.

        """
        pass

    @abstractmethod
    def get_curtain_edge(
        self,
        variable: str,
        ii: int,
        polyline: np.ndarray,
        x_data: tuple = None,
        index: tuple = None,
    ):
        """
        Query to extract data in a 2D slice format ('curtain') at the cell centroids for a given time step. It does
        this along the polyline specified.

        This function is currently not supported.
        """
        pass

    @abstractmethod
    def get_curtain_grid(
        self,
        variable: str,
        ii: int,
        polyline: np.ndarray,
        grid_x: np.ndarray,
        grid_y: np.ndarray,
        x_data: tuple = None,
        index: tuple = None,
        grid_index: np.ndarray = None,
    ):
        """
        Query to extract data in a 2D slice format ('curtain') at fixed grid points for a given time step. It does
        this along the polyline specified.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        polyline : 2D np.ndarray
            Polyline as [x, y] used to slice 3D data.
        grid_x : 1D np.ndarray
            Horizontal grid point values
        grid_y : 1D np.ndarray
            Vertical grid point values

        Other Parameters
        ----------------
        x_data : tuple
            Model edge intersection(x) data returned by self.get_intersections.
        index : tuple
            Curtain index data returned by self.get_curtain_cell_index.
        grid_index : 2D np.ndarray
            Curtain cell index for each grid point

        Returns
        -------
        data : 2D np.ndarray
            A gridded 2D slice 'curtain' of the relevant variable at time step ii.

        """
        pass

    @abstractmethod
    def get_profile_cell(self, variable, ii, point, index=None):
        """
        Query to extract data as 1D vertical profile of cells at the given time step.
        It does this at the point specified.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        ii : integer
            Time index at which to extract the data.
        point : tuple
            Point (x, y) of profile location.

        Other Parameters
        ----------------
        index : integer
            Index of cell which contains the point.

        Returns
        -------
        data : np.ndarray
            A 1D section of the vertical values of the relevant variable.

        """
        pass

    @abstractmethod
    def __prep_file_handle__(self):
        """Command which prepares the file handle for the extractor class"""

    @abstractmethod
    def __prep_time_vector__(self):
        """Command which prepares the result time stamp vector relative to python epoch"""

    @abstractmethod
    def __prep_2d_geometry__(self):
        """Command which prepares the result 2D mesh geometry"""

    @abstractmethod
    def __prep_3d_geometry__(self):
        """A command which prepares the result 3D mesh geometry"""


class FvExtractor(Extractor, Mesh):
    """
    Class that extracts data from a TUFLOW FV netCDF4 result file.

    Parameters
    ----------
    file : string
        Model result file path.

    Other Parameters
    ----------------
    is_spherical : bool
        True if model geometry defined in spherical coordinate reference system.

    Attributes
    ----------
    nc2 : int
        Number of 2D mesh cells
    nv2 : int
        Number of 2D mesh vertices
    is_tri : 1D np.ndarray
        Logical index of triangular elements
    is_quad : 1D np.ndarray
        Logical index of quadrilateral elements
    edge_node : tuple
        Tuple defining start node, end node and cell for each mesh half edge
    weights : 2D np.ndarray
        A (n, 4) array defining weighting of each cell gives to each mesh vertex
    tri_cell_node : 2D np.ndarray
        A (n, 3) array defining each mesh cell/element by three node indices
    tri_cell_index : 1D np.ndarray
        A (n,) array mapping triangular mesh elements to base mesh elements
    nc : netCDF4.Dataset
        Dataset object
    nz: np.ndarray
        A (nc2,) array defining number of vertical cells in each 2D model mesh cell
    idx2: np.ndarray
        A (nc3,) array defining the 2D model mesh cell index for each 3D cell
    idx3: np.ndarray
        A (nc2,) array defining the surface 3D model mesh cell index for each 2D model mesh cell
    idx4: np.ndarray
        A (nc3+nc2,) array defining the 2D model mesh cell index for each 3D vertical layer face
    wli: np.ndarray
        A (nc2,) array defining the surface vertical layer face index for each 2D model mesh cell
    bli: np.ndarray
        A (nc2,) array defining the bed vertical layer face index for each 2D model mesh cell
    """

    result_type = "Cell-centred TUFLOWFV output"

    def __init__(
        self,
        file: Union[Path, str, xr.Dataset],
        lazy_load: bool = True,
        is_spherical: bool = True,
        warmup: Union[str, pd.Timedelta] = "0D",
    ):
        super(FvExtractor, self).__init__(file, is_spherical, lazy_load, warmup)
        # self.__promote_coords__()

    @property
    def variables(self):
        return [
            x
            for x in self.ds.data_vars.keys()
            if "Time" in self.ds[x].dims
            if x not in ["ResTime", "stat", "layerface_Z"]
        ]

    @property
    def vector_variables(self):
        vecvar_map = {}
        for var in self.variables:
            if var[-2:] == "_x":
                basevar = var[:-2]
                if basevar + "_y" in self.variables:
                    vecvar_map[basevar] = (basevar + "_x", basevar + "_y")
        return vecvar_map

    # def _repr_(self):
    #     print(ds.__repr__())

    # def _repr_html_(self):
    #     display(self.ds)

    # def __getitem__(self, variable):
    #     return self.ds[variable]

    # def __setitem__(self, variable, array):
    #     self.ds[variable] = array

    def get_raw_data(self, variable: str, ii: int, dask=False):
        if dask:
            return self.ds[variable][ii, :].data
        else:
            return self.ds[variable][ii, :].values

    def get_mask_vector(self, ii: int, dask=False):
        if dask:
            return self.ds["stat"][ii, :].data == 0
        else:
            return self.ds["stat"][ii, :].values == 0

    def get_z_layer_faces(self, ii: int, dask=False):
        if dask:
            return self.ds["layerface_Z"][ii, :].data
        else:
            return self.ds["layerface_Z"][ii, :].values

    def get_integral_data(
        self, ii: int, datum: str, limits: tuple, lfz=None, dask=False
    ):
        if lfz is None:
            lfz = self.get_z_layer_faces(ii, dask=dask)

        # Ensure lfz is a Dask array
        if dask is False:
            lfz = np.asarray(lfz)
            assert isinstance(
                ii, (int, np.int64, np.int32)
            ), "Only single timestep can be handled unless `dask=True`"

        # Handle both single and multiple timesteps
        if lfz.ndim == 1:
            lfz = lfz[None, :]  # Add timestep dimension

        # Get water level (wl) and bed level (bl) of each 2D cell for all timesteps
        wl = lfz[:, self.wli]
        bl = lfz[:, self.bli]

        # Determine integral limits z1 and z2 for each 2D cell using wl, bl and the limits
        if datum == "sigma":
            z1 = limits[0] * (wl - bl) + bl
            z2 = limits[1] * (wl - bl) + bl
        elif datum == "height":
            z1 = limits[0] + bl
            z2 = limits[1] + bl
        elif datum == "depth":
            z1 = wl - limits[1]
            z2 = wl - limits[0]
        elif datum == "elevation":
            z1 = np.full_like(wl, limits[0])
            z2 = np.full_like(wl, limits[1])
        else:
            return None

        # This repetition is probably not required!
        if dask:
            # Create integral limits, filtering z2 and z1 above and below water level or bed level
            z1 = da.minimum(da.maximum(z1, bl), wl)
            z2 = da.minimum(da.maximum(z2, bl), wl)

            # Squeeze out middle value of each vertical layer face
            lfz = da.maximum(lfz, z1[:, self.idx4])
            lfz = da.minimum(lfz, z2[:, self.idx4])

            # Get upper z layer face and lower z layer face for each 3D cell
            mask_bli = np.ones(lfz.shape[1], dtype=bool)
            mask_bli[self.bli] = False
            ul = lfz[:, mask_bli]

            mask_wli = np.ones(lfz.shape[1], dtype=bool)
            mask_wli[self.wli] = False
            ll = lfz[:, mask_wli]
        else:
            # Create integral limits, filtering z2 and z1 above and below water level or bed level
            z1 = np.minimum(np.maximum(z1, bl), wl)
            z2 = np.minimum(np.maximum(z2, bl), wl)

            # Squeeze out middle value of each vertical layer face
            lfz = np.maximum(lfz, z1[:, self.idx4])
            lfz = np.minimum(lfz, z2[:, self.idx4])

            # Get upper z layer face and lower z layer face for each 3D cell
            ul = np.delete(lfz, self.bli)
            ll = np.delete(lfz, self.wli)

        dz = ul - ll

        # Clean up integral limit (z2 - z1) to avoid division by zero
        z2_z1 = z2 - z1
        mask = z2_z1 == 0

        # Return integral limit of each 2D cell and dz of each 3D cell contained within integral limit

        if dask is False:
            return np.ma.masked_array(
                data=np.squeeze(z2_z1), mask=mask, fill_value=np.nan
            ), np.squeeze(dz)
        else:
            return da.ma.masked_array(data=z2_z1, mask=mask, fill_value=np.nan), dz

    @Expression.decorator
    def get_sheet_cell(
        self,
        variable: str,
        ii: Union[int, str, pd.Timestamp],
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        mask_dry: bool = True,
        z_data: tuple = None,
    ):
        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get the raw data
        data = self.get_raw_data(variable, ii)
        if mask_dry:
            mask = self.get_mask_vector(ii)
        else:
            mask = np.zeros((self.nc2,), dtype=bool)

        # Check if data is 3D
        if data.size == self.nc3:
            # Get integral data for depth averaging
            if z_data is None:
                z_data = self.get_integral_data(ii, datum, limits)
            z2_z1, dz = z_data

            # Update stat vector with invalid limits
            mask = mask | z2_z1.mask

            if agg == "mean":
                # Integrate the data w.r.t z
                data = np.bincount(self.idx2, data * dz) * (1 / z2_z1)
            elif agg == "min":
                data = self._sparse_array_reduction(
                    data * (dz > 0).astype(int), np.minimum
                )
            elif agg == "max":
                data = self._sparse_array_reduction(
                    data * (dz > 0).astype(int), np.maximum
                )
            else:
                assert False, "agg should be equal to either `mean`, `max` or `min`"

        # Reshape stat vector for 2D sheets i.e bed mass
        if data.shape != mask.shape:
            n = data.shape[1]
            mask = np.tile(mask, (n, 1))
            mask = np.transpose(mask)

        # Return the data
        return np.ma.MaskedArray(data=data, mask=mask, fill_value=np.nan)

    @Expression.decorator
    def get_sheet_cell_dask(
        self,
        variable: str,
        indices: Union[int, np.ndarray, list],
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        mask_dry: bool = True,
        z_data: tuple = None,
    ):
        # Get the raw data
        data = self.get_raw_data(variable, indices, dask=True)

        if mask_dry:
            mask = self.get_mask_vector(indices, dask=True)
        else:
            mask = np.zeros(data.shape, dtype=np.bool)

        # Handle both single and multiple timesteps
        if data.ndim == 1:
            data = data[None, :]  # Add timestep dimension
        if mask.ndim == 1:
            mask = mask[None, :]  # Add timestep dimension

        # Check if data is 3D
        if "NumCells3D" in self.ds[variable].dims:
            # Get integral data for depth averaging
            if z_data is None:
                z_data = self.get_integral_data(indices, datum, limits, dask=True)
            z2_z1, dz = z_data
            z_mask = da.ma.getmaskarray(z2_z1)

            # Update stat vector with invalid limits
            mask = mask | z_mask

            if agg == "mean":
                # Integrate the data w.r.t z
                data = _weighted_sum(data, self.idx2, dz, z2_z1)
            else:
                raise ValueError(
                    "Only `agg='mean'` has been implemented for dask computations"
                )

        # Reshape stat vector for 2D sheets i.e bed mass
        if data.shape != mask.shape:
            raise ValueError(
                "Only standard 2D/3D variables are supported for dask calculations"
            )

        # Return the data
        return da.ma.masked_array(data=data, mask=mask, fill_value=np.nan)

    @Expression.decorator
    def get_sheet_node(
        self,
        variable: str,
        ii: int,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        mask_dry: bool = True,
        z_data: tuple = None,
    ):

        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get the raw data
        data = self.get_raw_data(variable, ii)
        if mask_dry:
            mask = self.get_mask_vector(ii)
        else:
            mask = np.zeros((self.nc2,), dtype=bool)

        # Check if data is 3D
        if "NumCells3D" in self.ds[variable].dims:
            # Get integral data for depth averaging
            if z_data is None:
                z_data = self.get_integral_data(ii, datum, limits)
            z2_z1, dz = z_data

            # Update stat vector for invalid limits (z2 - z1)
            mask = mask | z2_z1.mask

            if agg == "mean":
                # Integrate the data w.r.t z
                data = np.bincount(self.idx2, data * dz) * (1 / z2_z1)
            elif agg == "min":
                data = self._sparse_array_reduction(data, np.minimum)
            elif agg == "max":
                data = self._sparse_array_reduction(data, np.maximum)
            else:
                assert False, "agg should be equal to either `mean`, `max` or `min`"

        # Create copy of 2D node recovery weights
        weights = np.copy(self.weights)

        # Set weightings of invalid cells to zero
        weights[mask, :] = 0

        # Rescale weightings to account for discounted cells
        weights_sum = np.bincount(self.cell_node.flatten(), weights.flatten())
        mask = weights_sum == 0
        weights_sum[mask] = -999
        weights = weights / weights_sum[self.cell_node]

        if data.ndim == 1:
            # For each cell, calculate the weighted nodal data values
            tmp = np.tile(data, (4, 1)).transpose() * weights

            # Sum weighted data values for each node to get final vertex data
            data_node = np.bincount(self.cell_node.flatten(), tmp.flatten())
        else:
            data_node = np.empty((self.nv2, data.shape[1]), dtype=np.float64)
            for jj in range(data.shape[1]):
                # For each cell, calculate the weighted nodal data values
                tmp = np.tile(data[:, jj], (4, 1)).transpose() * weights

                # Sum weighted data values for each node to get final vertex data
                data_node[:, jj] = np.bincount(self.cell_node.flatten(), tmp.flatten())

            mask = np.tile(mask, (data.shape[1], 1))
            mask = np.transpose(mask)

        # Return the data
        return np.ma.MaskedArray(data=data_node, mask=mask, fill_value=np.nan)

    def get_sheet_grid(
        self,
        variable: str,
        ii: int,
        xg: np.ndarray,
        yg: np.ndarray,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        z_data: tuple = None,
        grid_index: np.ndarray = None,
    ):

        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get grid index
        if grid_index is None:
            grid_index = self.get_grid_index(xg, yg)
        mask = np.equal(grid_index, -999)
        valid = np.equal(mask, False)

        # Index mesh data using grid index
        grid_data = np.ma.MaskedArray(
            data=np.zeros(grid_index.shape) * np.nan, fill_value=np.nan, mask=mask
        )
        grid_data[valid] = self.get_sheet_cell(
            variable, ii, datum, limits, agg, z_data
        )[grid_index[valid]]

        # Return gridded data
        return grid_data

    @Expression.decorator
    def get_curtain_cell(
        self,
        variable: str,
        ii: int,
        polyline: np.ndarray,
        x_data: tuple = None,
        index: tuple = None,
    ):

        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get prerequisite data
        mask = self.get_mask_vector(ii)
        data = self.get_raw_data(variable, ii)

        # Check if data is 3D
        assert data.size == self.nc3, "Data is not 3D"

        # Get edge intersection data
        if x_data is None:
            x_data = self.get_intersection_data(polyline)
        _, _, idx = x_data

        # Get curtain index data
        if index is None:
            index = self.get_curtain_cell_index(polyline, x_data)
        line_index, cell_index = index

        # Return curtain data
        return np.ma.MaskedArray(
            data=data[cell_index], mask=mask[idx[line_index]], fill_value=np.nan
        )

    @unsupported_decorator
    def get_curtain_edge(
        self, variable: str, ii: int, polyline: np.ndarray, x_data=None, index=None
    ):
        pass

    def get_curtain_grid(
        self,
        variable: str,
        ii: int,
        polyline: np.ndarray,
        xg,
        yg,
        x_data=None,
        index=None,
        grid_index=None,
    ):

        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get grid index
        if grid_index is None:
            geo = self.get_curtain_cell_geo(ii, polyline, x_data)
            grid_index = Mesh(*geo).get_grid_index(xg, yg)
        mask = np.equal(grid_index, -999)
        valid = np.equal(mask, False)

        # Index mesh data using grid index
        grid_data = np.ma.MaskedArray(
            data=np.zeros(grid_index.shape) * np.nan, fill_value=np.nan, mask=mask
        )
        grid_data[valid] = self.get_curtain_cell(variable, ii, polyline, x_data, index)[
            grid_index[valid]
        ]

        # Return gridded data
        return grid_data

    @Expression.decorator
    def get_profile_cell(self, variable: str, ii: int, point: tuple, index=None):

        # Convert timestep into integer
        ii = self._timestep_index(ii)

        # Get the raw data
        data = self.get_raw_data(variable, ii)

        # Get 2D cell index
        if index is None:
            index = self.get_cell_index(point[0], point[1])
            if index < 0:
                print("Warning: point coordinate not inside model domain")

        # Allow profile cell to work for 2D data as well
        if "NumCells3D" in self.ds[variable].dims:
            # Index the data
            data = data[self.idx2 == index]

            # Repeat to get discrete elements
            insert = np.arange(0, data.size)
            data = np.insert(data, insert, data[insert])

        elif "NumCells2D" in self.ds[variable].dims:
            data = data[np.arange(0, self.nc2) == index]
        else:
            assert False, "Variable must include either NumCells3D or NumCells2D"
        return data

    def _get_profile_geometry(self, cell_index, time=None):
        dsx = self._subset_dataset(time)
        xtr = FvExtractor(dsx)

        t = dsx["Time"].values

        cell_index_lfz = xtr.idx4 == cell_index
        nz = np.squeeze(xtr.nz[cell_index])
        nt = t.shape[0]

        z = np.zeros((nz + 1, nt), dtype=np.float32)

        for ii in range(nt):
            z[:, ii] = xtr.get_z_layer_faces(ii)[cell_index_lfz]

        # Padded time-vector for smooth meshing
        tv = pd.date_range(t[0], t[-1], periods=t.shape[0] + 1)
        tc = np.tile(tv, (z.shape[0], 1))
        zc = np.hstack((z[:, [0]], 0.5 * (z[:, :-1] + z[:, 1:]), z[:, [-1]]))

        node_x, node_y = tc.ravel("F"), zc.ravel("F")

        nz, nt = tc.shape
        ii = np.arange(nz - 1)
        jj = np.arange(nt - 1)

        jj, ii = np.meshgrid(jj, ii)
        tl = np.ravel(ii + nz * jj, "F")
        tr = np.ravel(ii + nz * (jj + 1), "F")

        cell_node = np.vstack((tl, tl + 1, tr + 1, tr))
        cell_node = cell_node.transpose()

        return Mesh(node_x, node_y, cell_node)

    def __prep_file_handle__(self, lazy_load: bool, warmup: pd.Timedelta):
        # Assert the file exists
        if isinstance(self.file, str):
            self.file = Path(self.file)
            assert Path(
                self.file
            ).exists(), f"No such file or directory: \n{self.file.as_posix()}"
        elif isinstance(self.file, Path):
            assert (
                self.file.exists()
            ), f"No such file or directory: \n{self.file.as_posix()}"

        # ToDO: Refactor this if statement
        single_file = any([isinstance(self.file, x) for x in [str, Path]])
        multi_file = any([isinstance(self.file, x) for x in [list, GeneratorType]])

        # Direct xarray object passthrough
        if isinstance(self.file, xr.Dataset):
            self.ds = self.file
            self.__prep_time_vector__()

        # Normal file open
        elif (lazy_load == False) & single_file:
            self.ds = xr.open_dataset(self.file, decode_times=False)
            self.__prep_time_vector__()
            self.ds = _discard_warmup(self.ds, warmup)

        # Open as an out of memory dataset (single file)
        elif (lazy_load == True) & single_file:
            self.ds = xr.open_mfdataset([self.file], decode_times=False)
            self.__prep_time_vector__()

        # Require individual file loop loading
        elif multi_file:
            self.ds = _open_mf_tfv_dataset(self.file, warmup=warmup)
            self.time_vector = pd.to_datetime(self.ds["Time"].values)
            self.nt = self.time_vector.size

        else:
            msg = [
                "Unclear file(s) type",
                "Please supply either a str/path, a list of files, or an xr.Dataset",
                "",
            ]
            assert False, "\n".join(msg)

    def __prep_time_vector__(self):
        # Define fv epoch relative to python epoch
        fv_epoch = pd.Timestamp(1990, 1, 1)

        # Prepare time vector relative to python epoch
        # This if statement is a future check for when xarray starts decoding FV results
        if isinstance(self.ds["ResTime"].values[0], np.datetime64):
            self.time_vector = pd.to_datetime(self.ds["ResTime"].values)
        else:
            self.time_vector = (
                pd.to_timedelta(self.ds["ResTime"].values, unit="h") + fv_epoch
            )
        self.nt = self.time_vector.size
        self.ds["Time"] = pd.to_datetime(self.time_vector)

    def __prep_2d_geometry__(self):
        # Get basic data from file
        node_x = self.ds["node_X"].values
        node_y = self.ds["node_Y"].values
        cell_node = self.ds["cell_node"].values - 1

        # Identify null node indices
        cell_node[cell_node == -1] = -999

        # Pass commonly used attributes, and drop unrequired geo from dataset
        self.cell_x = self.ds["cell_X"].values
        self.cell_y = self.ds["cell_Y"].values
        self.cell_z = self.ds["cell_Zb"].values
        self.cell_a = self.ds["cell_A"].values

        # Check if spherical
        if "spherical" in self.ds.attrs:
            if self.ds.attrs["spherical"] == "true":
                self.is_spherical = True
            else:
                self.is_spherical = False

        # Initialize 2d geometry as Mesh
        Mesh.__init__(self, node_x, node_y, cell_node)

    def __prep_3d_geometry__(self):
        # Get basic data from file
        self.nz = self.ds["NL"].values

        # Prepare variables to define 3D mesh
        index = np.arange(self.nz.size)
        self.idx2 = np.repeat(index, self.nz)
        self.idx3 = np.cumsum(self.nz) - self.nz
        self.idx4 = np.repeat(index, self.nz + 1)
        self.wli = self.idx3 + index
        self.bli = self.wli + self.nz
        self.nc3 = self.idx2.size

    def _timestep_index(self, ii):
        # Function to handle timestep argument
        # Convert incoming arg into a Pd.Timestamp
        if isinstance(ii, str):
            time = pd.Timestamp(ii)
        elif isinstance(ii, (int, np.int64, np.int32, list, np.ndarray, tuple)):
            return ii  # Early return because this is likely integers!
        else:
            time = ii

        ii = np.argmin(np.abs(self.time_vector - time))

        return ii

    def _subset_dataset(self, time):
        """Helper function to subset datasets"""
        # Use sliced xarray dataset
        dsx = self.ds
        int_types = [int, np.int32, np.int64, np.int16]
        date_types = [pd.Timestamp, np.datetime64, str]
        try:
            if any([isinstance(time, x) for x in int_types]):
                dsx = dsx.isel(Time=[time])
            elif isinstance(time, slice):
                if isinstance(time.stop, int):
                    dsx = dsx.isel(Time=time)
                else:
                    dsx = dsx.sel(Time=time)
            elif any([isinstance(time, x) for x in date_types]):
                dsx = dsx.sel(Time=[time])
            elif isinstance(time, list):
                dsx = dsx.isel(Time=time)
            elif time is None:
                dsx
            else:
                dsx = dsx.sel(Time=time)
        except AttributeError:
            print(time_slice_err)

        return dsx

    def _sparse_array_reduction(self, data, function):
        aux = sparse.csr_matrix(
            (data, self.idx2, np.arange(data.size + 1)), (data.size, self.nc2)
        ).tocsc()

        cut = aux.indptr.searchsorted(data.size)
        reduced_array = np.empty(self.nc2)
        reduced_array.ravel()[:cut] = function.reduceat(aux.data, aux.indptr[:cut])

        return reduced_array

    def get_curtain_cell_index(self, polyline: np.ndarray, x_data: tuple = None):
        """
        Query to extract 3D cell indices of 2D vertical slice ('curtain') for a given polyline.

        Parameters
        ----------
        polyline : 2D np.ndarray
            Polyline as [x, y] used to slice 3D data.

        Other Parameters
        ----------------
        x_data : tuple
            Model edge intersection(x) data returned by self.get_intersections.

        Returns
        -------
        index : tuple
            Index data defined by line index & cell index (line_index, cell_index). The line index provides the 1D
            polyline segment indices for each cell in the 2D vertical slice. The cell index provides the 3D model cell
            indices for each cell in the 2D vertical slice.
        """

        # Get cell x_data
        if x_data is None:
            x_data = self.get_intersection_data(polyline)
        _, _, idx = x_data

        # Determine which cells in the polyline are valid
        is_valid = idx != -999

        # Prepare indexing variables for curtain
        idx = idx[is_valid]  # 2D cell index for each column in curtain
        nz = self.nz[idx]  # Number of 3D cells for each column in curtain
        n = int(np.sum(nz))  # Total number of 3D cells in curtain
        idx3 = np.cumsum(nz) - nz  # Index of top 3D cell for each column in curtain

        # Get 1D polyline index of the curtain cells (maps curtain cell to polyline segments)
        line_index = np.repeat(np.where(is_valid)[0], nz)

        # Get 3D cell index of the curtain cells (maps curtain cell to 3D model cell)
        cell_index = np.repeat(self.idx3[idx], nz) + (
            np.arange(n) - np.repeat(idx3, nz)
        )

        return line_index, cell_index

    def get_curtain_cell_geo(
        self,
        ii: int,
        polyline: np.ndarray,
        x_data: tuple = None,
        index: tuple = None,
        return_unit_vector=False,
        crs=None,
    ):
        """
        Query to extract geometry data for a 2D vertical slice ('curtain') along a given polyline.

        Parameters
        ----------
        ii : integer
            Time index at which to extract the data.
        polyline : 2D np.ndarray
            Polyline as [x, y] used to slice 3D data.

        Other Parameters
        ----------------
        x_data : tuple
            Model edge intersection(x) data returned by self.get_intersections.
        index : tuple
            Curtain index data returned by self.get_curtain_cell_index.
        crs : int
            EPSG Code for accurate transformations from spherical coordinates. Not necessary if model is non-spherical

        Returns
        -------
        geo : tuple
            A tuple containing the geometry of the 2D vertical slice as (node_x, node_y, cell_node).

        """

        # Get layer face z
        lfz = self.get_z_layer_faces(ii)

        # Get edge intersection(x) data
        if x_data is None:
            x_data = self.get_intersection_data(polyline)
        x, y, idx = x_data
        nic2 = len(idx)
        nl = self.nz
        coords = np.stack((x, y)).T

        # Get curtain index
        if index is None:
            index = self.get_curtain_cell_index(polyline, x_data)
        line_index, cell_index = index

        # Convert x & y into (m) if spherical
        if self.is_spherical:
            if crs is not None:
                try:
                    from pyproj import Transformer

                    transformer = Transformer.from_crs(4326, crs, always_xy=True)
                    x, y = transformer.transform(x, y)
                except ValueError:
                    print(
                        "To use the CRS input for accurate transformations, you must have `pyproj` installed"
                    )
            else:
                r_e = 6.378137 * 10**6
                cf = np.pi / 180
                x = (r_e * np.cos(y * cf)) * (x * cf)
                y = r_e * (y * cf)

        # Prepare curtain mesh (x, y)
        dx = np.diff(x)
        dy = np.diff(y)
        ds = np.hypot(dx, dy)
        s = np.cumsum(ds)
        s = np.hstack((0, s))

        s1 = s[line_index]
        s2 = s[line_index + 1]
        z1 = np.delete(lfz, self.wli)[cell_index]
        z2 = np.delete(lfz, self.bli)[cell_index]

        # Get nodes and node indices that define each cell
        n = cell_index.size
        node_x = np.vstack((s1, s2, s2, s1)).ravel("F")
        node_y = np.vstack((z1, z1, z2, z2)).ravel("F")
        cell_node = np.arange(n * 4, dtype=np.int32).reshape(n, 4)

        if return_unit_vector == True:
            # Get unit vector
            norm = np.array((-np.diff(coords[:, 1]), np.diff(coords[:, 0]))).T
            unorm_tmp = np.zeros((norm.shape[0], 2))
            unorm_tmp[:, 0] = norm[:, 0] / np.hypot(norm[:, 0], norm[:, 1])
            unorm_tmp[:, 1] = norm[:, 1] / np.hypot(norm[:, 0], norm[:, 1])
            unorm = []
            for aa in range(nic2):
                i = idx[aa]
                ext = np.broadcast_to(unorm_tmp[aa, :], [nl[i], 2])
                unorm.extend([ext])
            unorm = np.vstack(unorm).T

            # Get tangent vector
            tang = np.array((np.diff(coords[:, 0]), np.diff(coords[:, 1]))).T
            utang_tmp = np.zeros((norm.shape[0], 2))
            utang_tmp[:, 0] = tang[:, 0] / np.hypot(tang[:, 0], tang[:, 1])
            utang_tmp[:, 1] = tang[:, 1] / np.hypot(tang[:, 0], tang[:, 1])
            utang = []
            for aa in range(nic2):
                i = idx[aa]
                ext = np.broadcast_to(utang_tmp[aa, :], [nl[i], 2])
                utang.extend([ext])
            utang = np.vstack(utang).T

            return node_x, node_y, cell_node, unorm, utang
        else:
            return node_x, node_y, cell_node

    def get_profile_cell_geo(self, ii: int, point: tuple, index=None):
        # Get layer face z
        lfz = self.get_z_layer_faces(ii)

        # Get 2D cell index
        if index is None:
            index = self.get_cell_index(point[0], point[1])

        # Index faces of cell
        lfz = lfz[self.idx4 == index]

        # Repeat to represent discrete elements
        insert = np.arange(1, lfz.size - 1)
        lfz = np.insert(lfz, insert, lfz[insert])

        return lfz

    # ToDO: Think of a way to better ingrain this feature in xarray, accounting for
    # variable length layerface_z, which makes it difficult
    def write_time_series_file(
        self, out_file: Union[Path, str], locations: dict, variables: list = None
    ):
        """
        Query that writes 2D & 3D point time series data from a TUFLOW FV netCDF4 results file.

        Parameters
        ----------
        out_file : string
            File path to write time series file.
        locations : dictionary
            Extraction points as dict(SITE_1=(x, y), SITE_2=(x, y)).
        variables : list
            List of variables to extract. Default is all variables
        """

        if isinstance(out_file, str):
            out_file = Path(out_file)

        # Check if out path exists
        # ToDO: Improve messaging
        if out_file.exists():
            user_input = input(out_file.name + " exists - enter Y/n to proceed:\n")
            while True:
                if user_input.upper() == "Y":
                    os.remove(out_file)
                    break
                elif user_input.upper() == "N":
                    print("Finished - no files have been modified")
                    return
                else:
                    user_input = input("Invalid user input please enter Y/N:\n")

        # Get cell indicies for each location
        idx = {}
        for name, point in locations.items():
            ind_2d = self.get_cell_index(point[0], point[1])[0]
            ind_3d = np.where(self.idx2 == ind_2d)[0]
            ind_lfz = np.where(self.idx4 == ind_2d)[0]
            idx[name] = (ind_2d, ind_3d, ind_lfz, point)
            if idx[name] == -999:
                print("WARNING: point '{}' is outside of model domain".format(name))

        dsg = self.ds[["ResTime"]]
        dsg = dsg.drop(["Time"])
        dsg.attrs["Origin"] = (
            "Profile extracted from TUFLOWFV cell-centered output using `tfv` python tools"
        )
        dsg.attrs["Type"] = "Profile cell from TUFLOWFV output"
        dsg.to_netcdf(out_file)

        for pt, (i2, i3, i4, ptc) in idx.items():
            dsx = self.ds.sel(NumCells2D=i2, NumCells3D=i3, NumLayerFaces3D=i4)
            dsx = dsx.drop(
                [
                    "Time",
                    "ResTime",
                    "cell_Nvert",
                    "NL",
                    "cell_node",
                    "cell_A",
                    "node_X",
                    "node_Y",
                    "node_Zb",
                    "idx2",
                    "idx3",
                    "node_NVC2",
                    "node_cell2d_idx",
                    "node_cell2d_weights",
                ],
                errors="ignore",
            )
            dsx = dsx.rename(
                dict(
                    cell_X="X",
                    cell_Y="Y",
                    cell_Zb="Z",
                    NumCells3D="NumLayers",
                    NumLayerFaces3D="NumLayerFaces",
                )
            )

            for var in dsx.data_vars.keys():
                if len(dsx[var].dims) == 1:
                    dsx[var] = dsx[var].expand_dims(dim="N1", axis=1)

            # Optional variable check
            if variables:
                dsx = dsx[["X", "Y", "Z", "stat", "layerface_Z"] + variables]

            # Add N1 dim to match TUFLOW-FV Output
            dsx["X"] = dsx["X"].expand_dims(dim="N1")
            dsx["Y"] = dsx["Y"].expand_dims(dim="N1")
            dsx["Z"] = dsx["Z"].expand_dims(dim="N1")

            if isinstance(self.file, str):
                dsx.attrs["Source file"] = self.file
            elif isinstance(self.file, Path):
                dsx.attrs["Source file"] = self.file.as_posix()

            dsx.attrs["Created"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dsx.attrs["Loc. name"] = pt
            dsx.attrs["Loc. coords"] = ptc
            dsx.attrs["Origin"] = (
                "Profile extracted from TUFLOWFV cell-centered output using `tfv` python tools"
            )
            dsx.attrs["Type"] = "Profile cell from TUFLOWFV output"

            wj = dsx.to_netcdf(out_file, mode="a", group=pt, compute=False)
            with ProgressBar(minimum=5):
                print(f"Writing location: {pt}")
                wj.compute()
        print("Finished")

    def write_data_to_ascii(
        self,
        out_file: Union[Path, str],
        data: np.ndarray,
        resolution: float,
        precision: int = 2,
        bbox: list = None,
        grid_index: np.ndarray = None,
    ):
        """
        Query data at cell centroids to gridded raster ASCII file.

        Parameters
        ----------
        out_file : string
            File path of .asc file to write data to.
        data : 1D np.ndarray
            Cell centred TUFLOW FV data as numpy array.
        resolution : float
            Grid resolution at which to output data.
        precision : int
            Output precision as number of decimal places.
        bbox : list, optional
            The bounding box to trim the data with as [left, bottom, right, top].
        grid_index : 2D np.ndarray, optional
            Mesh cell index for each grid point returned by self.get_grid_index

        """

        # Calculate grid parameters
        if bbox is None:
            x_min, x_max = self.node_x.min(), self.node_x.max()
            y_min, y_max = self.node_y.min(), self.node_y.max()
        else:
            x_min, x_max = bbox[0], bbox[2]
            y_min, y_max = bbox[1], bbox[3]

        dx = x_max - x_min
        dy = y_max - y_min

        nc = int(np.ceil(dx / resolution))
        nr = int(np.ceil(dy / resolution))

        xg = np.linspace(x_min, x_max, nc)
        yg = np.linspace(y_min, y_max, nr)

        # Get grid index & flip (x increasing, y decreasing)
        if grid_index is None:
            grid_index = self.get_grid_index(xg, yg)
        grid_index = np.flipud(grid_index)
        valid = grid_index != -999

        # Index mesh data using grid index
        grid_data = np.ones(grid_index.shape) * np.nan
        grid_data[valid] = data[grid_index[valid]]
        grid_data[np.isnan(grid_data)] = -999

        # Specify header
        header = [
            "ncols {:d}".format(nc),
            "nrows {:d}".format(nr),
            "xllcorner {:.7f}".format(x_min - resolution / 2),
            "yllcorner {:.7f}".format(y_min - resolution / 2),
            "cellsize {:.7f}".format(resolution),
            "NODATA_value {:d}".format(-999),
        ]

        # Write ASCII file
        with open(out_file, "w") as f:
            f.write("\n".join(header) + "\n")
            np.savetxt(f, grid_data, "%.{}f".format(precision), delimiter=" ")

    # Inherit doc strings (needs to be done a better way with decorator as per matplotlib)
    get_raw_data.__doc__ = Extractor.get_raw_data.__doc__
    get_mask_vector.__doc__ = Extractor.get_mask_vector.__doc__
    get_z_layer_faces.__doc__ = Extractor.get_z_layer_faces.__doc__
    get_integral_data.__doc__ = Extractor.get_integral_data.__doc__

    get_sheet_cell.__doc__ = getdoc(Extractor.get_sheet_cell)
    get_sheet_node.__doc__ = Extractor.get_sheet_node.__doc__
    get_sheet_grid.__doc__ = Extractor.get_sheet_grid.__doc__

    get_curtain_cell.__doc__ = Extractor.get_curtain_cell.__doc__
    get_curtain_edge.__doc__ = Extractor.get_curtain_edge.__doc__
    get_curtain_grid.__doc__ = Extractor.get_curtain_grid.__doc__
    get_profile_cell.__doc__ = Extractor.get_profile_cell.__doc__


def _open_mf_tfv_dataset(
    files: Union[list, GeneratorType], warmup: pd.Timedelta = None
):
    """ """
    fv_epoch = pd.Timestamp(1990, 1, 1)

    # Always sort file list
    if isinstance(files, GeneratorType):
        files = list(files)
    files.sort()

    # Loop through each file, chop warmup
    ds_set = []
    for f in files:
        ds = xr.open_mfdataset([f], decode_cf=False, chunks={"Time": 10})

        tvec = pd.to_timedelta(ds["ResTime"].values, unit="h") + fv_epoch
        ds["Time"] = tvec

        # Take out warmup period
        if warmup:
            ds = _discard_warmup(ds, warmup)

        ds_set.append(ds)

    ds = xr.concat(ds_set, dim="Time", data_vars="minimal")

    # Drop duplicates
    _, index = np.unique(ds["Time"], return_index=True)

    if len(index) < len(ds["Time"].values):
        print("Warning: Dropping duplicate times")
    ds = ds.isel(Time=index)
    ds = ds.sortby("Time")

    return ds


def _discard_warmup(ds: xr.Dataset, warmup: pd.Timedelta):
    ts = ds["Time"][0] + warmup
    return ds.sel(Time=slice(ts, None))


def _strip_dataset(ds):
    dst = xr.Dataset()

    keep_vars = ("ResTime", "layerface_Z", "stat")
    for dv in ds.data_vars.keys():
        if "Time" in ds[dv].dims:
            if dv in keep_vars:
                dst = dst.assign({dv: ds[dv]})
        else:
            dst = dst.assign({dv: ds[dv]})

    dst["stat"][:] = -1
    return dst


def _weighted_sum(data, idx2, dz, z2_z1):
    """Run weighted sum, an alternative to running bincount for depth-averaging over dask arrays.

    Args:
        data (da.Array): Variable data (nt x nc3)
        idx2 (da.Array): cell idx2 array
        dz (da.Array): cell thickness array
        z2_z1 (da.Array): integral limits array
    """

    def bincount_weighted(weights, x):
        return np.bincount(x, weights, minlength=m + 1)

    # Ensure all inputs are Dask arrays
    if not isinstance(idx2, da.Array):
        idx2 = da.from_array(idx2, chunks=data.chunks[1])
    if not isinstance(dz, da.Array):
        dz = da.from_array(dz, chunks=data.chunks)
    if not isinstance(z2_z1, da.Array):
        z2_z1 = da.from_array(z2_z1, chunks=z2_z1.shape)

    # Calculate weights
    weights = data * dz

    # Compute the maximum index
    m = idx2.max().compute()

    # Use apply_along_axis to perform bincount on each row
    result = da.apply_along_axis(
        bincount_weighted, 1, weights, idx2, shape=(m + 1,), dtype=weights.dtype
    )

    # Multiply by 1 / z2_z1
    result = result * (1 / z2_z1)

    return result
