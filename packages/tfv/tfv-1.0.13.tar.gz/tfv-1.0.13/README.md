# TFV
tfv is the TUFLOW FV Python Toolbox for post-processing results from [TUFLOW FV](https://www.tuflow.com/Tuflow%20FV.aspx), TUFLOW's flexible mesh hydrodynamic (1D, 2D and 3D), sediment transport, water quality and particle tracking modelling software. 

## Installation
Users are recommended to install tfv using a pre-configured tfv-workspace Conda environment. Step-by-step setup instructions are provided on the [TUFLOW FV Python Toolbox Wiki Page](https://fvwiki.tuflow.com/index.php?title=TUFLOW_FV_Python_Toolbox).

Alternatively, the tfv package is available via the Python Package Index ([PyPi](https://pypi.org/project/tfv/)) or [Conda Forge](https://anaconda.org/conda-forge/tfv).

To install tfv from the conda command line tool:

```
conda install -c conda-forge tfv
```

To install tfv using pip:

```
python -m pip install tfv
```

*Note: The latest version has been built and tested on Python 3.9 to 3.13*.

### Dependencies
The tfv package depends on the following core packages:

```
    numpy>=1.24.0
    matplotlib>=3.7.0
    netCDF4>=1.6.3
    xarray>=2023.1.0
    dask>=2023.1.0
    scipy>=1.10.0
    tqdm>=4.65.0
    pyproj>=3.5.0
    geopandas>=0.13.0
    shapely>=2.0.0
    rioxarray>=0.13.0
    ipywidgets>=8.0.0
    ipympl>=0.9.0
```

These will be automatically installed or updated as part of the tfv installation.


## Tutorials, Documentation & Support
The data download package available via the [TUFLOW FV Python Toolbox Wiki Page]((https://fvwiki.tuflow.com/index.php?title=TUFLOW_FV_Python_Toolbox) includes working copies of the example tutorial and gallery notebooks. These notebooks can be previewed on the [tfvreadthedocs Example Page](https://tfv.readthedocs.io/en/latest/examples/index.html).
The API reference is provided via [tfvreadthedocs](https://tfv.readthedocs.io/en/latest/api_reference/index.html).

For support contact [TUFLOW Support](mailto:support@tuflow.com).

## License
This project is licensed under the MIT License - see the [LICENSE.txt](https://gitlab.com/TUFLOW/tfv/blob/master/LICENSE) file for details
