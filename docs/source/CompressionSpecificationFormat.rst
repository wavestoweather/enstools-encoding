Compression Specification Format
================================

For lossless compression, we can choose the backend and the compression leven as follows
    >>> lossless,backend,compression_level(from 1 to 9)

The backend must be one of the following options:
        - blosclz
        - lz4
        - lz4hc
        - snappy
        - zlib
        - zstd


For lossy compression, we can choose the compressor (sz or zfp),
the method and the method parameter.

    >>> lossy,compressor,mode,parameter

Some examples:
    - lossless
    - lossless,zlib,5
    - lossy,zfp,accuracy,0.00001
    - lossy,zfp,precision,12
    - lossy,zfp,rate,3.2
    - lossy,sz,abs,0.1
    - lossy,sz,rel,0.0001
    - lossy,sz,pw_rel,1.e-6

