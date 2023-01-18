import os
from copy import deepcopy
from pathlib import Path
from typing import Union, Dict

import xarray
import yaml

from . import rules
from .errors import InvalidCompressionSpecification
from .variable_encoding import _Mapping, parse_variable_specification, Encoding, \
    NullEncoding


def compression_dictionary_to_string(compression_dictionary: dict) -> str:
    """
    Convert a dictionary containing multiple entries to a single line specification
    """
    return rules.VARIABLE_SEPARATOR.join(
        [f"{key}{rules.VARIABLE_NAME_SEPARATOR}{value}" for key, value in compression_dictionary.items()])


def parse_full_specification(spec: str) -> Dict[str, Encoding]:
    from enstools.encoding.rules import VARIABLE_SEPARATOR, VARIABLE_NAME_SEPARATOR, \
        DATA_DEFAULT_LABEL, DATA_DEFAULT_VALUE, COORD_LABEL, COORD_DEFAULT_VALUE
    result = {}

    if spec is None:
        spec = "None"

    parts = spec.split(VARIABLE_SEPARATOR)
    for p in parts:
        # For each part, check if there's a variable name.
        # If there's a variable name, split the name and the specification
        if VARIABLE_NAME_SEPARATOR in p:
            var_name, var_spec = p.split(VARIABLE_NAME_SEPARATOR)
        # Otherwise, it corresponds to the default.
        else:
            var_name = DATA_DEFAULT_LABEL
            var_spec = p

        # If the variable name was already in the dictionary, raise an error.
        if var_name in result:
            raise InvalidCompressionSpecification(f"Variable {var_name} has multiple definitions."
                                                  f"")
        # Parse the variable specification
        result[var_name] = parse_variable_specification(var_spec)

    # In case values for default and coordinates haven't been provided, use the default values.
    if DATA_DEFAULT_LABEL not in result:
        result[DATA_DEFAULT_LABEL] = parse_variable_specification(DATA_DEFAULT_VALUE)

    if COORD_LABEL not in result:
        # If the default is a NullSpecification, we'll use the same for the coordinates
        if isinstance(result[DATA_DEFAULT_LABEL], NullEncoding):
            result[COORD_LABEL] = result[DATA_DEFAULT_LABEL]
        else:
            result[COORD_LABEL] = parse_variable_specification(COORD_DEFAULT_VALUE)

    # For each specification, check that the specifications are valid.
    for key, spec in result.items():
        spec.check_validity()

    return result


class DatasetEncoding(_Mapping):
    """
    Class to encapsulate compression specification parameters corresponding to a full dataset.
    The kind of encoding that xarray expects is a mapping between the variables and their corresponding h5py encoding.
    """

    def __init__(self, dataset: xarray.Dataset, compression: Union[str, dict, None]):
        self.dataset = dataset

        # Process the compression argument to get a single string with per-variable specifications
        compression = self.get_a_single_compression_string(compression)

        # Save it
        self.variable_encodings = parse_full_specification(compression)

    @staticmethod
    def get_a_single_compression_string(compression: Union[str, dict, Path]) -> str:
        # The compression parameter can be a string or a dictionary.

        # In case it is a string, it can be directly a compression specification or a yaml file.
        # If it is a file, convert it to a Path
        if isinstance(compression, str) and os.path.exists(compression):
            compression = Path(compression)

        if isinstance(compression, dict):
            # Just to make sure that we have all the mandatory fields (default, coordinates), we will convert
            # the input dictionary to a single specification string and convert it back.
            return compression_dictionary_to_string(compression)
        elif isinstance(compression, Path):
            with compression.open("r") as stream:
                dict_of_strings = yaml.safe_load(stream)
            return compression_dictionary_to_string(dict_of_strings)
        elif isinstance(compression, str):
            # Convert the single string in a dictionary with an entry for each specified variable plus the defaults
            # for data and coordinates
            return compression
        elif compression is None:
            return None
        else:
            raise InvalidCompressionSpecification(
                f"The argument 'compression' should be a string, a dictionary or a Path. It is {type(compression)!r}-")

    def encoding(self):
        # Get the defaults
        data_default = self.variable_encodings[rules.DATA_DEFAULT_LABEL]
        coordinates_default = self.variable_encodings[rules.COORD_LABEL]

        # Set encoding for coordinates
        coordinate_encodings = {coord: deepcopy(coordinates_default) for coord in self.dataset.coords}
        # Set encoding for data variables
        data_variable_encodings = {
            str(var): deepcopy(self.variable_encodings[str(var)]) if var in self.variable_encodings else deepcopy(
                data_default) for
            var
            in self.dataset.data_vars}

        # Add chunking?
        for variable in self.dataset.data_vars:
            chunks = {k: v if k != "time" else 1 for k, v in self.dataset[variable].sizes.items()}
            chunk_sizes = tuple(chunks.values())
            # Ugly python magic to add chunk sizes into the encoding mapping object.
            data_variable_encodings[variable]._kwargs._kwargs["chunksizes"] = chunk_sizes  # noqa

        # Merge
        all_encodings = {**coordinate_encodings, **data_variable_encodings}

        return all_encodings

    @property
    def _kwargs(self):
        return self.encoding()

    def add_metadata(self):
        """
        Add the corresponding compression metadata to the dataset.
        """
        for variable, encoding in self._kwargs.items():
            # If its a case without compression, don't write the metadata.
            if isinstance(encoding, NullEncoding):
                continue
            self.dataset[variable].attrs["compression"] = encoding.description()


def is_a_valid_dataset_compression_specification(specification):
    try:
        _ = parse_full_specification(specification)
        return True
    except InvalidCompressionSpecification:
        return False
