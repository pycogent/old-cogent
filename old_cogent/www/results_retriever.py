#!/usr/bin/env python
#file results_retriever.py

"""ResultsRetriever class to respond to browser requests for process results.

This module receives form or querystring data from the browser, either 
requesting the status of a submission or the finished
results of a submission.  The module retrieves the appropriate information by
checking the filesystem, formats it as xml, and sends it back to the browser.

Revision History:
01/25/04 Amanda Birmingham: created module by generalizing code from 
    bayesresults.py
"""

from os.path import join, isfile, normpath
from time import strftime
from xml.sax.saxutils import escape
from old_cogent.www.util import sendToBrowser, transformStringWithFile
from old_cogent.format.file import getFileAsString

#--------------------------------------------------------
class ResultsRetriever(object):
    """Object to check for results and send them back to client"""
    
    def __init__(self, form_fields, results_path, return_format):
        """Fill properties from form inputs
        
        form_fields: a FieldStorage or FieldStorage-like object containing
            form inputs
        results_path: the path specifying the directory in which results
            files will be saved
        return_format: the format that the browser should receive (xml,
            html, svg, etc.)        
        """
        
        #store the form fields and get the id of submission
        self._form_fields = form_fields
        self._data_id = form_fields["id"].value
        
        #store the path to the results and return format
        if results_path is not None:
            self._results_path = normpath(str(results_path))
        else:
            self._results_path = None
        #end if 
        self._return_format = str(return_format)
        
        self.WaitStylePath = None
        self.ResultStylePath = None
    #end __init__

    def _get_file_path(self, err_path_needed = False):
        """Determine the complete path to the results file for given id.

        err_path_needed: a boolean value specifying whether to retrieve the
            path to the error file or the results file.  False by default.
        """

        #assume we're looking for a .xml file unless told to use .err one
        file_extension = ".xml";
        if err_path_needed == True: file_extension = ".err"

        #join the data id with the path and extension, then return new path
        if self._results_path is not None:
            result = join(self._results_path, self._data_id)
        else:
            result = self._data_id
        #end if
        
        result += file_extension
        return result
    #end function _get_file_path

    def _build_state_xml(self):
        """Generate xml holding current state of results for input data id.

        This function checks to see whether the submission indicated has 
        finished processing, not finished processing, or errored out.  It 
        creates and returns an xml string indicating the current state.
        """

        #initalize state to be empty--meaning processing not done yet
        state = ""
        stylesheet = ""
        curr_time = strftime("%I:%M:%S %p, %b %d %Y ")
        data_id = self._data_id

        #generate a stylesheet directive if we have a stylesheet path
        if self.WaitStylePath:
            stylesheet = '<?xml-stylesheet href="' + self.WaitStylePath + \
                        '" type="text/xsl"?>'
        #end if there's a defined stylesheet

        #check if the results file or error file exists
        results_filename = self._get_file_path()
        error_filename = self._get_file_path(True)

        #if a results file exists, just say we're done; otherwise, if an 
        #error file exists, insert the error into the state xml
        if isfile(results_filename):
            state = "<done />"
        elif isfile(error_filename):
            #escape error msg (for safe xml)and put in an <error> tag
            state = getFileAsString(error_filename)
            state = "<error>" + escape(state) + "</error>"
        #end if either results or errors exist for this id

        result = \
"""<?xml version="1.0" ?>
%(stylesheet)s
<process>
<id>%(data_id)s</id><time>%(curr_time)s</time>%(state)s
</process>""" % locals()

        return result
    #end function _build_state_xml    
    
    def _build_results_xml(self):
        """Generate XML holding results of submission."""

        #work out the results filename, including path, then get results xml
        results_filename = self._get_file_path()
        result = getFileAsString(results_filename)
        
        return result
    #end _build_results_xml
    
    def _send_to_browser(self, xml, use_result_style = False):
        """Send the input to browser, after transforming if necessary
        
        Also returns the string that is sent to the browser
        """
    
        result = xml
    
        if self._return_format != "xml":
            stylepath = self.WaitStylePath
            if use_result_style: stylepath = self.ResultStylePath
            result = transformStringWithFile(xml, normpath(stylepath))
        #end if checking whether we need to transform

        result = sendToBrowser(result, self._return_format)
        return result
    #end _send_to_browser

    def retrieve(self):
        """Check results; send back if ready, else send wait page.

        form_fields: a FieldStorage or FieldStorage-like object containing 
            querystring or form variables and their values as submitted by 
            the browser.

        Depending on the 'retrieve' value sent by the browser, this function 
        either checks on the status of a given submission and returns the 
        current status or (if retrieve is true) returns the results of a 
        finished submission.
        
        Also returns the value it writes to browser (for testing purposes)
        """
        
        func_dict = {   1:self._build_results_xml, 
                        0:self._build_state_xml}

        #determine whether we are getting results or checking status
        final_results_ready = int(self._form_fields["retrieve"].value)
        
        retrieve_func = func_dict[final_results_ready]
        output = retrieve_func()

        result = self._send_to_browser(output, final_results_ready)
        return result
    #end function retrieve
#end ResultsRetriever class
#--------------------------------------------------------