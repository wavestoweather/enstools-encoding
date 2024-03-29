Compression Specification Format
================================

We created a Compression Specification Format, which can be easily read and utilized by various applications written in different programming languages.
An example of this format would be:

    >>> lossy,zfp,rate,4.0

The currently implemented compressors include `Blosc <https://www.blosc.org/>`_ for lossless compression,
and `ZFP <https://computing.llnl.gov/projects/zfp>`_, `SZ <https://szcompressor.org/>`_ and `SZ3 <https://szcompressor.org/>`_ for lossy compression.
In order to use lossless compression, one can simply write:

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
At the moment the lossy supported compressors are: **ZFP**, **SZ** and **SZ3**.

The compressors have different methods and different names for them:
    -**ZFP**:
        - **accuracy**: absolute threshold mode
        - **rate**: number of bits-per-value
        - **precision**: keep a certain bits of precision

    -**SZ**:
        - **abs**: absolute threshold mode
        - **rel**: relative threshold mode
        - **pw_rel**: point-wise relative threshold mode
    -**SZ3**:
        - **abs**: absolute threshold mode
        - **rel**: relative threshold mode
        - **norm2**: using norm2.
        - **psnr**: using the peak signal to noise ratio mode.

Few examples of lossy compression specifications:

.. code::

    lossy,sz,abs,0.01
    lossy,zfp,rate,4.0
    lossy,sz3,psnr,40
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

    >>> var1:lossy,zfp,rate,4.0 lossy,sz,abs,0.1 -> var1:lossy,zfp,rate,4.0 default:lossy,sz,abs,0.1

If no default value is provided, lossless compression will be applied:

    >>> var1:lossy,zfp,rate,4.0 ->  var1:lossy,zfp,rate,4.0 default:lossless

Coordinates are treated separately, by default are compressed using **lossless**, although it is possible to change that:

    >>> coordinates:lossy,zfp,rate,6
