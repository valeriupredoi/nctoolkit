import nctoolkit as nc

nc.options(lazy=True)
import pandas as pd
import xarray as xr
import os, pytest


class TestAnomaly:
    def test_relative(self):
        assert nc.session.session_info["parallel"] == False
        n = len(nc.session_files())
        assert n == 0
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        tracker.annual_anomaly(baseline=[1970, 1979])

        tracker.annual_anomaly(baseline=[1970, 1979], metric="relative", window=10)
        tracker.spatial_mean()
        tracker.subset(years=1979)

        x = tracker.to_xarray().sst.values[0][0][0].astype("float")
        assert x == 1.0
        n = len(nc.session_files())
        del tracker
        assert n == 1
        assert nc.session.session_info["parallel"] == False
        print(nc.session_files())
        n = len(nc.session_files())
        assert n == 0

    def test_error1(self):
        #print session files
        print(nc.session_files())
        assert nc.session.session_info["parallel"] == False
        n = len(nc.session_files())
        assert n == 0
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.monthly_anomaly(baseline="x")
        with pytest.raises(TypeError):
            tracker.annual_anomaly(baseline="x")
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data()
        with pytest.raises(ValueError):
            tracker.annual_anomaly(baseline=[1970, 1979])

        with pytest.raises(ValueError):
            tracker.monthly_anomaly(baseline=[1970, 1979])
        n = len(nc.session_files())
        assert n == 0
        assert nc.session.session_info["parallel"] == False

    def test_error2(self):
        assert nc.session.session_info["parallel"] == False
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.monthly_anomaly(baseline="x")
        n = len(nc.session_files())
        assert n == 0
        assert nc.session.session_info["parallel"] == False

    def test_error3(self):
        ff = "data/sst.mon.mean.nc"
        assert nc.session.session_info["parallel"] == False
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.annual_anomaly(baseline=[1, 2, 3])
        n = len(nc.session_files())
        assert n == 0
        assert nc.session.session_info["parallel"] == False

    def test_error4(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.monthly_anomaly(baseline=[1, 2, 3])
        n = len(nc.session_files())
        assert n == 0

    def test_error5(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.annual_anomaly(baseline=[1, "x"])
        n = len(nc.session_files())
        assert n == 0

    def test_error6(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.annual_anomaly(baseline=["x", "x"])
        n = len(nc.session_files())
        assert n == 0

    def test_error7(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.annual_anomaly(baseline=[1990, 1980])
        n = len(nc.session_files())
        assert n == 0
        del tracker
        assert len(nc.session.get_safe()) == 0

    def test_error8(self):
        assert len(nc.session.get_safe()) == 0
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.annual_anomaly(baseline=[1000, 1990])
            # tracker.annual_anomaly(baseline=[1990, 1980])
        n = len(nc.session_files())
        n == 0
        assert len(nc.session.get_safe()) == 1
        del tracker
        assert len(nc.session.get_safe()) == 0

    def test_error9(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.annual_anomaly(baseline=[1980, 1990], metric="x")
        n = len(nc.session_files())
        assert n == 0

    def test_error10(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.monthly_anomaly(baseline=[1, "x"])
        n = len(nc.session_files())
        assert n == 0

    def test_error11(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.monthly_anomaly(baseline=["x", "x"])
        n = len(nc.session_files())
        assert n == 0

    def test_error12(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.monthly_anomaly(baseline=[1990, 1980])
        n = len(nc.session_files())
        assert n == 0

    def test_error13(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.monthly_anomaly(baseline=[1000, 1990])
        n = len(nc.session_files())
        assert n == 0

    def test_empty(self):
        n = len(nc.session_files())
        assert n == 0

    def test_error_window(self):
        ff = "data/sst.mon.mean.nc"
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.annual_anomaly(baseline=[1970, 1979], window="x")
        with pytest.raises(TypeError):
            tracker.annual_anomaly(baseline=[1970, 1979], window=0)
