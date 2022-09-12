# [Ensemble Tools - Encoding](https://github.com/wavestoweather/enstools-encoding)

Library to generate the encodings to write compressed files as easily as possible with **xarray** using **hdf5 filters**.

Its only capability is to provide the encodings that **xarray** and **h5py** need in order to write files using filters.

The package doesn't provide the filters, need to be installed separately.

This package was originally inside [Ensemble Tools](https://github.com/wavestoweather/enstools) but can be used standalone.

It is also a building block for [Ensemble Tools - Compression](https://github.com/wavestoweather/enstools-compression),
which includes a command line tool to make compression even easier, along with other useful tools to find proper compression parameters.

## Compressors
At the current stage it is possible to generate encodings for three compressors:
- [BLOSC](https://github.com/Blosc/hdf5-blosc)
- [SZ](https://github.com/szcompressor/SZ)
- [ZFP](https://github.com/LLNL/H5Z-ZFP)


## Quickstart
Using lossy compression with xarray can be as easy as adding a single line and an argument in the call to **.to_netcdf()** :

```python
from enstools.encoding import FilterEncodingForXarray

...
encoding = FilterEncodingForXarray(dataset, "lossy,sz,rel,1.e-4")
dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")
...
```

Check below for more details on how to do it.

## Installation using pip

`pip` is the easiest way to install `enstools-encoding` along with all dependencies:

```
pip install enstools-encoding 
```



## Compression Specification Format

We defined our own specification format to represent the compression parameters that we want to apply to the data.
One example looks like this:

```
lossy,zfp,rate,4.0
```

Its purpose is to represent the specifications in a way that is easy to understand and use.

The currently implemented compressors include Blosc, for lossless compression, and ZFP and SZ for lossy compression.
For lossless compression, one can simply use:

```
lossless
```

This will use the default backend **lz4** with compression level 9.
It is also possible to select a different backend (blosclz, lz4, lz4hc,snappy,zlib or zstd) or compression level (1 to
9):

```
lossless,snappy,9
```

For lossy compression, it is mandatory to include the compressor, the mode and the parameter. Few examples:

```
lossy,sz,abs,0.01
lossy,zfp,rate,4.0
lossy,sz,rel,1e-3
lossy,zfp,precision,10
lossy,sz,pw_rel,0.05
lossy,zfp,accuracy,0.01
```

There are also few features that target datasets with multiple variables.
One can write a different specification for different variables by using a list of space separated specifications:

```
var1:lossy,zfp,rate,4.0 var2:lossy,sz,abs,0.1
```

It is possible too to specify the default value for the variables that are not explicitly mentioned:

```
var1:lossy,zfp,rate,4.0 default:lossy,sz,abs,0.1
```

In case a specification doesn't have a variable name, it will be considered the default. i.e:

`var1:lossy,zfp,rate,4.0 lossy,sz,abs,0.1` -> `var1:lossy,zfp,rate,4.0 default:lossy,sz,abs,0.1`

If no default value is provided, lossless compression will be applied:

`var1:lossy,zfp,rate,4.0` ->  `var1:lossy,zfp,rate,4.0 default:lossless`

Coordinates are treated separately, by default are compressed using `lossless`, although it is possible to change that:

`coordinates:lossy,zfp,rate,6`

## Examples

Save an **xarray** dataset using losslessly compression:

```python
from enstools.encoding import FilterEncodingForXarray

...
encoding = FilterEncodingForXarray(dataset, "lossless")
dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")
```

Also **xarray** but with multiple variables and lossy compression:

```python
from enstools.encoding import FilterEncodingForXarray

...
specification_string = "temperature:lossy,sz,abs,0.1 precipitation:lossy,sz,pw_rel,0.001 default:lossless"
encoding = FilterEncodingForXarray(dataset, specification_string)
dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")
```

If we want to directly use **h5py** we can do the following:

```python
from enstools.encoding import FilterEncodingForH5py

...

encoding = FilterEncodingForH5py.from_string("lossless")
f = h5py.File('test.h5', 'w')
f.create_dataset('lossless_compression_using_blosc',
                 data=numpy.arange(100),
                 **encoding)
f.close()

```

Or without using specification strings:

```python
from enstools.encoding import FilterEncodingForH5py, Compressors, CompressionModes

...

encoding = FilterEncodingForH5py(Compressors.ZFP, CompressionModes.RATE, 4.0)

f = h5py.File('test.h5', 'w')
f.create_dataset('lossy_compression_with_zfp_rate_4.0',
                 data=numpy.arange(100),
                 **encoding)
f.close()

```


# Acknowledgment and license

Ensemble Tools - Encoding (`enstools-encoding`) is a collaborative development within
Waves to Weather (SFB/TRR165) coordinated by the subproject 
[Z2](https://www.wavestoweather.de/research_areas/phase2/z2) and funded by the
German Research Foundation (DFG).

A full list of code contributors can [CONTRIBUTORS.md](./CONTRIBUTORS.md).

The code is released under an [Apache-2.0 licence](./LICENSE).
