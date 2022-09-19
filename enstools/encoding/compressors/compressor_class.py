from h5py._hl.filters import FilterRefBase  # noqa


class Compressor(FilterRefBase):
    # Define the variable chunksizes
    chunksizes = None

    # Redefine _kwargs to include chunksizes
    @property
    def _kwargs(self):
        return {
            'compression': self.filter_id,
            'compression_opts': self.filter_options,
            'chunksizes': self.chunksizes,
        }

    # Make it possible to modify the elements of the object using setitem.
    def __setitem__(self, key, value):
        if key not in self._kwargs.keys():
            raise TypeError(f"{type(self)!r} object does not support item assignment for {key!r}.")

        self.__setattr__(key, value)
