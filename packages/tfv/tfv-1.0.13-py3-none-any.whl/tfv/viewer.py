"""A module defining all objects used to visualise model result data extracts"""
import os
import time
import numpy as np
from tfv.mldatetime import *

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colorbar import Colorbar
from matplotlib.text import Text

# Check to see if PyQt5 is available
import_err_msg = "\n".join([
    "You must additionally install `PyQt5` to use the Viewer module",
    "Please install this using your relevant python package distribution",
    "PyPi - `pip install pyqt5` - https://pypi.org/project/PyQt5/ ",
    "Anaconda - `conda install -c anaconda pyqt` - https://anaconda.org/anaconda/pyqt",
    "Conda-forge - conda install -c conda-forge pyqt` - https://anaconda.org/conda-forge/pyqt"
])

import pkg_resources
try:
    pkg_resources.get_distribution('PyQt5')
except pkg_resources.DistributionNotFound:
    raise ImportError(import_err_msg)
else:
    HAS_PYQT5 = True

if HAS_PYQT5:
    from PyQt5.QtWidgets import QSlider, QWidget, QHBoxLayout, \
                                QVBoxLayout, QLabel, QPushButton
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import Qt

# configure MPL
mpl.use('Qt5Agg')
plt.interactive(True)


class Slider:
    """
    A class for a single slider object placed in the MPL toolbar, built with PyQt5.

    Parameters
    ----------
    figure : tuple
        Size of underlying figure as (width, height) in specified units

    Other Parameters
    ----------------
    range : np.ndarray
        range of values that slider selects from
    step : integer
        The step size of the slider, i.e. how manly values it skips
    wait : float
        The wait time in seconds between each step when in 'play' mode
    format : {'num', 'hms', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y', '%H:%M:%S %d-%m-%Y', ...}
        The slider value display format. Any custom datetime format string can be passed in addition
        to 'num' for the python date time as a number and 'hms' for total hours, minutes and seconds.

    Attributes
    ----------
    value : float
        The current value of the slider
    index : integer
        The current index of the slider
    text : string
        The display text of the slider
    """

    # Constructor functions
    def __init__(self,
                 figure,
                 range=np.arange(100),
                 step=1,
                 wait=0.01,
                 format='num'):
        # protected attributes
        self._figure = figure
        self._range = range

        self._value = None
        self._index = None
        self._text = ''
        self._playing = False
        self._callbacks = []

        # public attributes
        self.step = step
        self.wait = wait
        self.format = format

        # build the user interface
        self.__build_ui__()

        # set defaults
        self.value = 0
        self.index = 0

    def __build_ui__(self):
        """Method to build the User Interface (UI)"""

        # get the navigation widget handle
        nav_widget = self._figure.canvas.parent().children()[1]

        # add a separator to navigation widget
        nav_widget.addSeparator()

        # create and set layout of display widget
        self.display_widget = QWidget()
        self.display_layout = QVBoxLayout()
        self.display_widget.setLayout(self.display_layout)

        # format the display widget and layout
        self.display_widget.setContentsMargins(2, 2, 2, 2)
        self.display_layout.setContentsMargins(2, 2, 2, 2)
        self.display_widget.setMinimumWidth(125)
        self.display_widget.setMaximumWidth(125)

        # add the display widget to the navigation widget
        nav_widget.addWidget(self.display_widget)

        # create and set layout of label widget
        self.label_widget = QLabel(self._text)
        self.label_widget.setAlignment(Qt.AlignCenter)

        # add the label widget to the display layout
        self.display_layout.addWidget(self.label_widget)

        # create the slider widget
        self.slider_widget = QSlider(Qt.Horizontal)

        # format the slider widget
        self.slider_widget.setMinimum(0)
        self.slider_widget.setMaximum(len(self.range) - 1)

        # add the slider widget to the display layout
        self.display_layout.addWidget(self.slider_widget)

        # create and set layout of the buttons widget
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout()
        self.buttons_widget.setLayout(self.buttons_layout)

        # format the buttons widget and layout
        self.buttons_widget.setContentsMargins(2, 2, 2, 2)
        self.buttons_layout.setContentsMargins(2, 2, 2, 2)
        self.buttons_widget.setMinimumWidth(125)
        self.buttons_widget.setMaximumWidth(125)

        # add the buttons widget to the navigation widget
        nav_widget.addWidget(self.buttons_widget)

        # add the _first button
        self.first_button = QPushButton('|<')
        self.first_button.setMinimumWidth(20)
        self.first_button.setMaximumWidth(20)
        self.first_button.setToolTip('First Timestep')
        self.buttons_layout.addWidget(self.first_button)

        # add the previous button
        self.prev_button = QPushButton('<')
        self.prev_button.setMinimumWidth(20)
        self.prev_button.setMaximumWidth(20)
        self.prev_button.setToolTip('Previous Timestep')
        self.buttons_layout.addWidget(self.prev_button)

        # add the _next button
        self.next_button = QPushButton('>')
        self.next_button.setMinimumWidth(20)
        self.next_button.setMaximumWidth(20)
        self.next_button.setToolTip('Next Timestep')
        self.buttons_layout.addWidget(self.next_button)

        # add the _last button
        self.last_button = QPushButton('>|')
        self.last_button.setMinimumWidth(20)
        self.last_button.setMaximumWidth(20)
        self.last_button.setToolTip('Last Timestep')
        self.buttons_layout.addWidget(self.last_button)

        # add the play button
        self.play_button = QPushButton()
        self.play_button.setMinimumWidth(20)
        self.play_button.setMaximumWidth(20)
        self.play_button.setToolTip('Play Through Timesteps')
        self.buttons_layout.addWidget(self.play_button)

        # set the play button icon
        image_path = os.path.dirname(__file__) + "\\icons\\play_button.png"
        self.play_button.setIcon(QIcon(image_path))

        # connect slots to signals
        self.slider_widget.valueChanged.connect(self._changed)
        self.first_button.pressed.connect(self._first)
        self.prev_button.pressed.connect(self._prev)
        self.next_button.pressed.connect(self._next)
        self.last_button.pressed.connect(self._last)
        self.play_button.pressed.connect(self._toggle)

    # Protected member functions
    def _synchronise(self):
        # set the value of the slider widget
        self.slider_widget.setValue(self.index)

        # update the text display above the slider
        if self.format == 'int':
            self._text = str(self.index)
        elif type(self.value) == np.int32:
            self._text = str(self.index)
        else:
            self._text = self.value.strftime(self.format)
        self.label_widget.setText(self._text)

        # pass new value to call backs
        for callback in self._callbacks:
            callback(self.value)

    def _changed(self):
        self.index = self.slider_widget.value()

    def _first(self):
        self.index = 0

    def _prev(self):
        self.index = self.index - self.step

    def _next(self):
        self.index = self.index + self.step

    def _last(self):
        self.index = len(self.range) - 1

    def _toggle(self):
        path = os.path.dirname(__file__)
        if not self._playing:
            # _toggle the icon
            image_path = path + "\\icons\\stop_button.png"
            self.play_button.setIcon(QIcon(image_path))

            # _toggle flag
            self._playing = True

            # switch off interaction
            plt.interactive(False)

            # enter update loop
            while self._playing:
                self._next()
                self._redraw()
                time.sleep(self.wait)
        else:
            # _toggle the icon
            image_path = path + "\\icons\\play_button.png"
            self.play_button.setIcon(QIcon(image_path))

            # _toggle flag
            self._playing = False

            # switch on interaction
            plt.interactive(True)

    def _redraw(self):
        for axes in self._figure.axes:
            # Redraw the only items in frame
            axes.redraw_in_frame()

            # Draw x grid-lines
            x_grid = axes.get_xgridlines()
            for line in x_grid:
                axes.draw_artist(line)

            # Draw y grid-lines
            y_grid = axes.get_ygridlines()
            for line in y_grid:
                axes.draw_artist(line)

        # self.figure.canvas.update()
        self._figure.canvas.update()
        self._figure.canvas.flush_events()

    # Properties
    @property
    def figure(self):
        return self._figure

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, range):
        # set the protected range
        self._range = range

        # update slider limits
        min_val, max_val = 0, len(range) - 1
        self.slider_widget.setMinimum(min_val)
        self.slider_widget.setMaximum(max_val)

        # reset the value
        self.value = self._value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # set the index based on nearest value in range
        if value == 0:
            value = self.range[0]
        self.index = np.argmin(np.abs(self.range - value))

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        # check upper and lower bounds
        min_val, max_val = 0, len(self.range) - 1
        if index > max_val:
            index = max_val
        if index < min_val:
            index = min_val

        if self.index != index or self.value != self.range[index]:
            self._index = index
            self._value = self.range[index]
            self._synchronise()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.label_widget.setText(text)

    # Public member functions
    def connect(self, function):
        """Connect function or handler value _changed event"""
        self._callbacks.append(function)

    def disconnect(self, function):
        """Disconnect function or handler value _changed event"""
        self._callbacks.remove(function)


class Viewer:
    """
    Class to explore/view time varying model result data

    Other Parameters
    ----------------
    size : tuple
        Size of underlying figure as (width, height) in specified units
    units : {'mm', 'cm' or 'm'}
        Figure units
    step : integer
        The step size of the slider, i.e. how manly values it skips
    wait : float
        The wait time in seconds between each step when in 'play' mode
    format : {'num', 'hms', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y', '%H:%M:%S %d-%m-%Y', ...}
        The slider value display format. Any custom datetime format string can be passed in addition
        to 'num' for the python date time as a number and 'hms' for total hours, minutes and seconds.
    display : boolean
        Switch to display current time as text using the specified format. Default True.

    Attributes
    ----------
    figure : matplotlib.pyplot.Figure
        Underlying matplotlib figure object
    time_vector : np.ndarray
        Time vector associated with display
    time_current : np.float64
        Current time of display
    text : string
        Text of the display
    """

    __register__ = list()

    # Constructor function
    def __init__(self,
                 size=(240, 120),
                 units='mm',
                 step=1,
                 wait=0.01,
                 format='%d/%m/%Y %H:%M:%S',
                 display=True):
        """Initializes Viewer object with figure size, figure units & title time format"""

        # add self to the viewer register
        self.__register__.append(self)

        # public attributes
        self.figure = None
        self.size = size
        self.units = units
        self.axes = []

        # protected attributes
        self._slider_bar = None
        self._title_axes = None
        self._title_obj = None

        # set up the MPL figure
        sf_map = {'mm': 12 / 300, 'cm': 12 / 30, 'm': 12 / 0.3}

        sf = sf_map[self.units]
        w = self.size[0] * sf
        h = self.size[1] * sf

        self.figure = plt.figure(figsize=(w, h))

        # add the slider
        self._slider_bar = Slider(self.figure,
                                  step=step,
                                  wait=wait,
                                  format=format)

        # create title axes and add text for title
        rec = [0.30, 0.96, 0.40, 0.04]
        self._title_axes = self.figure.add_axes(rec)
        self._title_axes.xaxis.set_visible(False)
        self._title_axes.yaxis.set_visible(False)
        self._title_axes.set_navigate(False)

        for spine in self._title_axes.spines.values():
            spine.set_color('white')

        self._title_axes.set_xlim(0, 2)
        self._title_axes.set_ylim(0, 2)

        self._title_obj = Text(1,
                               1,
                               '',
                               fontsize=12,
                               horizontalalignment='center',
                               verticalalignment='center')
        self._title_axes._add_text(self._title_obj)

        # connect display text to the slider bar
        self._slider_bar.connect(self._set_text)

        # set text and show_time
        self.text = self._slider_bar.text
        self.show_time = display

    # Properties
    @property
    def time_current(self):
        return self._slider_bar.value

    @time_current.setter
    def time_current(self, time_current):
        self._slider_bar.value = time_current

    @property
    def time_vector(self):
        return self._slider_bar.range

    @time_vector.setter
    def time_vector(self, time_vector):
        # if np.all(self.time_vector == np.arange(100)):
        self._slider_bar.range = time_vector
        # else:
        #     self._slider_bar.range = np.arange(t1, t2 + dt, dt)

    @property
    def step(self):
        return self._slider_bar.step

    @step.setter
    def step(self, step):
        self._slider_bar.step = step

    @property
    def wait(self):
        return self._slider_bar.wait

    @wait.setter
    def wait(self, wait):
        self._slider_bar.wait = wait

    @property
    def time_fmt(self):
        return self._slider_bar.format

    @time_fmt.setter
    def time_fmt(self, time_fmt):
        self._slider_bar.format = time_fmt

    @property
    def text(self):
        return self._slider_bar.text

    @text.setter
    def text(self, text):
        self._title_obj.set_text(text)
        self._slider_bar.text = text

    @property
    def show_time(self):
        return self._title_axes.get_visible()

    @show_time.setter
    def show_time(self, show_time):
        self._title_axes.axes.set_visible(show_time)

    # protected member functions
    def _set_text(self, dummy):
        self.text = self._slider_bar.text

    # Public member functions
    def connect(self, function):
        """Subscribes callback to slider"""
        self._slider_bar.connect(function)

    def disconnect(self, function):
        """Removes callback subscription"""
        self._slider_bar.disconnect(function)

    def print(self, file_path, format='png', dpi=300):
        """
        Prints Viewer objects figure to image file.

        Parameters
        ---------
        file_path : string
            File path to output image file
        format : string
            File format i.e 'png', 'pdf', 'jpg'
        dpi : integer
            Resolution in dots per inch (dpi)
        """

        self.figure.savefig(file_path, format=format, dpi=dpi)

    def animate(self, file_path, ts, te, dt, fps=10, dpi=150):
        """
        Writes animation file for specified time interval.

        Parameters
        ----------
        file_path : string
            File path to output animation
        ts : float
            Start time as python time stamp
        te : float
            End time as python time stamp
        dt : float
            Time increment at which to save frame

        Other Parameters
        ----------------
        fps : integer
            Frames per second
        dpi : integer
            Resolution in dots per inch (dpi)
        """

        # Loop through time
        nt = int((te - ts) / dt) + 1
        writer = FFMpegWriter(fps=fps)
        with writer.saving(self.figure, file_path, dpi):
            for ii in range(nt):
                self.time_current = (ts + ii * dt)
                writer.grab_frame()


class ColourBar(Colorbar):
    """
    A wrapper around the matplotlib colorbar, simplifying for neater plots.

    Parameters
    ----------
    patch : matplotlib.collections.PatchCollection object
        matplotlib object from which to take colour limits and normalization

    Other Parameters
    ----------------
    location : {'left', 'right', 'bottom', 'top'}
        Size of underlying figure as (width, height) in specified units
    offset : float
        Offset from axes as fraction of total figure width or height
    thickness : float
        Thickness of bar as fraction of total figure width or height
    label : string
        String to label the colour bar.
    """

    def __init__(self,
                 patch,
                 location='bottom',
                 offset=0.075,
                 thickness=0.010,
                 label=''):

        # Get target axes handle
        if type(patch).__name__ == 'TriContourSet':
            target = patch.ax
        else:
            target = patch.axes

        if offset > 0:
            offset_1 = offset
            offset_2 = 0
        else:
            offset_1 = 0
            offset_2 = offset

        # Determine rectangles for target axes & colour bar axes
        rec = target.get_position().extents
        if location == 'bottom':
            rec1 = [
                rec[0], rec[1] + offset_1, rec[2] - rec[0],
                rec[3] - rec[1] - offset_1
            ]
            rec2 = [rec[0], rec[1] + offset_2, rec[2] - rec[0], thickness]
        elif location == 'top':
            rec1 = [
                rec[0], rec[1], rec[2] - rec[0], rec[3] - rec[1] - offset_1
            ]
            rec2 = [rec[0], rec[3] - offset_2, rec[2] - rec[0], thickness]
        elif location == 'left':
            rec1 = [
                rec[0] + offset_1, rec[1], rec[2] - rec[0] - offset_1,
                rec[3] - rec[1]
            ]
            rec2 = [rec[0] + offset_2, rec[1], thickness, rec[3] - rec[1]]
        elif location == 'right':
            rec1 = [
                rec[0], rec[1], rec[2] - rec[0] - offset_1, rec[3] - rec[1]
            ]
            rec2 = [rec[2] - offset_2, rec[1], thickness, rec[3] - rec[1]]

        target.set_position(rec1)
        axes = target.figure.add_axes(rec2)

        # Set orientation
        if location == 'bottom' or location == 'top':
            orientation = 'horizontal'
        elif location == 'left' or location == 'right':
            orientation = 'vertical'

        # Initialize Colorbar
        super(ColourBar, self).__init__(axes,
                                        mappable=patch,
                                        orientation=orientation)

        # Finish formatting
        if orientation == 'horizontal':
            axes.xaxis.set_ticks_position(location)
            axes.xaxis.set_label_position(location)
            axes.set_xlabel(label)
        elif orientation == 'vertical':
            axes.yaxis.set_ticks_position(location)
            axes.yaxis.set_label_position(location)
            axes.set_ylabel(label)
