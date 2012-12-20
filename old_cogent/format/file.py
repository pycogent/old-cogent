#!/usr/bin/env python
#file evo/writers/file.py

"""Public functions to read/write files.

Revision History:
08/22/03 Amanda Birmingham: created from public functions culled from 
    webtools.py
09/30/03 Amanda Birmingham: removed getNewId function; placed in
    general_tools, since it really belongs more there.
01/20/04 Amanda Birmingham: updated to fit into cvsroot and use packages.
"""

def getFileAsString(file_name):
    """Returns string of contents of file with input name."""

    #open and read the file
    requested_file = open(file_name)
    result = requested_file.read()

    #close the file and return the contents
    requested_file.close() 
    return result
#end getFileAsString

def writeFileFromString(file_name, file_string, use_append = False):
    """Writes a file with the given filename and contents.
    
    file_name: the name of the file to write, including (if needed) path.
    file_string: the contents of the new file as a string.
    use_append: a boolean.  False is default and means that file is opened 
        for write.  True means the file is opened for append.
    """
    
    #default write mode is w, but can be set to be a
    write_mode = "w"
    if use_append: write_mode = "a"

    #open the file
    script_file = open(file_name, write_mode)

    #write the string contents
    script_file.write(file_string)

    #close the file
    script_file.close()
# end writeFileFromString