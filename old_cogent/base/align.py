#!/usr/bin/env python
#file cogent/core/align.py
"""Utility classes for dealing with sequence and structure alignments.

Owner: Rob Knight rob@spot.colorado.edu

Status: Prototype in incomplete transition to new APIs.

Revision History

Written week of 3/29/04 for PyEvolve by Rob Knight.

4/9/04 Rob Knight: Alignment now preserves RowOrder if initialized from a list.

4/15/04 Rob Knight: Changed 'filter' to 'keep' for several methods following
suggestion by Cathy Lozupone. Added omit* to the mark*, get*, keep* interface.

4/20/04 Rob Knight: added distanceMatrix.

5/4/04 Rob Knight: changed method names as per discussion in lab (mark* ->
get*Indices, keep* -> get*If). Added ability to negate the get*, get*Indices,
and get*If methods with a 'negate' kwarg, default False.

6/4/04 Jeremy Widmann: Added IUPACConsensus, isRagged, and scoreMatrix
functions.  Added columnFrequencies, columnProbs, majorityConsensus, and
uncertainties from bayes_util.py.

10/14/05 Micah Hamady: Added getPhylipString()

1/30/06 Cathy Lozupone: changed getPhylipString() and getNexusString() to
toPhylip() and toNexus(). Added toFasta, omitRowsTemplate, and 
make_gap_filter. Added allowed_frac_bad_cols to options in omitGapCols.

1/30/06 Jeremy Widmann: added getIntMap, fixed toFasta so labels are coerced
into strings.  Changed getIntMap to prefix integer labels with 'seq_'
"""
from __future__ import division
from old_cogent.base.sequence import frac_same
from old_cogent.base.dict2d import Dict2D
from old_cogent.base.alphabet import *
from old_cogent.base.stats import Freqs
from Numeric import array, logical_and, logical_not, UInt8

eps = 1e-6  #small number: 1-eps is almost 1, and is used for things like the
            #default number of gaps to allow in a column.

class Alignment(dict):
    """Stores an Alignment as an ordered dict of sequences.

    Row order is given by self.RowOrder (makes it cheap to rearrange).

    Desirable input handlers for Alignment:

    - FASTA-format string (starts with >)
    - FASTA-format lines (first item must start with >)
    - list of seq objects, could be from diff. packages 
        (check with isinstance())
    - list of [(name, seq)] tuple or list or whatever: each must have
        two elements, first is a string, isn't a string itself
    - {name:seq} dict
    - name of FASTA file on disk, requires dot in filename
    - 2D array of small integers corresponding to indices on the alphabet       
        (check that first element is an integer)
    - string containing the sequence data, one seq per line (default case).
      if seqs are split across lines, will still treat each line as a separate
      seq b/c we can't detect.
    - list of strings
"""
    #Note that Alignment subclasses may want to change the gap chars.
    DefaultGap = '-'                #default gap character for padding
    GapChars = dict.fromkeys('-~')  #default gap chars for comparisons
    RowConstructor = list           #default constructor for rows
    
    def __init__(self, data=None, RowOrder=None, Info=None, \
        DefaultGap=None, GapChars=None):
        """Returns a new alignment object, using data and optionally RowOrder.

        data: either a dict, a sequence of (key, seq) tuples, or a sequence
        of sequences. If data can't be converted into a dict directly, the 
        keys will be successive integers assigned by enumerate().

        RowOrder: list of keys giving order of sequences in the alignment.

        Does not enforce the requirement that all the sequences be the same
        length. Assign to SeqLen to pad or truncate the sequences.
        """
        self.RowOrder = RowOrder
        self.Info = Info
        #DefaultGap and GapChars will use class data if not defined.
        if DefaultGap:
            self.DefaultGap = DefaultGap
        if GapChars:
            self.GapChars = GapChars
        if data:
            if hasattr(data, 'keys'):
                self.update(data)
            else:
                try:
                    self.update(dict(data))
                    self.RowOrder = [key for key, val in data]
                except:
                    self.clear()    #may have added some keys before failure
                    self.update(dict(enumerate(data)))
                    self.RowOrder = range(len(data))

    def _get_row_order(self):
        """Gets the row order, or uses self.keys() if not present."""
        if not hasattr(self, '_row_order'):
            self._row_order = None
        return self._row_order or self.keys()

    def _set_row_order(self, row_order):
        """Sets the row order."""
        self._row_order = row_order
        
    RowOrder = property(_get_row_order, _set_row_order)

    def _get_seq_len(self):
        """Gets the length of the longest sequence in self."""
        curr_len = 0
        for seq in self.values():
            curr_len = max(curr_len, len(seq))
        return curr_len

    def _set_seq_len(self, length=None):
        """Sets the length of all sequences in the alignment.

        Will truncate any sequences longer than length, and pad any sequences
        shorter than length using gap_char (if supplied) or self.DefaultGap.

        If length is None, will pad to the length of the longest sequence, so
        that A.SeqLen = None always performs this padding. Possibly this API
        should be improved, since it's not obvious. A.SeqLen = A.SeqLen will
        preform an equivalent taks.

        Note that all values are potentially re-bound to new objects during
        this operation (to allow for immutable sequences). Consequently:

            - External refs to sequence objects may break!

            - Any information not preserved by sequence objects under += or
              slicing will be lost!

        Note that length refers to len(seq), not to the index of the last 
        element (which is length - 1).

        The padding will always use self.DefaultGap. Support for end gaps will
        eventually go in self.formatGaps().
        """
        if length is None:
            length = self._get_seq_len()
        
        for key, seq in self.items():
            diff = length - len(seq)
            if diff > 0:    #curr seq was smaller, and needs padding
                padding = seq.__class__(self.DefaultGap * diff)
                #try in-place addition, but if it fails make a new object
                try:
                    seq += padding
                    new_seq = seq
                except (AttributeError, TypeError):
                    new_seq = seq + padding
                    
            elif diff < 0:  #curr seq was longer, and must be truncated
                new_seq = seq[:length]
            else:           #object is OK, so recycle it
                new_seq = seq   

            self[key] = new_seq

    SeqLen = property(_get_seq_len, _set_seq_len)
    
    def iterRows(self, row_order=None):
        """Iterates over values (sequences) in the alignment, in order.

        row_order: list of keys giving the order in which rows will be returned.
        Defaults to self.RowOrder. Note that only these sequences will be
        returned, and that KeyError will be raised if there are sequences
        in order that have been deleted from the Alignment. If self.RowOrder
        is None, returns the sequences in the same order as self.values().

        Use map(f, self.rows()) to apply the constructor f to each row. f must
        accept a single list as an argument.

        Always returns references to the same objects that are values of the
        alignment.
        """
        for key  in row_order or self.RowOrder:
            yield self[key]

    Rows = property(iterRows)   #can access as attribute if using default order.

    def iterCols(self, col_order=None):
        """Iterates over columns in the alignment, in order.

        col_order refers to a list of indices (ints) specifying the column 
        order. This lets you rearrange columns if you want to (e.g. to pull 
        out individual codon positions). 

        Note that self.iterCols() always returns new objects, specifically lists
        of elements. Use map(f, self.iterCols) to apply the constructor or 
        function f to the resulting lists (f must take a single list as a 
        parameter). Note that some sequences (e.g. ViennaStructures) have 
        rules that prevent arbitrary columns of their symbols from being 
        valid objects.

        Will raise IndexError if one of the indices in order exceeds the 
        sequence length. This will always happen on ragged alignments:
        assign to self.SeqLen to set all sequences to the same length.
        """
        col_order = col_order or xrange(self.SeqLen)
        row_order = self.RowOrder
        for col in col_order:
            yield [self[row][col] for row in row_order]

    Cols = property(iterCols)

    def iterItems(self, row_order=None, col_order=None):
        """Iterates over elements in the alignment.

        row_order (labels) can be used to select a subset of rows.
        col_order (columns) can be used to select a subset of columns.

        Always iterates along a row first, then down a column.

        WARNING: Alignment.iterItems() is not the same as alignment.iteritems()
        (which is the built-in dict iteritems that iterates over key-value 
        pairs).
        """
        if col_order:
            for row in self.iterRows(row_order):
                for i in col_order:
                    yield row[i]
        else:
            for row in self.iterRows(row_order):
                for i in row:
                    yield i

    Items = property(iterItems)

    def getRows(self, rows, negate=False):
        """Returns new Alignment containing only specified rows.
        
        Note that the rows in the new alignment will be references to the
        same objects as the rows in the old alignment.
        """
        result = {}
        if negate:
            #copy everything except the specified rows
            row_lookup = dict.fromkeys(rows)
            for r, row in self.items():
                if r not in row_lookup:
                    result[r] = row
        else:
            #copy only the specified rows
            for r in rows:
                result[r] = self[r]
        return self.__class__(result)

    def getRowIndices(self, f, negate=False):
        """Returns list of keys of rows where f(row) is True.
        
        List will be in the same order as self.RowOrder, if present.
        """
        #negate function if necessary
        if negate:
            new_f = lambda x: not f(x)
        else:
            new_f = f
        #get all the rows where the function is True
        return [key for key in self.RowOrder if new_f(self[key])]

    def getRowsIf(self, f, negate=False):
        """Returns new Alignment containing rows where f(row) is True.
        
        Note that the rows in the new Alignment are the same objects as the
        rows in the old Alignment, not copies.
        """
        #pass negate to get RowIndices
        return self.getRows(self.getRowIndices(f, negate))

    def getCols(self, cols, negate=False, row_constructor=None):
        """Returns new Alignment containing only specified cols.
        
        By default, the rows will be lists, but an alternative constructor
        can be specified.

        Note that getCols will fail on ragged columns.
        """
        if row_constructor is None:
            row_constructor = self.RowConstructor
        result = {}
        #if we're negating, pick out all the columns except specified indices
        if negate:
            col_lookup = dict.fromkeys(cols)
            for key, row in self.items():
                result[key] = row_constructor([row[i] for i in range(len(row)) \
                if i not in col_lookup])
        #otherwise, just get the requested indices
        else:
            for key, row in self.items():
                result[key] = row_constructor([row[i] for i in cols])
        return self.__class__(result)

    def getColIndices(self, f, negate=False):
        """Returns list of column indices for which f(col) is True."""
        #negate f if necessary
        if negate:
            new_f = lambda x: not f(x)
        else:
            new_f = f
        return [i for i, col in enumerate(self.Cols) if new_f(col)]

    def getColsIf(self, f, negate=False, row_constructor=None):
        """Returns new Alignment containing cols where f(col) is True.

        Note that the rows in the new Alignment are always new objects. Default
        constructor is list(), but an alternative can be passed in.
        """
        if row_constructor is None:
            row_constructor = self.RowConstructor
        return self.getCols(self.getColIndices(f, negate), \
            row_constructor=row_constructor)

    def getItems(self, items, negate=False):
        """Returns list containing only specified items.
        
        items should be a list of (row_key, col_key) tuples.
        """
        if negate:
            #have to cycle through every item and check that it's not in
            #the list of items to return
            item_lookup = dict.fromkeys(map(tuple, items))
            result = []
            for r in self:
                curr_row = self[r]
                for c in range(len(curr_row)):
                    if (r, c) not in items:
                        result.append(curr_row[c])
            return result
        #otherwise, just pick the selected items out of the list
        else:
            return [self[row][col] for row, col in items]

    def getItemIndices(self, f, negate=False):
        """Returns list of (key,val) tuples where f(self[key][val]) is True."""
        if negate:
            new_f = lambda x: not f(x)
        else:
            new_f = f
        result = [] 
        for row_label in self.RowOrder:
            curr_row = self[row_label]
            for col_idx, item in enumerate(curr_row):
                if new_f(item):
                    result.append((row_label, col_idx))
        return result

    def getItemsIf(self, f, negate=False):
        """Returns list of items where f(self[row][col]) is True."""
        return self.getItems(self.getItemIndices(f, negate))

    def getSimilar(self, target, min_similarity=0.0, max_similarity=1.0, \
        metric=frac_same, transform=None):
        """Returns new Alignment containing sequences similar to target.

        target: sequence object to compare to. Can be in the alignment.

        min_similarity: minimum similarity that will be kept. Default 0.0.

        max_similarity: maximum similarity that will be kept. Default 1.0.
        (Note that both min_similarity and max_similarity are inclusive.)

        metric: similarity function to use. Must be f(first_seq, second_seq).
        The default metric is fraction similarity, ranging from 0.0 (0% 
        identical) to 1.0 (100% identical). The Sequence classes have lots
        of methods that can be passed in as unbound methods to act as the
        metric, e.g. fracSameGaps.
        
        transform: transformation function to use on the sequences before
        the metric is calculated. If None, uses the whole sequences in each 
        case. A frequent transformation is a function that returns a specified 
        range of a sequence, e.g. eliminating the ends. Note that the 
        transform applies to both the real sequence and the target sequence.

        WARNING: if the transformation changes the type of the sequence (e.g.
        extracting a string from an RnaSequence object), distance metrics that
        depend on instance data of the original class may fail.
        """
        if transform:
            target = transform(target)
        m = lambda x: metric(target, x)

        if transform:
            def f(x):
                result = m(transform(x))
                return min_similarity <= result <= max_similarity
        else:
            def f(x):
                result = m(x)
                return min_similarity <= result <= max_similarity

        return self.getRowsIf(f)

    def _make_gaps_ok(self, allowed_gap_frac):
        """Makes the gaps_ok function used by omitGapCols and omitGapRows.

        Need to make the function because if it's a method of Alignment, it
        has unwanted 'self' and 'allowed_gap_frac' parameters that impede the 
        use of map() in getRowsIf.

        WARNING: may not work correctly if component sequences have gaps that
        are not the Alignment gap character. This is because the gaps are 
        checked at the column level (and the columns are lists), rather than
        at the row level. Working around this issue would probably cause a
        significant speed penalty.
        """
        def gaps_ok(seq):
            seq_len = len(seq)
            try:
                num_gaps = seq.countGaps()
            except AttributeError:
                num_gaps = len(filter(self.GapChars.__contains__, seq))
            return num_gaps / seq_len <= allowed_gap_frac

        return gaps_ok

    def omitGapCols(self, allowed_gap_frac=1-eps, del_rows=False, \
        allowed_frac_bad_cols=0, row_constructor=None):
        """Returns new alignment where all cols have <= allowed_gap_frac gaps.

        allowed_gap_frac says what proportion of gaps is allowed in each
        column (default is 1-eps, i.e. all cols with at least one non-gap
        character are preserved).

        If del_rows is True (default:False), deletes the sequences that don't 
        have gaps where everything else does. Otherwise, just deletes the 
        corresponding column from all sequences, in which case real data as
        well as gaps can be removed.

        Uses row_constructor(row) to make each new row object.

        Note: a sequence that is all gaps will not be deleted by del_rows
        (even if all the columns have been deleted), since it has no non-gaps
        in columns that are being deleted for their gap content. Possibly,
        this decision should be revisited since it may be a surprising
        result (and there are more convenient ways to return the sequences
        that consist wholly of gaps).
        """
        if row_constructor is None:
            row_constructor = self.RowConstructor
        gaps_ok = self._make_gaps_ok(allowed_gap_frac)
        #if we're not deleting the 'naughty' rows that contribute to the 
        #gaps, it's easy...
        if not del_rows:
            return self.getColsIf(f=gaps_ok, row_constructor=row_constructor)
        #otherwise, we have to figure out which rows to delete.
        #if we get here, we're doing del_rows.
        cols_to_delete = dict.fromkeys(self.getColIndices(gaps_ok, negate=True))
        default_gap_f = self.GapChars.__contains__
       
        bad_cols_per_row = {}
        for key, row in self.iteritems():
            try:
                is_gap = row.Alphabet.Gaps.__contains__
            except:
                is_gap = default_gap_f
                
            for col in cols_to_delete:
                if not is_gap(row[col]):
                    if key not in bad_cols_per_row:
                        bad_cols_per_row[key] = 1
                    else:
                        bad_cols_per_row[key] += 1
        #figure out which of the rows we're deleting
        rows_to_delete = {}
        for key, count in bad_cols_per_row.items():
            if float(count)/len(self[key]) >= allowed_frac_bad_cols:
                rows_to_delete[key] = True
        #It's _much_ more efficient to delete the rows before the cols.
        good_rows = self.getRows(rows_to_delete, negate=True)
        cols_to_keep = dict.fromkeys(range(self.SeqLen))
        for c in cols_to_delete:
            del cols_to_keep[c]
        return good_rows.getCols(cols=cols_to_keep.keys(), \
            row_constructor=row_constructor)

    def omitGapRows(self, allowed_gap_frac=0):
        """Returns new alignment with rows that have <= allowed_gap_frac.
        
        allowed_gap_frac should be a fraction between 0 and 1 inclusive.
        Default is 0.
        """
        gaps_ok = self._make_gaps_ok(allowed_gap_frac)

        return self.getRowsIf(gaps_ok)

    def omitGapRuns(self, allowed_run=1):
        """Returns new alignment where all rows have runs of gaps <=allowed_run.
        
        Note that rows with exactly allowed_run gaps are not deleted.
        Default is for allowed_run to be 1 (i.e. no consecutive gaps allowed).

        Because the test for whether the current gap run exceeds the maximum
        allowed gap run is only triggered when there is at least one gap, even
        negative values for allowed_run will still let sequences with no gaps
        through.
        """
        def ok_gap_run(x):
            try:
                is_gap = x.Alphabet.Gaps.__contains__
            except AttributeError:
                is_gap = self.GapChars.__contains__
            curr_run = max_run = 0
            for i in x:
                if is_gap(i):
                    curr_run += 1
                    if curr_run > allowed_run:
                        return False
                else:
                    curr_run = 0
            #can only get here if max_run was never exceeded (although this
            #does include the case where the sequence is empty)
            return True

        return self.getRowsIf(ok_gap_run)

    def omitRowsTemplate(self, template_name, gap_fraction, gap_run):
        """Returns new alignment where all rows are well aligned with template.

        gap_fraction = fraction of positions that either have a gap in the 
            template but not in the seq or in the seq but not in the template
        gap_run = number of consecutive gaps tolerated in query relative to 
            sequence or sequence relative to query
        """
        template = self[template_name]
        gap_filter = make_gap_filter(template, gap_fraction, gap_run)
        return self.getRowsIf(gap_filter)
        
    def distanceMatrix(self, f):
        """Returns Matrix containing pairwise distances between sequences.
        f is the distance function f(x,y) -> distance between x and y.

        It's often useful to pass an unbound method in as f.

        Does not assume that f(x,y) == f(y,x) or that f(x,x) == 0.
        """
        seqs = self.keys()
        result = Dict2D()
        for i in seqs:
            for j in seqs:
                d = f(self[i], self[j])
                if i not in result:
                    result[i] = {}
                if j not in result:
                    result[j] = {}
                result[i][j] = d
                result[j][i] = d
        return result

    def IUPACConsensus(self, alphabet=RnaAlphabet):
        """Returns string containing IUPAC consensus sequence of the alignment.

        RnaAlphabet by default.  User must pass in alphabet for DNA and Protein.
        """
        consensus = []
        degen = alphabet.degenerateFromSequence
        for col in self.Cols:
            consensus.append(degen(col))
        return ''.join(consensus)

    def isRagged(self):
        """Returns True if alignment has sequences of different lengths."""
        values = self.values()      #Get all sequences in alignment
        length = len(values[0])     #Get lenght of first sequence
        for seq in values:
            #If lenghts differ
            if length != len(seq):
                return True
        #Lengths were all equal
        return False

    def scoreMatrix(self):
        """Returns a position specific score matrix for the alignment."""
        return Dict2D(dict([(i,Freqs(col)) for i, col in enumerate(self.Cols)]))

    def columnFrequencies(self, constructor=Freqs):
        """Returns Freqss with item counts for each column.
        """
        return map(constructor, self.Cols)

    def columnProbs(self, constructor=Freqs):
        """Returns FrequencyDistribuutions w/ prob. of each item per column.

        Implemented as a list of normalized Freqs objects.
        """
        
        if hasattr(self,'ColumnFrequencies'):
            freqs = [fd.copy() for fd in self.ColumnFrequencies]
        else:
            freqs = self.columnFrequencies(constructor)
            
        for fd in freqs:
            fd.normalize()
        return freqs

    def majorityConsensus(self, transform=None, constructor=Freqs):
        """Returns list containing most frequent item at each position.
        
        Optional parameter transform gives constructor for type to which result
        will be converted (useful when consensus should be same type as 
        originals).
        """
        if hasattr(self, 'ColumnFrequencies'):
            col_freqs = self.ColumnFrequencies
        else:
            col_freqs = self.columnFrequencies(constructor)
        
        consensus = [freq.Mode for freq in col_freqs]
        if transform == str:
            return ''.join(consensus)
        elif transform:
            return transform(consensus)
        else:
            return consensus            

    def uncertainties(self, good_items=None):
        """Returns Shannon uncertainty at each position.
        
        Usage: information_list = alignment.information(good_items=None)
        
        If good_items is supplied, deletes any symbols that are not in
        good_items.
        """
        uncertainties = []
        #calculate column probabilities if necessary
        if hasattr(self, 'ColumnProbs'):
            probs = self.ColumnProbs
        else:
            probs = self.columnProbs()
        #calculate uncertainty for each column
        for prob in probs:
            #if there's a list of valid symbols, need to delete everything else
            if good_items:
                prob = prob.copy()  #do not change original
                #get rid of any symbols not in good_items
                for symbol in prob.keys():
                    if symbol not in good_items:
                        del prob[symbol]
                #normalize the probabilities and add to the list
                prob.normalize()
            uncertainties.append(prob.Uncertainty)
        return uncertainties
    
    def toPhylip(self):
        """
        Return alignment in PHYLIP format and mapping to sequence ids

        raises exception if invalid alignment
        """
       
        num_items = len(self)
        if not self or not num_items:
            return ""

        lengths = sum(map(len, self.values()))
        first_row_len = len(self.values()[0])
        avg_len = lengths / num_items
        
        if first_row_len != avg_len:
            raise ValueError, "Sequences in alignment are not all the same " +\
                              "length. Cannot generate PHYLIP format."
        
        phylip_out = ["%d %d" % (num_items, first_row_len)]
        id_map = {}
        cur_seq_id = 1 

        for align_id, align_seq in self.items():
            cur_id = "seq%07d" % cur_seq_id
            id_map[cur_id] = align_id
            phylip_out.append("%s %s" % (cur_id, align_seq))
            cur_seq_id += 1

        return '\n'.join(phylip_out), id_map

    def toFasta(self):
        """Return alignment in Fasta format"""
        fasta_out = []
        for seq in self:
            x = '>' + str(seq) + '\n' + ''.join(self[seq])
            fasta_out.append(x)
        return('\n').join(fasta_out)

    def toNexus(self, seq_type, interleave_len=50):
        """
        Return alignment in NEXUS format and mapping to sequence ids

        **NOTE** Not that every sequence in the alignment MUST come from
            a different species!! (You can concatenate multiple sequences from
            same species together before building tree)

        seq_type: dna, rna, or protein

        Raises exception if invalid alignment
        """
       
        num_items = len(self)
        if not self or not num_items:
            return ""

        lengths = sum(map(len, self.values()))
        first_row_len = len(self.values()[0])
        avg_len = lengths / num_items

        if first_row_len != avg_len:
            raise ValueError, "Sequences in alignment are not all the same " +\
                              "length. Cannot generate NEXUS format."
      
        nexus_out = ["#NEXUS\n\nbegin data;"]
        nexus_out.append("    dimensions ntax=%d nchar=%d;" % (num_items,
                                                         first_row_len))
        nexus_out.append("    format datatype=%s interleave=yes missing=? " % \
                                                        seq_type + "gap=-;")
        nexus_out.append("    matrix")
        cur_ix = 0
        while cur_ix < first_row_len:
            nexus_out.extend(["    %s    %s" % (x, y[cur_ix:cur_ix + interleave_len]) for x, y in self.items()])
            nexus_out.append("")
            cur_ix += interleave_len
        nexus_out.append("    ;\nend;")
        
        return '\n'.join(nexus_out)
        
    def getIntMap(self):
        """Returns a dict with labels mapped to enumerates integer labels.
            
            - label is prefixed with 'seq_'
            - int_keys is a dict mapping int labels to sorted original labels.
        """
        int_keys = \
            dict([('seq_'+str(i),k) for i,k in enumerate(sorted(self.keys()))])
        int_map = dict([(k, self[v]) for k,v in int_keys.items()])
        return int_map, int_keys

def make_gap_filter(template, gap_fraction, gap_run):
    """Returns f(seq) -> True if no gap runs and acceptable gap fraction.

    Calculations relative to template.
    gap_run = number of consecutive gaps allowed in either the template or seq
    gap_fraction = fraction of positions that either have a gap in the template 
        but not in the seq or in the seq but not in the template
    NOTE: template and seq must both be Sequence objects.
    """
    template_gaps = array(template.gapVector())
    def result(seq):
        """Returns True if seq adhers to the gap threshold and gap fraction."""
        seq_gaps = array(seq.gapVector())
        #check if gap amount bad
        if sum(seq_gaps!=template_gaps)/float(len(seq)) > gap_fraction:
            return False
        #check if gap runs bad
        if '\x01'*gap_run in logical_and(seq_gaps, \
                logical_not(template_gaps)).astype(UInt8).tostring():
            return False
        #check is insertion runs bad
        elif '\x01'*gap_run in logical_and(template_gaps, \
                logical_not(seq_gaps)).astype(UInt8).tostring():
            return False
        return True
    
    return result



