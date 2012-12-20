/*
number_validate.js

Free-standing functions to validate numeric data.

Revision History:
Written 2002 by Amanda Birmingham
*/

//******
//Function takes in a single character and determines whether or not it is a
//digit between one and nine.
//Returns a boolean.
function isDigit(inputCharacter) {
	return ((inputCharacter >="0")&&(inputCharacter <="9")) ? true : false;
} //end function isDigit
//******

//******
//function to determine if input is an integer
//Returns a boolean.
function isInteger(input) {
	return (parseInt(input) == input) ? true: false;
}//end function isInteger
//******

//******
//function to determine if input is a positive integer
function isPosInteger(input) {
	var blnReturn = false;
	if (parseInt(input) == input) {
		if (parseInt(input) > 0) {
			blnReturn = true;
		} //end if > 0
	} //end if an integer
	return blnReturn;
} //end function isPosInteger
//******

//******
//Default is assumption that range is NOT exclusive
function isNumInRange(fltNum, fltLow, fltHigh, blnExclusive) {
	if (blnExclusive == undefined) {blnExclusive = false;}
	if (fltLow == undefined) {fltLow = Number.NEGATIVE_INFINITY;}
	if (fltHigh == undefined) {fltHigh = Number.POSITIVE_INFINITY;}

	//turn input into a number
	fltNum = Number(fltNum);
	if (isNaN(fltNum)) {return false;}

	var blnReturn = false;
	switch (blnExclusive) {
		case true:
			if ((fltNum < fltHigh) && (fltNum > fltLow)) {blnReturn = true;} break;
		case false:
			if ((fltNum <= fltHigh) && (fltNum >= fltLow)) {blnReturn = true;} break;
	} //end switch

	return blnReturn;
} //end function isNumInRange
//******

//******
//culled from OverlapPerformanceTest.svg
//function to test for valid numbers.
//can tell whether number passes 3 tests:
//number variable is defined, number is not negative, number is greater than zero
//number variable is defined is the default test.
//if you want another one, you can put in an explicit test type: "neg" or "zero"
//function returns a boolean: true if test passes.
function numTest(fltNum, strTestType) {
	var blnPass = true;

	//check if value is defined & is a number
	//if they didn't specify a known test type, or if the result is false,
	//drop out after this test
	if (isNaN(Number(fltNum))) {blnPass = false;}
	if ((!blnPass) || ((strTestType != "neg") && (strTestType != "zero"))) {return blnPass;}

	//check if number is zero or greater (nonnegative)
	//if they specified a test type of neg, or if the result is false,
	//drop out after this test
	if (fltNum < 0) {blnPass = false;}
	if ((!blnPass) || (strTestType == "neg")) {return blnPass;}

	//check if the number is greater than zero
	//return what you got
	if (fltNum <= 0) {blnPass = false;}
	return blnPass;
} //end function numTest
//******