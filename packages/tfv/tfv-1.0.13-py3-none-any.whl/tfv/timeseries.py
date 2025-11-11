"""A module defining all point time series extractor classes"""

import xarray as xr
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from abc import ABC, abstractmethod
import datetime as dt
from tfv.miscellaneous import Expression
from tfv.geometry import Mesh
from typing import Union

time_slice_err = [
    "`time_limits` optional argument must be a slice function",
    "Examples:",
    "   slice(0, 10) for the first 10 timesteps",
    "   slice('2020-01-01', '2020-02-01') to slice between dates",
    "For more help, please refer to Pandas `.loc` or Xarray `.isel` or `.sel` methods",
]


class TimeSeries(ABC):
    """A base class which defines the API for all point time series based model result data extraction"""

    def __init__(self, file):
        """Initializes TimeSeries extractor object with model result file"""

        # Store file path string as attribute
        self.file = file
        self.sites = None

        # Prepare static TimeSeries attributes
        self.__prepare_file_handle__()
        self.__prepare_time_vector__()
        self.__prepare_locations__()

    @abstractmethod
    def get_raw_data(self, variable, site):
        """
        Query to extract raw time series data at a given location.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        site : string
            Location at which to extract the time series data.

        Returns
        -------
        data : np.ndarray
            The raw time series data as 1D or 2D numpy array
        """

    @abstractmethod
    def get_mask_vector(self, site):
        """
        Query to extract an array that defines invalid model data.

        Parameters
        ----------
        site : string
            Location at which to extract the time series data.

        Returns
        -------
        mask : np.ndarray
            Logical index, True if model cell at time step is invalid (i.e dry).
        """

    @abstractmethod
    def get_z_layer_faces(self, site):
        """
        Query to extract an array that defines the vertical layer faces of a 3D model at a given location.

        Parameters
        ---------
        site : string
            Location at which to extract the time series data.

        Returns
        -------
        lfz : np.ndarray
            Vertical layer faces. If model is 2D returns None.
        """

    @abstractmethod
    def get_integral_data(self, site, datum, limits):
        """
        Query to extract data for vertical integration at a given location. Principle data is the
        integral limit (z2 - z1) and dz for each 3D model cell at the location.

        Parameters
        ----------
        site : string
            Location at which to extract the time series data.
        datum : string
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits relative to vertical datum.

        Returns
        -------
        (z2_z1, dz) : tuple
            The elevation limits (z2 - z1) & dz for each 3D cell at a given location
        """

    @abstractmethod
    def get_data(self, variable, site, datum="sigma", limits=(0, 1)):
        """
        Query to extract time series data at a given location. If model data is 3D then it is
        depth-averaged according to the depth-averaging vertical datum and vertical limits.

        Parameters
        ----------
        variable : string
            Name of time varying data set to be extracted.
        site : string
            Location at which to extract the time series data.
        datum : {'sigma', 'depth', 'height', 'elevation'}
            Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
        limits : tuple
            Vertical depth-averaging limits (z1, z2) relative to vertical datum.
        agg : {'mean', 'min', 'max'}
            Vertical aggregration function, default = 'mean'
            'mean' will apply a weighted averaging routine (i.e., a depth average across the specified datum/limits)

        Returns
        -------
        data : np.ndarray
            1D Time series data at a given location.
        """

    @abstractmethod
    def __prepare_file_handle__(self):
        """Command which prepares the file handle for the extractor class"""

    @abstractmethod
    def __prepare_time_vector__(self):
        """Command which prepares the result time stamp vector relative to python epoch"""

    @abstractmethod
    def __prepare_locations__(self):
        """Command which prepares locations found in result time series file"""


class FvTimeSeries(TimeSeries):

    def __init__(self, file):
        super(FvTimeSeries, self).__init__(file)

    @property
    def variables(self):
        grp = list(self.locations.keys())[0]
        return [x for x in self.ds[grp].data_vars.keys() if x not in ["X", "Y", "Z"]]

    @property
    def vector_variables(self):
        vecvar_map = {}
        for var in self.variables:
            if var[-2:] == "_x":
                basevar = var[:-2]
                if basevar + "_y" in self.variables:
                    vecvar_map[basevar] = (basevar + "_x", basevar + "_y")
        return vecvar_map

    @Expression.decorator
    def get_raw_data(self, variable, site, time=None):
        ds = self._subset_dataset(site, time)
        return ds[variable].values.transpose()

    def get_mask_vector(self, site, time=None):
        ds = self._subset_dataset(site, time)
        if "stat" in ds.data_vars:
            return self.get_raw_data("stat", site, time=time) == 0
        else:
            return np.zeros((ds.sizes["Time"]), dtype=bool)

    def get_z_layer_faces(self, site, time=None):
        return self.get_raw_data("layerface_Z", site, time=time)

    def get_integral_data(self, site, datum, limits, time=None):
        # Get z layer faces
        lfz = self.get_z_layer_faces(site, time=time)

        # Get water level (wl) and bed level (bl) for each time step
        wli, bli = 0, lfz.shape[0] - 1
        wl, bl = lfz[wli, :], lfz[bli, :]

        # Determine integral limits z1 and z2 for each time step using wl, bl and the limits
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
            z1 = limits[0]
            z2 = limits[1]
        else:
            return None

        # Create integral limits, filtering z2 and z1 above and below water level or bed level
        z1 = np.minimum(np.maximum(z1, bl), wl)
        z2 = np.minimum(np.maximum(z2, bl), wl)

        # Squeeze out middle value of each vertical layer face
        lfz = np.maximum(lfz, np.tile(z1, (lfz.shape[0], 1)))
        lfz = np.minimum(lfz, np.tile(z2, (lfz.shape[0], 1)))

        # Get upper z layer face and lower z layer face for each 3D cell
        ul = np.delete(lfz, bli, axis=0)
        ll = np.delete(lfz, wli, axis=0)
        dz = ul - ll

        # Clean up integral limit to avoid division by zero
        z2_z1 = z2 - z1
        mask = z2_z1 == 0

        # Return integral limit of each 2D cell and dz of each 3D cell contained within integral limit
        return np.ma.masked_array(data=z2_z1, mask=mask, fill_value=np.nan), dz

    def get_geometry(self, site, time=None):
        z = self.get_z_layer_faces(site, time=time)

        ds = self._subset_dataset(site, time)

        t = ds["Time"].values

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

    @Expression.decorator
    def get_data(
        self, variable, site, datum="sigma", limits=(0, 1), agg="mean", time=None
    ):

        # Get the raw data
        data = self.get_raw_data(variable, site, time=time)
        stat = self.get_mask_vector(site, time=time)

        # Only dim names are used, so doesn't require a subset ds
        dims = self.ds[site][variable].dims

        # If data requires depth averaging
        if dims[-1] == "NumLayers":

            # Get the integral limits
            z2_z1, dz = self.get_integral_data(site, datum, limits, time=time)

            # Update stat vector with invalid limits
            stat = stat | z2_z1.mask

            if agg == "mean":
                # Integrate the data w.r.t z
                data = np.nansum(data * dz, axis=0) * (1 / z2_z1)
            elif agg == "min":
                data = np.ma.masked_array(data=data, mask=dz == 0).min(axis=0)
            elif agg == "max":
                data = np.ma.masked_array(data=data, mask=dz == 0).max(axis=0)
            else:
                assert False, "agg must be equal to 'min', 'mean' or 'max'"

        # No action required
        elif dims[-1] == "N1":
            data = np.squeeze(data)

        # Data is 1D in z but has 2 dims (e.g. BED_MASS (time, SEDIMENT_FRACTION))
        else:
            print(
                "Warning: Data is a 1D variable with a secondary dimension: {0}".format(
                    dims[-1]
                )
            )
            print("Summing data across the secondary dimension")
            print("Consider using get_raw_data if this is not the desired action")
            data = data.sum(axis=0)

        # Return the data
        return np.ma.masked_array(data=data, mask=stat, fill_value=np.nan)

    def get_timeseries(
        self,
        site: str,
        variables: Union[str, list] = None,
        time: slice = None,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
    ):
        ds = self._subset_dataset(site, time)
        if variables is not None:
            if isinstance(variables, str):
                variables = [variables]
        else:
            variables = [x for x in self.variables if x != "layerface_Z"]

        # Add V/VDir methods
        requested_vars = variables.copy()
        check_reqvars = False
        if "V" in variables:
            variables.extend(["V_x", "V_y"])
            variables.pop(variables.index("V"))
            check_reqvars = True
        if "VDir" in variables:
            variables.extend(["V_x", "V_y"])
            variables.pop(variables.index("VDir"))
            check_reqvars = True
        variables = np.unique(variables).tolist()

        # Prepare blank dataset with all variable info
        dropvars = [x for x in ds.data_vars if x not in variables]

        # Added missing_dims='ignore' for cases where profile was extracted from a 2D domain
        dst = ds.drop_vars(["layerface_Z"] + dropvars).isel(
            NumLayers=0, missing_dims="ignore"
        )
        dst.attrs["Origin"] = (
            "Timeseries extracted from TUFLOWFV cell-centered output using `tfv` python tools"
        )
        dst.attrs["Type"] = "Timeseries cell from TUFLOWFV Output"
        dst.attrs["Datum"] = str(datum)
        dst.attrs["Limits"] = str(limits)
        dst.attrs["Agg Fn"] = agg

        for var in variables:
            dst[var] = (
                ("Time",),
                self.get_data(
                    var, site, datum=datum, limits=limits, agg=agg, time=time
                ),
            )
            dst[var].attrs = ds[var].attrs

        # Very inelegant but it'll do for now. More efficient than routing through the magic expression decorator
        if "V" in requested_vars:
            dst["V"] = np.hypot(dst["V_x"], dst["V_y"])
            dst["V"].attrs = {"long_name": "current speed", "units": "m s^-1"}
        if "VDir" in requested_vars:
            dst["VDir"] = (90 - np.arctan2(dst["V_y"], dst["V_x"]) * 180 / np.pi) % 360
            dst["VDir"].attrs = {"long_name": "current direction", "units": "degN TO"}

        if check_reqvars:
            if "V_x" not in requested_vars:
                dst = dst.drop_vars(["V_x"])
            if "V_y" not in requested_vars:
                dst = dst.drop_vars(["V_y"])

        return dst

    def _subset_dataset(self, site, time):
        """Helper function to subset datasets"""
        # Use sliced xarray dataset
        dsx = self.ds[site]
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
                dsx = dsx.sel(Time=[time], method="nearest")
            elif isinstance(time, list):
                dsx = dsx.isel(Time=time)
            elif time is None:
                dsx
            else:
                dsx = dsx.sel(Time=time)
        except AttributeError:
            print(time_slice_err)

        return dsx

    def __prepare_file_handle__(self):
        if isinstance(self.file, xr.Dataset):
            self.file = self.file.encoding["source"]
        nc = Dataset(self.file, "r")
        grps = nc.groups.keys()
        time = nc["ResTime"][:]
        tvec = pd.to_timedelta(time, unit="h") + pd.Timestamp(1990, 1, 1)

        self.ds = {}
        for grp in grps:
            ds = xr.open_dataset(self.file, group=grp)
            ds["Time"] = tvec
            ds.attrs["Label"] = grp
            ds.attrs["X"] = float(ds["X"][0].values)
            ds.attrs["Y"] = float(ds["Y"][0].values)
            self.ds[grp] = ds

        # TODO: Remove in future - here for legacy support
        self.nc = nc

    def __prepare_time_vector__(self):
        # Prepare time vector relative to python epoch
        fv_epoch = pd.Timestamp(1990, 1, 1)
        self.time_vector = pd.to_timedelta(self.nc["ResTime"][:], unit="h") + fv_epoch
        self.nt = self.time_vector.size

    def __prepare_locations__(self):
        self.locations = {}
        for group in self.nc.groups.keys():
            xp = self.nc[group]["X"][:].data[0]
            yp = self.nc[group]["Y"][:].data[0]
            self.locations[group] = [xp, yp]

    # Inherit doc strings (needs to be done a better way)
    get_raw_data.__doc__ = TimeSeries.get_raw_data.__doc__
    get_mask_vector.__doc__ = TimeSeries.get_mask_vector.__doc__
    get_z_layer_faces.__doc__ = TimeSeries.get_z_layer_faces.__doc__
    get_integral_data.__doc__ = TimeSeries.get_integral_data.__doc__

    get_data.__doc__ = TimeSeries.get_data.__doc__

    __prepare_file_handle__.__doc__ = TimeSeries.__prepare_file_handle__.__doc__
    __prepare_time_vector__.__doc__ = TimeSeries.__prepare_time_vector__.__doc__
    __prepare_locations__.__doc__ = TimeSeries.__prepare_locations__.__doc__
