/*
alignment_parsers.js

Parser objects for common alignment formats.

Revision History:
10/13/03 Amanda Birmingham: started to hold FastaParser that grew out of
	InputAlignment widget
10/22/03 Amanda Birmingham: altered so that _sequence_data holds starting
	line number (base 0) of record (ie, label), rather than sequence. Added
	getErrorMsgs and getRecordData methods
10/23/03 Amanda Birmingham: added AlignmentParser and
	WhitespaceDelimitedParser classes
10/24/03 Amanda Birmingham: altered AlParser_store_record so that it creates
	a dictionary instead of a list


from iStringValidations uses startswith
*/

//----------------------------------------------------------
/* 	AlignmentParser is an abstract class: it has some real methods,
	but it shouldn't be instantiate on its own.
*/

//******
function AlignmentParser(errors_obj) {
	if (errors_obj != gstrPrototype) {
		this.module = "alignment_parsers";
		this.init(errors_obj);
	} //end if
} //end AlignmentParser constructor

//Shared methods
AlignmentParser.prototype.init = AlParser_init;
AlignmentParser.prototype.getErrorMsgs =
	function() {return this._error_msgs.slice();}
AlignmentParser.prototype.getRecordData =
	function () {return this._sequence_data.slice();}
AlignmentParser.prototype._reset_state = AlParser_reset_state;
AlignmentParser.prototype._store_record = AlParser_store_record;

//Abstract methods--must be overridden
//AlignmentParser.prototype.parse = AlParser_parse;
//******

//******
function AlParser_init(errors_obj) {
	var method_name = "AlParser_init";
	setErrorsObj(this, errors_obj, method_name);
} //end AlParser_init
//******

//******
function AlParser_reset_state() {
	var method_name = "AlParser_reset_state";
	var curr_action = "";
	try {
		curr_action = "clearing state properties";
		this._sequence_data = new Array();
		this._error_msgs = new Array();
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end AlParser_reset_state
//******

//******
function AlParser_store_record(curr_label, curr_sequence, line_num) {
	var method_name = "AlParser_store_record";
	var curr_action = "";
	try {
		//validate inputs
		if (curr_sequence == "") {curr_sequence = undefined;}
		if (curr_label == "") {curr_label = undefined;}
		line_num = Math.abs(parseInt(line_num));
		if (isNaN(line_num)) {
			throw new Error("line_num parameter must be castable to a positive integer");
		} //end if line_num is not a num

		//if at least one of seq/label is defined
		if ((curr_sequence != undefined) || (curr_label != undefined)) {
			//Label is not required for this format, so no error is possible;
			//Just go ahead and store
			current_tuple = {"label":curr_label, "sequence":curr_sequence,
							"line":line_num}
			this._sequence_data.push(current_tuple);
		} //end if at least one of seq/label is defined
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end AlParser_store_record
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function FastaParser(errors_obj) {
	if (errors_obj != gstrPrototype) {
		this.module = "alignment_parsers";
		this.init(errors_obj);
	} //end if
} //end FastaParser constructor

FastaParser.superclass = AlignmentParser.prototype;
FastaParser.prototype = new AlignmentParser(gstrPrototype);
FastaParser.prototype.constructor = FastaParser;
FastaParser.prototype.parse = FastaParser_parse;
FastaParser.prototype._reset_state = FastaParser_reset_state;
FastaParser.prototype._reset_accumulators = FastaParser_reset_accumulators;
FastaParser.prototype._parse_label = FastaParser_parse_label;
FastaParser.prototype._parse_sequence = FastaParser_parse_sequence;
FastaParser.prototype._store_accumulators = FastaParser_store_accumulators;

FastaParser.prototype.FASTA_LABEL_CHAR = ">";
//******

//******
function FastaParser_reset_state() {
	var method_name = "FastaParser_reset_state";
	var curr_action = "";
	try {
		curr_action = "clearing state properties";
		this._record_start_line_num = 0;

		curr_action = "calling _reset_state of superclass";
		WhitespaceDelimitedParser.superclass._reset_state.call(this);

		curr_action = "calling _reset_accumulators";
		this._reset_accumulators();
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_reset_state
//******

//******
function FastaParser_reset_accumulators() {
	var method_name = "FastaParser_reset_accumulators";
	var curr_action = "";
	try {
		curr_action = "resetting label and sequence accumulators";
		this._curr_label = undefined;
		this._accumulated_sequence = new Array();
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_reset_accumulators
//******

//******
function FastaParser_parse(input_lines) {
	var method_name = "FastaParser_parse";
	var curr_action = "";
	try {
		curr_action = "calling reset_state for a new run";
		this._reset_state();

		curr_action = "looping through each line to validate";
		for (var line_index in input_lines) {
			curr_line = input_lines[line_index];
			is_label_line = curr_line.startswith(this.FASTA_LABEL_CHAR);

			curr_action = "deciding on parse subroutine";
			if (is_label_line) {
				this._store_accumulators();
				this._parse_label(curr_line, line_index);
			} else {
				this._parse_sequence(curr_line);
			} //end if
		} //next line

		//handle when it is the last line
		this._store_accumulators();
		return this._sequence_data;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_parse
//******

//******
function FastaParser_parse_label(curr_line, line_index) {
	/* does not check for/handle bad input: it is
		the parse function's job to send only lines that
		actually have content/start with a label char.
	*/

	var method_name = "FastaParser_parse_label";
	var curr_action = "";
	try {
		//get the new label
		curr_action = "cutting the label away from its prefix";
		prefix_len = this.FASTA_LABEL_CHAR.length
		this._curr_label = curr_line.substr(prefix_len, curr_line.length);
		this._record_start_line_num = line_index;
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_parse_label
//******

//******
function FastaParser_parse_sequence(curr_line) {
	/* doesn't test for if line is not a string: up to parse function to
		prevent that from happening
	*/

	var method_name = "FastaParser_parse_sequence";
	var curr_action = "";
	try {
		//we are on a sequence line
		curr_action = "adding " + curr_line + " to the sequence";
		this._accumulated_sequence.push(curr_line)
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_parse_sequence
//******

//******
function FastaParser_store_accumulators() {
	var method_name = "FastaParser_store_accumulators";
	var curr_action = "";
	try {
		//collect the existing label and sequence
		curr_sequence = this._accumulated_sequence.join("");

		//if one or the other item is present, go ahead and store both
		//(and log any necessary errors.) If both are empty, ignore.
		if ((curr_sequence != "") || (this._curr_label != undefined)) {
			line_num = parseInt(this._record_start_line_num) + 1;

			//error if the sequence is empty
			if (curr_sequence == "") {
				error_msg = "Label at line " + line_num +
							" appears to be missing its sequence";
				this._error_msgs.push(error_msg);
			} //end if

			//error if label is empty
			if (this._curr_label == undefined) {
				error_msg = "Sequence starting at line " + line_num +
							" appears to be missing its label";
				this._error_msgs.push(error_msg);
			} //end if

			curr_action = "calling _store_record";
			this._store_record(this._curr_label, curr_sequence,
								this._record_start_line_num);

			//clear the accumulator variables
			this._reset_accumulators();
		} //end if
	} //end try
	catch (e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end FastaParser_store_accumulators
//******
//----------------------------------------------------------

//----------------------------------------------------------
//******
function WhitespaceDelimitedParser(errors_obj) {
	if (errors_obj != gstrPrototype) {
		this.module = "alignment_parsers";
		this.init(errors_obj);
	} //end if
} //end WhitespaceDelimitedParser constructor

WhitespaceDelimitedParser.superclass = AlignmentParser.prototype;
WhitespaceDelimitedParser.prototype = new AlignmentParser(gstrPrototype);
WhitespaceDelimitedParser.prototype.constructor = WhitespaceDelimitedParser;
WhitespaceDelimitedParser.prototype._reset_state = WdParser_reset_state;
WhitespaceDelimitedParser.prototype.parse = WdParser_parse;
WhitespaceDelimitedParser.prototype._tally_labels = WdParser_tally_labels;
WhitespaceDelimitedParser.prototype._validate_tally = WdParser_validate_tally;
//******

//******
function WdParser_reset_state(input_lines) {
	var method_name = "WdParser_reset_state";
	var curr_action = "";
	try {
		this._unlabelled_lines = new Array();
		this._labelled_lines = new Array();

		curr_action = "calling _reset_state of superclass";
		WhitespaceDelimitedParser.superclass._reset_state.call(this);
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end WdParser_reset_state
//******

//******
function WdParser_parse(input_lines) {
	var method_name = "WdParser_parse";
	var curr_action = "";
	try {
		var line_pieces, label_pieces, curr_label, curr_sequence;

		curr_action = "calling reset_state for a new run";
		this._reset_state();

		curr_action = "looping through each line to validate";
		for (var line_index in input_lines) {
			curr_line = input_lines[line_index];

			curr_action = "splitting the line on whitespaces";
			line_pieces = curr_line.split(/\s+/);

			curr_action = "checking if the line had any contents"
			if (line_pieces.length > 0) {
				curr_action = "last thing in the array is the sequence";
				curr_sequence = line_pieces.slice(-1);
				curr_sequence = curr_sequence[0];

				curr_action = "getting all but last piece of line as label";
				//label_pieces may be empty if no label on line
				label_pieces = line_pieces.slice(0,-1);
				curr_label = label_pieces.join(" ");

				curr_action = "calling _tally_labels";
				this._tally_labels(curr_label, line_index);

				curr_action = "calling _store_record";
				this._store_record(curr_label, curr_sequence, line_index);
			} //end if
		} //next line

		curr_action = "calling _validate_tally";
		this._validate_tally();

		return this._sequence_data;
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end WdParser_parse
//******

//******
function WdParser_tally_labels(curr_label, line_num) {
	var method_name = "WdParser_tally_labels";
	var curr_action = "";
	try {
		var tally_array;

		curr_action = "deciding whether this line is labelled or unlabelled";
		if (curr_label == "") {
			tally_array = this._unlabelled_lines;
		} else {tally_array = this._labelled_lines;}
		tally_array.push(parseInt(line_num));
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end WdParser_tally_labels
//******

//******
function WdParser_validate_tally() {
	var method_name = "WdParser_validate_tally";
	var curr_action = "";
	try {
		var num_labelled = this._labelled_lines.length;
		var num_unlabelled = this._unlabelled_lines.length;
		var msg_label = "Labelled";
		var msg_lines = this._labelled_lines;

		//if there is something in both, that's an error
		if ((num_labelled > 0) && (num_unlabelled > 0)) {
			if (num_unlabelled < num_labelled) {
				msg_label = "Unlabelled";
				msg_lines = this._unlabelled_lines;
			} //end if fewer unlabelled

			for (var line_num in msg_lines) {
				msg_lines[line_num] = msg_lines[line_num] + 1;
			} //next line
			msg_lines = msg_lines.join(", ");

			//whichever is smaller, report that as the outstanding cases
			var error_msg = "Some lines appear to have labels while others " +
				"don't.  " + msg_label + " line(s): " + msg_lines + ".";
			this._error_msgs.push(error_msg);
		} //end if there is an error
	} //end try
	catch(e) {
		this.errors.add(this.module, method_name, curr_action, e);
		throw new Error(method_name + " failed");
	} //end catch
} //end WdParser_validate_tally
//******

//----------------------------------------------------------
