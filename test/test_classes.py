import pytest
import xarray as xr
import numpy as np
import pandas as pd
import yaml
import hdf5plugin

from enstools.encoding.errors import InvalidCompressionSpecification


from enstools.encoding.dataset_encoding import DatasetEncoding
from enstools.encoding.variable_encoding import VariableEncoding


class TestEncoding:
    def test_create_dataset(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

    def test_DatasetEncoding_lossless(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossless")

    def test_DatasetEncoding_None(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, None)

    def test_DatasetEncoding_multivariate_lossy(self) -> None:
        # Few cases with lossy compression:
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        # Try with a single string
        compression_specification_string = \
            "lossy,sz,pw_rel,0.0001 temperature:lossy,zfp,rate,4 vorticity:lossy,sz,abs,0.1"
        encoding = DatasetEncoding(dataset=dataset, compression=compression_specification_string)

    def test_DatasetEncoding_dictionary(self) -> None:
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        compression_specification_dictionary = {"temperature": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
        encoding = DatasetEncoding(dataset=dataset, compression=compression_specification_dictionary)

    def test_DatasetEncoding_file(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        compression_specification_dictionary = {"default": "lossy,zfp,rate,4", "vorticity": "lossy,sz,abs,0.1"}
        compression_specification_file = "compression_specification.yaml"
        with open(compression_specification_file, "w") as stream:
            yaml.dump(compression_specification_dictionary, stream)
        #    Pass the file path as a compression argument
        encoding = DatasetEncoding(dataset=dataset, compression=compression_specification_file)

        os.remove(compression_specification_file)

    def test_DatasetEncoding_wrong_type(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            encoding = DatasetEncoding(dataset=dataset, compression=42)  # noqa

    def test_DatasetEncoding_wrong_file(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            encoding = DatasetEncoding(dataset=dataset, compression="non-existing")  # noqa

    def test_DatasetEncoding_encoding(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = DatasetEncoding(dataset=dataset, compression="lossless")  # noqa
        # Try encoding method.
        encoding.encoding()

    def test_DatasetEncoding_addMetadata(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = DatasetEncoding(dataset=dataset, compression="lossless")  # noqa
        # Try add_metadata method.
        encoding.add_metadata()

    def test_DatasetEncoding_Mapping(self) -> None:
        import os
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        encoding = DatasetEncoding(dataset=dataset, compression="lossless")  # noqa
        dict(encoding)
        len(encoding)
        encoding["dummy"] = None

    def test_FilterEncodingForH5py(self):
        from enstools.encoding.variable_encoding import get_variable_encoding
        _ = get_variable_encoding("lossy,zfp,rate,0.4")

    def test_FilterEncodingForH5py_from_string_none(self):

        _ = VariableEncoding("none")
        _ = VariableEncoding(None)
        _ = VariableEncoding("None")

    def test_FilterEncodingForH5py_wrong_compressor_from_string(self):
        with pytest.raises(InvalidCompressionSpecification):
            _ = VariableEncoding("lossy,wrong,mode,0.1")

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
            with pytest.raises(InvalidCompressionSpecification):
                _ = VariableEncoding(case)

    def test_FilterEncodingForH5py_object_to_string(self):
        h5encoding = VariableEncoding("lossy,zfp,rate,5.0")
        h5encoding.to_string()

    def test_FilterEncodingForH5py_description(self):
        h5encoding = VariableEncoding("lossy,zfp,rate,5.0")
        h5encoding.description()

    def test_long_list_of_cases(self):
        """
        Test a long list of valid and invalid cases.
        It contains a list of tuples with the specification and its validity.
        In case it is not a valid string, it should raise an exception.
        """

        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])

        cases = [
            ("lossless", True),
            ("lossy,lossless", False),
            ("lossless,lz4,5", True),
            ("lossy,zfp,rate,4.0,precision", False),
            ("lossy,sz,abs,0.01", True),
            ("lossy,sz,mode,0.01", False),
            ("lossy,sz3,abs,0.01", True),
            ("var1:lossless var2:lossy,sz,rel,1e-3", True),
            ("var1:lossless var2:lossy,sz,rel,1e-3,pw", False),
            ("default:lossless,lz4,3 var1:lossy,zfp,rate,4.0", True),
            ("default:lossless,lz4,3 var1:lossy,zfp,rate,4.0,precision", False),
            ("lossless,snappy", True),
            ("lossless,snapp", False),
            ("lossless,snappy,5", True),
            ("lossless,snappy,0", False),
            ("lossless,snappy,11", False),
            ("lossy,zfp,accuracy,0.01", True),
            ("lossy,zfp,accurancy,0.01", False),
            ("lossy,zfp,accurancy,0.01", False),
            ("lossy,sz,pw_rel,0.05", True),
            ("lossy,sz,pw_rel,-0.05", False),
            ("lossy,sz,pw_rel,0", False),
            ("lossy,sz,pw_rel,1", False),
            ("var1:lossless var2:lossy,sz,abs,0.1", True),
            ("var1:lossless var2:lossy,sz,abs,-0.1", False),
            ("var1:lossless var2:lossy,sz,abs,2", True),
            ("default:lossy,zfp,rate,4.0 var1:lossless", True),
            ("default:lossy,zfp,rate,4.0 var1:lossless,lz4", True),
            ("default:lossy,zfp,rate,4.0 var1:lossless,lz4,5", True),
            ("default:lossy,zfp,rate,4.0 var1:lossless,lz4,0", False),
            ("default:lossy,zfp,rate,4.0 var1:lossless,lz4,11", False),
            ("lossless,zstd", True),
            ("lossless,zst", False),
            ("lossless,zstd,5", True),
            ("lossless,zstd,0", False),
            ("lossless,zstd,11", False),
            ("lossy,zfp,precision,13", True),
            ("lossy,zfp,precission,13", False),
            ("lossy,zfp,precision,13,rate", False),
            ("lossy,zfp,precision,-13", False),
            ("var1:lossless var2:lossy,zfp,accuracy,0.01", True),
            ("var1:lossless var2:lossy,zfp,accurancy,0.01", False),
            ("default:lossless var1:lossy,zfp,rate,4.0", True),
            ("default:lossless,zlib var1:lossy,zfp,rate,4.0", True),
            # Some tricky cases
            ("lossless,lz4,2 default:lossy,zfp,rate,3", False),
            ("lossless,lz4,2 var1:lossy,zfp,rate,3 var2:lossless", True),
            ("lossless,lz4,2 var1:lossy,zfp,rate,3 var2:lossless,lz4hc,4", True),
            ("lossless,lz4,2 var1:lossy,zfp,rate,30 var2:lossless,lz4hc,4", True),
            ("lossy,sz,pw_rel,1e-2", True),
            ("lossy,sz,pw_rel,1e-20", True),
            ("lossy,sz,abs,1e-20", True),
            ("lossy,sz,abs,-1e-2", False),
            ("lossy,sz,abs,1", True),
            ("default:lossy,sz,abs,1 lossless,lz4,3", False),
            ("lossy,sz,abs,1 lossless,lz4,3", False),
            ("lossy,zfp,rate,3 lossy,sz,abs,1", False),
            ("default:lossy,zfp,rate,3 default:lossy,sz,abs,1", False),
            ("lossy,zfp,rate,3 var1:lossy,sz,abs,1", True),
            ("lossy,zfp,rate,3 lossless,lz4,3", False),
            ("lossy,zfp,rate,3 var1:lossless,lz4,3", True),
            # More tricky cases
            ("lossless,lz4,3 lossless,lz4hc,3", False),  # Two default values provided
            ("lossless,lz4,3 lossy,zfp,rate,4.0 lossless,snappy,9", False),  # Two default values provided
            ("var1:lossless,lz4,3 var2:lossy,zfp,rate,4.0 var1:lossless,snappy,9", False),  # var1 specified twice
            ("lossy,zfp,precision,0.5", False),  # precision expects an integer
            ("lossy,zfp,precision,32.5", False),  # precision expects an integer
            ("lossy,zfp,rate,-0.5", False),  # Rate should be positive
            ("lossy,zfp,rate,32.5", False),  # Rate should be between 0 and 32
            ("lossy,sz,pw_rel,1.5 lossy,sz,pw_rel,1.5", False),  # Two default values provided
            ("lossy,zfp,abs,1.5", False),  # abs is not a valid mode for zfp
            ("lossy,sz,abs,1.5 lossless,zfp,3", False),
            (None, True),  # None should be a possibility
            ("None", True),  # None should be a possibility, also provided as a string
            ("none", True),  # None should be a possibility, also provided as a string
        ]

        for case, valid in cases:
            if valid:
                DatasetEncoding(dataset=dataset, compression=case)
            else:
                with pytest.raises(Exception):
                    DatasetEncoding(dataset=dataset, compression=case)


class TestZFPEncoding:
    def test_DatasetEncoding_zfp_accuracy(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,zfp,accuracy,0.1")

    def test_DatasetEncoding_zfp_rate(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,zfp,rate,3.2")

    def test_DatasetEncoding_zfp_precision(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,zfp,precision,10")

    def test_DatasetEncoding_zfp_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            DatasetEncoding(dataset, "lossy,zfp,wrong,10")


class TestSZEncoding:
    def test_DatasetEncoding_sz_abs(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz,abs,0.1")

    def test_DatasetEncoding_sz_rel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz,rel,0.001")

    def test_DatasetEncoding_sz_pwrel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz,pw_rel,0.001")

    def test_DatasetEncoding_sz_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            DatasetEncoding(dataset, "lossy,sz,wrong,10")

    def test_DatasetEncoding_sz_wrongParameter(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            DatasetEncoding(dataset, "lossy,sz,abs,wrong")


@pytest.mark.skipif(not hasattr(hdf5plugin, "SZ3"), reason="hdf5plugin doesn't have SZ3")
class TestSZ3Encoding:
    def test_DatasetEncoding_sz3_abs(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz3,abs,0.1")

    def test_DatasetEncoding_sz3_rel(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz3,rel,0.001")

    def test_DatasetEncoding_sz3_psnr(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz3,psnr,60")

    def test_DatasetEncoding_sz3_norm2(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        DatasetEncoding(dataset, "lossy,sz3,norm2,0.01")

    def test_DatasetEncoding_sz3_wrongMode(self) -> None:
        # Create a dummy dataset with few variables
        dataset = create_dummy_xarray_dataset(variables=["temperature", "vorticity", "pressure"])
        with pytest.raises(InvalidCompressionSpecification):
            DatasetEncoding(dataset, "lossy,sz3,wrong,10")


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
