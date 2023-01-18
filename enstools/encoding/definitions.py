
# Dictionary of implemented lossy compressors and their respective modes and ranges.
# TODO: Would that be better to keep the definition of the available compressors and methods in a configuration file?
lossy_compressors_and_modes = {
    "sz": {
        "abs": {"range": [0, float('inf')], "type": float},
        "rel": {"range": [0, 1], "type": float},
        "pw_rel": {"range": [0, 1], "type": float},
    },
    "sz3": {
        "abs": {"range": [0, float('inf')], "type": float},
        "rel": {"range": [0, 1], "type": float},
        "norm2": {"range": [0, 1], "type": float},
        "psnr": {"range": [1, 120], "type": float},
    },
    "zfp": {
        "rate": {"range": [0, 32], "type": float},
        "precision": {"range": [1, 32], "type": int},
        "accuracy": {"range": [0, float('inf')], "type": float},
    }
}

# Create a list with the lossy compressors
lossy_compressors = [c for c in lossy_compressors_and_modes]

# Create a dictionary containing the available compression modes for each lossy compressor
lossy_compression_modes = {c: [k for k in lossy_compressors_and_modes[c]] for c in lossy_compressors}


# List of available BLOSC backends for lossless compression
lossless_backends = ['blosclz', 'lz4', 'lz4hc', 'snappy', 'zlib', 'zstd']

# Mappings between SZ modes and the keywords used in hdf5plugin
sz_mode_map = {
    "abs": "absolute",
    "rel": "relative",
    "pw_rel": "pointwise_relative",
    "psnr": "peak_signal_to_noise_ratio",
    "norm2": "norm2",
}

# Mapping between compressor names and hdf5plugin classes
import hdf5plugin
compressor_map = {
    "zfp": hdf5plugin.Zfp,
    "sz": hdf5plugin.SZ,
    "sz3": hdf5plugin.SZ3,
}
