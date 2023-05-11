"""
This module provides utility functions and a class for handling compression specifications
and chunking in xarray Datasets.

Functions:
- convert_size(size_bytes): Converts a given size in bytes to a human-readable format.
- convert_to_bytes(size_string): Converts a size string (e.g., '5MB') to the number of bytes.
- compression_dictionary_to_string(compression_dictionary): Converts a dictionary with
  compression entries to a single-line specification string.
- parse_full_specification(spec): Parses a full compression specification and returns a
  dictionary of variable encodings.
- is_a_valid_dataset_compression_specification(specification): Checks if a compression
  specification is valid for a dataset.
- find_chunk_sizes(data_array, chunk_size): Determines chunk sizes for each dimension of a
  data array based on a desired chunk size.

Class:
- DatasetEncoding: Encapsulates compression specification parameters for a full dataset.
  Provides methods to generate encodings and add metadata.

"""

import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Hashable, Union, Dict
import math

import numpy as np
import xarray
import yaml

from . import rules
from .errors import InvalidCompressionSpecification
from .variable_encoding import _Mapping, parse_variable_specification, Encoding, \
    NullEncoding
from .rules import VARIABLE_SEPARATOR, VARIABLE_NAME_SEPARATOR, \
    DATA_DEFAULT_LABEL, DATA_DEFAULT_VALUE, COORD_LABEL, COORD_DEFAULT_VALUE


def convert_size(size_bytes):
    """
    Converts a given size in bytes to a human-readable format.

    Args:
        size_bytes (int): Size in bytes.

    Returns:
        str: Size in human-readable format (e.g., '5MB').
    """
    if size_bytes < 0:
        prefix = "-"
        size_bytes = -size_bytes
    else:
        prefix = ""

    if size_bytes == 0:
        return "0B"

    size_units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    magnitude = int(math.floor(math.log(size_bytes, 1024)))
    factor = math.pow(1024, magnitude)
    size = round(size_bytes / factor, 2)
    return f"{prefix}{size}{size_units[magnitude]}"


def convert_to_bytes(size_string):
    """
    This function converts a given size string (e.g. '5MB') to the number of bytes.
    
    Args:
    size_string (str): The size string to be converted (e.g. '5MB')
    
    Returns:
    int: The number of bytes.
    """

    size_string = size_string.upper()
    digits = re.match(r'\d+(?:\.\d+)?', size_string)  # matches digits and optionally a dot followed by more digits
    if digits:
        digits = digits.group()  # get the matched digits
    else:
        raise ValueError(f"Invalid size string: {size_string}")
    unit = size_string.replace(digits, "")
    size_name_dict = {'B': 0, 'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4, 'PB': 5, 'EB': 6, 'ZB': 7, 'YB': 8}
    if unit in size_name_dict:
        size_bytes = float(digits) * np.power(1024, size_name_dict[unit])
    else:
        raise ValueError(f"Invalid size string: {size_string}")
    return int(size_bytes)


def compression_dictionary_to_string(compression_dictionary: Dict[str, str]) -> str:
    """
    Convert a dictionary containing multiple entries to a single line specification
    """
    return rules.VARIABLE_SEPARATOR.join(
        [f"{key}{rules.VARIABLE_NAME_SEPARATOR}{value}" for key, value in compression_dictionary.items()])


def parse_full_specification(spec: Union[str, None]) -> Dict[str, Encoding]:
    """
    Parses a full compression specification and returns a dictionary of variable encodings.

    Args:
        spec (Union[str, None]): The full compression specification as a string or None.

    Returns:
        Dict[str, Encoding]: A dictionary mapping variable names to their corresponding encodings.

    Raises:
        InvalidCompressionSpecification: If a variable has multiple definitions in the specification.

    """

    result = {}

    if spec is None:
        spec = "None"

    parts = spec.split(VARIABLE_SEPARATOR)
    for part in parts:
        # For each part, check if there's a variable name.
        # If there's a variable name, split the name and the specification
        if VARIABLE_NAME_SEPARATOR in part:
            var_name, var_spec = part.split(VARIABLE_NAME_SEPARATOR)
        # Otherwise, it corresponds to the default.
        else:
            var_name = DATA_DEFAULT_LABEL
            var_spec = part

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
    for _, _spec in result.items():
        _spec.check_validity()

    return result


class DatasetEncoding(_Mapping):
    """
    Class to encapsulate compression specification parameters corresponding to a full dataset.
    The kind of encoding that xarray expects is a mapping between the variables and their corresponding h5py encoding.
    """

    def __init__(self, dataset: xarray.Dataset, compression: Union[str, Dict[str, str], Path, None]):
        self.dataset = dataset

        # Process the compression argument to get a single string with per-variable specifications
        compression = self.get_a_single_compression_string(compression)

        # Save it
        self.variable_encodings = parse_full_specification(compression)

    @staticmethod
    def get_a_single_compression_string(compression: Union[str, Dict[str, str], Path, None]) -> Union[str, None]:
        """
        Converts the compression parameter into a single compression specification string.

        Args:
            compression (Union[str, Dict[str, str], Path, None]): The compression parameter,
            which can be a string, a dictionary, a file path, or None.

        Returns:
            Union[str, None]: The single compression specification string or None.

        Raises:
            InvalidCompressionSpecification: If the compression argument is not a valid type.

        """
        # The compression parameter can be a string or a dictionary.

        # In case it is a string, it can be directly a compression specification or a yaml file.
        # If it is a file, convert it to a Path
        if isinstance(compression, str) and os.path.exists(compression):
            compression = Path(compression)

        if isinstance(compression, dict):
            # Just to make sure that we have all the mandatory fields (default, coordinates), we will convert
            # the input dictionary to a single specification string and convert it back.
            return compression_dictionary_to_string(compression)
        if isinstance(compression, Path):
            with compression.open("r", encoding="utf-8") as stream:
                dict_of_strings = yaml.safe_load(stream)
            return compression_dictionary_to_string(dict_of_strings)
        if isinstance(compression, str):
            # Convert the single string in a dictionary with an entry for each specified variable plus the defaults
            # for data and coordinates
            return compression
        if compression is None:
            return None

        raise InvalidCompressionSpecification(
                f"The argument 'compression' should be a string, a dictionary or a Path. It is {type(compression)!r}-")

    def encoding(self):
        """
        Generate the encoding dictionary for all variables in the dataset.

        Returns:
            dict: A dictionary mapping variable names to their corresponding encodings.

        """
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

        # Merge
        all_encodings = {**coordinate_encodings, **data_variable_encodings}

        # Need to specify chunk size, otherwise it breaks down.
        self.chunk(encodings=all_encodings)

        return all_encodings

    def chunk(self, encodings: Dict[Union[Hashable, str], Encoding], chunk_memory_size="10MB"):
        """
        Add a variable "chunksizes" to each variable encoding with the corresponding 

        Args:
            encodings (dict): Dictionary with the corresponding encoding for each variable.
            chunk_memory_size (str): Desired chunk size in memory.
        """

        chunk_memory_size = convert_to_bytes(chunk_memory_size)

        # Loop over all the variables
        for variable in self.dataset.data_vars:
            data_array = self.dataset[variable]
            type_size = data_array.dtype.itemsize

            optimal_chunk_size = chunk_memory_size / type_size
            chunk_sizes = find_chunk_sizes(data_array=data_array, chunk_size=optimal_chunk_size)
            chunk_sizes = tuple(chunk_sizes[d] for d in data_array.dims)
            encodings[variable].set_chunk_sizes(chunk_sizes)

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
    """
        Checks if a compression specification is valid for a dataset.

        Args:
            specification: The compression specification to be validated.

        Returns:
            bool: True if the specification is valid, False otherwise.

        Note:
            - The function attempts to parse the specification using the `parse_full_specification` function.
            - If the specification is successfully parsed without raising an exception, it is considered valid.
            - If an `InvalidCompressionSpecification` exception is raised during parsing,
            the specification is considered invalid.
    """
    try:
        _ = parse_full_specification(specification)
        return True
    except InvalidCompressionSpecification:
        return False


def find_chunk_sizes(data_array, chunk_size):
    """
    Determines the chunk sizes for each dimension of a data array based on a desired chunk size.

    Args:
        data_array: The data array for which chunk sizes are determined.
        chunk_size: The desired chunk size in terms of the number of elements.

    Returns:
        dict: A dictionary mapping each dimension to its corresponding chunk size.
    """
    total_points = np.prod(data_array.shape)
    num_chunks = max(1, int(total_points // chunk_size))
    chunk_sizes = {}
    chunk_number = {}

    # Sort dimensions by size
    dims = sorted(data_array.dims, key=lambda x: data_array[x].shape)
    pending_num_chunks = num_chunks
    for dim in dims:
        chunk_sizes[dim] = max(1, int(data_array[dim].size // pending_num_chunks))
        chunk_number[dim] = data_array[dim].size // chunk_sizes[dim]

        pending_num_chunks = math.ceil(pending_num_chunks / chunk_number[dim])
    return chunk_sizes
