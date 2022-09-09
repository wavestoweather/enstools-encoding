import xarray as xr
import numpy as np
import pandas as pd
import yaml

from enstools.encoding import FilterEncodingForXarray, FilterEncodingForH5py, Compressors, CompressionModes
import enstools.encoding.compressors.availability_checks

enstools.encoding.compressors.availability_checks.SKIP_CHECKS = True

class TestClass:
    def test_create_dataset(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

    def test_FilterEncodingForXarray_lossless(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossless")

    def test_FilterEncodingForXarray_None(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, None)

    def test_FilterEncodingForXarray_multivariate_lossy(self) -> None:
        # Few cases with lossy compression:
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        # Try with a single string
        compression_specification_string = \
            "lossy,sz,pw_rel,0.0001 temperature:lossy,zfp,rate,4 vorticity:lossy,sz,abs,0.1"
        encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_string)

    def test_FilterEncodingForXarray_dictionary(self) -> None:
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        compression_specification_dictionary = {"temperature": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
        encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_dictionary)

    def test_FilterEncodingForXarray_file(self) -> None:
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        compression_specification_dictionary = {"default": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
        compression_specification_file = "compression_specification.yaml"
        with open(compression_specification_file, "w") as stream:
            yaml.dump(compression_specification_dictionary, stream)

        #    Pass the file path as a compression argument
        encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_file)

    def test_FilterEncodingForH5py(self):
        h5encoding = FilterEncodingForH5py(compressor=Compressors.ZFP, mode=CompressionModes.RATE, parameter=5.0)

    def test_FilterEncodingForH5py_from_string(self):
        # Try to use the filter for a single variable using a string
        h5encoding = FilterEncodingForH5py.from_string("lossy,zfp,rate,5")

    def test_FilterEncodingForH5py_from_string_none(self):
        # Try to use the filter for a single variable using a string
        h5encoding = FilterEncodingForH5py.from_string("none")


def create_dummy_xarray_dataset(variables: list = None) -> xr.Dataset:
    # Create a synthetic dataset representing a 4D variable (3D + time)
    if variables is None:
        variables = ["temperature", "vorticity", "pressure"]
    nx, ny, nz, t = 360, 91, 31, 5
    lon = np.linspace(-180, 180, nx)
    lat = np.linspace(-90, 90, ny)
    levels = np.array(range(nz))

    data_size = (t, nz, nx, ny)
    var_dimensions = ["time", "level", "lon", "lat"]

    # Select data type
    data_type = np.float32
    # Create some random data
    var_data = data_type(15 + 8 * np.random.randn(*data_size))

    var_dict = {var: (var_dimensions, var_data) for var in variables}

    ds = xr.Dataset(
        var_dict,
        # Set up the coordinates
        coords={
            "lon": lon,
            "lat": lat,
            "level": levels,
            "time": pd.date_range("2014-09-06", periods=t),
            "reference_time": pd.Timestamp("2014-09-05"),
        },
    )
    return ds
