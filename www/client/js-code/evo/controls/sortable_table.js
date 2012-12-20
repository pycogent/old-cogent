/*
sortable_tables.js

SortableTable object, which makes any table sortable by column. DynamicTable
object (on which the former is based), which allows table columns to be
replaced.

Revision History:
Written 2003 by Amanda Birmingham

uses string_validate.js
uses general_utils.js
uses web_utils.js
*/

//-------------------------------------------
//******
//SortableTable.
//An object that sorts html tables (represented as DynTable objects), using the w3c's table dom.
//SortableTable is a *decorator* class of the DynTable class (see GoF patterns.)  It
//implements the basic interface of DynTable by forwarding all requests for those functions
//to its private DynTable object.

//Public: SortableTable constructor.
//Takes in three arguments. First is either a DynamicTable object or a string holding the id of
//the table to make sortable.  If first arg is a dyntable, other args are ignored.  Otherwise,
//second arg must be string holding id of table head elm and third arg must be string holding
//id of table body elm.
//Returns new SortableTable object.
function SortableTable(varTableIdOrDynTable, strHeadId, strBodyId) {
	//if the first input isn't a dyntable
	if (!checkObjType(varTableIdOrDynTable, DynamicTable)) {
		//create new dyntable
		varTableIdOrDynTable = new DynamicTable(varTableIdOrDynTable, strHeadId, strBodyId);
	} //end if

	//set the dyntable to a private property
	this.dynTable = varTableIdOrDynTable;

	//since this class is a Decorator of the dynTable, import dynTable's (public) interface
	importInterfaces(this, this.dynTable, "dynTable");

	//set the empty properties (private)
	this.tbodyElm = undefined;
	this.curColIndex = undefined;
	this.ascendingSort = undefined;
} //end SortableTable constructor

SortableTable.prototype.sort = Sortable_sort;
SortableTable.prototype.setColAndDirection = Sortable_setColAndDirection;
SortableTable.prototype.sortRows = Sortable_sortRows;
SortableTable.prototype.reorderRow = Sortable_reorderRow;
//******

//******
//Public.  Sorts a table on the column whose id is specified.  Order depends on actions of
//setColAndDirection method.
//Takes in id of header cell for the column in question.
//No return value.
function Sortable_sort(strColumnId) {
	//local variables
	var intColIndex, intNumRows, intTestColValue, intCurColValue;

	//get the table object into a variable and put the body object into a property
	var objTable = document.getElementById(this.tableId);
	this.tbodyElm = document.getElementById(this.tbodyId);

	//set table's display to none (Netscape needs this; it misrenders 'live' changes to table);
	objTable.style.display = "none";

	try {
		//set the column index of the column to sort based on its id
		this.setColAndDirection(strColumnId);

		//reorder the rows based on this column
		this.sortRows();
	} //end try
	finally { //make sure to always reshow the table
		//set table's display to block again so we can see the results
		objTable.style.display = "block";
	} //end finally
} //end function Sortable_sort
//******

//******
//Private: does the actual work of sorting on columnid specified in this.curColIndex property,
//in direction specified by this.ascendingSort property.
//No inputs.
//No return value.
function Sortable_sortRows() {
	//local variables
	var intNumRows, intRowIndex, intInnerRowIndex, intCompareResult;
	var ascTestRowAndValue, ascCurRowAndValue;
	var intColIndex = this.curColIndex;

	//find out how many rows the tbody elm has
	intNumRows = this.tbodyElm.rows.length;

	//for each row (NOTE: starting at *second* one on purpose)
	for (intRowIndex = 1; intRowIndex < intNumRows; intRowIndex++) {
		//get the row object and its value in the specified column
		ascTestRowAndValue = this.getRowCellAndVal(intRowIndex, intColIndex);

		//for each row in the sorted section (up to intRowIndex)
		for (intInnerRowIndex = 0; intInnerRowIndex < intRowIndex; intInnerRowIndex++) {
			//get the row object and its value in the specified column
			ascCurRowAndValue = this.getRowCellAndVal(intInnerRowIndex, intColIndex);

			//if the column value for this row is greater than that of cur row
			intCompareResult = compareValues(ascTestRowAndValue["value"], ascCurRowAndValue["value"]);

			//if the sort order has been reversed, reverse the compare result too
			if (!this.ascendingSort) {intCompareResult = -intCompareResult;}

			//if the test value is smaller than the current value
			if (intCompareResult == -1) {
				//reorder these two rows and then break out of inner loop
				this.reorderRow(ascTestRowAndValue["row"], ascCurRowAndValue["row"]);;
				break;
			//else if the two rows have equal values AND
			//they are already next to each other, no need to do anything or test further
			} else if ((intCompareResult == 0) && (Math.abs(intInnerRowIndex-intRowIndex) == 1)) {
				break;
			} //end if compareResult is -1
		} //next row
	} //next row
} //end function Sortable_sortRows
//******

//******
//Private: moves the first input row to be before the second input row in the table being sorted.
//Takes in two HTMLTableRowElement objects.
//No return value.
function Sortable_reorderRow(objTestRow, objCurRow) {
	//local variables
	var objTbody = this.tbodyElm;

	//remove the test row
	objTbody.removeChild(objTestRow);

	//insert test row before the current row
	objTbody.insertBefore(objTestRow, objCurRow);
} //end function Sortable_reorderRow
//******

//******
//Private: determines the column index of the column to be sorted by and the direction of the sort.
//Direction is determined by checking whether this column is the one that was last sorted by; if so,
//the sort direction is reversed from what it was last time.  Otherwise, the sort direction is ascending.
//Sets curColIndex and ascendingSort properties.
//Takes in id of header cell for column to sort by.
//No return value.
function Sortable_setColAndDirection(strColumnId) {
	//call the getColIndexByHeaderId function of the associated dynTable
	var intColIndex = this.getColIndexByHeaderId(strColumnId);
	if (intColIndex == undefined) {throw new Error("No column index found for header id " + strColumnId);}

	//if the discovered col index is the same at the current col index
	if (intColIndex == this.curColIndex) {
		//flip-flop the sort direction
		this.ascendingSort = !this.ascendingSort
	} else {
		//(re)set the curColIndex property
		this.curColIndex = intColIndex;

		//(re)set the ascendingSort property
		this.ascendingSort = true
	} //end if
} //end function Sortable_setColAndDirection
//******
//-------------------------------------------


//-------------------------------------------
//******
//Public: constructor for DynamicTable object.
//Takes in three strings: id of table to make dynamic, id of head element, id of body element.
//Returns new DynamicTable object.
function DynamicTable(strTableId, strHeadId, strBodyId) {
	//make sure we have all three arguments and all are strings
	if (typeof strTableId != "string") {throw new Error ("Table id is not a string");}
	if (typeof strHeadId != "string") {throw new Error("Table head id is not string.");}
	if (typeof strBodyId != "string") {throw new Error("Table body id is not string.");}

	this.tableId = strTableId;
	this.theadId = strHeadId;
	this.tbodyId = strBodyId;
} //end DynamicTable constructor

DynamicTable.prototype.getColIndexByHeaderId = DynTable_getColIndexByHeaderId;
DynamicTable.prototype.getRowCellAndVal = DynTable_getRowCellAndVal;
DynamicTable.prototype.replaceColumn = DynTable_replaceColumn;
//******

//******
//Public
//Takes two args: first is a row index or a row id (as integer or string); second is
//selected column index as integer.
//Returns a hash containing the row object for the row specified by input, the
//cell object for the selected column in that row, and the value of the selected cell.
function DynTable_getRowCellAndVal(varRowIndexOrId, intColIndex) {
	//local variables
	var ascRowCellAndVal = new Array();
	var objTbodyRows = document.getElementById(this.tbodyId).rows;

	//validate the inputs
	if (typeof varRowIndexOrId != "string" && typeof varRowIndexOrId != "number") {throw new Error("Argument 1, varRowIndexOrId, must be a string or a number.");}
	if (parseInt(intColIndex) != intColIndex) {throw new Error("Argument 2, intColIndex, must be an integer.");}

	//if varRowIndexOrId is an integer expressed as a string, turn it into an integer
	if (parseInt(varRowIndexOrId) == varRowIndexOrId) {varRowIndexOrId = parseInt(varRowIndexOrId);}

	//get the row with the input index or id and put it in the return hash
	//Note that experimenting shows that the "item" call will take an index or an id
	//with equal facility ... no need for separate treatment.
	ascRowCellAndVal["row"] = objTbodyRows.item(varRowIndexOrId);
	if (ascRowCellAndVal["row"] == undefined) {throw new Error("No row found for index/id " + varRowIndexOrId);}

	//get the desired cell in the current row
	ascRowCellAndVal["cell"] = ascRowCellAndVal["row"].cells[intColIndex];
	if (ascRowCellAndVal["cell"] == undefined) {throw new Error("No cell found for id " + intColIndex);}

	//get the column value for this row and put in the return hash
	ascRowCellAndVal["value"] = getInnerText(ascRowCellAndVal["cell"]);

	return ascRowCellAndVal;
} //end function DynTable_getRowCellAndVal
//******

//******
//Public.  Finds the index of the column whose header cell has an id that matches the
//input id.  If blnInexactMatch is set to true, finds the column that contains that
//id within its own id.  Errors if more than one column contains that id for an inexact
//match; for an exact match, just returns first exact match.
//Takes in the id of a header cell (string, required) and an optional boolean.  If boolean
//isn't entered, it defaults to false.
//Returns the index of the column that cell belongs to, or undefined if no column is found.
function DynTable_getColIndexByHeaderId(strColumnId, blnInexactMatch) {
	//local variables
	var objTheadRow, arrTheadCells, objTheadCell;
	var intFoundIndex;

	//escape any RE-special characters in the column id
	var strEscapedId = reEscape(strColumnId);
	var objIdRe = new RegExp(strEscapedId);

	//if inexact match toggle isn't set, make it false
	if (blnInexactMatch == undefined) {blnInexactMatch = false;}

	//coerce the input to a string, just in case
	strColumnId = new String(strColumnId);
	if (typeof blnInexactMatch != "boolean") {throw new Error("blnInexactMatch argument must be a boolean");}

	//get the thead element's first (and only) row
	objTheadRow = document.getElementById(this.theadId).rows[0];
	arrTheadCells = objTheadRow.cells;

	//loop through the cells in thead row
	for (var intColIndex = 0; intColIndex < arrTheadCells.length; intColIndex++) {
		//get the cell object
		objTheadCell = arrTheadCells[intColIndex];

		//check if we're doing an inexact match
		if (blnInexactMatch) {
				//see if there is an inexact match
				if (objTheadCell.id.search(objIdRe) != -1) {
					//if we haven't already found a column that matches this
					if (intFoundIndex == undefined) {
						intFoundIndex = intColIndex; //but DON'T break; we keep going to make sure we don't find duplicate matches
					} else {
						//throw an error if more than one column matches the id inexactly:
						//that can't be what you want!
						throw new Error("inexact match for more than one column id: " + intFoundIndex + ", " + intColIndex);
					} //end if we have/haven't found anything else that matches this
				} //end if there's an inexact match with this cell's id
		} else {
			//if id of cell matches input id, this cell's index the desired column index; exit now
			if (strColumnId == objTheadCell.id) {intFoundIndex = intColIndex; break;}
		} //end if we're doing an exact or inexact match
	} //next cell

	return intFoundIndex;
} //end function DynTable_getColIndexByHeaderId
//******


//******
//Public: replaces some or all of the values in the selected column with others provided.
//Takes in the id of the header cell in the column to replace values for
//and a hash, keyed by id of row to change, where values are new entries
//for the chosen column in that row.
//No return value.
function DynTable_replaceColumn(strColumnId, ascValByRowIdOrIndex, blnInexactMatch) {
	//local variables
	var intColIndex, ascRowCellAndVal;

	//make sure we got an array ... other iterable items (like string)
	//are NOT acceptable
	if (ascValByRowIdOrIndex.slice == undefined) {
		throw new Error("ascValByRowIdOrIndex must be an array");
	} //end validation of ascValByRowIdOrIndex

	//get the column index by the column id
	intColIndex = this.getColIndexByHeaderId(strColumnId, blnInexactMatch);
	if (intColIndex == undefined) {throw new Error("Unable to find column index for header id " + strColumnId);}

	//for each rowid with new values
	for (var strRowId in ascValByRowIdOrIndex) {
		//get the hash of row, cell, and value, with flag to treat first param as id not index
		ascRowCellAndVal = this.getRowCellAndVal(strRowId, intColIndex, true);

		//replace the current cell text with the input text
		setInnerText(ascRowCellAndVal["cell"], ascValByRowIdOrIndex[strRowId]);
	} //next rowid
} //end function DynTable_replaceColumn
//******
//-------------------------------------------