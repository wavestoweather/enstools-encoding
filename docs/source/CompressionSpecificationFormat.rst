Compression Specification Format
================================

We defined our own specification format to represent the compression parameters that we want to apply to the data.
One example looks like this:

    >>> lossy,zfp,rate,4.0

Its purpose is to represent the specifications in a way that is easy to understand and use.

The currently implemented compressors include Blosc, for lossless compression, and ZFP and SZ for lossy compression.
For lossless compression, one can simply use:

    >>> lossless

This will use the default backend **lz4** with compression level 9.
It is also possible to select a different compression level (1 to 9) or backend:

        - blosclz
        - lz4
        - lz4hc
        - snappy
        - zlib
        - zstd

One example with a different backend and compression level could be:

    >>> lossless,snappy,7


For lossy compression, it is mandatory to include the compressor, the mode and the parameter.
At the moment two lossy compressors are supported: SZ and ZFP.

The two compressors have different methods and different names for them:
    -SZ:
        - **abs**: absolute threshold mode
        - **rel**: relative threshold mode
        - **pw_rel**: point-wise relative threshold mode
    -ZFP:
        - **accuracy**: absolute threshold mode
        - **rate**: number of bits-per-value
        - **precision**: keep a certain bits of precision


Few examples:

.. code::

    lossy,sz,abs,0.01
    lossy,zfp,rate,4.0
    lossy,sz,rel,1e-3
    lossy,zfp,precision,10
    lossy,sz,pw_rel,0.05
    lossy,zfp,accuracy,0.01

There are also few features that target datasets with multiple variables.
One can write a different specification for different variables by using a list of space separated specifications:

    >>> var1:lossy,zfp,rate,4.0 var2:lossy,sz,abs,0.1

It is possible too to specify the default value for the variables that are not explicitly mentioned:

    >>> var1:lossy,zfp,rate,4.0 default:lossy,sz,abs,0.1

In case a specification doesn't have a variable name, it will be considered the default. i.e:

    >>> `var1:lossy,zfp,rate,4.0 lossy,sz,abs,0.1` -> `var1:lossy,zfp,rate,4.0 default:lossy,sz,abs,0.1`

If no default value is provided, lossless compression will be applied:

    >>> `var1:lossy,zfp,rate,4.0` ->  `var1:lossy,zfp,rate,4.0 default:lossless`

Coordinates are treated separately, by default are compressed using `lossless`, although it is possible to change that:

    >>> `coordinates:lossy,zfp,rate,6`



For lossless compression, we can choose the backend and the compression leven as follows
    >>> lossless,backend,compression_level(from 1 to 9)

The backend must be one of the following options:



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

