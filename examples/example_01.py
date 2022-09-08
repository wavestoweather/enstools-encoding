import xarray as xr
import numpy as np
import pandas as pd
import yaml

from enstools.encodings import FilterEncodingForXarray, FilterEncodingForH5py, Compressors, CompressionModes

dummy_output_file = "example_01.nc"


def example_01() -> None:
    # Create a dummy dataset with few variables
    dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

    # One liner to losslessly compress a dataset:
    dataset.to_netcdf(dummy_output_file, encoding=FilterEncodingForXarray(dataset, "lossless"), engine="h5netcdf")

    # Few cases with lossy compression:
    # Try with a single string
    compression_specification_string = "lossy,sz,pw_rel,0.0001 temperature:lossy,zfp,rate,4 vorticity:lossy,sz,abs,0.1"
    encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_string)
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")

    # Try with the dictionary
    compression_specification_dictionary = {"temperature": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
    encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_dictionary)
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")

    # Try with the file

    #    Save a dictionary into a file
    compression_specification_dictionary = {"default": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
    compression_specification_file = "compression_specification.yaml"
    with open(compression_specification_file, "w") as stream:
        yaml.dump(compression_specification_dictionary, stream)

    #    Pass the file path as a compression argument
    encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_file)
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")

    # Now few cases using the encodings for a single variable
    # Try to use the filter for a single variable
    h5encoding = FilterEncodingForH5py(compressor=Compressors.ZFP, mode=CompressionModes.RATE, parameter=5.0)
    dataset.to_netcdf(dummy_output_file, encoding={"temperature": h5encoding}, engine="h5netcdf")

    # Try to use the filter for a single variable using a string
    h5encoding = FilterEncodingForH5py.from_string("lossy,zfp,rate,5")
    dataset.to_netcdf(dummy_output_file, encoding={"temperature": h5encoding}, engine="h5netcdf")


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


if __name__ == "__main__":
    example_01()
