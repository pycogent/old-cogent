/*
sets.js

Set object which implements bitvector-like functionality.

NB: this set implementation is hashed-based.  A string-based bitvector
implementation was developed, but was too slow to be plausible.  I know
that hashes don't seem like the best candidate handling set functions, but
in javascript they really are ... trust me on this.

Revision History:

from error_handler uses *
from general_utils uses hashToArray
*/


//--------------------------------------------
//Set Object
//I'd still like to add methods for member count, and maybe
//set relations at some point in the future
//******
function Set(objErrors, arrIncludedMembers, objSetUniverse) {
	if (objErrors != gstrPrototype) {
		this.module = "iHashSets";
		this.init(objErrors, arrIncludedMembers, objSetUniverse);
	} //end if
} //end constructor Set

//Set doesn't inherit from anything, so it doesn't need its superclass or prototype set, or its constructor reset.
Set.prototype.init = Set_init;
Set.prototype.update = Set_update;
Set.prototype.getMembers = Set_getMembers;
Set.prototype.add = function (arrIncludedMembers) {this.update(arrIncludedMembers, true);};
Set.prototype.remove = function (arrRemovedMembers) {this.update(arrRemovedMembers, false);};
Set.prototype.combine = Set_combine;
Set.prototype.isMember = Set_isMember;
Set.prototype.and = Set_and;
Set.prototype.or = Set_or;
Set.prototype.difference = Set_difference;
Set.prototype.singleUpdate = Set_singleUpdate;
//******

//******
//Errors is the only required argument, although if you omit both others, you get a hash that
//isn't good for much except filling up :)
function Set_init(objErrors, arrIncludedMembers, objSetUniverse) {
	var strRoutine = "Set_init";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "creating empty properties";
		this.length = 0;
		this.memberHash = new Array();

		strAction = "calling this.update to add members, if members were provided";
		if (arrIncludedMembers != undefined) {this.update(arrIncludedMembers, true);}
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_init function
//******

//******
function Set_update(arrIncludedMembers, blnAdd) {
	var strRoutine = "Set_update";
	var strAction = "";
	try {
		//local variables
		var strMemberName, arrMembers;

		strAction = "if we got nothing to update, just returning straightaway";
		if (arrIncludedMembers == undefined) {return;}

		//if the input isn't an array, create an array of 1 to hold it
		strAction = "get or create the array holding members to update";
		arrMembers = arrIncludedMembers; //initial assumption
		if (!checkObjType(arrIncludedMembers, Array)) {
			this.singleUpdate(arrIncludedMembers, blnAdd);
		} else {
			strAction = "looping through each item we are updating";
			for (var intMemberIndex = 0; intMemberIndex < arrMembers.length; intMemberIndex++) {
				strAction = "get out the member name";
				strMemberName = arrMembers[intMemberIndex];

				strAction = "calling singleUpdate for this member name  " + strMemberName;
				this.singleUpdate(strMemberName, blnAdd);
			} //next item
		} //end if the input is/isn't something other than an array
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_update function
//******

//******
function Set_singleUpdate(strMemberName, blnAdd) {
	var strRoutine = "Set_singleUpdate";
	var strAction = "";
	try {
		strAction = "getting value for this member name in memberHash " + strMemberName;
		var strMemberVal = this.memberHash[strMemberName];

		if (strMemberVal == undefined) {
			if (blnAdd) {
				this.memberHash[strMemberName] = strMemberName;
				this.length++;
			} //end if
		} else {
			if (!blnAdd) {
				delete this.memberHash[strMemberName];
				this.length--;
			} //end if
		} //end if
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_update function
//******

//******
//HOW TO HANDLE assigning the output set a universe?  Give it one only if the
//two input sets have the SAME universe, or what?
function Set_combine(strOperation, objSecondSet) {
	var strRoutine = "Set_combine";
	var strAction = "";
	try {
		//local variables
		var objReturnSet;

		strAction = "switching on operation: " + strOperation;
		switch (strOperation.toLowerCase()) {
			case "union":
			case "or":
				objReturnSet = this.or(objSecondSet); break;
			case "intersection":
			case "and":
				objReturnSet = this.and(objSecondSet); break;
			case "difference":
				objReturnSet = this.difference(objSecondSet); break;
			case "symmetric difference":
			case "xor":
				throw new Error("symmetric difference combination not implemented yet");
				//no need for a break here, since there's a throw
			default:
				throw new Error("unrecognized bitvector operation: " + strOperation);
		} //end switch


		//return the new set
		return objReturnSet;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_combine function
//******

//******
function Set_and(objSecondSet) {
	var strRoutine = "Set_and";
	var strAction = "";
	try {
		//local variables
		var objShorterSet = this; //initial assumption
		var objLongerSet = objSecondSet;
		var strMemberVal, objReturnSet;

		strAction = "creating a new, empty set";
		objReturnSet = new Set(this.errors, undefined, undefined);

		strAction = "if the second set is shorter than this one, make it = shortset";
		if (objSecondSet.length < this.length) {
			objShorterSet = objSecondSet;
			objLongerSet = this;
		} //end if

		strAction = "looping through each entry in shorter set";
		for (var strKey in objShorterSet.memberHash) {
			strAction = "getting member value from longer hash for key " + strKey;
			strMemberVal = objLongerSet.memberHash[strKey];

			strAction = "calling for add to return set if val for this key is defined " + strKey;
			if (strMemberVal != undefined) {objReturnSet.add(strKey);}
		} //next entry

		//return the new set
		return objReturnSet;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_and function
//******

//******
function Set_or(objSecondSet) {
	var strRoutine = "Set_or";
	var strAction = "";
	try {
		//local variables
		var objReturnSet;
		var ascShorterCopy = new Array();
		var objShorterSet = this; //initial assumption
		var objLongerSet = objSecondSet;

		strAction = "creating a new, empty set";
		objReturnSet = new Set(this.errors, undefined, undefined);

		strAction = "if the second set is shorter than this one, make it = shortset";
		if (objSecondSet.length < this.length) {
			objShorterSet = objSecondSet;
			objLongerSet = this;
		} //end if

		strAction = "copying shorter set";
		for (var strKey in objShorterSet.memberHash) {ascShorterCopy[strKey] = strKey;}

		strAction = "looping through each entry in longer set";
		for (strKey in objLongerSet.memberHash) {
			strAction = "calling for add to return set for key " + strKey;
			objReturnSet.singleUpdate(strKey, true);

			strAction = "delete key from shorter copy " + strKey;
			delete ascShorterCopy[strKey];
		} //next entry

		strAction = "looping through remnants of shorter copy";
		for (strKey in ascShorterCopy) {
			strAction = "calling for add to return set for key " + strKey;
			objReturnSet.singleUpdate(strKey, true);
		} //next

		//return the new set
		return objReturnSet;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_or function
//******

//******
function Set_difference(objSecondSet) {
	var strRoutine = "Set_and";
	var strAction = "";
	try {
		//local variables
		var strMemberVal, objReturnSet;

		strAction = "creating a new, empty set";
		objReturnSet = new Set(this.errors, undefined, undefined);

		strAction = "looping through each entry in this set";
		for (var strKey in this.memberHash) {
			strAction = "getting member value from second set hash for key " + strKey;
			strMemberVal = objSecondSet.memberHash[strKey];

			strAction = "calling for add to return set if val for this key is defined " + strKey;
			if (strMemberVal == undefined) {objReturnSet.singleUpdate(strKey, true);}
		} //next entry

		//return the new set
		return objReturnSet;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_and function
//******


//******
function Set_getMembers() {
	var strRoutine = "Set_getMembers";
	var strAction = "";
	try {
		return this.memberHash;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_getMembers function
//******

//******
function Set_isMember(strMemberName) {
	var strRoutine = "Set_isMember";
	var strAction = "";
	try {
		var blnIsMember = false;

		strAction = "getting value out of hash for member name " + strMemberName;
		var strMemberVal = this.memberHash[strMemberName];
		if (strMemberVal != undefined) {blnIsMember = true;}

		//return the member array
		return blnIsMember;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end Set_isMember function
//******
//--------------------------------------------