/*
transform_matrices.js

These function work on SVG transformation matrices.  They were modified from
originals in Adobe's SVG Draw; copyright notice after this header.

Revision History:
11/21/03 Amanda Birmingham: added handling of scale to transStrToMatrix
*/

/* Copyright 2001 Adobe Systems. You may copy, modify, and distribute
*  this file, if you include this notice & do not charge for the distribution.
*  This file is provided "AS-IS" without warranties of any kind, including any
*  implied warranties.
*
*  Initial Author and Architect:  Glen H. Gersten
*
*/

function getTrans(thisElem) {
	//local variable
	var strTransAttribute = "";
	var objReturnMatrix;

	//check that we got an element to find the transform attribute OF
	if (thisElem) {
		strTransAttribute = thisElem.getAttribute('transform');
	} //end if thisElem exists

	//if we managed to find a transform attribute
	if (strTransAttribute != "") {
		//create a new matrix object from that transform string
		objReturnMatrix = new transStrToMatrix(strTransAttribute);

		//if the new matrix is invalid, make it null again
		if (objReturnMatrix.a == "-999999") {objReturnMatrix = undefined;}
	} //end if we found a transform attribute

	return objReturnMatrix;
} //end function getTrans

function matrixCreate(thisString) {
	var vals = thisString.split(' ');
	this.a = vals[0] -0;
	this.b = vals[1] -0;
	this.c = vals[2] -0;
	this.d = vals[3] -0;
	this.x = vals[4] -0;
	this.y = vals[5] -0;
} //end function matrixCreate

function matrixToString(thisMatrix) {
	return "matrix(" + thisMatrix.a + " " + thisMatrix.b + " " +
		thisMatrix.c + " " + thisMatrix.d + " " + thisMatrix.x +
		" " + thisMatrix.y + ")";
} //end function matrixToString

function matrixMult(m1, m2) {
	this.a = m1.a * m2.a + m1.c * m2.b;
	this.b = m1.b * m2.a + m1.d * m2.b;
	this.c = m1.a * m2.c + m1.c * m2.d;
	this.d = m1.b * m2.c + m1.d * m2.d;
	this.x = m1.a * m2.x + m1.c * m2.y + m1.x;
	this.y = m1.b * m2.x + m1.d * m2.y + m1.y;
} //end function matrixMult

function matrixPointMult(m, X, Y) {
	this.x = m.a * X + m.c * Y + m.x;
	this.y = m.b * X + m.d * Y + m.y;
} //end function matrixPointMult

function transMatrix(thisX, thisY) {
	if( ! thisX || thisX == "" ) {thisX = 0;}
	if( ! thisY || thisY == "" ) {thisY = 0;}
	this.a = 1;
	this.b = 0;
	this.c = 0;
	this.d = 1;
	this.x = thisX;
	this.y = thisY;
} //end function transMatrix

function rotMatrix(thisAngle) {
	if (! thisAngle || thisAngle == "") {thisAngle = 0;}
	var cosAngle = Math.cos(thisAngle);
	var sinAngle = Math.sin(thisAngle);
	//var thisString = cosAngle  + " " + sinAngle + " " + -sinAngle + " " + cosAngle  + " 0 0";

	this.a = cosAngle;
	this.b = sinAngle;
	this.c = -sinAngle;
	this.d = cosAngle;
	this.x = 0;
	this.y = 0;
} //end function rotMatrix

function scaleMatrix(scaleX, scaleY) {
	if (! scaleX || scaleX == "") {scaleX = 1;}
	if (! scaleY || scaleY == "") {scaleY = 1;}
	this.a = scaleX;
	this.b = 0;
	this.c = 0;
	this.d = scaleY;
	this.x = 0;
	this.y = 0;
} //end function scaleMatrix

function transStrToMatrix(thisStr) {
	thisStr = thisStr + "";
	var numTrans = 0;
	var order = new Array();
	var matrixStart = thisStr.indexOf( "matrix(" ) +1;
	var translateStart = thisStr.indexOf( "translate(" ) +1;
	var rotateStart = thisStr.indexOf( "rotate(" ) +1;
	var scaleStart = thisStr.indexOf( "scale(" ) +1;

	if (matrixStart) {
		matrixStart = matrixStart +6;
		var matrixEnd = thisStr.indexOf( ")", matrixStart);
		if (matrixEnd != -2) {
			var matrixValue = thisStr.substring(matrixStart, matrixEnd);
		} //end if
		if (matrixValue) {
			var matrixM = new matrixCreate(matrixValue);
			numTrans++;
			order[numTrans] = new matrixOrder(matrixStart, matrixM);
		} //end if
	} //end if matrixStart

	if (translateStart) {
		translateStart = translateStart +9;
		var translateEnd = thisStr.indexOf( ")", translateStart);
		if (translateEnd != -2) {
			var translateValue = thisStr.substring(translateStart, translateEnd);
		}
		if (translateValue) {
			var translateM = new transMatrix(translateValue);
			numTrans++;
			order[numTrans] = new matrixOrder(translateStart, translateM);
		}
	}

	if (rotateStart) {
		rotateStart = rotateStart +9;
		var rotateEnd = thisStr.indexOf( ")", rotateStart);
		if (rotateEnd != -2) {
			var rotateAngle = thisStr.substring(rotateStart, rotateEnd);
		}
		var rotateValue = rotateAngle *0.017453293;
		if (rotateValue) {
			var rotateM = new rotMatrix(rotateValue);
			numTrans++;
			order[numTrans] = new matrixOrder(rotateStart, rotateM);
		}
	}

	if (scaleStart) {
		scaleStart = scaleStart + 5;
		var scaleEnd = thisStr.indexOf( ")", scaleStart);
		if (scaleEnd != -2) {
			var scaleValue = thisStr.substring(scaleStart, scaleEnd);
		}
		if (scaleValue) {
			var vals = scaleValue.split(',');
			var scaleM = new scaleMatrix(vals[0],vals[1]);
			numTrans++;
			order[numTrans] = new matrixOrder(scaleStart, scaleM);
		}
	}

	if (numTrans == 0 ) {
		this.a = "-999999";
	} else if (numTrans == 1) {
		return order[numTrans].matrix;
	} else {
		var mNum;
		var temp = new Object();
		for (mNum = 1; mNum < numTrans; mNum++) {
			var mCount = mNum;
			while (mCount < numTrans) {
				if (order[mNum].start > order[mCount +1].start) {
					temp.start = order[mCount +1].start;
					temp.matrix = order[mCount +1].matrix;
					order[mCount +1].start = order[mNum].start;
					order[mCount +1].matrix = order[mNum].matrix;
					order[mNum].start = temp.start;
					order[mNum].matrix = temp.matrix;
				}
				mCount++;
			} //end while
		} //next mNum

		for (mNum = numTrans; mNum > 1; mNum--) {
			order[numTrans -1].matrix = matrixMult(order[numTrans -1].matrix, order[numTrans].matrix);
		} //next mNum

		return order[1].matrix;
	} //end if
} //end function transStrToMatrix

function matrixOrder(start, thisMatrix) {
	this.start = start;
	this.matrix = thisMatrix;
} //end function matrixOrder

function matrixInvert(m) {
	var detInv = 1 / (m.a * m.d - m.b * m.c);
	this.a = m.d * detInv;
	this.d = m.a * detInv;
	this.x = (m.y * m.c - m.x * m.d) * detInv;
	this.y = (m.x * m.b - m.y * m.a) * detInv;
	detInv = -detInv;
	this.b = m.b * detInv;
	this.c = m.c * detInv;
} //end function matrixInvert