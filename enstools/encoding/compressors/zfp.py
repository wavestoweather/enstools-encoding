import struct
from typing import Tuple

from .compressor_class import Compressor
from ..errors import FilterNotAvailable, EnstoolsCompressionError
from .availability_checks import check_zfp_availability

zfp_filter_id = 32013


def zfp_pack_error(error: float) -> Tuple[int, int]:
    packed = struct.pack('<d', error)  # Pack as IEEE 754 double
    high = struct.unpack('<I', packed[0:4])[0]  # Unpack high bits as unsigned int
    low = struct.unpack('<I', packed[4:8])[0]
    return high, low


class Zfp(Compressor):
    filter_id = zfp_filter_id

    def __init__(self,
                 rate=None,
                 precision=None,
                 accuracy=None,
                 reversible=False,
                 minbits=None,
                 maxbits=None,
                 maxprec=None,
                 minexp=None):
        if not check_zfp_availability():
            raise FilterNotAvailable("ZFP filter is not available.")

        if rate is not None:
            rateHigh, rateLow = zfp_pack_error(rate)
            self.filter_options = 1, 0, rateHigh, rateLow, 0, 0

        elif precision is not None:
            self.filter_options = 2, 0, int(precision), 0, 0, 0

        elif accuracy is not None:
            accuracyHigh, accuracyLow = zfp_pack_error(accuracy)
            self.filter_options = 3, 0, accuracyHigh, accuracyLow, 0, 0

        elif reversible:
            self.filter_options = 5, 0, 0, 0, 0, 0

        elif minbits is not None:
            minbits = int(minbits)
            maxbits = int(maxbits)
            maxprec = int(maxprec)
            minexp = struct.unpack('I', struct.pack('i', int(minexp)))[0]
            self.filter_options = 4, 0, minbits, maxbits, maxprec, minexp
        else:
            raise EnstoolsCompressionError("Trying to create a ZFP encoding without a mode.")
