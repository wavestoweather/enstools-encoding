# Using a module file to store the desired chunk size.

# Chunk size used to save files to disk
chunk_size = "10MB"

# Chunk size used for the analysis
analysis_chunk_size = "100KB"
def change_chunk_size(new_chunk_size: str):
    global chunk_size
    chunk_size = new_chunk_size

# This variable will be used in many places.
# One can modify this variable directly assigning a new value
# enstools.encoding.chunk_size.chunk_size = "1MB"
# or using the function change_chunk_size("1MB")

