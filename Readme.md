# enstools-encoding [![Documentation Status](https://readthedocs.org/projects/enstools/badge/?version=latest)](https://enstools-encoding.readthedocs.io/en/latest/?badge=latest)

Library to generate the encodings to write compressed files as easily as possible with **xarray** using **hdf5 filters**.

Its only capability is to provide the encodings that **xarray** and **h5py** need in order to write files using filters.

The package doesn't provide the filters, need to be installed separately.

This package was originally inside [Ensemble Tools](https://github.com/wavestoweather/enstools) but can be used standalone.

It is also a building block for [Ensemble Tools - Compression](https://github.com/wavestoweather/enstools-compression),
which includes a command line tool to make compression even easier, along with other useful tools to find proper compression parameters.

It has been developed under the [Waves to Weather - Transregional Collaborative Research 
Project (SFB/TRR165)](https://wavestoweather.de). 

## Compressors
At the current stage it is possible to generate encodings for three compressors:
- [BLOSC](https://github.com/Blosc/hdf5-blosc)
- [SZ](https://github.com/szcompressor/SZ)
- [ZFP](https://github.com/LLNL/H5Z-ZFP)

# Installation

`pip` is the easiest way to install `enstools-encoding` along with all dependencies.

    pip install enstools-encoding

# Documentation

Explore [our documentation](https://enstools-encoding.readthedocs.io).          

# Acknowledgment and license

Ensemble Tools (`enstools`) is a collaborative development within
Waves to Weather (SFB/TRR165) coordinated by the subproject 
[Z2](https://www.wavestoweather.de/research_areas/phase2/z2) and funded by the
German Research Foundation (DFG).

A full list of code contributors can [CONTRIBUTORS.md](./CONTRIBUTORS.md).

The code is released under an [Apache-2.0 licence](./LICENSE).
