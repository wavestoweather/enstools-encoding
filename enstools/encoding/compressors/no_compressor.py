"""
In order to keep a structure,
we define here a NoCompression class to be used whenever we don't want to compress part of a dataset.
"""

from .compressor_class import Compressor


class NoCompression(Compressor):
    """
    Compressor subclass for when we don't want any compression.
    """
    filter_id = None
    filter_options = None
    chunksizes = None
