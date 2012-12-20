/*
bio_utils.js

Global data and free-standing functions to find matches and mismatches,
perform simple sequence complementing and reverse complementing, etc.

Revision History:
Written 2002 by Amanda Birmingham
*/

//******
//Global variables
//Iupac bases mapped to cannonical bases
var gIupacBaseMappings = new Array();
gIupacBaseMappings["R"] = new Array("A", "G");
gIupacBaseMappings["Y"] = new Array("U", "C");
gIupacBaseMappings["W"] = new Array("A", "U");
gIupacBaseMappings["S"] = new Array("G", "C");
gIupacBaseMappings["M"] = new Array("A", "C");
gIupacBaseMappings["K"] = new Array("U", "G");
gIupacBaseMappings["D"] = new Array("A", "U", "G");
gIupacBaseMappings["B"] = new Array("U", "C", "G");
gIupacBaseMappings["H"] = new Array("A", "U", "C");
gIupacBaseMappings["V"] = new Array("A", "G", "C");
gIupacBaseMappings["N"] = new Array("A", "C", "G", "U");

//Iupac bases mapped to cannonical bases AND IUPAC bases, including self
var gLooseBaseMappings = new Array();
gLooseBaseMappings["R"] = new Array("A", "G", "R");
gLooseBaseMappings["Y"] = new Array("U", "C", "Y");
gLooseBaseMappings["W"] = new Array("A", "U", "W");
gLooseBaseMappings["S"] = new Array("G", "C", "S");
gLooseBaseMappings["M"] = new Array("A", "C", "M");
gLooseBaseMappings["K"] = new Array("U", "G", "K");
gLooseBaseMappings["D"] = new Array("A", "U", "G", "W", "R", "K", "D");
gLooseBaseMappings["B"] = new Array("U", "C", "G", "Y", "S", "K", "B");
gLooseBaseMappings["H"] = new Array("A", "U", "C", "W", "Y", "M", "H");
gLooseBaseMappings["V"] = new Array("A", "G", "C", "R", "S", "M", "V");
gLooseBaseMappings["N"] = new Array("A", "C", "G", "U", "R", "Y", "W", "S", "M", "K", "D", "B", "H", "V", "N");

gBasesString = "ACGURYWSMKDBHVN-";
//******

//******
function reverseComSequence(objSeqTextbox) {
	//get the sequence out of the textbox
	var strSequence = objSeqTextbox.value;

	//complement the sequence
	strSequence = complementSequence(strSequence, true);

	//put it back in the textbox
	objSeqTextbox.value = strSequence;
} //end function reverseComSequence
//******


//******
function complementSequence(strSequence, blnReverse) {
	if (blnReverse == undefined) {blnReverse = false;}

	var arrSequence = strSequence.split("");

	for (var intCharIndex = 0; intCharIndex < arrSequence.length; intCharIndex++) {
		var strReplacement;
		switch (arrSequence[intCharIndex]) {
			case "A":
				strReplacement = "T"; break;
			case "a":
				strReplacement = "t"; break;
			case "C":
				strReplacement = "G"; break;
			case "c":
				strReplacement = "g"; break;
			case "G":
				strReplacement = "C"; break;
			case "g":
				strReplacement = "c"; break;
			case "T":
				strReplacement = "A"; break;
			case "t":
				strReplacement = "a"; break;
			default:
				strReplacement = undefined;
		} //end switch

		if (strReplacement != undefined) {
			arrSequence[intCharIndex] = strReplacement;
		} //end if
	} //next character

	if (blnReverse) {arrSequence.reverse();}

	return arrSequence.join("");
} //end function complementSequence
//******

//******
function turnTtoU(strSequence) {
	//replace any U with T
	var objUregExp = new RegExp ('T', 'g');
	strSequence = strSequence.replace(objUregExp, "U");

	var objUregExpLc = new RegExp("t", "g");
	strSequence = strSequence.replace(objUregExpLc, "u");

	return strSequence;
} //end function turnTtoU
//******

//******
findMatchMismatch.matchColors = new Array();
findMatchMismatch.matchColors["AU"] = "true";
findMatchMismatch.matchColors["UA"] = "true";
findMatchMismatch.matchColors["CG"] = "true";
findMatchMismatch.matchColors["GC"] = "true";
findMatchMismatch.matchColors["GU"] = "true";
findMatchMismatch.matchColors["UG"] = "true";

findMatchMismatch.letterMappings = new Array();
findMatchMismatch.letterMappings["-"] = new Array("-");
findMatchMismatch.letterMappings["A"] = new Array("A");
findMatchMismatch.letterMappings["C"] = new Array("C");
findMatchMismatch.letterMappings["G"] = new Array("G");
findMatchMismatch.letterMappings["U"] = new Array("U");
findMatchMismatch.letterMappings["R"] = new Array("A", "G");
findMatchMismatch.letterMappings["Y"] = new Array("U", "C");
findMatchMismatch.letterMappings["W"] = new Array("A", "U");
findMatchMismatch.letterMappings["S"] = new Array("G", "C");
findMatchMismatch.letterMappings["M"] = new Array("A", "C");
findMatchMismatch.letterMappings["K"] = new Array("U", "G");
findMatchMismatch.letterMappings["D"] = new Array("A", "U", "G");
findMatchMismatch.letterMappings["B"] = new Array("U", "C", "G");
findMatchMismatch.letterMappings["H"] = new Array("A", "U", "C");
findMatchMismatch.letterMappings["V"] = new Array("A", "G", "C");
findMatchMismatch.letterMappings["N"] = new Array("A", "C", "G", "U");

findMatchMismatch.letterN = "N";
findMatchMismatch.gap = "-";
function findMatchMismatch(strBaseContents, strPairContents) {
	//local variables
	var arrBaseLetters, arrPairLetters;
	var ascMakeBooleans = new Array();
	ascMakeBooleans["pair"] = false;
	ascMakeBooleans["mismatch"] = false;

	//throw an error if we weren't given two bases
	if (strBaseContents == undefined) {throw new Error("strBaseContents argument must be defined.");}
	if (strPairContents == undefined) {throw new Error("strPairContents argument must be defined.");}

	//class variables made local to shorten their names
	var ascMatches = findMatchMismatch.matchColors;
	var ascLetterMappings = findMatchMismatch.letterMappings;

	//uppercase both inputs and check for validity
	strBaseContents = String(strBaseContents).toUpperCase();
	strPairContents = String(strPairContents).toUpperCase();

	//get the array of letters corresponding to strContents and pairContents
	arrBaseLetters = ascLetterMappings[strBaseContents];
	arrPairLetters = ascLetterMappings[strPairContents];
	if (arrBaseLetters == undefined) {throw new Error("strBaseContents argument is unrecognized symbol: " + strBaseContents);}
	if (arrPairLetters == undefined) {throw new Error("strBaseContents argument is unrecognized symbol: " + strPairContents);}

	//if basecontents is n and paircontents is not - (or vice versa)
	if (((strBaseContents == findMatchMismatch.letterN) && (strPairContents != findMatchMismatch.gap)) || ((strPairContents == findMatchMismatch.letterN) && (strBaseContents != findMatchMismatch.gap))) {
		ascMakeBooleans["pair"] = ascMakeBooleans["mismatch"] = true;
	} else {
		//for each letter in the first array
		for (var intBaseIndex in arrBaseLetters) {
			//for each letter in the second array
			for (var intPairIndex in arrPairLetters) {
				//create the pair
				var strHashKey = arrBaseLetters[intBaseIndex] + arrPairLetters[intPairIndex];

				//find out whether this pair is a match
				var strMatchValue = ascMatches[strHashKey];

				//if pair is defined
				if (strMatchValue != undefined) {
					ascMakeBooleans["pair"] = true;
				} else {
					ascMakeBooleans["mismatch"] = true;
				} //end if
			} //next pair letter
		} //next base letter
	} //end if this is/isn't an always-match

	return ascMakeBooleans;
} //end function findMatchMismatch
//******