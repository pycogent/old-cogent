#!/usr/bin/env python
#file cogent/motif/motif_formatters.py
from __future__ import division
from old_cogent.motif.util import *
from old_cogent.motif.pdb_color import *
from old_cogent.base.align import Alignment
from old_cogent.base.alphabet import ProteinAlphabet, RnaAlphabet, DnaAlphabet
from old_cogent.base.dict2d import Dict2D
from old_cogent.base.bitvector import VectorFromMatches
from old_cogent.format.xml import Xml
from Numeric import array, zeros, nonzero
from old_cogent.align.weights.util import AlnToProfile
from zipfile import ZipFile
from old_cogent.app.util import get_tmp_filename
from gzip import GzipFile

"""Classes for various motif finder output formats.

Owner: Jeremy Widmann  jeremy.widmann@colorado.edu

Status: Development

Revision History:

July 2004 Jeremy Widmann: Written to be added to Cogent as
    cogent.motif.motif_formatters.
    
9/26/05 Jeremy Widmann: MotifStatsBySequence, MotifLocationsBySequence, and 
HighlightOnAlignment objects each have optional sequence order parameter
to be passed to __call__ method

3/20/06 Micah Hamady: Changed for demo. Need to fix this stuff. esp xml.

4/17/06 Jeremy Widmann: Added ability to highlight motifs on gapped alignment to
HighlightMotifs class.

8/29/06 Jeremy Widmann: Added functionality to HighlightOnCrystal.
"""

def _format_number(number):
    if number is None:
        return "None"
    return "%.2e" % number

def avg(l):
    """Returns the average of a list of numbers."""

    if not l:
        return None
    return sum(l)/len(l)

class MotifStatsBySequence(MotifFormatter):
    """Generates HTML table with Motifs organized by sequence.

        - Each sequence is listed as follows:

        Seq-ID  Combined-P-Value    Motif-ID    Motif-P-Value   Motif-Seq
    """

    def __init__(self,MotifResults=None):
        """init function for MotifStatsBySequence class"""
        self.MotifResults = MotifResults
        self.ColorMap = self.getColorMap(MotifResults)

        # for performance, cache consensus
        self.ConsCache = {}
        
    def __call__(self,order=None, wrap_html=False, title_class="ntitle",
                 normal_class="normal", cons_thresh=.9):
        """Call method for MotifStatsBySequence class.

        wrap_html: if True, wrap in html + body, else just return table
        table_class: css class to use to format table
        title_class: css class to use to format titles
        normal_class: css class to use to format normal text
        cons_thresh: conservation threshold
        """
        self.ConservationThresh = cons_thresh

        html_list = []
        #if MotifResults is not None
        if self.MotifResults:
            #Find out if the alignment has a combined P value from results
            if 'CombinedP' in self.MotifResults.Results:
                combined_p_string = 'Combined P-Value'
                self.combinedP = True
            else:
                combined_p_string = '&nbsp;'
                self.combinedP = False
            
            #Start HTML string with table and table headers
            html_list = ["""<table cellpadding=2 cellspacing=2 border=0>
                             <tr class="%s">
                                <td>Sequence ID</td>
                                <td>%s</td>
                                <td>Motif ID</td>
                                <td>Motif P-Value</td>
                                <td>Motif Sequence</td>
                             </tr>""" % ( title_class, combined_p_string)]
 
            #For each sequence in alignment get HTML for that sequence
            if not order:
                order = sorted(self.MotifResults.Alignment.keys())

            for seqID in order:
                html_list.append(self.sequenceLines(seqID, title_class, normal_class))

            html_list.append("</table>")

            if wrap_html:
                return """<html><head><title>Motif Finder Results</title></head><body>%s</table></body></html>""" % ''.join(html_list)
            return  ''.join(html_list) 
            
        return "" 

    def _get_location_dict(self):
        """Builds dict of all locations.
            {module:{seqID:[indices]}}
        """
        location_dict = {}  #Dict with locations of every motif keyed by module
        #Build dict of all the locations:
        # {module:{seqID:[indices]}}
        if self.MotifResults:
            for motif in self.MotifResults.Motifs:
                for module in motif.Modules:
                    location_dict[module]=module.LocationDict
        return location_dict

    Locations = property(_get_location_dict)

    def _makeConservationConsensus(self, module):
        """
        Return conservation consensus string
        """
        mod_id = module.ID
        if mod_id in self.ConsCache:
            return self.ConsCache[mod_id]

        cons_thresh = self.ConservationThresh

        cons_seq = ''.join(module.majorityConsensus())
        col_freqs = module.columnFrequencies()
        cons_con_seq = []
        for ix, col in enumerate(col_freqs):
            col_sum = sum(col.values())
            keep = False
            for b, v in col.items():
                cur_cons = v / col_sum
                if cur_cons >= cons_thresh:
                    keep = True
            if keep:
                cons_con_seq.append(cons_seq[ix])
            else:
                cons_con_seq.append(" ")
        self.ConsCache[mod_id] = (cons_seq, ''.join(cons_con_seq))
        return self.ConsCache[mod_id]


    def _flagConservedConsensus(self, cons_con_seq, cons_seq, cur_seq):
        """
        Annotate consensus  
        """
        color_style = """background-color: %s; font-family: 'Courier New', Courier"""

        span_fmt = """<span style="%s">%s</span>"""
        h_str = []
        for ix in range(len(cur_seq)):
            cur_c = cur_seq[ix]
            if cur_c == cons_con_seq[ix]:
                h_str.append(span_fmt % (color_style % "#eeeeee", "+"))
            elif cons_con_seq[ix] != " ":
                #h_str.append("<font color=red>-</font>")
                h_str.append(span_fmt % (color_style % "#ff0000", "-"))
            elif cons_seq[ix] == cur_c:
                #h_str.append("<font color=orange>*</font>")
                h_str.append(span_fmt % (color_style % "white", "*"))
            else:
                h_str.append("&nbsp;")
        #return h_str 
        return """<font face="Courier New, Courier, monospace">%s</font>""" % ''.join(h_str)
#

#    def _flagConsensus(self, cons_con_seq, cur_seq):
#        """
#        Annotate consensus  
#        """
#        h_str = []
#        for ix in range(len(cur_seq)):
#            cur_c = cur_seq[ix]
#            if cur_c == cons_con_seq[ix]:
#                h_str.append("<font color=green>+</font>")
#            elif cons_con_seq[ix] != " ":
#                h_str.append("<font color=red>-</font>")
#            else:
#                h_str.append(".")
#        return """<font face="Courier New, Courier, monospace">%s</font>""" % ''.join(h_str)
#

    def sequenceLines(self, seqID, title_class="ntitle", normal_class="normal"):
        """Returns HTML string for single sequence in alignment.

         - Must call for each sequence in the alignment.
         normal_class: css class to use to format rows
         title_class: css class to use to format title cells
        """
        #Variable which signifies if given sequence in alignment contains motifs
        contains_motifs=False
        #Generate first row in table
        html_list = ["""<tr bgcolor="eeeeee" class="%s"><td class="%s">%s</td><td colspan=4>&nbsp;</td></tr>"""%(normal_class, title_class, seqID)]
        #If there is a combined P for the sequences, put it in first row
        if self.combinedP:
            try:
                html_list = ["""<tr bgcolor="#eeeeee" class="%s">
                                <td class="%s">%s</td>
                                <td>%s</td>
                                <td>&nbsp;</td>
                                <td>&nbsp;</td>
                                <td>&nbsp;</td>
                                </tr>""" % ( normal_class, title_class, seqID,
                                         _format_number(float(
                        self.MotifResults.Results['CombinedP'][seqID])))]
            except KeyError:
                pass

        #For each module
        for module in self.Locations.keys():

            #kcons_seq = ''.join(module.majorityConsensus())
            #kcol_freqs = module.columnFrequencies()
            cons_seq, cons_con_seq =  self._makeConservationConsensus(module)

            #Check to see if it appeared in the sequence
            if seqID in self.Locations[module]:
                contains_motifs=True
                for index in self.Locations[module][seqID]:

                    cur_seq =  str(module[(seqID,index)])
                    html_list.append("""<tr class="%s">
            <td colspan=2>&nbsp;</td>
            <td>%s</td>
            <td>%s</td>
            <td><span style="%s">%s</span><br>%s</td>
            </tr>""" %(normal_class, module.ID,
                       _format_number(module.Pvalue),
                       self.ColorMap[module.ID],
                       cur_seq, 
                       self._flagConservedConsensus(cons_con_seq, cons_seq, cur_seq)
                       ))

        if not contains_motifs:
            html_list=[]
        return ''.join(html_list)
                    

class MotifLocationsBySequence(MotifFormatter):
    """Generates HTML table with Motifs organized by sequence.

        - Each sequence is listed as follows:

        Seq-ID  #_bases-module_sequence-#_bases-module_sequence-#_bases-etc 
    """

    def __init__(self,MotifResults=None):
        """init function for MotifLocationsBySequence class"""
        self.MotifResults = MotifResults
        self.ColorMap = self.getColorMap(MotifResults)

    def _get_location_dict(self):
        """Builds dict of all locations.
            {seqID:{index:module}}
        """
        #Dict with locations of every module keyed by seqID
        locations_list = []
        module_map = {}
        #If MotifResults object exists
        if self.MotifResults:
            #Build dict of all the locations:
            # {seqID:{index:module}}
            #For each motif in MotifResults object
            for motif in self.MotifResults.Motifs:
                #For each module in the Motif
                for module in motif.Modules:
                    #Get the location dict for that module
                    location_dict = module.LocationDict
                    #For each sequence the module is in
                    for seqID in location_dict.keys():
                        #For each module instance in the sequence
                        for index in location_dict[seqID]:
                            #Add module to dict
                            locations_list.append((seqID,index,module))
                            module_map[(seqID,index)] = module
        locations = Dict2D()
        locations.fromIndices(locations_list)
        self.ModuleMap = module_map
        return locations

    Locations = property(_get_location_dict)

    def formatLine(self, seqID, max_index_len):
        """Returns motif line """
        #Variable which signifies if given sequence in alignment contains motifs
        contains_motifs=False
        #List of strings for sequence line
        seq_line_list = []
        #Get all indices for the sequence
        indices = []
        if seqID in self.Locations:
            indices = self.Locations[seqID].keys()
            contains_motifs=True
        indices.sort()
        #Current position in sequence
        pos=0
        #For each index in sequence
        fmt_str = "%0" + max_index_len + "d"
        for index in indices:
            #Add distance between motifs or ends of sequence to list if > 0

            seq_line_list.append(fmt_str % (index-pos))
            #Add module instance sequence to list
            # HHHERE
            mod_id = self.ModuleMap[(seqID, index)].ID
            seq_line_list.append( """<span style="%s" onmouseover="return overlib('Motif ID: %s');" onmouseout="return nd();">%s</span>""" % ( self.ColorMap[mod_id], mod_id, self.Locations[seqID][index][(seqID,index)].Sequence))
            #Find new position in sequence
            pos = self.Locations[seqID][index][(seqID,index)].Location.End
        #Add distance from end of last module to end of sequence to list if > 0
        if len(self.MotifResults.Alignment[seqID])-pos > 0:
            seq_line_list.append(str(len(self.MotifResults.Alignment[seqID])\
                                     -pos))

        return '-'.join(seq_line_list), contains_motifs
       
    def sequenceLines(self, seqID, max_index_len, title_class="ntitle", normal_class="normal"):
        """Returns HTML string for single sequence in alignment.

         - Must call for each sequence in the alignment.

         title_class: css class to use to format title
         normal_class: css class to use to format text
        """
        seq_line_list, contains_motifs = self.formatLine(seqID, max_index_len)
        if contains_motifs:
            #Return sequence string
            return """<tr class="%s">
                        <td class="%s">%s</td>
                        <td>%s</td></tr>"""%( normal_class, title_class,
                            seqID, seq_line_list)
        else:
            return ''
        

    def __call__(self, order=None, wrap_html=False, title_class="ntitle",
                normal_class="normal"):
        """Call method for MotifLocationsBySequence class.
        
            - must pass in an alignment order
        """
        html_list = []

        # need to calculate this acrosss all

        all_indicies = []
        for locs in  self.Locations.values():
            all_indicies.extend(locs.keys())

        max_index_len = str(len(str(max(all_indicies))))

        #If MotifResults is not None
        if self.MotifResults:
            #For each sequence in alignment get HTML for that sequence
            html_list.append("""<tr class="%s"><td>Sequence ID</td><td>Motif Locations</td></tr>""" % title_class)
            if not order:
                order=sorted(self.Locations.keys())
            for seqID in order:
                html_list.append(self.sequenceLines(seqID, max_index_len, title_class, normal_class))
           
            out_str = "<table cellpadding=2 cellspacing=2 border=0>%s</table>" % ''.join(html_list)
             
            if wrap_html: 
                return """<html><head><title>Motif Finder Results</title></head><body>%s</body></html>""" % out_str 
            return out_str

        return "" 

        
class SequenceByMotif(MotifFormatter):
    """Generates HTML table with sequences organized by Motif.  """

    def __init__(self,MotifResults=None):
        """init function for MotifLocationsBySequence class"""
        self.MotifResults = MotifResults
        self.ColorMap = self.getColorMap(MotifResults)

    def _get_location_dict(self):
        """Build dict of all the locations:
            {module:{seqID:[indices]}}
        """
        location_dict = {}  #Dict with locations of every motif keyed by module
        if self.MotifResults:
            for motif in self.MotifResults.Motifs:
                for module in motif.Modules:
                    location_dict[module]=module.LocationDict
        return location_dict

    Locations = property(_get_location_dict)

    def __call__(self, wrap_html=False, title_class="ntitle", 
                 normal_class="normal", cons_thresh=.9):
        """Call method for SequenceByMotif class.  """

        #Start HTML string with table and table headers
        html_list = []

        #Get modules
        modules = self.Locations.keys()
        modules.sort()
        self.ConservationThresh = cons_thresh

        #For each module
        for module in modules:
            html_list.append(self.moduleLines(module, title_class, normal_class))

        out_str = """<table cellpadding=2 cellspacing=2 border=0>
               <tr class="%s"><td>Motif ID</td><td>Combined P-Value</td>
                    <td>Sequence ID</td>
                    <td>Motif Sequence</td>
               </tr>
               %s
               </table>""" % (title_class, ''.join(html_list))


        if html_list:
            if wrap_html:
                return"""<html><head><title>Motif Finder Results</title></head><body>%s</body></html>""" % out_str
            else:
                return out_str
        return "" 

    def _makeConservationConsensus(self, module):
        """
        Return conservation consensus string
        """
        cons_thresh = self.ConservationThresh

        cons_seq = ''.join(module.majorityConsensus())
        col_freqs = module.columnFrequencies()
        cons_con_seq = []
        for ix, col in enumerate(col_freqs):
            col_sum = sum(col.values())
            keep = False
            for b, v in col.items():
                cur_cons = v / col_sum
                if cur_cons >= cons_thresh:
                    keep = True
            if keep:
                cons_con_seq.append(cons_seq[ix])
            else:
                cons_con_seq.append(" ")
        return cons_seq, ''.join(cons_con_seq)


    def _highlightConsensus(self, con_seq, cons_con_seq, cur_seq, cur_color):
        """
        Hightlight positions identical to consensus
        """
        grey_style = """background-color: #dddddd; font-family: 'Courier New', Courier"""

        span_fmt = """<span style="%s">%s</span>"""
        h_str = []
        for ix in range(len(cur_seq)):
            cur_c = cur_seq[ix]
            if cur_c == cons_con_seq[ix]:
                h_str.append(span_fmt % (cur_color,cur_c))
            elif cur_c == con_seq[ix]:
                h_str.append(span_fmt % (grey_style,cur_c))
            else:
                h_str.append(cur_c)
        return ''.join(h_str)

    def moduleLines(self, module, title_class="ntitle", normal_class="normal"):
        """Returns HTML string for single module.

         - Must call for each module.
        """

        #cons_seq = ''.join(module.majorityConsensus())

        cons_seq, cons_con_seq = self._makeConservationConsensus(module)

        cur_color =  self.ColorMap[module.ID]

        #Generate first row in table
        html_list = ['<tr bgcolor="#eeeeee" class="%s"><td class="%s">%s</td><td>%s</td><td>&nbsp;</td><td><span style="%s">%s</span></td></tr>'%\
                     (normal_class, title_class, 
                      module.ID,
                      _format_number(module.Pvalue),
                      cur_color, 
                      cons_seq, 
                      )]
        sequences = self.Locations[module].keys()
        sequences.sort()
        #For each sequence
        for seq in sequences:
            cur_seq = str( module[(seq,self.Locations[module][seq][0])] )
            
            html_list.append("""<tr class="%s">
                                    <td>&nbsp;</td>
                                    <td>&nbsp;</td>
                                    <td class="%s">%s</td>
                                    <td style="font-family: 'Courier New', Courier, monospace">%s</td>
                               </tr>""" % (normal_class, title_class,
               seq, 
               #_format_number(module.Pvalue), 
               self._highlightConsensus(cons_seq, cons_con_seq, cur_seq, cur_color)
               ))
        return ''.join(html_list)

class HighlightOnAlignment(MotifFormatter):
    """Generates XML for motif data table and alignment with motifs highlighted.
    """
    
    def __init__(self, motif_results=None, doc_root="/"):
        """init function for HighlightOnAlignment class.
       
        motif_results: motif results object
        doc_root: doc root for hrefs
        """
        self.MotifResults = motif_results
        self.DocRoot = doc_root
        self.ColorMap = self.getColorMap(motif_results)
    
    def __call__(self,order=None):
        """call method for HighlightOnAlignment class.
        Generates XML for each motif and sequence which will be transformed
        by an XSLT stylesheet and sent to the browser.
        """
        motif_Xml_list = []
        base_Xml =["""<?xml version="1.0"?>
<?xml-stylesheet href="%smfStylesheet.xsl" type="text/xsl"?>""" % self.DocRoot]
        Xml_list = []
        for motif in self.MotifResults.Motifs:
            motif_Xml_list.append(self.motifXml(motif))
        Xml_list.append(Xml('motifs', motif_Xml_list))
        sequence_Xml = self.sequenceXml(self.MotifResults.Alignment,order)
        Xml_list.append(Xml('sequences', sequence_Xml))
        base_Xml.append(Xml('motif_finder_data', Xml_list))
        return '\n'.join(map(str, base_Xml))
    
    def sequenceXml(self, alignment,order=None):
        """Generates XML necessary to highlight motifs on an alignment.
        """
        sequence_Xml = []
        if not order:
            order = alignment.keys()
        for i,key in enumerate(order):
            seq = alignment[key]
            outer_Xml = []
            outer_Xml.append(Xml('base_string', [str(seq)], Delimiter=''))
            motif_Xml = []
            for motif in self.MotifResults.Motifs:
                inner_Xml = []
                #Create a bitvector mask for seq,
                # where Strict motif sequence matches on seq
                inner_Xml.append(Xml('strict',
                [str(VectorFromMatches(str(seq),motif.Modules[0].Template))],Delimiter=''))
                #Create a bitvector mask for seq,
                # where Loose motif sequence matches on seq
                inner_Xml.append(Xml('loose',
                [str(VectorFromMatches(str(seq),motif.Modules[0].Loose))],
                Delimiter='')
                    )
                motif_Xml.append(Xml('motif_vector', inner_Xml,
                                     {'motif':"%s"%(str(motif.Modules[0]))},
                                     Delimiter=''))
            outer_Xml.append(Xml('motif_vectors', motif_Xml))
            sequence_Xml.append(Xml('sequence', outer_Xml, {'index':"%s"%(i)}))
        return sequence_Xml
        
    
    def motifXml(self, motif):
        """Will generate all necessary Xml for each Motif that will in turn
        be transformed by an XSLT style sheet for output to a browser.
        """
        outer_list = []
        inner_list = []
        inner_list.append(Xml('strict', [motif.Modules[0].Strict[0].Sequence], Delimiter=''))
        inner_list.append(Xml('loose', [str(motif.Modules[0])], Delimiter=''))
        outer_list.append(Xml('base_string',inner_list, Delimiter=''))
        inner_list = []
        inner_list.append(Xml('strict', [len(motif.Modules[0].Strict)], Delimiter=''))
        inner_list.append(Xml('loose', [len(motif.Modules)], Delimiter=''))
        outer_list.append(Xml('frequency',inner_list, Delimiter=''))
        inner_list = []
        inner_list.append(Xml('strict',\
            [_format_number(motif.Modules[0].Pvalue)], Delimiter=''))
        inner_list.append(Xml('loose',
            [_format_number(avg([i.Pvalue for i in \
            motif.Modules[0].values() if i.Pvalue is not None]))], Delimiter=''))
        outer_list.append(Xml('pvalue',inner_list, Delimiter=''))
        
        return Xml('motif', outer_list, {"value":"%s"%(\
        motif.Modules[0].Template)})

class HighlightMotifs(MotifFormatter):
    """Generates HTML table with sequences highlighted """

    def makeModuleMap(self, motif_results):
        """
        Need to extract this b/c can't pickle motif_results... grr.

        motif_results: MotifResults object
        keep_module_ids: list of module ids to keep
        """
        module_map = {}  #Dict with locations of every motif keyed by module
        if motif_results:
            for motif in motif_results.Motifs:
                for module in motif.Modules:
                    mod_len = len(module.ConsensusSequence)
                    mod_id = str(module.ID)
                    for skey, indexes in module.LocationDict.items():
                        if skey not in module_map:
                            module_map[skey] = []
                        for ix in indexes:
                            module_map[skey].append((ix, mod_id, mod_len))
        return module_map



    def __init__(self, motif_results, NodeOrder=None, KeepIds=[], KeepAll=False):
        """Set up color map and motif results

        ModuleMap: flattened map (b/c of pickle problem.)
                generate using make_module_map() function
        Alignment: alignment object (or dict) 
        KeepIds: list of module ids to keep
        KeepAll: When True, ignores KeepIds and highlights all motifs
        """
        ModuleMap = self.makeModuleMap(motif_results)
        module_ids = set([])
        for skey, slist in ModuleMap.items():
            for stup in slist:
                module_ids.add(stup[1])
        self.ColorMap = self.getColorMapS0(sorted(list(module_ids)))
        self.ModuleMap = ModuleMap 
        self.Alignment = motif_results.Alignment
        self.KeepIds = set(KeepIds)
        self.KeepAll = KeepAll
        self.NodeOrder = NodeOrder
        self.GapMap = self.getGapMap()
        self.HighlightMap = {}

    def __call__(self, title_class="ntitle", normal_class="normal", row_class="highlight"):
        """Call method for HightlightMotifs class.  """

        #Start HTML string with table and table headers
        html_list = []

        #For each module
        for seq_id in self.NodeOrder: 
            html_list.append(self.highlightSequence(seq_id, title_class, row_class))

        out_str = """<table cellpadding=2 cellspacing=2 border=0>
               <tr class="ntitle">
                    <td colspan=2><p>Add description here.</p> </td>
               </tr>
         
               <tr class="%s"><td nowrap>Sequence ID</td>
                    <td>Sequence</td>
               </tr>
               %s
               </table>""" % (title_class, ''.join(html_list))


        if html_list:
                return out_str
        return ""
    
    def getGapMap(self):
        """Returns dict mapping gapped_coord to ungapped_coord in self.Alignment
        
            - {seq_id:{gapped_coord:ungapped_coord}}
        """
        gap_map = {}
        for k,v in self.Alignment.items():
            gapped, ungapped = ProteinAlphabet.gapMaps(v)
            gap_map[k] = gapped
        return gap_map

    def highlightSequence(self, seq_id, title_class="ntitle", row_class="highlight"):
        """Returns HTML string for single sequence.

        seq_id: sequence_id to highlight 
        """
        #Generate first row in table
        row_tmpl = """<tr class="%s">
                          <td class="%s">%s</td>
                          <td>%s</td>
                      </tr>"""
  
        mo_span_tmpl = """<span style="%s" onmouseover="return overlib('%s');" onmouseout="return nd();">%s</span>"""
        seq_list = list(self.Alignment[seq_id])
        seq_len = len(seq_list)
        seq_mask = zeros(seq_len)
        mod_id_map = {}

        if seq_id in self.ModuleMap:
            for mod_tup in self.ModuleMap[seq_id]:
                ix, mod_id, mod_len = mod_tup
                
                # skip modules we con't care about
                if not self.KeepAll and mod_id not in self.KeepIds:
                    continue

                mod_mask = zeros(seq_len)

                # mask motif region
                for i in range(ix,ix+mod_len):
                    gapped_ix = self.GapMap[seq_id][i]
                    mod_mask[gapped_ix] = 1

                # add to sequence map
                seq_mask += mod_mask

                # map module ids to indexes
                for jx in range(ix,ix+mod_len):
                    gapped_jx = self.GapMap[seq_id][jx]
                    if gapped_jx not in mod_id_map:
                        mod_id_map[gapped_jx] = [] 
                    mod_id_map[gapped_jx].append(mod_id)

            # get module regions
            for jx in nonzero(seq_mask):

                # if overlapping use red background, otherwise display color
                if seq_mask[jx] > 1:
                    style = "background-color: red"
                else:
                    style = self.ColorMap[mod_id_map[jx][0]].replace("font-family: 'Courier New', Courier, monospace", "")

                seq_list[jx] = mo_span_tmpl % (style,
                                                "<br>".join(['Motif ID: %s' % \
                                                x for x in mod_id_map[jx]]),
                                                seq_list[jx])

        # cache data
        self.HighlightMap[seq_id] = ''.join(seq_list)
        # return row output 
        return row_tmpl % (row_class, title_class, seq_id, ''.join(seq_list))



class HighlightMotifsForm(MotifFormatter):
    """Generates HTML form to submit module ids """

    def __init__(self,
                 MotifResults,
                 FormAction="/cgi-bin/motifcluster/highlight.py",
                 FormTarget="_blank"):
        """Set up color map and motif results

        MotifResults: MotifResults object
        ModuleIds: List of module ids to highlight 
        FormAction: Form action cgi-script
        FormTarget: Form target 
        """
        self.MotifResults = MotifResults
        self.ColorMap = self.getColorMap(MotifResults)
        self.Modules= self._get_modules()
        self.FormAction = FormAction
        self.FormTarget = FormTarget

    def _get_modules(self):
        """Build map of modules
            {seq_id:[(ix, module_id, module_len)]
        """
        modules = [] 
        if self.MotifResults:
            for motif in self.MotifResults.Motifs:
                for module in motif.Modules:
                    modules.append(module)
        return modules


    def __call__(self, title_class="ntitle", normal_class="normal", highlight_class="highlight"):
        """Call method for HightlightMotifs class.  """

        #Start HTML string with table and table headers
        cells = []

        # format cells
        for module in self.Modules:
            cur_tup = (module.Pvalue, len(module.LocationDict), 
                        self.moduleRow(module))
            cells.append(cur_tup)

        # sort by p value, then frequency
        cells = [x[-1] for x in sorted(cells)]
       
        cur_cells = []
        header_tmpl = """<td bgcolor=ffffff>&nbsp;</td><td>ID</td> <td>Motif</td> <td>Fequency</td> <td>P-Value</td>"""

        header_cells = []
        num_headers = len(cells)
        if num_headers > 3:
            num_headers = 3
        for i in range(num_headers):
            header_cells.append(header_tmpl)
        header_row = """<tr bgcolor=eeeeee class="%s">%s</tr>""" % (title_class, ''.join(header_cells))

        html_out = []
        html_out.append("""<tr class="%s">""" % highlight_class)

        for ix, cell in enumerate(cells):
            if ix % 3 == 0:
                if cur_cells:
                    html_out.append("""%s</tr><tr class="%s">""" % (''.join(cur_cells), highlight_class))
                cur_cells = []
                cur_cells.append(cell)
            else:
                cur_cells.append(cell)

        html_out.append("%s</tr>" % ''.join(cur_cells))
        out_str = """
               <form action="%s" method="POST" target="%s">
               <table cellpadding=2 cellspacing=2 border=0>
               %s
               %s
               </table>
               <p>
               <input type="Submit" value="Highlight Selected Motifs" />
               </p>
               </form> 
               """ % (self.FormAction, self.FormTarget,
                      header_row, ''.join(html_out))

        if cells:
            return out_str
        return "" 

    def moduleRow(self, module):
        """Returns HTML string for single module.

        module: module to generate 
        """
        #Generate first row in table
        cells_tmpl = """<td bgcolor=dddddd><input type="checkbox" name="module_ids" value="%s" checked /></td><td>%s</td><td ><span style="%s">%s</span></td><td>%d</td><td>%s</td>"""
  
        # return row output 
        return cells_tmpl % (module.ID, 
                             module.ID, 
                             self.ColorMap[module.ID], 
                             #str(module),
                             module.ConsensusSequence,
                             len(module.LocationDict),
                             _format_number(module.Pvalue))

   
class HighlightOnCrystal(MotifFormatter):
    """Generates pymol script to highlight motifs on crystal structure.
    """
    
    def __init__(self, motif_results=None, cons_thresh=0.9):
        """init function for HighlightOnAlignment class.
       
        motif_results: motif results object
        """
        self.ConservationThresh = float(cons_thresh)
        ModuleMap, ModuleConsMap = self.makeModuleMap(motif_results)
        module_ids = set([])
        for skey, slist in ModuleMap.items():
            for stup in slist:
                module_ids.add(stup[1])
        self.ColorMapHex = self.getColorMapS0(sorted(list(module_ids)))
        self.ModuleMap = ModuleMap 
        self.ModuleConsMap = ModuleConsMap 
        self.MotifResults = motif_results
        self.ColorMap = self.getColorMapRgb(motif_results)
        self.GapMap = {}
        self.HighlightMap = {}
        self.RunScriptString = \
'''
from pymol import cmd
cmd.load("%s")
cmd.do("run %s")
'''
        self.ColorFunctionString = \
'''
color_map = %s
color_command_list = %s
sticks_command_list = %s
#Set color list using color_map
set_color_list(list(color_map.items()))
#Set seq colors
for color_cmd in color_command_list:
    colors,indices,chain_id = color_cmd
    set_seq_colors(colors,indices,chain_id)
#Set sticks
for sticks_cmd in sticks_command_list:
    indices,chain_id = sticks_cmd
    set_show_shapes(indices,chain_id)

'''
    
    def __call__(self,seq_id,pdb_id,\
                sequence_type='Protein',\
                zipfile_dir='.',
                pdb_dir='/quicksand2/hamady/data/cron_sync/pdb/'):
        """call method for HighlightOnCrystal class.
        Generates pymol script for highlighting motifs on crystal structure and
        creates .zip archive with pdb file and pymol script.
        """
        #Get PDB file
        curr_pdb = \
            [x.rstrip("\n") for x in self.getPdb(pdb_id,pdb_dir).readlines()]
        

        #Get subject sequence
        subject_seq = self.MotifResults.Alignment[seq_id]
        #Get PDB chains
        pdb_matching, ungapped_to_pdb = \
            get_matching_chains(subject_seq,curr_pdb,sequence_type)
        
        pdb_aligned = align_subject_to_pdb(subject_seq,pdb_matching)
        #get color command list
        color_command_list, found_seq_motifs, missed_seq_motifs = \
            self.makeColorCommandLists(seq_id,pdb_aligned,ungapped_to_pdb)
        #get sticks command list
        sticks_command_list = \
            self.makeSticksCommandsConservedPositions(seq_id, pdb_aligned,\
                                                    ungapped_to_pdb)
        
        #Generate pdb file
        pdb_out = pdb_id+'.pdb'
        
        #Generate pymol script
        pymol_script_list = [PYMOL_FUNCTION_STRING,MAIN_FUNCTION_STRING]

        pymol_script_list.append(self.ColorFunctionString % (self.ColorMap,\
                                color_command_list,sticks_command_list))
        pymol_script_string = ''.join(pymol_script_list)
        pymol_script_name = '%s_motif_coloring.pml' % (pdb_id)
        
        pymol_execute_name = '%s_double_click_me.pml' % (pdb_id)
        pymol_execute_string = \
            self.RunScriptString % (pdb_out,pymol_script_name)
        
        
        
        #Generate zip file

        output_pre = get_tmp_filename(zipfile_dir, prefix="pdb_%s_" % pdb_id) 
        if output_pre.endswith(".txt"):
            output_pre = output_pre[:-4]
        zip_dir = output_pre.split("/")[-1]
        output_filename = output_pre + ".zip"
        web_name = output_filename.split("/")[-1]

        curr_zip = ZipFile(output_filename,'w')
        curr_zip.writestr(zip_dir + "/" + pymol_script_name,pymol_script_string)

        curr_zip.writestr(zip_dir + "/" + pdb_out,'\n'.join(curr_pdb))
        
        curr_zip.writestr(zip_dir + "/" + pymol_execute_name,pymol_execute_string)
        curr_zip.close()
        
        alignment_html = {}
        for k,v in pdb_aligned.items():
            alignment_html[k]=self.highlightSequence(seq_id,v[0],pdb_id,v[1])
     
        #print [module for module in self.MotifResults.Modules]

        #set up return dictionary
        return_dir = { "output_filename":output_filename, 
                       "web_name":web_name,
                       "colored_alignment":alignment_html,
                       #"found_seq_motifs":found_seq_motifs,
                       "found_seq_motifs":[(module.ID, _format_number(module.Pvalue)) for module in self.MotifResults.Modules if module.ID in found_seq_motifs],
                       "missed_seq_motifs":missed_seq_motifs,
                       "all_motifs":[(module.ID, _format_number(module.Pvalue)) for module in self.MotifResults.Modules],
                       "all_motif_colors":self.ColorMapHex}
        
        return return_dir

    #################################################### 
    # NEED TO REFACTOR THESE FUNCTIONS - THE ARE COPIED 3 TIMES!!
    #################################################### 
    def getConservedPositions(self,min_conservation=1.0):
        """Returns dict mapping motif id to list of conserved positions.
        """
        conserved_positions = {}
        for motif in self.MotifResults.Motifs:
            for module in motif.Modules:
                curr_id = module.ID
                conserved_positions[curr_id]=[]
                curr_profile = AlnToProfile(module,self.MotifResults.Alphabet)
                for ix,pos in enumerate(curr_profile.rowMax()):
                    if pos >= min_conservation:
                        conserved_positions[curr_id].append(ix)
        return conserved_positions

    def _flagConservedConsensus(self, cons_con_seq, cons_seq, cur_seq):
        """
        Annotate consensus  
        """
        color_style = """background-color: %s; font-family: 'Courier New', Courier"""

        span_fmt = """<span style="%s">%s</span>"""
        h_str = []
        for ix in range(len(cur_seq)):
            cur_c = cur_seq[ix]
            if cur_c == cons_con_seq[ix]:
                h_str.append(span_fmt % (color_style % "#eeeeee", "+"))
            elif cons_con_seq[ix] != " ":
                #h_str.append("<font color=red>-</font>")
                h_str.append(span_fmt % (color_style % "#ff0000", "-"))
            elif cons_seq[ix] == cur_c:
                #h_str.append("<font color=orange>*</font>")
                h_str.append(span_fmt % (color_style % "white", "*"))
            else:
                h_str.append("&nbsp;")
        return h_str 


    def makeColorCommandLists(self,seq_id, pdb_aligned, ungapped_to_pdb):
        """Returns lists of (colors, indices, and chain_id) for coloring.
        
            - each chain is a separate tuple in the list.
            - colors are named by motif id
        """
        #list of motifs found in pdb sequence
        found_seq_motifs = []
        #list of motifs not in pdb sequence
        missed_seq_motifs = []
        
        color_command_list = []
        #Get locations by sequence
        locations = \
            MotifLocationsBySequence(self.MotifResults).Locations[seq_id]
        for chain, aligned in pdb_aligned.items():
            #Get subject gap map
            subject_gapped,subject_ungapped = \
                self.MotifResults.Alphabet.gapMaps(aligned[0])
            #Get pdb gap map
            pdb_gapped,pdb_ungapped = \
                self.MotifResults.Alphabet.gapMaps(aligned[1])
            

            for curr_ix, curr_module in locations.items():
                curr_module_len = len(str(curr_module))
                curr_module_id = curr_module.ID
                #curr_color = self.ColorMap[curr_module_id]
                curr_color = "color_" + str(curr_module_id)
                #get index list
                ix_list = []
                #for each position in motif
                for i in range(curr_ix,curr_ix+curr_module_len):
                    #Get the gapped index of the motif in the subject seq
                    try:
                        sub_gap = subject_gapped[i]
                    except KeyError:
                        continue

                    #Get the ungapped index of the motif in the pdb seq
                    try:
                        pdb_ungap = pdb_ungapped[sub_gap]
                        
                        #Get the index of the position in pdb coordinates

                        pdb_ix = ungapped_to_pdb[chain][pdb_ungap]
                        ix_list.append(pdb_ix)
                    except KeyError:
                        continue

                    
                if ix_list:
                    ix_string = '+'.join(map(str,ix_list))
                    color_command_list.append(([curr_color],[ix_string],chain))
                    found_seq_motifs.append(curr_module_id)
                else:
                    missed_seq_motifs.append(curr_module_id)
        

        return color_command_list, found_seq_motifs, missed_seq_motifs
                
    
    def makeSticksCommandsConservedPositions(self,seq_id, pdb_aligned,\
        ungapped_to_pdb, min_conservation=1.0):
        """Returns list of (indices, chain_id) to show sticks at indices.
        
            - each chain is a separate tuple in the list.
        """
        conserved_positions = self.getConservedPositions()
        show_command_list = []
        #Get locations by sequence
        locations = \
            MotifLocationsBySequence(self.MotifResults).Locations[seq_id]
        for chain, aligned in pdb_aligned.items():
            #Get subject gap map
            subject_gapped,subject_ungapped = \
                self.MotifResults.Alphabet.gapMaps(aligned[0])
            #Get pdb gap map
            pdb_gapped,pdb_ungapped = \
                self.MotifResults.Alphabet.gapMaps(aligned[1])
            
            for curr_ix, curr_module in locations.items():
                curr_module_id = curr_module.ID
                curr_module_conserved = conserved_positions[curr_module_id]
                #get index list
                ix_list = []
                #for each position in motif
                for i in curr_module_conserved:
                    #Get the gapped index of the motif in the subject seq
                    try:
                        sub_gap = subject_ungapped[i]
                    except KeyError:
                        continue
                    #Get the ungapped index of the motif in the pdb seq
                    try:
                        pdb_ungap = pdb_gapped[sub_gap]
                        #Get the index of the position in pdb coordinates
                        
                        pdb_ix = ungapped_to_pdb[pdb_ungap]
                        ix_list.append(pdb_ix)
                    except KeyError:
                        continue
                
                if ix_list:
                    show_command_list.append((ix_list,chain))
        
        return show_command_list
    
    
    def getPdb(self,pdb_id, pdb_dir):
        """Returns open pdb file.
        
            - currently gets pdb file from pdb website.
        """
        pdb_file = pdb_dir + "pdb%s.ent" % pdb_id.lower()
        of = None
        try:
            of = open(pdb_file)
        except Exception, e:
            of = GzipFile(pdb_file + ".gz")
        return of 
    
    def getGapMap(self,seq_id,gapped_seq):
        """Returns dict mapping gapped_coord to ungapped_coord in self.Alignment
        
            - {seq_id:{gapped_coord:ungapped_coord}}
        """
        gap_map = {}
        gapped, ungapped = ProteinAlphabet.gapMaps(gapped_seq)
        gap_map[seq_id] = gapped
        return gap_map

    def highlightSequence(self, seq_id, seq_aligned, pdb_id, pdb_aligned,\
        title_class="ntitle", row_class="highlight"):
        """Returns HTML string for single sequence.

        seq_id: sequence_id to highlight 
        """
        #Generate first row in table
        seq_row_tmpl = """<tr class="%s">
                          <td class="%s">%s</td>
                          <td>%s</td>
                      </tr>"""
  
        mo_span_tmpl = """<span style="%s" onmouseover="return overlib('%s');" onmouseout="return nd();">%s</span>"""
        seq_list = list(seq_aligned)
        pdb_list = list(pdb_aligned)
        seq_len = len(seq_list)
        seq_mask = zeros(seq_len)
        #pdb sequence mask
        pdb_mask = zeros(seq_len)
        mod_id_map = {}
        
        self.GapMap = self.getGapMap(seq_id,seq_aligned)

        cons_str = list(" " * len(seq_list)) 
        if seq_id in self.ModuleMap:
            for mod_tup in self.ModuleMap[seq_id]:
                ix, mod_id, mod_len = mod_tup
                

                cons_seq, cons_con_seq =  self.ModuleConsMap[mod_id]
                cur_seq =  ''.join(seq_list[ix:ix+mod_len])
                cc_str = self._flagConservedConsensus(cons_con_seq, cons_seq, cur_seq)
                cons_str[ix:ix+mod_len] = cc_str

                mod_mask = zeros(seq_len)
                #pdb module mask
                pdb_mod_mask = zeros(seq_len)

                # mask motif region
                for i in range(ix,ix+mod_len):
                    gapped_ix = self.GapMap[seq_id][i]
                    mod_mask[gapped_ix] = 1
                    #only allow coloring of ungapped pdb sequence
                    if pdb_list[gapped_ix] != '-':
                        pdb_mod_mask[gapped_ix]=1

                # add to sequence map
                seq_mask += mod_mask
                pdb_mask += pdb_mod_mask

                # map module ids to indexes
                for jx in range(ix,ix+mod_len):
                    gapped_jx = self.GapMap[seq_id][jx]
                    if gapped_jx not in mod_id_map:
                        mod_id_map[gapped_jx] = [] 
                    mod_id_map[gapped_jx].append(mod_id)

            mm_str = []
            for ix in range(len(seq_list)):
                if seq_list[ix] == pdb_list[ix]:
                    mm_str.append("|")
                else:
                    mm_str.append("*")

            # get module regions
            for jx in nonzero(seq_mask):

                # if overlapping use red background, otherwise display color
                if seq_mask[jx] > 1:
                    style = "background-color: red"
                else:
                    style = self.ColorMapHex[mod_id_map[jx][0]].replace("font-family: 'Courier New', Courier, monospace", "")

                seq_list[jx] = mo_span_tmpl % (style,
                                                "<br>".join(['Motif ID: %s' % \
                                                x for x in mod_id_map[jx]]),
                                                seq_list[jx])
                pdb_list[jx] = mo_span_tmpl % (style,
                                                "<br>".join(['Motif ID: %s' % \
                                                x for x in mod_id_map[jx]]),
                                                pdb_list[jx])
        
        clean_cons_str = []
        for item in cons_str:
            if item == " ":
                clean_cons_str.append("&nbsp;")
            else:
                clean_cons_str.append(item)

        cons_str = ''.join(clean_cons_str)

        # cache data
        self.HighlightMap[seq_id] = ''.join(seq_list)
        # return row output 
        seq_row = seq_row_tmpl % (row_class, title_class, seq_id, ''.join(seq_list))
        pdb_row = seq_row_tmpl % (row_class, title_class, pdb_id, ''.join(pdb_list))
        high_row = seq_row_tmpl % (row_class, title_class, "Cons", ''.join(cons_str))
        mm_row = seq_row_tmpl % (row_class, title_class, "Mismatch", ''.join(mm_str))

        return ''.join(['<table>',high_row,seq_row,mm_row, pdb_row,'</table>'])
        
    def _makeConservationConsensus(self, module):
        """
        Return conservation consensus string
        """
        cons_thresh = self.ConservationThresh

        cons_seq = ''.join(module.majorityConsensus())
        col_freqs = module.columnFrequencies()
        cons_con_seq = []
        for ix, col in enumerate(col_freqs):
            col_sum = sum(col.values())
            keep = False
            for b, v in col.items():
                cur_cons = v / col_sum
                if cur_cons >= cons_thresh:
                    keep = True
            if keep:
                cons_con_seq.append(cons_seq[ix])
            else:
                cons_con_seq.append(" ")
        return cons_seq, ''.join(cons_con_seq)



    def makeModuleMap(self, motif_results):
        """
        Need to extract this b/c can't pickle motif_results... grr.

        motif_results: MotifResults object
        keep_module_ids: list of module ids to keep
        """
        module_map = {}  #Dict with locations of every motif keyed by module
        module_cons_map = {}
        if motif_results:
            for motif in motif_results.Motifs:
                for module in motif.Modules:
                    mod_id = str(module.ID)
                    mod_len = len(module.ConsensusSequence)
                    
                    if mod_id not in module_cons_map:
                        module_cons_map[mod_id] = self._makeConservationConsensus(module)
                    for skey, indexes in module.LocationDict.items():
                        if skey not in module_map:
                            module_map[skey] = []
                        for ix in indexes:
                            module_map[skey].append((ix, mod_id, mod_len))

        return module_map, module_cons_map


class GraphComponentMotifs(MotifFormatter):
    """Generates component graph of motifs 
   
    You have to install networkx package from https://networkx.lanl.gov
    in order to run this
    """
    def makeModuleMap(self, motif_results):
        """
        Need to extract this b/c can't pickle motif_results... grr.

        motif_results: MotifResults object
        keep_module_ids: list of module ids to keep
        """
        module_map = {}  #Dict with locations of every motif keyed by module
        aln_module_map = {} # module -> list of sequence ids
        module_count_map = {} # sequence id -> { motif: motif_ct}
        all_mod_ids = set([])
        rev_keys = self.RevAlignKeys
        ctr = 0
        if motif_results:
            for motif in motif_results.Motifs:
                for module in motif.Modules:
                    module_len = len(module.ConsensusSequence)
                    for skey, indexes in module.LocationDict.items():
                        if skey not in module_map:
                            module_map[skey] = []
                        for ix in indexes:
                            mod_id = str(module.ID)
                            module_map[skey].append((ix, mod_id, module_len))
                            if mod_id not in aln_module_map:
                                aln_module_map[mod_id] = set([])
                            aln_module_map[mod_id].add(rev_keys[skey]) 
                            if skey not in module_count_map:
                                module_count_map[skey] = {}
                            cur_mod = module_count_map[skey]
                            if mod_id not in cur_mod:
                                cur_mod[mod_id] = 0

                            cur_mod[mod_id] += 1 
                            all_mod_ids.add(mod_id)
        return module_map, aln_module_map, module_count_map, all_mod_ids

    def __init__(self, motif_results, edge_thresh=1):
        """Set up color map and motif results

        edge_thresh: minimum edge thresh in order 
        """
        from networkx import XGraph, draw_random

        self.Alignment = motif_results.Alignment
        aln_keys = self.Alignment.keys()
        self.AlignKeys = dict(zip(range(len(aln_keys)), aln_keys))
        self.RevAlignKeys = dict(zip(aln_keys, range(len(aln_keys))))

        ModuleMap, AlnModuleMap, ModuleCtMap, AllModuleIds = self.makeModuleMap(motif_results)
        module_ids = set([])
        for skey, slist in ModuleMap.items():
            for stup in slist:
                module_ids.add(stup[1])
        self.ColorMap = self.getColorMapS0(sorted(list(module_ids)))
        self.ModuleMap = ModuleMap 
        self.AlnModuleMap = AlnModuleMap
        self.ModuleCtMap = ModuleCtMap
        self.AllModuleIds = AllModuleIds
        self.EdgeThresh = edge_thresh

        self.CurGraph = XGraph()
        self._init_graph(edge_thresh)

    def _make_edges(self, aln_keys):
        """
        Return list of combos of align keys
        """
        num_aln_keys = len(aln_keys)
        edges = []
        for i in range(num_aln_keys):
            for j in range(i+1, num_aln_keys):
                edges.append((aln_keys[i], aln_keys[j]))
        return edges

    def _set_edges(self, edges):
        """
        Set edges. Increment weight count
        """
        cur_graph = self.CurGraph 
        for edge in edges:
            n1, n2 = edge
            for n in edge:
                if not cur_graph.has_node(n):
                    cur_graph.add_node(n)

            if cur_graph.has_edge(edge):
                weight = cur_graph.get_edge(n1,n2)
                cur_graph.add_edge(n1,n2,weight + 1)
            else:
                cur_graph.add_edge(n1,n2,1)


    def _init_graph(self, edge_thresh):
        """ Set up graph """

        # store list of seqs that each module contains
        for mod_key, aln_key_list in  self.AlnModuleMap.items():
            edges = self._make_edges(list(aln_key_list))
            self._set_edges(edges)
            #print edges
        
        cur_graph = self.CurGraph

        # delete edges with fewer than edge_thresh weight
        for edge in cur_graph.edges():
            n1,n2,weight = edge
            if weight < edge_thresh:
                cur_graph.delete_edge(n1,n2)
                 

    def __call__(self, write_dir, doc_root="/tmp", title_class="ntitle", 
                 normal_class="normal"):
        """Call method for HightlightMotifs class.  """

        from networkx import connected_components 

        components = connected_components(self.CurGraph)

        #Start HTML string with table and table headers
        html_list = []

        #For each module
        for component_num, component in enumerate(components): 
            html_list.append(self.displayComponent(component_num, component,
                    title_class, normal_class, write_dir, doc_root)) 

        motif_count_out = self.formatMotifCountTable()

        out_str = """<table cellpadding=2 cellspacing=2 border=0 width=800>
                <tr class="%s"><td colspan=4>Connected Component Graphs: (connection threshold >= %d)</td></tr> 
                <tr class="%s">
                    <td nowrap>#</td>
                    <td nowrap>&nbsp;</td>
                    <td>Short Sequence IDs</td>
                    <td nowrap>Download FASTA</td>
               </tr>
               <p>
               <span class=normal>
                Need to add description of count matrix below.
               </span>
               </p>
               %s
               </table><br>%s""" % (title_class, self.EdgeThresh, title_class, 
                                    ''.join(html_list), motif_count_out)


        if html_list:
            return out_str
        return ""
 
    def formatMotifCountTable(self,title_class="ntitle", normal_class="normal"):
        """ Format count table """

        all_module_ids = self.AllModuleIds
        all_rows = []
        rev_map = self.RevAlignKeys

        for seq_id, module_ids in self.ModuleCtMap.items():
            cur_counts = []
            for m_id in all_module_ids:
                if m_id in module_ids:
                    cur_counts.append(module_ids[m_id])
                else:
                    cur_counts.append(0)
            all_rows.append((rev_map[seq_id], seq_id, cur_counts))

        all_rows.sort()
        #comp_mo_href = """<a onmouseover="return overlib('Seq ID: %s');" onmouseout="return nd();">%d</a>"""
        comp_mo_href = """Seq ID: %s (%d)"""
        row_tmpl ="""<tr %s><td class="%s">%s</td>%s</tr>"""
        td_tmp = "<td class=%s>%%d</td>" % normal_class

        header = """<tr class="%s"><td>Sequence ID</td>%s</tr>""" % (
            title_class, ''.join(["""<td><span style="%s">M<br>o<br>t<br>i<br>f<br>:<br>%s</span></td>""" % (self.ColorMap[x], x) for x in all_module_ids]))
         
        rows = [header]
        for rn, line in enumerate(all_rows):
            bgstr = ""
            if rn % 2 == 0:
                bgstr = " bgcolor=eeeeee"

            rows.append(row_tmpl % (bgstr, title_class, 
                                    comp_mo_href % (line[1], line[0]), 
                                    ''.join([td_tmp % x for x in line[2]])))
        return "<table cellpadding=2 cellspacing=2 border=0>%s</table>" % '\n'.join(rows)



    def displayComponent(self, component_num, component, title_class="ntitle", 
                         normal_class="normal", write_dir="/tmp", 
                         doc_root="/tmp"):
        """
        Format component row
            
        Generate fasta files for download (make links)
        
        component id, list if ids (link to download)
        """
        from graph_writer import draw_graph
   
        # remove nodes not in current component

        GRAPH_MO_HREF = """<a href="#" onmouseover="return overlib('%s', STICKY, MOUSEOFF, FGCOLOR, '#FFFFFF', ABOVE, LEFT, CAPTION, 'Motif Graph', CAPCOLOR, '#000000', BGCOLOR, '#DDDDDD', CLOSECOLOR, 'blue');" onmouseout="return nd();" >%s</a><br>%s"""
        if len(component) > 1:
            cur_graph = self.CurGraph.copy()
            keep_list =  set(component)
            all_list =  set(cur_graph.nodes())
            del_list = list(all_list.difference(keep_list))
            
            for n in del_list:
                cur_graph.delete_node(n)

            fn, graph_link, eps_link = draw_graph(cur_graph, graph_type="random",
                            write_dir=write_dir, web_dir=doc_root+"/")
        
            mo_link = GRAPH_MO_HREF % (graph_link.replace('"', "\\'"),
                                   graph_link.replace("border=0", 
                                   "height=100 width=100 border=1"),
                                   eps_link) 
        else:
            mo_link = "<font color=red>Graph Suppressed.</font>"


        comp_mo_href = """<a onmouseover="return overlib('Seq ID: %s');" onmouseout="return nd();">%d</a>"""
        comp_keys = [comp_mo_href % (self.AlignKeys[x], x) for x in component]
        str_keys = [self.AlignKeys[x] for x in component]
        row_tmpl ="""<tr %s><td class="%s" align=center>%d</td>
                            <td class="%s">%s</td>
                            <td class="%s"><font color=blue>%s</b></td>
                            <td class="%s">%s</td>
                            </tr>"""
    
        bgstr = ""
        if component_num % 2 == 0:
            bgstr = " bgcolor=eeeeee"

        download_tmpl = """<a href="%s/%s" target="_blank" ><b>Download</b></a> """
        filename = get_tmp_filename(write_dir, "component_%d_" % component_num)
        of = open(filename, "w+")
        for skey in str_keys:
            of.write(">%s\n%s\n" % (skey, self.Alignment[skey].replace("-","")))
        of.close()
        
        return row_tmpl % (bgstr, title_class, component_num, 
                           normal_class, mo_link,
                           normal_class, ', '.join(comp_keys), 
                           normal_class, download_tmpl % (doc_root, filename.split("/")[-1]),
                           )


