import nctoolkit as nc

nc.options(lazy=True)
import pandas as pd
import xarray as xr
import numpy as np
import os, pytest, pytest


ff = "data/sst.mon.mean.nc"


class TestAddetc:

    def test_rmse(self):
        ds1 = nc.open_data("data/sst.mon.mean.nc", checks=False)
        ds2 = nc.open_data("data/sst.mon.mean.nc", checks=False)
        ds1.subtract(2)
        ds1.rmse(ds2)
        assert np.abs(ds1.to_dataframe().sst.max() - 2.0) < 0.000001
        assert np.abs(ds1.to_dataframe().sst.min() - 2.0) < 0.000001


    def test_dailyts(self):
        ds = nc.open_data("data/hourly/01/*.nc", checks = False)
        ds.set_precision("F64")
        ds.merge("time")
        ds.tmean("day")
        ds.run()
        ds1 = nc.open_data("data/hourly/01/*.nc", checks=False)
        ds1.set_precision("F64")
        ds1.merge("time")
        ds1.subtract(ds)
        ds1.tmean("day")
        ds1.to_dataframe().abs().max()
        assert float(ds1.to_dataframe().abs().max()) < 1e-6

    def test_yearlyts(self): 
        version = nc.cdo_version()
        if nc.utils.version_below(version, "1.9.9") == False:
            ds1 = nc.open_data(ff, checks = False)
            ds2 = nc.open_data(ff, checks = False)
            ds2.tmean("year")
            ds1.subtract(ds2)
            ds1.tmean("year")
            sst_max = ds1.to_dataframe().sst.max()
            sst_min = ds1.to_dataframe().sst.min()

            assert (sst_max < 1e-6) and (sst_min > -1e-6)


            ff1 = "data/2003.nc"
            ds1 = nc.open_data(ff1, checks=False)
            ds2 = nc.open_data(ff1, checks=False)   
            ds1.set_precision("F32")
            ds2.set_precision("F32")
            ds2.tmean("month")
            ds1.subtract(ds2)
            ds1.tmean("month")
            ds1.run()
            sst_max = ds1.to_dataframe().analysed_sst.abs().max()
            assert (sst_max < 1e-4)

            ff1 = "data/2003.nc"
            ff2 = "data/2004.nc"
            ds1 = nc.open_data([ff1, ff2], checks=False)
            ds1.set_precision("F32")
            ds1.merge("time")
            ds2 = nc.open_data(ff1, checks=False)
            ds2.set_precision("F32")
            ds2.tmean("month")
            ds1.subtract(ds2)
            ds1.tmean(["year","month"])

            ds1.subset(year = 2003)

            sst_max = ds1.to_dataframe().analysed_sst.abs().max()

            assert (sst_max < 1e-4)


            ff1 = "data/2003.nc"
            ff2 = "data/2004.nc"
            ds1 = nc.open_data([ff1, ff2], checks=False)
            ds1.set_precision("F32")
            ds1.merge("time")
            ds2 = ds1.copy()
            ds2.tmean(["year", "month"])
            ds1.subtract(ds2)
            ds1.tmean(["year", "month"])

            sst_max = ds1.to_dataframe().analysed_sst.abs().max()

            assert (sst_max < 1e-4)

    def test_merger(self):
        new = nc.open_data(ff, checks = False)
        tracker = nc.open_data(ff, checks = False)
        tracker.split("year")
        tracker.merge("time")
        tracker.subtract(new)
        tracker.tmean()
        x = tracker.to_dataframe().sst.values[0]

        assert x == 0

        n = len(nc.session_files())
        assert n == 1

    def test_add_safe(self):
        nc.options(lazy = False)
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years = list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.multiply(2)
        tracker.spatial_mean()
        new.add(new)
        new.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x  == y

        n = len(nc.session_files())
        assert n == 2
        nc.options(lazy = True)

    def test_add(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.spatial_mean()
        new.add(1)
        new.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x + 1.0  == y

        n = len(nc.session_files())
        assert n == 2

    def test_add_multiple(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker)
        new.subtract(tracker)
        new.subtract(tracker)
        new.spatial_mean()

        x = new.to_dataframe().sst.values[0]

        assert x == 0

        n = len(nc.session_files())
        assert n == 2

    def test_add2(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker)
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]

        y = new.to_dataframe().sst.values[0]

        assert x + x == y
        n = len(nc.session_files())
        assert n == 2

    def test_add21(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker, "sst")
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x + x == y

        n = len(nc.session_files())
        assert n == 2

    def test_add_var(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.assign(tos = lambda x: x.sst+1-1, drop = True)
        tracker.run()
        new.add(tracker, var="tos")
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().tos.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x + x == y
        n = len(nc.session_files())
        assert n == 2

    def test_add3(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker.current[0])
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x + x == y

        n = len(nc.session_files())
        assert n == 2

    def test_add4(self):
        nc.options(lazy=False)
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker.current[0])
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert x + x == y

        n = len(nc.session_files())
        assert n == 2
        nc.options(lazy=True)

    def test_subtract(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(1)
        new.subtract(tracker)
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert y == 1
        n = len(nc.session_files())
        assert n == 2

    def test_subtract1(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(1)
        new.subtract(tracker.current[0])
        new.spatial_mean()
        tracker.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = new.to_dataframe().sst.values[0]

        assert y == 1
        n = len(nc.session_files())
        assert n == 2

    def test_op_list(self):
        ff = "data/sst.mon.mean.nc"
        data = nc.open_data(ff, checks = False)
        data.subset(timesteps=0)
        new = nc.open_data(ff, checks = False)
        new.subset(timesteps=[0, 1])
        new.split("yearmonth")
        new.subtract(data)
        new.merge("time")
        new.subset(timesteps=0)
        new.spatial_sum()
        x = new.to_dataframe().sst.values[0].astype("float")

        assert x == 0.0
        n = len(nc.session_files())
        assert n == 2

    def test_subtract2(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.spatial_mean()
        new.subtract(1)
        new.spatial_mean()

        x = tracker.to_dataframe().sst.values[0].astype("float")
        y = new.to_dataframe().sst.values[0].astype("float")

        assert x - 1 == y
        n = len(nc.session_files())
        assert n == 2

    def test_multiply(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.spatial_mean()
        new.multiply(10)
        new.spatial_mean()

        x = tracker.to_dataframe().sst.values[0].astype("float") * 10.0
        y = new.to_dataframe().sst.values[0].astype("float")


        assert np.round(x, 3) == np.round(y, 3)
        n = len(nc.session_files())
        assert n == 2

    def test_multiply1(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(2)
        new.subtract(tracker)
        out = tracker.copy()
        tracker.multiply(new)
        tracker.spatial_mean()
        out.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = out.to_dataframe().sst.values[0]

        assert x == y * 2
        n = len(nc.session_files())
        assert n == 3

        del new
        del out
        del tracker
        n = len(nc.session_files())
        assert n == 0

    def test_multiply2(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(2)
        new.subtract(tracker.current[0])
        out = tracker.copy()
        tracker.multiply(new)
        tracker.spatial_mean()
        out.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = out.to_dataframe().sst.values[0]

        assert x == y * 2
        n = len(nc.session_files())
        assert n == 3

    def test_divide(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        tracker.spatial_mean()
        new.divide(10)
        new.spatial_mean()

        x = tracker.to_dataframe().sst.values[0].astype("float")
        y = new.to_dataframe().sst.values[0].astype("float")

        assert np.round(x / 10, 4) == np.round(y, 4)
        n = len(nc.session_files())
        assert n == 2

    def test_divide1(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(2)
        new.subtract(tracker)
        out = tracker.copy()
        tracker.divide(new)
        tracker.spatial_mean()
        out.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = out.to_dataframe().sst.values[0]

        assert x == y / 2
        n = len(nc.session_files())
        assert n == 3

    def test_divide2(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(2)
        new.subtract(tracker.current[0])
        out = tracker.copy()
        tracker.divide(new)
        tracker.spatial_mean()
        out.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = out.to_dataframe().sst.values[0]

        assert x == y / 2
        n = len(nc.session_files())
        assert n == 3

    def test_divide3(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(2)
        new.subtract(tracker.current[0])
        out = tracker.copy()
        tracker.divide(new)
        tracker.spatial_mean()
        out.spatial_mean()

        x = tracker.to_dataframe().sst.values[0]
        y = out.to_dataframe().sst.values[0]

        assert x == y / 2
        n = len(nc.session_files())
        assert n == 3

    def test_file_incompat(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        data2 = nc.open_data(ff2, checks=False)
        data2.assign(tos = lambda x: x.analysed_sst + 2)
        data2.run()
        with pytest.raises(ValueError):
            tracker.add(data2.current[0])
        n = len(nc.session_files())
        assert n == 1

    def test_file_incompat1(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        data2 = nc.open_data(ff2, checks=False)
        data2.assign(tos = lambda x:  x.analysed_sst + 2)
        data2.run()
        with pytest.raises(ValueError):
            tracker.subtract(data2)
        n = len(nc.session_files())
        assert n == 1

    def test_file_incompat2(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        data2 = nc.open_data(ff2, checks=False)
        data2.assign(tos = lambda x:  x.analysed_sst + 2)
        data2.run()
        with pytest.raises(ValueError):
            tracker.divide(data2)
        n = len(nc.session_files())
        assert n == 1

    def test_file_incompat3(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.multiply("xyz")
        n = len(nc.session_files())
        assert n == 0

    def test_file_incompat4(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.subtract("xyz")
        n = len(nc.session_files())
        assert n == 0

    def test_file_incompat5(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.add("xyz")
        n = len(nc.session_files())
        assert n == 0

    def test_file_incompat6(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.divide("xyz")
        n = len(nc.session_files())
        assert n == 0

    def test_file_incompat7(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        data2 = nc.open_data(ff2, checks=False)
        data2.assign(tos = lambda x: x.analysed_sst + 2)
        data2.run()
        with pytest.raises(ValueError):
            tracker.multiply(data2)
        n = len(nc.session_files())
        assert n == 1

    def test_file_typeerror(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.multiply([1, 2])
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data()
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.multiply([1, 2])
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data()
        ff2 = "data/2003.nc"
        with pytest.raises(ValueError):
            tracker.multiply(1)
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data()
        ff2 = "data/2003.nc"
        with pytest.raises(ValueError):
            tracker.add(1)
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data()
        ff2 = "data/2003.nc"
        with pytest.raises(ValueError):
            tracker.subtract(1)
        n = len(nc.session_files())
        assert n == 0

        version = nc.utils.cdo_version()
        if nc.utils.version_below(version, "1.9.9") == False:
            tracker = nc.open_data()
            ff2 = "data/2003.nc"
            tracker2 = nc.open_data(ff2, checks=False)
            with pytest.raises(ValueError):
                tracker.divide(tracker2)
            n = len(nc.session_files())
            assert n == 0

        ff2 = "data/2003.nc"
        tracker = nc.open_data(ff2, checks=False)
        tracker2 = nc.open_data()
        with pytest.raises(ValueError):
            tracker.add(tracker2)
        with pytest.raises(ValueError):
            tracker.subtract(tracker2)
        with pytest.raises(ValueError):
            tracker.multiply(tracker2)
        with pytest.raises(ValueError):
            tracker.divide(tracker2)
        n = len(nc.session_files())
        assert n == 0

        tracker = nc.open_data(ff2, checks=False)

        with pytest.raises(TypeError):
            tracker.power("x")




    def test_file_typeerror1(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.subtract([1, 2])
        n = len(nc.session_files())
        assert n == 0

    def test_file_typeerror2(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.add([1, 2])

        n = len(nc.session_files())
        assert n == 0

    def test_file_typeerror3(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.divide([1, 2])
        n = len(nc.session_files())
        assert n == 0

    def test_file_typeerror4(self):
        tracker = nc.open_data(ff, checks = False)
        ff2 = "data/2003.nc"
        with pytest.raises(TypeError):
            tracker.divide([1, 2])
        n = len(nc.session_files())
        assert n == 0

    def test_var_typeerror(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(TypeError):
            tracker.add(tracker, var=1)

    def test_var_valueerror(self):
        tracker = nc.open_data(ff, checks = False)
        with pytest.raises(ValueError):
            tracker.add(tracker, var="tos222")

    def test_lazy_add(self):
        tracker = nc.open_data(ff, checks = False)
        tracker.subset(years=list(range(1970, 1971)))
        tracker.subset(months=[1])
        tracker.run()
        new = tracker.copy()
        new.add(tracker, "sst")
        new.subtract(tracker, "sst")
        new.subtract(tracker, "sst")
        new.spatial_mean()

        x = new.to_dataframe().sst.values[0]

        assert x == 0

        n = len(nc.session_files())
        assert n == 2

    def test_empty(self):
        n = len(nc.session_files())
        assert n == 0



    def test_ariths(self):

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.power(2)
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]



        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.assign(sst = lambda x: x.sst ** 2)
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y


        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.power(2.1)
        ds.spatial_range()
        x = ds.to_dataframe().sst.values[0]



        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.assign(sst = lambda x: x.sst ** 2.1)
        ds.spatial_range()
        y = ds.to_dataframe().sst.values[0]

        # Spatial range seems to have a bug in cdo v. 2.0.0
        x == y


        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.abs()
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.assign(sst = lambda x: abs(x.sst))
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y


        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.sqrt()
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.assign(sst = lambda x: sqrt(x.sst))
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.exp()
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.assign(sst = lambda x: exp(x.sst))
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.add(200)
        ds.log()
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.add(200)
        ds.assign(sst = lambda x: log(x.sst))
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.add(200)
        ds.log10()
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]

        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.add(200)
        ds.assign(sst = lambda x: log10(x.sst))
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y



        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.power(2)
        ds.spatial_mean()
        x = ds.to_dataframe().sst.values[0]



        ds = nc.open_data(ff, checks = False)
        ds.subset(time = 0)
        ds.square()
        ds.spatial_mean()
        y = ds.to_dataframe().sst.values[0]

        assert x == y
