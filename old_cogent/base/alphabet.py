#! /usr/bin/env python
# file evo/alphabet.py
"""Contains information about Alphabets, amino acids, and RNA and DNA bases.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development -- feedback requested

Revision History

9/1/03 Rob Knight: Written based on earlier file aminoAcid.py by Greg
Caporaso, which was written on or before 8/25/03.

10/14/03 Rob Knight: Renamed to alphabet.py and modified to include information
for RNA and DNA monomers, and the Alphabet class.

11/3/03 Rob Knight: Separated out MatchMaker and PairMaker, primarily for
debugging purposes. Renamed couldMatch and couldMisMatch. Added mustMatch, 
canPair, canMispair, and mustPair.

11/6/03 Rob Knight: added RNAWCAlphabet for situations where only Watson-Crick
pairs are desired.

11/8/03 Rob Knight: added delta to MW to allow custom molecular weights to be
passed in.

4/7/04 Rob Knight: added isGap, gapVector, and gapMaps methods to Alphabet
(the latter two of these were based on standalone code by Cathy Lozupone). 
Changed implementation of gapList to make it shorter and clearer.

6/3/04 Rob Knight: added InverseDegenerate property to Alphabet, and added
degenerateFromSequence() method that returns the least degenerate symbol that
describes the sequence used as input. Per the Cogent alphabet object, added '?'
as a symbol that could be either a base or a gap.

01/19/06 Zongzhi isValidStrict is added.
"""
from pdb import set_trace
from old_cogent.util.misc import FunctionWrapper, add_lowercase, iterable, if_
from old_cogent.util.transform import allchars, keep_chars
from sets import Set, ImmutableSet
from random import choice
from string import maketrans, upper

class FoundMatch(Exception):
    """Raised when a match is found in a deep loop to skip many levels"""
    pass

class Monomer(object):
    """Contains name, symbols, and MW for a particular monomer.

    Usage : x = Monomer(OneLetter, ThreeLetter, Name)
    
    OneLetter :  one-letter symbol for amino acid, uppercase
    ThreeLetter: three-letter code for amino acid, first uppercase
    Name:        name of the amino acid
    MW:          molecular weight of the amino acid, Daltons

    Other attributes (e.g. hydrophobicity, pKa, etc.) will be looked up in
    tables keyed by the one-letter symbol.
    
    Monomers should be treated as immutable, though this is enforced by
    convention rather than by code.
    """
    def __init__(self, OneLetter, ThreeLetter, Name, MW, **kwargs):
        self.OneLetter = OneLetter
        self.ThreeLetter = ThreeLetter
        self.Name = Name
        self.MW = MW
        self.__dict__.update(kwargs)

    def __str__(self):
        """Returns one-letter code for amino acid"""
        return self.OneLetter

    def __cmp__(self, other):
        """Default sort is alphabetical by symbol"""
        return cmp(str(self), str(other))

AminoAcidData = [Monomer(*data) for data in [
    ["A", "Ala", "Alanine", 89.09],
    ["C", "Cys", "Cysteine",  121.16],
    ["D", "Asp", "Aspartate", 133.10],
    ["E", "Glu", "Glutamate",  147.13],
    ["F", "Phe", "Phenylalanine", 165.19],
    ["G", "Gly", "Glycine",  75.07],
    ["H", "His", "Histidine", 155.16],
    ["I", "Ile", "Isoleucine", 131.18],
    ["K", "Lys", "Lysine", 146.19],
    ["L", "Leu", "Leucine", 131.18],
    ["M", "Met", "Methionine", 149.21],
    ["N", "Asn", "Asparagine", 132.12],
    ["P", "Pro", "Proline", 115.13],
    ["Q", "Gln", "Glutamine", 146.15],
    ["R", "Arg", "Arginine", 174.20],
    ["S", "Ser", "Serine",  105.09],
    ["T", "Thr", "Threonine", 119.12],
    ["V", "Val", "Valine", 117.15],
    ["W", "Trp", "Tryptophan", 204.23],
    ["Y", "Tyr", "Tyrosine", 181.19],
    ["*", "Ter", "Stop", 0],
    ["U", "Sec", "Selenocysteine", 168.06],
    ]]

#build dict of AminoAcid objects keyed by symbol
AminoAcids = dict([(str(i), i) for i in AminoAcidData])

RnaData = [Monomer(*data) for data in [
    ["A", "Ade", "Adenine", 313.21],
    ["U", "Ura", "Uracil", 290.17],
    ["C", "Cyt", "Cytosine", 289.19],
    ["G", "Gua", "Guanine", 329.21],
]]

RnaBases = dict([(str(i), i) for i in RnaData])

DnaData = [Monomer(*data) for data in [
    ["A", "Ade", "Adenine", 297.21],
    ["T", "Thy", "Thymine", 274.17],
    ["C", "Cyt", "Cytosine", 273.19],
    ["G", "Gua", "Guanine", 313.21],
]]
DnaBases = dict([(str(i), i) for i in DnaData])


def MatchMaker(monomers=None, gaps=None, degenerates=None):
    """Makes a dict of symbol pairs (i,j) -> strictness.

    Strictness is True if i and j always match and False if they sometimes
    match (e.g. A always matches A, but W sometimes matches R).
    """
    result = {}
    #allow defaults to be left blank without problems
    monomers = monomers or {}
    gaps = gaps or {}
    degenerates = degenerates or {}
    #all monomers always match themselves and no other monomers
    for i in monomers:
        result[(i,i)] = True
    #all gaps always match all other gaps
    for i in gaps:
        for j  in gaps:
            result[(i,j)] = True
    #monomers sometimes match degenerates that contain them
    for i in monomers:
        for j in degenerates:
            if i in degenerates[j]:
                result[(i,j)] = False
                result[(j,i)] = False
    #degenerates sometimes match degenerates that contain at least one of
    #the same monomers
    for i in degenerates:
        for j in degenerates:
            try:
                for i_symbol in degenerates[i]:
                    if i_symbol in degenerates[j]:
                        result[(i,j)] = False
                        raise FoundMatch
            except FoundMatch:
                pass    #just using for flow control
    return result


def PairMaker(pairs=None, monomers=None, gaps=None, degenerates=None):
    """Expands pairs into all possible pairs using degen symbols."""
    result = {}
    #allow defaults to be left blank without problems
    pairs = pairs or {}
    monomers = monomers or {}
    gaps = gaps or {}
    degenerates = degenerates or {}
    #add in the original pairs: should be complete monomer pairs
    result.update(pairs)
    #all gaps 'weakly' pair with each other
    for i in gaps:
        for j in gaps:
            result[(i,j)] = False
    #monomers sometimes pair with degenerates if the monomer's complement
    #is in the degenerate symbol
    for i in monomers:
        for j in degenerates:
            found = False
            try:
                for curr_j in degenerates[j]:
                    #check if (i,curr_j) and/or (curr_j,i) is a valid pair:
                    #not mutually required if pairs are not all commutative!
                    if (i, curr_j) in pairs:
                        result[(i,j)] = False
                        found = True
                    if (curr_j, i) in pairs:
                        result[(j,i)] = False
                        found = True
                    if found:
                        raise FoundMatch
            except FoundMatch:
                pass    #just using for flow control
    #degenerates sometimes pair with each other if the first degenerate
    #contains the complement of one of the bases in the second degenerate
    for i in degenerates:
        for j in degenerates:
            try:
                for curr_i in degenerates[i]:
                    for curr_j in degenerates[j]:
                        if (curr_i, curr_j) in pairs:
                            result[(i,j)] = False
                            raise FoundMatch
            except FoundMatch:
                pass    #just using for flow control
    #don't forget the return value!
    return result


def first_(attrname, inverse=False):
    def first(self, sequence):
        attr = getattr(self, attrname)
        for i, s in enumerate(sequence):
            if (not inverse and s in attr) \
                    or (inverse and not s in attr):
                return i
        return None
    first.__doc__ = \
    """Returns the index of the first char %s within self.%s in the \
    sequence, or None.""" % (if_(inverse, 'not', ''), attrname)
    return first

class Alphabet(object):
    """Class defining interface for alphabet operations."""

    def __init__(self, Monomers, Degenerates=None, Gaps=None, Complements=None,
        Order=None, Pairs=None, WeightAdjust=0, add_lower=True):
        """Returns new Alphabet object, minimally initialized with monomers.

        Monomers:   Dict of monomers, keyed by symbol. Expect 1-letter and
                    3-letter symbols, name, and molecular weight (in chain).
        Degenerate: Dict of degenerate symbol -> monomer mapping.
        Gaps:       Dict of valid gap symbols.
        Complements:Dict of monomer -> complement (optional).
        Order:      Customary order in which symbols appear. Used by __iter__.
        Pairs:      Dict of tuples containing valid, non-degenerate pairs.
        WeightAdjust: Weight added for terminal residue
        add_lower:  Whether or not to add lowercase chars (default True)

        NOTE: All of Monomers, Degenerates, Gaps, Complements, Order, Pairs 
        _must_ support keys() and items() if present.

        Alphabets should be treated as immutable, though at present there is
        no explicit code to enforce this. However, the Alphabet makes
        several additional variables on creation, which would need to be
        handled carefully if some of the Alphabet's components were changed.
        """
        self.Monomers = Monomers
        self.Degenerates = Degenerates or {}
        self.Gaps = Gaps or {}
        self.Complements = Complements or {}
        self.Matches = MatchMaker(Monomers, Gaps, Degenerates)
        self.Pairs = Pairs or {}
        self.Pairs.update(PairMaker(Pairs, Monomers, Gaps, Degenerates))
        
        self._add_order(Order)
        self.WeightAdjust = WeightAdjust
        if add_lower:
            self._add_lowercase()
        self._make_all()
        self._make_comp_table()
        self.GapString = ''.join(self.Gaps.keys())
        self.stripDegenerate = FunctionWrapper(
            keep_chars(self.GapString+self.Order))
        self.stripBad = FunctionWrapper(keep_chars(''.join(self.All.keys())))
        self.stripBadAndGaps = FunctionWrapper(keep_chars(
        ''.join(map(''.join,[self.Monomers.keys(),self.Degenerates.keys()]))))

        #make inverse degenerates from degenerates
        #ensure that lowercase versions also exist
        inv_degens = {}
        for key, val in self.Degenerates.items():
            inv_degens[ImmutableSet(val)] = key
            inv_degens[ImmutableSet(val.lower())] = key.lower()
        for m in self.Monomers:
            inv_degens[ImmutableSet(m)] = m
            inv_degens[ImmutableSet(m.lower())] = m.lower()
        for m in self.Gaps:
            inv_degens[ImmutableSet(m)] = m
        self.InverseDegenerates = inv_degens
            

    def _add_order(self, order):
        """Uses sort order if present, or constructs from sorted monomers."""
        if order:
            self.Order = order
        else:
            items = self.Monomers.keys()
            items.sort()
            self.Order = ''.join(items)

    def _add_lowercase(self):
        """Adds lowercase versions of keys and vals to each internal dict."""
        for d in (self.Monomers, self.Degenerates, self.Gaps, self.Complements,
            self.Pairs, self.Matches):
            add_lowercase(d)

    def _make_all(self):
        """Sets self.All, which contains all the symbols self knows about.
        
        Note that the value of items in self.All will be the string containing
        the possibly degenerate set of symbols that the items expand to.
        """
        all = {}
        for i in self.Monomers:
            curr = str(i)
            all[i] = i
        for key, val in self.Degenerates.items():
            all[key] = val
        for i in self.Gaps:
            all[i] = i
        self.All = all

    def _make_comp_table(self):
        """Sets self.ComplementTable, which maps items onto their complements.

        Note: self.ComplementTable is only set if self.Complements exists.
        """
        if self.Complements:
            self.ComplementTable = maketrans(''.join(self.Complements.keys()), 
                                             ''.join(self.Complements.values()))
    def complement(self, item):
        """Returns complement of item, using data from self.Complements.
       
        Always tries to return same type as item: if item looks like a dict,
        will return list of keys.
        """
        if not self.Complements:
            raise TypeError, \
            "Tried to complement sequence using alphabet without complements."
        try:
            return item.translate(self.ComplementTable)
        except (AttributeError, TypeError):
            item = iterable(item)
            get = self.Complements.get
            return item.__class__([get(i, i) for i in item])

    def rc(self, item):
        """Returns reverse complement of item w/ data from self.Complements.
        
        Always returns same type as input.
        """
        comp = list(self.complement(item))
        comp.reverse()
        if isinstance(item, str):
            return item.__class__(''.join(comp))
        else:
            return item.__class__(comp)

    def __contains__(self, item):
        """An Alphabet contains every character it knows about."""
        return item in self.All

    def __iter__(self):
        """An Alphabet iterates only over its monomers."""
        return iter(self.Order)

    def isGap(self, char):
        """Returns True if char is a gap."""
        return char in self.Gaps

    def isGapped(self, sequence):
        """Returns True if sequence contains gaps."""
        return self.firstGap(sequence) is not None

    def isDegenerate(self, sequence):
        """Returns True if sequence contains degenerate characters."""
        return self.firstDegenerate(sequence) is not None

    def isValid(self, sequence):
        """Returns True if sequence contains no items that are not in self."""
        try:
            return self.firstInvalid(sequence) is None
        except:
            return False

    def isStrict(self, sequence):
        """Returns True if sequence contains only items in self.Monomers."""
        try:
            return (len(sequence)==0) or (self.firstNonStrict(sequence) is None)
        except:
            return False

    def isValidStrict(self, sequence):
        """Returns True if sequence contains only items in self.Order"""
        try:
            return (len(sequence)==0) \
                    or (self.firstNonValidStrict(sequence) is None)
        except:
            return False
    
    firstNonValidStrict = first_('Order', inverse=True)

    def firstGap(self, sequence):
        """Returns the index of the first gap in the sequence, or None."""
        gap = self.Gaps
        for i, s in enumerate(sequence):
            if s in gap:
                return i
        return None

    def firstDegenerate(self, sequence):
        """Returns the index of first degenerate symbol in sequence, or None."""
        degen = self.Degenerates
        for i, s in enumerate(sequence):
            if s in degen:
                return i
        return None

    def firstInvalid(self, sequence):
        """Returns the index of first invalid symbol in sequence, or None."""
        all = self.All
        for i, s in enumerate(sequence):
            if not s in all:
                return i
        return None

    def firstNonStrict(self, sequence):
        """Returns the index of first non-strict symbol in sequence, or None."""
        monomers = self.Monomers
        for i, s in enumerate(sequence):
            if not s in monomers:
                return i
        return None

    def disambiguate(self, sequence, method='strip'):
        """Returns a non-degenerate sequence from a degenerate one.
        
        method can be 'strip' (deletes any characters not in monomers or gaps) 
        or 'random'(assigns the possibilities at random, using equal 
        frequencies).
        """
        if method == 'strip':
            try:
                return sequence.__class__(self.stripDegenerate(sequence))
            except:
                ambi = self.Degenerates
                def not_ambiguous(x):
                    return not x in ambi
                return sequence.__class__(filter(not_ambiguous, sequence))

        elif method == 'random':
            degen = self.Degenerates
            result = []
            for i in sequence:
                if i in degen:
                    result.append(choice(degen[i]))
                else:
                    result.append(i)
            if isinstance(sequence, str):
                return sequence.__class__(''.join(result))
            else:
                return sequence.__class__(result)
        else:
            raise NotImplementedError, "Got unknown method %s" % method

    def degap(self, sequence):
        """Deletes all gap characters from sequence."""
        try:
            return sequence.__class__(sequence.translate( \
            allchars, self.GapString))
        except AttributeError:
            gap = self.Gaps
            def not_gap(x):
                return not x in gap
            return sequence.__class__(filter(not_gap, sequence))

    def gapList(self, sequence):
        """Returns list of indices of all gaps in the sequence, or []."""
        gaps = self.Gaps
        return [i for i, s in enumerate(sequence) if s in gaps]

    def gapVector(self, sequence):
        """Returns list of bool indicating gap or non-gap in sequence."""
        return map(self.isGap, sequence)

    def gapMaps(self, sequence):
        """Returns tuple containing dicts mapping between gapped and ungapped.

        First element is a dict such that d[ungapped_coord] = gapped_coord.
        Second element is a dict such that d[gapped_coord] = ungapped_coord.
        
        Note that the dicts will be invalid if the sequence changes after the
        dicts are made.

        The gaps themselves are not in the dictionary, so use d.get() or test
        'if pos in d' to avoid KeyErrors if looking up all elements in a gapped
        sequence.
        """
        ungapped = {}
        gapped = {}
        num_gaps = 0
        for i, is_gap in enumerate(self.gapVector(sequence)):
            if is_gap:
                num_gaps += 1
            else:
                ungapped[i] = i - num_gaps
                gapped[i - num_gaps] = i
        return gapped, ungapped
        

    def countGaps(self, sequence):
        """Counts the gaps in the specified sequence."""
        gaps = self.Gaps
        gap_count = 0
        for s in sequence:
            if s in gaps:
                gap_count += 1
        return gap_count

    def countDegenerate(self, sequence):
        """Counts the degenerate bases in the specified sequence."""
        degen = self.Degenerates
        degen_count = 0
        for s in sequence:
            if s in degen:
                degen_count += 1
        return degen_count

    def possibilities(self, sequence):
        """Counts number of possible sequences matching the sequence.

        Uses self.Degenerates to decide how many possibilites there are at 
        each position in the sequence.
        """
        degen = self.Degenerates
        count = 1
        for s in sequence:
            if s in degen:
                count *= len(degen[s])
        return count

    def MW(self, sequence, method='random', delta=None):
        """Returns the molecular weight of the sequence.

        If the sequence is ambiguous, uses method (random or strip) to
        disambiguate the sequence.
        
        if delta is present, uses it instead of self.WeightAdjust.
        """
        if not sequence:
            return 0
        try:
            return self._inner_mw(sequence, delta)
        except KeyError:    #assume sequence was ambiguous
            return self._inner_mw(self.disambiguate(sequence, method), delta)

    def _inner_mw(self, sequence, delta):
        """Inner part of MW calculations."""
        weight = delta or self.WeightAdjust
        for s in sequence:
            if s in self.Gaps:  #gaps have no weight
                continue
            else:
                weight += self.Monomers[s].MW
        return weight

    def canMatch(self, first, second):
        """Returns True if every pos in 1st could match same pos in 2nd.

        Truncates at length of shorter sequence.
        Gaps are only allowed to match other gaps.
        """
        m = self.Matches
        for pair in zip(first, second):
            if pair not in m:
                return False
        return True

    def canMismatch(self, first, second):
        """Returns True if any position in 1st could cause a mismatch with 2nd.

        Truncates at length of shorter sequence.
        Gaps are always counted as matches.
        """
        m = self.Matches
        if not first or not second:
            return False
        
        for pair in zip(first, second):
            if not m.get(pair, None):
                return True
        return False

    def mustMatch(self, first, second):
        """Returns True if all positions in 1st must match positions in second."""
        return not self.canMismatch(first, second)

    def canPair(self, first, second):
        """Returns True if first and second could pair.

        Pairing occurs in reverse order, i.e. last position of second with
        first position of first, etc.

        Truncates at length of shorter sequence.
        Gaps are only allowed to pair with other gaps, and are counted as 'weak'
        (same category as GU and degenerate pairs).

        NOTE: second must be able to be reverse
        """
        p = self.Pairs
        sec = list(second)
        sec.reverse()
        for pair in zip(first, sec):
            if pair not in p:
                return False
        return True

    def canMispair(self, first, second):
        """Returns True if any position in 1st could mispair with 2nd.

        Pairing occurs in reverse order, i.e. last position of second with
        first position of first, etc.

        Truncates at length of shorter sequence.
        Gaps are always counted as possible mispairs, as are weak pairs like GU.
        """
        p = self.Pairs
        if not first or not second:
            return False
        
        sec = list(second)
        sec.reverse()
        for pair in zip(first, sec):
            if not p.get(pair, None):
                return True
        return False

    def mustPair(self, first, second):
        """Returns True if all positions in 1st must pair with second.
        
        Pairing occurs in reverse order, i.e. last position of second with
        first position of first, etc.
        """
        return not self.canMispair(first, second)

    def degenerateFromSequence(self, sequence):
        """Returns least degenerate symbol corresponding to chars in sequence.

        First tries to look up in self.InverseDegenerates. Then disambiguates
        and tries to look up in self.InverseDegenerates. Then tries converting
        the case (tries uppercase before lowercase). Raises TypeError if 
        conversion fails.
        """
        symbols = ImmutableSet(sequence)
        #check if symbols are already known
        inv_degens = self.InverseDegenerates
        result = inv_degens.get(symbols, None)
        if result:
            return result
        #then, try converting the symbols
        degens = self.All
        converted = Set()
        for sym in symbols:
            for char in degens[sym]:
                converted.add(char)
        symbols = ImmutableSet(converted)
        result = inv_degens.get(symbols, None)
        if result:
            return result
        #then, try converting case
        symbols = ImmutableSet([s.upper() for s in symbols])
        result = inv_degens.get(symbols, None)
        if result:
            return result
        symbols = ImmutableSet([s.lower() for s in symbols])
        result = inv_degens.get(symbols, None)
        if result:
            return result
        #finally, try to find the minimal subset containing the symbols
        lengths = {}
        for i in inv_degens:
            if symbols.issubset(i):
                lengths[len(i)] = i
        if lengths:  #found at least some matches
            sorted = lengths.keys()
            sorted.sort()
            return inv_degens[lengths[sorted[0]]]
        
        #if we got here, nothing worked
        raise TypeError, "Cannot find degenerate char for symbols: %s" \
                % symbols
        
        


ProteinDegenerateSymbols = {
    '?':'ACDEFGHIKLMNPQRSTUVWY-',
    'X':'ACDEFGHIKLMNPQRSTUVWY',
    'B':'DN',
    'Z':'EQ',
    } 

RnaDegenerateSymbols = {
    'B':'UCG',
    'D':'UAG',
    'H':'UCA',
    'K':'UG',
    'M':'CA',
    'N':'UCAG',
    '?':'UCAG-',
    'R':'AG',
    'S':'CG',
    'V':'CAG',
    'W':'UA',
    'Y':'UC',
}

DnaDegenerateSymbols = {
    'B':'TCG',
    'D':'TAG',
    'H':'TCA',
    'K':'TG',
    'M':'CA',
    '?':'TCAG-',
    'N':'TCAG',
    'R':'AG',
    'S':'CG',
    'V':'CAG',
    'W':'TA',
    'Y':'TC',
}

RnaComplements = {
    'A':'U',
    'B':'V',
    'C':'G',
    'D':'H',
    'G':'C',
    'H':'D',
    'K':'M',
    'M':'K',
    'N':'N',
    'R':'Y',
    'S':'S',
    'U':'A',
    'V':'B',
    'W':'W',
    'Y':'R',
}

DnaComplements = {
    'A':'T',
    'B':'V',
    'C':'G',
    'D':'H',
    'G':'C',
    'H':'D',
    'K':'M',
    'M':'K',
    'N':'N',
    'R':'Y',
    'S':'S',
    'T':'A',
    'V':'B',
    'W':'W',
    'Y':'R',
}

RnaPairs = {
    ('A','U'): True,    #True vs False for 'always' vs 'sometimes' pairing
    ('C','G'): True,
    ('G','C'): True,
    ('U','A'): True,
    ('G','U'): False,
    ('U','G'): False,
}

RnaWCPairs = {
    ('A','U'): True,    #True vs False for 'always' vs 'sometimes' pairing
    ('C','G'): True,
    ('G','C'): True,
    ('U','A'): True,
}
DnaPairs = {
    ('A','T'): True,
    ('C','G'): True,
    ('G','C'): True,
    ('T','A'): True,
}

ProteinOrder = 'ACDEFGHIKLMNPQRSTVWY'   #omit selenocysteine

RnaBaseOrder = 'UCAG'

DnaBaseOrder = 'TCAG'

MinimalGapSymbols = {'-':True}

ProteinWeightCorrection = 18.0          #terminal residues not dehydrated
NucleicAcidWeightCorrection = 61.96     #assumes 5' monophosphate, 3' OH

ProteinAlphabet = Alphabet(Monomers=AminoAcids, 
    Degenerates=ProteinDegenerateSymbols, Gaps=MinimalGapSymbols,
    Order=ProteinOrder,
    WeightAdjust=ProteinWeightCorrection)

RnaAlphabet = Alphabet(Monomers=RnaBases, Degenerates=RnaDegenerateSymbols,
    Gaps=MinimalGapSymbols, Complements=RnaComplements, Order=RnaBaseOrder,
    Pairs=RnaPairs, WeightAdjust=NucleicAcidWeightCorrection)

DnaAlphabet = Alphabet(Monomers=DnaBases, Degenerates=DnaDegenerateSymbols,
    Gaps=MinimalGapSymbols, Complements=DnaComplements, Order=DnaBaseOrder,
    Pairs=DnaPairs, WeightAdjust=NucleicAcidWeightCorrection)

#use RNAWCAlphabet if you only want Watson-Crick RNA pairs, not GU, to count 
#in deciding which degenerate symbols could pair with each other. 
RnaWCAlphabet = Alphabet(Monomers=RnaBases, Degenerates=RnaDegenerateSymbols,
    Gaps=MinimalGapSymbols, Complements=RnaComplements, Order=RnaBaseOrder,
    Pairs=RnaWCPairs, WeightAdjust=NucleicAcidWeightCorrection)

if __name__ == '__main__':
    set_trace()
    print ProteinAlphabet.firstNonValidStrict('ADDFFU*')
