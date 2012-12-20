/*
fancy_dictionary.js

Js dictionaries are just arrays (isn't everything in javascript?)
However, since arrays have some unfortunate properties (like, if you try to
get an element that doesn't exist, it just adds it for you ... and no
"exists" property), I've extended it a little to be an all-singing,
all-dancing dictionary object.

NB: most of the time these extra functions are not necessary.  Only use this
object if your need for the extra methods really justifies the added weight.

Revision History:

from error_handler uses *
*/

//******
//Dictionary constructor
function Dictionary(objErrors, arrValidKeys) {
	//Setup error-handling
	this.module = "fancy_dictionary";
	var strRoutine = "Dictionary";
	var strAction = "";
	if (!isInstanceOf(objErrors, Errors)) {throw new Error(strRoutine + " constructor did not receive an errors object");}
	this.errors = objErrors;

	try {
		//the associative array that holds the actual keys/items of the dictionary
		this.entries = new Array();

		//an array of keys that are considered valid; used by add.  If they passed it in,
		if (typeof arrValidKeys == "Array") {
			this.validKeys = arrValidKeys; //use what they gave us
		} else { //otherwise, make an empty one
			this.validKeys = new Array();
		} //end if they did/didn't pass in an array holding the valid keys
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end constructor Dictionary

//These statements should be kept WITH the Dictionary constructor function
//give Dictionary's prototype some methods
Dictionary.prototype.add = Dic_add;
Dictionary.prototype.remove = Dic_remove;
Dictionary.prototype.key = Dic_key;
Dictionary.prototype.item = Dic_item;
Dictionary.prototype.exists = Dic_exists;
Dictionary.prototype.array = Dic_array;
Dictionary.prototype.count = Dic_count;
Dictionary.prototype.toString = Dic_toString;
Dictionary.prototype.setValids = Dic_setValids;
Dictionary.prototype.checkValids = Dic_checkValids; //NB: this is SUPPOSED to be a private function for use by Dic_add and Dic_setValids only.
//******

//******
//this function allows the user to add a valids dictionary if they didn't add one before.
//It also checks to see whether any of the existing elements in the dictionary conflict
//with this valids dictionary, and throws an error if any do.  In that case, the valids
//dictionary remains as it was before this function was called.
function Dic_setValids (objArray) {
	var strRoutine = "Dic_setValids";
	var strAction = "";
	try {
		//local variable
		var arrTempValidKeys;

		//first, check to see that they passed us in an array
		strAction = "checking to make sure the input is an array";
		if ((typeof objArray != "object") || (objArray.constructor != Array)) {throw new Error("input is not an array");}

		//now copy the current this.validKeys into a temp variable and set this.validKeys to be the input array
		strAction = "copying current this.validKeys into a temp variable and replacing this.validKeys with the input array";
		arrTempValidKeys = this.validKeys;
		this.validKeys = objArray;

		//loop through all the keys for this.entries and call this.checkValids on each entry
		//to make sure it doesn't have an illegal key under the new valids array
		strAction = "looping through all the keys in this.entries";
		for (var strCurKey in this.entries) {
			strAction = "calling this.checkValids on " + strCurKey;
			if (!this.checkValids(strCurKey)) {
				//reset this.validKeys to the original being held in the temp variable
				strAction = "resetting this.validKeys to its original value and throwing error";
				this.validKeys = arrTempValidKeys;
				throw new Error("Existing key " + strCurKey + " would be illegal under new valids definition; definition not changed. ");
			} //end if the current key is invalid
		} //next this.entries key
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_setValids
//******

//******
//this function handles adding/overwriting values in a dictionary
function Dic_add(strKey, strItem) {
	var strRoutine = "Dic_add";
	var strAction = "";
	try {
		strAction = "making sure the inputs aren't undefined: " + strKey + ", " + strItem;
		if (strKey == undefined) {throw new Error("key is undefined");}
		if (strItem == undefined) {throw new Error("item is undefined");}

		//if the validKeys array has a length greater than zero,
		//see if the input key exists in the valids array
		strAction = "checking whether validKeys array length > 0";
		if (this.validKeys.length > 0) {
			strAction = "calling this.checkValids to see if the input key exists in the valids array: " + strKey;
			if (!this.checkValids(strKey)) {throw new Error(strKey + " is not one of the valid keys for this dictionary");}
		} //end if we have a list of validKeys to check

		//add/overwrite the value for the key with the value for the item
		strAction = "writing " + strItem + " to dictionary under key " + strKey;
		this.entries[strKey] = strItem;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
}//end function Dic_set
//******

//******
//function that loops through the valids array and sees if a given key is in it.
//returns true if it is, false if it isn't ... duh.
//NB: this is SUPPOSED to be a private function for use by Dic_add and Dic_setValids only.
function Dic_checkValids(strKey) {
	var strRoutine = "Dic_checkValids";
	var strAction = "";
	try {
		var blnReturn = false; //set the return value to assume the worst

		//loop through all the elements of the valids array, and if any of them
		//match the input one, set return value to true and break out of loop
		strAction = "loop through the valids array";
		for (var intValidIndex = 0; intValidIndex < this.validKeys.length; intValidIndex++) {
			strAction = "checking current valid against input key: " + this.validKeys[intValidIndex] + " =? " + strKey;
			if (this.validKeys[intValidIndex] == strKey) {
				strAction = "setting return value to true and breaking out of loop";
				blnReturn = true;
				break;
			} //end if current valid matches input
		} //next valid key

		//send back the return value
		return blnReturn;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_checkValids
//******

//******
//if an entry for this key exists, remove it
function Dic_remove(strKey) {
	var strRoutine = "Dic_remove";
	var strAction = "";
	try {
		//try to delete this key.  If it doesn't exist, delete will still return true
		strAction = "calling delete on this.entries for key " + strKey;
		delete this.entries[strKey];
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_remove
//******

//******
//return key of item if item exists, otherwise return undefined
function Dic_key(strItem) {
	var strRoutine = "Dic_key";
	var strAction = "";
	try {
		var strKey; //initialize the return value, but leave it undefined

		//loop through the internal array using for ... in
		strAction = "looping through all the keys in this.entries";
		for (var strCurKey in this.entries) {
			//if current item = input item
			strAction = "checking if entry for " + strCurKey + " = " + strItem;
			if (this.entries[strCurKey] == strItem) {
				//put that in return value and break out of the loop
				strAction = "appropriate key found; setting as return and breaking loop";
				strKey = strCurKey;
				break;
			} //end if this is the item they're looking for
		} //next key

		//return the return value; if we found an item, it will be filled;
		//if we didn't, it will have remained undefined
		return strKey;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_key
//******

//******
//return item for key if key exists, otherwise return undefined
function Dic_item(strKey) {
	var strRoutine = "Dic_item";
	var strAction = "";
	try {
		//try to grab the item out of the array;
		//if it doesn't exist, the array will give back an undefined
		//and won't try to add it to the array
		strAction = "getting item for " + strKey + " out of this.entries";
		return this.entries[strKey];
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_item
//******

//******
//return true if key exists
function Dic_exists(strKey) {
	var strRoutine = "Dic_exists";
	var strAction = "";
	try {
		var strEntryType = "";
		var blnExists = false; // set up the return variable; assume the worst :)

		//check the typeof property of the the array entry with this key:
		//if it is NOT undefined, this key does exist in the array
		strAction = "checking typeof of " + strKey;
		strEntryType = typeof this.entries[strKey]; //NB: typeof returns a string reading "undefined", rather than the keyword undefined, for undefined objects :(
		if (strEntryType != "undefined") {
			blnExists = true;
		} //end if this item really was defined

		return blnExists;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_exists
//******

//******
//return either an array of keys or an array of items, depending on which the user wanted.
//can also be used to return the array of valids, if the input word is "valids".
//the default is keys.  The valid input strings are stored in class variables so they
//should be easy to change--no magic words.
Dic_array.keysInput = "keys";
Dic_array.itemsInput = "items";
Dic_array.validsInput = "valids";

function Dic_array(strKeysOrItems) {
	var strRoutine = "Dic_array";
	var strAction = "";
	try {
		var arrReturn; //define return variable
		//if strKeysOrItems is undefined, make it keys
		strAction = "checking to see if strKeysOrItems is undefined";
		if (strKeysOrItems == undefined) {strKeysOrItems = Dic_array.keysInput;}

		//if they want the valids,
		strAction = "checking what kind of array is wanted: " + strKeysOrItems;
		if (strKeysOrItems == Dic_array.validsInput) {
			//just make the return array the dictionary object's valids array
			strAction = "making return array = this.validKeys";
			arrReturn = this.validKeys;
		} else if ((strKeysOrItems == Dic_array.keysInputs) || (strKeysOrItems == Dic_array.itemsInput)) {
			 arrReturn = new Array(); //we're going to make a new array

			//loop through all the keys
			strAction = "looping through this.entries";
			for (var strCurrent in this.entries) {
				//right now, the current value is the key.
				//if they wanted the items instead, make the NEW current value
				//the item corresponding to the PRESENT current value
				strAction = "checking whether to get the key or item for current entry: " + strKeysOrItems;
				if (strKeysOrItems == Dic_array.itemsInput) {strCurrent = this.entries[strCurrent];}
				//add the current value to the array
				strAction = "adding current key or item to return array: " + strCurrent;
				arrReturn[arrReturn.length] = strCurrent;
			} //next key
		} else { //not a recognized input, so error
			throw new Error(strKeysOrItems + "is not a recognized array type");
		} //end if the input is valids, keys or items, or not recognized

		//return whatever array we just got
		return arrReturn;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_array
//******

//******
//this function returns how many entries are in the dictionary
function Dic_count() {
	var strRoutine = "Dic_count";
	var strAction = "";
	try {
		var intCount = 0;

		strAction ="adding one to count for each key";
		for (var strKey in this.entries) {intCount++;}
		return intCount;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_count
//******

//******
//this function goes through the dictionary and dumps it to a string
function Dic_toString() {
	var strRoutine = "Dic_toString";
	var strAction = "";
	try {
		var strOutput = "";

		//loop through the internal array
		strAction = "looping through this.entries keys";
		for (var strCurKey in this.entries) {
			strAction = "building up current entry into a string";
			strOutput = strOutput + strCurKey + "->" + this.entries[strCurKey] + "\n";
		} //next key

		//return the big string we made
		return strOutput;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Dic_toString
//******