"""
# to convert enstools into a namespace package, the version is now listed here and not in the level above
import pkg_resources  # part of setuptools
version = pkg_resources.require("enstools-encoding")[0].version
__version__ = version
"""

# FIXME: There should be a proper way of doing this. Meanwhile I just keep it without a __version__ variable.