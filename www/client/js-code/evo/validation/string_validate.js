/*
string_validate.js

String validation functions.

Revision History:
Written 2002 by Amanda Birmingham
10/13/03 Amanda Birmingham: added startswith extension method for String
*/

//******
//Public: collapses consecutive whitespace characters in the input
//string into one space, and chops all whitespace off both ends.
//Takes in a string.
//Returns a "normalized" version of the input string.
function normalizeString(strInput) {
	var strReturn = "";

	if (!isEmpty(strInput)) {
		//if there are any tabs, replace them with one space each
		strReturn = strInput.replace(/\t/g, " " );

		// Regular expressions for normalizing white space.
		var whtSpEnds = new RegExp("^\\s*|\\s*$", "g");
		var whtSpMult = new RegExp("\\s\\s+", "g");

		strReturn = strReturn.replace(whtSpMult, " ");  // Collapse any multiple white space.
		strReturn = strReturn.replace(whtSpEnds, "");   // Remove leading or trailing white space
	} //end if the string isn't empty

	return strReturn;
} //end function normalizeString
//******

//******
function isEmpty(strInput) {
	var blnReturn = false;
	if ((strInput == undefined) || (strInput == null) || (strInput.length == 0)) {blnReturn = true;}

	return blnReturn;
} //end function isEmpty
//******

//******
//Public
//changed name from IsWhiteSpace to isWhitespace and changed
//implementation from examination of each character to use of
//a blanket regular expression (02/21/03)
function isWhitespace(strInput) {
	var blnReturn = false;

	if (isEmpty(strInput)) {
		blnReturn = true;
	} else {
		//run a regex against the string to look for non whitespace;
		//if it matches, return false
		var intContentIndex = strInput.search(/\S/);
		if (intContentIndex == -1) {blnReturn = true;}
	} //end if the string is/isn't empty

	return blnReturn;
} //end function isWhitespace
//******

//******
//Private: This function takes in a list of characters and builds a string
//representing the character class containing these.  It handles
//placing special characters (- and ^) in places where they will
//be interpreted as literals rather than metacharacters.  If the
//negate argument is true, the class includes an opening ^ to
//negate it.  By default blnNegate is false.  If the ranges argument is
//defined, its contents are passed into the string verbatim (as in,
//"a-zA-Z".
function buildCharacterClass(strIncludedCharacters, strRanges, blnNegate) {
	if (strIncludedCharacters == undefined) {strIncludedCharacters = "";}
	if (strRanges == undefined) {strRanges = "";}
	if (blnNegate == undefined) {blnNegate = false;}

	//if both the ranges and the included characters are empty, there are
	//no characters to put in the character class, so error out.
	if ((isEmpty(strIncludedCharacters)) && (isEmpty(strRanges))) {
		throw new Error("buildCharacterClass: both included characters parameter and ranges parameter are empty");
	} //end if

	//local variables
	var strCurCharacter, strReturn;
	var strCharClass = "";
	var strLiteralCircumflex = "";
	var arrIncludedCharacters = strIncludedCharacters.split("");

	//if blnNegate then negateCharacter is "^", otherwise ""
	var strNegateChar = (blnNegate == true) ? "^" : "";

	//for each character in strIncludedCharacters
	for (var intIndex in arrIncludedCharacters) {
		//get the current character
		strCurCharacter = arrIncludedCharacters[intIndex];

		//decide if it needs special treatment
		switch (strCurCharacter) {
			case "-":
				//put it on the beginning of the return string
				strCharClass = strCurCharacter + strCharClass; break;
			case "^":
				//put it aside to tack onto the end of the string
				strLiteralCircumflex = "^"; break;
			default:
				//if it is "]", put a "\" onto the string
				if (strCurCharacter == "]") {strCharClass += "\\";}

				//put it onto the end of the return string
				strCharClass += strCurCharacter;
		} //end switch
	} //next included character

	//return string is:
	strReturn = "[" + strNegateChar + strCharClass + strRanges + strLiteralCircumflex + "]";
	return strReturn;
} //end function buildCharacterClass
//******

//******
//Public
function isRangePlus(strRange, strInput, strExtraCharacters) {
	if (strExtraCharacters == undefined) {strExtraCharacters = "";}

	//local variables
	var blnReturn = false;

	//if the string isn't empty
	if (!isEmpty(strInput)) {
		//if either the range or the extra characters are not empty
		//(if neither are filled, there are NO legal characters :( )
		if ((!isEmpty(strExtraCharacters)) || (!isEmpty(strRange))) {
			//create a negated char class
			var strCharClass = buildCharacterClass(strExtraCharacters, strRange, true);

			//create a regex from char class
			var objRegEx = new RegExp(strCharClass);

			//if string doesn't match new char class
			if (strInput.search(objRegEx) == -1) {blnReturn = true;}
		} //end if either the range or the extra characters are filled
	} //end if string isn't empty

	return blnReturn;
} //end function isRangePlus
//******

//******
//Public
function isAlphaPlus(strInput, strExtraCharacters) {
	return isRangePlus("a-zA-Z", strInput, strExtraCharacters);
} //end function isAlphaPlus
//******

//******
//Public
function isAlphanumericPlus(strInput, strExtraCharacters) {
	return isRangePlus("a-zA-Z0-9", strInput, strExtraCharacters);
} //end function isAlphanumericPlus
//******

//******
//Public
function isNumericPlus(strInput, strExtraCharacters) {
	return isRangePlus("0-9", strInput, strExtraCharacters);
} //end function isNumericPlus
//******

//******
//Public
function containsOnlySpecialCharacters(strInput, strExtraCharacters) {
	return isRangePlus("", strInput, strExtraCharacters);
} //end function containsOnlySpecialCharacters
//******

//******
//returns true if any of the characters which appear in the string of special
//characters also appear in the input string
function containsSpecialCharacter (strInput, strSpecialChars) {
	var blnReturn = false;

	//if the input isn't empty (in which case it *certainly* doesn't have any special chars)
	if (!isEmpty(strInput)) {
		//create a char class holding special characters
		var strCharClass = buildCharacterClass(strSpecialChars);

		//create a regex from char class
		var objRegEx = new RegExp(strCharClass);

		//if string matches new char class
		if (strInput.search(objRegEx) != -1) {blnReturn = true;}
	} //end if the input isn't empty

	return blnReturn;
} //end function containsSpecialCharacters
//******

//******
//Public
function containsNoSpecialCharacters(strInput, strExtraCharacters) {
	//call containsSpecialCharacter
	var blnContains = containsSpecialCharacter(strInput, strExtraCharacters);

	//invert the answer and return
	return !blnContains;
} //end function containsNoSpecialCharacters
//******

//******
function isCapitalLetter(varTempCharacter) {
	var blnReturn = ((varTempCharacter >="A")&&(varTempCharacter <="Z")) ? true : false;
	return blnReturn;
} //end function isCapitalLetter
//******

//******
function isLowercaseLetter(varTempCharacter) {
	var blnReturn = ((varTempCharacter >="a")&&(varTempCharacter <="z")) ? true : false;
	return blnReturn;
}//end function isLowercaseLetter
//******

//******
//returns a string in which any characters problematic for html or xml
//have been replaced with their entities.  These include <>'"
//it also excises any leading or trailing whitespace and converts
//tabs into spaces
function replaceBadCharacters(strOriginal) {
	var arrBadCharacters = new Array("'", ">", "<", '"');
	for (var intCharacterIndex = 0; intCharacterIndex < arrBadCharacters.length; intCharacterIndex++) {
		strOriginal = replaceCharacter(strOriginal, arrBadCharacters[intCharacterIndex]);
	} //next bad character

	//if there are any tabs, replace them with one space each
	strOriginal = strOriginal.replace(/\t/g, " " );

	//if there are leading or trailing spaces, cut them off
	strOriginal = strOriginal.replace(/^\s*|\s*$/g, "");

	return strOriginal;
} //end function replaceBadCharacters
//******

//******
//return original, with any instance of character replaced with the
//replacement.  If replacement is undefined, it is assumed to be the
//entity representing that character
function replaceCharacter(strOriginal, strCharacter, strReplacement) {
	if (strReplacement == undefined) {strReplacement = "&#" + strCharacter.charCodeAt(0) + ";";}

	var arrStuff = strOriginal.split(strCharacter);
	if (arrStuff.length > 1) {
		strOriginal = arrStuff.join(strReplacement);
	} //end if

	return strOriginal;
} //end function replaceCharacter
//******

//******
//Public: this function takes in a string that the user wishes to use as a
//regular expression.  It looks for characters that are special in
//regular expressions and creates a new string that has those special characters
//escaped.  For example, if one wants to search for the string $^^ in some data
//using a regular expression, it must be escaped to \$\^\^
//because $ and ^ are special characters in regular expressions.
//Takes in a string or something that can be converted to a string
//Returns a string escaped for use with re's
reEscape.specialChars = ["\\", "^", "$", "*", "+", "?", ".", "(", ")", "[", "]", "{", "}"];
function reEscape(strToEscape) {
	//if input was undefined, just return undefined
	if (strToEscape == undefined) {return undefined;}

	//coerce the input to a string
	strToEscape = new String(strToEscape);

	//local variables
	var arrSpecials = reEscape.specialChars;
	var arrToEscape, strCurInput, strCurEscape;
	var arrToReturn = new Array();

	//split the input string into an array of single characters
	arrToEscape = strToEscape.split("");

	//for each character in the test string
	for (var intEscapeIndex in arrToEscape) {
		//get the current character to test for escaping
		strCurInput = arrToEscape[intEscapeIndex];

		//for each character in the escape list
		for (var intSpecialIndex in arrSpecials) {
			//if the character in the test string matches the escape character
			if (strCurInput == arrSpecials[intSpecialIndex]) {
				//write a \ into the output string
				arrToReturn.push("\\"); break;
			} //end if
		} //next special character

		//write the character in the test string into the output
		arrToReturn.push(strCurInput);
	} //next character to escape

	//return output string
	return arrToReturn.join("");
} //end function reEscape
//******

//******
function startswith(search_text) {
	/* Returns true if string starts with search_text

	search_text: string or string-castable
	*/

	result = false;

	//error if no input
	if (search_text == undefined) {
		throw Error("startswith takes one argument (zero given)");
	} //end if no argument given

	//convert input to string
	if (search_text.toString) {
		search_text = search_text.toString();
	} else{
		search_text = String(search_text);
	} //end if input has a toString method

	//determine the length of the search text and get the substr of that len
	substr_len = search_text.length;
	start_text = this.substr(0, substr_len);
	if (start_text == search_text) {result = true;}
	return result;
} //end startswith

String.prototype.startswith = startswith;
//******
//-------------------------------
//Deprecated functions:

/*
//******
//THE FUNCTION IsWhiteSpace HAS BEEN DEPRECATED: use isWhitespace instead.
//******

//******
//THE FUNCTION removeConsecutiveSpaces HAS BEEN DEPRECATED: use normalizeString instead.
//******

//******
//THE FUNCTION hasCharsInBag HAS BEEN DEPRECATED: use containsSpecialCharacter instead.
//******

//******
//THE FUNCTION isLetter HAS BEEN DEPRECATED: use isAlphaPlus instead.
//******
*/
//-------------------------------