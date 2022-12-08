"""
Setup file for enstools-encoding
"""
from setuptools import setup

# Use the Readme file as long description.
try:
    with open("Readme.md", "r") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""


def get_version():
    from pathlib import Path
    version_path = Path(__file__).parent / "VERSION"
    with version_path.open() as version_file:
        return version_file.read().strip()


# perform the actual install operation
setup(name="enstools-encoding",
      version=get_version(),
      author="Oriol Tintó",
      author_email="oriol.tinto@lmu.de",
      long_description=long_description,
      long_description_content_type='text/markdown',
      url="https://github.com/wavestoweather/enstools-encoding",
      packages=["enstools.encoding", "enstools.encoding.compressors"],
      namespace_packages=['enstools'],

      install_requires=[
          "xarray",
          "PyYAML",
          "h5py",
          "h5netcdf",
          "hdf5plugin",
      ],
      )
