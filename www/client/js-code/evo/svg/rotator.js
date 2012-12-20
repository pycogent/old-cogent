/*
rotator.js

These functions allow a user to arbitrarily rotate the painting object.
They were modified from originals in Adobe's SVG Draw; copyright notice
after this header.

Revision History:
Modified 2002 by Amanda Birmingham
*/

/* Copyright 2001 Adobe Systems. You may copy, modify, and distribute
*  this file, if you include this notice & do not charge for the distribution.
*  This file is provided "AS-IS" without warranties of any kind, including any
*  implied warranties.
*
*  Initial Author and Architect:  Glen H. Gersten
*
*/

//-------------------------------------
//GLOBAL VARIABLES -- used ONLY in event handler functions
var moveHandler = nothing; //for mouse event handlers
var upHandler = nothing; //for mouse event handlers
var gobjCurRotation;
var gascResolution;
var gfltTraversedAngle;
//-------------------------------------


//-------------------------------------
//EVENT HANDLERS

//******
function nothing() {}
//******

//******
function rotatePrep(mouseEvt, strElmId) {
	//local variables
	var objSvgRoot, objRotTarget;
	var blnAltKey, blnCtrlKey, intBtnNum;

	//find out if the alt key is held down, or
	//the control key is held down, and which
	//mouse button was pushed
	blnAltKey = mouseEvt.getAltKey();
	blnCtrlKey = mouseEvt.getCtrlKey();
	intBtnNum = mouseEvt.getButton();

	//only if the right mouse button was pushed, with no modifier keys
	if (!blnAltKey && !blnCtrlKey && (intBtnNum == 0)) {
		//get the target element by its id
		objOwnerDoc = mouseEvt.getTarget().getOwnerDocument();
		objSvgRoot = objOwnerDoc.getDocumentElement();
		objRotTarget = objOwnerDoc.getElementById(strElmId);

		//get the pixelSize:
		gascResolution = getPixSize(objSvgRoot);

		//reset the global traversed angle and global rotation object
		gfltTraversedAngle = 0;
		gobjCurRotation = new Rotation(objRotTarget);

		//set the starting angle of the rotation
		gobjCurRotation.angle1 = gobjCurRotation.findAngle(mouseEvt, gascResolution);

		//set the event handlers for the coming rotation
		moveHandler = rotate;
		upHandler = rotateStop;
	} //end if mousebutton is zero
} //end function rotatePrep
//******

//******
function rotate(mouseEvt) {
	//local variables
	var angle2;

	if (mouseEvt.getButton() == 0) {
		//find the ending angle of the rotation
		angle2 = gobjCurRotation.findAngle(mouseEvt, gascResolution);

		//find the traversed angle of the rotation;
		gfltTraversedAngle = angle2 - gobjCurRotation.angle1;

		gobjCurRotation.makeNewTransform(gfltTraversedAngle);
	} //end if mousebutton is zero
} //end function rotate
//******

//******
function rotateStop() {
	moveHandler = nothing;
	upHandler = nothing;

	reRotate(gobjCurRotation.element, gfltTraversedAngle);
} //end function rotateStop
//******
//-------------------------------------


//-------------------------------------
//MISC UTILITY FUNCTIONS
//******
//calculates viewbox x & y and pixel x & y, returns
//a hash containing these values.
function getPixSize(objSvgRoot) {
	//local variables
	var pluginW, pluginH, strViewbox;
	var arrViewboxVals, viewboxW, viewboxH;
	var ascReturn = new Array();

	//get the width and height of the plugin window
	pluginW = parseFloat(window.innerWidth);
	pluginH = parseFloat(window.innerHeight);

	//split the viewbox on spaces
	strViewbox = objSvgRoot.getAttribute("viewBox");
	arrViewboxVals = strViewbox.split(" ");

	//get the first two entries: x and y
	ascReturn["viewboxX"] = parseFloat(arrViewboxVals[0]);
	ascReturn["viewboxY"] = parseFloat(arrViewboxVals[1]);

	//get the width and height
	viewboxW = parseFloat(arrViewboxVals[2]);
	viewboxH = parseFloat(arrViewboxVals[3]);

	//calculate the x and y pixelsize
	ascReturn["pixelX"] = viewboxW / pluginW;
	ascReturn["pixelY"] = viewboxH / pluginH;

	return ascReturn;
} //end function getPixSize
//******

//******
function reRotate(objRotatedElm, fltAngle) {
	//get all textnodes
	var arrTextElms = objRotatedElm.getElementsByTagName("text");

	//for each textnode, rerotate it
	for (var intElmIndex = 0; intElmIndex < arrTextElms.length; intElmIndex++) {
		//getting the text element with index intElmIndex
		var objElement = arrTextElms.item(intElmIndex);

		//"creating a rotation object for this base group";
		var objRotation = new Rotation(objElement);

		//"calling makenewtransform on rotation obj";
		objRotation.makeNewTransform(-fltAngle);
	} //next id
} //end function reRotate
//-------------------------------------


//-------------------------------------
//ROTATION OBJECT
//******
//Rotation constructor.  Given an element that will be rotated, works out starting transformation,
//and center information.  Stores this in a neat object package.
function Rotation(objElement) {
	this.element = objElement;
	this.angle1 = undefined;
	this.traversedAngle = undefined;

	this.prevTransform = getTrans(this.element);

	this.setCenters();
} //end Rotation constructor

Rotation.prototype.setCenters = Rot_setCenters;
Rotation.prototype.findAngle = Rot_findAngle;
Rotation.prototype.makeNewTransform = Rot_makeNewTransform;
//******

//******
function Rot_setCenters() {
	//local variables
	var objCenterMatrix, objBbox;
	var fltBoxCx, fltBoxCy;

	objBbox = this.element.getBBox();

	fltBoxCx = objBbox.x + objBbox.width/2;
	fltBoxCy = objBbox.y + objBbox.height/2;

	if (this.prevTransform) {
		objCenterMatrix = new matrixPointMult(this.prevTransform, fltBoxCx, fltBoxCy);
		this.cx = objCenterMatrix.x;
		this.cy = objCenterMatrix.y;
	} else {
		this.cx = fltBoxCx;
		this.cy = fltBoxCy;
	} //end if we have a preexisting matrix

	this.boxCx = fltBoxCx;
	this.boxCy = fltBoxCy;
} //end function Rot_setCenters
//******

//******
function Rot_findAngle(mouseEvt, ascResolution) {
	//local variables
	var X, Y;
	var px, py;
	var angle;

	X = mouseEvt.getClientX() - 0;
	Y = mouseEvt.getClientY() - 0;

	px = X * ascResolution["pixelX"] - this.cx + ascResolution["viewboxX"];
	py = Y * ascResolution["pixelY"] - this.cy + ascResolution["viewboxY"];

	if (py != 0 && px != 0) {
		angle = Math.atan2(py, px);
	} else {
		angle = 0;
	} //end if py and px are not both zero

	return angle;
} //end function Rot_findAngle
//******

//******
function Rot_makeNewTransform(fltTraversedAngle) {
	//local variables
	var originM, rotateM, backM, tempM, transM, newM;
	var thisTransform;
	var boxCx = this.boxCx;
	var boxCy = this.boxCy;

	originM = new transMatrix(-boxCx , -boxCy);
	rotateM = new rotMatrix(fltTraversedAngle);
	backM = new transMatrix(boxCx, boxCy);
	tempM = new matrixMult(rotateM, originM);
	transM = new matrixMult(backM, tempM);

	if (this.prevTransform) {
		newM = new matrixMult(this.prevTransform, transM);
	} else {
		newM = transM;
	} //end if there is an existing transform for the current elm

	thisTransform = matrixToString(newM);

	this.element.setAttribute("transform", thisTransform);
} //end function makeRotateTransform
//******
//-------------------------------------