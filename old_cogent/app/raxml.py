#!/usr/bin/env python
# raxml.py
"""Application controller for RAxML-V (v2.2) 

Owner: Micah Hamady (hamady@colorado.edu)
Status: Prototype - DO NOT USE YET

Revision History:
Initial Prototype: 10/14/2005 Micah Hamady
1/30/06: Cathy Lozupone: changes name of getPhylipString to toPhylip
"""
from old_cogent.app.parameters import FlagParameter, ValuedParameter
from old_cogent.app.util import CommandLineApplication, ResultPath
from random import choice
from os import walk
from old_cogent.parse.tree import DndParser

class Raxml(CommandLineApplication):
    """RAxML application controller"""

    _options ={

        # Specify a column weight file name to assign individual wieghts to 
        # each column of the alignment. Those weights must be integers 
        # separated by any number and type of whitespaces whithin a separate 
        # file, see file "example_weights" for an example.
        '-a':ValuedParameter('-',Name='a',Delimiter=' '),

        #  Specify an integer number (random seed) for bootstrapping
        '-b':ValuedParameter('-',Name='b',Delimiter=' '),


        # Specify number of distinct rate catgories for raxml when 
        # ModelOfEvolution is set to GTRCAT or HKY85CAT.
        # Individual per-site rates are categorized into numberOfCategories 
        # rate categories to accelerate computations. (Default = 50)
        '-c':ValuedParameter('-',Name='c',Delimiter=' ', Value=50),


        # select search algorithm: 
        #   c for normal hill-climbing search (Default)
        #     when -f option is omitted this algorithm will be used
        #   e (evaluate) to optimize model+branch lengths for given input tree
        #   f (fast) for fast-less exhaustive hill climbing search
        #   s (simulated annealing) for simulated annealing search
        '-f':ValuedParameter('-',Name='f',Delimiter=' ', Value="c"),

        # specify integer time limit in seconds, program will abort after 
        # approximately timeLimit seconds if in normal hill-climbing or 
        # simulated annealing mode
        '-l':ValuedParameter('-',Name='l',Delimiter=' '),

        # SIMULATED ANNEALING MODE ONLY!!! specify integer number of moves 
        # after which temperature is lowered 
        # (Default == number of taxa in alignment)
        '-g':ValuedParameter('-',Name='g',Delimiter=' '),

        # SIMULATED ANNEALING MODE ONLY!!! specify integer start temperature 
        # for chain (Default = 3.0)
        '-d':ValuedParameter('-',Name='d',Delimiter=' '),

        # Specifies the name of the output file.
        '-n':ValuedParameter('-',Name='n',Delimiter=' '),

        # Name of the working directory where RAxML-V will write its output 
        # files.
        '-w':ValuedParameter('-',Name='w',Delimiter=' '),

        # Minimum rearrangment setting. (Default = 5)
        '-r':ValuedParameter('-',Name='r',Delimiter=' '),

        # Maximum rearrangement setting. (Default = 21)
        '-k':ValuedParameter('-',Name='k',Delimiter=' '),

        # Specify a user starting tree file name in Newick format
        '-t':ValuedParameter('-',Name='t',Delimiter=' '),

        # Initial rearrangement setting for the subsequent application of 
        # topological changes phase
        '-i':ValuedParameter('-',Name='i',Delimiter=' '),

        # specify the name of the alignment data file
        '-s':ValuedParameter('-',Name='s',Delimiter=' '),

        # Model of Nucleotide Substitution:
        # -m HKY85: HKY85 + Optimization of Tr/Tv ratio
        # -m HKY85CAT: HKY85 + Optimization of Tr/Tv ratio + Optimization of 
        #    site-specific evolutionary rates which are categorized into 
        #    numberOfCategories distinct rate categories for greater 
        #    computational efficiency
        # -m GTR: GTR + Optimization of substitution rates
        # -m GTRCAT: GTR + Optimization of substitution rates +  Optimization 
        #    of site-specific evolutionary rates which are categorized into 
        #    numberOfCategories distinct rate categories for greater 
        #    computational efficiency
        
        # Amino Acid Models
		# -m JTT: JTT model of amino acid substitution
		# -m JTTCAT: JTT model of amino acid substitution + Optimization of site-specific
		#   evolutionary rates which are categorized into numberOfCategories distinct 
		#   rate categories for greater computational efficiency
		# -m PAM: PAM model of amino acid substitution
		# -m PAMCAT: PAM model of amino acid substitution + Optimization of site-specific
		#   evolutionary rates which are categorized into numberOfCategories distinct 
		#   rate categories for greater computational efficiency
		# -m PMB: PMB model of amino acid substitution
		# -m PMBCAT: PMB model of amino acid substitution + Optimization of site-specific
		#   evolutionary rates which are categorized into numberOfCategories distinct 
		#   rate categories for greater computational efficiency

        '-m':ValuedParameter('-',Name='m',Delimiter=' '),

    }

    _parameters = {}
    _parameters.update(_options)
    _command = "raxml"
    _out_format = "RAxML_%s.%s"

    #def _input_as_seqs(self,data):
    #    lines = []
    #    for i,s in enumerate(data):
    #        #will number the sequences 1,2,3,etc.
    #        lines.append(''.join(['>',str(i+1)]))
    #        lines.append(s)
    #    return self._input_as_lines(lines)

    #def _input_as_lines(self,data):
    #    if data:
    #        self.Parameters['-s']\
    #            .on(super(Raxml,self)._input_as_lines(data))
    #    return ''

    #def _input_as_string(self,data):
    #    """Makes data the value of a specific parameter
    # 
    #    This method returns the empty string. The parameter will be printed
    #    automatically once set.
    #    """
    #    if data:
    #        self.Parameters['-in'].on(str(data))
    #    return ''

    def _input_as_multiline_string(self, data):
        if data:
            self.Parameters['-s']\
                .on(super(Raxml,self)._input_as_multiline_string(data))
        return ''

   
    def _absolute(self,path):
        if path.startswith('/'):
            return path
        elif self.Parameters['-w'].isOn():
            return self.Parameters['-w'].Value + path
        else:
            return self.WorkingDir + path

    def _log_out_filename(self):
        if self.Parameters['-n'].isOn():
            out_filename = self._absolute(
                   self._out_format % ("log", str(self.Parameters['-n'].Value)))
        else:
            raise ValueError, "No output file specified." 
        return out_filename

    def _info_out_filename(self):
        if self.Parameters['-n'].isOn():
            out_filename = self._absolute(
                   self._out_format % ("info",
                                        str(self.Parameters['-n'].Value)))
        else:
            raise ValueError, "No output file specified." 
        return out_filename

    def _parsimony_tree_out_filename(self):
        if self.Parameters['-n'].isOn():
            out_filename = self._absolute(
                   self._out_format % ("parsimonyTree",
                                        str(self.Parameters['-n'].Value)))
        else:
            raise ValueError, "No output file specified." 
        return out_filename

    def _result_tree_out_filename(self):
        if self.Parameters['-n'].isOn():
            out_filename = self._absolute(
                   self._out_format % ("result",
                                        str(self.Parameters['-n'].Value)))
        else:
            raise ValueError, "No output file specified." 
        return out_filename


    def _checkpoint_out_filenames(self):
        """
        RAxML generates a crapload of checkpoint files so need to
        walk directory to collect names of all of them.
        """
        out_filenames = []
        if self.Parameters['-n'].isOn():
            out_name = str(self.Parameters['-n'].Value)
            walk_root = self.WorkingDir
            if self.Parameters['-w'].isOn(): 
                walk_root = str(self.Parameters['-w'].Value)
            for tup in walk(walk_root):
                dpath, dnames, dfiles = tup
                if dpath == walk_root:
                    for gen_file in dfiles:
                        if out_name in gen_file and "checkpoint" in gen_file:
                            out_filenames.append(walk_root + gen_file)
                    break

        else:
            raise ValueError, "No output file specified." 
        return out_filenames

    def _get_result_paths(self,data):
        
        result = {}
        result['Log'] = ResultPath(Path=self._log_out_filename(),
                                            IsWritten=True)
        result['Info'] = ResultPath(Path=self._info_out_filename(),
                                            IsWritten=True)
        result['ParsimonyTree'] = ResultPath(
                        Path=self._parsimony_tree_out_filename(),
                        IsWritten=True)
        result['Result'] = ResultPath(
                        Path=self._result_tree_out_filename(),
                        IsWritten=True)
        for checkpoint_file in self._checkpoint_out_filenames():
            checkpoint_num = checkpoint_file.split(".")[-1]
            try:
                checkpoint_num = int(checkpoint_num)
            except Exception, e:
                raise ValueError, "%s does not appear to be a valid checkpoint file"
            result['Checkpoint%d' % checkpoint_num] = ResultPath(
                        Path=checkpoint_file,
                        IsWritten=True)
 
        return result


#SOME FUNCTIONS TO EXECUTE THE MOST COMMON TASKS
def raxml_alignment(align_obj,
                 params={},
                 SuppressStderr=True,
                 SuppressStdout=True):
    """Run raxml on alignment object 

    align_obj: Alignment object
    params: you can set any params except -w and -n

    returns: tuple (phylonode, 
                    parsimonyphylonode, 
                    log likelihood, 
                    total exec time)
    """

    # generate temp filename for output
    params["-w"] = "/tmp/"
    params["-n"] = get_tmp_filename()
    ih = '_input_as_multiline_string'
    seqs, align_map = align_obj.toPhylip()

    # set up command
    raxml_app = Raxml(
                   params=params,
                   InputHandler=ih,
                   WorkingDir=None,
                   SuppressStderr=SuppressStderr,
                   SuppressStdout=SuppressStdout)

    # run raxml
    ra = raxml_app(seqs)

    # generate tree
    tree_node =  DndParser(ra["Result"])

    # generate parsimony tree
    parsimony_tree_node =  DndParser(ra["ParsimonyTree"])

    # extract log likelihood from log file
    log_file = ra["Log"]
    total_exec_time = exec_time = log_likelihood = checkpoint_num = 0.0
    for line in log_file:
        exec_time, log_likelihood, checkpoint_num = map(float, line.split())
        total_exec_time += exec_time

    # remove output files
    ra.cleanUp()

    return tree_node, parsimony_tree_node, log_likelihood, total_exec_time

def get_tmp_filename(tmp_dir=""):
    # temp hack - change this to lookup and generate file in class
    chars = "abcdefghigklmnopqrstuvwxyz"
    all_chars = chars + chars.upper() + "0123456790"
    picks = list(all_chars)
    if tmp_dir:
        tmp_dir = tmp_dir + "/"

    return tmp_dir + "tmp%s.txt" % ''.join([choice(picks) for i in range(10)]) 


