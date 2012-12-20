/*
palette.js

Palette object, which provides automatic enabling/disabling of apply and
cancel buttons when any element in the palette changes. CollapsablePalette,
which adds a handlebar to the palette allowing it to slide in and out.

NB: will only work if associated tab html template has been used to create
the interface.  Watch out for naming conventions ... to avoid having to
pass a bunch o'different ids, the palettes require that html elements be
named according to a fixed convention: a prefix identifying the particular
palette added to fixed suffixes:
	prefix + "Palette" for palette div
	prefix + "HandleBar" for handlebar div
	"btn" + prefix + "Apply" for apply button
	"btn" + prefix + "Cancel" for cancel button

Revision History:
Written 2002 by Amanda Birmingham

from error_handler.js uses *
*/


//--------------------------------------------
//******
function Palette(objErrors, strApplyButtonId, strCancelButtonId) {
	if (objErrors != gstrPrototype) {
		this.module = "iPalette";
		this.init(objErrors, strApplyButtonId, strCancelButtonId);
	} //end if
} //end constructor Palette

//Palette doesn't inherit from anything, so it doesn't need its superclass or prototype set, or its constructor reset.
Palette.prototype.init = Palette_init;
Palette.prototype.countChangedFields = function () {var intCount = 0; for (var strKey in this.changedFieldList) {intCount++;} return intCount;};
Palette.prototype.clearChangedFields = function () {this.changedFieldList = new Array(); this.enableButtons(false);};
Palette.prototype.setCurrentVal = function(objFormElm) {this.currentVal = getFormElmValue(objFormElm);};
Palette.prototype.registerChangeOn = Palette_registerChangeOn;
Palette.prototype.cancelChanges = Palette_cancelChanges;
Palette.prototype.enableButtons = Palette_enableButtons;
//******

//******
function Palette_init(objErrors, strIdPrefix) {
	var strRoutine = "Palette_init";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "creating empty properties";
		this.changedFieldList = new Array();
		this.currentVal = undefined;
		this.form = undefined;

		strAction = "collecting the apply and cancel button objects";
		this.applyButton = document.getElementById("btn" + strIdPrefix + "Apply");
		this.cancelButton = document.getElementById("btn" + strIdPrefix + "Cancel");
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Palette_init function
//******

//******
function Palette_registerChangeOn(objFormElm) {
	var strRoutine = "Palette_registerChangeOn";
	var strAction = "";
	try {
		strAction = "setting the form if it is empty";
		if (this.form == undefined) {this.form = objFormElm.form;}

		strAction = "getting the form element name";
		var strFieldName = objFormElm.name;

		strAction = "getting the form element value";
		var strFieldValue = getFormElmValue(objFormElm);

		strAction = "checking if the new value is different from the old one.";
		if (strFieldValue != this.currentVal) {
			strAction = "creating a new array";
			var ascOldAndNewValues = new Array();
			ascOldAndNewValues["old"] = this.currentVal;
			ascOldAndNewValues["new"] = strFieldValue;

			strAction = "putting new array into changedFieldList";
			this.changedFieldList[strFieldName] = ascOldAndNewValues;

			strAction = "enabling the apply and cancel buttons";
			this.enableButtons();
		} //end if this value is actually different from the old one
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Palette_registerChangeOn
//******

//******
function Palette_cancelChanges() {
	var strRoutine = "Palette_cancelChanges";
	var strAction = "";
	try {
		strAction = "looping through all the changed fields";
		for (var strFormField in this.changedFieldList) {
			strAction ="getting the old value of the field named " + strFormField;
			var strOldFormValue = this.changedFieldList[strFormField]["old"];

			strAction = "checking that the old value is not undefined";
			if (strOldFormValue != undefined) {
				strAction = "calling setFormElmByValue with elm name and value " + strFormField + ", " + strOldFormValue;
				setFormElmByVal(this.form, strFormField, strOldFormValue);
			} //end if the old value isn't undefined
		} //next changed field

		strAction = "calling clearChangedFields";
		this.clearChangedFields();
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Palette_cancelChanges
//******

//******
function Palette_enableButtons(blnEnable) {
	var strRoutine = "Palette_enableButtons";
	var strAction = "";
	try {
		if (blnEnable == undefined) {blnEnable = true;}

		strAction = "altering the state of the apply and cancel buttons; disabled = " + !blnEnable;
		this.applyButton.disabled = !blnEnable;
		this.cancelButton.disabled = !blnEnable;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Palette_enableButtons
//******
//--------------------------------------------


//--------------------------------------------
//******
//Errors and idprefix are required.  objfuncowner, funcclose, and funcopen are not ... all can
//be left out as each has defaults.
function CollapsablePalette(objErrors, strIdPrefix, funcClose, funcOpen, objFuncOwner) {
	if (objErrors != gstrPrototype) {
		this.module = "iSets";
		this.init(objErrors, strIdPrefix, funcClose, funcOpen, objFuncOwner);
	} //end if
} //end constructor Palette

CollapsablePalette.superclass = Palette.prototype;
CollapsablePalette.prototype = new Palette(gstrPrototype);
CollapsablePalette.prototype.constructor = CollapsablePalette;
CollapsablePalette.prototype.init = CP_init;
CollapsablePalette.prototype.togglePalette = CP_togglePalette;
//******

//******
function CP_init (objErrors, strIdPrefix, funcClose, funcOpen, objFuncOwner) {
	var strRoutine = "CP_init";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "calling the init of CollapsablePalette's superclass (Palette) to set up inherited properties";
		CollapsablePalette.superclass.init.call(this, objErrors, strIdPrefix);

		strAction = "collecting the handlebar and palette objects";
		this.handlebar = document.getElementById(strIdPrefix + "HandleBar");
		this.palette = document.getElementById(strIdPrefix + "Palette");

		strAction = "setting the closePalette function";
		if (funcClose == undefined) {funcClose = function () {};}
		this.closePalette = funcClose;

		strAction = "setting the openPalette function";
		if (funcOpen == undefined) {funcOpen = function () {};}
		this.openPalette = funcOpen;

		strAction = "setting the functionOwner property";
		this.functionOwner = objFuncOwner;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end CP_init

//******
function CP_togglePalette() {
	var strRoutine = "CP_togglePalette";
	var strAction = "";
	try {
		var strDisplay, strHandleText;

		strAction = "if functionOwner property is empty, make it default to this.owner";
		if (this.functionOwner == undefined) {this.functionOwner = this.owner;}

		strAction = "getting palette object's display style";
		var strPaletteDisplay = this.palette.style.display;

		strAction = "switching on if the palette is currently displayed: " + strPaletteDisplay;
		switch (strPaletteDisplay) {
			case "block":
				strAction = "checking if anything has changed";
				if (this.countChangedFields() > 0) {
					//if warnings are on
						strAction = "confirming with the user that they want to close the palette";
						if (!window.confirm("Some options have been changed.\nClose palette without applying changes?")) {return;}

						strAction = "calling cancelChanges";
						this.cancelChanges();
					//end if
				} //end if anything has changed

				strAction = "calling closePalette";
				this.closePalette.call(this.functionOwner);

				strAction = "setting palette display and handlebar text values";
				strDisplay = "none";
				strHandleText = "&gt;";
				break;
			case "none":
				strAction = "calling openPalette";
				this.openPalette.call(this.functionOwner);

				strAction = "setting palette display and handlebar text values";
				strDisplay = "block";
				strHandleText = "&lt;";
				break;
			default:
				throw new Error("invalid palette visibility attribute: " + strPaletteDisplay);
		} //end switch

		strAction = "setting palette display to " + strDisplay;
		this.palette.style.display = strDisplay;

		strAction = "changing handlebar's text to " + strHandleText;
		this.handlebar.innerHTML = strHandleText;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function CP_togglePalette
//******
//--------------------------------------------