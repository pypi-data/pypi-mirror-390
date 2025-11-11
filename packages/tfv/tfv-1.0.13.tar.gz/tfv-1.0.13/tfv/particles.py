"""Particle module"""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
from datetime import datetime as dt
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional, List
from types import GeneratorType

from tfv.miscellaneous import Expression

import dask
import dask.array as da


@dataclass
class Grid3D:
    """Container for 3D grid information"""

    xedges: np.ndarray
    yedges: np.ndarray
    zedges: np.ndarray
    bbox: Tuple[float, float, float, float]
    zlims: Tuple[float, float]


class FvParticles:
    """Low-level particle processing functionality"""

    def __init__(self):
        pass

    def _validate_aggregation(self, agg: str) -> None:
        """Validate aggregation method"""
        valid_aggs = ["mean", "sum", "min", "max"]
        if agg not in valid_aggs:
            raise ValueError(
                f"Unsupported aggregation method: {agg}. "
                f"Must be one of: {valid_aggs}"
            )

    def _validate_dimensions(self, *arrays: Union[np.ndarray, da.Array]) -> None:
        """Validate that input arrays have compatible dimensions"""
        shapes = [arr.shape for arr in arrays]
        if not all(s == shapes[0] for s in shapes):
            raise ValueError(f"Input arrays have incompatible shapes: {shapes}")

    def _setup_grid(
        self,
        x: Union[np.ndarray, da.Array],
        y: Union[np.ndarray, da.Array],
        z: Union[np.ndarray, da.Array],
        bbox: Optional[Tuple[float, float, float, float]] = None,
        zlims: Optional[Tuple[float, float]] = None,
        dx: Optional[float] = None,
        dy: Optional[float] = None,
        dz: Optional[float] = None,
        nx: int = 100,
        ny: int = 100,
        nz: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Setup grid edges based on data extents or specified bounds"""
        # Get horizontal bounds
        if bbox is None:
            if isinstance(x, da.Array):
                xmin, xmax = da.nanmin(x).compute(), da.nanmax(x).compute()
                ymin, ymax = da.nanmin(y).compute(), da.nanmax(y).compute()
            else:
                xmin, xmax = np.nanmin(x), np.nanmax(x)
                ymin, ymax = np.nanmin(y), np.nanmax(y)
        else:
            xmin, ymin, xmax, ymax = bbox

        # Get vertical bounds
        if zlims is None and ((nz > 1) | (dz is not None)):
            if isinstance(z, da.Array):
                zmin, zmax = da.nanmin(z).compute(), da.nanmax(z).compute()
            else:
                zmin, zmax = np.nanmin(z), np.nanmax(z)
        elif zlims is not None:
            zmin, zmax = zlims
        else:
            # For 2D case, use mean z as single layer
            zmin = zmax = float(
                da.nanmean(z).compute() if isinstance(z, da.Array) else np.nanmean(z)
            )

        # Create edges based on spacing or number of cells
        if dx is not None:
            xedges = np.arange(xmin, xmax + dx / 2, dx)
        else:
            xedges = np.linspace(xmin, xmax, nx + 1)

        if dy is not None:
            yedges = np.arange(ymin, ymax + dy / 2, dy)
        else:
            yedges = np.linspace(ymin, ymax, ny + 1)

        if dz is not None:
            zedges = np.arange(zmin, zmax + dz / 2, dz)
            if len(zedges) == 1:
                zedges = np.array([zmin - 0.1, zmax + 0.1])
        else:
            if nz > 1:
                zedges = np.linspace(zmin, zmax, nz + 1)
            else:
                zedges = np.array([zmin - 0.1, zmax + 0.1])

        return xedges, yedges, zedges

    def grid_timestep(
        self,
        x: Union[np.ndarray, da.Array],
        y: Union[np.ndarray, da.Array],
        z: Union[np.ndarray, da.Array],
        values: Optional[Union[np.ndarray, da.Array]] = None,
        xedges: np.ndarray = None,
        yedges: np.ndarray = None,
        zedges: np.ndarray = None,
        agg: str = "mean",
    ) -> da.Array:
        """Grid a single timestep of particle data with Dask support

        Args:
            x, y, z: Particle coordinates (numpy or dask arrays)
            values: Values to grid (optional)
            xedges, yedges, zedges: Grid edges
            agg: Aggregation method

        Returns:
            da.Array: Gridded data with shape (nz, ny, nx)
        """

        @dask.delayed
        def process_arrays(x, y, z, values=None):
            """Process arrays with computed valid mask"""
            # Convert to numpy arrays for processing
            x = da.compute(x)[0] if isinstance(x, da.Array) else x
            y = da.compute(y)[0] if isinstance(y, da.Array) else y
            z = da.compute(z)[0] if isinstance(z, da.Array) else z

            # Compute valid mask
            valid = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z)
            x_valid = x[valid]
            y_valid = y[valid]
            z_valid = z[valid]

            if values is not None:
                values = (
                    da.compute(values)[0] if isinstance(values, da.Array) else values
                )
                values_valid = values[valid]
            else:
                values_valid = None

            # Handle 2D vs 3D gridding
            if len(zedges) == 2:  # 2D case
                if values_valid is None:
                    H, _, _ = np.histogram2d(y_valid, x_valid, bins=(yedges, xedges))
                    H = H.reshape(1, H.shape[0], H.shape[1])  # Add z dimension
                else:
                    if agg == "mean":
                        H_sum, _, _ = np.histogram2d(
                            y_valid,
                            x_valid,
                            bins=(yedges, xedges),
                            weights=values_valid,
                        )
                        H_count, _, _ = np.histogram2d(
                            y_valid, x_valid, bins=(yedges, xedges)
                        )
                        with np.errstate(divide="ignore", invalid="ignore"):
                            H = np.divide(H_sum, H_count)
                            H[H_count == 0] = np.nan
                    elif agg == "sum":
                        H, _, _ = np.histogram2d(
                            y_valid,
                            x_valid,
                            bins=(yedges, xedges),
                            weights=values_valid,
                        )
                    H = H.reshape(1, H.shape[0], H.shape[1])  # Add z dimension
            else:  # 3D case
                if values_valid is None:
                    H, _ = np.histogramdd(
                        (z_valid, y_valid, x_valid), bins=(zedges, yedges, xedges)
                    )
                else:
                    if agg == "mean":
                        H_sum, _ = np.histogramdd(
                            (z_valid, y_valid, x_valid),
                            bins=(zedges, yedges, xedges),
                            weights=values_valid,
                        )
                        H_count, _ = np.histogramdd(
                            (z_valid, y_valid, x_valid), bins=(zedges, yedges, xedges)
                        )
                        with np.errstate(divide="ignore", invalid="ignore"):
                            H = np.divide(H_sum, H_count)
                            H[H_count == 0] = np.nan
                    elif agg == "sum":
                        H, _ = np.histogramdd(
                            (z_valid, y_valid, x_valid),
                            bins=(zedges, yedges, xedges),
                            weights=values_valid,
                        )

                # Transpose to get (z, y, x) order
                H = np.transpose(H, (0, 1, 2))

            return H

        # Compute shape for output array
        if len(zedges) == 2:
            shape = (1, len(yedges) - 1, len(xedges) - 1)
        else:
            shape = (len(zedges) - 1, len(yedges) - 1, len(xedges) - 1)

        # Process arrays with delayed computation
        delayed_result = process_arrays(x, y, z, values)

        # Convert to dask array
        return da.from_delayed(delayed_result, shape=shape, dtype=float)


class ParticleScatter:
    """Visualization class for particle tracking results"""

    def __init__(self, ax: plt.Axes, data: "xr.Dataset"):
        """
        Initialize visualization object.

        Args:
            ax (plt.Axes): Matplotlib axis to draw on
            data (xr.Dataset): Dataset containing particle data
        """
        self.ax = ax
        self._data = data
        self.scatter = None
        self._current_time = None
        self.time_vector = pd.to_datetime(self._data["time"].values)
        self.color_by = "groupID"

    def update(
        self,
        time_idx: int,
        color_by: str = None,
        size_by: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Update the particle visualization for a given time.

        Args:
            time_idx (int): Time index to plot
            ds (xr.Dataset): Filtered dataset to plot
            color_by (str, optional): Variable to color points by. Defaults to 'groupID'
            size_by (str, optional): Variable to scale point sizes by
            **kwargs: Additional arguments passed to scatter
        """

        if color_by is not None:
            self.color_by = color_by

        ds = self._data

        # Get data for current timestep
        data = ds.isel(time=time_idx)
        self._current_time = data.time

        # Handle coloring
        c, clabel = _process_color_variable(data, self.color_by)
        c = kwargs.pop("c", c)
        self.plot_label = clabel

        # Handle sizing
        if size_by is not None and size_by in data.variables:
            s = data[size_by]
        else:
            s = kwargs.pop("s", 3)

        alpha = kwargs.pop("alpha", 0.75)

        if self.scatter is None:
            self.scatter = self.ax.scatter(
                data.x, data.y, c=c, s=s, alpha=alpha, **kwargs
            )
        else:
            self.scatter.set_offsets(np.c_[data.x, data.y])
            if isinstance(c, (xr.DataArray, np.ndarray)):
                self.scatter.set_array(c)
            if isinstance(s, (xr.DataArray, np.ndarray)):
                self.scatter.set_sizes(s)

    def get_time_current(self) -> pd.Timestamp:
        """Get current time"""
        return pd.to_datetime(self._current_time.values)

    def set_time_current(self, time: Union[int, str, pd.Timestamp]) -> None:
        """Set current time"""
        if isinstance(time, str):
            time = pd.Timestamp(time)
            idx = np.argmin(np.abs(self.time_vector - time))
        elif isinstance(time, pd.Timestamp):
            idx = np.argmin(np.abs(self.time_vector - time))
        elif isinstance(time, int):
            idx = time
        else:
            raise ValueError(f"Time type `{type(time)}` not supported.")

        self.update(idx)


class ParticleHist:
    """Visualization class for particle histogram results"""

    def __init__(self, ax: plt.Axes, data: "xr.Dataset"):
        """Initialize histogram visualization object."""
        self.ax = ax
        self._data = data
        self.quadmesh = None
        self._current_time = None
        self.time_vector = pd.to_datetime(self._data["time"].values)
        # Initialize gridding processor
        self._processor = FvParticles()
        # Store grid parameters
        self._grid_params = {}
        # Store the color_by choice
        self.color_by = None

    def update(
        self,
        time_idx: int,
        color_by: Optional[str] = None,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        dx: Optional[float] = None,
        dy: Optional[float] = None,
        nx: int = 100,
        ny: int = 100,
        statistic: str = "mean",
        **kwargs,
    ) -> None:
        """
        Update the histogram visualization for a given time.
        """
        # Get data for current timestep
        data = self._data.isel(time=time_idx)
        self._current_time = data.time

        if color_by is not None:
            self.color_by = color_by

        # Get particle positions
        x = data.x
        y = data.y
        z = data.z

        # Setup grid if needed
        if not self._grid_params or self._grid_params != {
            "bbox": bbox,
            "dx": dx,
            "dy": dy,
            "nx": nx,
            "ny": ny,
        }:
            self._xedges, self._yedges, self._zedges = self._processor._setup_grid(
                x, y, z, bbox, None, dx, dy, None, nx, ny, 1
            )
            self._grid_params = {"bbox": bbox, "dx": dx, "dy": dy, "nx": nx, "ny": ny}

        # Compute grid
        if color_by is not None:
            values, default_label = _process_color_variable(data, color_by)

            H = self._processor.grid_timestep(
                x, y, z, values, self._xedges, self._yedges, self._zedges, agg=statistic
            )
            default_label = f"{statistic.capitalize()} of {default_label}"
        else:
            # Compute density
            H = self._processor.grid_timestep(
                x, y, z, None, self._xedges, self._yedges, self._zedges
            )
            # Normalize for density
            total = float(H.sum())
            H = H / total if total > 0 else H
            default_label = "Density"

        # Squeeze out z dimension
        H = H.squeeze(axis=0)

        # Set 0 to nan so we get transparent bg
        H[H == 0.0] = np.nan

        # Set default colormap if not specified
        if "cmap" not in kwargs:
            cmap = plt.get_cmap("viridis").copy()
            cmap.set_bad(alpha=0)  # Make nan values transparent
            kwargs["cmap"] = cmap

        # Create or update plot
        if self.quadmesh is None:
            self.quadmesh = self.ax.pcolormesh(self._xedges, self._yedges, H, **kwargs)
        else:
            self.quadmesh.set_array(H.ravel())

        # Store attributes for future reference
        self.plot_label = default_label

    def get_time_current(self) -> pd.Timestamp:
        """Get current time"""
        return pd.to_datetime(self._current_time.values)

    def set_time_current(self, time: Union[int, str, pd.Timestamp]) -> None:
        """Set current time and update visualization"""
        # Convert input time to index
        if isinstance(time, str):
            time = pd.Timestamp(time)
            idx = np.argmin(np.abs(self.time_vector - time))
        elif isinstance(time, pd.Timestamp):
            idx = np.argmin(np.abs(self.time_vector - time))
        elif isinstance(time, int):
            idx = time
        else:
            raise ValueError(f"Time type `{type(time)}` not supported.")

        # Update visualization with current grid parameters
        self.update(
            time_idx=idx,
            color_by=self.color_by,
            bbox=self._grid_params.get("bbox"),
            dx=self._grid_params.get("dx"),
            dy=self._grid_params.get("dy"),
            nx=self._grid_params.get("nx", 100),
            ny=self._grid_params.get("ny", 100),
            statistic=self._grid_params.get("statistic", "mean"),
        )


def _process_color_variable(
    data: xr.Dataset, color_by: Optional[str]
) -> Tuple[Optional[np.ndarray], str]:
    """Process color variable, handling special cases like age

    Args:
        data: Dataset containing variables
        color_by: Name of variable to use for coloring

    Returns:
        Tuple of (processed values, label)
    """
    if color_by is None:
        return None, ""

    if color_by == "age":
        # Convert timedelta to hours
        values = data.age.astype("timedelta64[ns]").astype("float64") / (3600 * 1e9)
        label = "Age (hours)"
    else:
        values = data[color_by]
        label = color_by

    return values, label
