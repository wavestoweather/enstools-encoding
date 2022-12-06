"""
In order to keep a structure,
we define here a NoCompression class to be used whenever we don't want to compress part of a dataset.
"""


class NoCompression:
    """
    Compressor subclass for when we don't want any compression.
    """
    filter_id = None
    filter_options = None
    chunksizes = None
