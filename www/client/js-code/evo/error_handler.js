//----------------------------
//ERRORS & ERRORWRITER OBJECTS
//----------------------------

//******
//create a global errors object & associated variables
var undefined;
var gobjErrors = new Errors();
var gstrModule = "default"; //should be reset by page that uses gobjErrors

//takes in routine name string, action string, and event,
//displays errors in text form.  No return value.
showMainErrors.log = false;
showMainErrors.logFunction = function() {};
showMainErrors.logFunctionOwner = undefined;
function showMainErrors(strRoutine, strAction, e) {
	//add the error we just caught to our errors object
	gobjErrors.add(gstrModule, strRoutine, strAction, e);

	//report what errors we have
	var strErrorOutput = gobjErrors.show(new TextErrorWriter());

	alert(strErrorOutput);

	if (showMainErrors.log) {
		if (showMainErrors.logFunctionOwner != undefined) {
			showMainErrors.logFunction.call(showMainErrors.logFunctionOwner, strErrorOutput);
		} //end if
	} //end if
} //end function showMainErrors
//******


//******
//GLOBAL Variable that is used in OO code; when this is passed as the value of
//the objErrors input (instead of a real object), it means that the object
//is being used for inheritance only so initialization is not necessary.
var gstrPrototype = "prototype";
//******


//******
//THIS CREATES A setErrorsObj() FUNCTION.  IT IS A GENERAL FUNCTION THAT
//IS USED BY A WHOLE PROJECT, AND IS HERE ONLY BECAUSE EVERY PROJECT SHOULD
//BE INCLUDING THIS ERROR-HANDLING MODULE ANYWAY!
//if owner doesn't already have an errors object defined, makes sure that it got
//an errors object, and puts the reference in its local errors property
function setErrorsObj(objOwner, objErrors, strRoutine) {
	//if the object doesn't already have an error property
	if (objOwner.errors == undefined) {
		if (!isInstanceOf(objErrors, Errors)) {throw new Error(strRoutine + "'s call to setErrorsObj did not receive an errors object");}
		objOwner.errors = objErrors;
	} //end if the error property hasn't been set already
} //end function setErrorsObj
//******

//******
//THIS CREATES AN isInstanceOf() FUNCTION.  IT IS A GENERAL FUNCTION THAT
//IS USED BY A WHOLE PROJECT, AND IS HERE ONLY BECAUSE EVERY PROJECT SHOULD
//BE INCLUDING THIS ERROR-HANDLING MODULE ANYWAY!
//This function checks whether the first input is an instance of the constructor
//that is the second input.  It requires that the constructor be defined, but
//not the first input.
function isInstanceOf(varInput, objConstructor) {
	//make sure the constructor is defined
	if (objConstructor == undefined) {throw new Error("isInstanceOf: objConstructor is undefined");}

	//if the input isn't an object or doesn't have the desired constructor, return false
	if ((typeof varInput != "object") || (varInput.constructor != objConstructor)) {
		return false;
	} else { //if it passed the above test, the input is an instance of the constructor, so return true
		return true;
	} //end if
} //end function isInstanceOf
//******


//-------------------------------------
//ERRORS OBJECT
//this class keeps a collection of all the errors that the code has reported,
//in the order in which they were reported
//******
//constructor for the Errors class
function Errors() {
	//array to hold errors object
	this.arrErrors = new Array(); //this should be private, but then prototype functions couldn't reach it ...
} //end constructor Errors

//These statements should be kept WITH the Errors constructor function
//give Errors' prototype some methods
Errors.prototype.show = Errors_show;
Errors.prototype.add = Errors_add;
Errors.prototype.count = Errors_count;
Errors.prototype.clear = Errors_clear;
Errors.prototype.create = Errors_new;
//******

//******
//this function adds a new error to the collection being kept by its parent, the
//Errors object.  It takes in four parameters for: the name of the
//module in which the error is being logged, the name of the function in which the error
//is being logged, a description of the action that was being attempted
//when the error occurred (NOTE TO GOOD PROGRAMMERS: the action string should include
//the inputs to the action!), and an existing error object
function Errors_add(strModule, strRoutine, strAction, objError) {
	try {
		//Extend the message to hold the error type
		objError.message = objError.message + " (" + objError.name + ")";

		//if the severity for this error object is undefined, make it 0
		//for most severe
		if (objError.severity == undefined) {objError.severity = 0;}

		//extend the error object we were given to hold info
		//about the module, routine, and action for which it is being logged
		objError.module = strModule;
		objError.routine = strRoutine;
		objError.action = strAction;

		//push error object onto stack
		this.arrErrors.push(objError);
	} //end try
	catch (e) {alert("Errors_add threw " + e.name + ": " + e.message);}
} //end function Errors_add
//******

//******
//This function creates a new error according to user specifications.
//It is ONLY preferable to "new Error('blah')" WHEN you are making a non-fatal
//error and want to set the severity accordingly.  Don't use it otherwise ...
//it won't hurt anything, but it would be wasteful.
//The new error thas is returned is suitable for throwing :)
//The first parameter contains the message for the error.
//The second parameter should contain an integer defining the severity of the error.
function Errors_new(strMessage, intSeverity) {
	try {
		//local variables
		var objNewError;

		//create new error object
		objNewError = new Error();

		//get the inputs into the new error object
		objNewError.message = strMessage;
		objNewError.severity = intSeverity;

		//return the spanking new error
		return objNewError;
	} //end try
	catch(e)  {alert("Errors_new threw " + e.name + ": " + e.message);}
} //end function Errors_new
//******

//******
//this function gives the user a way to *get at* all the lovely errors they've been
//logging so carefully: it creates an output of the info from all the errors,
//This method uses the GoF "Strategy" pattern: the first argument to the method is
//an object which is a subclass of ErrorWriter and defines one of the ways to output
//the errors.  This object can be different whenever the method is called, and can
//be created in the method call (i.e., "gobjErrors.show(new XmlErrorWriter(), false);").
//The second argument is a boolean, which states whether the Errors object should be cleared
//out after all the errors have been reported. NB: the default is that errors *ARE* cleared.
function Errors_show(objErrorWriter, blnClearErrors) {
	try {
		//local variables
		var intNumErrors, intErrorIndex, objCurError, strOutput;
		var arrLocalErrors = new Array();

		//if no clear errors variable was passed in, make it true
		if (blnClearErrors == undefined) {blnClearErrors = true;}

		//get the number of errors that exist in the array
		//(have to get it now because shifting changes this number!)
		intNumErrors = this.arrErrors.length;

		//for each error obj in errors array
		for (intErrorIndex = 0; intErrorIndex < intNumErrors; intErrorIndex++) {
			//shift the current first error element off errors array
			objCurError = this.arrErrors.shift();

			//tell the ErrorWriter object to write this error
			objErrorWriter.writeError(objCurError);

			//if they don't want the Errors object cleared, push the current error back onto a dummy errors array
			if (!blnClearErrors) {arrLocalErrors.push(objCurError);}
		} //next error object

		//if they don't want the Errors object cleared, reset it to be the dummy one we built up in the loop
		if (!blnClearErrors) {this.arrErrors = arrLocalErrors;}

		//return the ErrorWriter's total writeup of the errors
		return objErrorWriter.writeErrors();
	} //end try
	catch (e) {alert("Errors_show threw " + e.name + ": " + e.message);}
} //end function Errors_show
//******

//******
//This function simply returns how many errors *CURRENTLY EXIST* in the Errors object's
//collection.  Sure, you could get this yourself by looking at the array, but that would
//be naughty because it is supposed to be private!
//Note that if someone cleared the errors, either explicitly or by using showErrors in a
//way that cleared them, this will give zero even though errors *used* to be there.
function Errors_count () {
	return this.arrErrors.length;
} //end function Errors_count
//******

//******
//This function just reinitializes the Errors object's collection.  Again, you could do it
//yourself, but that would be messing with private properties, so don't.
function Errors_clear() {
	this.arrErrors = new Array();
} //end function Errors_clear
//******
//-------------------------------------


//-------------------------------------
//ERRORWRITER OBJECT
//ErrorWriter is an abstract class which defines algorithms that
//can be passed to the Errors object's show method.  Note that this
//whole function is commented out because it is *abstract*, and doesn't
//contain any actual implementations of its methods; it is just
//here as a guide to what methods an ErrorWriter must expose.
/*
function ErrorWriter() {
	this.writeError = writeError;
	this.writeErrors = writeErrors; //must return a value (which will be the return value of the show method)
} //end constructor ErrorWriter
*/

//******
//constructor for the XmlErrorWriter.  This is a subclass of the abstract class ErrorWriter,
//and defines an algorithm and variables for writing out errors as xml.
//The method writeErrors returns xml of the errors shown in the order the errors occurred.
function XmlErrorWriter() {
	//note that this is "output", not "this.output" .. that means it is private.
	//inline functions can access it, but not outside ones :)
	var strOutput = "";

	//methods
	this.writeError = function (objCurError) {
							//turn input into xml and add to output
							strOutput = strOutput +
										'<error>' +
										'<module>' + objCurError.module + '</module>' +
										'<routine>' + objCurError.routine + '</routine>' +
										'<action>' + objCurError.action + '</action>' +
										'<message>' + objCurError.message + '</message>' +
										'<severity>' + objCurError.severity + '</severity>' +
										'</error>';
						}; //end inline function writeError

	this.writeErrors = function () {
							//tack the beginning and ending xml onto the errors xml we've built up
							strOutput = '<?xml version="1.0" ?><errors>' + strOutput + '</errors>';
							return strOutput;
						}; //end inline function writeErrors
} //end constructor XmlErrorWriter
//******

//******
//constructor for the TextErrorWriter.  This is a subclass of the abstract class ErrorWriter,
//and defines an algorithm and variables for writing out errors as text.
//The method writeErrors returns text of the errors shown in the order the errors occurred.
function TextErrorWriter() {
	//note that this is "output", not "this.output" .. that means it is private.
	//inline functions can access it, but not outside ones :)
	var strOutput = "";

	//methods
	this.writeError = function (objCurError) {
							//turn input into xml and add to output
							strOutput = strOutput +
										objCurError.module + '->' +
										objCurError.routine + '->' +
										objCurError.action + ': ' +
										objCurError.message +
										' (severity ' + objCurError.severity + ')\n';
						}; //end inline function writeError

	this.writeErrors = function () {
							return strOutput;
						}; //end inline function writeErrors
} //end constructor TextErrorWriter
//******
//-------------------------------------