from h5py._hl.filters import FilterRefBase  # noqa


class Compressor(FilterRefBase):
    chunksizes = None

    @property
    def _kwargs(self):
        return {
            'compression': self.filter_id,
            'compression_opts': self.filter_options,
            'chunksizes': self.chunksizes,
        }

    def __setitem__(self, key, value):
        if key not in self._kwargs.keys():
            raise TypeError(f"{type(self)!r} object does not support item assignment for {key!r}.")

        self.__setattr__(key, value)
