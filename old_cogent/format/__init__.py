#!/usr/bin/env python
#file cogent/format/__init__.py
"""Package cogent.format: provides modules for writing specific file formats.

Currently provides:
    mage: writers for the MAGE 3D visualization program
    xml:  xml base class
    file: general functions to read and write files

Revision History

Written 2003 by Sandra Smit and Rob Knight

11/12/03 Rob Knight: added svg (from evo.graphics) and xml (from evo) to this
package.
01/20/04 Amanda Birmingham: added file (from evo) to this package.
"""
all = ['mage', 'xml', 'file']

"""Need writers for:
    
    -various sequence and alignment file formats

    -various motif file formats

    -various phylogeny file formats

    -sql?
"""
