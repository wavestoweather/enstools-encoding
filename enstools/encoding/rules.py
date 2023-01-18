"""
Different rules to format the compression specification string as well as some default values.
"""

# Separator between two variable entries
VARIABLE_SEPARATOR = " "

# Separator between the variable name and the compression specification
VARIABLE_NAME_SEPARATOR = ":"

# Separator between the compression type, the compressor, the mode and the parameter
COMPRESSION_SPECIFICATION_SEPARATOR = ","

# Default Labels
DATA_DEFAULT_LABEL = "default"
COORD_LABEL = "coordinates"

# Default Values
DATA_DEFAULT_VALUE = "lossless"
COORD_DEFAULT_VALUE = "lossless"

# Lossless defaults
LOSSLESS_DEFAULT_BACKEND = "lz4"
LOSSLESS_DEFAULT_COMPRESSION_LEVEL = 5
