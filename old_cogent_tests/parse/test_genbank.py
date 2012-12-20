#!/usr/bin/env python
#file cogent/parse/test_genbank.py
"""Unit tests for the GenBank database parsers.

Revision History

Written 7/15/05 by Rob Knight
"""
from old_cogent.parse.genbank import locus_parser, single_line_parser, \
    indent_splitter, sequence_parser, block_consolidator, organism_parser, \
    feature_parser, location_line_tokenizer, simple_location_segment_parser, \
    location_line_parser, reference_parser, source_parser, \
    Location, LocationList
from old_cogent.util.unit_test import TestCase, main


class GenBankTests(TestCase):
    """Tests of the GenBank main functions."""
    
    def test_locus_parser(self):
        """locus_parser should give correct results on specimen locus lines"""
        line = 'LOCUS       AF108830                5313 bp    mRNA    linear   PRI 19-MAY-1999'
        result = locus_parser(line)
        self.assertEqual(len(result), 6)
        self.assertEqual(result['locus'], 'AF108830')
        self.assertEqual(result['length'], 5313)    #note: int, not str
        self.assertEqual(result['mol_type'], 'mRNA')
        self.assertEqual(result['topology'], 'linear')
        self.assertEqual(result['db'], 'PRI')
        self.assertEqual(result['date'], '19-MAY-1999')
        #should work if some of the fields are missing
        line = 'LOCUS       AF108830                5313'
        result = locus_parser(line)
        self.assertEqual(len(result), 2)
        self.assertEqual(result['locus'], 'AF108830')
        self.assertEqual(result['length'], 5313)    #note: int, not str
       

    def test_single_line_parser(self):
        """single_line_parser should split off the label and return the rest"""
        line_1 = 'VERSION     AF108830.1  GI:4868112\n'
        self.assertEqual(single_line_parser(line_1), 'AF108830.1  GI:4868112')
        #should work if leading spaces
        line_2 = '      VERSION     AF108830.1  GI:4868112\n'
        self.assertEqual(single_line_parser(line_2), 'AF108830.1  GI:4868112')

    def test_indent_splitter(self):
        """indent_splitter should split lines at correct locations"""
        #if lines have same indent, should not group together
        lines = [
        'abc    xxx',
        'def    yyy'
        ]
        self.assertEqual(list(indent_splitter(lines)),\
            [[lines[0]], [lines[1]]])
        #if second line is indented, should group with first
        lines = [
        'abc    xxx',
        ' def    yyy'
        ]
        self.assertEqual(list(indent_splitter(lines)),\
            [[lines[0], lines[1]]])

        #if both lines indented but second is more, should group with first
        lines = [
        ' abc    xxx',
        '  def    yyy'
        ]
        self.assertEqual(list(indent_splitter(lines)),\
            [[lines[0], lines[1]]])
        
        #if both lines indented equally, should not group
        lines = [
        '   abc    xxx',
        '   def    yyy'
        ]
        self.assertEqual(list(indent_splitter(lines)), \
            [[lines[0]], [lines[1]]])

        #for more complex situation, should produce correct grouping
        lines = [
        '  xyz',    #0 -
        '  xxx',    #1 -
        '   yyy',   #2
        '   uuu',   #3
        '   iii',   #4
        '  qaz',    #5 -
        '  wsx',    #6 -
        '   az',    #7
        '   sx',    #8
        '        gb',#9
        '   bg',    #10
        '  aaa',    #11 -
        ]
        self.assertEqual(list(indent_splitter(lines)), \
            [[lines[0]], lines[1:5], [lines[5]], lines[6:11], [lines[11]]])

        #real example from genbank file
        lines = \
"""LOCUS       LAAJ4821    16866 bp    DNA             MAM       23-AUG-2000
DEFINITION  Loxodonta africana complete mitochondrial genomic sequence.
ACCESSION   AJ224821
VERSION     AJ224821.1  GI:3021460
KEYWORDS    complete genome.
SOURCE      African elephant.
  ORGANISM  Mitochondrion Loxodonta africana
            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
            Mammalia; Eutheria; Proboscidea; Elephantidae; Loxodonta.
REFERENCE   1  (bases 1 to 16866)
  AUTHORS   Hauf,J., Waddell,P.J., Chalwatzis,N., Joger,U. and Zimmermann,F.K.
  TITLE     The complete mitochondrial genome sequence of the African elephant
            (Loxodonta africana), phylogenetic relationships of Proboscidea to
            other mammals and D-loop heteroplasmy""".split('\n')
        self.assertEqual(list(indent_splitter(lines)), \
            [[lines[0]],[lines[1]],[lines[2]],[lines[3]],[lines[4]],lines[5:9],\
            lines[9:]])

    def test_sequence_parser(self):
        """sequence_parser should strip bad chars out of sequence lines"""
        lines = """
ORIGIN
        1 gggagcgcgg cgcgggagcc cgaggctgag actcaccgga ggaagcggcg cgagcgcccc
       61   gccatcgtcc \t\t cggctgaagt 123 \ngcagtg  \n
      121 cctgggctta agcagtcttc45ccacctcagc 
//\n\n\n""".split('\n')
        result = sequence_parser(lines)
        self.assertEqual(result, 'gggagcgcggcgcgggagcccgaggctgagactcaccggaggaagcggcgcgagcgccccgccatcgtcccggctgaagtgcagtgcctgggcttaagcagtcttcccacctcagc')
        
    def test_block_consolidator(self):
        """block_consolidator should join the block together."""
        lines = """  ORGANISM  Homo sapiens
            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
            Mammalia; Eutheria; Euarchontoglires; Primates; Catarrhini;
            Hominidae; Homo.""".split('\n')
        label, data = block_consolidator(lines)
        self.assertEqual(label, 'ORGANISM')
        self.assertEqual(data, ['Homo sapiens',
'            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;',
'            Mammalia; Eutheria; Euarchontoglires; Primates; Catarrhini;',
'            Hominidae; Homo.'])

    def test_organism_parser(self):
        """organism_parser should return species, taxonomy (up to genus)"""
        #note: lines modified to include the following:
        # - multiword names
        # - multiword names split over a line break
        # - periods and other punctuation in names
        lines = """  ORGANISM  Homo sapiens
        Eukaryota; Metazoa; Chordata Craniata; Vertebrata; Euteleostomi;
        Mammalia; Eutheria; Euarchontoglires; Primates \t abc.  2.; Catarrhini
        Hominidae; Homo.""".split('\n')
        species, taxonomy = organism_parser(lines)
        self.assertEqual(species, 'Homo sapiens')
        self.assertEqual(taxonomy, ['Eukaryota', 'Metazoa', \
            'Chordata Craniata', 'Vertebrata', 'Euteleostomi', 'Mammalia', \
            'Eutheria', 'Euarchontoglires', 'Primates abc. 2.', \
            'Catarrhini Hominidae', 'Homo'])

    def test_feature_parser(self):
        """feature_parser should return dict containing annotations of feature"""
        example_feature=\
"""     CDS             complement(join(102262..102647,105026..105217,
                     106638..106719,152424..152682,243209..243267))
                     /gene="nad1"
                     /note="Protein sequence is in conflict with the conceptual
                     translation; author given translation (not conceptual
                     translation)
                     start codon is created by C to U RNA editing"
                     /codon_start=1
                     /exception="RNA editing"
                     /product="NADH dehydrogenase subunit 1"
                     /protein_id="NP_064011.1"
                     /db_xref="GI:9838451"
                     /db_xref="IPI:12345"
                     /translation="MYIAVPAEILGIILPLLLGVAFLVLAERKVMAFVQRRKGPDVVG
                     SFGLLQPLADGSKLILKEPISPSSANFSLFRMAPVTTFMLSLVARAVVPFDYGMVLSD
                     PNIGLLYLFAISSLGVYGIIIAGWSSNSKYAFLGALRSAAQMVPYEVSIGLILITVLI
                     CVGPRNSSEIVMAQKQIWSGIPLFPVLVMFFISCLAETNRAPFDLPEAERELVAGYNV
                     EYSSMGSALFFLGEYANMILMSGLCTSLSPGGWPPILDLPISKRIPGSIWFSIKVILF
                     LFLYIWVRAAFPRYRYDQLMGLGRKVFLPLSLARVVAVSGVLVTFQWLP"""
        result = feature_parser(example_feature.split('\n'))
        self.assertEqual(result['type'], 'CDS')
        self.assertEqual(result['raw_location'], \
            ['complement(join(102262..102647,105026..105217,', \
'                     106638..106719,152424..152682,243209..243267))'])
        self.assertEqual(result['gene'], ['nad1'])
        self.assertEqual(result['note'], ['Protein sequence is in conflict with the conceptual translation; author given translation (not conceptual translation) start codon is created by C to U RNA editing'])
        self.assertEqual(result['codon_start'], ['1'])
        self.assertEqual(result['exception'], ['RNA editing'])
        self.assertEqual(result['product'], ['NADH dehydrogenase subunit 1'])
        self.assertEqual(result['protein_id'],['NP_064011.1'])
        self.assertEqual(result['db_xref'], ['GI:9838451','IPI:12345'])
        self.assertEqual(result['translation'],['MYIAVPAEILGIILPLLLGVAFLVLAERKVMAFVQRRKGPDVVGSFGLLQPLADGSKLILKEPISPSSANFSLFRMAPVTTFMLSLVARAVVPFDYGMVLSDPNIGLLYLFAISSLGVYGIIIAGWSSNSKYAFLGALRSAAQMVPYEVSIGLILITVLICVGPRNSSEIVMAQKQIWSGIPLFPVLVMFFISCLAETNRAPFDLPEAERELVAGYNVEYSSMGSALFFLGEYANMILMSGLCTSLSPGGWPPILDLPISKRIPGSIWFSIKVILFLFLYIWVRAAFPRYRYDQLMGLGRKVFLPLSLARVVAVSGVLVTFQWLP'])
        self.assertEqual(len(result), 11)

        short_feature = ['D-loop          15418..16866']
        result = feature_parser(short_feature)
        self.assertEqual(result['type'], 'D-loop')
        self.assertEqual(result['raw_location'], ['15418..16866'])
        #can get more than one = in a line
        #from AF260826  
        bad_feature = \
"""     tRNA            1173..1238
                     /note="codon recognized: AUC; Cove score = 16.56"
                     /product="tRNA-Ile"
                     /anticodon=(pos:1203..1205,aa:Ile)"""
        result = feature_parser(bad_feature.split('\n'))
        self.assertEqual(result['note'], \
            ['codon recognized: AUC; Cove score = 16.56'])
        #need not always have an = in a line
        #from NC_001807
        bad_feature = \
'''     mRNA            556
     /partial
     /citation=[6]
     /product="H-strand"'''
        result = feature_parser(bad_feature.split('\n'))
        self.assertEqual(result['partial'], [''])

    def test_location_line_tokenizer(self):
        """location_line_tokenizer should tokenize location lines"""
        llt =location_line_tokenizer
        self.assertEqual(list(llt(['123..456'])), ['123..456'])
        self.assertEqual(list(llt(['complement(123..456)'])), \
            ['complement(', '123..456', ')'])
        self.assertEqual(list(llt(['join(1..2,3..4)'])), \
            ['join(', '1..2', ',', '3..4', ')'])
        self.assertEqual(list(llt([\
            'join(complement(1..2, join(complement( 3..4),',\
            '\n5..6), 7..8\t))'])),\
            ['join(','complement(','1..2',',','join(','complement(','3..4',\
            ')', ',', '5..6',')',',','7..8',')',')'])

    def test_simple_location_segment_parser(self):
        """simple_location_segment_parser should parse simple segments"""
        lsp = simple_location_segment_parser
        l = lsp('37')
        self.assertEqual(l._data, 37)
        self.assertEqual(str(l), '37')
        self.assertEqual(l.Strand, 1)
        l = lsp('40..50')
        first, second = l._data
        self.assertEqual(first._data, 40)
        self.assertEqual(second._data, 50)
        self.assertEqual(str(l), '40..50')
        self.assertEqual(l.Strand, 1)
        #should handle ambiguous starts and ends
        l = lsp('>37')
        self.assertEqual(l._data, 37)
        self.assertEqual(str(l), '>37')
        l = lsp('<37')
        self.assertEqual(l._data, 37)
        self.assertEqual(str(l), '<37')
        l = lsp('<37..>42')
        first, second = l._data
        self.assertEqual(first._data, 37)
        self.assertEqual(second._data, 42)
        self.assertEqual(str(first), '<37')
        self.assertEqual(str(second), '>42')
        self.assertEqual(str(l), '<37..>42')

    def test_location_line_parser(self):
        """location_line_parser should give correct list of location objects"""
        llt = location_line_tokenizer
        r = location_line_parser(llt(['123..456']))
        self.assertEqual(str(r), '123..456')
        r = location_line_parser(llt(['complement(123..456)']))
        self.assertEqual(str(r), 'complement(123..456)')
        r = location_line_parser(llt(['complement(123..456, 345..678)']))
        self.assertEqual(str(r), \
            'join(complement(345..678),complement(123..456))')
        r = location_line_parser(llt(['complement(join(123..456, 345..678))']))
        self.assertEqual(str(r), \
            'join(complement(345..678),complement(123..456))')
        r = location_line_parser(\
            llt(['join(complement(123..456), complement(345..678))']))
        self.assertEqual(str(r), \
            'join(complement(123..456),complement(345..678))')
        #try some nested joins and complements
        r = location_line_parser(llt(\
            ['complement(join(1..2,3..4,complement(5..6),',
              'join(7..8,complement(9..10))))']))
        self.assertEqual(str(r), \
          'join(9..10,complement(7..8),5..6,complement(3..4),complement(1..2))')

    def test_reference_parser(self):
        """reference_parser should give correct fields"""
        r = \
"""REFERENCE   2  (bases 1 to 2587)
  AUTHORS   Janzen,D.M. and Geballe,A.P.
  TITLE     The effect of eukaryotic release factor depletion on translation
            termination in human cell lines
  JOURNAL   (er) Nucleic Acids Res. 32 (15), 4491-4502 (2004)
   PUBMED   15326224"""
        result = reference_parser(r.split('\n'))
        self.assertEqual(len(result), 5)
        self.assertEqual(result['reference'], '2  (bases 1 to 2587)')
        self.assertEqual(result['authors'], 'Janzen,D.M. and Geballe,A.P.')
        self.assertEqual(result['title'], \
            'The effect of eukaryotic release factor depletion ' + \
            'on translation termination in human cell lines')
        self.assertEqual(result['journal'], \
            '(er) Nucleic Acids Res. 32 (15), 4491-4502 (2004)')
        self.assertEqual(result['pubmed'], '15326224')

    def test_source_parser(self):
        """source_parser should split into source and organism"""
        s = \
"""SOURCE      African elephant.
  ORGANISM  Mitochondrion Loxodonta africana
            Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
            Mammalia; Eutheria; Proboscidea; Elephantidae; Loxodonta.""".split('\n')
        r = source_parser(s)
        self.assertEqual(len(r), 3)
        self.assertEqual(r['source'], 'African elephant.')
        self.assertEqual(r['species'], 'Mitochondrion Loxodonta africana')
        self.assertEqual(r['taxonomy'], ['Eukaryota','Metazoa', 'Chordata',\
            'Craniata', 'Vertebrata', 'Euteleostomi', 'Mammalia',\
            'Eutheria', 'Proboscidea', 'Elephantidae', 'Loxodonta'])
        
class LocationTests(TestCase):
    """Tests of the Location class."""
    def test_init(self):
        """Location should init with 1 or 2 values, plus params."""
        l = Location(37)
        self.assertEqual(str(l), '37')
        l = Location(37, Ambiguity = '>')
        self.assertEqual(str(l), '>37')
        l = Location(37, Ambiguity='<')
        self.assertEqual(str(l), '<37')
        l = Location(37, Accession='AB123')
        self.assertEqual(str(l), 'AB123:37')
        l = Location(37, Accession='AB123', Db='Kegg')
        self.assertEqual(str(l), 'Kegg::AB123:37')

        l1 = Location(37)
        l2 = Location(42)
        l = Location([l1,l2])
        self.assertEqual(str(l), '37..42')
        l3 = Location([l1,l2], IsBounds=True)
        self.assertEqual(str(l3), '(37.42)')
        l4 = Location([l1,l2], IsBetween=True)
        self.assertEqual(str(l4), '37^42')
        l5 = Location([l4,l3])
        self.assertEqual(str(l5), '37^42..(37.42)')
        l5 = Location([l4,l3], Strand=-1)
        self.assertEqual(str(l5), 'complement(37^42..(37.42))')

class LocationListTests(TestCase):
    """Tests of the LocationList class."""
    def test_extract(self):
        """LocationList extract should return correct sequence"""
        l = Location(3)
        l2_a = Location(5)
        l2_b = Location(7)
        l2 = Location([l2_a,l2_b], Strand=-1)
        l3_a = Location(10)
        l3_b = Location(12)
        l3 = Location([l3_a, l3_b])
        ll = LocationList([l, l2, l3])
        s = ll.extract('ACGTGCAGTCAGTAGCAT')
        #               123456789012345678
        self.assertEqual(s, 'G'+'TGC'+'CAG')
        #check a case where it wraps around
        l5_a = Location(16)
        l5_b = Location(4)
        l5 = Location([l5_a,l5_b])
        ll = LocationList([l5])
        s = ll.extract('ACGTGCAGTCAGTAGCAT')
        self.assertEqual(s, 'CATACGT')
        
        
        

        
if __name__ == '__main__':
    from sys import argv
    if len(argv) > 2 and argv[1] == 'x':
        filename = argv[2]
        lines = open(filename)
        for i in indent_splitter(lines):
            print '******'
            print i[0]
            for j in indent_splitter(i[1:]):
                print '?????'
                for line in j:
                    print line
    else:
        main()
    
