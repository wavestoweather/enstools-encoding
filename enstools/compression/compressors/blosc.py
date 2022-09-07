from .availability_checks import check_blosc_availability

from hdf5plugin import Blosc as _Blosc


class Blosc(_Blosc):
    """
    Just a wrapper to add a filter check
    """
    def __init__(self, *args, **kwargs):
        assert check_blosc_availability()
        super().__init__(*args, **kwargs)

