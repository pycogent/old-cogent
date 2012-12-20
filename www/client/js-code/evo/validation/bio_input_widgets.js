/*
bio_input_widgets.js

Biology-related InputWidget subclasses used to validate form inputs.

Revision History:
Written 2003 by Amanda Birmingham
10/09/03 Amanda Birmingham: Removed the getFormValue method of InputName;
	have the InputWidget superclass to handle this work directly.  Renamed
	variables/private methods of functional classes to match guidelines.
10/10/03 Amanda Birmingham: added elm_id arg to constructor/input functions
	of InputName, InputTemperature, and InputAlignment to make them more
	reusable.
10/23/03 Amanda Birmingham: filled in InAlign_fill_err_msgs and
	InAlign_parse_lines
10/24/03 Amanda Birmingham: fixed bug in InAlign_fill_err_msgs; now correctly
	handles empty alignments. Changed filename to bio_info_widgets.  Added
	InputName_fill_err_msgs to fix bug that autocorrect wasn't being reached
	by validate.  Changed all instances of ._errorMsgs to ._error_msgs to
	comply with standards, and all instances of _fill_err_msgs to _fill_msgs
	since InputWidget can now do warning msgs, too.  Added
	InAlign_warn_bad_runs method to generate warning msg if alignment has
	too many gaps or degenerate bases to produce good results.
10/25/03 Amanda Birmingham: removed init method of InputName; now handled
	by InputWidget superclass ... same for InputAlignment. Added InputLabel
	class and started adding InputSequence
10/26/03 Amanda Birmingham: moved warning code out of InputAlignment and
	created a dummy _create_warnings functions; different uses of alignments
	have different warning conditions, and should override this.

from PyEvolve/iStringValidations uses normalizeString, startswith
from PyEvolve/input_tools uses InputWidget
from PyEvolve/alignment_parsers uses FastaParser, WhitespaceDelimitedParser
*/

//----------------------------------------------------------
//******
function InputName(errors_obj, elm_id) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id);
	} //end if
} //end InputName constructor

InputName.superclass = InputWidget.prototype;
InputName.prototype = new InputWidget(gstrPrototype);
InputName.prototype.constructor = InputName;
InputName.prototype._fill_msgs = function () {this.getFormValue();}
InputName.prototype._autocorrect = InputName_autocorrect;
//******

//******
function InputName_autocorrect(form_elm) {
	var method_name = "InputName_autocorrect";
	var curr_action = "";
	try {
		curr_action = "getting the value in the form";;
		var align_name = form_elm.value;

		curr_action = "checking if name is empty string";
		if (align_name == "") {
			curr_action = "creating new date and making it into a name";
			var curr_date = new Date();
			align_name = curr_date.toString() + " alignment";

			curr_action = "resetting form elm value to be new default name";
			form_elm.value = align_name;
		} //end if
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputName_autocorrect
//******
//----------------------------------------------------------


//----------------------------------------------------------
//******
function InputTemperature(errors_obj, elm_id) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id);
	} //end if
} //end InputTemperature constructor

InputTemperature.superclass = InputWidget.prototype;
InputTemperature.prototype = new InputWidget(gstrPrototype);
InputTemperature.prototype.constructor = InputTemperature;
InputTemperature.prototype.init = InputTemp_init;
InputTemperature.prototype.getFormValue = InputTemp_getFormValue;
InputTemperature.prototype._fill_msgs = InputTemp_fill_msgs;
//******

//******
//Public: init function for InputTemperature.
function InputTemp_init(errors_obj, elm_id) {
	var method_name = "InputTemp_init";
	var curr_action = "";
	setErrorsObj(this, errors_obj, method_name);

	try {
		curr_action = "calling the init of InputTemperature's superclass";
		InputTemperature.superclass.init.call(this, errors_obj, elm_id);
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputTemp_init
//******

//******
function InputTemp_getFormValue() {
	var method_name = "InputTemp_getFormValue";
	var curr_action = "";
	try {
		curr_action = "getting the temperature from the form";
		var temp_text = document.getElementById(this._formElmId).value;
		var temp_num = parseFloat(temp_text);
		return temp_num;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputTemp_getFormValue
//******

//******
function InputTemp_fill_msgs() {
	var method_name = "InputTemp_fill_msgs";
	var curr_action = "";
	try {
		curr_action = "getting the form value for this entry";
		var temperature = this.getFormValue();

		curr_action = "checking if the temperature is not a number";
		if (isNaN(temperature)) {
			this._error_msgs.push("Temperature must be a number.");
		} else {
			curr_action = "adding error if the temp isn't between 0 and 100";
			if ((temperature < 0) || (temperature > 100)) {
				this._error_msgs.push("Temperature must be between 0 and 100.");
			}
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputTemp_fill_msgs
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputPrimers(errors_obj) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj);
	} //end if
} //end InputPrimers constructor

InputPrimers.superclass = InputWidget.prototype;
InputPrimers.prototype = new InputWidget(gstrPrototype);
InputPrimers.prototype.constructor = InputPrimers;
InputPrimers.prototype.init = InputPrmrs_init;
//InputPrimers.prototype.getFormValue = InputPrmrs_getFormValue;
//InputPrimers.prototype._fillErrorMsgs = InputPrmrs_fillErrorMsgs;
//******

//******
//Public: init function for InputPrimers.
function InputPrmrs_init(errors_obj) {
	var method_name = "InputPrmrs_init";
	var curr_action = "";
	setErrorsObj(this, errors_obj, method_name);

	try {
		curr_action = "calling the init of InputPrimers' superclass";
		InputPrimers.superclass.init.call(this, errors_obj, "divPrimers", "divPrimerErrors", "", 0);

		this._children["3primer"] = new InputPrimer(this.errors, 3);
		this._children["5primer"] = new InputPrimer(this.errors, 5);
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputPrmrs_init
//******

//******
function InputPrmrs_validate() {
	var method_name = "InPrime_validate";
	var curr_action = "";
	try {
		//validate the primer children

		//get the primer children

		//if one but not both of them are blank,
			//create an error

	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function InputPrmrs_validate
//******

//******
//Private. returns false if there are errors in primers, true otherwise
function IM_validatePrimers() {
	var method_name = "IM_validatePrimers";
	var curr_action = "";
	try {
		var blnPrimersFilled;
		var arrPrimerErrors = new Array();
		var blnErrorFree = true;

		curr_action = "calling this.getPrimers";
		var arrPrimers = this.getPrimers();

		curr_action = "looping over primers array";
		for (var intPrimerEnd in arrPrimers) {
			curr_action = "getting the current primer";
			var strPrimer = arrPrimers[intPrimerEnd];

			curr_action = "checking whether the current primer has content";
			var blnCurPrimerFilled = true;
			if (strPrimer == "") {blnCurPrimerFilled = false;}

			curr_action = "checking whether we've determined the primer fill state yet";
			if (blnPrimersFilled != undefined) {
				curr_action = "checking whether the current primer matches the primer filled state";
				if (blnPrimersFilled != blnCurPrimerFilled) {
					curr_action = "adding an error because primer filled states don't match";
					arrPrimerErrors.push("Primers must be either both present or both absent.");
				} //end if
			} else {
				curr_action = "setting primer filled state";
				blnPrimersFilled = blnCurPrimerFilled;
			} //end if

			curr_action = "calling validatePrimer on " + strPrimer;
			this.validatePrimer(strPrimer, intPrimerEnd, arrPrimerErrors);
		} //next

		curr_action = "resetting primer errordiv html";
		document.getElementById("divPrimerErrors").innerHTML = this.generateErrors(arrPrimerErrors);

		if (arrPrimerErrors.length > 0 ) {blnErrorFree = false;}
		return blnErrorFree;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function IM_validatePrimers
//******

//******
//Private. returns an array holding 3' and 5' primers with indices 3 and 5 respectively
function IM_getPrimers() {
	var method_name = "IM_getPrimers";
	var curr_action = "";
	try {
		var arrPrimers = new Array();
		var arrPrimerEnds = new Array();
		arrPrimerEnds.push(3);
		arrPrimerEnds.push(5);

		//strange loop is just an easy way to get three and five
		curr_action = "getting the primers";
		for (var intPrimerIndex = 0; intPrimerIndex < arrPrimerEnds.length; intPrimerIndex++) {
			var intPrimerEnd = arrPrimerEnds[intPrimerIndex];

			curr_action = "getting the current primer's textbox object"
			var objPrimerTextbox = document.getElementById("txtPrimer" + intPrimerEnd);

			curr_action = "calling autoCorrectTxtbx and pushing outcome into return array";
			arrPrimers[intPrimerEnd] = this.autoCorrectTxtbx(objPrimerTextbox, true);
		} //next
		return arrPrimers;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function IM_getPrimers
//******

//******
//Private. Returns the total length of both primers added together.
function IM_getPrimerLength() {
	var method_name = "IM_getPrimerLength";
	var curr_action = "";
	try {
		//local variables
		var arrPrimers;
		var intPrimerLength = 0;

		curr_action = "calling this.getPrimers";
		arrPrimers = this.getPrimers();

		curr_action = "looping over the primers array";
		for (var intPrimerEnd in arrPrimers) {
			curr_action = "adding the length of this primer to the primer length total";
			intPrimerLength = intPrimerLength + arrPrimers[intPrimerEnd].length;
		} //next primer

		return intPrimerLength;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function IM_getPrimerLength
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputPrimer(errors_obj, intPrimerEnd) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, intPrimerEnd);
	} //end if
} //end InputPrimer constructor

InputPrimer.superclass = InputWidget.prototype;
InputPrimer.prototype = new InputWidget(gstrPrototype);
InputPrimer.prototype.constructor = InputPrimer;
InputPrimer.prototype.init = InputPrmrs_init;
InputPrimer.prototype._fillErrorMsgs = InputPrmr_fillErrorMsgs;
InputPrimer.prototype.getLength = InputPrmr_getLength;
//******

//******
//Public: init function for InputPrimer.
function InputPrmr_init(errors_obj, intPrimerEnd) {
	var method_name = "InputPrmr_init";
	var curr_action = "";
	setErrorsObj(this, errors_obj, method_name);

	try {
		//check that primerend is an integer, either three or five

		this.primerEnd = intPrimerEnd;

		curr_action = "calling the init of InputPrimers' superclass (InputWidget) to set up inherited properties";
		InputPrimers.superclass.init.call(this, errors_obj, "", "", "txtPrimer" + this.primerEnd, 0);
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputPrmr_init
//******

//******
//Public. Returns the length of the primer.
function InputPrmr_getLength() {
	var method_name = "InputPrmr_getLength";
	var curr_action = "";
	try {
		curr_action = "calling this.getFormValue";
		var strPrimer = this.getFormValue();

		curr_action = "returning the primer length";
		return strPrimer.length;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function InputPrmr_getLength
//******

//******
//Private.
function InputPrmr_fillErrorMsgs() {
	var method_name = "InputPrmr_fillErrorMsgs";
	var curr_action = "";
	try {
		curr_action = "getting the primer from the form";
		strPrimer = this.getFormValue();

		curr_action = "checking if the primer contains any characters other than agcu";
		var intSearchIndex = strPrimer.search(/[^agcu]/i);

		curr_action = "if primer contains something illegal, adding error";
		if (intSearchIndex != -1) {this._error_msgs.push(this.primerEnd + "' primer may contain only a,g,c, and u.");}
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function InputPrmr_fillErrorMsgs
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputAlignment(errors_obj, elm_id) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id);
	} //end if
} //end InputAlignment constructor

InputAlignment.superclass = InputWidget.prototype;
InputAlignment.prototype = new InputWidget(gstrPrototype);
InputAlignment.prototype.constructor = InputAlignment;
InputAlignment.prototype._autocorrect = InAlign_autocorrect;
InputAlignment.prototype._fill_msgs = InAlign_fill_msgs;
InputAlignment.prototype._check_empty = InAlign_check_empty;
InputAlignment.prototype._parse_lines = InAlign_parse_lines;
InputAlignment.prototype._create_warnings = function (record_data) {return;}
//******

//******
function InAlign_autocorrect(form_elm) {
	var method_name = "InAlign_autocorrect";
	var curr_action = "";
	try {
		curr_action = "getting the value in the form";;
		var align_text = form_elm.value;

		curr_action = "removing extra line breaks from the alignment text";
		align_text = align_text.replace(/(\r|\n)+\s*/g, "\n");

		curr_action = "writing the normalized value back to the textarea";
		form_elm.value = align_text;
		return align_text;
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InAlign_autocorrect
//******

//******
function InAlign_fill_msgs() {
	var method_name = "InAlign_fill_msgs";
	var curr_action = "";
	try {
		//local variables
		var input_text, input_lines;

		curr_action = "getting the form value";
		input_text = this.getFormValue();

		curr_action = "calling _check_empty";
		is_empty = this._check_empty(input_text);

		curr_action = "spliting the input_text if it isn't empty";
		if (!is_empty) {
			input_lines = input_text.split(/\n/);

			curr_action = "calling _parse_lines";
			record_data = this._parse_lines(input_lines);

			curr_action = "calling _create_warnings";
			this._create_warnings(record_data);
		} //end if the input isn't empty

		curr_action = "setting the validatedData if there are no errors";
		if (this._error_msgs.length == 0) {this.validatedData = record_data;}
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InAlign_fill_msgs
//******

//******
function InAlign_check_empty(input_text) {
	var method_name = "InAlign_check_empty";
	var curr_action = "";
	try {
		is_empty = false;

		//if that string is empty or has only whitespace-type things,
		//throw an error telling them they need to do better than that
		curr_action = "making sure alignment is not empty";
		if (normalizeString(input_text) == "") {
			is_empty = true;
			error_msg = "Please enter an alignment.";
			this._error_msgs.push(error_msg);
		} //end if input is empty

		return is_empty
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InAlign_check_empty
//******

//******
function InAlign_parse_lines(input_lines) {
	var method_name = "InAlign_parse_lines";
	var curr_action = "";
	try {
		parse_class = WhitespaceDelimitedParser;

		curr_action = "switching to fasta parser if necessary";
		fasta_char = FastaParser.prototype.FASTA_LABEL_CHAR;
		if (input_lines[0].startswith(fasta_char)) {
			parse_class = FastaParser;
		} //end if input is in FASTA format

		//create the correct parser and call parse
		parser = new parse_class(this.errors);
		record_data = parser.parse(input_lines);

		//get the error msgs and put into this._error_msgs
		this._error_msgs = this._error_msgs.concat(parser.getErrorMsgs());
		return record_data;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InAlign_parse_lines
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputLabel(errors_obj, elm_id, index) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id, index);
	} //end if
} //end InputName constructor

InputLabel.superclass = InputWidget.prototype;
InputLabel.prototype = new InputWidget(gstrPrototype);
InputLabel.prototype.constructor = InputLabel;
InputLabel.prototype.init = InputLabel_init;
InputLabel.prototype._fill_msgs = function () {this.getFormValue();}
InputLabel.prototype._autocorrect = InputLabel_autocorrect;
//******

//******
function InputLabel_init(errors_obj, elm_id, index) {
	var method_name = "InputLabel_init";
	var curr_action = "";
	setErrorsObj(this, errors_obj, method_name);

	try {
		if (index == undefined) {throw new Error("Index parameter is undefined");}
		this._index = String(index);

		curr_action = "calling the init of InputName's superclass";
		InputName.superclass.init.call(this, errors_obj, elm_id);
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputLabel_init
//******

//******
function InputLabel_autocorrect(form_elm) {
	var method_name = "InputLabel_autocorrect";
	var curr_action = "";
	try {
		curr_action = "getting the value in the form";;
		var label_text = form_elm.value;

		curr_action = "checking if label is empty string";
		if (label_text == "") {
			curr_action = "creating a new label and putting in form";
			label_text = "sequence " + this._index;
			form_elm.value = label_text;
		} //end if
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputLabel_autocorrect
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputSequence(errors_obj, elm_id) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id);
	} //end if
} //end InputSequence constructor

InputSequence.superclass = InputWidget.prototype;
InputSequence.prototype = new InputWidget(gstrPrototype);
InputSequence.prototype.constructor = InputSequence;
InputSequence.prototype._autocorrect = InputSeq_autocorrect;
InputSequence.prototype._fill_msgs = InputSeq_fill_msgs;
InputSequence.prototype._delete_extra_gaps = InputSeq_delete_extra_gaps;

InputSequence.prototype.GAP_CHAR = "-";
InputSequence.prototype.MAX_LENGTH = 150;
//******

//******
//Private.  Takes in a textbox, calls normalizeString and turnTtoU on value.
//Puts the new value into textbox and returns modified value.
function InputSeq_autocorrect(form_elm) {
	var method_name = "InputSeq_autocorrect";
	var curr_action = "";
	try {
		curr_action = "getting the string in the textbox object";
		var seq_text = form_elm.value;

		curr_action = "calling normalizeString on " + seq_text
		seq_text = normalizeString(seq_text);

		curr_action = "change any t's to u's";
		seq_text = turnTtoU(seq_text);

		curr_action = "change any of ._~ or space to -";
		seq_text = seq_text.replace(/[._~ ]/g, this.GAP_CHAR);

		curr_action = "remove any extra gaps";
		seq_text = this._delete_extra_gaps(seq_text);

		curr_action = "uppercasing the sequence"
		seq_text = strText.toUpperCase();

		curr_action = "putting updated string back in textbox";
		form_elm.value = seq_text;

		return seq_text;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputSeq_autocorrect
//******

//******
function InputSeq_delete_extra_gaps(seq_text) {
	var method_name = "InputSeq_delete_extra_gaps";
	var curr_action = "";
	try {
		var strSequence = objEntry.sequence;

		//read the number of prefixing and suffixing gaps
		//create a regexp for the gap character
		var objGapRe = new RegExp("(" + gstrGapChar + "*)[^" + gstrGapChar + "].*[^" + gstrGapChar + "](" + gstrGapChar + "*)");

		curr_action = "counting how many gap characters are at the beginning and end of the sequence";
		var arrMatchResults = strSequence.match(objGapRe);
		if (arrMatchResults == null) {arrMatchResults = new Array(0,0);}

		curr_action = "looping over the prefix and suffix gap counts";
		for (var intIndex = 0; intIndex < this.extraGaps.length; intIndex++) {
			curr_action = "getting the length of the gap match for this index + 1";
			//add one because the *first* index will always contain the whole string, if
			//any match was found.
			var intCurGaps = arrMatchResults[intIndex + 1].length;

			curr_action = "checking if the current gap count is less than the preexisting one";
			if (intCurGaps < this.extraGaps[intIndex]) {
				curr_action = "replacing the existing gap count with the new one";
				this.extraGaps[intIndex] = intCurGaps;
			} //end if
		} //next gap measure
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputSeq_delete_extra_gaps
//******

//******
function InputSeq_fill_msgs() {
	var method_name = "InputSeq_fill_msgs";
	var curr_action = "";
	try {
		//local variables
		var input_text, is_valid;

		curr_action = "getting the form value";
		input_text = this.getFormValue();

		curr_action = "calling containsOnlySpecial characters on sequence " + strSequence;
		is_valid = containsOnlySpecialCharacters(strSequence, "ACGUN-");

		curr_action = "if sequence is invalid, adding an error to entry";
		if (!is_valid) {objEntry.errors.push("Sequence may contain only ACGNU and/or hyphens, and may not be empty.");}

		curr_action = "call this.validateSeqLength"
		this.validateSeqLength(objEntry, this.seqLength);
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputSeq_fill_msgs
//******

//******
//Private.
function IM_validateSeqLength(objEntry, intSeqLength) {
	var method_name = "IM_validateSeqLength";
	var curr_action = "";
	try {
		//local variable
		var intTotalLength = intSeqLength;

		curr_action = "call this.getPrimerLength and add to total length";
		intTotalLength += this.getPrimerLength();

		curr_action = "if the sequence length is longer than the max allowed, add an error"
		if (intTotalLength > InputMediator.MAX_SEQLENGTH) {
			objEntry.errors.push("Sequence may be only " + InputMediator.MAX_SEQLENGTH + " bases long, including primers.");
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end function IM_validateSeqLength
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function InputBasicSeq(errors_obj, elm_id, elm_name) {
	if (errors_obj != gstrPrototype) {
		this.module = "bio_input_widgets";
		this.init(errors_obj, elm_id, elm_name);
	} //end if
} //end InputSequence constructor

InputBasicSeq.superclass = InputWidget.prototype;
InputBasicSeq.prototype = new InputWidget(gstrPrototype);
InputBasicSeq.prototype.constructor = InputBasicSeq;
InputBasicSeq.prototype._autocorrect = InputBasicSeq_autocorrect;
InputBasicSeq.prototype._fill_msgs = InputBasicSeq_fill_msgs;

InputBasicSeq.prototype.ALLOWED_CHARS = "ACGTU "
InputBasicSeq.prototype.MAX_LENGTH = 150;
//******

//******
//Private.  Takes in a textbox, calls normalizeString and turnTtoU on value.
//Puts the new value into textbox and returns modified value.
function InputBasicSeq_autocorrect(form_elm) {
	var method_name = "InputBasicSeq_autocorrect";
	var curr_action = "";
	try {
		curr_action = "getting the string in the textbox object";
		var seq_text = form_elm.value;

		curr_action = "calling normalizeString on " + seq_text;
		seq_text = normalizeString(seq_text);

		curr_action = "removing commas";
		seq_text = seq_text.replace(/,/g, "");

		curr_action = "uppercasing the sequence"
		seq_text = seq_text.toUpperCase();

		curr_action = "putting updated string back in textbox";
		form_elm.value = seq_text;

		return seq_text;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputBasicSeq_autocorrect
//******

//******
function InputBasicSeq_fill_msgs() {
	var method_name = "InputBasicSeq_fill_msgs";
	var curr_action = "";
	try {
		//local variables
		var input_text, is_valid;

		curr_action = "getting the form value";
		input_text = this.getFormValue();

		if (input_text != "") {
			curr_action = "calling containsOnlySpecial characters on sequence " + input_text;
			is_valid = containsOnlySpecialCharacters(input_text, this.ALLOWED_CHARS);

			curr_action = "if sequence is invalid, adding an error to entry";
			if (!is_valid) {this._error_msgs.push(this._elm_name + "may contain only " + this.ALLOWED_CHARS + ".");}
		} //end if
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end InputBasicSeq_fill_msgs
//******
//----------------------------------------------------------