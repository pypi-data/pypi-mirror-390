import unittest
import xarray as xr
import numpy as np
import tfv.xarray
import matplotlib.pyplot as plt
from pathlib import Path

path = Path(__file__).parent / "data"
fv = xr.open_dataset(path / "HYD_002_mini.nc", decode_times=False).tfv


class TestTfvDomain(unittest.TestCase):
    def test_get_sheet_H_numcells2d(self):
        """Test that get sheet runs with very simple defaults and a 2D var"""
        dims = fv.get_sheet("H")["H"].shape
        self.assertEqual(dims[1], fv.sizes["NumCells2D"])

    def test_get_sheet_V_numcells2d(self):
        """Test that get sheet runs with the magic 'V' variable"""
        dims = fv.get_sheet("V")["V"].shape
        self.assertEqual(dims[1], fv.sizes["NumCells2D"])

    def test_get_sheet_TEMP_time_integer_slice(self):
        """Test that get sheet runs with integer slicing"""
        tslc = slice(1, 3)
        ts = fv._obj.isel(Time=tslc).sizes["Time"]  # Correct behaviour

        # Check func behaviour
        dims = fv.get_sheet("TEMP", time=tslc)["TEMP"].shape
        self.assertEqual(dims[0], ts)

    def test_get_sheet_TEMP_time_single_time_integer(self):
        """Test that get sheet runs with single integer time"""
        # Check func behaviour
        dims = fv.get_sheet("TEMP", time=1)["TEMP"].shape
        self.assertEqual(dims[0], 1)

    # def test_get_sheet_TEMP_time_single_time_datestr(self):
    # ''' Test that get sheet runs with a hard datestr '''
    ## Check func behaviour
    # dims = fv.get_sheet('TEMP', time='2011-02-01T02:00:00.263494800')['TEMP'].shape
    # self.assertEqual(dims[0], 1)

    def test_get_statistics_single_stat(self):
        """Test a single statistic"""
        # Check func behaviour
        dims = fv.get_statistics("mean", "V")["V_mean"].shape
        self.assertEqual(dims[0], 1)

    def test_get_statistics_several_stats(self):
        """Test several statistics"""
        # Check func behaviour
        stats = ["mean", "p95", "p20", "sum"]
        var = "SAL"

        fv2d = fv.get_statistics(stats, var)

        svar = f"{var}_{stats[2]}"
        timecheck = fv2d.sizes["Time"] == 1
        varcheck = len(fv2d.variables) == len(stats)
        dimcheck = fv2d[svar].shape[1] == fv.sizes["NumCells2D"]

        self.assertTrue(timecheck & varcheck & dimcheck)

    def test_get_timeseries(self):
        """Test get timeseries with defaults, multi locations."""
        # Check func behaviour
        locs = dict(pt1=(159.09380193, -31.39236190), pt2=(159.11004448, -31.39781102))
        vars = ("H", "V", "V_x", "SAL")

        ts = fv.get_timeseries(vars, locs)
        tsx = fv.get_timeseries("V", locs)  # Test with 1 variable as bonus

        timecheck = ts.sizes["Time"] == fv.sizes["Time"]
        varcheck = len(ts.data_vars) == len(vars)
        dimcheck = ts.sizes["Location"] == len(locs)

        self.assertTrue(timecheck & varcheck & dimcheck)

    def test_get_timeseries_with_dave_opts(self):
        """Test get timeseries with depthaveraging options"""
        # Check func behaviour
        locs = dict(
            pt1=(159.09380193, -31.39236190),
        )
        vars = ("H", "SAL")
        datum = "height"
        limits = (0, 2.42)
        agg = "max"

        ts = fv.get_timeseries(vars, locs, datum=datum, limits=limits, agg=agg)

        timecheck = ts.sizes["Time"] == fv.sizes["Time"]
        varcheck = len(ts.data_vars) == len(vars)
        dimcheck = (
            "Location" not in ts.dims
        )  # Only one location, should not be present!

        self.assertTrue(timecheck & varcheck & dimcheck)

    def test_get_profile_variables(self):
        """Test get profile a set of variables"""
        locs = dict(
            pt1=(159.09380193, -31.39236190),
        )
        vars = ("H", "V", "V_x", "SAL")

        prof = fv.get_profile(locs, variables=vars)

        # Check all variables made it through
        vars_all = len(prof.data_vars) == len(vars) + 5
        vars_in = all([x in prof.data_vars for x in vars])

        self.assertTrue(all([vars_all, vars_in]))

    def test_get_curtain_latlon(self):
        """Test to get a curtain dataset from a polyline"""
        polyline = np.loadtxt(path / "HYD002_Polyline.txt")
        curt = fv.get_curtain(polyline, ["V_x", "V", "TEMP"])
        self.assertEqual(curt.sizes["Time"], fv.sizes["Time"])

    def test_plot_crs_curtain_latlon(self):
        """Test to plot a curtain dataset from a polyline"""
        polyline = np.loadtxt(path / "HYD002_Polyline.txt")

        # Plot 1 - SIMPLE CHAINAGE METHOD!!
        curt_1 = fv.plot_curtain(polyline, "V", 1)
        chn_1 = curt_1.geo[0]
        self.assertLess(chn_1.max(), 7585)

        # Plot 2 - CRS IS PROVIDED, USE PYPROJ TO ACCURATE CALCULATE CHAINAGE
        crs = 32757
        curt_2 = fv.plot_curtain(polyline, "V", 1, crs=crs)
        chn_2 = curt_2.geo[0]

        # Compare against a UTM line drawn in QGIS
        self.assertAlmostEqual(chn_2.max(), 7585, 0)

    def test_plot_curtain_cartesian(self):
        """Test to plot a curtain dataset from a polyline"""
        polyline = np.loadtxt(path / "Cudgen_Creek_Polyline.txt")
        fvc = xr.open_dataset(path / "Cudgen_Creek_example_cartesian.nc").tfv

        # Plot 1 - SIMPLE CHAINAGE METHOD!!
        curt = fvc.plot_curtain(polyline, "V", 1)
        chn = curt.geo[0]

        # Compare against the actual polyline drawn in QGIS
        self.assertAlmostEqual(chn.max(), 5814, 0)

    def test_get_profile_dims(self):
        """Test get profile a set of variables"""
        locs = dict(
            pt1=(159.09380193, -31.39236190),
        )
        vars = ("H", "V", "V_x", "SAL")
        nt = 2
        prof = fv.get_profile(locs, time=slice(nt), variables=vars)

        dims = all(
            [
                "N1" in prof.dims,  # to match TUFLOW FV output
                "NumLayers" in prof.dims,  # 3D model should have this!
                "NumLayerFaces" in prof.dims,  # Lfz as standard
            ]
        )

        shp = all(
            [
                prof.sizes["Time"] == nt,
            ]
        )
        self.assertTrue(all([dims, shp]))

    def test_plot_defaults_H(self):
        """Test whether the default plot picks the correct time, and runs without issue."""
        var = "H"
        time = "2011-02-01 02:00"

        fv.plot(var, time)
        ax = plt.gca()

        self.assertEqual(time, ax.get_title())

    def test_plot_defaults_V(self):
        """Test whether the default plot works with the magic V var, and auto-labels"""
        var = "V"
        vlbl = "current speed (m s^-1)"  # Auto label should assign this.
        time = "2011-02-01 02:30"

        fv.plot(var, time)
        fig = plt.gcf()

        # Loop through children to get colorbar
        for c in fig.get_children():
            if hasattr(c.axes, "get_label"):
                if c.axes.get_label() == "<colorbar>":
                    lbl = c.axes.get_ylabel()

        self.assertEqual(vlbl, lbl)

    def test_get_contours_gdf(self):
        gdf = fv.get_contours([0.1, 0.2, 0.3], "V", time=1, datum="depth")
        self.assertTrue(0.2 in gdf["level"].values)

    def test_sheet_2d_grid_defaults(self):
        """Test if a sheet grid is made with pre defaults"""
        dg = fv.get_sheet_grid()

        # Salinity should be in this sheet grid! Plot it.
        dg["SAL"][2].plot()

        # Check all variables made it through
        vars_all = len(dg.data_vars) == len(fv.variables)
        vars_in = all([x in dg.data_vars for x in fv.variables])

        self.assertTrue(all([vars_all, vars_in]))

    def test_sheet_2d_grid_extended(self):
        """Test if a sheet grid is output with many options"""

        dg = fv.get_sheet_grid(
            time=slice(1),
            variables=["SAL", "VDir", "V"],
            dx=1e-3,
            ny=210,
            method="linear",
            crs=4326,
            datum="height",
            agg="max",
        )

        # Salinity should be in this sheet grid! Plot it.
        dg["SAL"][0].plot()

        self.assertEqual(dg["latitude"].shape[0], 210)
        self.assertEqual(dg["longitude"].shape[0], 59)
        self.assertEqual(dg.attrs["crs"], 4326)

    def test_sheet_2d_grid_cartesian(self):
        """Test a cartesian sheet grid output"""

        fvc = xr.open_dataset(path / "Cudgen_Creek_example_cartesian.nc").tfv

        dg = fvc.get_sheet_grid(
            time=slice(1),
            variables=["SAL", "VDir", "V"],
            dx=50,
            ny=120,
            method="linear",
            crs=7856,
            datum="height",
            agg="max",
        )

        # VDir should be in this sheet grid! Plot it.
        dg["VDir"][0].plot()

        self.assertEqual(dg["xp"].shape[0], 240)
        self.assertEqual(dg["yp"].shape[0], 120)
        self.assertEqual(dg.attrs["crs"], 7856)

    def test_profile_fvtimeseries_load(self):
        ds = xr.open_dataset(
            (path / "HYD_001_time_series.nc").as_posix(), decode_times=False
        )
        ts = ds.tfv

        dsx = ts.get_location("Point_5")
        tsx = ts.get_timeseries(["Point_1", "Point_3"], ["V", "TEMP"], datum="height")
        self.assertEqual(dsx.attrs["Label"], "Point_5")
        self.assertEqual(tsx.attrs["Datum"], "height")


if __name__ == "__main__":
    unittest.main()
