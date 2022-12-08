class EnstoolsCompressionError(Exception):
    ...


class WrongCompressionSpecificationError(EnstoolsCompressionError):
    ...


class WrongCompressionModeError(EnstoolsCompressionError):
    ...


class WrongCompressorError(EnstoolsCompressionError):
    ...


class WrongParameterError(EnstoolsCompressionError):
    ...


class CompressionStringFormatException(EnstoolsCompressionError):
    ...


class FilterNotAvailable(EnstoolsCompressionError):
    ...
