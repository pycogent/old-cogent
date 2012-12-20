#!/usr/bin/env python
#file cogent/db/ncbi.py
"""
Purpose:
    To automate batch functions provided by EUtils
    (http://www.ncbi..nih.gov/entrez/eutils) so that we can
    search and fetch for sets of sequence information

Owner: Mike Robeson (Michael Robeson@colorado.edu)

Status: Develpment

Development History:
July 20, 2005
    File Created by Mike Robeson
    Not all possible parameters of EUtils are implemented at the moment, just
    enough to see if we can get the basics to work.
July 21, 2005
    Edited by Rob Knight (mostly) and Mike Robeson. Added the classes: \
        UrlGetter, ESearch, EFetch, GenBank (not complete).

7/22-24/05 Rob Knight: added XML parsing and hooked up the esearch/efetch steps
so that we can actually get records. Exciting stuff! Rudimentary command-line
functionality added. Added dicts of valid databases and report formats, mainly
for my own information when testing from the commandline. No validation is
currently performed -- not sure whether we should add it, since new report
formats are added so frequently.

03/07/06 Zongzhi Liu: the method _expand_slice becomes a function named
expand_slice, passed a test from omim_xml.py
"""
from urllib import urlopen, urlretrieve
from xml.dom.minidom import parseString

eutils_base='http://eutils.ncbi.nlm.nih.gov/entrez/eutils'
        
#databases last updated 7/22/05
valid_databases=dict.fromkeys(["pubmed", "protein", "nucleotide", "structure",\
    "genome", "books", "cancerchromosomes", "cdd", "domains", "gene", \
    "genomeprj", "gensat", "geo", "gds", "homologene", "journals", "mesh",\
    "ncbisearch", "nlmcatalog", "omim", "pmc", "popset", "probe", "pcassay",\
    "pccompound", "pcsubstance", "snp", "taxonomy", "unigene", "unists"])

#rettypes last updated 7/22/05
#somehow, I don't think we'll be writing parsers for all these...
rettypes = {}
rettypes['pubmed']='DocSum Brief Abstract Citation MEDLINE XML uilist ExternalLink ASN1 pubmed_pubmed pubmed_pubmed_refs pubmed_books_refs pubmed_cancerchromosomes pubmed_cdd pubmed_domains pubmed_gds pubmed_gene pubmed_gene_rif pubmed_genome pubmed_genomeprj pubmed_gensat pubmed_geo pubmed_homologene pubmed_nucleotide pubmed_omim pubmed_pcassay pubmed_pccompound pubmed_pccompound_mesh pubmed_pcsubstance pubmed_pcsubstance_mesh pubmed_pmc pubmed_pmc_refs pubmed_popset pubmed_probe pubmed_protein pubmed_snp pubmed_structure pubmed_unigene pubmed_unists'

rettypes['protein']='DocSum ASN1 FASTA XML GenPept GiList graph fasta_xml igp_xml gpc_xml ExternalLink protein_protein protein_cdd protein_domains protein_gene protein_genome protein_genomeprj protein_homologene protein_nucleotide protein_nucleotide_mgc protein_omim protein_pcassay protein_pccompound protein_pcsubstance protein_pmc protein_popset protein_pubmed protein_snp protein_snp_genegenotype protein_structure protein_taxonomy protein_unigene'

rettypes['nucleotide']='DocSum ASN1 FASTA XML GenBank GiList graph fasta_xml gb_xml gbc_xml ExternalLink nucleotide_comp_nucleotide nucleotide_nucleotide nucleotide_nucleotide_comp nucleotide_nucleotide_mrna nucleotide_comp_genome nucleotide_gene nucleotide_genome nucleotide_genome_samespecies nucleotide_gensat nucleotide_geo nucleotide_homologene nucleotide_mrna_genome nucleotide_omim nucleotide_pcassay nucleotide_pccompound nucleotide_pcsubstance nucleotide_pmc nucleotide_popset nucleotide_probe nucleotide_protein nucleotide_pubmed nucleotide_snp nucleotide_snp_genegenotype nucleotide_structure nucleotide_taxonomy nucleotide_unigene nucleotide_unists'

rettypes['structure']='DocSum Brief Structure Summary uilist ExternalLink structure_domains structure_genome structure_nucleotide structure_omim structure_pcassay structure_pccompound structure_pcsubstance structure_pmc structure_protein structure_pubmed structure_snp structure_taxonomy'

rettypes['genome']='DocSum ASN1 GenBank XML ExternalLink genome_genomeprj genome_nucleotide genome_nucleotide_comp genome_nucleotide_mrna genome_nucleotide_samespecies genome_omim genome_pmc genome_protein genome_pubmed genome_structure genome_taxonomy'

rettypes['books']='DocSum Brief Books books_gene books_omim books_pmc_refs books_pubmed_refs'

rettypes['cancerchromosomes']='DocSum SkyCghDetails SkyCghCommon SkyCghCommonVerbose cancerchromosomes_cancerchromosomes_casecell cancerchromosomes_cancerchromosomes_cellcase cancerchromosomes_cancerchromosomes_cytocgh cancerchromosomes_cancerchromosomes_cytoclincgh cancerchromosomes_cancerchromosomes_cytoclinsky cancerchromosomes_cancerchromosomes_cytodiagcgh cancerchromosomes_cancerchromosomes_cytodiagsky cancerchromosomes_cancerchromosomes_cytosky cancerchromosomes_cancerchromosomes_diag cancerchromosomes_cancerchromosomes_textual cancerchromosomes_pmc cancerchromosomes_pubmed'

rettypes['cdd']='DocSum Brief uilist cdd_cdd_fused cdd_cdd_related cdd_gene cdd_homologene cdd_pmc cdd_protein cdd_pubmed cdd_taxonomy'

rettypes['domains']='DocSum Brief uilist domains_domains_new domains_pmc domains_protein domains_pubmed domains_structure domains_taxonomy'

rettypes['gene']='Default DocSum Brief ASN.1 XML Graphics gene_table uilist ExternalLink gene_books gene_cdd gene_gensat gene_geo gene_homologene gene_nucleotide gene_nucleotide_mgc gene_omim gene_pmc gene_probe gene_protein gene_pubmed gene_pubmed_rif gene_snp gene_snp_genegenotype gene_taxonomy gene_unigene gene_unists'

rettypes['genomeprj']='DocSum Brief Overview genomeprj_genomeprj genomeprj_genome genomeprj_nucleotide genomeprj_nucleotide_mrna genomeprj_nucleotide_organella genomeprj_nucleotide_wgs genomeprj_pmc genomeprj_popset genomeprj_protein genomeprj_pubmed genomeprj_taxonomy'

rettypes['gensat']='Group Detail DocSum Brief gensat_gensat gensat_gene gensat_geo gensat_nucleotide gensat_pmc gensat_pubmed gensat_taxonomy gensat_unigene'

rettypes['geo']='DocSum Brief ExternalLink geo_geo_homologs geo_geo_prof geo_geo_seq geo_gds geo_gene geo_gensat geo_homologene geo_nucleotide geo_omim geo_pmc geo_pubmed geo_taxonomy geo_unigene'

rettypes['gds']='DocSum Brief gds_gds gds_geo gds_pmc gds_pubmed gds_taxonomy'

rettypes['homologene']='DocSum Brief HomoloGene AlignmentScores MultipleAlignment ASN1 XML FASTA homologene_homologene homologene_cdd homologene_gene homologene_geo homologene_nucleotide homologene_omim homologene_pmc homologene_protein homologene_pubmed homologene_snp homologene_snp_genegenotype homologene_taxonomy homologene_unigene'

rettypes['journals']='DocSum full journals_PubMed journals_Protein journals_Nucleotide journals_Genome journals_Popset journals_PMC journals_nlmcatalog'

rettypes['mesh']='Full DocSum Brief mesh_PubMed'

rettypes['ncbisearch']='DocSum Brief Home+Page+View ncbisearch_ncbisearch'

rettypes['nlmcatalog']='Brief DocSum XML Expanded Full Subject ExternalLink'

rettypes['omim']='DocSum Detailed Synopsis Variants ASN1 XML ExternalLink omim_omim omim_books omim_gene omim_genome omim_geo omim_homologene omim_nucleotide omim_pmc omim_protein omim_pubmed omim_snp omim_snp_genegenotype omim_structure omim_unigene omim_unists'

rettypes['pmc']='DocSum Brief XML TxTree pmc_books_refs pmc_cancerchromosomes pmc_cdd pmc_domains pmc_gds pmc_gene pmc_genome pmc_genomeprj pmc_gensat pmc_geo pmc_homologene pmc_nucleotide pmc_omim pmc_pccompound pmc_pcsubstance pmc_popset pmc_protein pmc_pubmed pmc_refs_pubmed pmc_snp pmc_structure pmc_taxonomy pmc_unists'

rettypes['popset']='DocSum PS ASN1 XML GiList ExternalLink TxTree popset_genomeprj popset_nucleotide popset_protein popset_pubmed popset_taxonomy'

rettypes['probe']='DocSum Brief ASN1 XML Probe probe_probe probe_gene probe_nucleotide probe_pubmed probe_taxonomy'

rettypes['pcassay']='DocSum Brief uilist pcassay_nucleotide pcassay_pccompound pcassay_pccompound_active pcassay_pccompound_inactive pcassay_pcsubstance pcassay_pcsubstance_active pcassay_pcsubstance_inactive pcassay_protein pcassay_pubmed pcassay_structure'

rettypes['pccompound']='Brief DocSum PROP SYNONYMS pc_fetch pccompound_pccompound_pulldown pccompound_pccompound_sameanytautomer_pulldown pccompound_pccompound_sameconnectivity_pulldown pccompound_pccompound_sameisotopic_pulldown pccompound_pccompound_samestereochem_pulldown pccompound_nucleotide pccompound_pcassay pccompound_pcassay_active pccompound_pcassay_inactive pccompound_pcsubstance pccompound_pmc pccompound_protein pccompound_pubmed pccompound_pubmed_mesh pccompound_structure'

rettypes['pcsubstance']='Brief DocSum PROP SYNONYMS pc_fetch IDLIST pcsubstance_pcsubstance_pulldown pcsubstance_pcsubstance_same_pulldown pcsubstance_pcsubstance_sameanytautomer_pulldown pcsubstance_pcsubstance_sameconnectivity_pulldow pcsubstance_pcsubstance_sameisotopic_pulldown pcsubstance_pcsubstance_samestereochem_pulldown pcsubstance_mesh pcsubstance_nucleotide pcsubstance_pcassay pcsubstance_pcassay_active pcsubstance_pcassay_inactive pcsubstance_pccompound pcsubstance_pmc pcsubstance_protein pcsubstance_pubmed pcsubstance_pubmed_mesh pcsubstance_structure'

rettypes['snp']='DocSum Brief FLT ASN1 XML FASTA RSR ssexemplar CHR FREQXML GENB GEN GENXML DocSet Batch uilist GbExp ExternalLink MergeStatus snp_snp_genegenotype snp_gene snp_homologene snp_nucleotide snp_omim snp_pmc snp_protein snp_pubmed snp_structure snp_taxonomy snp_unigene snp_unists'

rettypes['taxonomy']='DocSum Brief TxUidList TxInfo XML TxTree ExternalLink taxonomy_protein taxonomy_nucleotide taxonomy_structure taxonomy_genome taxonomy_gene taxonomy_cdd taxonomy_domains taxonomy_gds taxonomy_genomeprj taxonomy_gensat taxonomy_homologene taxonomy_pmc taxonomy_popset taxonomy_probe taxonomy_pubmed taxonomy_snp taxonomy_unigene taxonomy_unists'

rettypes['unigene']='DocSum Brief ExternalLink unigene_unigene unigene_unigene_expression unigene_unigene_homologous unigene_gene unigene_gensat unigene_geo unigene_homologene unigene_nucleotide unigene_nucleotide_mgc unigene_omim unigene_protein unigene_pubmed unigene_snp unigene_snp_genegenotype unigene_taxonomy unigene_unists'

rettypes['unists']='DocSum Brief ExternalLink unists_gene unists_nucleotide unists_omim unists_pmc unists_pubmed unists_snp unists_taxonomy unists_unigene'

#convert into dict of known rettypes for efficient lookups -- don't want to
#scan list every time.
for key, val in rettypes.items():
    rettypes[key] = dict.fromkeys(val.split())

class UrlGetter(object):
    Defaults = {}       #override in derived classes -- default values
    PrintedFields = {}  #override in derived classes -- fields to print
    BaseUrl = ''        #override in derived classes
    KeyValDelimiter = '='
    FieldDelimiter = '&'
    
    def __init__(self, **kwargs):
        self.__dict__.update(self.Defaults)
        self.__dict__.update(kwargs)

    def __str__(self):
        return self.BaseUrl + self.FieldDelimiter.join(\
            [k+self.KeyValDelimiter+str(v) for k, v in self.__dict__.items()\
            if k in self.PrintedFields])

    def open(self, **kwargs):
        """Returns a stream handle to URL result."""
        self.__dict__.update(kwargs)
        return urlopen(str(self))

    def read(self, **kwargs):
        """Gets URL and reads into memory."""
        result = self.open(**kwargs)
        data = result.read()
        result.close()
        return data

    def retrieve(self, fname, **kwargs):
        """Gets URL and writes to file fname. No return value."""
        self.__dict__.update(**kwargs)
        urlretrieve(str(self), fname)
        
class ESearch(UrlGetter):
    PrintedFields = dict.fromkeys(['db', 'usehistory', 'term'])
    Defaults = {'db':'nucleotide','usehistory':'y'}
    BaseUrl = eutils_base+'/esearch.fcgi?'

class EFetch(UrlGetter):
    PrintedFields = dict.fromkeys(['db', 'rettype', 'retmode', 'query_key',\
        'WebEnv', 'retmax'])
    Defaults = {'retmode':'text','rettype':'fasta','db':'nucleotide',\
            'retmax':3}#'retmax':100}
    BaseUrl = eutils_base+'/efetch.fcgi?'

class ESearchResult(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __str__(self):
        return str(self.__dict__)

def id_list_constructor(id_list_node):
    """Takes an id_list xml node and converts it into list of ids as strings"""
    return [str_constructor(n) for n in id_list_node.childNodes \
        if n.nodeType != n.TEXT_NODE]

def int_constructor(node):
    """Makes an int out of node's first textnode child."""
    return int(node.firstChild.data)

def str_constructor(node):
    """Makes an str out of node's first textnode child."""
    return str(node.firstChild.data)

#the following are the only keys we explicitly handle now:
esearch_constructors = {'Count':int_constructor, 'RetMax':int_constructor,\
    'RetStart':int_constructor, 'QueryKey':int_constructor, \
    'WebEnv':str_constructor, 'IdList':id_list_constructor}

def ESearchResultParser(result_as_string):
    """Parses an ESearch result. Returns ESearchResult object."""
    doc = parseString(result_as_string)
    #assume one query result -- may need to fix
    query = doc.childNodes[-1]
    result = {}
    for n in query.childNodes:
        #skip top-level text nodes
        if n.nodeType==n.TEXT_NODE:
            continue
        name = str(n.tagName)   #who cares about unicode anyway...
        if name in esearch_constructors:
            result[name] = esearch_constructors[name](n)
        else:   #just keep the data if we don't know what it is
            result[name] = n.toxml()
    return ESearchResult(**result)

class GenBank(object):
    DEBUG=False
    filename=None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __getitem__(self, query):
        """Gets an item from GenBank. Assumes lists are lists of accessions.
        
        Returns a handle to the result (either in memory or file on disk).
        WARNING: result is not guaranteed to contain any data.
        """
        #check if it's a slice
        if isinstance(query, slice):
            query = expand_slice(query)
        #check if it's a list -- if so, delimit with '+'
        if isinstance(query, list) or isinstance(query,tuple):
            query = '+'.join(map(str, query))
        self.term = query
        search_query = ESearch(**self.__dict__)
        #do the search
        cookie = search_query.read()
        if self.DEBUG:
            print `cookie`
        search_result = ESearchResultParser(cookie)
        if self.DEBUG:
            print search_result
        #set the query key and WebEnv
        self.query_key = search_result.QueryKey
        self.WebEnv = search_result.WebEnv
        #do the fetch
        fetch_query = EFetch(**self.__dict__)
        #return the result of the fetch
        if self.filename:
            fetch_query.retrieve(self.filename)
            return(open(self.filename))
        else:
            return fetch_query

def expand_slice(s):
    """Takes a start and end accession, and gets the whole range.

    WARNING: Unlike standard slices, includes the last item in the range.
    In other words, self[AF1001:AF1010] will include AF1010.
    
    Both accessions must have the same non-numeric prefix.
    """
    start, step, end = s.start, s.step, s.stop
    #find where the number is
    start_index = last_nondigit_index(start)
    end_index = last_nondigit_index(end)
    prefix = start[:start_index]
    if prefix != end[:end_index]:
        raise TypeError, "Range start and end don't have same prefix"
    if not step:
        step = 1
    range_start = long(start[start_index:])
    range_end = long(end[end_index:])
    return [prefix+str(i) for i in range(range_start, range_end+1, step)]
    
def last_nondigit_index(s):
    """Returns the index of s such that s[i:] is numeric, or None."""
    for i in range(len(s)):
        if s[i:].isdigit():
            return i
    #if we get here, there weren't any trailing digits
    return None

if __name__ == '__main__':
    from sys import argv, exit
    
    if len(argv) < 5:
        print "Syntax: python eutils_beta.py db rettype retmax query."
        exit()
    db = argv[1]
    rettype = argv[2]
    retmax = int(argv[3])
    query = '+'.join(argv[4:]).replace(' ', '+')
    print 'Query: ', query
    g = GenBank(db=db,rettype=rettype,retmax=retmax)
    print g[query].read()
