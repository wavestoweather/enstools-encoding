"""
Application Programming Interface

Access point to have access to all utilities defined in enstools-encoding
"""

# pylint: disable= unused-import
from .definitions import lossy_compressors, lossy_compression_modes, lossy_compressors_and_modes, lossless_backends
from .variable_encoding import VariableEncoding, LossyEncoding, LosslessEncoding, NullEncoding, Encoding
from .dataset_encoding import DatasetEncoding
