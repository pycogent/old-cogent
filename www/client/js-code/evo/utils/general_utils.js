/*
general_utils.js

Functions and extension methods of general use in js programming.

Revision History:
Written 2002 by Amanda Birmingham
10/25/03 Amanda Birmingham: branched from BayesFold 1.0 version and renamed
*/

//******
//The UniqueId function returns ... umm ... a unique id.  In the form of an integer.
//Design taken from Functions chapter of Flanagan's Definitive Guide.  Ids are unique
//WITHIN a run.
UniqueId.counter = 0;

function UniqueId() {
	//increment and return the static variable
	return UniqueId.counter++;
} //end function UniqueId
//******

//******
//NOTE:
//numTest, isInteger, and isPosInteger have been moved into iNumericValidations.js (02/05/03)
//******

//******
//THIS FUNCTION IS DEPRECATED: replace by 'this.propertyX = strInput || "" '
//if the input to to this function is undef, it returns an empty string.
//otherwise, it returns the originalinput.
/*
function undefToEmptyString(strInput) {
	var undef;
	if (strInput == undef) {strInput = "";}
	return strInput;
} //end function undefToEmptyString
*/
//******

//******
//THIS FUNCTION IS DEPRECATED: replace by 'this.propertyX = strInput || 0 '!
//if the input to to this function is undef, it returns zero.
//otherwise, it returns the originalinput.
/*
function undefToZero(strInput) {
	var undef;
	if (strInput == undef) {strInput = 0;}
	return strInput;
} //end function undefToEmptyString
*/
//******

//******
//culled from iBlowBubbles.js
function genericSet(arrProperties, arrInputs) {
	for (var i=0; i<arrProperties.length; i++) {
		if (i<arrInputs.length) {
			eval("if (!isNaN(parseInt(" + arrInputs[i] + "))) {this." + arrProperties[i] + " = parseInt(" + arrInputs[i] + ");}");
		} //end if we haven't run out of input yet
	} //next property to fill
} //end function genericSet

/*
//Example of how to use genericSet:
function setTime(intTimeMin, intTimeMax) {
	var arrProperties = new Array('tmin', 'tmax');
	this.genericSet(arrProperties, arguments);
} //end method setTime
*/
//******

//******
//function to create a string that spells out "arguments[n], arguments[n+1], ..."
//starting at an arbitrary n.  To be used when passing inputs through to another
//function (as in calling OO init functions). Takes in the number of arguments in
//the arguments array and the number at which the string should start.  NB: this
//doesn't do ANYTHING with the actual arguments!
//Optional third argument gives the name of an array other than 'arguments' to
//be used instead; if this is not there, defaults to 'arguments'
//returns the string with a ", " at the beginning because this is how I generally
//want to use it; if last option is true, cuts this off.
function writeArgString(intArgArrayLength, intStartIndex, strArrayName, blnNoComma) {
	//local variable
	var strArguments = "";

	//check if it arraylength is a nonnegative integer?
	//if the start index is undefined, make it zero
	if (intStartIndex == undefined) {intStartIndex = 0;}
	//check if startIndex is a nonnegative integer?

	//check if the arrayname was passed in, and make it 'arguments' if it wasn't
	if (strArrayName == undefined) {strArrayName = "arguments";}

	if (blnNoComma == undefined) {blnNoComma = false;}

	//loop from intStartIndex to intArgArrayLength and build up the string referring to the arguments
	for (var intArgIndex = intStartIndex; intArgIndex < intArgArrayLength; intArgIndex++) {
			strArguments = strArguments + ", " + strArrayName + "[" + intArgIndex + "]";
	} //next arg index

	//if the user doesn't want a ", " at the beginning of the string, cut it off
	if (blnNoComma) {strArguments = strArguments.substring(2, strArguments.length);}

	return strArguments;
} //end function writeArgString
//******


//******
//culled from SequenceDefs.js
//function checks to make sure an input object has as its constructor the
//required objInputConstructor.  By default, function will allow any object
//that is a subclass of the necessary constructor, although this behavior
//can be turned off by setting the optional third argument to false.
//Assuming the object passed the test, it is returned unchanged.  If the
//object DIDN'T pass the test, an error is thrown.
function confirmObjType(objInput, objInputConstructor, blnAllowSubclasses) {
	//if we didn't get a value for blnAllowSubclasses, make it true
	if (blnAllowSubclasses == undefined) {blnAllowSubclasses = true;}

	//checking input object to make sure it is a objInputConstructor
	if (!isInstanceOf(objInput, objInputConstructor)) {
		//it isn't an instance of the constructor.
		//This switch statement PURPOSELY allows fallthrough: it only breaks out if
		//we are allowing subclasses AND this object is a subclass of the constructor.
		//Otherwise, it falls through to give the "not correct object type" error.
		switch(blnAllowSubclasses) {
			case true:
				//if it is a subclass of the constructor
				if (objInputConstructor.prototype.isPrototypeOf(objInput)) {break;}
				//This switch statement PURPOSELY allows fallthrough
			case false:
				throw new Error("input is not of correct object type");
		} //end switch
	} //end if input object is not one of constructor

	//return input object unchanged
	return objInput;
} //end function confirmObjType
//******

//******
//this function wraps confirmObjType.  It is for use in those situations
//where you just want a true/false answer about whether an object is of
//a given type, rather than having an error thrown when it isn't.  Takes
//exactly the same arguments as confirmObjType, returns true or false.
function checkObjType(objInput, objInputConstructor, blnAllowSubclasses) {
	try {
		//call confirmObjType
		confirmObjType(objInput, objInputConstructor, blnAllowSubclasses);

		//if we didn't get an error in that last call, return true
		return true;
	} //end try
	catch(e) {
		//if we got an error, it means confirmObjType failed (wasn't really an obj of that type), so
		return false;
	} //end catch
} //end function checkObjType
//******

//******
//for use with OO structures.  Lets the aggregated (owned) object
//know who owns it (always set as "owner" property).
function aggregate(objOwnee, objOwner) {
	//put the owner object into the owner
	//property of the ownee; then return the ownee
	objOwnee.owner = objOwner;
	return objOwnee;
} //end function aggregate
//******

//******
//for use with OO structures when association knowledge flows both directions.
//lets associated object know who it is associated with via the appropriate
//property.  No point to using this function for unidirectional associations...
//just use a regular assignment statement.
function associate(objAssociated, objAssociate, strReverseProperty) {
	//if this association is known in both directions
	//put the objAssociate object into the reverse property.
	//then return objAssociated.
	if (strReverseProperty != undefined) {eval("objAssociated." + strReverseProperty + " = objAssociate;");}
	return objAssociated;
} //end function associate
//******

//******
//function to clone javascript objects, since simple copying doesn't work on references.
//optional second argument tells whether to copy any child properties which are objects
//(as long as those objects do not have constructors listed in the noCloneObjs array).
//default is false--children are not cloned.  Function returns the clone.
cloneObject.noCloneObjs = new Array(undefined, String, Boolean, Number, Function);

function cloneObject(objInput, blnCopyChildren) {
	//find out the constructor of the object, and determine whether to clone children
	if (objInput.constructor == undefined) {throw new Error("objectClone input is not an object");}
	if (blnCopyChildren == undefined) {blnCopyChildren = false;}

	//make another one of it
	var objReturn = new objInput.constructor();

	//go through all the input object's properties
	for (var aProperty in objInput) {
		//assume property holds a value, not an object
		var newProperty = objInput[aProperty];

		//if the property is an object but not a function, you'll have to clone that too ...
		if (blnCopyChildren) {
			//check on the constructor
			var blnDoClone = true;
			var curConstructor = objInput[aProperty].constructor;
			for (var intNoCloneIndex = 0; intNoCloneIndex < cloneObject.noCloneObjs.length; intNoCloneIndex++) {
				if (curConstructor == cloneObject.noCloneObjs[intNoCloneIndex]) {
					blnDoClone = false;
					break;
				} //end if
			} //next noCloneObj constructor

			if (blnDoClone) {newProperty = cloneObject(objInput[aProperty], blnCopyChildren);}
		} //end if we're supposed to make copies of object children

		//set properties in the new object equal to these
		objReturn[aProperty] = newProperty;
	} //next property

	//return the clone
	return objReturn;
} //end function cloneObject
//******

//******
//function to set up an array that indicates multiple superclasses that a class belongs to,
//to simulate multiple inheritance.  NB: the flaw in this method of simulating multiple
//inheritance is that if more secondary superclasses are added to a parent in run-time,
//the children that have already been created will NOT know about them.  However, changing
//the inheritance at runtime seems a little dodgy anyway, so I'm not too sad about that.
//First argument should be the string name of the property where secondary superclasses
//would be stored if we had inherited any of them (not including the "this." part) ... ie,
//if they'd be stored in an array named "secondarySuperclasses" in our parent, pass in
//"secondarySuperclasses".  After that, takes in an arbitrary number of arguments where the
//arguments are string representations of constructor function names (ie, "String" if String
//is the constructor object).  Returns an array that will be the new secondarySuperclasses
//array for the object we're setting multiple inheritance on.
function multipleInherit(strSecSupArrayname) {
	//local variables
	var arrReturn, arrInheritedSuperclasses;

	//get the value for the inherited array of superclasses (might be undefined)
	eval("arrInheritedSuperclasses = this." + strSecSupArrayname);

	//check to see if we've already inherited a secondarySuperclasses array
	if (arrInheritedSuperclasses != undefined) {
		//have to get a *copy* of the inherited array of superclasses because
		//we don't want to change this array itself, or else our superclass
		//would think it inherited everything that its subclasses did--bad!
		arrReturn = cloneObject(arrInheritedSuperclasses);
	} else { //create a new array
		arrReturn = new Array();
	} //end if we did/didn't inherit an array of secondary superclasses

	//go through the arguments, STARTING WITH INDEX 1 to skip the arrayname arg,
	//and add each constructor to the array under a string of its name
	for (var intArgIndex = 1; intArgIndex < arguments.length; intArgIndex++) {
		eval("arrReturn['" + arguments[intArgIndex] + "'] = " + arguments[intArgIndex] + ";");
	} //next argument

	//return the array
	return arrReturn;
} // end function multipleInherit
//******

//******
//culled from OverlapPerformanceTest.svg
//constructor for a Timer object
function Timer() {
	this.begin = 0;
	this.end = 0;
	this.time = 0;

	this.start = function () {
		this.begin = new Date().getTime();
		this.time = "timing";
		}; //end function start

	this.stop = function () {
		this.end = new Date().getTime();
		this.time = this.end - this.begin;
		}; //end function stop
} //end constructor Timer
//******

//******
//function to be used with CALL on associative arrays to return
//string concatenated from either their keys or their items.
//Works just like join on regular arrays.  Default is to join keys.
function assocJoin(strJoinChars, blnJoinItems) {
	var strCurrent, strReturn = "";
	//if we weren't given a join char, use ", "
	if (strJoinChars == undefined) {strJoinChars = ", ";}

	//loop through all the keys
	for (var strKey in this) {
		//if they want items, get the item. Else, use the key.
		if (blnJoinItems) {
			strCurrent = this[strKey];
		} else {
			strCurrent = strKey;
		} //end if they do/don't want items

		strReturn = strReturn + strCurrent + strJoinChars;
	} //next key

	//cut off the last characters (the excessive join chars) and return
	strReturn = strReturn.substring(0, strReturn.length-strJoinChars.length);
	return strReturn;
} //end function assocJoin
//******

//******
//function to be used on associative arrays to count
//how many items they have in them.
//Works just like length on regular arrays.
//Can be used with call, but can also be used by passing in
//the array to count
function assocLength(objAssocArray) {
	var intReturnCount = 0;
	if (objAssocArray == undefined) {objAssocArray = this;}
	//loop through all the keys
	for (var strKey in objAssocArray) {intReturnCount++;}
	return intReturnCount;
} //end function assocLength
//******

//******
//Spoofer object.  Gives one object a defined way to pretend to be something else
//for a while (and a way to stop pretending.)  To make an object that inherits from
//Spoofer spoof say, an Arc, set myObj.spoof = Arc and then CALL myObj.spoof()!
//This way, it is easy to find out what an object is spoofed as .. just look at
//spoof as a property instead of a method.
//In this case, Arc MUST have an unmake method.
function Spoofer() {
	this.init();
} //end Spoofer constructor

Spoofer.prototype.init = function () {
							this.spoofedAs = "";
							this.spoof = Spoofer_spoof;
							this.unmake = function () {};
							this.unspoof = this.unmake;
						}; //end Spoofer init

function Spoofer_spoof(objConstructor) {
	//check and make sure that the thing you're spoofing as is the same kinda thing as you??

	//check and make sure that the object you're spoofing as has make and unmake properties
	if ((objConstructor.prototype.make == undefined) || (objConstructor.prototype.unmake == undefined)) {throw new Error("constructor object does not have a make or unmake method and therefore cannot be spoofed.");}

	//set this constructor in the spoofedAs property
	this.spoofedAs = objConstructor;

	//any arguments that came after the constructor are fed into the constructor's make
	var strArgs = "";
	strArgs = writeArgString(arguments.length, 1);

	//call the make property
	eval ("objConstructor.prototype.make.call(this" + strArgs + ");");
} //end Spoofer_spoof function
//******

//******
//adds the desired value(s) to the beginning or end of the parent array.
//default is to add to end.  varAddition can be a single variable or an
//array.
function addToArray(arrParentArray, varAddition, blnAddFirst) {
	//var intStartIndex = 0;
	//var intNumDeletes = 0; //always, at least for now.
	var strVarsToAdd = "varAddition";  //initially, assume varAddition isn't an array
	var strAddFunction = "push"; //initially assume we're adding to the end

	//check that parentarray is really an array?

	//if blnaddfirst wasn't specified, make it the default
	if (blnAddFirst == undefined) {blnAddFirst = false;}

	//reset the start index for the splice if we're tacking things onto the end

	if (blnAddFirst == false) {strAddFunction = "unshift";}
	//intStartIndex = arrParentArray.length;}

	//if varAddition is an array
	if (varAddition.constructor == Array) {
		//create a string that refers to each element of the array
		strVarsToAdd = writeArgString(varAddition.length, 0, "varAddition", true);
	} //end if varAddition turns out to be an array

	//use eval to splice the desired values into the parent array at the desired point
	var strEval = "arrParentArray." + strAddFunction + "("  + strVarsToAdd + ");";
	eval(strEval);
} //end function addToArray
//******

//******
//NOTE: items of the array MUST be strings ... or something that can be meaningfully
//automatically converted to a string.  Otherwise I won't be responsible for the results!
//If blnSelfKeyed is true, the keys and items are the same; if false, the items of the hash
//are the corresponding indices of the original array. Default is blnSelfKeyed = true.
function arrayToHash(arrInput, blnSelfKeyed) {
	//local variables
	var strKey, strItem;
	var arrReturnHash = new Array();

	if (blnSelfKeyed == undefined) {blnSelfKeyed = true;}

	//loop through the input array, putting each item into a hash
	for (var intMemberIndex = 0; intMemberIndex < arrInput.length; intMemberIndex++) {
		strKey = strItem = arrInput[intMemberIndex];
		if (!blnSelfKeyed) {strItem = intMemberIndex;}
		arrReturnHash[strKey] = strItem;
	} //next array member

	//return the new hash
	return arrReturnHash;
} //end function arrayToHash
//******

//******
//function that takes in a string containing a range of numbers in the form
//"5, 1-3, 19-21, 8", etc, and returns an array with "1" set as the value for
//each item that is in the range.  Error messages are returned if something is
//wrong with the input string
function rangeSplit(strRange, intMaxPosition) {
	if (strRange == "") {return;}

	//take any spaces out of the string
	var objSpaceRegExp = new RegExp(" ", "g");
	strRange = strRange.replace(objSpaceRegExp, "");

	//make sure the string has only numbers, hyphens, and commas
	if (!isNumericPlus(strRange, "-,")) {
		return "Range may contain only numbers, hyphens, and commas";
	} //end if

	if (intMaxPosition != undefined) {
		//split the string on the commas
		var arrRanges = strRange.split(",");

		var arrReturn = new Array();

		//go through each entry
		for (var intRangeIndex = 0; intRangeIndex < arrRanges.length; intRangeIndex++) {
			var intPosition;
			var strCurRange = arrRanges[intRangeIndex];

			//if it has a hyphen in it
			if (strCurRange.search(/-/) > -1) {
				//split it on the hyphen
				var arrPositions = strCurRange.split("-");

				//parse each end as a number
				intPosition = parseInt(arrPositions[0]);
				var intSecondPosition = parseInt(arrPositions[1]);

				//make sure the first number is one or greater
				if (intPosition < 1) {return "first position " + intPosition + " must be changed to be one or greater";}

				//make sure the first number is less than the second number
				if (intPosition >= intSecondPosition) {return "first position " + intPosition + " must be changed to be less than second position " + intSecondPosition;}

				//subtract 1 from the first number and put it into the array
				arrReturn[intPosition-1] = 1;

				//make sure the second number is less than the maximum
				if (intSecondPosition > intMaxPosition) {return "position " + intSecondPosition + " must be less than or equal to " + intMaxPosition;}

				//now loop from the first number through the second number, subtracting one from each number and put it into the array
				for (var intIndex = intPosition-1; intIndex < intSecondPosition; intIndex++) {arrReturn[intIndex] = 1;}

			} else {
				//parse it as a number
				intPosition = parseInt(strCurRange);

				//make sure the number is one or greater
				if (intPosition < 1) {return "position " + intPosition + " must be changed to be one or greater";}

				//make sure the number is less than the maximum
				if (intPosition > intMaxPosition) {return "position " + intPosition + " must be less than or equal to " + intMaxPosition;}

				//subtract 1 from the number and put into the array
				arrReturn[intPosition-1] = 1;
			} //end if
		} //next string entry

		return arrReturn;
	} //end if
} //end function
//******

//******
//function that takes in a string containing a list of strings made up of some set
//of legal characters, separated by commas.  Returns (depending on value of blnToHash)
//either an array of the strings or a hash keyed by the strings.  Default is the hash.
//Also takes bln stating whether to uppercase the string. Default is yes.
//Error messages are returned if something is wrong with the input string.
//Requires the iValidations.js library for the "containsOnlySpecialCharacters" function.
function stringRangeSplit(strRange, strLegalChars, blnUppercase, blnToHash) {
	if (blnToHash == undefined) {blnToHash = true;}
	if (blnUppercase == undefined) {blnUppercase = true;}
	if (strRange == "") {return new Array();}

	//take any spaces out of the string and uppercase if desired
	var objSpaceRegExp = new RegExp(" ", "g");
	strRange = strRange.replace(objSpaceRegExp, "");
	if (blnUppercase) {strRange = strRange.toUpperCase();}

	//add the comma (the separator) to the legal char string
	strLegalChars = strLegalChars + ",";

	//make sure the string has only numbers, hyphens, and commas
	if (!containsOnlySpecialCharacters(strRange, strLegalChars)) {
		return "Range may contain only spaces and the following characters: " + strLegalChars;
	} //end if

	//split the string on the commas
	var arrReturn = strRange.split(",");

	//If the return is supposed to be a hash
	if (blnToHash) {arrReturn = arrayToHash(arrReturn);}

	return arrReturn;
} //end function stringRangeSplit
//******

//******
//A standard compare of two values, as used in sort functions:
//If val1 < val2, return -1; if val1 = val2, return 0;
//if val1 > val2, return 1.  Values are compared as numbers
//if both can successfully be converted.
function compareValues(varVal1, varVal2) {
	//local variables
	var fltVal1, fltVal2, intReturn;

	//try converting both values to numbers
	fltVal1 = parseFloat(varVal1);
	fltVal2 = parseFloat(varVal2);

	//see if they can both be treated as numbers
	if (!isNaN(fltVal1) && !isNaN(fltVal2)) {
		//work with the numbers from now on
		varVal1 = fltVal1;
		varVal2 = fltVal2;
	} //end if

	//Now do a standard compare, as used in sort functions:
	//If val1 < val2, return -1; if val1 = val2, return 0;
	//if val1 > val2, return 1.
	if (varVal1 < varVal2) {
		intReturn = -1;
	} else if (varVal1 == varVal2) {
		intReturn = 0;
	} else {
		intReturn = 1;
	} //end if

	return intReturn;
} //end function compareValues
//******

//******
//written to be used with the GoF decorator pattern, where
//the decorator object needs to expose the all the interfaces
//of the object that it is decorating
function importInterfaces(objImportTo, objImportFrom, strInnerName) {
	//local variables
	var reArgList = /\([^)]*\)/;

	//loop over all properties and methods in the object to import from
	for (var strPropOrMethod in objImportFrom) {
		//if prop or method starts with an underscore, ignore it ... it is private
		//Also ignore it if it is overridden in the class we're importing to!
		if ((strPropOrMethod.substr(0, 1) != "_") && (objImportTo[strPropOrMethod] == undefined)) {
			//get the value of the current prop or method
			var varCurPropOrMethod = objImportFrom[strPropOrMethod];

			//if current item is a function
			if ((varCurPropOrMethod != undefined) && (varCurPropOrMethod.constructor == Function)) {
				//capture the argument list from the function definition
				var strFuncDefinition = varCurPropOrMethod.toString();
				var strArgList = strFuncDefinition.match(reArgList)[0];

				//generate a string representing a new function
				var strNewFunction = "function " + strArgList + " { return this." + strInnerName + "." + strPropOrMethod + strArgList + ";}";

				//make the new function a method of the object we're importing into
				eval("objImportTo[strPropOrMethod] = " + strNewFunction + ";");
			} else {
				//import the property into the "to" object
				objImportTo[strPropOrMethod] = objImportFrom[strPropOrMethod];
			} //end if we're dealing with a function or a property
		} //end if prop/method isn't private
	} //next prop/method
} //end function importInterfaces
//******

//******
//sets a property of the input object to the input value only if it is different
//from the preexisting value of that property.
//Takes in the object which is the parent of the constant being set, the name of the
//property being set (as a string) and the value it should be set to.
//Returns true or false depending on whether the property value was changed
function setProperty(objConstantParent, strConstantProperty, varConstantValue) {
		var blnChanged = false;

		strAction= "getting the current value of the property";
		var varCurValue = objConstantParent[strConstantProperty];

		strAction = "checking if current value of property is different from the input value";
		if (varCurValue != varConstantValue) {
			strAction = "setting the format constant to the input value " + varConstantValue;
			objConstantParent[strConstantProperty] = varConstantValue;
			blnChanged = true;
		} //end if

		return blnChanged;
} //end setProperty
//******

//******
//This function creates a basic toString function that is more
//useful than the built-in one assigned to objects.  It displays
//a semi-colon separated list of any properties and their values.
//It ignores methods.  By default it does NOT display the contents
//of objects, but it can be made to by setting the blnDrillDown
//parameter to true.
function toString(blnDrillDown) {
	//local variables
	var varCurFuncOrProp, strPropContents;
	var strReturn = "";

	if (blnDrillDown == undefined) {blnDrillDown = false;}

	//loop over all functions and properties of this object
	for (var strFuncOrProp in this) {
		//get the current function or property
		varCurFuncOrProp = this[strFuncOrProp];

		//if current item is a property (ignore functions)
		if ((varCurFuncOrProp == undefined) || (varCurFuncOrProp.constructor != Function)) {
			if ((varCurFuncOrProp != undefined) && (varCurFuncOrProp instanceof Object) && (!blnDrillDown)) {
				strPropContents = "object";
			} else {
				strPropContents = varCurFuncOrProp;
			} //end if

			//add this property's name and value to the return string
			strReturn += strFuncOrProp + ": " + strPropContents + "; ";
		} //end if the cur item is a property
	} //next property or method

	//return the string
	return strReturn;
} //end function DynTable_toString

//NB: since the built in Object.toString is useless, I'm overriding it with mine
//for all Objects.
Object.prototype.toString = toString;
Array.prototype.toString = toString;
//******