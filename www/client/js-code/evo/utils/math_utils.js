/*
math_utils.js

Objects and free-standing functions for finding random numbers, calculating
basic statistics, and performing many mathematical (mostly geometrical)
calculations.

Revision History:
Written 2002 by Amanda Birmingham
*/

//******
//culled from iBlowBubbles.js
//function to get a random whole number between lower limit and upper limit;
//if lower limit is not specified, it is zero
function getRand(intUpperLimit, intLowerLimit) {
	//check to make sure they entered an upper limit
	if ((intUpperLimit == 0)||(intUpperLimit==undefined)) {throw new Error("getRand: intUpperLimit is zero or undefined");}

	//if they didnt enter a lower limit, set it to zero
	if (intLowerLimit == undefined) {intLowerLimit=0;}

	//get a random number between 0 and 1
	var fltSeed = Math.random();

	//return the least integer >= to the seed*upper limit
	return Math.ceil((fltSeed*intUpperLimit) + intLowerLimit);
} //end function getRand
//******

//******
//solveByHalves: this function takes in an expression in X and tries to find
//the value of X for which the expression evaluates to zero.  The parameters
//are the expression itself (using X everywhere that the variable should go
//and nowhere that it shouldn't!), a value for X that makes the expression
//negative, a value for X that makes the expression positive, and a value of
//how close to X the returned result must be.

//The function works by halving the difference between positive and negative
//values, finding out whether the result at that halved point is positive or
//negative, and repeating the process until it reaches a value that produces
//a value for the expression that is within the desired error of zero.  It
//then returns this value.  If the process diverges instead of converging, it
//returns an undefined.

//NOTE that the function will also (eventually) return undefined if the expression
//has no real solution (ie, x*x - 4) or has no solution *in the defined range*
//(ie, x-9 over the range -1 to 1).  This happens when can no longer tell the
//difference between the previous value of the expression and the current value of
//the expression because it is working with such small numbers.  Maybe someday I'll
//get back to this and make it smarter about working these cases out some other way...

solveByHalves.XregExp = /X/g;

function solveByHalves(strExpressionInX, fltNegX, fltPosX, fltError) {
	//local variables
	var fltCurX;
	var fltXforNeg = fltNegX;
	var fltXforPos = fltPosX;
	var fltNegExp, fltPosExp;
	var fltCurExp = Number.POSITIVE_INFINITY; //initialize expression value for current X to something outrageous

	//while the expression value for the current x is not within fltError of 0
	while (Math.abs(fltCurExp) > fltError) {
		//evaluate the expression for the fltXforNeg and fltXforPos values
		fltNegExp = eval(strExpressionInX.replace(solveByHalves.XregExp,fltXforNeg)); //alert("NegExp is " + fltNegExp);
		fltPosExp = eval(strExpressionInX.replace(solveByHalves.XregExp,fltXforPos)); //alert("PosExp is " + fltPosExp);

		//find the point half way between fltXforNeg and fltXforPos
		//(Note that it doesn't matter which direction you do the subtraction in.)
		fltCurX = (fltXforPos - fltXforNeg)/2 + fltXforNeg; //alert("new curX is " + fltCurX);

		//evaluate strExpressionInX with fltCurX = fltCurExp;
		fltCurExp = eval(strExpressionInX.replace(solveByHalves.XregExp,fltCurX)); //alert("new curExp is " + fltCurExp);

		//check on whether the current value of the expression is positive
		//or negative and replace the appropriate variables for the next
		//runthrough.  Note, however, that we may never end up using them
		//if, when the while is evaluated, it turns out that this current
		//value is good enough.
		//if fltCurExp is positive
		if (fltCurExp > 0) {
			//if fltCurExp is < fltPosExp (ie, closer to zero)
			if (fltCurExp < fltPosExp) {
				//replace the values of fltPosExp and fltXforPos with the current values
				fltPosExp = fltCurExp;
				fltXforPos = fltCurX;
			} else { //if it is positive but not less than the current positive
				//we've got a problem ... X is diverging. return an undefined value.
				//alert("expression is diverging positively");
				return undefined;
			} //end if the current value is less than the positive value
		} else if (fltCurExp < 0) { //if fltCurExp is negative
			//if fltCurExp is > fltNegExp (ie, closer to zero)
			if (fltCurExp > fltNegExp) {
				//replace the values of fltNegExp and fltXforNeg with the current values
				fltNegExp = fltCurExp;
				fltXforNeg = fltCurX;
			} else { //we're diverging, so return undefined (see above for explanation).
				//alert("expression is diverging negatively");
				return undefined;
			} //end if the current value is greater than the negative value
		} //end if the value of the expression for the current X is - or +
		//NB: don't need a case in above 'if' for X = 0 ... that will just get returned
		//when we jump back up to the 'while' next anyway.
	} // end while

	//if we got this far, we managed to solve X within the desired error.  Return it.
	return fltCurX;
} //end function solveByHalves
//******

//******
//a constructor to create an object of the XYvalue class
function XYvalue(fltX, fltY) {
	//check that x and y are both numbers
	this.x = fltX;
	this.y = fltY;
} //end constructor XYvalue
//******

//******
//a function to find the center of a line segment for which one knows the endpoints
//(expressed as XYvalue objects, mind you.)
function findCenterpoint(objPoint1, objPoint2) {
	//make sure that objPoint1 and objPoint2 are both instances of XYvalue

	//work out deltaX/2 and deltaY/2
	var fltHalfDx = (objPoint2.x - objPoint1.x)/2;
	var fltHalfDy = (objPoint2.y - objPoint1.y)/2;

	//work out the center x and y values
	var fltXc = fltHalfDx + objPoint1.x;
	var fltYc = fltHalfDy + objPoint1.y;

	//return a new XYvalue object holding the center point
	return new XYvalue(fltXc, fltYc);
} //end function findCenterpoint
//******

//******
//a function to find the length of a line segment given its endpoints.
function findLength(objPoint1, objPoint2) {
	//make sure that objPoint1 and objPoint2 are both instances of XYvalue

	//use the pythagorean theorem: l^2 = deltaX^2 + deltaY^2
	var fltDeltaX = objPoint2.x - objPoint1.x;
	var fltDeltaY = objPoint2.y - objPoint1.y;
	var fltLength = Math.sqrt(Math.pow(fltDeltaX,2) + Math.pow(fltDeltaY,2));
	return fltLength; //return the length
} //end function findLength
//******

//******
//function to find the slope of a line between two points.  Returns the
//numerical slope value.  Returns undefined if the line is vertical.
function findSlope(objPoint1, objPoint2) {
	var fltDeltaX, fltDeltaY, fltSlope;

	//make sure that objPoint1 and objPoint2 are both instances of XYvalue
	fltDeltaX = objPoint2.x - objPoint1.x;
	fltDeltaY = objPoint2.y - objPoint1.y;

	//if x changed, calculate slope and return.  Otherwise, just return undefined.
	if (!floatEquals(fltDeltaX, 0)) {fltSlope = fltDeltaY/fltDeltaX;}
	return fltSlope;
} //end function findSlope
//******

//******
//invertSlope.  Returns the slope of a line perpendicular to the slope given.
//Handles special cases of original slope being undefined (vertical line) or
//zero (horizontal line);
function invertSlope(fltSlope) {
	if (fltSlope == undefined) {
		fltSlope = 0;
	} else if (floatEquals(fltSlope, 0)) {
		fltSlope = undefined;
	} else {
		fltSlope = -1/fltSlope;
	} //end examination of original slope

	return fltSlope;
} //end function invertSlope
//******

//******
//function to find the 2 possible center points of a circle from two points on the
//endpoint of one of its chords and its radius.  Takes an optional argument
//giving the length of the chord if you want to save it the trouble of
//working that out. Returns an array of XY value objects holding the centerpoints; this
//array can contain one or two objects, depending on how many viable centerpoints were
//found.  If none were found, returns undefined.

//Here's how it works:
//find the slope of the chord

//since a line (the height) bisecting a chord and going through the center
//will be perpendicular to the chord it bisects, we know the height line's
//slope will be the negative reciprocal of the slope of the chord.
//The slope of the height line can also be represented using the endpoints
//of the height line itself (pointH, pointC).  Thus, we have our first equation:
//-1/(ChordSlope) = (Yc - Yh)/(Xc - Xh);

//Of course, we also have an equation describing the length of the height line
//using the pythagorean theorem on the triangle it participates in with pointH
//and pointC:
//h^2 = (Xc - Xh)^2 + (Yc - Yh)^2
//Since h is a known quantity (using the pythagorean theorem on the triangle it
//participates in with 1/2*c and r), this gives us our second equation for solving
//for our two unknowns (Xc and Yc).

//solve h^2 = (Xc - Xh)^2 + (Yc - Yh)^2 for Xc and plug that into the
//slope equation, which then (for the algebraically hardy) reduces to
//an equation in Yc of the form that can be solved with the quadratic formula.

//once Yc is in hand, go back to the slope equation and solve for Xc.


function findCircleCentersFromChord(objPoint1, objPoint2, fltRadius, fltChordLength) {
	//local variables
	//a,b,&c are the constants in the quadratic formula.
	//K2 and K3 are intermediate constants aggregated
	//along the road to solving the equations, to keep them readable.
	//the others are explained as they are assigned.
	var fltK2, fltK3, fltA, fltB, fltC, objChordCenter;
	var fltChordM, fltH, fltM, fltXh, fltYh, fltXc, fltYc;
	var arrReturnPoints = new Array();

	//make sure that objPoint1 and objPoint2 are both instances of XYvalue
	//make sure fltRadius is a number greater than zero
	//if we didn't get a chord length, call findLength to get it
	if (fltChordLength == undefined) {fltChordLength = findLength(objPoint1, objPoint2);}
	//now validate that chordlength is a number greater than zero

	//find the length of the height (line from the center to the middle of the chord)
	//using 1/2*c and the radius and the pythagorean theorem
	fltH = Math.sqrt(Math.pow(fltRadius,2) - Math.pow((fltChordLength/2),2));

	//find the centerpoint of the chord line and break out the
	//x and y values into separate variables for easier use
	objChordCenter = findCenterpoint(objPoint1, objPoint2);
	fltXh = objChordCenter.x;
	fltYh = objChordCenter.y;

	//find the chord slope
	fltChordM = findSlope(objPoint1, objPoint2);

	//Decide how to get possible centers based on slope of chord
	if (fltChordM == undefined) {
		//if the slope is undefined, the chord is vertical, so the height is horizontal
		arrReturnPoints[arrReturnPoints.length] = new XYvalue(fltXh + fltH, fltYh);
		arrReturnPoints[arrReturnPoints.length] = new XYvalue(fltXh - fltH, fltYh);
	} else if (floatEquals(fltChordM, 0)) {
		//else if the slope is zero, the chord is horizontal, so the height is vertical
		arrReturnPoints[arrReturnPoints.length] = new XYvalue(fltXh, fltYh + fltH);
		arrReturnPoints[arrReturnPoints.length] = new XYvalue(fltXh, fltYh - fltH);
	} else {
		//find the slope of the height line (neg reciprocal of chord slope)
		fltM = -1/fltChordM;

		//solving height length and slope equations for Yc reduces to a form
		//that can be solved with the quadratic formula. Here goes:
		//First, work out the constants (remember K1 in notes = fltM)
		fltK2 = fltYh;
		fltK3 = Math.pow((fltM * fltH),2) - Math.pow((fltM*fltYh),2) - Math.pow(fltK2, 2);
		fltA = Math.pow(fltM,2) + 1;
		fltB = -2 * (Math.pow(fltM,2) * fltYh + fltK2);
		fltC = -fltK3;

		//now use quadratic formula to find the two possible Yc's
		var arrPossibleYcs = solveQuadratic(fltA, fltB, fltC);

		//if we found roots
		if (arrPossibleYcs != undefined) {
			//plug Yc into the slope equation to get Xc for each of possible Ycs,
			//create the center point object, and add to return array
			for (var intYcIndex = 0; intYcIndex < arrPossibleYcs.length; intYcIndex++) {
				fltYc = arrPossibleYcs[intYcIndex];
				fltXc = (fltYc - fltYh)/fltM + fltXh;

				//check that neither of the values for this centerpoint are NaN
				if ((!isNaN(fltYc)) && (!isNaN(fltXc))) {
					arrReturnPoints[arrReturnPoints.length] = new XYvalue(fltXc, fltYc);
				} //end if neither value is NaN
			} //next possible Yc
		} //end if we did find real Ycs
	} //end choice of slopes

	//will return undefined if no real roots
	if (arrReturnPoints.length == 0) {arrReturnPoints = undefined;}

	//return the array holding the two center points
	return arrReturnPoints;
} //end function findCircleCentersFromChord
//******

//******
//function to return the two possible values given by the
//quadratic formula.  Inputs are a, b, and c as described
//in the formula: [x = (-b +- sqrt(b^2 - 4ac))/2a] for an
//equation of the form 0 = ax^2 + bx + c.  The return values
//are sent back as a 2-element array.  If the formula finds
//no real roots, an undefined is returned instead of the array!
function solveQuadratic(fltA, fltB, fltC) {
	//strict error checking would make sure fltA, fltB, and fltC are all numbers

	//find the discriminant and check that it isn't negative
	var fltDiscriminant = Math.pow(fltB, 2) - 4*fltA*fltC;
	if (fltDiscriminant < 0) {return undefined;} //there are no real roots

	//calculate the sqrt of the discriminant and plug it into the equation
	var fltSqrtDiscriminant = Math.sqrt(Math.pow(fltB, 2) - 4*fltA*fltC);
	var fltRoot1 = (-fltB + fltSqrtDiscriminant)/(2*fltA);
	var fltRoot2 = (-fltB - fltSqrtDiscriminant)/(2*fltA);

	//create and return the roots array
	return new Array(fltRoot1, fltRoot2);
} //end function solveQuadratic
//******

//******
//findArcEndpoint.  Determines the endpoint of the arc with the input
//starting position, using radius, center point, and theta of the arc's circle.
//Returns an XYvalue holding the endpoint.  Since I often want to find many arcs on
//the same circle, it will hold onto the radius and centerpoint you give it .. thus,
//if you're working from the same circle over and over, you only have to include those
//arguments the first time through.  Any time you include them, they'll overwrite any
//previous saved values for those values.  You can have it either add or subtract
//the value of theta from the starting value; I have the default set to add, because
//that works better for creating a loop left-to-right in screen coordinates.
findArcEndpoint.radius = undefined;
findArcEndpoint.centerPoint = undefined;

function findArcEndpoint(objStartPosition, arcTheta, objCenterPoint, fltRadius, blnSubtractTheta) {
	var deltaX, deltaY, x, y, thetaStartPoint, thetaEndPoint;
	var intSignMultiplier = 1;

	if (objCenterPoint != undefined) {findArcEndpoint.centerPoint = objCenterPoint;}
	if (findArcEndpoint.centerPoint == undefined) {throw new Error("centerpoint is not defined");}

	if (fltRadius != undefined) {findArcEndpoint.radius = fltRadius;}
	if (findArcEndpoint.radius == undefined) {throw new Error("radius is undefined");}

	if (blnSubtractTheta == undefined) {blnSubtractTheta = false;}
	if (blnSubtractTheta == true) {intSignMultiplier = -1;}

	//work out the x and y distance of the start point from the center
	deltaX = objStartPosition.x - findArcEndpoint.centerPoint.x;
	deltaY = objStartPosition.y - findArcEndpoint.centerPoint.y;

	if (floatEquals(deltaX, 0)) {
		if (deltaY > 0) {thetaStartPoint = Math.PI/2;}
		if (deltaY < 0) {thetaStartPoint = Math.PI * (3/2);}
	} else if (floatEquals(deltaY, 0)) {
		if (deltaX > 0) {thetaStartPoint = 0;}
		if (deltaX < 0) {thetaStartPoint = Math.PI;}
	} else {
		//find the angle to the starting point from a horizontal line through the centerpoint
		thetaStartPoint = Math.atan(Math.abs(deltaY)/Math.abs(deltaX));

		if (deltaX < 0) {
			if (deltaY < 0) {thetaStartPoint = thetaStartPoint + Math.PI;}
			else {thetaStartPoint = Math.PI - thetaStartPoint;}
		} else {
			if (deltaY < 0 ) {thetaStartPoint = -thetaStartPoint;}
		} //end if deltaX is/isn't negative
	} //end if

	//find the angle of the endpoint from a horizontal line through the centerpoint
	thetaEndPoint = thetaStartPoint + (intSignMultiplier * arcTheta);

	//get the x position of the end point (convert back from polar coords)
	x = findArcEndpoint.radius * Math.cos(thetaEndPoint) + findArcEndpoint.centerPoint.x;
	y = findArcEndpoint.radius * Math.sin(thetaEndPoint) + findArcEndpoint.centerPoint.y;

	return new XYvalue(x, y);
} //end function findArcEndpoint
//******

//******
//findLineEndpoint.  Determines the endpoint of the line segment with the input
//starting position, length,  and slope.  Returns an XYvalue holding the endpoint.
//Works out the position of the undefined endpoint of the line seg
//using point-slope eqn of the line & eqn for length of the line segment (chord)
//by pythagorean theorem to get x = sqrt(length^2/(slope^2 + 1)) + x1
//and then using x to get y = m(x-x1) + y1 (pointslope eqn).  Because a given
//length, point, and slope define *2* endpoints, not one, function requires
//that it be passed an XYvalue argument holding ">", "<", or "==" for x and y,
//telling it whether the endpoint it is looking for has x,y >,<, == to that of
//the point it was given.
function findLineEndpoint(objStartPosition, fltLength, fltSlope, objEndptOperators) {
	var x, y, x1, y1;
	var intXsignMultiplier = 1;
	var intYsignMultiplier = 1;

	//input typechecks?

	//getting start x and y into local variables
	x1 = objStartPosition.x;
	y1 = objStartPosition.y;

	//transform the operators into signmultipliers for x and y
	if (objEndptOperators.x == findOperator.less) {intXsignMultiplier = -1;}
	if (objEndptOperators.y == findOperator.less) {intYsignMultiplier = -1;}

	//find x and y values of undefined end's position
	//if the slope is undefined, this is a vertical line
	if (fltSlope == undefined) {
		//just add the length, with the appropriate sign multiplier, to y1
		x = x1;
		y = y1 + intYsignMultiplier * fltLength;
	} else {
		x = intXsignMultiplier * Math.sqrt(Math.pow(fltLength,2)/(Math.pow(fltSlope,2) + 1)) + x1;
		y = fltSlope * (x - x1) + y1;
	} //end if slope is/isn't undefined

	return new XYvalue(x, y);
} //end function findLineEndpoint
//******

//******
//findOperator.  Returns as a string the operator (">", "<", "==")
//that describes how value1 input compares to value2 input.
findOperator.greater = ">";
findOperator.less = "<";
findOperator.equal = "==";

function findOperator(fltVal1, fltVal2) {
	var strReturnOp = "";

	//important to do the floatEquals test first, because the > test may be
	//technically true even if vals are equal w/in float epsilon!
	if (floatEquals(fltVal1,fltVal2)) {strReturnOp = findOperator.equal;}
	else if (fltVal1 > fltVal2) {strReturnOp = findOperator.greater;}
	else {strReturnOp = findOperator.less;}

	return strReturnOp;
} //end function findOperator
//******

//******
function findOperators(objPosition1, objPosition2) {
	var objReturnOps = new XYvalue();

	objReturnOps.x = findOperator(objPosition1.x, objPosition2.x);
	objReturnOps.y = findOperator(objPosition1.y, objPosition2.y);

	return objReturnOps;
} //end function findOperators
//******

//******
//reverseOperator.  Returns as a string the operator (">", "<", "==")
//that describes how value1 input compares to value2 input.
function reverseOperator(strOperator) {
	if (strOperator == findOperator.greater) {strOperator = findOperator.less;}
	else if (strOperator == findOperator.less) {strOperator = findOperator.greater;}

	return strOperator;
} //end function reverseOperator
//******

//******
function reverseOperators(objOperatorsXy) {
	var objNewOperators = new XYvalue();

	objNewOperators.x = reverseOperator(objOperatorsXy.x);
	objNewOperators.y = reverseOperator(objOperatorsXy.y);

	return objNewOperators;
} //end function reverseOperators
//******

//******
//Public: works out the average, stddev, and total of
//a list of numbers.
//Takes in an array of numbers
//Returns a hash with keys "sum", "average", and "stddev"
function getNumListStats(arrNumbers) {
	//check that input is an array?

	//local variables
	var intNumItems, fltCurItem;
	var ascReturn = new Array();
	var fltSum = 0;
	var fltSumSquares = 0;

	//get the length of the array
	intNumItems = arrNumbers.length;

	//for each entry in the list
	for (var intIndex in arrNumbers) {
		//get the current value
		fltCurItem = arrNumbers[intIndex];

		//add it to the sum
		fltSum += fltCurItem;

		//square it and add to the sum of squares
		fltSumSquares += fltCurItem * fltCurItem;
	} //next entry

	//work out the average and put in return array:
	ascReturn["average"] = fltSum / intNumItems;

	//work out the stddev and put in return array:
	ascReturn["stddev"] = Math.sqrt((fltSumSquares - ascReturn["average"])/(intNumItems - 1));

	//put sum in return array
	ascReturn["sum"] = fltSum;

	//return the hash
	return ascReturn;
} //end function getNumListStats
//******

//******
//Public.  Compares two floating point numbers to see whether
//they are equal within the epsilon provided.
//Takes in two floating point numbers (required) and an
//epsilon (string, optional.)  If epsilon is not provided,
//it is set to the default value.
//Returns true or false.
//Note: epsilon is a string, rather than a number, because
//someday I might want to give this function the ability
//to compare by relative amounts (percents) as well as absolute
//amounts.
floatEquals.epsilon = 0.00005;
function floatEquals(flt1, flt2, strEpsilon) {
	//local variables
	var fltEpsilon, fltDifference;
	var blnIsEqual = false;

	//if no epsilon is defined, make it default
	if (strEpsilon == undefined) {strEpsilon = floatEquals.epsilon;}

	//validate inputs: if any of them can't be converted to numbers, squalk
	fltEpsilon = parseFloat (strEpsilon);
	if (typeof flt1 != "number") {throw new Error ("flt1 argument must be a number, but was " + flt1 + " instead.");}
	if (typeof flt2 != "number") {throw new Error ("flt2 argument must be a number, but was " + flt2 + " instead.");}
	if (isNaN(fltEpsilon)) {throw new Error("strEpsilon argument must be convertable to a number, but was " + strEpsilon + " instead.");}
	if (fltEpsilon < 0) {throw new Error("strEpsilon argument must be nonnegative.");}

	//subtract flt2 from flt1; then find out whether the absolute value of the difference is
	//less than the epsilon value.  If so, equal is true.
	//Note that the first check fails if epsilon is zero, even if difference is also zero.
	//Clearly, this case should pass!  Hence the second condition.
	fltDifference = flt1 - flt2;
	if ((Math.abs(fltDifference) < fltEpsilon) || (fltDifference == 0)) {blnIsEqual = true;}

	return blnIsEqual;
} //end floatEquals
//******