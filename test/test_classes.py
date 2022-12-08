import pytest
import xarray as xr
import numpy as np
import pandas as pd
import yaml
import hdf5plugin

from enstools.encoding.api import FilterEncodingForXarray, FilterEncodingForH5py, Compressors, CompressionModes
import enstools.encoding.compressors.availability_checks
from enstools.encoding.errors import WrongCompressorError, WrongCompressionModeError, \
    WrongCompressionSpecificationError, WrongParameterError

# Trick to disable the filter availability checks during the tests.
enstools.encoding.compressors.availability_checks.SKIP_CHECKS = True


class TestEncoding:
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
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        compression_specification_dictionary = {"default": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
        compression_specification_file = "compression_specification.yaml"
        with open(compression_specification_file, "w") as stream:
            yaml.dump(compression_specification_dictionary, stream)
        #    Pass the file path as a compression argument
        encoding = FilterEncodingForXarray(dataset=dataset, compression=compression_specification_file)

        os.remove(compression_specification_file)

    def test_FilterEncodingForXarray_wrong_type(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(TypeError):
            encoding = FilterEncodingForXarray(dataset=dataset, compression=42)  # noqa

    def test_FilterEncodingForXarray_wrong_file(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(WrongCompressionSpecificationError):
            encoding = FilterEncodingForXarray(dataset=dataset, compression="non-existing")  # noqa

    def test_FilterEncodingForXarray_encoding(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = FilterEncodingForXarray(dataset=dataset, compression="lossless")  # noqa
        # Try encoding method.
        encoding.encoding()

    def test_FilterEncodingForXarray_addMetadata(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = FilterEncodingForXarray(dataset=dataset, compression="lossless")  # noqa
        # Try add_metadata method.
        encoding.add_metadata()

    def test_FilterEncodingForXarray_Mapping(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = FilterEncodingForXarray(dataset=dataset, compression="lossless")  # noqa
        dict(encoding)
        len(encoding)
        encoding["dummy"] = None

    def test_FilterEncodingForH5py(self):
        h5encoding = FilterEncodingForH5py(compressor=Compressors.ZFP, mode=CompressionModes.RATE, parameter=5.0)

    def test_FilterEncodingForH5py_from_string(self):
        # Try to use the filter for a single variable using a string
        h5encoding = FilterEncodingForH5py.from_string("lossy,zfp,rate,5")

    def test_FilterEncodingForH5py_from_string_none(self):
        # Try to use the filter for a single variable using a string
        h5encoding = FilterEncodingForH5py.from_string("none")

    def test_FilterEncodingForH5py_wrong_compressor_from_string(self):
        with pytest.raises(WrongCompressorError):
            h5encoding = FilterEncodingForH5py.from_string("lossy,wrong,mode,0.1")

    def test_FilterEncodingForH5py_wrong_compressor(self):
        with pytest.raises(NotImplementedError):
            h5encoding = FilterEncodingForH5py(Compressors.ALL, None, None)

    def test_FilterEncodingForH5py_using_strings(self):
        h5encoding = FilterEncodingForH5py("zfp", "rate", 3.2)

    def test_FilterEncodingForH5py_wrong_specification(self):
        # Different cases that should raise a wrong specification error.
        cases = [
            "poijasduiohqwoir",
            "lossly",
            "random",
            "zfp,rate,2",
            "lossy,",
            "lossy:zfp:rate:1",
        ]

        for case in cases:
            with pytest.raises(WrongCompressionSpecificationError):
                h5encoding = FilterEncodingForH5py.from_string(case)

    def test_FilterEncodingForH5py_object_to_string(self):
        h5encoding = FilterEncodingForH5py(compressor=Compressors.ZFP, mode=CompressionModes.RATE, parameter=5.0)
        h5encoding.to_string()

    def test_FilterEncodingForH5py_description(self):
        h5encoding = FilterEncodingForH5py(compressor=Compressors.ZFP, mode=CompressionModes.RATE, parameter=5.0)
        h5encoding.description()


class TestZFPEncoding:
    def test_FilterEncodingForXarray_zfp_accuracy(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,zfp,accuracy,0.1")

    def test_FilterEncodingForXarray_zfp_rate(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,zfp,rate,3.2")

    def test_FilterEncodingForXarray_zfp_precision(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,zfp,precision,10")

    def test_FilterEncodingForXarray_zfp_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(WrongCompressionModeError):
            FilterEncodingForXarray(dataset, "lossy,zfp,wrong,10")


class TestSZEncoding:
    def test_FilterEncodingForXarray_sz_abs(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz,abs,0.1")

    def test_FilterEncodingForXarray_sz_rel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz,rel,0.001")

    def test_FilterEncodingForXarray_sz_pwrel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz,pw_rel,0.001")

    def test_FilterEncodingForXarray_sz_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(WrongCompressionModeError):
            FilterEncodingForXarray(dataset, "lossy,sz,wrong,10")

    def test_FilterEncodingForXarray_sz_wrongParameter(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(WrongParameterError):
            FilterEncodingForXarray(dataset, "lossy,sz,abs,wrong")


@pytest.mark.skipif(not hasattr(hdf5plugin, "SZ3"), reason="hdf5plugin doesn't have SZ3")
class TestSZ3Encoding:
    def test_FilterEncodingForXarray_sz3_abs(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz3,abs,0.1")

    def test_FilterEncodingForXarray_sz3_rel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz3,rel,0.001")

    def test_FilterEncodingForXarray_sz3_psnr(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz3,psnr,60")

    def test_FilterEncodingForXarray_sz3_norm2(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        FilterEncodingForXarray(dataset, "lossy,sz3,norm2,0.01")

    def test_FilterEncodingForXarray_sz3_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(WrongCompressionModeError):
            FilterEncodingForXarray(dataset, "lossy,sz3,wrong,10")


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
