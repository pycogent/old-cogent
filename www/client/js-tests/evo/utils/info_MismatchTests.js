/*
info_MismatchTests.js

Constants and helper functions for testing findMatchMismatch function and
MismatchCodingEvaluator object

Revision History:
Written 2003 by Amanda Birmingham
*/

//******
//global constants:
//bases acceptable as glyph contents
var garrBases = new Array("A", "C", "G", "U", "R", "Y", "W", "S", "M", "K", "D", "B", "H", "V", "N", "-");

//lower triangular matrix comparing all bases with all others.
//first number is boolean of whether bases can make a match; second number is
//boolean of whether bases can make a mismatch.
var garrOutputMatrix = new Array();
garrOutputMatrix[0] = new Array("0/1");
garrOutputMatrix[1] = new Array("0/1", "0/1");
garrOutputMatrix[2] = new Array("0/1", "1/0", "0/1");
garrOutputMatrix[3] = new Array("1/0", "0/1", "1/0", "0/1");
garrOutputMatrix[4] = new Array("0/1", "1/1", "0/1", "1/0", "0/1");
garrOutputMatrix[5] = new Array("1/1", "0/1", "1/0", "0/1", "1/1", "0/1");
garrOutputMatrix[6] = new Array("1/1", "0/1", "1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[7] = new Array("0/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[8] = new Array("0/1", "0/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "0/1");
garrOutputMatrix[9] = new Array("1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[10] = new Array("1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[11] = new Array("1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[12] = new Array("1/1", "0/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[13] = new Array("0/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[14] = new Array("1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1",
								"1/1", "1/1", "1/1", "1/1", "1/1", "1/1", "1/1");
garrOutputMatrix[15] = new Array("0/1", "0/1", "0/1", "0/1",
								"0/1", "0/1", "0/1", "0/1",
								"0/1", "0/1", "0/1", "0/1",
								"0/1", "0/1", "0/1", "0/1");
//******

//******
function getOutputFromMatrix(intFirstIndex, intSecondIndex) {
	//turn the (string) indexes into numbers so they can be compared right
	intFirstIndex = parseInt(intFirstIndex);
	intSecondIndex = parseInt(intSecondIndex);

	//get larger of two indices
	if (intSecondIndex > intFirstIndex) {
		var tmp = intFirstIndex;
		intFirstIndex = intSecondIndex;
		intSecondIndex = tmp;
	} //end if second index is larger

	//get array out of garrOutputMatrix for that index,
	//then get item for smaller index out
	var arrOutput = garrOutputMatrix[intFirstIndex];
	var strOutput = arrOutput[intSecondIndex];

	return strOutput;
} //end getOutputFromMatrix
//******
//------------------------------------------------