/*
display_list.js

DisplayList and DisplayCheck objects used to automatically create a
complex checkbox-based control to show and hide groups of table columns.
See BayesFold Sequence and Structure table display palettes for an example.

Revision History:
Written 2002 by Amanda Birmingham

from error_handler.js uses *
from web_utils uses importInterfaces
*/

//------------------------------------
//DisplayList object.
//******
//DisplayList constructor.
function DisplayList(objErrors, strTableId, strIdPrefix, strDelimiter) {
	if (objErrors != gstrPrototype) {
		this.module = "display_list";
		this.init(objErrors, strTableId, strIdPrefix, strDelimiter);
	} //end if
} //end constructor DisplayList

//DisplayList doesn't inherit from anything
DisplayList.hiddenClass = "hiddenElm";
DisplayList.columnIdPrefix = "column";
DisplayList.columnsDisplay = "Columns";
DisplayList.typesDisplay = "Types";

DisplayList.prototype.init = DL_init;
DisplayList.prototype.createDisplayChecks = DL_createDisplayChecks;
DisplayList.prototype.splitThId = DL_splitThId;
DisplayList.prototype.findDisplayCategories = DL_findDisplayCategories;
DisplayList.prototype.updateChildCheckboxes = DL_updateChildCheckboxes;
DisplayList.prototype.getTypeCheckLib = DL_getTypeCheckLib;
DisplayList.prototype.findDisplayChanges = DL_findDisplayChanges;
DisplayList.prototype.recordChanges = DL_recordChanges;
DisplayList.prototype.applyDisplayChanges = DL_applyDisplayChanges;
DisplayList.prototype.collectChanges = DL_collectChanges;
DisplayList.prototype.showChanges = DL_showChanges;
DisplayList.prototype.updateTableDisplay = DL_updateTableDisplay;
DisplayList.prototype.pickDisplayOption = DL_pickDisplayOption;
//******

//******
//init function for the DisplayList.
function DL_init(objErrors, strTableId, strIdPrefix, strDelimiter) {
	var strRoutine = "DL_init";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "setting form property";
		this.prefix = strIdPrefix;
		this.fullPrefix = strIdPrefix + "Display";

		this.dataTableId = strTableId; //I'm not getting the actual dataTable because, in BayesFold, it doesn't get added in until later ...
		this.displayListDiv = document.getElementById(this.fullPrefix + "List");
		this.currentStates = new Array();
		this.instantiated = false;
		this.displayOption = DisplayList.columnsDisplay;
		this.typesCheckboxes = undefined;
		this.delimiter = strDelimiter; //Public

		strAction = "creating the display palette object";
		this.palette = aggregate(new CollapsablePalette(this.errors, this.fullPrefix, undefined, this.createDisplayChecks), this);

		//strAction = "calling this.setUpdateFunction if necessary";
		//if (funcUpdateDisplayRecords != undefined) {this.setUpdateFunction(funcUpdateDisplayRecords, objFuncOwner);}
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end DL_init
//******

//******
//Public
function DL_createDisplayChecks() {
	var strRoutine = "DL_createDisplayChecks";
	var strAction = "";
	try {
		strAction = "returning immediately if this instantiation has already been done";
		if (this.instantiated == true) {return;}

		strAction = "getting the dataTable object with id " + this.dataTableId;
		var objDataTable = document.getElementById(this.dataTableId);

		strAction = "looping through each cell in the first row";
		var objFirstRow = objDataTable.rows[0];
		for (var intCellIndex = 0; intCellIndex < objFirstRow.cells.length; intCellIndex++) {
			var objParent = this.displayListDiv;

			strAction = "getting the current cell";
			var objCurCell = objFirstRow.cells[intCellIndex];

			strAction = "checking if cell's class is DisplayList.hiddenClass";
			var blnVisible = (objCurCell.className == DisplayList.hiddenClass) ? false : true;

			strAction = "putting cell's visibility status into the currentState array: " + blnVisible;
			this.currentStates[intCellIndex] = blnVisible;

			strAction = "calling this.splitThId";
			var arrCellCategories = this.splitThId(objCurCell);
			var strCurId = arrCellCategories[0];

			strAction = "if this column is not the select column";
			if (strCurId != "select") {
				strAction = "checking the length of the categories array";
				if (arrCellCategories.length > 1) {
					strAction = "calling findDisplayCategories";
					objParent = this.findDisplayCategories(arrCellCategories, objParent, blnVisible);
				} //end if

				strAction = "creating a new div for the column itself and appendchild it to the parent";
				var strColId = DisplayList.columnIdPrefix + this.delimiter + intCellIndex + this.delimiter + arrCellCategories[0];
				new DisplayCheck(objParent, strColId, objCurCell.innerText, this.prefix, blnVisible);
			} //end if cell id isn't "select"
		} //next cell

		strAction = "setting instantiated flag to true";
		this.instantiated = true;
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function createDisplayChecks
//******

//******
//Private
function DL_splitThId(objThCell) {
	var strRoutine = "DL_splitThId";
	var strAction = "";
	try {
		strAction = "cutting the seq/struct prefix off the id";
		var strCurId = objThCell.id.slice(this.prefix.length);

		strAction = "splitting the id";
		return strCurId.split(this.delimiter);
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_splitThId
//******

//******
//Private
function DL_findDisplayCategories(arrCellCategories, objParent, blnVisible) {
	var strRoutine = "DL_findDisplayCategories";
	var strAction = "";
	try {
		strAction = "going through the categories of the split in *reverse* order, stopping with second to last";
		for (var intCategoryIndex = arrCellCategories.length - 1; intCategoryIndex > 0; intCategoryIndex--) {
			strAction = "getting the current category";
			var strCategory = arrCellCategories[intCategoryIndex];

			strAction = "checking that the category is not empty";
			if (strCategory != "") {
				strAction = "looking for a div id-ed as current category under the current parent";
				//currently this will find something w/same name at ANY depth below current parent; should it be more specific?
				var objCurrentDiv = document.getElementById(this.prefix + strCategory);

				strAction = "checking if no div for the current category was found";
				if (objCurrentDiv == undefined) {
					strAction = "creating a new DisplayCheck to represent the category " + strCategory;
					objCurrentDiv = new DisplayCheck(objParent, strCategory, strCategory, this.prefix, blnVisible);
				} //end if

				strAction = "make current category div into parent";
				objParent = objCurrentDiv;
			} //end if category isn't empty
		} //next category

		//return parent
		return objParent;
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_findDisplayCategories
//******

//******
//Public
function DL_updateChildCheckboxes(objCurrentCheckbox) {
	var strRoutine = "DL_updateChildCheckboxes";
	var strAction = "";
	try {
		strAction = "getting the parent div of the current checkbox";
		var objParentDiv = objCurrentCheckbox.parentNode;

		strAction = "getting all the checkbox descendants of the current checkbox's parent";
		var objCheckboxDescendants = objParentDiv.getElementsByTagName("input");

		//collect the original currentval
		var strOldVal = this.palette.currentVal;

		strAction = "looping through each checkbox descendant";
		for (var intCheckboxIndex = 0; intCheckboxIndex < objCheckboxDescendants.length; intCheckboxIndex++) {
			strAction = "collecting the checkbox with index " + intCheckboxIndex;
			var objCurCheckbox = objCheckboxDescendants[intCheckboxIndex];

			if (objCurCheckbox != objCurrentCheckbox) {
				strAction = "manually collecting the currentVal for this checkbox";
				this.palette.setCurrentVal(objCurCheckbox);

				strAction = "making current checkbox's value the same as that of the selected checkbox";
				objCheckboxDescendants[intCheckboxIndex].checked = objCurrentCheckbox.checked;
			} else {
				//set the this.currentval back to the old value for this checkbox
				this.palette.currentVal = strOldVal;
			} //end if this isn't/is the checkbox that triggered this whole thing

			strAction = "manually registering a change on the current checkbox";
			this.palette.registerChangeOn(objCurCheckbox);
		} //next checkbox
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_updateChildCheckboxes
//******

//******
//Public
function DL_applyDisplayChanges() {
	var strRoutine = "DL_applyDisplayChanges";
	var strAction = "";
	try {
		strAction = "calling collectChanges";
		var arrChangedCols = this.collectChanges();

		strAction = "calling showChanges with the array of changed columns";
		this.showChanges(arrChangedCols);
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_applyDisplayChanges
//******

//******
//Public
function DL_collectChanges(arrOutputDisplayInfo) {
	var strRoutine = "DL_collectChanges";
	var strAction = "";
	try {
		strAction = "calling this.findDisplayChanges";
		var arrChangedCols = this.findDisplayChanges();

		strAction = "calling recordChanges";
		this.recordChanges(arrOutputDisplayInfo, arrChangedCols);

		return arrChangedCols;
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_collectChanges
//******


//******
//Public
function DL_showChanges(arrChangedCols) {
	var strRoutine = "DL_showChanges";
	var strAction = "";
	try {
		strAction = "calling updateTableDisplay with the array of changed columns";
		this.updateTableDisplay(arrChangedCols);

		strAction = "clear the changedfields list of the palette";
		this.palette.clearChangedFields();
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_showChanges
//******

//******
//Private
function DL_getTypeCheckLib() {
	var strRoutine = "DL_getTypeCheckLib";
	var strAction = "";
	try {
		if (this.typesCheckboxes == undefined) {
			this.typesCheckboxes = new Array();

			//getting an associative array of types checkbox objects, keyed by the type
			strAction = "getting the types fieldset with id " + this.fullPrefix + DisplayList.typesDisplay;
			var objTypesFieldset = document.getElementById(this.fullPrefix + DisplayList.typesDisplay);

			strAction = "getting an array of all the input elements inside the fieldset";
			var arrInputs = objTypesFieldset.getElementsByTagName("input");

			strAction = "looping through and entering each checkbox in array under its value";
			for (var intInputIndex = 0; intInputIndex < arrInputs.length; intInputIndex++) {
				var objCurCheckbox = arrInputs[intInputIndex];
				this.typesCheckboxes[objCurCheckbox.value] = objCurCheckbox;
			} //next
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_getTypeCheckLib
//******

//******
//Private
function DL_findDisplayChanges() {
	var strRoutine = "DL_findDisplayChanges";
	var strAction = "";
	try {
		//local variables
		var arrChangedCols = new Array();

		strAction = "calling this.getTypeCheckLib";
		this.getTypeCheckLib();

		strAction = "getting all checkboxes in displayListDiv";
		var objCheckboxDescendants = this.displayListDiv.getElementsByTagName("input");

		strAction = "looping through each checkbox";
		for (var intCheckboxIndex = 0; intCheckboxIndex < objCheckboxDescendants.length; intCheckboxIndex++) {
			strAction = "getting the current checkbox object";
			var objCurCheckbox = objCheckboxDescendants[intCheckboxIndex];

			strAction = "getting the id of the checkbox's parent object";
			var strParentId = objCurCheckbox.parentNode.id;

			strAction = "splitting the current id: " + strParentId;
			var arrIdSplit = strParentId.split(this.delimiter);

			strAction = "checking if the first item in the split is prefix + columnIdPrefix";
			if (arrIdSplit[0] == this.prefix + DisplayList.columnIdPrefix) {
				strAction = "getting the type checkbox object for the type of this column";
				var objTypeCheckbox = this.typesCheckboxes[arrIdSplit[2]];

				if (objTypeCheckbox != undefined) {
					strAction = "checking if displayoption is types";
					if (this.displayOption == DisplayList.typesDisplay) {
						strAction = "if the checkbox for this type is checked, making the checkbox for this column checked";
						if (objTypeCheckbox.checked) {objCurCheckbox.checked = true;}
					} else if (this.displayOption == DisplayList.columnsDisplay) {
						strAction = "if the checkbox for this column is unchecked, making the checkbox for this type unchecked";
						if (!objCurCheckbox.checked) {objTypeCheckbox.checked = false;}
					} //end if displayoption is columns/types
				} //end if there's a checkbox for this type

				strAction = "getting the column number out of the split array";
				var intColIndex = Number(arrIdSplit[1]);

				strAction = "collecting the current visibility state for column number " + intColIndex;
				var blnCurVisibility = this.currentStates[intColIndex];

				strAction = "checking if the current visibility state of the column is different from the 'checked' state of the current checkbox";
				if (blnCurVisibility != objCurCheckbox.checked) {
					strAction = "adding this column number to the changed array: " + intColIndex;
					arrChangedCols[intColIndex] = objCurCheckbox.checked;
				} //end if this column's visibility has changed
			} //end if this id starts with the column id prefix
		} //next checkbox

		//return the array of changed columns
		return arrChangedCols;
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_findDisplayChanges
//******

//******
//Private
function DL_recordChanges(arrDisplayIds, arrChangedCols) {
	var strRoutine = "DL_recordChanges";
	var strAction = "";
	try {
		//strAction = "check if there is an updateDisplayRecords function defined";
		//if (this.updateDisplayRecords != undefined) {
			//var arrDisplayIds = new Array();

			strAction = "getting the dataTable object with id " + this.dataTableId;
			var objDataTable = document.getElementById(this.dataTableId);

			strAction = "get the first row object";
			var objFirstRow = objDataTable.rows[0];

			strAction = "looping over every changed cell to get that cell's id";
			for (var intCellIndex in arrChangedCols) {
				strAction = "getting the current cell";
				var objCurCell = objFirstRow.cells[intCellIndex];

				strAction = "calling this.splitThId and entering result in arrDisplayIds";
				arrDisplayIds[intCellIndex] = this.splitThId(objCurCell);
			} //next cell

			//return arrDisplayIds;

			//strAction = "calling this.updateDisplayRecords on the function owner with " + this.prefix;
			//this.updateDisplayRecords.call(this.functionOwner, this.prefix, arrDisplayIds, arrChangedCols);
		//} //end if this.updateDisplayRecords isn't undefined
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_recordChanges
//******

//******
//Private
function DL_updateTableDisplay(arrChangedCols) {
	var strRoutine = "DL_updateTableDisplay";
	var strAction = "";
	try {
		strAction = "getting the dataTable object with id " + this.dataTableId;
		var objDataTable = document.getElementById(this.dataTableId);

		strAction = "looping through all table rows";
		for (var intRowIndex = 0; intRowIndex < objDataTable.rows.length; intRowIndex++) {
			strAction = "getting the row object with index " + intRowIndex;
			var objCurRow = objDataTable.rows[intRowIndex];

			strAction = "looping over each changed column";
			for (var intColIndex in arrChangedCols) {
				var strClassName;

				strAction = "getting the cell in column with index " + intColIndex;
				var objCurCell = objCurRow.cells[intColIndex];

				strAction = "switching on the value of the changed col to select the className";
				switch (arrChangedCols[intColIndex]) {
					case true:
						strClassName = ""; break;
					case false:
						strClassName = DisplayList.hiddenClass; break;
				} //end switch

				strAction = "resetting the classname for the changed column cell";
				objCurCell.className = strClassName;
			} //next changed column
		} //next row

		//now do one last loop to update the entries in the currentstates array
		strAction = "looping over each changed column";
		for (intColIndex in arrChangedCols) {
			strAction = "updating currentStates array to reflect change for col " + intColIndex;
			this.currentStates[intColIndex] = arrChangedCols[intColIndex];
		} //next changed column
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function DL_updateTableDisplay
//******

function DL_pickDisplayOption(objOptionRadio) {
	var strRoutine = "DL_pickDisplayOption";
	var strAction = "";
	try {
		strAction = "getting the radio button obj array";
		var arrRadios = objOptionRadio.form.elements[objOptionRadio.name];

		strAction = "going through each radio button option";
		for (var intRadioIndex = 0; intRadioIndex < arrRadios.length; intRadioIndex++) {
			strAction = "getting the current radio button option for index " + intRadioIndex;
			var objCurRadio = arrRadios[intRadioIndex];

			strAction = "if this radio button is checked, making its value the displayoption value";
			if (objCurRadio.checked) {this.displayOption = objCurRadio.value;}

			strAction = "getting the fieldset with id " + objCurRadio.value;
			var objCurFieldset = document.getElementById(this.fullPrefix + objCurRadio.value);

			strAction = "getting an array of all the input elements inside the fieldset";
			var arrInputs = objCurFieldset.getElementsByTagName("input");

			strAction = "looping through and setting disabled property for each input in fieldset";
			for (var intInputIndex = 0; intInputIndex < arrInputs.length; intInputIndex++) {
				arrInputs[intInputIndex].disabled = !objCurRadio.checked;
			} //next
		} //next option
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end DL_pickDisplayOption
//------------------------------------


//------------------------------------
//******
//Private constructor
function DisplayCheck(objParent, strId, strLabel, strPrefix, blnVisible) {
	var strRoutine = "DisplayCheck";
	var strAction = "";
	try {
		//local variables
		var objCurrentDiv;
		var strChecked = "";

		strAction = "creating a new div and appendchilding it to the parent";
		objCurrentDiv = document.createElement("div");
		objParent.appendChild(objCurrentDiv);

		strAction = "if column is visible, setting checked attribute";
		if (blnVisible) {strChecked = "checked = 'true'";}

		strAction = "setting new div's id, class, and innerhtml";
		objCurrentDiv.id = strPrefix + strId;
		objCurrentDiv.className = "displayCheck";
		objCurrentDiv.innerHTML = "<input type = 'checkbox' name = 'chk" + strPrefix + strId + "' " + strChecked + " onfocus = 'gobjMediator.setCurrentVal(\"" + strPrefix + "\", this);' onclick = 'gobjMediator.updateChildCheckboxes(\"" + strPrefix + "\", this);' /> " + strLabel + " <br />";

		return objCurrentDiv;
	} //end try
	catch(e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end DisplayCheck constructor
//******
//------------------------------------