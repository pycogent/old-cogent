/*
input_tools.js

Objects to automate form validation.  InputWidget (the basic validation
element), InputErrDisplayer (which handles the screen display of errors
generated by one or more widgets), and InputMediator (a generic mediator
for form validation and submission).

Revision History:
Written 2003 by Amanda Birmingham
10/09/03 Amanda Birmingham: altered InputWidget_getFormValue so that it
	calls _autocorrect on input before returning value.  Added an
	_autocorrect stub that does nothing.  Renamed private methods to
	conform to guidelines.
10/13/03 Amanda Birmingham: altered signature of autocorrect: may now
	return corrected value.  Altered getFormValue so that it returns
	the value returned from _autocorrect if there is one and otherwise
	returns the value in the form.
10/23/03 Amanda Birmingham: added an optional screen_id parameter to the
	InputErrDisplayer init, w/default 0. Stored in public ScreenId property.
10/24/03 Amanda Birmingham: branched from BayesFold 1.0 code.  Changed
	file name from input_tools to input_tools.  Changed errorLessHtml
	property of InputErrDisplayer to ErrorlessHtml to match conventions.
	Added generalized InputMediator class culled from bfInputMediator.
	Moved screen_id property out of InputErrDisplayer and put it in
	InputWidget, renamed it ScreenNum.  Added new functionality to
	InputWidget: can now collect BOTH error AND warning msgs; will report
	errors first and warnings only when no errors are found. This change
	includes significant changes to interface: _fill_err_msgs became
	_fill_msgs, ditto _reset_err_msgs; _collect_msgs was added; public
	updateErrorMsgs method became updateMsgs.  Altered implementation of
	updateMsgs to handle warnings, too, and added _build_warning method.
10/25/03 Amanda Birmingham: added addChildren method to InputWidget
01/12/04 Amanda Birmingham: added validate and continue button id params to
	InputMediator object.  Altered refreshValidateBtn method so it only
	attempts to modify state of buttons if ids exist for them.  Started
	filling in continue function.
01/27/04 Amanda Birmingham: added InputPercent, InputNonnegNum, and
	InputPosNum classes


uses error_handler.js
from general_tools uses importInterfaces
*/

//----------------------------------------------------------
//******
function InputWidget(objErrors, strFormElmId, elm_name, screen_num) {
	if (objErrors != gstrPrototype) {
		this.module = "input_tools";
		this.init(objErrors, strFormElmId, elm_name, screen_num);
	} //end if
} //end InputWidget constructor

//Shared methods:
InputWidget.prototype.init = InWidget_init;
InputWidget.prototype.getFormValue = InWidget_getFormValue; //there is a default implementation, suitable for simple textboxes
InputWidget.prototype.validate = InWidget_validate;
InputWidget.prototype.updateMsgs = InWidget_updateMsgs;
InputWidget.prototype.getValidatedData = function () {return this.validatedData;}
InputWidget.prototype._collect_msgs = InWidget_collect_msgs;
InputWidget.prototype._reset_msgs = function () {
										this._error_msgs = new Array();
										this._warning_msgs = new Array();
										this.validatedData = undefined;
									}; //end _reset_msgs
InputWidget.prototype.addChildren = function () {
										for (var i = 0; i < arguments.length; i++) {
											this._children.push(arguments[i]);
										} //next argument
									}; //end addChildren

//To be overridden by subclasses:
InputWidget.prototype._fill_msgs = function () {return;}; //the simplest objects don't have fillErrorMsgs, so let this be inherited
InputWidget.prototype._autocorrect = function () {return;};
//******

//******
//Public
//InputWidget init function (used by all of InputWidget's subclasses)
function InWidget_init(objErrors, strFormElmId, elm_name, screen_num) {
	var method_name = "InWidget_init";
	var curr_action = "";
	setErrorsObj(this, objErrors, method_name);

	try {
		curr_action = "validating the datatype of input";
		if (strFormElmId != undefined) {strFormElmId = String(strFormElmId);}
		if (screen_num == undefined) {screen_num = 0;}
		screen_num = Math.abs(parseInt(screen_num));
		if (isNaN(screen_num)) {
			throw new Error("Parameter screen_num must be castable to a nonnegative integer");
		} //end if screen_num isn't a number

		curr_action = "setting properties";
		this._children = new Array();
		this.ScreenNum = screen_num;
		//Not everything will have a meaningful formElmId
		this._formElmId = strFormElmId;

		if (elm_name == undefined) {
			elm_name = "";
		} else {
			elm_name = elm_name + " ";
		} //end if elm_name is/isn't undefined
		this._elm_name = elm_name;

		curr_action = "calling this._reset_msgs";
		this._reset_msgs();
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InWidget_init
//******

//******
function InWidget_getFormValue() {
	var method_name = "InWidget_getFormValue";
	var curr_action = "";
	try {
		var strReturnValue = undefined;

		if (this._formElmId) {
			curr_action = "getting the value in the form";
			var objFormElm = document.getElementById(this._formElmId);

			curr_action = "calling autocorrect on the form value";
			strReturnValue = this._autocorrect(objFormElm);

			curr_action = "getting form value if autocorrect didn't return one";
			if (strReturnValue == undefined) {
				strReturnValue = objFormElm.value;
			} //end if
		} //end if

		return strReturnValue;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InWidget_getFormValue
//******


//******
//Public.  Collects all error and warning msgs that relate to this object,
//and to any children that haven't already had their messages
//collected.  Returns dictionary of error and warning messages.
function InWidget_updateMsgs() {
	var method_name = "InWidget_updateMsgs";
	var curr_action = "";
	try {
		//local variables
		var error_msgs, warning_msgs;
		var result = new Array();

		//collect all the errors and all the warnings
		result["errors"] = this._collect_msgs(true);
		result["warnings"] = this._collect_msgs(false);

		curr_action = "clearing own msgs, since they have now been reported";
		this._reset_msgs();

		return result;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InWidget_updateMsgs
//******

//******
//Private: collects all the messages of a given type (error or warning)
//from all uncollected children and self, then returns them.
function InWidget_collect_msgs(get_errors) {
	var method_name = "InWidget_collect_msgs";
	var curr_action = "";
	try {
		//local variables
		var curr_child, child_msgs;
		var collected_msgs = new Array();
		if (get_errors == undefined) {get_errors = true};

		curr_action = "looping over each child";
		for (var child_name in this._children) {
			curr_action = "calling _collect_msgs on each child";
			curr_child = this._children[child_name];
			child_msgs = curr_child._collect_msgs(get_errors);

			curr_action = "adding that child's messages to the collected list";
			for (var msg_index in child_msgs) {
				collected_msgs.push(child_msgs[msg_index]);
			} //next child msg
		} //next child

		curr_action = "add the msgs from this object itself";
		local_msgs = this._error_msgs;
		if (get_errors == false) {local_msgs = this._warning_msgs;}
		for (msg_index in local_msgs) {
			collected_msgs.push(local_msgs[msg_index]);
		} //next local msg

		return collected_msgs;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InWidget_collect_msgs
//******

//******
function InWidget_validate() {
	var method_name = "InWidget_validate";
	var curr_action = "";
	try {
		//start by assuming no errors
		var blnErrorFree = true;

		curr_action = "resetting the errors array";
		this._reset_msgs();

		curr_action = "looping over each child";
		for (var strChildKey in this._children) {
			curr_action = "calling validate on each child";
			var blnValidChild = this._children[strChildKey].validate();
			if (!blnValidChild) {blnErrorFree = false;}
		} //next child

		curr_action = "calling this._fill_msgs";
		this._fill_msgs();

		curr_action = "checking the number of errors";
		if (this._error_msgs.length > 0) {blnErrorFree = false;}
		return blnErrorFree;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InWidget_validate
//******
//----------------------------------------------------------

//----------------------------------------------------------
//InputErrDisplayer
//An object that displays errors collected for an input element (represented as InputWidget).
//InputErrDisplayer is a *decorator* class of the InputWidget class (see GoF patterns.)  It
//implements the basic interface of InputWidget by forwarding all requests for those functions
//to its private InputWidget object.
//******
//Public: InputErrDisplayer constructor.
//Returns new InputErrDisplayer object.
function InputErrDisplayer(objErrors, objInputWidget, strErrorElmId) {
	if (objErrors != gstrPrototype) {
		this.module = "input_tools";
		this.init(objErrors, objInputWidget, strErrorElmId);
	} //end if
} //end InputErrDisplayer constructor

InputErrDisplayer.prototype.init = InErrDisp_init;
InputErrDisplayer.prototype.updateMsgs = InErrDisp_updateMsgs;
InputErrDisplayer.prototype._htmlize_err_msgs = InErrDisp_htmlize_err_msgs;
InputErrDisplayer.prototype._refresh_error_div = InErrDisp_refresh_error_div;
InputErrDisplayer.prototype._build_warning = InErrDisp_build_warning

InputErrDisplayer.prototype.ErrorlessHtml = "<br />";
//******

//******
//Public
//InputErrDisplayer init function
function InErrDisp_init(objErrors, objInputWidget, strErrorElmId) {
	var method_name = "InErrDisp_init";
	var curr_action = "";
	setErrorsObj(this, objErrors, method_name);

	try {
		curr_action = "validating the inputs";
		if ((objInputWidget == undefined) || (objInputWidget.updateMsgs == undefined)) {throw new Error("Parameter objInputWidget is not an inputwidget");}
		if (typeof strErrorElmId != "string") {throw new Error("Parameter strErrorElmId is not a string");}

		curr_action = "storing the inputwidget in a private variable"
		this._inputWidget = objInputWidget;

		//since this class is a Decorator of the InputWidget, import InputWidget's (public) interface
		importInterfaces(this, this._inputWidget, "_inputWidget");

		curr_action = "setting the errorElmId property";
		this._errorElmId = strErrorElmId;
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InErrDisp_init
//******

//******
//Public.  Collects all error msgs that relate to this object,
//and to any children that haven't already had their errors
//collected.  If this object has a valid errorElmId, puts those
//collected errors into that error elm.
function InErrDisp_updateMsgs() {
	var method_name = "InErrDisp_updateMsgs";
	var curr_action = "";
	try {
		//local variables
		var msgs_by_categ, warning_text, error_html;

		curr_action = "calling updateMsgs on the private inputwidget";
		msgs_by_categ = this._inputWidget.updateMsgs();

		curr_action = "calling htmlizeErrorMsgs on self";
		error_html = this._htmlize_err_msgs(msgs_by_categ["errors"]);

		curr_action = "calling refreshErrorDiv";
		this._refresh_error_div(error_html);

		curr_action = "calling _build_warning";
		warning_text = this._build_warning(msgs_by_categ["warnings"]);
		if (warning_text != undefined) {alert(warning_text);}
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InErrDisp_updateMsgs
//******

//******
//Private
function InErrDisp_htmlize_err_msgs(arrErrorMsgs) {
	var method_name = "InErrDisp_htmlize_err_msgs";
	var curr_action = "";
	try {
		//local variables
		var strEntryHtml = "";

		curr_action = "checking if any errors exist for this entry";
		if (arrErrorMsgs.length > 0) {
			curr_action = "looping through all errors for this entry";
			for (var intErrorIndex = 0; intErrorIndex < arrErrorMsgs.length; intErrorIndex++) {
				curr_action = "putting the error html into the entry html";
				strEntryHtml = strEntryHtml + "<span style = 'color:red;'>" + arrErrorMsgs[intErrorIndex] + "</span><br />";
			} //next error
		} //end if

		return strEntryHtml;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InErrDisp_htmlize_err_msgs
//******

//******
//Private.  If this object has a valid errorElmId, puts input
//collected errors into that error elm.
function InErrDisp_refresh_error_div(strErrorHtml) {
	var method_name = "InErrDisp_refresh_error_div";
	var curr_action = "";
	try {
		curr_action = "getting the error element";
		var objErrorDiv = document.getElementById(this._errorElmId);

		curr_action = "making the error html this.ErrorlessHtml if none were found";
		if (strErrorHtml == "") {strErrorHtml = this.ErrorlessHtml;}

		curr_action = "resetting errordiv html";
		objErrorDiv.innerHTML = strErrorHtml;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InErrDisp_refresh_error_div
//******

//******
function InErrDisp_build_warning(warning_msgs) {
	var method_name = "InErrDisp_build_warning";
	var curr_action = "";
	try {
		//local variables
		var warning_string;

		//display the warning messages, if there are any
		if (warning_msgs.length > 0) {
			warning_string = "Warning:\n" + warning_msgs.join("\n");
		} //end if there were warnings

		return warning_string;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InErrDisp_build_warning
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputMediator(errors_obj, screen_pieces, continue_id, validate_id) {
	if (errors_obj != gstrPrototype) {
		this.module = "input_tools";
		this.init(errors_obj, screen_pieces, continue_id, validate_id);
	} //end if
} //end InputMediator constructor

InputMediator.prototype.init = IM_init;
InputMediator.prototype.validate = IM_validate;
//Note that following function is named step, not continue, because (although
//continue might make more sense, it is a reserved word in JavaScript).
InputMediator.prototype.continueForm = IM_continue;
InputMediator.prototype.refreshValidateBtn = IM_refreshValidateBtn;
InputMediator.prototype._show_hide_pieces = IM_show_hide_pieces;
//******

//******
//Public: InputMediator init function
function IM_init(errors_obj, screen_pieces, continue_id, validate_id) {
	var method_name = "IM_init";
	var curr_action = "";
	setErrorsObj(this, errors_obj, method_name);

	try {
		this._screen_pieces = screen_pieces;
		this._current_screen = 0;
		this._continue_id = continue_id;
		this._validate_id = validate_id;
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end IM_init
//******

//******
function IM_validate() {
	var method_name = "IM_validate";
	var curr_action = "";
	try {
		//local variables
		var curr_piece, piece_is_valid;

		curr_action = "start by assuming no errors";
		var screen_not_valid = false;

		//for each screen piece
		for (var piece_name in this._screen_pieces) {
			curr_action = "get the current piece";
			curr_piece = this._screen_pieces[piece_name];

			curr_action = "checking if current piece is a member of the current screen";
			if (curr_piece.ScreenNum == this._current_screen) {
				curr_action = "calling validate on current piece";
				piece_is_valid = curr_piece.validate();

				curr_action = "if validate returns false, haserrors is true";
				if (!piece_is_valid) {screen_not_valid = true;}

				curr_action = "calling updateMsgs on member";
				curr_piece.updateMsgs();
			} //end if piece is on this screen
		} //next piece

		curr_action = "calling refreshValidateBtn";
		this.refreshValidateBtn(screen_not_valid);

		curr_action = "returning true if no errors are detected";
		return !screen_not_valid;
	} //end try
	catch(e) {
		showMainErrors(method_name, curr_action, e);
	} //end catch
} //end IM_validate
//******

//******
//Public
function IM_refreshValidateBtn(validate_required) {
	var method_name = "IM_refreshValidateBtn";
	var curr_action = "";
	try {
		if (validate_required == undefined) {validate_required = true;}
		if (typeof validate_required != "boolean") {throw new Error("Parameter validate_required must be boolean");}

		if (this._validate_id) {
			curr_action = "enable/disable the validate button";
			validate_btn = document.getElementById(this._validate_id);
			validate_btn.disabled = !validate_required;
		} //end if there is a validate id

		if (this._continue_id) {
			curr_action = "enable/disable the continue button";
			var continue_btn = document.getElementById(this._continue_id);
			continue_btn.disabled = validate_required;
		} //end if there is a continue id
	} //end try
	catch(e) {
		//alert(method_name + ": " + curr_action + ", " + e.message);
		showMainErrors(method_name, curr_action, e);
	} //end catch
} //end function IM_refreshValidateBtn
//******

//******
function IM_show_hide_pieces(blnHide) {
	var method_name = "IM_show_hide_pieces";
	var curr_action = "";
	try {
		//for each piece
			//if it is a member of the current screen
				//call hide on it or show on it
			//end if
		//next piece
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end IM_show_hide_pieces
//******


//******
//Public
function IM_continue() {
	var method_name = "IM_continue";
	var curr_action = "";
	try {
		var result = false;

		curr_action = "calling this.validate";
		var is_valid = this.validate();

		if (is_valid) {
			//if screen number is less than max screen number
				//increment the screen number
				//call hide on old screen elements
				//change current screen
				//call show on new screen elements
			//else
				  result = true;
			//end if
		} //end if current screen is valid

		return result;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function IM_continue
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputNonnegNum(errors_obj, elm_id, elm_name) {
	if (errors_obj != gstrPrototype) {
		this.module = "input_widgets";
		this.init(errors_obj, elm_id, elm_name);
	} //end if
} //end InputNonnegNum constructor

InputNonnegNum.superclass = InputWidget.prototype;
InputNonnegNum.prototype = new InputWidget(gstrPrototype);
InputNonnegNum.prototype.constructor = InputNonnegNum;
InputNonnegNum.prototype.getFormValue = InputNonneg_getFormValue;
InputNonnegNum.prototype._fill_msgs = InputNonneg_fill_msgs;
//******

//******
function InputNonneg_getFormValue() {
	var method_name = "InputNonneg_getFormValue";
	var curr_action = "";
	try {
		curr_action = "getting the number value for " + this._formElmId;
		var temp_text = document.getElementById(this._formElmId).value;
		var temp_num = parseFloat(temp_text);
		return temp_num;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputNonneg_getFormValue
//******

//******
function InputNonneg_fill_msgs() {
	var method_name = "InputNonneg_fill_msgs";
	var curr_action = "";
	try {
		curr_action = "getting the form value for " + this._formElmId;
		var input_val = this.getFormValue();

		curr_action = "checking if the input is not a number";
		if (isNaN(input_val)) {
			this._error_msgs.push(this._elm_name + "must be a number.");
		} else if (input_val < 0) {
			this._error_msgs.push(this._elm_name + "must be zero or greater");
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputNonneg_fill_msgs
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputPosNum(errors_obj, elm_id, elm_name) {
	if (errors_obj != gstrPrototype) {
		this.module = "input_widgets";
		this.init(errors_obj, elm_id, elm_name);
	} //end if
} //end InputPosNum constructor

InputPosNum.superclass = InputNonnegNum.prototype;
InputPosNum.prototype = new InputNonnegNum(gstrPrototype);
InputPosNum.prototype.constructor = InputPosNum;
InputPosNum.prototype._fill_msgs = InputPosNum_fill_msgs;
//******

//******
function InputPosNum_fill_msgs() {
	var method_name = "InputPercent_fill_msgs";
	var curr_action = "";
	try {
		curr_action = "getting the form value for " + this._formElmId;
		var input_val = this.getFormValue();

		curr_action = "checking if the input is not a number";
		if (isNaN(input_val)) {
			this._error_msgs.push(this._elm_name + "must be a number.");
		} else if (input_val <= 0) {
			this._error_msgs.push(this._elm_name + "must be greater than zero");
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputPosNum_fill_msgs
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputPercent(errors_obj, elm_id, elm_name) {
	if (errors_obj != gstrPrototype) {
		this.module = "input_widgets";
		this.init(errors_obj, elm_id, elm_name);
	} //end if
} //end InputPercent constructor

InputPercent.superclass = InputNonnegNum.prototype;
InputPercent.prototype = new InputNonnegNum(gstrPrototype);
InputPercent.prototype.constructor = InputPercent;
InputPercent.prototype._fill_msgs = InputPercent_fill_msgs;
//******

//******
function InputPercent_fill_msgs() {
	var method_name = "InputPercent_fill_msgs";
	var curr_action = "";
	try {
		curr_action = "getting the form value for " + this._formElmId;
		var input_val = this.getFormValue();

		curr_action = "checking if the input is not a number";
		if (isNaN(input_val)) {
			this._error_msgs.push(this._elm_name + "must be a number.");
		} else if ((input_val < 0) || (input_val > 100)) {
				this._error_msgs.push(this._elm_name + "must be between 0 and 100.");
		} //end if the input is incorrect
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputPercent_fill_msgs
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputRange(errors_obj) {
	if (errors_obj != gstrPrototype) {
		this.module = "input_widgets";
		this.init(errors_obj);
	} //end if
} //end InputRange constructor

InputRange.superclass = InputWidget.prototype;
InputRange.prototype = new InputWidget(gstrPrototype);
InputRange.prototype.constructor = InputRange;
InputRange.prototype.addChildren = InputRange_addChildren;
InputRange.prototype._fill_msgs = InputRange_fill_msgs;
//******

//******
function InputRange_addChildren(min_widget, max_widget) {
	var method_name = "InputRange_addChildren";
	var curr_action = "";
	try {
		curr_action = "setting min and max children";
		this._children["min"] = min_widget;
		this._children["max"] = max_widget;
	} catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputRange_addChildren
//******

//******
function InputRange_fill_msgs() {
	var method_name = "InputRange_fill_msgs";
	var curr_action = "";
	try {
		curr_action = "getting the form value for min and max";
		var min_val = this._children["min"].getFormValue();
		var max_val = this._children["max"].getFormValue();

		curr_action = "checking max is greater than min";
		if (max_val < min_val) {
			this._error_msgs.push("Minimum must be less than or equal to maximum.");
		} //end if max less than min
	} catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputRange_fill_msgs
//******
//----------------------------------------------------------