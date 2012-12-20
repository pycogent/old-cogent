/*
iterators.js

This module is based whole hog on the GoF Iterator pattern, and their
example of it in the book's case study section.  Includes an abstract
Iterator interface, an ArrayIterater, and preorder and post-order tree
iterators.

Revision History:

from error_handler.js uses *
*/


//---------------------------------------------
//The abstract Iterator root class that all the other iterators derive from.
//******
//Iterator Constructor
function Iterator(objErrors) {
	//since the abstract Iterator has only methods, and all those are defined
	//in its prototype, nothing goes here :)
} //end function Iterator

//Iterator doesn't inherit from anything, so it doesn't need its superclass or prototype set, or its constructor reset.
Iterator.prototype.first = function() {};
Iterator.prototype.next = function() {};
Iterator.prototype.isDone = function() {};
Iterator.prototype.currentItem = function() {};
Iterator.prototype.iterateVisitor = Iterator_iterateVisitor;
//******

//******
//loops through all the items accessible through the
//iterator and tells them to accept a visitor, if they
//know how to do so.  If they don't, they are IGNORED!
//no return value.
function Iterator_iterateVisitor(objVisitor) {
	var strRoutine = "Iterator_iterateVisitor";
	var strAction = "";
	try {
		//check that what we were passed is really a visitor?

		strAction = "loop through the current items provided by this iterator";
		for (this.first(); !this.isDone(); this.next()) {
			strAction = "calling currentItem on iterator";
			var objCurrentItem = this.currentItem();

			strAction = "checking if acceptVisitor method is defined for this item";
			if (objCurrentItem.acceptVisitor != undefined) {
				strAction = "calling accept visitor on currentItem";
				objCurrentItem.acceptVisitor(objVisitor);
			} //end if this item can accept visitors
		} //next currentItem
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function Iterator_iterateVisitor
//******
//---------------------------------------------

//---------------------------------------------
//Null iterator: this is the one used by leaf nodes.
//Its methods are all dummies, except for isDone, which
//tells you it is automatically done.
//******
//NullIterator constructor.  Takes only an errors object.
function NullIterator(objErrors) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		var strRoutine = "NullIterator";
		var strAction = "";
		setErrorsObj(this, objErrors, strRoutine);

		try {
			//since NullIterator has only methods, and all those are defined in its prototype
			//nothing goes here :)
		} //end try
		catch (e) {
			this.errors.add(this.module, strRoutine, strAction, e);
			throw new Error(strRoutine + " failed");
		} //end catch
	} //end if this isn't a prototype
} //end constructor NullIterator

NullIterator.superclass = Iterator.prototype;
NullIterator.prototype = new Iterator(gstrPrototype);
NullIterator.prototype.constructor = NullIterator;
NullIterator.prototype.isDone = function() {return true;};
//******
//---------------------------------------------


//---------------------------------------------
//Array iterator.  You know who you are.
//******
//Array iterator constructor.  Takes in an error object and the array object it will iterate.
function ArrayIterator(objErrors, objArray) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		var strRoutine = "ArrayIterator";
		var strAction = "";
		setErrorsObj(this, objErrors, strRoutine);

		try {
			strAction = "creating properties";
			this.currentIndex = undefined;
			this.currentArray = objArray;
		} //end try
		catch (e) {
			this.errors.add(this.module, strRoutine, strAction, e);
			throw new Error(strRoutine + " failed");
		} //end catch
	} //end if this isn't a prototype
} //end constructor ArrayIterator

ArrayIterator.superclass = Iterator.prototype;
ArrayIterator.prototype = new Iterator(gstrPrototype);
ArrayIterator.prototype.constructor = ArrayIterator;
ArrayIterator.prototype.first = function() {this.currentIndex = 0;};
ArrayIterator.prototype.next = function() {this.currentIndex++;};
ArrayIterator.prototype.isDone = function() {
									if (this.currentIndex < this.currentArray.length) {
										return false;
									} else {return true;}
								}; //end inline function isDone
ArrayIterator.prototype.currentItem = function() {return this.currentArray[this.currentIndex];};
//******
//---------------------------------------------

//---------------------------------------------
//******
function IteratorDummy(objErrors, objChild) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		var strRoutine = "DictionaryIterator";
		var strAction = "";
		setErrorsObj(this, objErrors, strRoutine);

		try {
			this.children = new Array(objChild);
		} //end try
		catch (e) {
			this.errors.add(this.module, strRoutine, strAction, e);
			throw new Error(strRoutine + " failed");
		} //end catch
	} //end if this isn't a prototype
} //end constructor IteratorDummy

IteratorDummy.prototype.createIterator = function () {return new ArrayIterator(this.errors, this.children);};
//******
//---------------------------------------------


//---------------------------------------------
//NOT FINISHED
//Dictionary iterator: work your way through the entries of my custom dictionary object.
//******
//DictionaryIterator constructor: takes errors object and the dictionary to iterate through.
function DictionaryIterator(objErrors, objDictionary) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		var strRoutine = "DictionaryIterator";
		var strAction = "";
		setErrorsObj(this, objErrors, strRoutine);

		try {
			//Dictionaries are really just smart arrays, so
			//call the array function of the dictionary to get all the items,
			//and then just use an array iterator
		} //end try
		catch (e) {
			this.errors.add(this.module, strRoutine, strAction, e);
			throw new Error(strRoutine + " failed");
		} //end catch
	} //end if this isn't a prototype
} //end constructor DictionaryIterator

DictionaryIterator.superclass = ArrayIterator.prototype;
DictionaryIterator.prototype = new ArrayIterator(gstrPrototype);
DictionaryIterator.prototype.constructor = DictionaryIterator;
//******
//---------------------------------------------


//---------------------------------------------
//Order iterator: Abstract.  It is passed the root object, and uses
//the other, structure-specific objects of that root to iterate.
//******
//OrderIterator constructor: takes in errors object and root object of tree to iterate.
function OrderIterator(objErrors, objRoot) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		this.init(objErrors, objRoot);
	} //end if this isn't a prototype
} //end constructor PreorderIterator


OrderIterator.superclass = Iterator.prototype;
OrderIterator.prototype = new Iterator(gstrPrototype);
OrderIterator.prototype.constructor = OrderIterator;
OrderIterator.prototype.init = OrderIt_init;
OrderIterator.prototype.currentItem = OrderIt_currentItem;
OrderIterator.prototype.isDone = OrderIt_isDone;
OrderIterator.prototype.getTop = OrderIt_getTop;
OrderIterator.prototype.countIterators = function () {return this.iteratorStack.length;};
//******

//******
function OrderIt_init(objErrors, objRoot) {
	var strRoutine = "OrderIt_init";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "creating properties";
		this.root = objRoot;
		this.iteratorStack = new Array();
		this.firstCalled = false;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function OrderIt_init
//******

//******
function OrderIt_currentItem() {
	var strRoutine = "OrderIt_currentItem";
	var strAction = "";
	try {
		var objReturn;

		strAction = "calling countIterators to check if there are items on the stack";
		if (this.countIterators() > 0) {
			strAction = "calling currentItem on the top one and returning it";
			objReturn = this.getTop().currentItem();
		} //end if the top iterator exists

		return objReturn;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function OrderIt_currentItem
//******

//******
function OrderIt_isDone() {
	var strRoutine = "OrderIt_isDone";
	var strAction = "";
	try {
		strAction = "checking if there's nothing in our stack AND we have already had first called on us";
		if ((this.countIterators() == 0) && (this.firstCalled)) {
				return true;
		} else {
			return false;
		} //end if we have nothing on the stack and we've already had first called
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function OrderIt_isDone
//******

//******
//return the top iterator on the iterator stack, WITHOUT popping it off.
//if the stack is empty, return a null iterator
function OrderIt_getTop() {
	var strRoutine = "OrderIt_getTop";
	var strAction = "";
	try {
		var objReturnIterator;

		strAction = "checking how many iterators are on the stack";
		if (this.countIterators() > 0) {
			objReturnIterator = this.iteratorStack[this.countIterators() - 1];
		} else {
			objReturnIterator = new NullIterator(this.errors);
		}

		return objReturnIterator;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end OrderIt_getTop
//---------------------------------------------


//---------------------------------------------
//A preorder iterator.  It is passed the root object, and uses
//the other, structure-specific objects of that root to iterate.
//******
//PreorderIterator constructor: takes in errors object and root object of tree to iterate.
function PreorderIterator(objErrors, objRoot) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		this.init(objErrors, objRoot);
	} //end if this isn't a prototype
} //end constructor PreorderIterator

PreorderIterator.superclass = OrderIterator.prototype;
PreorderIterator.prototype = new OrderIterator(gstrPrototype);
PreorderIterator.prototype.constructor = PreorderIterator;
PreorderIterator.prototype.init = PreIt_init;
PreorderIterator.prototype.first = PreIt_first;
PreorderIterator.prototype.next = PreIt_next;
//******

//******
//PreorderIterator constructor: takes in errors object and root object of tree to iterate.
function PreIt_init(objErrors, objRoot) {
	var strRoutine = "PreorderIterator";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "calling the init of PreorderIterator's superclass (OrderIterator) to set up inherited properties";
		PreorderIterator.superclass.init.call(this, objErrors, objRoot);
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end constructor PreorderIterator
//******

//******
function PreIt_first() {
	var strRoutine = "PreIt_first";
	var strAction = "";
	try {
		strAction = "creating a dummy iteratable object";
		var objRoot = new IteratorDummy(this.errors, this.root);

		strAction = "calling createIterator on the root object";
		var rootIterator = objRoot.createIterator();

		strAction = "calling first on the root iterator";
		rootIterator.first();

		strAction = "pushing the root iterator onto the empty iteratorstack";
		this.iteratorStack.push(rootIterator);

		strAction = "setting the this.firstCalled property to true";
		this.firstCalled = true;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function PreIt_first
//******

//******
function PreIt_next() {
	var strRoutine = "PreIt_next";
	var strAction = "";
	try {
		strAction = "geting the current item from the iterator stack"; // (but DON'T pop it off)
		var currentIterator = this.getTop();

		strAction = "creating an iterator from the current item of the top iterator";
		var newIterator = currentIterator.currentItem().createIterator();

		strAction = "calling first on the new iterator";
		newIterator.first();

		strAction = "puting the new iterator into the stack";
		this.iteratorStack.push(newIterator);

		strAction = "while (stack has iterator on it AND the top iterator has isDone = true)";
		while ((this.countIterators() > 0) && (this.getTop().isDone())) {
			strAction = "popping the stack"; // (is deleting necessary here, in JavaScript??)
			this.iteratorStack.pop();

			strAction = "calling next on the new top iterator of the stack";
			this.getTop().next();
		} //end while
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function PreIt_next
//******
//---------------------------------------------


//---------------------------------------------
//A postorder iterator.  It is passed the root object, and uses
//the other, structure-specific objects of that root to iterate.
//******
//PostorderIterator constructor: takes in errors object and root object of tree to iterate.
function PostorderIterator(objErrors, objRoot) {
	if (objErrors != gstrPrototype) {
		//Set up error-handling:
		this.module = "Iterator";
		this.init(objErrors, objRoot);
	} //end if this isn't a prototype
} //end constructor PostorderIterator

PostorderIterator.superclass = OrderIterator.prototype;
PostorderIterator.prototype = new OrderIterator(gstrPrototype);
PostorderIterator.prototype.constructor = PostorderIterator;
PostorderIterator.prototype.init = PostIt_init;
PostorderIterator.prototype.first = PostIt_first;
PostorderIterator.prototype.next = PostIt_next;
PostorderIterator.prototype.getBottom = PostIt_getBottom;
//******

//******
//PostorderIterator constructor: takes in errors object and root object of tree to iterate.
function PostIt_init(objErrors, objRoot) {
	var strRoutine = "PreorderIterator";
	var strAction = "";
	setErrorsObj(this, objErrors, strRoutine);

	try {
		strAction = "calling the init of PostorderIterator's superclass (OrderIterator) to set up inherited properties";
		PostorderIterator.superclass.init.call(this, objErrors, objRoot);
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end constructor PreorderIterator
//******

//******
function PostIt_first() {
	var strRoutine = "PostIt_first";
	var strAction = "";
	try {
		strAction = "creating a dummy iteratable object";
		var objRoot = new IteratorDummy(this.errors, this.root);

		strAction = "calling getBottom on objRoot";
		this.getBottom(objRoot);

		strAction = "setting the this.firstCalled property to true";
		this.firstCalled = true;
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function PostIt_first
//******

//******
function PostIt_next() {
	var strRoutine = "PostIt_next";
	var strAction = "";
	try {
		strAction = "calling next on the top iterator from the iterator stack";
		var objCurrentIterator = this.getTop();
		objCurrentIterator.next();

		strAction = "checking if the initial top iterator is done";
		if (objCurrentIterator.isDone()) {
			strAction = "popping off the initial top iterator";
			this.iteratorStack.pop();
		} else {
			strAction = "getting the current item of the new top iterator";
			var objCurrentItem = this.getTop().currentItem();

			strAction = "calling getBottom on the new current item";
			this.getBottom(objCurrentItem);
		} //end if the initial top iterator was done
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end function PostIt_next
//******

//******
function PostIt_getBottom(objRoot) {
	var strRoutine = "PostIt_getBottom";
	var strAction = "";
	try {
		strAction = "checking that the input item is defined";
		if (objRoot != undefined) {
			strAction = "calling createIterator on the root object";
			var objNewIterator = objRoot.createIterator();

			strAction = "calling first on the root iterator";
			objNewIterator.first();

			strAction = "checking if the iterator is not done";
			if (!objNewIterator.isDone()) {
				strAction = "pushing the root iterator onto the iteratorstack";
				this.iteratorStack.push(objNewIterator);

				strAction = "getting iterator's current item";
				var objCurItem = objNewIterator.currentItem();

				strAction = "calling getBottom on current item";
				this.getBottom(objCurItem);
			} //end if
		} //end if input item is defined
	} //end try
	catch (e) {
		this.errors.add(this.module, strRoutine, strAction, e);
		throw new Error(strRoutine + " failed");
	} //end catch
} //end PostIt_getBottom
//******
//---------------------------------------------