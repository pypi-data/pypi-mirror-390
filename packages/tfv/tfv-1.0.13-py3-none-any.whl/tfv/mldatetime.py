"""MATLAB style date and time functions"""

import datetime as dt
import numpy as np


def datetime(in_array, fmt='%d/%m/%Y %H:%M:%S'):
    """Converts date numbers or date strings to python datetime objects"""

    # convert input to np.array
    in_array = np.array(in_array, ndmin=1)

    # initialize conversion logic
    from_str = False
    from_flt = False
    from_int = False

    # determine conversion logic
    arr_type = in_array.dtype.type
    if arr_type is np.str_:
        from_str = True
    elif arr_type is np.float64:
        from_flt = True
    elif arr_type is np.int32:
        from_int = True

    # determine output array shape & size
    arr_shape = in_array.shape
    if from_int:
        if len(arr_shape) > 1:
            arr_shape = arr_shape[:-1]
        else:
            arr_shape = (1,)
    arr_size = int(np.prod(arr_shape))

    # flatten the input array
    if from_int:
        in_array = in_array.reshape((arr_size, in_array.shape[-1]))
    else:
        in_array = in_array.flatten()

    # initialize output array
    out_array = np.empty((arr_size,), dtype=np.object)

    # if from string -> datetime
    if from_str:
        for ii in range(arr_size):
            out_array[ii] = dt.datetime.strptime(in_array[ii], fmt)

    # if from float -> datetime
    if from_flt:
        epoch = dt.datetime(1970, 1, 1)
        in_array = in_array.astype(np.float64)
        for ii in range(arr_size):
            delta = dt.timedelta(seconds=in_array[ii])
            out_array[ii] = epoch + delta

    # if from int -> datetime
    if from_int:
        for ii in range(arr_size):
            out_array[ii] = dt.datetime(*list(in_array[ii]))

    # reshape the output array
    out_array = out_array.reshape(arr_shape)

    # handle output
    if out_array.size == 1:
        return out_array[0]
    else:
        return out_array


def datestr(in_array, fmt='%d/%m/%Y %H:%M:%S'):
    """Converts python datetime objects or date numbers to date strings"""

    # convert input to np.array
    in_array = np.array(in_array, ndmin=1)

    # convert everything to datetime
    arr_type = in_array.dtype.type
    if arr_type is not np.object_:
        in_array = datetime(in_array)
        in_array = np.array(in_array, ndmin=1)

    # get the array shape and size
    arr_shape = in_array.shape
    arr_size = np.prod(arr_shape)

    # flatten the input array
    in_array = in_array.flatten()

    # initialize output array
    str_check = in_array[0].strftime(fmt)
    d_type = '<U{:d}'.format(len(str_check))
    out_array = np.empty((arr_size,), dtype=d_type)

    # convert datetime to string
    for ii in range(in_array.size):
        out_array[ii] = in_array[ii].strftime(fmt)

    # reshape the output array
    out_array = out_array.reshape(arr_shape)

    # handle output
    if out_array.size == 1:
        return out_array[0]
    else:
        return out_array


def datenum(in_array, fmt='%d/%m/%Y %H:%M:%S'):
    """Converts python datetime objects or date strings to date numbers"""

    # convert input to np.array
    in_array = np.array(in_array, ndmin=1)

    # convert everything to datetime
    arr_type = in_array.dtype.type
    if arr_type is not np.object_:
        in_array = datetime(in_array, fmt=fmt)
        in_array = np.array(in_array, ndmin=1)

    # get the array shape and size
    arr_shape = in_array.shape
    arr_size = np.prod(arr_shape)

    # flatten the input array
    in_array = in_array.flatten()

    # initialize the output array
    out_array = np.empty((arr_size,), dtype=np.float64)

    # Convert datetime to number
    epoch = dt.datetime(1970, 1, 1)
    for ii in range(in_array.size):
        delta = in_array[ii] - epoch
        out_array[ii] = delta.total_seconds()

    # reshape the output array
    out_array = out_array.reshape(arr_shape)

    # handle output
    if out_array.size == 1:
        return out_array[0]
    else:
        return out_array


def datevec():
    """Python implementation of datevec"""
    pass


def convtime(in_array, to='py'):
    """Converts tuflow time to python time"""

    # Define epoch relative to python time
    fv_epoch = datenum((1990, 1, 1))

    # Convert input to datenum
    in_array = datenum(in_array)

    if to == 'py':
        return in_array*3600 + fv_epoch
    elif to == 'fv':
        return (in_array - fv_epoch)/3600


def timeit(function_call):

    name = function_call.__name__
    message = '{} took {}s to execute'

    def wrapper(*args, **kwargs):
        ts = dt.datetime.now().timestamp()
        output = function_call(*args, **kwargs)
        te = dt.datetime.now().timestamp()
        print(message.format(name, te - ts))

        return output

    return wrapper
