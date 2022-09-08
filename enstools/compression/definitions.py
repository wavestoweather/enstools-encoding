from enum import Enum, auto


class Compressors(Enum):
    """
    List of supported compressors
    """
    NONE = None
    BLOSC = 32001
    ZFP = 32013
    SZ = 32017
    ALL = auto()


class CompressionModes(Enum):
    """
    List of supported compression Modes
    """
    # ZFP Modes
    RATE = auto()
    PRECISION = auto()
    ACCURACY = auto()
    REVERSIBLE = auto()
    EXPERT = auto()

    # SZ Modes
    ABS = auto()
    REL = auto()
    PW_REL = auto()

    # BLOSC Modes
    BLOSCLZ = auto()
    LZ4 = auto()
    LZ4HC = auto()
    SNAPPY = auto()
    ZLIB = auto()
    ZSTD = auto()

    # Other modes
    ALL = auto()
    NONE = None


compressor_aliases = {mode: str(mode).replace("Compressors.", "").lower() for mode in Compressors}

compression_mode_aliases = {mode: str(mode).replace("CompressionModes.", "").lower() for mode in CompressionModes}
