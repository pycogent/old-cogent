#!/usr/bin/env python
# cogent.app.meme.py
"""Provides an application controller for the commandline version of:
MEME

Owner: Jeremy Widmann (jeremy.widmann@colorado.edu)

Status: Development

Revision History:

Written July 2005 by Jeremy Widmann
"""
from old_cogent.app.parameters import FlagParameter, ValuedParameter, \
    MixedParameter
from old_cogent.app.util import CommandLineApplication, ResultPath
from old_cogent.format.fasta import fasta_from_sequences, fasta_from_alignment
from old_cogent.parse.meme import MemeParser
from old_cogent.parse.fasta import MinimalFastaParser,FastaParser
from old_cogent.base.align import Alignment
from old_cogent.motif.util import Motif
from tempfile import mkstemp

class MEME(CommandLineApplication):
    """MEME application controller.
    
    Parameters organized by as presented in MEME help file.
    """
    
    _help = {'-h':FlagParameter('-','h',Value=False)}
    
    #Alphabet MEME uses. Protein by default
    _alphabet = {\
        '-dna':FlagParameter('-','dna',Value=False),
        '-protein':FlagParameter('-','protein',Value=False)}
        
    #Distribution of motifs
    _distribution = {\
        '-mod':ValuedParameter('-','mod',Value='anr',Delimiter=' ')}
    
    #Number of motifs. Default = 1
    _number_of_motifs = {\
        '-nmotifs':ValuedParameter('-','nmotifs',Delimiter=' '),
        '-evt':ValuedParameter('-','evt',Delimiter=' ')}
    
    _number_of_motif_occurences = {\
        '-nsites':ValuedParameter('-','nsites',Delimiter=' '),
        '-minsites':ValuedParameter('-','minsites',Delimiter=' '),
        '-maxsites':ValuedParameter('-','maxsites',Delimiter=' '),
        '-wnsites':ValuedParameter('-','wnsites',Delimiter=' ')}
    
    _motif_width = {\
        '-w':ValuedParameter('-','w',Delimiter=' '),
        '-minw':ValuedParameter('-','minw',Delimiter=' '),
        '-maxw':ValuedParameter('-','maxw',Delimiter=' '),
        '-nomatrim':FlagParameter('-','nomatrim',Value=False),
        '-wg':ValuedParameter('-','wg',Delimiter=' '), #Default=11
        '-ws':ValuedParameter('-','ws',Delimiter=' '), #Default=1
        '-noendgaps':FlagParameter('-','noendgaps',Value=False)}
        
    _background_model = {\
        '-bfile':ValuedParameter('-','bfile',Delimiter=' ')}
    
    _dna_palindromes_and_strands = {\
        '-revcomp':FlagParameter('-','revcomp',Value=False),
        '-pal':FlagParameter('-','pal',Value=False)}
    
    _em_algorithm = {\
        '-maxiter':ValuedParameter('-','maxiter',Delimiter=' '),   #Default=50
        '-distance':ValuedParameter('-','distance',Delimiter=' '),#Default=0.001
        '-prior':ValuedParameter('-','prior',Delimiter=' '), 
        #Default=dirichlet for -dna, Default=dmix for -protein
        '-b':ValuedParameter('-','b',Delimiter=' '),
        #Default=0.01 if prior=dirichlet, Default=0 if prior=dmix
        '-plib':ValuedParameter('-','plib',Delimiter=' ')}
    
    _selecting_starts_for_em = {\
        '-spfuzz':ValuedParameter('-','spfuzz',Delimiter=' '),
        '-spmap':ValuedParameter('-','spmap',Delimiter=' '),
        '-cons':ValuedParameter('-','cons',Delimiter=' ')}
    
    _output = {\
        '-text':FlagParameter('-','text',Value=True),
        '-maxsize':ValuedParameter('-','maxsize',Delimiter=' '),
        '-nostatus':FlagParameter('-','nostatus',Value=False),
        '-p':ValuedParameter('-','p',Delimiter=' '),
        '-time':ValuedParameter('-','time',Delimiter=' '),
        '-sf':ValuedParameter('-','sf',Delimiter=' ')}
    
    _parameters = {}
    _parameters.update(_help)
    _parameters.update(_alphabet)
    _parameters.update(_distribution)
    _parameters.update(_number_of_motifs)
    _parameters.update(_number_of_motif_occurences)
    _parameters.update(_motif_width)
    _parameters.update(_background_model)
    _parameters.update(_dna_palindromes_and_strands)
    _parameters.update(_em_algorithm)
    _parameters.update(_selecting_starts_for_em)
    _parameters.update(_output)
    
    _command='meme'
    _working_dir='/tmp/meme'
    _suppress_stderr=True
    
    #def _input_as_lines(self,data):
    #    """ Write a seq of lines to a temp file and return the filename string
    #    
    #        data: a sequence to be written to a file, each element of the 
    #            sequence will compose a line in the file
#
#            Note: '\n' will be stripped off the end of each sequence element
#                before writing to a file in order to avoid multiple new lines
#                accidentally be written to a file
#        """
#        filename = self._input_filename = mkstemp(dir=self.WorkingDir)[1]
#        data_file = open(filename,'w')
#        data_file.write(data)
#        data_file.close()
#        return filename

def add_p_values(meme_results):
    """Adds P values to the Modules in meme_results.
    
        - meme_results must have an Alignment.
    """
    aln_length = 0
    for seq in meme_results.Alignment.values():
        aln_length += len(seq)
    for motif in meme_results.Motifs:
        for module in motif.Modules:
            module.Pvalue = module.Evalue/aln_length
    return meme_results

def findMotifsFromSeqs(seqs,Alphabet=None):
    """Runs MEME using alignment created from list of sequences.
        
        - Returns MotifResults object.
        - seqs can be Sequence objects or strings.
    """
    #Make Fasta Alignment
    fasta_aln = fasta_from_sequences(seqs)
    #Make an Alignment object
    aln = Alignment(list(FastaParser(fasta_aln)))
    app = MEME(InputHandler='_input_as_multiline_string')
    if Alphabet == 'dna':
        app.Parameters['-dna'].on()
    else:
        app.Parameters['-protein'].on()
        app.Parameters['-maxw'].Value = 40 
        app.Parameters['-nmotifs'].Value = 20 
        app.Parameters['-evt'].Value = 0.01 

    app.Parameters['-mod'].Value = "anr"
    app.Parameters['-maxsize'].Value = len(fasta_aln) + 1 
    print app.BaseCommand
    output = app(fasta_aln)
    meme_results = MemeParser(output['StdOut'].readlines())
    meme_results.Alignment = aln
    return add_p_values(meme_results)

def findMotifsFromAlignment(aln,WorkingDir=None):
    """Runs MEME using an Alignment object.
    
        - Returns MotifResults object
        - seqs can be an Alignment object or dict
    """
    #Make Fasta Alignment
    fasta_aln = fasta_from_alignment(aln)
    #Make sure aln is Alignment object
    aln = Alignment(aln)
    app = MEME(InputHandler='_input_as_lines')
    output = app(fasta_aln)
    meme_results = MemeParser(output['StdOut'])
    meme_results.Alignment = aln
    return add_p_values(meme_results)

def findMotifsFromFile(filename,Alphabet=None):
    """Runs MEME using a Fasta file.
    
        - Returns MotifResults object.
    """
    #Make an Alignment object
    aln = Alignment(list(MinimalFastaParser(open(filename))))
    app = MEME(InputHandler='_input_as_string')
    if Alphabet == 'dna':
        app.Parameters['-dna'].on()
    print app.BaseCommand
    output = app(filename)
    print app.BaseCommand
    print 'standard out'
    print output['StdOut']
    print 'standard error'
    print output['StdErr']
    meme_results = MemeParser(output['StdOut'])
    meme_results.Alignment = aln
    return add_p_values(meme_results)
    
