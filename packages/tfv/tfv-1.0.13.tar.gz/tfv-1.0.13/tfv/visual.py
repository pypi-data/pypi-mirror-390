"""A module defining all objects used to visualise model result data extracts"""

import numpy as np
from tqdm import tqdm

# from tfv.viewer import *
from tfv.extractor import FvExtractor
from tfv.timeseries import FvTimeSeries
from tfv.miscellaneous import *
from tfv.geometry import Mesh
from abc import ABC, abstractmethod

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.quiver import Quiver
from matplotlib.streamplot import streamplot
from matplotlib.patches import FancyArrowPatch
from matplotlib.tri import Triangulation, TriContourSet
from matplotlib.cbook import silent_list
from matplotlib._tri import TriContourGenerator
from matplotlib.collections import PolyCollection, TriMesh, PathCollection

# Non-essential imports
from matplotlib import cm
from matplotlib.dates import DateFormatter
from matplotlib.colors import Normalize, BoundaryNorm


# --------------------------------------------------- Visual Objects ---------------------------------------------------
class Visual(ABC):
    """
    An abstract base class for an object which visualizes a variable. The main purpose of a Visual sub-class is to
    initialize and store a plotting library specific graphics object for a given extract type i.e SheetPatch.

    The Visual object works by connecting its set_time_current method to the Slider object. When self.set_time_current
    is called by the Slider, the Visual object selects a valid time based on the Extractor objects time_vector and updates itself.
    """

    @property
    def time_vector(self):
        return self.extractor.time_vector

    def __init__(self, axes, extractor, expression, **kwargs):
        # Set target axes
        self.axes = axes

        # Set extractor
        self.extractor = extractor
        self._time_current = self.time_vector[0]
        self._time_index = 0

        self.expression = expression
        self.expression_kwargs = dict(
            post_process=kwargs.pop("post_process", None),
        )

        # Check whether the user has supplied a normal exp
        # (e.g., str 'V_x', list of vars ['V_x', 'V_y'])
        # OR whether the user supplied a list of data [np.array, np.array]
        self.custom_data = False
        if isinstance(self.expression, list):
            if isinstance(self.expression[0], np.ndarray):
                self.__process_custom_data__()
        elif isinstance(self.expression, np.ndarray):
            self.__process_custom_data__()
        else:
            self.custom_data = False

        # Connect with viewer
        viewer = kwargs.pop("viewer", None)
        if viewer is None:
            # viewer = Viewer.__register__[0]
            self.viewer = None
        else:
            self.viewer = viewer
            self.viewer.time_vector = self.time_vector
            self.viewer.connect(self.set_time_current)

        # Initialize the graphics object
        zoom = kwargs.pop("zoom", True)
        self.__prep_graphics_obj__(**kwargs)

        # NOTE: AEW Dec 22, 2022: Moved zoom above __prep_graphics_object__
        # Unsure what ramifications this will have, but it will solve vector grid for zoomed
        # Zoom to the graphics object
        if zoom is True:
            self.zoom()

    def get_time_current(self):
        return self._time_current

    def set_time_current(self, time):
        # Add a catch to allow str or int based indexing
        if type(time) == str:
            time = pd.Timestamp(time)
        elif type(time) == int:
            time = self.time_vector[time]

        ii = np.argmin(np.abs(self.time_vector - time))

        if ii != self._time_index:
            self._time_index = ii
            self._time_current = self.time_vector[ii]
            self.__dynamic_update__()

            if self.viewer:
                self.viewer.figure.canvas.draw()

    def __process_custom_data__(self):
        self.custom_data = True
        self.vardata = np.ma.stack(self.expression)

        # Apply post-processing logic to data
        if self.expression_kwargs["post_process"]:
            fn = self.expression_kwargs["post_process"]
            self.vardata = fn(self.vardata)
        else:
            self.vardata = np.squeeze(self.vardata)

    @abstractmethod
    def __get_data__(self):
        """Abstract method which returns object data based on the expression"""

    @abstractmethod
    def __prep_graphics_obj__(self, **kwargs):
        """Abstract method to initialize the graphics object which will be used to visualize the result"""

    @abstractmethod
    def __static_update__(self):
        """Abstract method which updates static components of graphics object"""

    @abstractmethod
    def __dynamic_update__(self):
        """Abstract method which updates dynamic components graphics object"""

    @abstractmethod
    def zoom(self):
        """Abstract method which zooms axis to extent of graphics object"""


class SheetPatch(Visual):
    """
    Class for dynamic visualization of model result sheet extracts as collection of patches


    Parameters
    ----------
    axes : matplotlib.pyplot.Axes
        Axes object to display/render the graphics object
    extractor : tfv.extractor.Extractor
        Extractor object which is extracting data
    expression : string
        Expression that defines a variable
    datum : {'sigma', 'depth', 'height', 'elevation'}
        Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    limits : tuple
        Vertical depth-averaging limits (z1, z2) relative to vertical datum.
    data : numpy.array
        Custom data array of data for plotting. Should have length equal to either
        NumCells2D (if uses shading==flat, the default default) or NumVert2D if shading =='interp'


    Other Parameters
    ----------------
    shading : {'flat', 'interp'}
        Sets the shading to be flat (default) or interpolated (gourad)
    zorder : integer
        Layer order in which graphics object will be rendered (0 is bottom/first)
    cmap : matplotlib.colors.LinearSegmentedColormap
        Colormap object for mapping normalized data (0 - 1) to rgb colors
    norm : matplotlib.colors.BoundaryNorm
        Normalization object for normalizing raw data to (0 - 1) based on (min, max)
    clim : tuple
        Colour limits of the underlying matplotlib.collections.PatchCollection object (min, max)
    edgecolor : string
        Sets the mesh edge colouring of the underlying matplotlib.collections object
    antialiased : bool
        Sets the antialiasing state for rendering the underlying matplotlib.collections object
    alpha : float
        Sets the transparencies of the underlying matplotlib.collections object

    """

    def __init__(
        self,
        axes,
        extractor,
        expression,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        mask_dry=True,
        **kwargs,
    ):
        self.datum = datum
        self.limits = limits
        self.agg = agg
        self.mask_dry = mask_dry

        # Call initialize method of super class
        super(SheetPatch, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        args = (
            self.expression,
            self._time_index,
            self.datum,
            self.limits,
            self.agg,
            self.mask_dry,
        )
        if self.shading == "flat":
            return self.extractor.get_sheet_cell(*args, **self.expression_kwargs)
        elif self.shading == "interp":
            return self.extractor.get_sheet_node(*args, **self.expression_kwargs)

    def __prep_graphics_obj__(self, **kwargs):
        # Pop key word arguments which are not used by the graphics object
        self.shading = kwargs.pop("shading", "flat")

        # Get handles on sheet geometry
        node_x = self.extractor.node_x
        node_y = self.extractor.node_y
        cell_node = self.extractor.cell_node
        tri_cell_node = self.extractor.tri_cell_node

        # # Instantiate graphics object based on shading type
        if self.custom_data:
            data = self.vardata
        else:
            data = self.__get_data__()

        if self.shading == "flat":
            xy = np.dstack((node_x[cell_node], node_y[cell_node]))
            self.patch = PolyCollection(xy, array=data, **kwargs)
        elif self.shading == "interp":
            self.tri = Triangulation(node_x, node_y, triangles=tri_cell_node)
            self.patch = TriMesh(self.tri, array=data, antialiased=True, **kwargs)

            # Mask invalid triangles
            mask = np.any(data.mask[self.extractor.tri_cell_node], axis=1)
            self.tri.set_mask(mask)

        # Add the graphics object to axes
        self.axes.add_collection(self.patch)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        data = self.__get_data__()
        self.patch.set_array(data)

        # Mask invalid triangles
        if self.shading == "interp":
            mask = np.any(data.mask[self.extractor.tri_cell_node], axis=1)
            self.tri.set_mask(mask)

    def zoom(self):
        self.axes.set_xlim(
            [np.min(self.extractor.node_x), np.max(self.extractor.node_x)]
        )
        self.axes.set_ylim(
            [np.min(self.extractor.node_y), np.max(self.extractor.node_y)]
        )


class SheetContour(Visual):
    """
    Class for dynamic visualization of model result sheet extracts as contours

    Parameters
    ----------
    axes : matplotlib.pyplot.Axes
        Axes object to display/render the graphics object
    extractor : tfv.extractor.Extractor
        Extractor object which is extracting data
    expression : string
        Expression that defines a variable
    datum : {'sigma', 'depth', 'height', 'elevation'}
        Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    limits : tuple
        Vertical depth-averaging limits (z1, z2) relative to vertical datum.

    Other Parameters
    ----------------
    zorder : integer
        Layer order in which graphics object will be rendered (0 is bottom/first)
    cmap : matplotlib.colors.LinearSegmentedColormap
        Colormap object for mapping normalized data (0 - 1) to rgb colors
    norm : matplotlib.colors.BoundaryNorm
        Normalization object for normalizing raw data to (0 - 1) based on (min, max)
    clim : tuple
        Colour limits of the underlying matplotlib.collections.PatchCollection object (min, max)
    edgecolor : string
        Sets the mesh edge colouring of the underlying matplotlib.collections object
    antialiased : bool
        Sets the antialiasing state for rendering the underlying matplotlib.collections object
    alpha : float
        Sets the transparencies of the underlying matplotlib.collections object
    """

    def __init__(
        self,
        axes,
        extractor,
        expression,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        mask_dry=True,
        **kwargs,
    ):
        self.datum = datum
        self.limits = limits
        self.agg = agg
        self.mask_dry = mask_dry

        # Call initialize method of super class
        super(SheetContour, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        args = (
            self.expression,
            self._time_index,
            self.datum,
            self.limits,
            self.agg,
            self.mask_dry,
        )
        return self.extractor.get_sheet_node(*args, **self.expression_kwargs)

    def __prep_graphics_obj__(self, **kwargs):
        # Get handles on sheet geometry
        node_x = self.extractor.node_x
        node_y = self.extractor.node_y
        tri_cell_node = self.extractor.tri_cell_node

        # Get triangular mesh and initialize cpp triangulation
        tri = Triangulation(node_x, node_y, triangles=tri_cell_node)
        self.tri = tri
        self.cpp_tri = tri.get_cpp_triangulation()

        # Get data
        if self.custom_data:
            data = self.vardata
        else:
            data = self.__get_data__()

        # Mask bad triangles
        mask = np.any(data.mask[self.extractor.tri_cell_node], axis=1)
        self.cpp_tri.set_mask(mask)

        # Set contour limits/levels
        zlim = [data.min(), data.max()]

        # BUG: This is a workaround for matplotlib's TriContourSet, which has issues on a log scale with nega values
        # even if they are masked. Hence we will block out this data
        data.data[data.mask] = zlim[0]

        clim = kwargs.pop("clim", [zlim[0], zlim[1]])
        self.levels = kwargs.pop("levels", 50)

        if type(self.levels) is int:
            levels = np.linspace(clim[0], clim[1], self.levels)
        else:
            levels = self.levels

        self.cont_args = kwargs  # For dynamic update
        filled = kwargs.pop("filled", True)
        extend = kwargs.pop("extend", "both")
        self.cont = TriContourSet(
            self.axes, tri, data.data, levels, filled=filled, extend=extend, **kwargs
        )

        if clim is not None:
            self.cont.set_clim(clim)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        # Get data
        if self.custom_data:
            assert False, "You can't update time dynamically when supplying custom data"
        data = self.__get_data__()

        # Mask bad triangles
        mask = np.any(data.mask[self.extractor.tri_cell_node], axis=1)
        self.cpp_tri.set_mask(mask)

        # Set contour limits/levels
        zlim = [data.min(), data.max()]
        clim = self.cont.get_clim()

        if type(self.levels) is int:
            levels = np.linspace(clim[0], clim[1], self.levels)
        else:
            levels = self.levels

        self.cont.remove()

        self.cont = TriContourSet(
            self.axes,
            self.tri,
            data.data,
            levels,
            filled=True,
            extend="both",
            **self.cont_args,
        )

        self.cont.set_clim(clim)

    def zoom(self):
        self.axes.set_xlim(
            [np.min(self.extractor.node_x), np.max(self.extractor.node_x)]
        )
        self.axes.set_ylim(
            [np.min(self.extractor.node_y), np.max(self.extractor.node_y)]
        )


class SheetVector(Visual):
    """
    Class for dynamic visualization of model result sheet extracts as gridded vector field

    Parameters
    ----------
    axes : matplotlib.pyplot.Axes
        Axes object to display/render the graphics object
    extractor : tfv.extractor.Extractor
        Extractor object which is extracting data
    expression : tuple
        Tuple of string expressions that defines vector, e.g., ('V_x', 'V_y')
    datum : {'sigma', 'depth', 'height', 'elevation'}
        Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    limits : tuple
        Vertical depth-averaging limits (z1, z2) relative to vertical datum.
    agg : str
        Depth-averaging aggregation function. One of {`min`,`mean`,`max`}.
        Defaults to 'mean'.
    normalise : bool
        Flag to normalise the plotted vectors. Defaults to False.
    convention : str
        Convention basis upon which to calculate and draw the vectors.
        One of {'cartesian', 'polar'}. Defaults to 'cartesian'.
        Cartesian convention expects the expression to be U/V components,
        while polar expects these to be MAG/THETA. The base and heading
        can be modified using `convention_base` and `convention_heading`.
    convention_base : str
        Base from which angles are measured from, one of {'north','east'}.
        Defaults to 'east. Does not do anything unless convention == 'polar'
    convention_heading : str
        Direction which the angles are measured along. One of {'CW', 'CCW'}.
        Defaults to 'CCW' for counter clockwise.
        Does not do anything unless convention == 'polar'
    plot_type : str
        Type of vector plot to show. One of {'quiver', 'streamplot'}.
        Defaults to quiver.
    """

    def __init__(
        self,
        axes,
        extractor,
        expression,
        datum="sigma",
        limits=(0, 1),
        agg="mean",
        normalise=False,
        convention="cartesian",
        convention_base="east",
        convention_heading="CCW",
        plot_type="quiver",
        **kwargs,
    ):
        self.datum = datum
        self.limits = limits
        self.agg = agg
        self.norm = normalise

        self.xg = None
        self.yg = None
        self.grid_index = None

        self.convention = convention
        self.cbase = convention_base
        self.cheading = convention_heading

        self.plot_type = plot_type
        self.fancy_lw = kwargs.pop("fancy_lw", False)

        # Call initialize method of super class
        super(SheetVector, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        args = (self._time_index, self.xg, self.yg, self.datum, self.limits, self.agg)
        c1 = self.extractor.get_sheet_grid(
            self.expression[0], *args, grid_index=self.grid_index
        )
        c2 = self.extractor.get_sheet_grid(
            self.expression[1], *args, grid_index=self.grid_index
        )

        if self.convention == "cartesian":
            u, v = c1, c2

        elif self.convention == "polar":
            mag, th = c1, c2

            if self.cbase == "north":
                th = (90 - th) % 360
            elif self.cbase != "east":
                raise ValueError("`convention_base` must be one of {'east', 'north'}")

            if self.cheading == "CW":
                th = (180 - th) % 360
            elif self.cheading != "CCW":
                raise ValueError("`convention_heading` must be one of {'CCW', 'CW'}")

            u = mag * np.cos(np.radians(th))
            v = mag * np.sin(np.radians(th))
        else:
            raise ValueError("`convention` must be one of {'cartesian','polar'}")

        return u, v

    def __prep_graphics_obj__(self, **kwargs):
        # Pop key word arguments which are not used by the graphics object
        self.resolution = kwargs.pop("resolution", 40)

        # Instantiate graphics object with no data, data will be added on draw event automatically
        if self.plot_type == "quiver":
            self.vectors = Quiver(
                self.axes,
                np.mean(self.extractor.node_x),
                np.mean(self.extractor.node_y),
                0,
                0,
                **kwargs,
            )

            self.axes.add_collection(self.vectors)
        elif self.plot_type == "streamplot":
            self.kwargs = kwargs  # need to store for later

        # Connect the regrid method to the draw event of the figure object.
        self._x_cid = self.axes.callbacks.connect(
            "xlim_changed", self.__static_update__
        )
        self._y_cid = self.axes.callbacks.connect(
            "ylim_changed", self.__static_update__
        )

    def __static_update__(self, event=None):
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        self.xg = np.linspace(xlim[0], xlim[1], self.resolution)
        self.yg = np.linspace(ylim[0], ylim[1], self.resolution)
        self.grid_index = self.extractor.get_grid_index(self.xg, self.yg)

        u, v = self.__get_data__()
        msk = u.mask  # This is for the first timestep when Vx Vy = 0.
        if self.norm == True:
            r = np.power(np.add(np.power(u, 2), np.power(v, 2)), 0.5)
        else:
            r = 1
        u = u / r
        v = v / r

        x, y = [arr.flatten() for arr in np.meshgrid(self.xg, self.yg)]
        xy = np.hstack((x[:, np.newaxis], y[:, np.newaxis]))

        if self.plot_type == "quiver":
            self.vectors.set_offsets(xy)
            self.vectors.N = xy.shape[0]
            self.vectors.set_UVC(u.flatten(), v.flatten())

        elif self.plot_type == "streamplot":
            self.__redraw_streamplot(u, v)

    def __dynamic_update__(self):
        u, v = self.__get_data__()
        if self.norm == True:
            r = np.power(np.add(np.power(u, 2), np.power(v, 2)), 0.5)
        else:
            r = 1

        if self.plot_type == "quiver":
            self.vectors.set_UVC(u / r, v / r)

        elif self.plot_type == "streamplot":
            self.__redraw_streamplot(u, v)

    def __redraw_streamplot(self, u, v):
        if hasattr(self, "vectors"):
            self.vectors.lines.remove()
        for artist in self.axes.get_children():
            if isinstance(artist, FancyArrowPatch):
                artist.remove()

        if self.fancy_lw:
            self.kwargs.pop("linewidth", None)
            mag = np.hypot(u, v)
            lw = 1 * mag / mag.max()
        else:
            lw = self.kwargs.pop("linewidth", 0.5)
        self.vectors = self.axes.streamplot(
            self.xg, self.yg, u, v, linewidth=lw, **self.kwargs
        )

    def zoom(self):
        self.axes.set_xlim(
            [np.min(self.extractor.node_x), np.max(self.extractor.node_x)]
        )
        self.axes.set_ylim(
            [np.min(self.extractor.node_y), np.max(self.extractor.node_y)]
        )


class CurtainPatch(Visual):
    """
    Class for dynamic visualization of model result curtain extracts as collection of patches.

    Arguments
    ---------
    :param axes -- object | Axes object.
    :param extractor -- object | Extractor object.
    :param expression -- string | String expression that defines variable.
    :param polyline -- 2D array | Polyline as [x, y] used to slice 3D data.

    Returns
    -------
    :param curtain -- object | CurtainPatch instance.

    Examples
    --------
    >> xtr = FvExtractor('my_file_3D.nc')
    >> curtain = CurtainPatch(axes, xtr, polyline, 'SAL')
    """

    def __init__(self, axes, extractor, expression, polyline, crs=None, **kwargs):
        self.polyline = polyline
        self.x_data = extractor.get_intersection_data(polyline)
        self.index = extractor.get_curtain_cell_index(polyline)
        self.crs = crs

        # Call initialize method of super class
        super(CurtainPatch, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        self.geo = self.extractor.get_curtain_cell_geo(
            self._time_index, self.polyline, self.x_data, self.index, crs=self.crs
        )

        args = (
            self.expression,
            self._time_index,
            self.polyline,
            self.x_data,
            self.index,
        )
        return self.extractor.get_curtain_cell(*args, **self.expression_kwargs)

    def __prep_graphics_obj__(self, **kwargs):
        if self.custom_data:
            data = self.vardata
        else:
            data = self.__get_data__()

        node_x, node_y, cell_node = self.geo

        xy = np.dstack((node_x[cell_node], node_y[cell_node]))
        self.patch = PolyCollection(xy, array=data, **kwargs)

        # Add the graphics object to axes
        self.axes.add_collection(self.patch)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        data = self.__get_data__()
        node_x, node_y, cell_node = self.geo

        xy = np.dstack((node_x[cell_node], node_y[cell_node]))

        self.patch.set_verts(xy)
        self.patch.set_array(data)

    def zoom(self):
        self.axes.set_xlim([np.min(self.geo[0]), np.max(self.geo[0])])
        self.axes.set_ylim([np.min(self.geo[1]), np.max(self.geo[1])])


class CurtainVector(Visual):
    """
    Class for dynamic visualization of model result curtain extracts as gridded vector field

    Arguments
    ---------
    :param axes -- object | Axes object.
    :param extractor -- object | Extractor object.
    :param expression -- string | String expression that defines variable.
    :param polyline -- 2D array | Polyline as [x, y] used to slice 3D data.

    Returns
    -------
    :param curtain -- object | CurtainPatch instance.

    Examples
    --------
    >> xtr = FvExtractor('my_file_3D.nc')
    >> curtain = SheetContour(axes, xtr, polyline, ['V', 'W'])
    """

    def __init__(
        self, axes, extractor, expression, polyline, tangential=True, **kwargs
    ):
        self.polyline = polyline
        self.x_data = extractor.get_intersection_data(polyline)
        self.index = extractor.get_curtain_cell_index(polyline)
        self.tangential = tangential

        self.xg = np.array([0, 1])
        self.yg = np.array([0, 1])

        # Call initialize method of super class
        super(CurtainVector, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        self.geo = self.extractor.get_curtain_cell_geo(
            self._time_index,
            self.polyline,
            self.x_data,
            self.index,
            return_unit_vector=True,
        )

        args = (
            self._time_index,
            self.polyline,
            self.xg,
            self.yg,
            self.x_data,
            self.index,
        )

        u = self.extractor.get_curtain_grid(self.expression[0], *args)
        v = self.extractor.get_curtain_grid(self.expression[1], *args)

        # Get the tangential component to the patch faces
        if self.tangential:
            grid_index = Mesh(*self.geo[:3]).get_grid_index(self.xg, self.yg)
            mask = np.equal(grid_index, -999)
            valid = np.equal(mask, False)
            uv = np.stack((u.ravel(), v.ravel()))

            utang = self.geo[4]
            utang_msk = utang[:, grid_index[valid]]
            tang = np.sum(uv[:, valid.ravel()].conj() * utang_msk, axis=0)

            u[valid] = -tang * utang_msk[0, :]

            if "W" in self.extractor.variables:
                v[valid] = self.extractor.get_curtain_grid("W", *args)[valid]
            else:
                v[valid] = 0

        return u, v

    def __prep_graphics_obj__(self, **kwargs):
        # Pop key word arguments which are not used by the graphics object
        self.resolution = kwargs.pop("resolution", 40)

        # Update geometry
        self.__get_data__()

        # Instantiate graphics object with no data, data will be added on draw event automatically
        self.quiver = Quiver(
            self.axes, np.mean(self.geo[0]), np.mean(self.geo[1]), 0, 0, **kwargs
        )

        # Add the graphics object to axes
        self.axes.add_collection(self.quiver)

        # Connect the regrid method to the draw event of the figure object.
        self._cid = self.axes.figure.canvas.mpl_connect(
            "draw_event", lambda event: self.__dynamic_update__()
        )

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()

        self.xg = np.linspace(xlim[0], xlim[1], self.resolution)
        self.yg = np.linspace(ylim[0], ylim[1], self.resolution)

        u, v = self.__get_data__()

        x, y = [arr.flatten() for arr in np.meshgrid(self.xg, self.yg)]
        xy = np.hstack((x[:, np.newaxis], y[:, np.newaxis]))

        self.quiver.set_offsets(xy)
        self.quiver.N = xy.shape[0]
        self.quiver.set_UVC(u, v)

    def zoom(self):
        self.axes.set_xlim([np.min(self.geo[0]), np.max(self.geo[0])])
        self.axes.set_ylim([np.min(self.geo[1]), np.max(self.geo[1])])


class ProfileCell(Visual):
    """
    Class for dynamic visualization of model result profile extracts as vertical line

    Arguments
    ---------
    :param axes -- object | Axes object.
    :param extractor -- object | Extractor object.
    :param expression -- string | String expression that defines variable.
    :param point -- tuple | Point (x, y) of profile location.

    Returns
    -------
    :param profile -- object | ProfileCell instance.

    Examples
    --------
    >> xtr = FvExtractor('my_file_3D.nc')
    >> profile = ProfileCell(axes, xtr, point, 'SAL')
    """

    def __init__(self, axes, extractor, expression, point, **kwargs):
        self.point = point

        super(ProfileCell, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        self.elevation = self.extractor.get_profile_cell_geo(
            self._time_index, self.point
        )

        args = (self.expression, self._time_index, self.point)
        return self.extractor.get_profile_cell(*args, **self.expression_kwargs)

    def __prep_graphics_obj__(self, **kwargs):
        if self.custom_data:
            data = self.vardata
        else:
            data = self.__get_data__()
        self.line = Line2D(data, self.elevation, **kwargs)

        self.axes.add_line(self.line)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        data = self.__get_data__()
        self.line.set_data(data, self.elevation)

    def zoom(self):
        data = self.__get_data__()
        if data.min() != 0 and data.max() != 0:
            self.axes.set_xlim([data.min() * 0.95, data.max() * 1.05])
        self.axes.set_ylim([self.elevation.min() * 0.95, self.elevation.max() * 1.05])


class SeriesGlider(Visual):
    """
    Class for dynamic visualization of model result time series extracts with current time marked

    Arguments
    ---------
    :param axes -- object | Axes object.
    :param extractor -- object | Extractor object.
    :param expression -- string | String expression that defines variable.
    :param location -- tuple | Point (x, y) of profile location.

    Keyword Arguments
    -----------------
    :param datum -- string | Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    :param limits -- tuple | Vertical depth-averaging limits relative to vertical datum.

    Returns
    -------
    :param profile -- object | ProfileCell instance.

    Examples
    --------
    >> xtr = FvExtractor('my_file_3D.nc')
    >> profile = ProfileCell(axes, xtr, point, 'SAL')
    """

    def __init__(
        self,
        axes,
        extractor,
        expression,
        location,
        datum="sigma",
        limits=(0, 1),
        **kwargs,
    ):
        self.location = location
        self.datum = datum
        self.limits = limits

        super(SeriesGlider, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        args = (self.expression, self.location, self.datum, self.limits)
        return self.extractor.get_data(*args)

    def __prep_graphics_obj__(self, **kwargs):
        self.date_fmt = kwargs.pop("date_fmt", "%d/%m/%Y")

        x = self.extractor.time_vector
        y = self.__get_data__()

        self.time_series = Line2D(x, y, **kwargs)
        self.axes.add_line(self.time_series)

        glider_spec = dict(linewidth=0.8, linestyle="--", color="black")
        self.glider = Line2D([x[0], x[0]], [-(10**20), 10**20], **glider_spec)
        self.axes.add_line(self.glider)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        tc = self.get_time_current()
        x = np.array([tc, tc])
        self.glider.set_xdata(x)

    def zoom(self):
        x, y = self.time_series.get_data()
        xlim = [x.min(), x.max()]
        ylim = [y.min(), y.max()]
        self.axes.set_xlim(xlim)
        self.axes.set_ylim(ylim)


class HovmollerGlider(Visual):
    def __init__(
        self,
        axes,
        extractor,
        expression,
        location,
        time=None,
        shading="patch",
        **kwargs,
    ):
        self.location = location
        self.time = time

        # We subset the dataset to get the model time
        # This could be handled better when we do a full refactor.
        if isinstance(extractor, FvTimeSeries):
            self.extractor_type = "FvTimeSeries"
            ds = extractor._subset_dataset(location, time)

            self._times = ds["Time"].values
            self._nt = self._times.shape[0]
            if self._nt < 1:
                raise ValueError("Requested times do not intersect model result")

        # Spatial model result logic
        elif isinstance(extractor, FvExtractor):
            self.extractor_type = "FvExtractor"
            ds = extractor._subset_dataset(time)

            self._times = ds["Time"].values
            self._nt = self._times.shape[0]
            if self._nt < 1:
                raise ValueError("Requested times do not intersect model result")

            # Recurse FvExtractor with the "cut" down dataset
            extractor = FvExtractor(ds)
            self.location = extractor.get_cell_index(*location)
            self.NL = np.squeeze(extractor.nz[self.location])
        else:
            raise ValueError("Unrecognised `extractor` type, check arguments")

        super(HovmollerGlider, self).__init__(axes, extractor, expression, **kwargs)

    @property
    def time_vector(self):
        # Override time_vector for this method, because FvTimeSeries is inflexible.
        return self._times

    def __get_data__(self):

        # We need to pull data differently depending on FvExtractor or FvTimeSeries.
        # ToDO: Refactor this to be handled internally by FvExtractor or FvTimeSeries
        if self.extractor_type == "FvTimeSeries":
            args = (self.expression, self.location)
            raw_data = self.extractor.get_raw_data(*args, time=self.time)

        elif self.extractor_type == "FvExtractor":
            raw_data = np.zeros((self.NL, self.time_vector.shape[0]), dtype=np.float32)
            cell_index_3d = self.extractor.idx2 == self.location

            for i in tqdm(range(self.time_vector.shape[0])):
                args = (self.expression, i)
                raw_data[:, i] = self.extractor.get_raw_data(*args)[cell_index_3d]

        return raw_data.ravel("F")

    def __prep_graphics_obj__(self, **kwargs):
        if self.extractor_type == "FvTimeSeries":
            self.mesh = self.extractor.get_geometry(self.location, time=self.time)
        elif self.extractor_type == "FvExtractor":
            self.mesh = self.extractor._get_profile_geometry(
                self.location, time=self.time
            )

        self.mesh.node_x = mdates.date2num(pd.to_datetime(self.mesh.node_x))
        node_x = self.mesh.node_x[self.mesh.cell_node]
        node_y = self.mesh.node_y[self.mesh.cell_node]
        verts = np.dstack((node_x, node_y))

        self.patch = PolyCollection(verts, array=self.__get_data__(), **kwargs)
        self.axes.add_collection(self.patch)

        glider_spec = dict(linewidth=0.8, linestyle="--", color="black")
        self.glider = Line2D(
            self.time_vector[[0, 0]], [-(10**20), 10**20], **glider_spec
        )
        self.axes.add_line(self.glider)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        tc = self.get_time_current()
        x = np.array([tc, tc])
        self.glider.set_xdata(x)

    def zoom(self):
        xlim = [self.mesh.node_x.min(), self.mesh.node_x.max()]
        ylim = [self.mesh.node_y.min(), self.mesh.node_y.max()]
        self.axes.set_xlim(xlim)
        self.axes.set_ylim(ylim)


# --------------------------------------------- Particle Tracking Objects ----------------------------------------------
class ParticlesScatter(Visual):
    """
    Class for dynamic visualization of particle tracking model results as collection of patches

    Parameters
    ----------
    axes : matplotlib.pyplot.Axes
        Axes object to display/render the graphics object
    extractor : tfv.particles.FvParticles
        Extractor object which is extracting data
    expression : string
        Expression used to color the particles
    datum : {'sigma', 'depth', 'height', 'elevation'}
        Vertical datum applied for particle selection
    limits : tuple
        Vertical limits (z1, z2) applied for particle selection.
    show : dict
        Expression used to select particles for display (works on top of vertical selection)
    show_method : str
        String either 'any' or 'all' applied to the show dictionary. Equivilent to OR or AND boolean.
    highlight : dict
        Expression used to highlight particles
    highlight_method : str
        String either 'any' or 'all' applied to the highlight dictionary. Equivilent to OR or AND boolean.
    scale : float
        Number used to scale marker size (this is in map units i.e metres or degrees)
    shape : {'tri','square','o','star','diamond'}
        Shape of marker

    Other Parameters
    ----------------
    zorder : integer
        Layer order in which graphics object will be rendered (0 is bottom/first)
    cmap : matplotlib.colors.LinearSegmentedColormap
        Colormap object for mapping normalized data (0 - 1) to rgb colors
    norm : matplotlib.colors.BoundaryNorm
        Normalization object for normalizing raw data to (0 - 1) based on (min, max)
    clim : tuple
        Colour limits of the underlying matplotlib.collections.PatchCollection object (min, max)
    edgecolor : string
        Sets the edge colouring of the underlying matplotlib.collections object
    facecolor : string
        Sets the face colouring of the underlying matplotlib.collections object
    antialiased : bool
        Sets the antialiasing state for rendering the underlying matplotlib.collections object
    alpha : float
        Sets the transparencies of the underlying matplotlib.collections object
    """

    def __init__(
        self,
        axes,
        extractor,
        expression=None,
        datum=None,
        limits=None,
        show=None,
        show_method="any",
        highlight=None,
        highlight_method="any",
        track=0,
        scale=0.001,
        shape="tri",
        **kwargs,
    ):
        self.datum = datum
        self.limits = limits
        self.track = track
        self.scale = scale
        self.shape = shape

        # Used to filter by STATUS or GroupID
        self.show = show
        self.show_method = show_method

        # Used to filter by groupID
        self.highlight = highlight
        self.highlight_method = highlight_method

        # Link to underlying xarray object

        # if show is not None:
        #     self.show = Expression(show)
        # else:
        #     self.show = show
        # if highlight is not None:
        #     self.highlight = Expression(highlight)
        # else:
        #     self.highlight = highlight

        # Call initialize method of super class
        super(ParticlesScatter, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        return self.extractor.get_raw_data(self.expression, self._time_index)

    def __prep_graphics_obj__(self, **kwargs):
        # Initialize dimensionless shape
        pi = np.pi
        n = None
        r = pi / 2

        shape = self.shape.lower()
        if shape in ["triangle", "tri"]:
            n = 3
        elif shape == "square":
            n = 4
        elif shape in ["circle", "o"]:
            n = 50
        elif shape in ["diamond", "d"]:
            n = 4
            r = 0
        elif shape == "star":
            rad = np.linspace(0, 2 * pi, 6) - pi / 5 - r
            rad = rad[1, 3, 5, 2, 4, 1]
            self.shape_x = np.cos(rad)
            self.shape_y = np.sin(rad)
        else:
            pass

        if n is not None:
            rad = np.linspace(0, 2 * pi, n + 1) - pi / n - r
            self.shape_x = np.cos(rad)
            self.shape_y = np.sin(rad)

        node_x = 0 + self.scale * self.shape_x
        node_y = 0 + self.scale * self.shape_y

        xy = np.dstack((node_x, node_y))
        self.patch = PolyCollection(xy, **kwargs)

        # Add the graphics object to axes
        self.axes.add_collection(self.patch)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        # Get logical index of particles to show based on self.show expression
        if self.show is None:
            show_lgi = np.ones((self.extractor.np,), dtype=np.bool_)
        else:
            # show_lgi = self.extractor.get_raw_data(self.show, self._time_index)

            log = []
            for k, v in self.show.items():
                if any([isinstance(v, x) for x in [float, int]]):
                    log.append(v == self.extractor.get_raw_data(k, self._time_index))
                elif any([isinstance(v, x) for x in [list, tuple]]):
                    l = np.any(
                        [
                            vi == self.extractor.get_raw_data(k, self._time_index)
                            for vi in v
                        ],
                        axis=0,
                    )
                    log.append(l)
                else:
                    raise ValueError(
                        "Expected `show` dictionary to contain only int/float or list/tuple criteria"
                    )

            if self.show_method == "any":
                show_lgi = np.any(log, axis=0)
            elif self.show_method == "all":
                show_lgi = np.all(log, axis=0)
            else:
                raise ValueError("`show_method` must be either `all` or `any`")

        # Apply additional elevation & inactivity filters
        if self.datum is None and self.limits is None:
            # Get valid particles based on mask only
            valid_lgi = np.invert(self.extractor.get_mask_vector(self._time_index))
        else:
            # Get valid particles based elevation filter (mask applied in get_vertical selection)
            valid_lgi = self.extractor.get_vertical_selection(
                self._time_index, self.datum, self.limits
            )

        # Update the 'show' logical index
        show_lgi = show_lgi & valid_lgi

        # Count number to show
        ns = np.sum(show_lgi)

        # Plot the particles
        if ns != 0:
            # Get logical index of particles to highlight
            if self.highlight is None:
                # Default to highlighting none of the shown particles
                highlight_lgi = np.zeros((ns,), dtype=np.bool_)
            else:
                # Get highlight logical index (sub setting with the 'show' lgi)
                # highlight_lgi = np.zeros((ns,), dtype=np.bool_)
                log = []
                for k, v in self.highlight.items():
                    if any([isinstance(v, x) for x in [float, int]]):
                        log.append(
                            v == self.extractor.get_raw_data(k, self._time_index)
                        )
                    elif any([isinstance(v, x) for x in [list, tuple]]):
                        l = np.any(
                            [
                                vi == self.extractor.get_raw_data(k, self._time_index)
                                for vi in v
                            ],
                            axis=0,
                        )
                        log.append(l)
                    else:
                        raise ValueError(
                            "Expected `highlight` dictionary to contain only int/float or list/tuple criteria"
                        )

                if self.highlight_method == "any":
                    highlight_lgi = np.any(log, axis=0)[show_lgi]
                elif self.highlight_method == "all":
                    highlight_lgi = np.all(log, axis=0)[show_lgi]
                else:
                    raise ValueError("`highlight_method` must be either `all` or `any`")

            highlight_lgi[0] = False  # Stops from highlighting all particles (bug)
            nh = np.sum(highlight_lgi)  # Count number to highlight

            # Update patch faces (sub setting with the 'show' lgi)
            x = self.extractor.get_raw_data("x", self._time_index)[show_lgi]
            y = self.extractor.get_raw_data("y", self._time_index)[show_lgi]

            node_x = x.reshape(x.size, 1) + self.scale * self.shape_x
            node_y = y.reshape(y.size, 1) + self.scale * self.shape_y

            xy = np.dstack((node_x, node_y))
            self.patch.set_verts(xy)

            # Update colours
            if self.expression is None:
                # Get face colours
                c = self.patch.get_facecolor()[0]
                face_colours = np.tile(c, (ns, 1))

                # Finish highlighting with yellow
                y = np.array([255, 255, 0.0, 255.0]) / 255
                face_colours[highlight_lgi, :] = np.tile(y, (nh, 1))

                # Set face colours
                self.patch.set_facecolor(face_colours)

                # Get edge colours & set edge colors
                c = self.patch.get_edgecolor()
                if c.size > 0:
                    # Set edge colours
                    edge_colours = np.tile(c[0], (ns, 1))
                    self.patch.set_edgecolor(edge_colours)
            else:
                # Get data relating to self.expression (sub setting with the 'show' lgi)
                data = self.extractor.get_raw_data(self.expression, self._time_index)[
                    show_lgi
                ]

                # Get face colours
                norm = self.patch.norm(data)
                face_colours = self.patch.cmap(norm)

                # Finish highlighting
                y = np.array([255, 255, 0.0, 255]) / 255
                face_colours[highlight_lgi, :] = np.tile(y, (nh, 1))

                # Set face colours
                self.patch.set_facecolor(face_colours)

                # Get & set edge colours
                c = self.patch.get_edgecolor()
                if c.size > 0:
                    # Set edge colours
                    edge_colours = np.tile(c[0], (ns, 1))
                    self.patch.set_edgecolor(edge_colours)
        else:
            node_x = np.nan + self.scale * self.shape_x
            node_y = np.nan + self.scale * self.shape_y

            xy = np.dstack((node_x, node_y))
            self.patch.set_verts(xy)

    def zoom(self):
        pass


class ParticlesHeat(Visual):
    def __init__(
        self, axes, extractor, expression, datum="sigma", limits=(0, 1), **kwargs
    ):
        self.datum = datum
        self.limits = limits

        # Call initialize method of super class
        super(ParticlesHeat, self).__init__(axes, extractor, expression, **kwargs)

    def __get_data__(self):
        args = (self._time_index, self.datum, self.limits, self.count)

        return self.extractor.get_particle_density(*args)

    def __prep_graphics_obj__(self, **kwargs):
        # Pop key word arguments which are not used by the graphics object
        self.count = kwargs.pop("count", 10000)
        self.index = np.arange(
            0, self.extractor.np, np.ceil(self.extractor.np / self.count)
        ).astype(dtype=np.int32)

        x = self.extractor.get_particle_data("x", self._time_index)[self.index]
        y = self.extractor.get_particle_data("y", self._time_index)[self.index]

        # Instantiate graphics object with no data, data will be added on draw event automatically
        self.sca = self.axes.scatter(x, y, **kwargs)

    def __static_update__(self):
        pass

    def __dynamic_update__(self):
        x = self.extractor.get_particle_data("x", self._time_index)[self.index]
        y = self.extractor.get_particle_data("y", self._time_index)[self.index]
        data = self.__get_data__()

        self.sca.set_offsets(np.column_stack((x, y)))
        self.sca.set_array(data)

    def zoom(self):
        pass


# ------------------------------------------------ Delta Visual Objects ------------------------------------------------
class DeltaSheetPatch(SheetPatch):
    """
    Class for dynamic visualization of model result sheet extract differences as collection of patches

    Arguments
    ---------
    :param axes -- object | Axes object
    :param extractor -- tuple | Extractor objects (base, developed)
    :param expression -- string | Expression that defines variable

    Keyword Arguments
    -----------------
    :param datum -- string | Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    :param limits -- tuple | Vertical depth-averaging limits relative to vertical datum.

    Returns
    -------
    :param sheet -- object | DeltaSheetPatch instance

    Examples
    --------
    >> base_xtr = FvExtractor('my_file_base.nc')
    >> dev_xtr = FvExtractor('my_file_developed.nc')
    >> diff_sheet = DeltaSheetPatch(axes, (base_xtr, dev_xtr), 'H')
    """

    def __init__(
        self, axes, extractors, expression, datum="sigma", limits=(0, 1), **kwargs
    ):
        # Store multiple extractor objects
        self.extractors = extractors

        # Initialize as super class
        super(DeltaSheetPatch, self).__init__(
            axes, self.extractors[0], expression, datum, limits, **kwargs
        )

    def __get_data__(self):
        self.extractor = self.extractors[0]
        data_1 = super(DeltaSheetPatch, self).__get_data__()

        self.extractor = self.extractors[1]
        data_2 = super(DeltaSheetPatch, self).__get_data__()

        return data_2 - data_1


class DeltaSheetContour(SheetContour):
    """
    Class for dynamic visualization of model result sheet extract differences as contours

    Arguments
    ---------
    :param axes -- object | Axes object
    :param extractor -- tuple | Extractor objects (base, developed)
    :param expression -- string | Expression that defines variable

    Keyword Arguments
    -----------------
    :param datum -- string | Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    :param limits -- tuple | Vertical depth-averaging limits relative to vertical datum.

    Returns
    -------
    :param sheet -- object | DeltaSheetContour instance

    Examples
    --------
    >> base_xtr = FvExtractor('my_file_base.nc')
    >> dev_xtr = FvExtractor('my_file_developed.nc')
    >> diff_sheet = DeltaSheetContour(axes, (base_xtr, dev_xtr), 'H')
    """

    def __init__(
        self, axes, extractors, expression, datum="sigma", limits=(0, 1), **kwargs
    ):
        # Store multiple extractor objects
        self.extractors = extractors

        # Initialize as super class
        super(DeltaSheetContour, self).__init__(
            axes, self.extractors[0], expression, datum, limits, **kwargs
        )

    def __get_data__(self):
        self.extractor = self.extractors[0]
        data_1 = super(DeltaSheetContour, self).__get_data__()

        self.extractor = self.extractors[1]
        data_2 = super(DeltaSheetContour, self).__get_data__()

        return data_2 - data_1


class DeltaSheetVector(SheetVector):
    """
    Class for dynamic visualization of model result sheet extract differences as gridded vector field

    Arguments
    ---------
    :param axes -- object | Axes object
    :param extractor -- tuple | Extractor objects (base, developed)
    :param expression -- string | Expression that defines variable

    Keyword Arguments
    -----------------
    :param datum -- string | Vertical depth-averaging datum i.e sigma, depth, height, elevation, top, bottom.
    :param limits -- tuple | Vertical depth-averaging limits relative to vertical datum.

    Returns
    -------
    :param vector -- object | DeltaSheetVector instance

    Examples
    --------
    >> base_xtr = FvExtractor('my_file_base.nc')
    >> dev_xtr = FvExtractor('my_file_developed.nc')
    >> diff_sheet = DeltaSheetVector(axes, (base_xtr, dev_xtr), ['V_x', 'V_y'])
    """

    def __init__(
        self, axes, extractors, expression, datum="sigma", limits=(0, 1), **kwargs
    ):
        # Store multiple extractor objects
        self.extractors = extractors

        # Initialize as super class
        super(DeltaSheetVector, self).__init__(
            axes, self.extractors[0], expression, datum, limits, **kwargs
        )

    def __get_data__(self):
        self.extractor = self.extractors[0]
        data_1 = super(DeltaSheetVector, self).__get_data__()

        self.extractor = self.extractors[1]
        data_2 = super(DeltaSheetVector, self).__get_data__()

        return data_2[0] - data_1[0], data_2[1] - data_1[1]
