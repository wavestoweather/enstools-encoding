"""
Setup file for easycompression
"""
from setuptools import setup

# perform the actual install operation
setup(name="enstools-encoding",
      version="0.1.0",
      author="Oriol Tintó",
      author_email="oriol.tinto@lmu.de",
      packages=[f"enstools.encoding"],
      namespace_packages=['enstools'],

      install_requires=[
          "xarray",
          "PyYAML",
          "h5py",
          "h5netcdf",
      ],
      )
