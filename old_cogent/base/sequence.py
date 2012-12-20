#!/usr/bin/env python
#file cogent/base/sequence.py

"""Provides Sequence and its subclasses.

Owner: Rob Knight rob@spot.colorado.edu

Status: Development -- feedback requested!

Sequence holds a string and several attributes, and defines several functions
(strip, shuffle). 

Implementation Notes

Sequences are implemented as strings; MutableSequences are implemented as lists.
All string operations are supported on MutableSequences, but will be _very_
slow: e.g. find() or translate() is handled by making an immutable copy of the
data and performing the operation on that. In general, the code is written for
user convenience rather than speed, with some exceptions.

Typically, sequences from untrusted sources will be constructed using one of the
factory functions:
    
    Rna(), Dna(), Protein() 
    
These functions will, by default, strip
out any unrecognized characters (i.e. characters not in the IUPAC alphabet and
not gaps), although if strict=True (strict is the second parameter) they will
instead raise a ConstraintError if there are unrecognized characters in the
input. These functions are _very_ forgiving with bad input, and will try to
coerce basically anything into a sequence. Rna() and Dna() will do the right
thing with t's and u's, converting both the uppercase and lowercase characters
accordingly.

All of the sequence classes treat uppercase and lowercase characters as separate
sets: 'a' doesn't match 'A', and 'c' doesn't pair with 'G' (though it does
pair with 'g'). If you want case-insensitive matches etc., use upper() on your
input before you feed it in. It is frequently useful to be able to make the
distinction between upper- and lowercase characters, and since it is so easy
to convert them either before you make the sequence or by calling upper() on
the resulting sequence this will not change.

The corresponding mutable constructors:

    MutableRna(), MutableDna(), MutableProtein()

...behave exactly the same way as the normal ones, except that they return a
mutable sequence instead of an immutable one.

The ungapped constructors:

    RnaUngapped(), DnaUngapped(), ProteinUngapped() (plus the mutable versions)

...behave the same, except that they strip out all gap characters. The gap
characters are defined by the relevant Alphabet, but are typically '.-~ '. The
ungapped constructors won't complain of the input has gaps -- they just strip
out any they find.

The actual classes are RnaSequence, DnaSequence, ProteinSequence, plus mutable
versions with the word 'Mutable' prefixed. There are also generic Sequence and
MutableSequence classes. All of these classes basically delegate most of the
character-based work to their alphabets, found in cogent.base.alphabet (DnaAlphabet,
RnaAlphabet, and ProteinAlphabet respectively). The Alphabets define a large
amount of data, including dictionaries for every possible pair and every 
possible match for degenerate sequences, and handle all the niceties of 
complementation (or raising TypeError if it's not possible), matching, pairing,
disambiguating, etc.

Revision History

11/6/03 Rob Knight: Rewritten, based on Sandra's code for RNAAnalysis and my
BayesFold code.

11/7-8/03: Added additional methods and factory functions. Default constructors
are now non-validating: beware! (This is for performance where many known good
sequences must all be e.g. RnaSequence objects.)

4/7/04 Rob Knight: added gapVector, gapMaps, and isGap (all by way of Alphabet).
Added distance functions frac_same and frac_diff, and distance methods 
matrixDistance, fracSame, fracDiff, fracSameGaps, fracDiffGaps, 
fracSameNonGaps, fracDiffNonGaps, and fracSimilar. Not entirely clear that
these should all be methods of SequenceI rather than free-standing functions
(either here or in another module), but they're all general enough that
putting them in SequenceI seems like a reasonable compromise.
"""
from __future__ import division
from random import shuffle
from old_cogent.util.transform import keep_chars, for_seq, per_shortest, per_longest
from old_cogent.parse.record import MappedRecord
from old_cogent.util.misc import Delegator, ConstrainedString, ConstrainedList, \
    ConstrainedContainer, ConstraintError, DistanceFromMatrix
from old_cogent.base.info import Info as InfoClass
from old_cogent.base.alphabet import DnaAlphabet, RnaAlphabet, ProteinAlphabet
from string import maketrans
from operator import eq, ne

#standard distance functions: left  because generally useful
frac_same = for_seq(f=eq, aggregator=sum, normalizer=per_shortest)
frac_diff = for_seq(f=ne, aggregator=sum, normalizer=per_shortest)

class SequenceI(Delegator):
    """Sequence object interface.

    SequenceI should be treated as an abstract class (it basically allows for
    implementations of immutable and immutable sequences that inherit from
    different built-in types). Mostly, it delegates sequence methods to that
    sequence's Alphabet, passing in the sequence as data. However, it will not
    raise an exception if you instantiate it directly.
   
    Alphabet is a synonym for Constraint. Cannot set Alphabet in sequence
    init directly (though it can be changed afterwards if necessary): should 
    instead set as class data.

    Desirable input handlers for sequences:
    - FASTA-format string (starts with >)
    - FASTA-format lines (first item must start with >)
    - seq object, could be from diff. packages (check with isinstance())
    - (name, seq) tuple or list or whatever: has two elements, first is a
        string, isn't a string itself
    - name of FASTA file on disk, requires dot in filename
    - array of small integers corresponding to indices on the alphabet 
      (check that first element is an
      integer)
    - string containing the sequence data (default case)
    """
    def _find_info(self, data='', Info=None):
        """Used during init: tries to set Info.
        
        Uses Info if passed as parameter. If it wasn't, first looks in the
        data, then looks in the data's class, then gives up.

        Whatever was selected as the data for info will then be tested. If it's
        None, a new Info object will be created. If it's an Info object already,
        it will be returned directly. Otherwise, try to coerce it into an Info
        object: if the coercion succeeds, return the new Info object; if it
        fails, return the object itself. For example, if a string or number is
        passed as Info, that string or number will be used directly and no
        Info object will be created (this is a potential way of avoiding Info's
        overhead, which is considerable, if e.g. making very large numbers of
        random sequences, but it is probably better to either (a) generate 
        strings directly, or (b) just accept the Info overhead and use it to
        store metadata about how the sequences were created.
        """
        #figure out what object to use for the data in the final Info object
        if Info is None:
            if hasattr(data, 'Info') and data.Info is not None:
                curr_info = data.Info
            elif hasattr(data.__class__, 'Info'):
                curr_info = data.__class__.Info
            else:
                curr_info = None
        else:
            "Info parameter was not none: setting to curr_info"
            curr_info = Info
        #coerce the relevant data into the correct type, or give up
        if curr_info is None:
            return InfoClass()
        elif isinstance(curr_info, InfoClass):
            return curr_info
        else:
            try:
                return InfoClass(curr_info)
            except:
                return curr_info

    def _get_alphabet(self):
        """Accessor for Alphabet."""
        return self.Constraint
    def _set_alphabet(self, val):
        """Mutator for Alphabet."""
        self.Constraint = val
        
    Alphabet = property(_get_alphabet, _set_alphabet)

    def _get_info(self):
        """Accessor for info."""
        return self._handler

    def _set_info(self, data):
        """Mutator for handler."""
        self._handler = data

    Info = property(_get_info, _set_info)

    def shuffle(self):
        """returns a randomized copy of the Sequence object"""
        randomized_copy_list = list(self)
        shuffle(randomized_copy_list)
        return self.__class__(''.join(randomized_copy_list),Info=self.Info)

    def complement(self):
        """Returns complement of self, using data from Alphabet.
       
        Always tries to return same type as item: if item looks like a dict,
        will return list of keys.
        """
        return self.__class__(self.Alphabet.complement(self), Info=self.Info)

    def stripDegenerate(self):
        """Removes degenerate bases by stripping them out of the sequence."""
        return self.__class__(self.Alphabet.stripDegenerate(self), 
            Info=self.Info)

    def stripBad(self):
        """Removes any symbols not in the alphabet."""
        return self.__class__(self.Alphabet.stripBad(self), Info=self.Info)

    def stripBadAndGaps(self):
        """Removes any symbols not in the alphabet, and any gaps."""
        return self.__class__(self.Alphabet.stripBadAndGaps(self), 
            Info=self.Info)

    def rc(self):
        """Returns reverse complement of self w/ data from Alphabet.
        
        Always returns same type self.
        """
        return self.__class__(self.Alphabet.rc(self), Info=self.Info)

    def isGapped(self):
        """Returns True if sequence contains gaps."""
        return self.Alphabet.isGapped(self)

    def isGap(self, char=None):
        """Returns True if char is a gap. 
        
        If char is not supplied, tests whether self is gaps only.
        """
        if char is None:    #no char - so test if self is all gaps
            return len(self) == self.countGaps()
        else:
            return self.Alphabet.isGap(char)

    def isDegenerate(self):
        """Returns True if sequence contains degenerate characters."""
        return self.Alphabet.isDegenerate(self)

    def isValid(self):
        """Returns True if sequence contains no items absent from alphabet."""
        return self.Alphabet.isValid(self)

    def isStrict(self):
        """Returns True if sequence contains only monomers."""
        return self.Alphabet.isStrict(self)

    def firstGap(self):
        """Returns the index of the first gap in the sequence, or None."""
        return self.Alphabet.firstGap(self)

    def firstDegenerate(self):
        """Returns the index of first degenerate symbol in sequence, or None."""
        return self.Alphabet.firstDegenerate(self)

    def firstInvalid(self):
        """Returns the index of first invalid symbol in sequence, or None."""
        return self.Alphabet.firstInvalid(self)

    def firstNonStrict(self):
        """Returns the index of first non-strict symbol in sequence, or None."""
        return self.Alphabet.firstNonStrict(self)

    def disambiguate(self, method='strip'):
        """Returns a non-degenerate sequence from a degenerate one.
        
        method can be 'strip' (deletes any characters not in monomers or gaps) 
        or 'random'(assigns the possibilities at random, using equal 
        frequencies).
        """
        return self.__class__(self.Alphabet.disambiguate(self, method), 
            Info=self.Info)

    def degap(self):
        """Deletes all gap characters from sequence."""
        return self.__class__(self.Alphabet.degap(self), Info=self.Info)

    def gapList(self):
        """Returns list of indices of all gaps in the sequence, or []."""
        return self.Alphabet.gapList(self)

    def gapVector(self):
        """Returns vector of True or False according to which pos are gaps."""
        return self.Alphabet.gapVector(self)
    
    def gapMaps(self):
        """Returns dicts mapping between gapped and ungapped positions."""
        return self.Alphabet.gapMaps(self)

    def countGaps(self):
        """Counts the gaps in the specified sequence."""
        return self.Alphabet.countGaps(self)

    def countDegenerate(self):
        """Counts the degenerate bases in the specified sequence."""
        return self.Alphabet.countDegenerate(self)

    def possibilities(self):
        """Counts number of possible sequences matching the sequence.

        Uses self.Degenerates to decide how many possibilites there are at 
        each position in the sequence.
        """
        return self.Alphabet.possibilities(self)

    def MW(self, method='random', delta=None):
        """Returns the molecular weight of (one strand of) the sequence.

        If the sequence is ambiguous, uses method (random or strip) to
        disambiguate the sequence.

        If delta is passed in, adds delta per strand (default is None, which
        uses the alphabet default. Typically, this adds 18 Da for terminal
        water. However, note that the default nucleic acid weight assumes 
        5' monophosphate and 3' OH: pass in delta=18.0 if you want 5' OH as
        well.

        Note that this method only calculates the MW of the coding strand. If
        you want the MW of the reverse strand, add self.rc().MW(). DO NOT
        just multiply the MW by 2: the results may not be accurate due to 
        strand bias, e.g. in mitochondrial genomes.
        """
        return self.Alphabet.MW(self, method, delta)

    def canMatch(self, other):
        """Returns True if every pos in self could match same pos in other.

        Truncates at length of shorter sequence.
        Gaps are only allowed to match other gaps.
        """
        return self.Alphabet.canMatch(self, other)

    def canMismatch(self, other):
        """Returns True if any position in self could mismatch with other.

        Truncates at length of shorter sequence.
        Gaps are always counted as matches.
        """
        return self.Alphabet.canMismatch(self, other)

    def mustMatch(self, other):
        """Returns True if all positions in self must match positions in other."""
        return self.Alphabet.mustMatch(self, other)

    def canPair(self, other):
        """Returns True if self and other could pair.

        Pairing occurs in reverse order, i.e. last position of other with
        first position of self, etc.

        Truncates at length of shorter sequence.
        Gaps are only allowed to pair with other gaps, and are counted as 'weak'
        (same category as GU and degenerate pairs).

        NOTE: second must be able to be reverse
        """
        return self.Alphabet.canPair(self, other)

    def canMispair(self, other):
        """Returns True if any position in self could mispair with other.

        Pairing occurs in reverse order, i.e. last position of other with
        first position of self, etc.

        Truncates at length of shorter sequence.
        Gaps are always counted as possible mispairs, as are weak pairs like GU.
        """
        return self.Alphabet.canMispair(self, other)

    def mustPair(self, other):
        """Returns True if all positions in self must pair with other.
        
        Pairing occurs in reverse order, i.e. last position of other with
        first position of self, etc.
        """
        return not self.Alphabet.canMispair(self, other)

    def diff(self, other):
        """Returns number of differences between self and other.
        
        NOTE: truncates at the length of the shorter sequence. Case-sensitive.
        """
        count = 0
        for first, second in zip(self, other):
            if first != second:
                count += 1
        return count

    def distance(self, other, function=None):
        """Returns distance between self and other using function(i,j).
        
        other must be a sequence.
        
        function should be a function that takes two items and returns a
        number. To turn a 2D matrix into a function, use 
        cogent.util.miscs.DistanceFromMatrix(matrix).
        
        NOTE: Truncates at the length of the shorter sequence.

        Note that the function acts on two _elements_ of the sequences, not
        the two sequences themselves (i.e. the behavior will be the same for
        every position in the sequences, such as identity scoring or a function
        derived from a distance matrix as suggested above). One limitation of
        this approach is that the distance function cannot use properties of
        the sequences themselves: for example, it cannot use the lengths of the
        sequences to normalize the scores as percent similarities or percent
        differences.

        If you want functions that act on the two sequences themselves, there
        is no particular advantage in making these functions methods of the
        first sequences by passing them in as parameters like the function
        in this method. It makes more sense to use them as standalone functions.
        The factory function cogent.util.transform.for_seq is useful for converting
        per-element functions into per-sequence functions, since it takes as
        parameters a per-element scoring function, a score aggregation
        function, and a normalization function (which itself takes the two
        sequences as parameters), returning a single function that combines
        these functions and that acts on two complete sequences.
        """
        if function is None:
            #use identity scoring function
            function = lambda a, b : a != b
        distance = 0
        for first, second in zip(self, other):
            distance += function(first, second)
        return distance

    def matrixDistance(self, other, matrix):
        """Returns distance between self and other using a score matrix.
        
        WARNING: the matrix must explicitly contain scores for the case where
        a position is the same in self and other (e.g. for a distance matrix,
        an identity between U and U might have a score of 0). The reason the
        scores for the 'diagonals' need to be passed explicitly is that for
        some kinds of distance matrices, e.g. log-odds matrices, the 'diagonal'
        scores differ from each other. If these elements are missing, this
        function will raise a KeyError at the first position that the two
        sequences are identical.
        """
        return self.distance(other, DistanceFromMatrix(matrix))

    def fracSame(self, other):
        """Returns fraction of positions where self and other are the same.

        Truncates at length of shorter sequence.
        Note that fracSame and fracDiff are both 0 if one sequence is empty.
        """
        return frac_same(self, other)

    def fracDiff(self, other):
        """Returns fraction of positions where self and other differ.

        Truncates at length of shorter sequence.
        Note that fracSame and fracDiff are both 0 if one sequence is empty.
        """
        return frac_diff(self, other)

    def fracSameGaps(self, other):
        """Returns fraction of positions where self and other share gap states.

        In other words, if self and other are both all gaps, or both all 
        non-gaps, or both have gaps in the same places, fracSameGaps will 
        return 1.0. If self is all gaps and other has no gaps, fracSameGaps 
        will return 0.0. Returns 0 if one sequence is empty.

        Uses self's gap characters for both sequences.
        """
        if not self or not other:
            return 0.0
        
        is_gap = self.Alphabet.Gaps.__contains__
        return sum([is_gap(i) == is_gap(j) for i,j in zip(self, other)]) \
            /min(len(self),len(other))

    def fracDiffGaps(self, other):
        """Returns frac. of positions where self and other's gap states differ.

        In other words, if self and other are both all gaps, or both all 
        non-gaps, or both have gaps in the same places, fracDiffGaps will 
        return 0.0. If self is all gaps and other has no gaps, fracDiffGaps 
        will return 1.0.

        Returns 0 if one sequence is empty.

        Uses self's gap characters for both sequences.
        """
        if not self or not other:
            return 0.0
        return 1.0 - self.fracSameGaps(other)

    def fracSameNonGaps(self, other):
        """Returns fraction of non-gap positions where self matches other.

        Doesn't count any position where self or other has a gap.
        Truncates at the length of the shorter sequence.

        Returns 0 if one sequence is empty.
        """
        if not self or not other:
            return 0.0
        
        is_gap = self.Alphabet.Gaps.__contains__
        count = 0
        identities = 0
        for i, j in zip(self, other):
            if is_gap(i) or is_gap(j):
                continue
            count += 1
            if i == j:
                identities += 1
                
        if count:
            return identities/count
        else:   #there were no positions that weren't gaps
            return 0

    def fracDiffNonGaps(self, other):
        """Returns fraction of non-gap positions where self differs from other.

        Doesn't count any position where self or other has a gap.
        Truncates at the length of the shorter sequence.

        Returns 0 if one sequence is empty. Note that this means that 
        fracDiffNonGaps is _not_ the same as 1 - fracSameNonGaps, since both
        return 0 if one sequence is empty.
        """
        if not self or not other:
            return 0.0

        is_gap = self.Alphabet.Gaps.__contains__
        count = 0
        diffs = 0
        for i, j in zip(self, other):
            if is_gap(i) or is_gap(j):
                continue
            count += 1
            if i != j:
                diffs += 1
                
        if count:
            return diffs/count
        else:   #there were no positions that weren't gaps
            return 0

    def fracSimilar(self, other, similar_pairs):
        """Returns fraction of positions where self[i] is similar to other[i].

        similar_pairs must be a dict such that d[(i,j)] exists if i and j are
        to be counted as similar. Use PairsFromGroups in cogent.util.misc to construct
        such a dict from a list of lists of similar residues.

        Truncates at the length of the shorter sequence.

        Note: current implementation re-creates the distance function each
        time, so may be expensive compared to creating the distance function
        using for_seq separately.

        Returns 0 if one sequence is empty.
        """
        if not self or not other:
            return 0.0

        return for_seq(f = lambda x, y: (x,y) in similar_pairs, \
            normalizer=per_shortest)(self, other)


class Sequence(ConstrainedString, SequenceI):
    """Holds an immutable Sequence object, i.e. one whose sequence can't change.

    Info and other properties can be changed, but do not contribute to tests
    for equality.

    Sequence objects can be dictionary keys.

    Use seq.thaw() to get a mutable copy whose sequence can be changed, e.g. by
    element assignment and slicing.
    """
    _constraint = None

    def __new__(cls, data='', Info=None, **kwargs):
        """Non-validating constructor for sequence.

        WARNING: Using this constructor will NOT check the items in the
        sequence for validity! Use the Seq (or Rna, Dna, Protein) factory
        functions for validation. The reason for this choice is that many
        sequences come from known good sources, and validation is slow
        because it must check every character.
        """
        #If the data is not a string, try ''.join to turn it into one.
        #This prevents insertion of punctuation, as in str(my_list).
        #Note that a dict will become a concatenation of its keys, _not_ items.
        if not isinstance(data, str):
            try:
                data = ''.join(map(str, data))
            except TypeError:
                pass
        new_str =  str.__new__(cls, data)   #str.__new__ rejects kwargs
        return new_str

    def __init__(self, data='', Info=None, **kwargs):
        """Initializes sequence object, with associated Info object."""
        ConstrainedString.__init__(self, data, **kwargs)
        new_info = self._find_info(data, Info)
        Delegator.__init__(self, new_info)

    def freeze(self):
        """Supports freeze/thaw interface: returns self."""
        return self

    def thaw(self):
        """Returns mutable version of self."""
        return MutableSequence(self, Info=self.Info)

    def __cmp__(self, other):
        """Sequence should compare equal to list version of self."""
        if isinstance(other, str):
            return str.__cmp__(self, other)
        else:
            return cmp(other.__class__(self), other)

class MutableSequence(SequenceI, ConstrainedList):
    """Holds a sequence that can be changed, e.g. with element assignment.

    NOTE: MutableSequences cannot be used as keys in dictionaries. Use 
    s.freeze() to get an immutable copy that can be so used.
    """
    _constraint = None

    def __init__(self, data='', Info=None, **kwargs):
        """Initializes sequence object, bypassing validation.
        
        WARNING: Using this constructor can result in invalid data, though it
        is much faster without doing the validation. If validation is required,
        use the MutableSeq factory function, or one of its relatives (Rna, Dna,
        etc.)
        """
        #ConstrainedContainer, not ConstrainedList, init to bypass validation
        #Note that ConstrainedContainer init ignores data!
        ConstrainedContainer.__init__(self, **kwargs)
        list.__init__(self, data)
        new_info = self._find_info(data, Info)
        Delegator.__init__(self, new_info)

    def __str__(self):
        """Behaves like string rather than list."""
        return ''.join(self)

    def thaw(self):
        """Supports freeze/thaw interface: returns self."""
        return self

    def freeze(self):
        """Returns immutable version of self."""
        return Sequence(self, Info=self.Info)

    def __cmp__(self, other):
        """Compares equal to string of same sequence as well as list."""
        if isinstance(other, str):
            return cmp(''.join(self), other)
        else:
            #note: apparently, it's not possible to call list's __cmp__ with
            #two parameters, for whatever reason.
            if self < other:
                return -1
            elif self == other:
                return 0
            else:
                return 1

    def __getattr__(self, attr):
        """Masquerade as string for string methods: else, use superclass."""
        if hasattr(str, attr):
            return getattr(self.freeze(), attr)
        else:
            return super(MutableSequence, self).__getattr__(attr)

    def __contains__(self, item):
        """Support multi-item contains, by using string copy."""
        if len(item) == 1:
            return super(MutableSequence, self).__contains__(item)
        else:
            return ''.join(map(str,item)) in str(self)

class DnaSequence(Sequence):
    """Holds a DNA sequence object."""
    _constraint = DnaAlphabet

    def thaw(self):
        """Returns mutable version of self."""
        return MutableDnaSequence(self, Info=self.Info)
    
class RnaSequence(Sequence):
    """Holds an RNA sequence object."""
    _constraint = RnaAlphabet

    def thaw(self):
        """Returns mutable version of self."""
        return MutableRnaSequence(self, Info=self.Info)
 
class ProteinSequence(Sequence):
    """Holds a Protein sequence object."""
    _constraint = ProteinAlphabet

    def thaw(self):
        """Returns mutable version of self."""
        return MutableProteinSequence(self, Info=self.Info)
 
class MutableDnaSequence(MutableSequence):
    """Holds a mutable DNA sequence object."""
    _constraint = DnaAlphabet

    def freeze(self):
        """Returns immutable version of self."""
        return DnaSequence(self, Info=self.Info)
    
class MutableRnaSequence(MutableSequence):
    """Holds a mutable RNA sequence object."""
    _constraint = RnaAlphabet

    def freeze(self):
        """Returns immutable version of self."""
        return RnaSequence(self, Info=self.Info)

class MutableProteinSequence(MutableSequence):
    """Holds a mutable Protein sequence object."""
    _constraint = ProteinAlphabet

    def freeze(self):
        """Returns immutable version of self."""
        return ProteinSequence(self, Info=self.Info)

def SequenceCleaner(constructor=Sequence, validator=None, coercer=None, 
    translator=None):
    """Returns a factory function that produces valid Sequence objects.

    This function is used to instantiate the Rna, Dna, and Protein factory
    functions.

    Parameters
        
        constructor: determines the type of the object (default Sequence).
        
        validator: a function that checks if the sequence is valid. Typically
        some_alphabet.isValid().
        
        coercer: a function that will convert an invalid sequence into a valid
        one. Typically some_alphabet.stripBad().

        translator: a function that is always applied to the sequence, e.g.
        converting t to u for RNA.
    """
    def result(data='', strict=False, **kwargs):
        """Filters input data and returns a new Sequence object of some kind.
        
        strict: controls whether bad characters cause errors or are stripped.
        """
        if not isinstance(data, str):
            data = ''.join(map(str, data))
        if translator:
            data = translator(data)
        if strict and validator:
            if not validator(data):
                raise ConstraintError, "\
                    Input data %s not valid with current rules." % data
        if coercer:
            data = coercer(data)
        return constructor(data, **kwargs)
    return result

_t_to_u_trans = maketrans('tT.~ ', 'uU---') #also normalize common gap chars
_u_to_t_trans = maketrans('uU.~ ', 'tT---')
_gap_trans = maketrans('.~ ', '---')
def _t_to_u(x):
    return x.translate(_t_to_u_trans)
def _u_to_t(x):
    return x.translate(_u_to_t_trans)
def _normal_gaps(x):
    return x.translate(_gap_trans)

Rna = SequenceCleaner(RnaSequence, RnaAlphabet.isValid, RnaAlphabet.stripBad,
        _t_to_u)
Dna = SequenceCleaner(DnaSequence, DnaAlphabet.isValid, DnaAlphabet.stripBad,
        _u_to_t)
Protein = SequenceCleaner(ProteinSequence, ProteinAlphabet.isValid, 
        ProteinAlphabet.stripBad, _normal_gaps)
        
RnaUngapped = SequenceCleaner(RnaSequence, RnaAlphabet.isValid, 
        RnaAlphabet.stripBadAndGaps, _t_to_u)
DnaUngapped = SequenceCleaner(DnaSequence, DnaAlphabet.isValid, 
        DnaAlphabet.stripBadAndGaps, _u_to_t)
ProteinUngapped = SequenceCleaner(ProteinSequence, ProteinAlphabet.isValid, 
        ProteinAlphabet.stripBadAndGaps, _normal_gaps)

MutableRna = SequenceCleaner(MutableRnaSequence, RnaAlphabet.isValid, 
        RnaAlphabet.stripBad, _t_to_u)
MutableDna = SequenceCleaner(MutableDnaSequence, DnaAlphabet.isValid, 
        DnaAlphabet.stripBad, _u_to_t)
MutableProtein = SequenceCleaner(MutableProteinSequence, 
        ProteinAlphabet.isValid, ProteinAlphabet.stripBad, _normal_gaps)
        
MutableRnaUngapped = SequenceCleaner(MutableRnaSequence, RnaAlphabet.isValid, 
        RnaAlphabet.stripBadAndGaps, _t_to_u)
MutableDnaUngapped = SequenceCleaner(MutableDnaSequence, DnaAlphabet.isValid, 
        DnaAlphabet.stripBadAndGaps, _u_to_t)
MutableProteinUngapped = SequenceCleaner(MutableProteinSequence, 
        ProteinAlphabet.isValid, ProteinAlphabet.stripBadAndGaps, 
        _normal_gaps)
