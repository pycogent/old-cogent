#!/usr/bin/env python
# parameters.py

"""
Provides Parameter, FlagParameter, ValuedParameter, MixedParameter,
Parameters.  These are intended to be used with the Application class and
its subclasses

Owner: Sandra Smit (sandra.smit@colorado.edu) and 
    Greg Caporaso (caporaso@colorado.edu)

Status: Development

Revision history:
6/8-14/04: Written by Sandra Smit and Greg Caporaso, all tests pass
7/29/04 Sandra Smit: added all_off() to Parameters

"""
from old_cogent.util.misc import MappedDict, FunctionWrapper
from copy import deepcopy

def is_not_None(x):
    """Returns True if x is not None"""
    return x is not None

class ParameterError(ValueError):
    """Error raised when field in parameter is bad"""
    pass

class Parameter(object):
    """Stores information regarding a parameter to an application.
    
        An abstract class.
    """

    def __init__(self,Prefix,Name,Value=None,Delimiter=None,Quote=None):
        """Initialize the Parameter object.
        
        Prefix: the character(s) preceding the name of the parameter
            (eg. '-' for a '-a' parameter)       
        Name: the name of the parameter (eg. 'a' for a '-a' parameter)
        Value: the value of the parameter (eg. '9' in a '-t=9' parameter)
            The value is also used in subclasses to turn parameters on and off
        Delimiter: the character separating the identifier and the value, 
            (eg. '=' for a '-t=9' command or ' ' for a '-t 9' parameter) 
        Quote: the character to use when quoting the value (eg. "\"" for
            a '-l="hello" parameter). At this point asymmetrical quotes 
            are not possible (ie. [4]) 
            WARNING: You must escape the quote in most cases.     
                
        Id: The combination of Prefix and Name is called the identifier (Id)
            of the parameter. (eg. '-a' for a '-a' parameter, or '-t' for 
            a '-t=9' parameter)

        This is intended to be an abstract class and has no use otherwise.
        To subclass Parameter, the subclass should implement the 
        following methods:
            __str__(): returns the parameter as a string when turned on,
                or as an empty string when turned off
            on(): turns the parameter on
            isOn(): return True if a parameter is on, otherwise False
            off(): turns the parameter off
            isOff(): return True if a parameter is off, otherwise False

        Whether a parameter is on or off can be specified in different
        ways in subclasses, your isOn() and isOff() methods should define
        this.

        Optionally you can overwrite __init__, but you should be sure to 
        either call the superclass init or handle the setting of the
        self._default attribute (or things will break!)
        """
        self.Name = Name
        self.Prefix = Prefix
        self.Delimiter = Delimiter
        self.Quote = Quote
        self.Value = Value
    
    def _get_id(self):
        """Construct and return the identifier"""
        return ''.join(map(str,filter(is_not_None,[self.Prefix,self.Name])))

    Id = property(_get_id)

    def __eq__(self,other):
        """Return True if two parameters are equal"""
        return (self.Name == other.Name) and\
                (self.Prefix == other.Prefix) and\
                (self.Delimiter == other.Delimiter) and \
                (self.Quote == other.Quote) and \
                (self.Value == other.Value) 

    def __ne__(self,other):
        """Return True if two parameters are not equal to each other"""
        return not self == other
         

class FlagParameter(Parameter):
    """Stores information regarding a flag parameter to an application"""

    def __init__(self,Prefix,Name,Value=False):
        """Initialize a FlagParameter object

        Prefix: the character(s) preceding the name of the parameter
            (eg. '-' for a '-a' parameter)       
        Name: the name of the parameter (eg. 'a' for a '-a' parameter)        
        Value: determines whether the flag is turned on or not;
            should be True to turn on, or False to turn off, 
            False by default
        
        Id: The combination of Prefix and Name is called the identifier (Id)
            of the parameter. (eg. '-a' for a '-a' parameter, or '-t' for 
            a '-t=9' parameter)
   
        Usage: 
            f = FlagParameter(Prefix='-',Name='a')
            Parameter f is turned off by default, so it won't be used by
            the application until turned on.
            
        or  f = FlagParameter(Prefix='+',Name='d',Value=True)
            Parameter f is turned on. It will be used by the application.
        """
        super(FlagParameter,self).__init__(Name=Name,Prefix=Prefix,\
                Value=Value,Delimiter=None,Quote=None)

    def __str__(self):
        """Return the parameter as a string.
        
        When turned on: string representation of the parameter
        When turned off: empty string
        """
        if self.isOff():
            return ''
        else:
            return ''.join(map(str,[self.Prefix,self.Name]))

    def isOn(self):
        """Returns True if the FlagParameter is turned on.
        
        A FlagParameter is turned on if its Value is True or evaluates to True.
        A FlagParameter is turned off if its Value is False or evaluates
            to False.
        """
        if self.Value:
            return True
        return False

    def isOff(self):
        """Returns True if the parameter is turned off
        
        A FlagParameter is turned on if its Value is True or evaluates to True.
        A FlagParameter is turned off if its Value is False or evaluates
            to False.
        """
        return not self.isOn()

    def on(self):
        """Turns the FlagParameter ON by setting its Value to True"""
        self.Value = True

    def off(self):
        """Turns the FlagParameter OFF by setting its Value to False"""
        self.Value = False

class ValuedParameter(Parameter):
    """Stores information regarding a valued parameter to an application"""

    def __init__(self,Prefix,Name,Value=None,Delimiter=None,Quote=None):
        """Initialize a ValuedParameter object.
        
        Prefix: the character(s) preceding the name of the parameter
            (eg. '-' for a '-a' parameter)       
        Name: the name of the parameter (eg. 'a' for a '-a' parameter)
        Value: the value of the parameter (eg. '9' in a '-t=9' parameter)
        Delimiter: the character separating the identifier and the value, 
            (eg. '=' for a '-t=9' command or ' ' for a '-t 9' parameter) 
        Quote: the character to use when quoting the value (eg. "\"" for
            a '-l="hello" parameter). At this point asymmetrical quotes 
            are not possible (ie. [4]) 
            WARNING: You must escape the quote in most cases.     
        
        Id: The combination of Prefix and Name is called the identifier (Id)
            of the parameter. (eg. '-a' for a '-a' parameter, or '-t' for 
            a '-t=9' parameter)
        Default: the default value of the parameter; this is defined as
            what is passed into init for Value and can not be changed 
            after object initialization
                
        Usage:
            v = ValuedParameter(Prefix='-',Name='a',Delimiter=' ',Value=3)
            the parameter is turned on by default (value=3) and will be 
            used by the application as '-a 3'.
        or  v = ValuedParameter(Prefix='-',Name='d',Delimiter='=')
            the parameter is turned off by default and won't be used by
            the application unless turned on with some value.
        """
        super(ValuedParameter,self).__init__(Name=Name,Prefix=Prefix,\
                Value=Value,Delimiter=Delimiter,Quote=Quote)
        self._default = Value

    def __str__(self):
        """Return the parameter as a string
        
        When turned on: string representation of the parameter
        When turned off: empty string
        """
        if self.isOff():
            return ''
        else:
            parts = [self.Prefix,self.Name,self.Delimiter,\
                self.Quote,self.Value,self.Quote]
            return ''.join(map(str,filter(is_not_None,parts)))
    
    def __eq__(self,other):
        """Return True if two parameters are equal"""
        return (self.Name == other.Name) and\
                (self.Prefix == other.Prefix) and\
                (self.Delimiter == other.Delimiter) and \
                (self.Quote == other.Quote) and \
                (self.Value == other.Value) and\
                (self._default == other._default)

    def _get_default(self):
        """Get the default value of the ValuedParameter
        
        Accessed as a property to avoid the user changing this
            after initialization.
        """
        return self._default
    
    Default = property(_get_default)
    
    def reset(self):
        """Reset Value of the ValuedParameter to the default"""
        self.Value = self._default

    def isOn(self):
        """Returns True if the ValuedParameter is turned on
        
        A ValuedParameter is turned on if its Value is not None.
        A ValuedParameter is turned off if its Value is None.
        """
        if self.Value is not None:
            return True
        return False

    def isOff(self):
        """Returns True if the ValuedParameter is turned off 
        
        A ValuedParameter is turned on if its Value is not None.
        A ValuedParameter is turned off if its Value is None.
        """
        return not self.isOn()

    def on(self,val):
        """Turns the ValuedParameter ON by setting its Value to val
        
        An attempt to turn the parameter on with value 'None' will result
            in an error, since this is the same as turning the parameter off.
        """
        if val is None:
            raise ParameterError,\
            "Turning the ValuedParameter on with value None is the same as "+\
            "turning it off. Use another value."
        else:
            self.Value = val

    def off(self):
        """Turns the ValuedParameter OFF by setting its Value to None"""
        self.Value = None

class MixedParameter(ValuedParameter):
    """Stores information regarding a mixed parameter to an application
    
    A mixed parameter is a mix between a FlagParameter and a ValuedParameter.
    When its Value is False, the parameter will be turned off.
    When its Value is set to None, the parameter will behave like a flag.
    When its Value is set to anything but None or False, it will behave
        like a ValuedParameter.

    Example: RNAfold [-d[0|1]] 
    You can give either '-d' or '-d0' or '-d1' as input.
    """

    def __init__(self,Prefix,Name,Value=False,Delimiter=None,Quote=None):
        """Initialize a MixedParameter object
        
        Prefix: the character(s) preceding the name of the parameter
        (eg. '-' for a '-a' parameter)       
        Name: the name of the parameter (eg. 'a' for a '-a' parameter)
        Value: the value of the parameter (eg. '9' in a '-t=9' parameter)
        Delimiter: the character separating the identifier and the value, 
            (eg. '=' for a '-t=9' command or ' ' for a '-t 9' parameter) 
        Quote: the character to use when quoting the value (eg. "\"" for
            a '-l="hello" parameter). At this point asymmetrical quotes 
            are not possible (ie. [4]) 
            WARNING: You must escape the quote in most cases.     
        
        Id: The combination of Prefix and Name is called the identifier (Id)
            of the parameter. (eg. '-a' for a '-a' parameter, or '-t' for 
            a '-t=9' parameter)
        Default: the default value of the parameter; this is defined as
            what is passed into init for Value and can not be changed 
            after object initialization
                
        Usage:
            m = MixedParameter(Prefix='-',Name='a',Delimiter=' ',Value=3)
            the parameter is turned on by default (value=3) and will be 
            used by the application as '-a 3'.
        or  m = MixedParameter(Prefix='-',Name='d',Delimiter='=',Value=None)
            the parameter is turned on by default as a flag parameter and 
            will be used by the application as '-d'.
        or  m = MixedParameter(Prefix='-',Name='d',Delimiter='=')
            the parameter is turned off by default (Value=False) and won't be
            used by the application unless turned on with some value.
        """
        super(MixedParameter,self).__init__(Name=Name,Prefix=Prefix,\
                Value=Value,Delimiter=Delimiter,Quote=Quote)

    def __str__(self):
        """Return the parameter as a string
        
        When turned on: string representation of the parameter
        When turned off: empty string
        """
        if self.isOff():
            return ''
        elif self.Value is None:
            return ''.join(map(str,[self.Prefix,self.Name]))
        else:
            parts = [self.Prefix,self.Name,self.Delimiter,\
                self.Quote,self.Value,self.Quote]
            return ''.join(map(str,filter(is_not_None,parts)))

    def isOn(self):
        """Returns True if the MixedParameter is turned on
        
        A MixedParameter is turned on if its Value is not False.
        A MixedParameter is turned off if its Value is False.
        
        A MixedParameter is used as flag when its Value is None.
        A MixedParameter is used as ValuedParameter when its Value is
            anything but None or False.
        """
        if self.Value is not False:
            return True
        return False

    def isOff(self):
        """Returns True if the MixedParameter is turned off
        
        A MixedParameter is turned on if its Value is not False.
        A MixedParameter is turned off if its Value is False.
        """
        return not self.isOn()

    def on(self,val=None):
        """Turns the MixedParameter ON by setting its Value to val
        
        An attempt to turn the parameter on with value 'False' will result
            in an error, since this is the same as turning the parameter off.
        
        Turning the MixedParameter ON without a value or with value 'None'
            will let the parameter behave as a flag.
        """
        if val is False:
            raise ParameterError,\
            "Turning the ValuedParameter on with value False is the same as "+\
            "turning it off. Use another value."
        else:
            self.Value = val

    def off(self):
        """Turns the MixedParameter OFF by setting its Value to False"""
        self.Value = False

def _find_synonym(synonyms):
    """ Returns function to lookup a key in synonyms dictionary.
        
        Inteded for use by the Parameters object.
    """
    def check_key(key):
        if key in synonyms:
            return synonyms[key]
        return key
    return check_key

class Parameters(MappedDict):
    """Parameters is a dictionary of Parameter objects.
    
    Parameters provides a mask that lets the user lookup and access parameters
        by its synonyms.
    """
   
    def __init__(self,parameters={},synonyms={}):
        """Initialize the Parameters object.

        parameters: a dictionary of Parameter objects keyed by their identifier
        synonyms: a dictionary of synonyms. Keys are synonyms, values are
            parameter identifiers.
        """
        mask = FunctionWrapper(_find_synonym(synonyms))
        super(Parameters,self).__init__(data=deepcopy(parameters),Mask=mask)
        
        self.__setitem__ = self.setdefault = self.update =\
            self.__delitem__ = self._raiseNotImplemented

    def _raiseNotImplemented(self,*args):
        """Raises an error for an attempt to change a Parameters object"""
        raise NotImplementedError, 'Parameters object is immutable'

    def all_off(self):
        """Turns all parameters in the dictionary off"""
        for v in self.values():
            v.off()
