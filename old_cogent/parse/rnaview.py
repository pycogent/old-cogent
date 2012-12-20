#!/usr/bin/env python
# evo/parsers/rnaview_pairs.py

# Author Greg Caporaso
# status: development

"""Revision History
5/18-19/04 Greg Caporaso: File creation, creation of all objects used to store 
data, ie.Base, BasePair, BasePairs
5/20/04 Greg Caporaso: Added capabilites for detecting Wobble Pairs to 
support objects, changed BpList object name to BasePairs; added 
toPairsFromWobble, toPairsFromWC to BasePairs object; some parser 
methods written
5/21/04 Greg Caporaso: Completed many private methods of parser
5/24/04 Greg Caporaso: Completed public methods of parser, added functionality
of parser to translate modified bases based on translation table in pdb file
5/25/04 Greg Caporaso: Optimizaton and organization of code
5/26/04 Greg Caporaso: Modified _parse_pair_seqs() to be a little neater; 
changed toPairs* methods to raise NotImplementedError rather than BasePairsError
when handed a molecule with more than one sequence
6/3/04 Greg Caporaso: changed some variable names as suggested by Rob
6/8/04 Greg Caporaso: minor modifications based on suggestions
"""

from old_cogent.base.sequence import Rna, RnaSequence
from old_cogent.struct.rna2d import Pairs

class BaseInitError(ValueError):
    pass

class BasePairsError(ValueError):
    pass

class BasePairsInitError(BasePairsError):
    pass

class RnaViewParseError(SyntaxError):
    pass

class Base(object):
    """Essentially a struct for a nucleic acid base """

    def __init__(self,Position,Identity,Sequence):
        """ Initialize the object

            Position: the location of self in sequence, an 
                integer
            Identity: a string to serve as an abbreviation of the base, can
                be any string to allow for modified bases
            Sequence: the sequence of which self is a part of, an 
                cogent.core.sequence.RnaSequence object

            Note: no error checking is performed to ensure that
                Identity == Sequence[Position]. Since it doesn't really
                make sense that that wouldn't be the case, the user should
                be careful of this. No error checking is provided since these
                are all public variables and can be changed at anytime.
                In order to ensure that Identity == Sequence[Position] was
                always true, we'd have to overwrite methods allowing these
                values to be changed to also include error checking, which
                could really slow things down.
        """
        try:
            self.Position = int(Position)
        except ValueError:
            raise BaseInitError, 'Position must be convertable to an int'

        try:
            self.Identity = str(Identity)
        except ValueError:
            raise BaseInitError, 'Identity must be convertable to a str'

        # Better way to test for this?
        self.Sequence = Sequence
        if type(self.Sequence) is not RnaSequence:
            raise BaseInitError,\
             'Sequence must be a cogent.core.sequence.RnaSequence object'
    
    def __eq__(self,other):
        """ Overwrite the == operator """
        if self.Position != other.Position:
            return False
        if self.Identity != other.Identity:
            return False
        if self.Sequence != other.Sequence:
            return False
        return True

    def __ne__(self,other):
        """ Overwrite the != operator """
        return not self == other

    def __str__(self):
        """ Return a string constructed from the Base attributes """
        return ' '.join([str(self.Identity),str(self.Position),\
                str(self.Sequence)])

class BasePair(object):
    """ Object for storing paired RNA bases 
    
        This object is made to store two Base objects which are involved in a
            base pairing interaction with each other.
    
    """

    _wc_pairs = dict.fromkeys(['GC','CG','AU','UA'])
    _wobble_pairs = dict.fromkeys(['GU','UG'])
    
    def __init__(self,Upstream,Downstream,BpClass):
        """ Initialize the object 
            
            Upstream: the upstream Base object
            Downstream: the downstream Base object
            BpClass: the classification of the base pair
        """
        self.Upstream = Upstream
        self.Downstream = Downstream
        self.BpClass = BpClass

    def __eq__(self,other):
        """ Overwrite the == operator """
        if self.Upstream != other.Upstream:
            return False
        if self.Downstream != other.Downstream:
            return False
        if self.BpClass != other.BpClass:
            return False
        return True

    def __ne__(self,other):
        """ Overwrite the != operator """
        return not self == other

    def isWC(self):
        """ Returns True if base pair is a Watson-Crick pair 
            
        """
        # The complicated looking one-liner just makes an upper-case string
        # out of the two Base identities and checks to see if it exists in
        # self._wc_pairs
        return ''.join([self.Upstream.Identity,self.Downstream.Identity])\
                .upper() in self._wc_pairs

    def isWobble(self):
        """ Returns True if base pair is a wobble pair
        """
        # The complicated looking one-liner just makes an upper-case string
        # out of the two Base identities and checks to see if it exists in
        # self._wobble_pairs
        return ''.join([self.Upstream.Identity,self.Downstream.Identity])\
                .upper() in self._wobble_pairs

    def __str__(self):
        return ' '.join(['Up:' + str(self.Upstream) +\
                'Down:' + str(self.Downstream) + 'C:' + self.BpClass])
        

class BasePairs(list):
    """ List for storing BasePair objects corresponding to a molecule of RNA
    
    """

    def __init__(self,base_pairs=[]):
        """ Initialize the object 
            
            base_pairs: list of BasePair objects representing all base pairs 
                present in the molecule, default is []
           
            several iterators are defined:
            self: you can iterate over the base pairs since self is a list
            Sequences: iterate over all involved Sequences
            WCPairs: iterate over all Watson-Crick base pairs
            WobblePairs: iterate over all Wobble base pairs
            NonCannonicalPairs: iterate over all non-cannonical (non W/C or 
                Wobble) base pairs

            A useful application of the selective iterators is to create a 
                new BasePairs object from them. For example, if you have BasePairs
                object that contains assorted types of  base pairs,
                and you are only interested in the W-C base pairs. You
                can easily use the current object to create a new BasePairs which
                contains only the Watson-Crick base pairs:

                all_bps = BasePairs(base_pairs=list_of_all_base_pairs)
                wc_pairs = BasePairs(all_bps.WCPairs)
            
            
        """
        try:
            self[:] = list(base_pairs)
        except TypeError:
            raise BasePairsInitError, 'base_pairs must be convertable to a list'

        self._sequences = {}
        try:
            for bp in self:
                if bp.Upstream.Sequence not in self._sequences:
                    self._sequences[bp.Upstream.Sequence] = None
                if bp.Downstream.Sequence not in self._sequences:
                    self._sequences[bp.Downstream.Sequence] = None
            self._sequences = self._sequences.keys()
        except AttributeError:
            raise BasePairsInitError, 'objects in list must be BasePair objects'

    def _get_sequences(self):
        """Iterator over sequences """
        seqs = self._sequences
        for s in seqs:
            yield s
    Sequences = property(_get_sequences)

    def _get_wc_pairs(self):
        """Iterator over Watson-Crick base pairs """
        for bp in self:
            if bp.isWC():
                yield bp
    WCPairs = property(_get_wc_pairs)

    def _get_wobble_pairs(self):
        """Iterator over Wobble base pairs """
        for bp in self:
            if bp.isWobble():
                yield bp
    WobblePairs = property(_get_wobble_pairs)

    def _get_non_cannonical_pairs(self):
        """Iterator over non-cannonical base pairs """
        for bp in self:
            if not bp.isWC() and not bp.isWobble():
                yield bp
    NonCannonicalPairs = property(_get_non_cannonical_pairs)

    def toPairsFromWC(self):
        """Create cogent.struct.rna2d.Pairs object from W-C Pairs"""
        selection = []
        for bp in self.WCPairs:
            # Can only convert pairs that occur in single sequence
            if bp.Upstream.Sequence == bp.Downstream.Sequence:
                selection += [(bp.Upstream.Position,bp.Downstream.Position)]
            else:
                raise NotImplementedError, \
                    'Pairs can only handle unimolecular base pairs'
        return Pairs(selection)

    def toPairsFromWobble(self):
        """Create cogent.struct.rna2d.Pairs object from Wobble Pairs"""
        selection = []
                    
        for bp in self.WobblePairs:
            # Can only convert pairs that occur in single sequence
            if bp.Upstream.Sequence == bp.Downstream.Sequence:
                selection += [(bp.Upstream.Position,bp.Downstream.Position)]
            else:
                raise NotImplementedError, \
                    'Pairs can only handle unimolecular base pairs'
        return Pairs(selection)

class RnaViewPairsParser(object):
    """Parses base pair information from output of RnaView program """

    def __init__(self):
        """Initalize the parser object"""
        
    def __call__(self,rnaview_file,pdb_file):
        """Parse output of rnaview and pdb file into a BasePairs object 
            
            rnaview_file: an object containing the rnaview file iterable
                by line
            pdb_file: an object containing the pdb file iterable by line
            
            Usage:
                p = RnaViewPairsParser()
                bps = p(rnaview_file, pdb_file)

            bps will be a BasePairs object
            
        """
        # create a dict of all sequences in the molecule keyed by their 
        # identifier in the pdb file
        all_seqs = self._get_sequences(pdb_file)

        return self._parse_base_pairs(rnaview_file, all_seqs)

    def _parse_base_pairs(self,rnaview_file,all_seqs):
        """Build BasePairs object from data 
            data: an iterable set of lines to parse
            all_seqs: a dict of sequences keyed as in the pdb file

            
        """
        bps = []
        collecting = False
        for l in rnaview_file:
            if l.startswith('BEGIN_base-pair'):
                collecting = True
            elif l.startswith('END_base-pair'):
                collecting = False
            elif collecting:
                try:
                    bps += [self._parse_base_pair(l,all_seqs)]
                except RnaViewParseError:
                    raise RnaViewParseError, 'Parser found invalid format in line: '\
                            + str(rnaview_file.index(l) + 1)
        return BasePairs(bps)
                

    def _get_sequences(self, pdb_file):
        """Return the sequences from the pdb file in a dict

            pdb_file: a iterable sequence of lines of the pdb file 
        
            Note: the result of this function will contain both
                amino acids sequences and RNA sequences if both are present.
                It won't make any difference because the amino acid sequences
                will never be referenced, so rather than create a complicated
                way to ignore them in the parsing I choose to let them be
                parsed into the object and then ignored. (there doesn't
                seem to be an easy way to select between the two types of
                sequences due to the possibility of modified bases)
        """
        
        result = {}
        for line in pdb_file:
            if line.startswith('SEQRES'):
                words = line.split()
                if words[2].isalpha():
                    key = words[2]
                    seq_start = 4
                else:
                    key = 'A'
                    seq_start = 3
                if key not in result:
                    result[key] = words[seq_start:]
                else:
                    result[key] =result[key] + words[seq_start:]

        # Translate modified bases if necessary
        self._translate(result,self._build_translation_table(result,pdb_file))
        return result

    def _build_translation_table(self,seqs,pdb_file):
        """Create a translation table for modified bases -> cannonical bases
    
            seqs: dict of sequences in molecule
            pdb_file: a iterable sequence of lines of the pdb file 

        """
        result = {}
        seq_order = seqs.keys()
        seq_order.sort()
        for l in pdb_file:
            if l.startswith('SEQADV'):
                words = l.split()
                if words:
                    try:
                        # grab the necessary data
                        modified_base = words[2]
                        seq = words[3]
                        index = int(words[4])
                        cannonical_base = words[7]
                        if cannonical_base not in dict.fromkeys('AGCU'):
                            raise ValueError
                        # if there are multiple sequences the position
                        # will need to be modified accordingly
                        sum_prior = 0
                        for e in seq_order[:seq_order.index(seq)]:
                            sum_prior += len(seqs[e])
                    # if the data is corrupt an IndexError may occur
                    except (ValueError,IndexError):
                        raise RnaViewParseError,\
                      'Cannot parse modified base translation table'
                    # Construct the necessary dictionary components to 
                    # store the translation information
                    if seq not in result:
                        result[seq] = {modified_base:{}}
                    elif modified_base not in result[seq]:
                        result[seq][modified_base] = {}
                    # store the information
                    result[seq][modified_base][index-1-sum_prior] = \
                            cannonical_base.lower()
        return result

    def _translate(self,seqs,trans_table):
        """Translate modified bases to lower case tagged cannonical bases """
        cannonical_bases = dict.fromkeys(list('AGCUagcu'))
        for s in seqs:
            try:
                # for each modified base in the translation table
                for mb in trans_table[s]:
                    # for each index the modified base appears at
                    for i in trans_table[s][mb]:
                            try:
                                # before altering the sequence, make sure 
                                # the modified base appears where the 
                                # translation table says it does
                                if seqs[s][int(i)] == mb:
                                    # if so, swap the translated value into
                                    # the sequence
                                    seqs[s][int(i)] = trans_table[s][mb][i]
                                # if not, there is an error
                                else:
                                    raise RnaViewParseError,\
                                        'Could not translate modified bases'
                            except IndexError:
                                # the index for modification is out of range
                                # so skip it
                                pass
            except KeyError:
                # No translations for current sequence so skip it
                pass
                        
    def _parse_positions(self,raw):
        """Parse positions from raw position data """
        try:
            # remove trialing ',' and split on the '_'
            result = raw[0:-1].split('_')
            # Convert to array style numbering (starting at 0),
            # also ensures that values can be treated as int
            result[0] = int(result[0]) - 1
            result[1] = int(result[1]) - 1
        except (ValueError,IndexError):
            raise RnaViewParseError, 'Line does not contain valid base pair description'
           
        return result

    def _parse_pair_seqs(self,first,second,all_seqs):
        """Parse the sequences corresponding to each base"""
        try:
            result = ['A','A']
            for i,s in enumerate([first,second]):
                if s != ':':
                    result[i] = s[0]
                if result[i] not in all_seqs:
                    raise ValueError
        except (IndexError,ValueError):
            raise RnaViewParseError, 'Line does not contain valid base pair description'
        
        return result

    def _parse_bases(self,raw):
        """Parse the base identities """
        try:
            # Get identity of bases
            result = raw.split('-')
            allowed_bases = dict.fromkeys(list('ACUGacug'))
            # explicit test, is there a better way to do this?
            for b in result:
                if b not in allowed_bases:
                    raise RnaViewParseError, 'Line does not contain valid base pair description'
            return result
        except IndexError:
            raise RnaViewParseError, 'Line does not contain valid base pair description'
       
    def _parse_bpclass(self,first,second=None):
        """Parse the BpClass data """
        # BpClass can be made of two components, the first is always
        # BpClass data, the second may or may not be BpClass data, depending on
        # it's value
        result = str(first)
        
        if second and (second == 'cis' or second == 'tran'\
                or second == 'stacked'):
            result = ' '.join([result,second])
        
        return result

    def _adjust_positions(self,positions,pair_seqs,all_seqs):
        """Adjust positions to represent positions in individual sequences 
            
            This is necessary because the numbering represents the sequences
                as being one long sequence and we want numbering based on the
                individual sequences.
        """
        seq_order = all_seqs.keys()
        seq_order.sort()
        for i,s in enumerate(pair_seqs):
            sum_lengths = 0
            try:
                for s in seq_order[:seq_order.index(s)]:
                    sum_lengths += len(all_seqs[s])
            except (ValueError,KeyError):
                raise RnaViewParseError, 'Line does not contain valid base pair description'
            positions[i] = positions[i] - sum_lengths

    def _adjust_stream_order(self,positions,pair_seqs,all_seqs):
        """Return description of which base is Upstream and which is Downstream
        """
        seq_order = all_seqs.keys()
        seq_order.sort()
        # make the first read the upstream and the second read the
        # downstream by default
        up = 0
        down = 1
        # if the bases of the pair belong to different sequences and
        # the upstream doens't come before the downstream in the alphabet
        # reverse their order
        if pair_seqs[up] != pair_seqs[down]:
            if seq_order.index(pair_seqs[up]) > seq_order.index(pair_seqs[down]):
                up, down = down, up
        # if the bases are of the same sequence, make sure the one that
        # occurs eariler in the sequence (smaller index) is upstream
        elif positions[up] > positions[down]:
            up, down = down, up
        return up,down

    def _parse_base_pair(self,line,all_seqs):
        """Given a line describing a base pair return a BasePair object """
        data = line.split()
        
        # Get sequence ids
        try:
            positions = self._parse_positions(data[0])
            pair_seqs = self._parse_pair_seqs(data[1],data[5],all_seqs)
            bases = self._parse_bases(data[3]) 
            try:
                bp_class = self._parse_bpclass(data[6],data[7])
            except IndexError:
                bp_class = self._parse_bpclass(data[6])
        except IndexError:
            raise RnaViewParseError, 'Line does not contain valid base pair description'


        # if the data is from more than one sequence we will
        # need to adjust the positions accordingly
        self._adjust_positions(positions,pair_seqs,all_seqs)            
       
        # Determine which base is upstream and which is downstream
        up,down = self._adjust_stream_order(positions,pair_seqs,all_seqs)
        
        try:        
            return BasePair(Upstream=Base(Position=positions[up],\
                    Identity=bases[up],\
                    Sequence=Rna(all_seqs[pair_seqs[up]])),\
                    Downstream=Base(Position=positions[down],\
                    Identity=bases[down],\
                    Sequence=Rna(all_seqs[pair_seqs[down]])),\
                    BpClass=bp_class)
        except KeyError:
            raise RnaViewParseError, 'Line does not contain valid base pair description' 

def BasePairsFromFile(rnaview_file,pdb_file):
    """Given a rnaview output and pdb file return a BasePairs object

        rnaview_file: a file or list of lines containing the output
            of rnaview. This is not a path to a file!
        pdb_file: a file or list of lines containing the pdb file used
            to generate the rnaview output. This is not a path to a file!
    """
    p = RnaViewPairsParser()
    return p(rnaview_file,pdb_file)
    

