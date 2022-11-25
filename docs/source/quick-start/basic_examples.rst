Basic Examples
==============

Using **lossy compression** with xarray can be as easy as adding a **single line** and an argument in the call to **.to_netcdf()** :

.. code::

    from enstools.encoding.api import FilterEncodingForXarray

    ...
    encoding = FilterEncodingForXarray(dataset, "lossy,sz,rel,1.e-4")
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")
    ...


Save an **xarray** dataset using losslessly compression:


.. code::

    from enstools.encoding.api import FilterEncodingForXarray
    ...
    encoding = FilterEncodingForXarray(dataset, "lossless")
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")


Also **xarray** but with multiple variables and lossy compression:

.. code::

    from enstools.encoding.api import FilterEncodingForXarray

    ...
    specification_string = "temperature:lossy,sz,abs,0.1 precipitation:lossy,sz,pw_rel,0.001 default:lossless"
    encoding = FilterEncodingForXarray(dataset, specification_string)
    dataset.to_netcdf(dummy_output_file, encoding=encoding, engine="h5netcdf")


If we want to directly use **h5py** we can do the following:

.. code::

    from enstools.encoding.api import FilterEncodingForH5py

    ...

    encoding = FilterEncodingForH5py.from_string("lossless")
    f = h5py.File('test.h5', 'w')
    f.create_dataset('lossless_compression_using_blosc',
                     data=numpy.arange(100),
                     **encoding)
    f.close()


Or without using specification strings:

.. code::

    from enstools.encoding.api import FilterEncodingForH5py, Compressors, CompressionModes

    ...

    encoding = FilterEncodingForH5py(Compressors.ZFP, CompressionModes.RATE, 4.0)

    f = h5py.File('test.h5', 'w')
    f.create_dataset('lossy_compression_with_zfp_rate_4.0',
                     data=numpy.arange(100),
                     **encoding)
    f.close()
