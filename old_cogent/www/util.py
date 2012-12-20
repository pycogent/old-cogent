#!/usr/bin/env python
#file util.py

"""Public functions to send and receive data from web browsers.

These functions deal with reading fields from FieldStorage objects (the kind
created from form submissions and querystrings), with gzipping data, and with
sending xml to the browser.

Owner: Amanda Birmingham

Revision History:
08/07/03 Amanda Birmingham: created from public functions culled from 
    bayesresults.py and bayesinput.py
08/22/03 Amanda Birmingham: moved file-related functions into filetools.py
10/13/03 Amanda Birmingham: added transformStringWithFile
11/10/03 Amanda Birmingham: added FakeFieldStorage
01/09/04 Amanda Birmingham: added makeXmlTag function
01/20/04 Amanda Birmingham: updated to fit into cvsroot and use packages.
01/25/04 Amanda Birmingham: added forkProcess function
01/27/04 Amanda Birmingham: fixed bug in transformStringWithFile: have to
    use style.saveResultToString, not result_dom.serialize, or else output
    format is lost (you always get xml declaration even for text, html, etc).
"""

from os import environ, close
from random import randrange 
from sys import stdout, exit
from cgi import MiniFieldStorage
from libxml2 import parseFile, parseDoc
from libxslt import parseStylesheetDoc
from gzip import GzipFile
from cStringIO import StringIO

def getField(form_fields, field_name, type_caster = None):
    """Retrieves given field as given type if it exists; else returns None.
    
    form_fields: FieldStorage or FieldStorage-like object containing
        values for form fields sent by user, available by name.
    field_name: name of the field of which to get the value.
    type_caster: a function that turns the field value into the desired type.
    """

    result = None
    try:
        result = form_fields[field_name].value
        if type_caster is not None: result = type_caster(result)
    except:
        pass

    return result
#end function getField

def redirectBrowser(url):
    """Send the browser a page telling it to redirect to the input url.
    
    url: a valid url string.
    """
    
    #write the redirecting header
    stdout.write("Location: " + url + "\n\n")
# end redirectBrowser
    
def sendXmlToBrowser(xml):
    """Wrapper function for sendToBrowser with 'xml' format parameter.
    
    xml: a string of xml.
    
    This function is kept only for compatibility and ease of use; all 
    functionality now resides in the more general sendToBrowser.
    """
    
    sendToBrowser(xml, "xml");
#end function sendXmlToBrowser

def sendToBrowser(content, format):
    """Send content to stdout with format headers, gzipped if browser accepts.
    
    content: a string of content to send to browser.
    format: the format of the content. Should be one of the following strings:
        xml, html, plain
    
    This function sends the input content to the browser (via stdout) with 
    appropriate headers.  It checks whether the requesting browser accepts 
    gzipped content.  If so, it gzips the content before sending and adds 
    headers for the new content encoding.  Also returns the string that was
    sent.
    
    Modified from code described at www.xhaus.com by Alan Kennedy
    """
    
    #write the content type header to the browser
    output = []
    output.append("Content-type: text/" + format + "\n")
    
    #check whether the browser supports gzipped content
    if testAcceptsGzip():
        #gzip the content and write out the extra headers for compressed data
        content = compressData(content)
        output.append("Content-Encoding: gzip\n")
        output.append("Content-Length: %d\n" % (len(content)))
    #end if the browser takes gzipped content
    
    #write out the mandatory separator line and the data
    output.append("\n")
    output.append(content)
    
    result = "".join(output)
    stdout.write(result)
    return result
#end function sendToBrowser

def testAcceptsGzip():
    """Tests if requesting browser accepts gzipped data; returns bool.
    
    Modified from code described at www.xhaus.com by Alan Kennedy    
    """
    #initally, assume gzipping is not allowed
    result = False
    
    try:
        #try to get the accept encoding header that the browser sent to the 
        #environment ... if none are accepted, might not have sent one, I think
        acceptable_encodings = environ["HTTP_ACCEPT_ENCODING"];
        
        #if we found an encodings header, check whether gzip is in it
        if (acceptable_encodings.find("gzip") != -1): result = True
    except: 
        pass
        
    return result
#end function testAcceptsGzip

def compressData(data):
    """Gzip the input data and return compressed data.
    
    data: any data that can be successfully str'd.
    
    Modified from code described at www.xhaus.com by Alan Kennedy
    """
    
    #create a stringio object to use instead of a file in creating a gzipfile
    fake_file = StringIO()
    
    #create the gzipfile obj; mode is write binary
    zip_file = GzipFile(mode = "wb", fileobj = fake_file)
    
    #convert the input data to a string and write into the new gzipfile obj;
    #this compresses the data
    zip_file.write(str(data))
    zip_file.close()
        
    #get the compressed value from the stringio
    result = fake_file.getvalue()
    fake_file.close()
    
    return result
#end compressData function 

def transformStringWithFile(xml_string, xsl_filename):
    """Return result an xsl transform on xml string using named xsl file"""
    
    #read the stylesheet into a stylesheet obj
    styledoc = parseFile(xsl_filename)
    style = parseStylesheetDoc(styledoc)

    #read the xml into a dom and transform it
    doc = parseDoc(xml_string)
    result_dom = style.applyStylesheet(doc, None)
    result = style.saveResultToString(result_dom)

    #free the data structures
    style.freeStylesheet()
    doc.freeDoc()
    result_dom.freeDoc()
    
    #return the result string
    return result
#end transformStringWithFile

class FakeFieldStorage(dict):
    """Object that pretends to be a field storage, for testing web stuff"""

    def __init__(self, test_vals):
        """returns a dictionary that can be used like a fieldstorage
        
        test_vals: a dictionary of form elm value keyed by name, as in: 
            test_vals = {"txtFirstName":"Amanda","txtLastName":"Birmingham"}
        """

        for key,value in test_vals.items():
            self[key] = MiniFieldStorage(key, value)
        #next key and value
    #end __init__
#end FakeFieldStorage

def makeXmlTag(tag_name, value):
    """Return a string holding the value enclosed in the tag"""
    
    xml_pieces = ["<", tag_name, ">", str(value), "</", tag_name, ">"]
    return "".join(xml_pieces)
#end makeXmlTag

def forkProcess(forkable):
    """Fork the current process so that one offspring can
    reply to the browser while the other performs time-consuming
    calculations.
    
    If forking is not possible (code not being run on a unix system),
    then just have the code reply to the browser.
    
    forkable is an object with an updateBrowser property (that returns
    something--html, xml, svg, whatever--to the browser, and a
    calculate property that kicks off whatever the time-consuming 
    calculations are.
    """
    
    try:
        from os import fork 
    except ImportError:
        #if we can't fork, then just assume you're the original process, 
        #which only updates the browser.
        pid = 1;
    else:
        #split into two processes, one of which will talk to the browser
        #and the other of which will perform time-consuming calculations.
        pid = fork()    
    #end try/except/else     

    #check if this is the original or child process
    if pid > 0:
        #return something to the browser
        forkable.updateBrowser()
        stdout.flush()
        exit(0)
    else:
        #if child process, run the actual calculations, but
        #first, close stdout (1) and stderr (2) so that
        #apache releases those file descriptors.  This
        #allows the original process to return info to
        #the browser.
        close(1)
        close(2)
        
        forkable.calculate()
    #end if we're looking at original or child process
#end forkProcess