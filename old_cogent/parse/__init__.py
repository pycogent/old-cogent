#!/usr/bin/env python
#file evo/parsers/__init__.py

"""parsers: provides support libraries and parsers for various file formats.

Usage: import cogent.parse

Revision History:

Package created 10/9/03 by Rob Knight.

11/12/03 Rob Knight: added fasta and sprinzl.

12/28/03 Rob Knight: added tree and clustal.
"""

__all__ = [ 'aaindex', 'bpseq', 'clustal', 'cutg', 'fasta', 
            'locuslink', 'ncbi_taxonomy',
            'rdb', 'record', 'record_finder', 
            'sprinzl', 'tree', 'unigene']

"""Need to add:

    rfam            RNA families database
    genbank         GenBank flat file
    go              Gene Ontology
    cdd             Conserved Domain Database
    kegg            KEGG metabolic pathways and related file formats
    pfam            Protein families database
    pdb             Protein Data Bank
    ndb             Nucleotide Data Bank ('Atlas' files)
    tcoffee         TCoffee multiple alignment format
    embl (?)        EMBL flat file format
    mmdb (?)        mmdb format from NCBI
    some sort of SNP format
    some sort of literature format, presumably PubMed
"""
