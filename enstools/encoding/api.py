from .definitions import Compressors, CompressionModes, compressor_aliases, compression_mode_aliases
from .encodings import FilterEncodingForXarray, FilterEncodingForH5py
from .compressors.availability_checks import check_dataset_filters_availability, check_filters_availability, \
    check_sz_availability, check_zfp_availability, check_blosc_availability, check_libpressio_availability

__version__ = "v0.1.0"
