from .compressor_class import Compressor


class NoCompression(Compressor):
    filter_id = None
    filter_options = None
    chunksizes = None
