"""
This module provides exceptions related to compression in Enstools.

"""


class EnstoolsCompressionError(Exception):
    """
    Base exception class for Enstools compression-related errors.
    """


class InvalidCompressionSpecification(EnstoolsCompressionError):
    """
    Exception raised for an invalid compression specification.
    """
