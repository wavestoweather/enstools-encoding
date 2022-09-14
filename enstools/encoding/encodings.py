import os.path
from typing import Union, Any, Mapping

import xarray
import yaml

from . import rules
from .compressors.sz import SZ
from .compressors.zfp import Zfp
from .compressors.blosc import Blosc
from .compressors.no_compressor import NoCompression
from .definitions import Compressors, CompressionModes
from .errors import WrongCompressionSpecificationError, WrongCompressionModeError
from copy import deepcopy

class _Mapping(Mapping):
    """
    Subclass to implement dunder methods that are mandatory for Mapping to avoid repeating the code everywhere.
    """
    _kwargs: dict

    def __getitem__(self, item):
        return self._kwargs[item]

    def __setitem__(self, key, value):
        self._kwargs[key] = value

    def __iter__(self):
        return iter(self._kwargs)

    def __len__(self):
        return len(self._kwargs)


class FilterEncodingForH5py(_Mapping):
    """
    Class to encapsulate compression specification parameters for a single variable.

    It stores the compressor, the mode and the parameter.

    It has a method to create a new instance from a specification string,
    a method to get the corresponding specification string from an existing object
    and a method to obtain the corresponding FilterRefBase expected by H5py.


    FilterRefBase subclasses help creating the mapping with the corresponding filter_id and filter_options.

    """

    def __init__(self,
                 compressor: Compressors,
                 mode: Union[CompressionModes, None],
                 parameter: Union[float, None],
                 ):
        # Init basic components
        self.compressor = compressor
        self.mode = mode
        self.parameter = parameter

        self._kwargs = self.filter_mapping()

    @staticmethod
    def from_string(string: str) -> Any:
        """
        Method to create a specification object from a specification string
        """
        return compression_string_to_object(string)

    def to_string(self) -> str:
        """
        Method to obtain a specification string from a specification object
        """
        return compression_object_to_string(self)

    def filter_mapping(self):
        """
        Method to get the corresponding FilterRefBase expected by h5py/xarray
        """
        if self.compressor is Compressors.BLOSC:
            return Blosc(clevel=9)
        elif self.compressor is Compressors.ZFP:
            mode = str(self.mode).lower().split('.')[-1]
            options = {mode: self.parameter}
            return Zfp(**options)
        elif self.compressor is Compressors.SZ:
            mode = str(self.mode).lower().split('.')[-1]
            options = {mode: self.parameter}
            return SZ(**options)
        elif self.compressor is Compressors.NONE:
            return NoCompression()
        else:
            raise NotImplementedError

    def description(self):
        return f"Compressed with HDF5 filter: {self.to_string()} " \
               f"(Using {self.compressor} " \
               f"filter with id: {self.compressor.value})"


class FilterEncodingForXarray(_Mapping):
    """
    Class to encapsulate compression specification parameters corresponding to a full dataset.
    The kind of encoding that xarray expects is a mapping between the variables and their corresponding h5py encoding.
    """

    def __init__(self, dataset: xarray.Dataset, compression: Union[str, dict]):
        self.dataset = dataset

        # Process the compression argument to get a dictionary with a specification for each variable
        dict_of_strings = self.get_dictionary_of_specifications(compression)

        # Convert each string specification into a CompressionDataArraySpecification
        variable_encodings = {key: FilterEncodingForH5py.from_string(value) for key, value in
                              dict_of_strings.items()}
        # Save it
        self.variable_encodings = variable_encodings

    @staticmethod
    def get_dictionary_of_specifications(compression: Union[str, dict]):
        # The compression parameter can be a string or a dictionary.
        # In case it is a string, it can be directly a compression specification or a yaml file.

        if isinstance(compression, dict):
            # Just to make sure that we have all the mandatory fields (default, coordinates), we will convert
            # the input dictionary to a single specification string and convert it back.
            dict_of_strings = compression_string_to_dictionary(compression_dictionary_to_string(compression))
        elif isinstance(compression, str):
            # Check if it corresponds to an existing file
            if os.path.exists(compression):
                with open(compression, "r") as stream:
                    dict_of_strings = yaml.safe_load(stream)
                # Just to make sure that we have all the mandatory fields (default, coordinates), we will convert
                # the input dictionary to a single specification string and convert it back.
                dict_of_strings = compression_string_to_dictionary(compression_dictionary_to_string(dict_of_strings))
            else:
                # Convert the single string in a dictionary with an entry for each specified variable plus the defaults
                # for data and coordinates
                dict_of_strings = compression_string_to_dictionary(compression)
        elif compression is None:
            dict_of_strings = {rules.DATA_DEFAULT_LABEL: None, rules.COORD_LABEL: None}
        else:
            raise TypeError(
                f"The argument 'compression' should be a string or a dictionary. It is {type(compression)!r}-")
        return dict_of_strings

    @property
    def _kwargs(self):
        return self.encoding()

    def encoding(self):
        # Get the defaults
        data_default = self.variable_encodings[rules.DATA_DEFAULT_LABEL]
        coordinates_default = self.variable_encodings[rules.COORD_LABEL]

        # Set encoding for coordinates
        coordinate_encodings = {coord: deepcopy(coordinates_default) for coord in self.dataset.coords}
        # Set encoding for data variables
        data_variable_encodings = {
            str(var): deepcopy(self.variable_encodings[str(var)]) if var in self.variable_encodings else deepcopy(data_default) for
            var
            in self.dataset.data_vars}

        # Add chunking?
        for variable in self.dataset.data_vars:
            chunks = {k: v if k != "time" else 1 for k, v in self.dataset[variable].sizes.items()}
            data_variable_encodings[variable]["chunksizes"] = tuple(chunks.values())

        # Merge
        all_encodings = {**coordinate_encodings, **data_variable_encodings}

        return all_encodings

    def add_metadata(self):
        """
        Add the corresponding compression metadata to the dataset.
        """
        for variable, encoding in self.encoding().items():
            if encoding.compressor != Compressors.NONE:
                self.dataset[variable].attrs["compression"] = encoding.description()


def compression_string_to_object(compression: str) -> FilterEncodingForH5py:
    """
    Receive a CFS string and return a CompressionDataArraySpecification
    """
    if compression in [None, "None", "none"]:
        return FilterEncodingForH5py(compressor=Compressors.NONE, mode=CompressionModes.NONE, parameter=None)

    arguments = compression.split(rules.COMPRESSION_SPECIFICATION_SEPARATOR)
    mode = ""
    parameter = 0.0
    if len(arguments) == 4:
        keyword, compressor, mode, parameter = arguments

        # In case the keyword doesn't correspond to lossy most probably the user has used the wrong separator
        if keyword != "lossy":
            raise WrongCompressionSpecificationError(
                f"Wrong separator {keyword!r}, "
                f"please use {rules.VARIABLE_NAME_SEPARATOR!r}"
            )

        compressor = Compressors[compressor.upper()]
        if mode.upper() not in CompressionModes.__members__:
            raise WrongCompressionModeError(
                f"Compression mode {mode} is not valid")
        mode = CompressionModes[mode.upper()]
        parameter = float(parameter)
    elif arguments[0] == "lossless":
        compressor = Compressors.BLOSC
    elif arguments[0].lower() == "none":
        compressor = Compressors.NONE
    else:
        raise WrongCompressionSpecificationError(
            f"Problem parsing compression specification: {compression!r}")

    return FilterEncodingForH5py(compressor, mode, parameter)


def compression_object_to_string(compression: FilterEncodingForH5py) -> str:
    """
    From a CompressionDataArraySpecification to a CFS compliant string
    :param compression:
    :return:
    """
    # Separator
    s = rules.COMPRESSION_SPECIFICATION_SEPARATOR
    if compression.compressor is Compressors.BLOSC:
        # For now we are ignoring BLOSC backends
        return f"lossless"
    else:
        # Convert the compressor
        compressor = str(compression.compressor).lower().split('.')[-1]
        mode = str(compression.mode).lower().split('.')[-1]
        parameter = str(compression.parameter)
        return f"lossy{s}{compressor}{s}{mode}{s}{parameter}"


def compression_dictionary_to_string(compression_dictionary: dict) -> str:
    """
    Convert a dictionary containing multiple entries to a single line specification
    """
    return rules.VARIABLE_SEPARATOR.join(
        [f"{key}{rules.VARIABLE_NAME_SEPARATOR}{value}" for key, value in compression_dictionary.items()])


def compression_string_to_dictionary(compression_string: str) -> dict:
    """
    This function splits a single string containing multiple compression specifications into a dictionary.
    This dictionary will contain a default entry, a coordinates entry and an additional entry for each variable
    explicitly mentioned.

    ----------
    compression_specification: str

    Returns
    -------
    compression_specification: dict
    """

    compression_dictionary = {}

    cases = compression_string.split(rules.VARIABLE_SEPARATOR)
    for case in cases:
        if case.strip():
            if rules.VARIABLE_NAME_SEPARATOR in case:
                variable, spec = case.split(rules.VARIABLE_NAME_SEPARATOR)
            else:
                variable = rules.DATA_DEFAULT_LABEL
                spec = case
            compression_dictionary[variable] = spec

    # Default for data variables if not explicitly specified
    if rules.DATA_DEFAULT_LABEL not in compression_dictionary:
        compression_dictionary[rules.DATA_DEFAULT_LABEL] = rules.DATA_DEFAULT_VALUE

    # Default for coordinates will be set if it was not explicitly specified in the string
    if rules.COORD_LABEL not in compression_dictionary:
        compression_dictionary[rules.COORD_LABEL] = rules.COORD_DEFAULT_VALUE
    return compression_dictionary
