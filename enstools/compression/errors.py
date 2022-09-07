class EnstoolsCompressionError(Exception):
    ...


class WrongCompressionSpecificationError(EnstoolsCompressionError):
    ...


class WrongCompressionModeError(EnstoolsCompressionError):
    ...


class CompressionStringFormatException(EnstoolsCompressionError):
    ...


class FilterNotAvailable(EnstoolsCompressionError):
    ...
