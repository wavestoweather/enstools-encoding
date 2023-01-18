from abc import ABC

from .definitions import lossy_compressors_and_modes
import logging

from typing import Mapping, Union, Protocol

import hdf5plugin

from enstools.encoding import rules, definitions
from enstools.encoding.errors import InvalidCompressionSpecification
from .rules import LOSSLESS_DEFAULT_BACKEND, LOSSLESS_DEFAULT_COMPRESSION_LEVEL

# Change logging level for the hdf5plugin to avoid unnecessary warnings
loggers = {name: logging.getLogger(name) for name in logging.root.manager.loggerDict}
hdf5plugin_loggers = [key for key in loggers.keys() if key.count("hdf5plugin")]
for key in hdf5plugin_loggers:
    loggers[key].setLevel(logging.WARNING)


class _Mapping(Mapping):
    """
    Subclass to implement dunder methods that are mandatory for Mapping to avoid repeating the code everywhere.
    """
    _kwargs: Mapping

    def __getitem__(self, item):
        return self._kwargs[item]

    def __setitem__(self, key, value):
        self._kwargs[key] = value

    def __iter__(self):
        return iter(self._kwargs)

    def __len__(self):
        return len(self._kwargs)


class Encoding(_Mapping):
    def check_validity(self) -> bool:
        ...

    def to_string(self) -> str:
        ...

    def encoding(self) -> Mapping:
        ...

    def description(self) -> str:
        ...

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_string()})"


class VariableEncoding(_Mapping):
    """
    Factory class to get the proper encoding depending on the arguments provided.

    To get an encoding from a specification:

    >>> VariableEncoding("lossy,zfp,rate,3.2")

    or

    >>> VariableEncoding(specification="lossy,zfp,rate,3.2")

    To get a lossy compression encoding specifing things separatelly:

    >>> VariableEncoding(compressor="zfp", mode="rate", parameter="3.2")


    To get a lossless compression encoding:

    >>> VariableEncoding("lossless")

    Or it is possible to specify the backend and the compression level.

    >>> VariableEncoding(backend="snappy")

    >>> VariableEncoding(backend="snappy", compression_level=9)

    """
    def __new__(cls,
                specification: str = None,
                compressor: str = None,
                mode: str = None,
                parameter: Union[str, float, int] = None,
                backend: str = None,
                compression_level: int = None,
                ) -> Encoding:
        return get_variable_encoding(specification=specification,
                                     compressor=compressor,
                                     mode=mode,
                                     parameter=parameter,
                                     backend=backend,
                                     compression_level=compression_level,
                                     )


class NullEncoding(Encoding):
    def check_validity(self) -> bool:
        return True

    def to_string(self) -> str:
        return "None"

    def encoding(self) -> Mapping:
        return {}

    def description(self) -> str:
        return ""


class LosslessEncoding(Encoding):
    def __init__(self, backend: str, compression_level: int):
        self.backend = backend if backend is not None else rules.LOSSLESS_DEFAULT_BACKEND
        self.compression_level = compression_level if compression_level is not None \
            else rules.LOSSLESS_DEFAULT_COMPRESSION_LEVEL

        self.check_validity()
        self._kwargs = self.encoding()

    def check_validity(self) -> bool:
        if self.backend not in definitions.lossless_backends:
            raise InvalidCompressionSpecification(f"Backend {self.backend!r} is not a valid backend.")
        elif not (1 <= self.compression_level <= 9):
            raise InvalidCompressionSpecification(f"Compression level {self.compression_level} must be within 1 and 9.")
        else:
            return True

    def to_string(self) -> str:
        return rules.COMPRESSION_SPECIFICATION_SEPARATOR.join(["lossless", self.backend, str(self.compression_level)])

    def encoding(self) -> Mapping:
        return hdf5plugin.Blosc(cname=self.backend, clevel=self.compression_level)

    def description(self) -> str:
        return f"Losslessly compressed with the HDF5 Blosc filter: {self.to_string()} " \
               f"(Using {self.backend!r} with compression level {self.compression_level})"

    def __repr__(self):
        return f"{self.__class__.__name__}(backend={self.backend}, compression_level={self.compression_level})"


class LossyEncoding(Encoding):
    def __init__(self, compressor: str, mode: str, parameter: Union[float, int]):
        self.compressor = compressor
        self.mode = mode

        self.parameter = parameter

        self.check_validity()
        self._kwargs = self.encoding()

    def check_validity(self):
        # Check compressor validity
        if self.compressor not in definitions.lossy_compressors_and_modes:
            raise InvalidCompressionSpecification(f"Invalid compressor {self.compressor}")
        # Check compression mode validity
        if self.mode not in definitions.lossy_compressors_and_modes[self.compressor]:
            raise InvalidCompressionSpecification(f"Invalid mode {self.mode!r} for compressor {self.compressor!r}")

        # Get parameter range and type
        mode_range = definitions.lossy_compressors_and_modes[self.compressor][self.mode]["range"]
        mode_type = definitions.lossy_compressors_and_modes[self.compressor][self.mode]["type"]
        # Check type
        if not isinstance(self.parameter, mode_type):
            try:
                self.parameter = mode_type(self.parameter)
            except TypeError:
                raise InvalidCompressionSpecification(f"Invalid parameter type {self.parameter!r}")
        # Check range
        if self.parameter <= mode_range[0] or self.parameter >= mode_range[1]:
            raise InvalidCompressionSpecification(f"Parameter out of range {self.parameter!r}")
        return True

    def to_string(self) -> str:
        return rules.COMPRESSION_SPECIFICATION_SEPARATOR.join(
            ["lossy", self.compressor, self.mode, str(self.parameter)])

    def encoding(self) -> Mapping:

        mode = definitions.sz_mode_map[self.mode] if self.mode in definitions.sz_mode_map else self.mode
        arguments = {mode: self.parameter}
        return definitions.compressor_map[self.compressor](**arguments)

    def description(self) -> str:
        return f"Lossy compressed using the HDF5 filters with specification: {self.to_string()} " \
               f"(Using {self.compressor!r} with mode {self.mode!r} and parameter {self.parameter})"

    def __repr__(self):
        return f"{self.__class__.__name__}(compressor={self.compressor}, mode={self.mode}, parameter={self.parameter})"


def parse_variable_specification(var_spec: str) -> Encoding:
    """
    Parse a string following the compression specification format for a single variable
     and return a Specification object.
    Parameters
    ----------
    var_spec

    Returns
    -------

    """
    if var_spec in (None, "None", "none"):
        return NullEncoding()

    from enstools.encoding.rules import COMPRESSION_SPECIFICATION_SEPARATOR
    # Split the specification in the different parts.
    var_spec_parts = var_spec.split(COMPRESSION_SPECIFICATION_SEPARATOR)
    # Treatment for lossless
    if var_spec_parts[0] == "lossless":
        backend = var_spec_parts[1] if len(var_spec_parts) > 1 else None
        compression_level = int(var_spec_parts[2]) if len(var_spec_parts) > 2 else None
        return LosslessEncoding(backend, compression_level)
    # Treatment for lossy
    elif var_spec_parts[0] == "lossy":
        # Lossy specifications must have 4 elements (lossy,compressor,mode,parameter)
        if len(var_spec_parts) != 4:
            raise InvalidCompressionSpecification(f"Invalid specification {var_spec!r}")

        # Get the different components.
        compressor, mode, specification = var_spec_parts[1:]
        # Check that the compressor is a valid option.
        if compressor not in lossy_compressors_and_modes:
            raise InvalidCompressionSpecification(f"Invalid compressor {compressor!r} in {var_spec!r}")
        # Check that the mode is a valid option.
        if mode not in lossy_compressors_and_modes[compressor]:
            raise InvalidCompressionSpecification(
                f"Invalid mode {mode!r} for compressor {compressor!r} in {var_spec!r}")
        # Cast the specification to the proper type.
        specification_type = lossy_compressors_and_modes[compressor][mode]["type"]
        try:
            specification = specification_type(specification)
        except ValueError:
            raise InvalidCompressionSpecification(f"Could not cast {specification!r} to type {specification_type!r}")
        return LossyEncoding(compressor, mode, specification)
    else:
        # In case its not lossy nor lossless, raise an exception.
        raise InvalidCompressionSpecification(f"Invalid specification {var_spec!r}")


# class VariableEncoding(_Mapping):
#     """
#     Class to encapsulate compression specification parameters for a single variable.
#
#     It stores the compressor, the mode and the parameter.
#
#     It has a method to create a new instance from a specification string,
#     a method to get the corresponding specification string from an existing object
#     and a method to obtain the corresponding mapping expected by h5py.
#
#     """
#
#     def __init__(self, specification: Specification):
#         # Init basic components
#         self.specification = specification
#
#         self._kwargs = self.filter_mapping()
#
#     @staticmethod
#     def from_string(string: str) -> 'VariableEncoding':
#         specification = parse_variable_specification(string)
#         """
#         Method to create a specification object from a specification string
#         """
#         return VariableEncoding(specification)
#
#     def to_string(self) -> str:
#         """
#         Method to obtain a specification string from a specification object
#         """
#         return self.specification.to_string()
#
#     def filter_mapping(self) -> Mapping:
#         """
#         Method to get the corresponding FilterRefBase expected by h5py/xarray
#         """
#
#         return self.specification.encoding()
#
#     def description(self):
#         self.specification.description()

def get_variable_encoding(
        specification: str = None,
        compressor: str = None,
        mode: str = None,
        parameter: Union[str, float, int] = None,
        backend: str = None,
        compression_level: int = None,
) -> Encoding:
    """
        Wildcard entry point for all ways of specifying an encoding:
        - Using a string specification
        - For lossy compression, specifying the compressor, the mode and the parameter
        - For lossless compression, specifying the backend and the compression level
    """

    # Two special cases:
    if (specification is None) and (compressor is None) and (backend is None):
        return LosslessEncoding(backend=LOSSLESS_DEFAULT_BACKEND, compression_level=LOSSLESS_DEFAULT_COMPRESSION_LEVEL)

    assert (specification is None) + (compressor is None) + (backend is None) == 2, \
        "Only one of the options can be used to create an Encoding"
    if specification:
        return parse_variable_specification(specification)
    elif compressor:
        return LossyEncoding(compressor=compressor, mode=mode, parameter=parameter)
    elif backend:
        if compression_level is None:
            compression_level = LOSSLESS_DEFAULT_COMPRESSION_LEVEL
        return LosslessEncoding(backend=backend, compression_level=compression_level)


def is_valid_variable_compression_specification(specification):
    try:
        _ = parse_variable_specification(specification)
        return True
    except InvalidCompressionSpecification:
        return False
