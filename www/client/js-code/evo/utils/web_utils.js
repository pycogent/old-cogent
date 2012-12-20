/*
web_utils.js

Objects and free-standing functions for manipulating querystrings, urls,
form elements, and doms (among others.)  Several browser/xml parser
sniffers and MSIE-specific file manipulation methods.

Revision History:
Written 2002 by Amanda Birmingham
*/

//******
//Depends on 'blnHasDom' variable from iBrowserSniff.js
function toggleLink(objLink, strLinkClass) {
	//this function depends on basic dom actions, so check if the browser supports them
	if (blnHasDom) {
		//local variables
		var arrLinkClasses;
		var intClassIndex;
		var strClassName;

		//define the array of exclusive class names
		arrLinkClasses = new Array("activeLink", "inactiveLink", "disabledLink", "activeMenu", "inactiveMenu");

		//get the classname into a temp variable so we can work on it
		strClassName = objLink.className;

		//loop through the array
		for (intClassIndex = 0; intClassIndex < arrLinkClasses.length; intClassIndex++) {
			//create a new regular expression
			var objTempRegExp = new RegExp(" " + arrLinkClasses[intClassIndex]);

			//replace (remove) each one
			strClassName = strClassName.replace(objTempRegExp,"");
		} //next exclusive class

		//apply the new style
		objLink.className = strClassName + " " + strLinkClass;
	} //if this browser supports dom actions
} //end function toggleLink
//******

//******
function openSubWindow(windowAddress, windowName, windowHeight, windowWidth, strProperties) {
	var windowProperties;

	//define the basic properties for a subwindow
//	if ((strProperties == '') || (strProperties == undefined)) {
		windowProperties = "directories=no,location=no,menubar=no,resizable=yes,scrollbars=yes,status=no,toolbar=no,titlebar=no";
//	} else {
//		windowProperties = strProperties;
//	} //end if the user didn't/did supply the window properties themselves


	//check to make sure that we got a windowAddress and a windowName
	if (windowAddress == '') {
		alert('Javascript Error: no url specified for subwindow');
	}
	else if (windowName == '') {
		alert('Javascript Error: no window name specified for subwindow');
	}

	//now check whether we got a windowHeight and windowWidth or not
	if ((windowHeight == "")||(windowHeight == undefined)) {
		windowHeight = geditorWindowHeight;
	}
	if ((windowWidth == "")||(windowWidth == undefined)) {
		windowWidth = geditorWindowWidth;
	}


	//append the height and width to the windowProperties string
	windowProperties = windowProperties + ",height=" + windowHeight + ",width=" + windowWidth;


	//open the window and give it focus
	var newWindow = window.open(windowAddress, windowName, windowProperties);
	newWindow.focus();
	return newWindow;
}
//******

//******
//function below adapted from http://www.dominopower.com/issues/issue200004/howto002.html
//gets parameter values out of a querystring--or a kcookie, if you pass in the correct optional
//delimiter (";")
function getParameter(queryString, parameterName, delimiter) {
	//local variables
	var intParamBegin, intParamEnd;

	//if they didn't pass in a delimiter, make it "&"
	if ((delimiter == "") || (delimiter == undefined)) {
		delimiter = "&";
	} //end if they didn't pass in a delimiter

	//Add "=" to the parameter name (i.e. parameterName=value)
	parameterName = parameterName + "=";

	//if the querystring is not empty
	if ( queryString.length > 0 ) {
		// Find the beginning of the string
		intParamBegin = queryString.indexOf(parameterName);

		// If the parameter name is not found, skip it, otherwise return the value
		if ( intParamBegin != -1 ) {
			// Add the length (integer) to the beginning
			intParamBegin += parameterName.length;

			//We need to know where this parameter's value ends.
			//Multiple parameters are separated by the delimiter,
			//so look for one in the rest of the querystring
			intParamEnd = queryString.indexOf ( delimiter , intParamBegin );

			//if there is no delimiter in the rest of the querystring, then
			//just take the end of the querystring as the end of this parameter
			if ( intParamEnd == -1 ) {
				intParamEnd = queryString.length;
			} //end if there is no delimiter in the rest of the querystring

			// Return the string
			return unescape (queryString.substring ( intParamBegin, intParamEnd ));
		} //end if the parameter name is found
	} //end if the parameter string isn't empty

	//Because we would already have returned if a parameter was found,
	//this code will only be executed if the parameter WASN'T found and/or.
	//the querystring was empty.  Return "null" in these cases.
	return "null";
} //end function getParameter
//******

//******
function getPageName(strAddress) {
	var intPeriodPosition, intSlashPosition;
	var strPaneName;

	intPeriodPosition = strAddress.lastIndexOf(".");
	intSlashPosition = strAddress.lastIndexOf("/");
	strPaneName = strAddress.slice(intSlashPosition + 1, intPeriodPosition);
	return strPaneName;
} //end function getPageName
//******

//******
function urlEncode(strURL) {
	//local variables
	var strEncodedURL;
	var rePlus = /\+/g;

	//The escape function encodes special characters in the specified string and
	//returns the new string, with the exception of these characters: * @ - _ + . /
	strEncodedURL = escape(strURL);
	//now encode the + character
	strEncodedURL = strEncodedURL.replace(rePlus, "%2B");

	return(strEncodedURL);
} //end function urlEncode
//******

//******
function checkRadioButton(objRadioList, varChosenValue) {
	for (var intRadioIndex = 0; intRadioIndex < objRadioList.length; intRadioIndex++) {
		if (objRadioList[intRadioIndex].value == varChosenValue) {
			objRadioList[intRadioIndex].checked = true;
			break;
		} //end if this item has the right value
	} //next radio button
} //end function changeSeqTo
//******

//******
//loadXmlFromUrl function: loads xml from the specified url and into the loadUrl.xmlDom
//variable.  If blnInit is true, it sets onreadystatechange to changeReadyState.
//A default implementation of changeReadyState (which does nothing) is included;
//it should be overridden if you want to use it for something
loadXmlFromUrl.xmlDom = "";

function loadXmlFromUrl(strUrl, blnInit) {
	//strAction = "creating new activex xmldom object and setting properties";
	loadXmlFromUrl.xmlDom = new ActiveXObject("Microsoft.XMLDOM");
	loadXmlFromUrl.xmlDom.async = false;

	//strAction = "setting onreadystatechange if necessary";
	if (blnInit) {loadXmlFromUrl.xmlDom.onreadystatechange = changeReadyState;}

	//strAction = "loading xmldom from url: " + strUrl;
	loadXmlFromUrl.xmlDom.load(strUrl);
} //end function loadXmlFromUrl

function changeReadyState() {
	if (loadXmlFromUrl.xmlDom.readyState == 4) {return;}
} //end function changeReadyState
//******

//******
//press a button labelled "Show" or "Hide" to show or hide a div
function showHide(objButton, strDivId) {
	//local variables
	var objDiv, strDisplayType, strButtonValue;

	//get the div object
	objDiv = document.getElementById(strDivId);

	//based on the button value
	if (objButton.value == 'Show') {
		//pick the display value and new button value
		strButtonValue = 'Hide';
		strDisplayType = 'block';
	} else if (objButton.value == 'Hide') {
		//pick the display value and new button value
		strButtonValue = 'Show';
		strDisplayType = 'none';
	} //end if the button value is show or hide

	//reset the button value
	objButton.value = strButtonValue;

	//reset the display style
	objDiv.style.display = strDisplayType;
} //end function showHide
//******

//******
//Object to mimic the Spinner control.  Implement with a text box and a + and - button.
function Spinner (strTextId, intIncrement, intLowerBound, intUpperBound) {
	this.textId = strTextId;

	if (intUpperBound == undefined) {intUpperBound = Math.POSITIVE_INFINITY;}
	this.upperBound = intUpperBound;

	if (intLowerBound == undefined) {intLowerBound = Math.NEGATIVE_INFINITY;}
	this.lowerBound = intLowerBound;

	if (intIncrement == undefined) {intIncrement = 1;}
	this.step = intIncrement;
} //end Spinner constructor

Spinner.prototype.decrement = function() {this.validate(-this.step);};
Spinner.prototype.increment = function() {this.validate(this.step);};
Spinner.prototype.validate = Spinner_validate;

function Spinner_validate(fltChange) {
	if (fltChange == undefined) {fltChange = 0;}

	var objTextInput = document.getElementById(this.textId);
	var fltValue = Number(objTextInput.value) + fltChange;

	if (fltValue < this.lowerBound) {
		fltValue = this.lowerBound;
	} else if (fltValue > this.upperBound) {
		fltValue = this.upperBound;
	} //end if

	var modValue = fltValue % this.step;
	if (modValue != 0) {fltValue = fltValue - modValue;}

	objTextInput.value = fltValue;
} //end function Spinner_validate
//******

//******
//Function to get the value of (the currently-selected piece of) a given form element.
//Handles selectboxes and radio buttons as well as simpler elements.
//returns the value.  Will return the value of a checkbox's "checked" attribute unless you
//specifically tell it that you want the checkbox's value attribute instead.
function getFormElmValue(objFormElm, blnGetCheckboxVal) {
	var strReturnValue;

	if (blnGetCheckboxVal == undefined) {
		blnGetCheckboxVal = (objFormElm.type == "radio")?true:false;
	} //end if

	if (objFormElm.options) {
		strReturnValue = objFormElm.options[objFormElm.selectedIndex].value;
		if (strReturnValue == "") {strReturnValue = objFormElm.options[objFormElm.selectedIndex].text;}
	} else if (objFormElm.length) {
		for (var b = 0; b < objFormElm.length; b++) {
		  if (objFormElm[b].checked) {strReturnValue = objFormElm[b].value; break;}
		}//next
	} else {
		if (objFormElm.type == "checkbox") {
			if (blnGetCheckboxVal) {
				strReturnValue = objFormElm.value;
			} else {
				strReturnValue = objFormElm.checked;
			} //end if
		} else {
			strReturnValue = objFormElm.value;
		} //end if
	} //end if

	return strReturnValue;
} //end function getFormElmValue
//******

//******
//Function to set a form element with a given name to have the given value.
//Handles selectboxes and radio buttons as well as simpler elements.
//Will set the "checked" property of a checkbox unless specifically told to set the
//"value" property.
function setFormElmByVal(objForm, strFormElmName, strFormElmValue, blnSetCheckboxVal) {
	//get the form element with the given name
	var objFormElm = objForm.elements[strFormElmName];

	//if this is a multivalue element, like select or radio buttons
	if ((objFormElm.options) || (objFormElm.length)) {
		var objFormArray = objFormElm;
		if (objFormElm.options) {objFormArray = objFormArray.options;}

		//loop through all the values, find the one that matches what we want it to be,
		//and set the appropriate checked/selected value for the form elm
		for (var intOptionIndex = 0; intOptionIndex < objFormArray.length; intOptionIndex++) {
			if (objFormArray[intOptionIndex].value == strFormElmValue) {
				if (objFormElm.options) {
					objFormElm["selectedIndex"] = intOptionIndex;
				} else {
					objFormArray[intOptionIndex]["checked"] = true;
				} //end if
				break;
			} //end if
		} //next option
	} else {
		if (objFormElm.type == "checkbox") {
			if (blnSetCheckboxVal) {
				objFormElm.value = strFormElmValue;
			} else {
				objFormElm.checked = strFormElmValue;
			} //end if
		} else {
			//for simple elements, just set the value property of the element
			objFormElm.value = strFormElmValue;
		} //end if
	} //end if
} //end function setFormElmByVal
//******

//******
//NOTE: originally this function used the following lines to create a file:
	//var forWriting = 2;
	//var ts = fso.OpenTextFile(strFilename,forWriting,true);
//HOWEVER, bitter experience showed that a file opened in this manner can only
//handle ascii values up to 127 (ie, the write method will choke horribly on
//say, &#916;, the character for the greek capital delta.
//Now I use "CreateTextFile" instead of "OpenTextFile"; when the blnAsciiOnly
//argument is false, the file is create to use unicode, which has no prob with
//such characters.
function saveFile(strFilename, strContents, blnNoOverwrites, blnAsciiOnly) {
	//set default values
	if (blnNoOverwrites == undefined) {blnNoOverwrites = false;}
	if (blnAsciiOnly == undefined) {blnAsciiOnly = false;}

	//create a filesystemobject
	var fso = new ActiveXObject ("Scripting.FileSystemObject");

	//create a text file with the given filename
	var ts = fso.CreateTextFile(strFilename, !blnNoOverwrites, !blnAsciiOnly);

	//write the contents into the file
	ts.Write(strContents);

	//close the file
	ts.Close();
} //end saveFile
//******

//******
function deleteFile(strFilename) {
	var fso = new ActiveXObject ("Scripting.FileSystemObject");
	fso.DeleteFile(strFilename, false);
} //end deleteFile
//******

//******
//based on functions taken from http://www.brainjar.com/dhtml/tablesort/default4.asp
//USES the 'normalizeString' function in iStringValidations.js
function getInnerText(objElement) {
	var intChildIndex;
	var strInnerText = "";

	// This code is necessary for browsers that don't implement the DOM constants (like IE).
	if (document.ELEMENT_NODE == null) {
		document.ELEMENT_NODE = 1;
		document.TEXT_NODE = 3;
	} //end if there's no ELEMENT_NODE constant defined

	// Find and concatenate the values of all text nodes contained within the element.
	for (intChildIndex = 0; intChildIndex < objElement.childNodes.length; intChildIndex++) {
		//get the child node
		var objChildNode = objElement.childNodes[intChildIndex];

		if (objChildNode.nodeType == document.TEXT_NODE) {
			strInnerText += objElement.childNodes[intChildIndex].nodeValue;
		} else if (objChildNode.nodeType == document.ELEMENT_NODE && (objChildNode.tagName == "BR" || objChildNode.tagName == "br")) {
			strInnerText += " ";
		} else {
			// Use recursion to get text within sub-elements.
			strInnerText += getInnerText(objChildNode);
		} //end if this child is/isn't a text node
	} //next child node

	return normalizeString(strInnerText);
} //end function getInnerText
//******


//******
//based on functions taken from http://www.pxl8.com/innerHTML.html
function setInnerText(objElement, strInnerText) {
	// This code is necessary for browsers that don't implement the DOM constants (like IE).
	if (document.ELEMENT_NODE == null) {
		document.ELEMENT_NODE = 1;
		document.TEXT_NODE = 3;
	} //end if there's no ELEMENT_NODE constant defined

	//check that the first argument is really an element
	if (!objElement.childNodes || !objElement.appendChild) {throw new Error("objElement parameter does not expose Element interface.");}

	//coerce the innertext input to a string if it isn't already
	strInnerText = new String(strInnerText);

	// Find and erase all text nodes contained within the element.
	for (var intChildIndex = 0; intChildIndex < objElement.childNodes.length; intChildIndex++) {
		//get the child node
		var objChildNode = objElement.childNodes[intChildIndex];

		//if this node is a text node, remove it
		if (objChildNode.nodeType == document.TEXT_NODE) {objElement.removeChild(objChildNode);}
	} //next child node

	//now add a new text node
	var objNewText = document.createTextNode(strInnerText);
	objElement.appendChild(objNewText);
} //end function setInnerText
//******

//******
//XML DOM function: returns an array of nodes that are *direct* children of the desired node
//and have the desired tag name
function getChildrenByTagName(objNode, strTagName, blnFirstOnly) {
	var arrTagChildren = new Array();
	var arrChildren = objNode.childNodes;
	for (var intChildIndex = 0; intChildIndex < arrChildren.length; intChildIndex++) {
		if (arrChildren[intChildIndex].tagName == strTagName) {
			if (blnFirstOnly) {
				arrTagChildren = arrChildren[intChildIndex];
				break;
			} else {
				arrTagChildren[arrTagChildren.length] = arrChildren[intChildIndex];
			} //end if we're returning only the first child by this name
		} //end if this child has the right tag name
	} //next child

	return arrTagChildren;
} //end function getChildrenByTagName
//******

//******
//XML DOM function
//NB: tag names must be unique.  Will only get the info for the first child of that name.
function getDomInfo(objCurNode, arrIdentifiers, blnGetAttributes) {
	//create the return assoc array
	var arrReturn = new Array();
	var strCurVal;

	//if blnGetAttributes isn't set, make it false
	if (blnGetAttributes == undefined) {blnGetAttributes = false;}

	//if arrIdentifiers isn't an array, complain
	if (arrIdentifiers.constructor != Array) {throw new Error("invalid input type to getDomInfo: arrIdentifiers must be an array");}

	//for each element in the tag names array
	for (var intIndex = 0; intIndex < arrIdentifiers.length; intIndex++) {
		//get the name of this tag
		var strIdentifier = arrIdentifiers[intIndex];

		if (blnGetAttributes) {
			//get the attribute
			strCurVal = objCurNode.getAttribute(strIdentifier);
		} else {
			//get the text element's value
			strCurVal = objCurNode.getElementsByTagName(strIdentifier)[0].text;
		} //end if blnGetAttributes is/isn't true

		//put value into the return array under the identifier name
		arrReturn[strIdentifier] = strCurVal;
	} //next tag name

	//return the assoc array
	return arrReturn;
} //end getDomInfo
//******


//******
repaintByResize.blnPosResize = true;
function repaintByResize () {
	var intNumPixels;
	intNumPixels = repaintByResize.blnPosResize ? 1 : -1;
	window.resizeBy(intNumPixels, intNumPixels);
	repaintByResize.blnPosResize = !repaintByResize.blnPosResize;
} //end function repaintByResize
//******

//******
//takes in a url string and returns a string of the page at that url.
//Significantly modified the original so that it gets data synchronously,
//rather than asynchronously (which is a big headache with requiring
//callback functions, etc.)
//original version came from http://jibbering.com/2002/4/httprequest.html.
function openUrl(strUrl) {
	var objHttpRequest;

	//create an xmlhttp object
	if (window.XMLHttpRequest) {
		objHttpRequest = new XMLHttpRequest();
	} else if (window.ActiveXObject) {
		objHttpRequest = new ActiveXObject("Microsoft.XMLHTTP");
	} else {
		return "Error: http request object not supported.";
	} //end if

	//open the url; note the false: do NOT open asynchrononously
	objHttpRequest.open("GET", strUrl, false);

	//send null ... why?
	//I don't know, but it is necessary ...
	//maybe it makes the explicit request for the page?
	objHttpRequest.send(null);

	return objHttpRequest.responseText;
} //end function openUrl
//******

//******
//based on http://www.javascriptkit.com/javatutors/navigator.shtml
//Detect whether the browser is IE, version equal to or greater than the input number
function isIeVerPlus(fltLowestVersion) {
	var varUndefined;
	var strMsie = "MSIE";
	var strOpera = "Opera";
	var blnIsIeVerPlus = false;

	//if lowest version wasn't put in, make it zero -- will detect any IE
	if (fltLowestVersion == varUndefined) {fltLowestVersion = 0;}

	//get navigator object
	var objNavigator = navigator;

	//if there is a navigator object
	if (objNavigator) {
		//check for Opera first, since opera imitates other browsers.
		if (objNavigator.userAgent.indexOf(strOpera) == -1) {
			if (objNavigator.appVersion.indexOf(strMsie) != -1) {
				//split the appversion on 'MSIE'
				var arrVersionSplit = navigator.appVersion.split(strMsie);

				//get the version number --- should be the first flt number after 'msie'
				var fltVersion = parseFloat(arrVersionSplit[1]);

				//check whether this version number is >= to the input number
				if (fltVersion >= fltLowestVersion) {blnIsIeVerPlus = true;}
			} //end if 'MSIE' is in the app version
		} //end if this isn't opera
	} //end if there is an appversion

	return blnIsIeVerPlus;
} //end function isIeVerPlus
//******

//******
//based on the msxml sniffer from the XmlXslPortal at bayes.co.uk
function isUsingMsxml3plus() {
	var blnIs3plus = false;
	var xml = "<?xml version=\"1.0\" encoding=\"UTF-16\"?><cjb></cjb>";
	var xsl = "<?xml version=\"1.0\" encoding=\"UTF-16\"?><x:stylesheet version=\"1.0\" xmlns:x=\"http://www.w3.org/1999/XSL/Transform\" xmlns:m=\"urn:schemas-microsoft-com:xslt\"><x:template match=\"/\"><x:value-of select=\"system-property('m:version')\" /></x:template></x:stylesheet>";

	try{
		//create two new xmldom objects
		var s = new ActiveXObject("Microsoft.XMLDOM");
		var x = new ActiveXObject("Microsoft.XMLDOM");

		//set their async property to false
		s.async = false;
		x.async = false;

		//load the xml into x
		if (x.loadXML(xml)) {
			//load the xsl into s
			if (s.loadXML(xsl)){
				try{
					//try to transform the xml with the xsl
					var op = x.transformNode(s);

					//if the transform didn't return an error message
					if (op.indexOf("stylesheet") == -1) {blnIs3plus = true;}
				}catch(e){}
			} //end if the xsl loaded ok
		} //end if the xml loaded ok
	}catch(e){}

	return blnIs3plus;
} //end function isUsingMsxml3plus()
//******

//******
//Function to dig the FIRST instance a particular node out of an xml dom and perform a
//transform on it with the input stylesheet object (note: "object", not "name").  If a
//parameter value is specified, the function will also change the FIRST parameter in
//the stylesheet to have the input value.
//Returns a string holding the transform result.
function transformGroupNode(objXmlDom, objStylesheet, strGroupTag, strParamValue) {
	var strRoutine = "transformGroupNode";
	var strAction = "";
	try {
		strAction = "checking whether strParamValue is undefined: " + strParamValue;
		if (strParamValue != undefined) {
			strAction = "getting first stylesheet param tag";
			var objParam = objStylesheet.getElementsByTagName("xsl:param")[0];

			strAction = "updating stylesheet param tag to value " + strParamValue;
			objParam.setAttribute("select", "'" + strParamValue + "'");
		} //end if

		strAction = "getting the node we're going to (re)transform, with tag name " + strGroupTag;
		var objGroupNode = objXmlDom.getElementsByTagName(strGroupTag)[0];

		strAction = "transforming the node using stylesheet";
		var strResults = objGroupNode.transformNode(objStylesheet);

		return strResults;
	} //end try
	catch (e) {
		throw new Error("In " + strRoutine + ", while " + strAction + ": " + e.description);
	} //end catch
} //end transformGroupNode
//******
//--------------------------------------------
/*
Abstract class ColorGenerator has one public function:
getColorForValue, which takes in a color and a toggle
indicating if it should be greyscale.  Returns a string
containing the color.
*/
//--------------------------------------------
//******
function ArbitraryColorGenerator(ascColorsAndGreysByVal, arrDefaultColorAndGrey) {
	//set defaults if necessary
	if (arrDefaultColorAndGrey == undefined) {arrDefaultColorAndGrey = new Array("black", "black");}

	//validate inputs
	if (ascColorsAndGreysByVal.constructor != Array) {throw new Error("Parameter ascColorsAndGreysByVal must be an array");}
	if (arrDefaultColorAndGrey.constructor != Array) {throw new Error("Parameter arrDefaultColorAndGrey must be an array if defined");}

	//set properties
	this.defaults = arrDefaultColorAndGrey;
	this.colorsByVal = ascColorsAndGreysByVal;
} //end ArbitraryColorGenerator constructor

ArbitraryColorGenerator.COLOR_INDEX = 0;
ArbitraryColorGenerator.GREY_INDEX = 1;
ArbitraryColorGenerator.prototype.getColorForValue = ACG_getColorForValue;
//******

//******
function ACG_getColorForValue(strInputValue, blnGreyscale) {
	strInputValue = String(strInputValue);
	if (blnGreyscale == undefined) {blnGreyscale = false;}
	if (typeof blnGreyscale != "boolean") {throw new Error("Parameter blnGreyscale must be a boolean if defined");}

	//local variables
	var intColorIndex, arrColorAndGrey;
	var strReturn = undefined;

	//turn the greyscale boolean into an index we'll use to access the arrays
	intColorIndex = Number(blnGreyscale); //true = 1; false = 0;

	//get the color and grey array for this value, if there is one
	arrColorAndGrey = this.colorsByVal[strInputValue];

	//if the array exists, get the value for the appropriate color/grey state
	if (arrColorAndGrey) {strReturn = arrColorAndGrey[intColorIndex];}

	//if we didn't find anything yet, return the default color
	if (strReturn == undefined) {strReturn = this.defaults[intColorIndex];}

	return strReturn;
} //end ACG_getColorForValue
//******
//--------------------------------------------


//--------------------------------------------
//******
function LinearColorGenerator(fltNormalBound, fltSpecialBound) {
	if (parseFloat(fltNormalBound) != fltNormalBound) {throw new Error("Parameter fltNormalBound must be a floating point: " + fltNormalBound);}
	if (parseFloat(fltSpecialBound) != fltSpecialBound) {throw new Error("Parameter fltSpecialBound must be a floating point: " + fltSpecialBound);}

	this.normalBound = fltNormalBound;
	this.specialBound = fltSpecialBound;
} //end LinearColorGenerator constructor

LinearColorGenerator.prototype.getColorForValue = LIG_getColorOfValueOnScale;
//******

//******
//Public function that takes in a value and the normal and special bounds of the range that the
//value falls into.  Returns string representing that value's color on that range.  Is either a
//shade of red or (if the greyscale toggle is true) a shade of grey.
LIG_getColorOfValueOnScale.lowScale = 0;
LIG_getColorOfValueOnScale.highGreyScale = 70;
LIG_getColorOfValueOnScale.highColorScale = 100;
function LIG_getColorOfValueOnScale(fltCurValueInput, blnGreyscale) {
	//local variables
	var fltGreenPercent = 0;
	var fltBluePercent = 0;
	var fltNormalBound = this.normalBound;
	var fltSpecialBound = this.specialBound;

	//if greyscale toggle wasn't entered, assume it is false
	if (blnGreyscale == undefined) {blnGreyscale = false;}

	//validate the inputs
	var fltCurValue = parseFloat(fltCurValueInput);
	if (isNaN(fltCurValue)) {throw new Error("fltCurValueInput argument must be convertable to a floating point: " + fltCurValueInput);}
	if (typeof blnGreyscale != "boolean") {throw new Error("Parameter blnGreyscale must be a boolean: " + blnGreyscale);}

	//test the input is within the available range
	var fltGreaterBound = fltNormalBound;
	var fltSmallerBound = fltSpecialBound;
	if (fltSmallerBound > fltGreaterBound) {
		fltGreaterBound = fltSpecialBound;
		fltSmallerBound = fltNormalBound;
	} //end if
	if ((fltCurValue > fltGreaterBound) || (fltCurValue < fltSmallerBound)) {throw new Error("fltCurValue is not between the normalBound and specialBound.");}

	//set the normal and special values
	var fltSpecialScale = LIG_getColorOfValueOnScale.highColorScale;
	var fltNormalScale = LIG_getColorOfValueOnScale.lowScale;

	//if we're in greyscale, switch to other normal and special values
	if (blnGreyscale) {
		fltSpecialScale = LIG_getColorOfValueOnScale.lowScale;
		fltNormalScale = LIG_getColorOfValueOnScale.highGreyScale;
	} //end if

	var fltScaleMinusLow = (fltCurValue - fltNormalBound) * (fltSpecialScale - fltNormalScale) / (fltSpecialBound - fltNormalBound);
	var fltRedPercent = fltScaleMinusLow + fltNormalScale;
	fltRedPercent = fltRedPercent.toFixed(0);

	//if we're in greyscale, set the saturation in each channel to be the same
	if (blnGreyscale) {fltGreenPercent = fltBluePercent = fltRedPercent;}

	//calculate and return string holding rgb color for the input value
	return "rgb(" + fltRedPercent + "%, " + fltGreenPercent + "%, " + fltBluePercent + "%)";
} //end function LIG_getColorOfValueOnScale
//******
//--------------------------------------------

//******
//Public: function that uses an (absolute) base url and a
//relative url to create the absolute url to the relative
//resource. NOTE: this function does NOT validate urls or
//ensure that the relative url really is relative, etc: GIGO.
//Takes in a base url string and a relative url string
//Returns an absolute url string
function makeAbsoluteUrl(base_url, relative_url) {
	var PATH_SEPARATOR = "/";
	var UPLEVEL_INDICATOR = "..";
	var HTTP_PREFIX = "http://";
	var used_relative_pieces = new Array();

	//split on a questionmark to get rid of the querystring, if any
	var url_and_querystring = base_url.split("?");
	base_url = url_and_querystring[0]; //get the url part only

	//if "http:// is in the base_url, remove it .. we'll readd it at the end
	base_url = base_url.replace(new RegExp(HTTP_PREFIX, "i"), "");

	//split the base on '/' and assume we'll use all pieces
	var base_pieces = base_url.split(PATH_SEPARATOR);
	var first_unused_index = base_pieces.length;

	//get the last entry in the base url; if it is empty (url ended with
	//a '/') or it contains a period (and thus is a filename), we definitely
	//don't want to use that piece in the final url we build
	var last_piece = base_pieces[base_pieces.length-1];
	if ((last_piece.search(/\./) != -1) || (last_piece == "")) {
		first_unused_index--;
	}

	//split the relative url on '/'
	var relative_pieces = relative_url.split(PATH_SEPARATOR);

	//loop over all pieces of the relative url; determine whether
	//a piece contains ".." (in which case we subtract one from the
	//number of pieces of the base that we will use) or is an actual
	//path element (in which case we save it to use later.)
	for (var intPieceIndex in relative_pieces) {
		var curr_piece = relative_pieces[intPieceIndex];
		if (curr_piece == UPLEVEL_INDICATOR) {first_unused_index--;}
		else {used_relative_pieces.push(curr_piece);}
	} //next

	//make sure the relative path uses at least some of the base
	if (first_unused_index < 1) {
		throw new Error("relative path points above top level of base.");
	}

	//create the new, absolute url string and return
	var used_base_pieces = base_pieces.slice(0, first_unused_index);
	var result = HTTP_PREFIX + used_base_pieces.join(PATH_SEPARATOR) +
					PATH_SEPARATOR +
					used_relative_pieces.join(PATH_SEPARATOR);
	return result;
} //end makeAbsoluteUrl
//******

//******
//Public: Culled from jsprofiler. Creates and adds options to the input
//select box for each of the items listed in the input array.
//Takes in a form's select box object and an array of new text to be
//options for it.
//No return value
function populateSelect(objSelect, arrOptions) {
	//for each entry in the jslibraries array
	for (var intIndex in arrOptions) {
		//create a new option
		var objOption = new Option(arrOptions[intIndex]);

		//add it to the options list
		objSelect.options[objSelect.options.length] = objOption;
	} //next option
} //end populateSelect
//******

//******
//based on functions from http://www.faqts.com/knowledge_base/view.phtml/aid/1695/fid/178
//returns an array of the text for each selected option in a multiple select element,
//unless specifically told to get an array of the values for each.
//NOTE: eventually this could be expanded to also include an option to get the
//indexes of the selected options, if that would be useful.
function getMultiSelects(objMultiSelectElm, blnGetValue) {
	//local variables
	var objCurOption, strStoredInfo;
	var arrOptions = objMultiSelectElm.options;
	var arrReturn = new Array();

	if (blnGetValue == undefined) {blnGetValue = false;}

	//loop through each option in the selectbox
	for (var i = 0; i < arrOptions.length; i++) {
		//get the current option object
		objCurOption = arrOptions[i];

		//if this option is one of the selected ones
		if (objCurOption.selected) {
			//get the appropriate property, depending on what we
			//were asked to return
			if (!blnGetValue) {
				strStoredInfo = objCurOption.text;
			} else {
				strStoredInfo = objCurOption.value;
			} //end if

			//pus the info into the return array
			arrReturn.push(strStoredInfo);
		} //end if
	} //next

	return arrReturn;
} //end function getMultiSelects
//******
