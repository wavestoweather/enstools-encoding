import logging

from .compressor_class import Compressor
from .availability_checks import check_sz_availability
from ..errors import FilterNotAvailable

# The unique filter id given by HDF5
sz_filter_id = 32017


def sz_pack_error(error: float) -> int:
    from struct import pack, unpack
    return unpack('I', pack('<f', error))[0]  # Pack as IEEE 754 single


class SZ(Compressor):
    filter_id = sz_filter_id

    def __init__(self, abs=None, rel=None, pw_rel=None, chunksizes=None):
        # Check that a single option is selected:
        assert sum([abs is None, rel is None, pw_rel is None]) == 2, "Please select a single option."
        if not check_sz_availability():
            raise FilterNotAvailable("SZ filter is not available.")

        # Get SZ encoding options
        if abs is not None:
            sz_mode = 0
            parameter = abs
        elif rel is not None:
            sz_mode = 1
            parameter = rel
        elif pw_rel is not None:
            sz_mode = 10
            parameter = pw_rel
        else:
            raise NotImplementedError("One of the options need to be provided: abs, rel or pw_rel .")

        packed_error = sz_pack_error(parameter)
        compression_opts = (sz_mode, packed_error, packed_error, packed_error, packed_error)

        logging.info(f"SZ mode {sz_mode} used.")
        logging.info(f"filter options {compression_opts}")

        if chunksizes:
            # if compression_encoding:
            self.chunksizes = tuple(chunksizes)

        self.filter_options = compression_opts
