/*
timers.js

GlobalTimer, an object that collects and displays profiling information on
javascript functions that have had timer calls inserted into them.  This
module is used by the javascript profiler under development by
Amanda Birmingham.

This is the best version of the old iTimer family. For each individual
timer, it uses a hash containing (if necessary) an array--this is less
elegant than using a Timer object, but it also adds a lot less
performance degradation.  Furthermore, the internal array (holding
references to child timer hashes) is only inited if the function being
timed actually turns out to call a child function.  This saved a
whopping 10% execution time in my tests.  Wow!

Revision History:
*/


//--------------------------------------------
//******
function GlobalTimer() {
	this.timerStack = new Array();
	this.topFuncCalls = new Array();
} //end GlobalTimer constructor

GlobalTimer.prototype.END = "GT_END";
GlobalTimer.prototype.start = GT_start;
GlobalTimer.prototype.stop = GT_stop;
GlobalTimer.prototype.summarize = GT_summarize;
GlobalTimer.prototype.showResults = GT_showResults;

//The following are functions that OUGHT to go in their own
//Timer object, only they can't because of performance concerns
GlobalTimer.prototype.makeTimer = GT_makeTimer;
GlobalTimer.prototype.stopTimer = GT_stopTimer;
GlobalTimer.prototype.addChildTimer = GT_addChildTimer;

//summary functions:
GlobalTimer.prototype.summarizeTimer = GT_summarizeTimer;
GlobalTimer.prototype.summarizeAggregate = GT_summarizeAggregate;
GlobalTimer.prototype.getTimerSummaryString = GT_getTimerSummaryString;
GlobalTimer.prototype.sumUnaggregatableTimer = GT_sumUnaggregatableTimer;
GlobalTimer.prototype.sumAggregatableTimer = GT_sumAggregatableTimer;
GlobalTimer.prototype.resetTimerAggregate = GT_resetTimerAggregate;
//******

//******
function GT_start(strFunctionName) {
	//create a timer for the function
	var arrNewTimer = this.makeTimer(strFunctionName);

	//push it onto the stack
	this.timerStack.push(arrNewTimer);
} //end function GT_start
//******

//******
function GT_stop(strFunctionName) {
	var objTimerStack = this.timerStack;

	//pop the top entry off the stack
	var objCurTimer = objTimerStack.pop();

	//stop it
	this.stopTimer(objCurTimer);

	//if there are any items left on the stack
	var intStackLength = objTimerStack.length ;
	if (intStackLength > 0) {
		//call addChildTimer on the new top of the stack
		this.addChildTimer(objTimerStack[intStackLength-1], objCurTimer);
	} else {
		//add this timer to the list of top calls
		this.topFuncCalls.push(objCurTimer);
	} //end if
} //end function GT_stop
//******

//******
function GT_summarize() {
	var strSummary = "";
	var arrTopFuncCalls = this.topFuncCalls;

	//add a sentinal to the end of the list so that
	//the timer aggregation knows when to stop
	arrTopFuncCalls.push(this.makeTimer(this.END));

	//call summarize on each top function call
	for (var intIndex in arrTopFuncCalls) {
		strSummary += this.summarizeTimer(arrTopFuncCalls[intIndex]);
	} //next top call

	return strSummary;
} //end function GT_summarize
//******

//******
function GT_showResults() {
	//open a results window
	var hndResultsWin = window.open("", "resultsWin", "directories=no,location=no,menubar=no,resizable=yes,scrollbars=yes,status=no,toolbar=no,titlebar=no");

	//summarize the results and write to new win
	hndResultsWin.document.write("<strong>Summarizing Profiler Results ....</strong><br />");

	//summarize the results and write to new win
	hndResultsWin.document.write(this.summarize());
} //end function GT_showResults
//******

//--------------------------------------------

//--------------------------------------------
//The methods of GlobalTimer that make up the
//Timer pseudo-object

//******
function GT_makeTimer(strFunctionName) {
	//create a new array
	var arrFuncTimer = new Array();

	//put the function name in the first slot
	arrFuncTimer["name"] = strFunctionName;

	//put the start time in the second slot
	arrFuncTimer["time"] = new Date().getTime();

	//put a new array in the fourth slot
	//arrFuncTimer["children"] = new Array();

	return arrFuncTimer;
} //end function GT_makeTimer
//******

//******
function GT_stopTimer(arrCurTimer) {
	arrCurTimer["time"] = new Date().getTime() - arrCurTimer["time"];
	//arrCurTimer["stop"] = new Date().getTime();
} //end function GT_stopTimer
//******

//******
function GT_addChildTimer(arrParentTimer, arrChildTimer) {
	//create a child timer array if none exists
	if (arrParentTimer["children"] == undefined) {
		arrParentTimer["children"] = new Array();
	} //end if

	//get the child timer array out of the parent timer
	var arrChildTimers = arrParentTimer["children"];

	//push the new child timer onto it
	arrChildTimers.push(arrChildTimer);
} //end function GT_addChildTimer
//******
//--------------------------------------------

//--------------------------------------------
//The methods of the GlobalTimer object that
//are associated with summarizing each timer:

//******
//calling this with no arguments resets it to empty
function GT_resetTimerAggregate(ascTimerAggregate, strName, fltTime, strIndent) {
	ascTimerAggregate["name"] = strName;
	ascTimerAggregate["times"] = new Array();
	if (fltTime != undefined) {ascTimerAggregate["times"].push(fltTime);}

	if (strIndent == undefined) {strIndent = "";}
	ascTimerAggregate["indent"] = strIndent;
} //end function GT_resetTimerAggregate
//******


//******
GT_summarizeTimer.timerAggregate = new Array(); //static variable
function GT_summarizeTimer(arrCurTimer, strIndent) {
	var strSummary;

	//if strIndent is undefined, it is an empty string
	if (strIndent == undefined) {strIndent = "";}

	//loop through each child timer, calling summarize
	var arrChildTimers = arrCurTimer["children"];
	if (arrChildTimers) {
		//sum unaggregatable timer
		strSummary = this.sumUnaggregatableTimer(arrCurTimer, strIndent, GT_summarizeTimer.timerAggregate);
	} else {
		//sum aggregatable timer
		strSummary = this.sumAggregatableTimer(arrCurTimer, strIndent, GT_summarizeTimer.timerAggregate);
	} //end if there ARE any child timers

	return strSummary;
} //end function GT_summarizeTimer
//******

//******
function GT_sumUnaggregatableTimer(arrCurTimer, strIndent, ascTimerAggregate) {
	var strSummary = "";

	//if a current aggregate exists
	if (ascTimerAggregate["name"] != undefined) {
		//summarize it
		strSummary += this.summarizeAggregate(ascTimerAggregate, strIndent);

		//blank it out
		this.resetTimerAggregate(ascTimerAggregate);
	} //end if aggregate exists

	//summarize this timer
	strSummary += this.getTimerSummaryString(arrCurTimer, strIndent);

	//increase the indent by one tab
	strIndent += GT_getTimerSummaryString.indentChar;

	//loop through its children and summarize them
	var arrChildTimers = arrCurTimer["children"];
	for (var intIndex in arrChildTimers) {
		strSummary += this.summarizeTimer(arrChildTimers[intIndex], strIndent);
	} //next child timer

	return strSummary;
} //end function GT_sumUnaggregatableTimer
//******

//******
function GT_sumAggregatableTimer(arrCurTimer, strIndent, ascTimerAggregate) {
	var strSummary = "";

	var strName = arrCurTimer["name"];
	var fltTime = arrCurTimer["time"];

	//switch on if current aggregate exists
	switch (ascTimerAggregate["name"] != undefined) {
		case true:
			//if its name matches that of cur timer
			if (ascTimerAggregate["name"] == strName) {
				//add cur time to its array
				ascTimerAggregate["times"].push(fltTime);
				break;
			} else {
				//summarize it
				strSummary = this.summarizeAggregate(ascTimerAggregate, strIndent);
			} //end if
			//NB: intentional fallthrough for "else" case
		case false:
			//reset the timer aggregate to contain the info for this timer
			this.resetTimerAggregate(ascTimerAggregate, strName, fltTime, strIndent);
	} //end switch

	return strSummary;
} //end function GT_sumAggregatableTimer
//******

//******
GT_getTimerSummaryString.lineEndChar = "<br />";
GT_getTimerSummaryString.indentChar = "&nbsp;&nbsp;";
function GT_getTimerSummaryString(arrCurTimer, strIndent) {
	var strSummary;

	//if strIndent is undefined, it is an empty string
	if (strIndent == undefined) {strIndent = "";}

	//create a string with the time and the function name
	strSummary = strIndent + arrCurTimer["name"] + ": " + arrCurTimer["time"] + GT_getTimerSummaryString.lineEndChar;

	return strSummary;
} //end function GT_getTimerSummaryString
//******

//******
function GT_summarizeAggregate(ascTimerAggregate, strIndent) {
	var intDecimals = 1;

	//if strIndent is undefined, it is an empty string
	if (strIndent == undefined) {strIndent = "";}

	var arrTimes = ascTimerAggregate["times"];

	//get the length of the time array
	var intNumTimes = arrTimes.length;

	if (intNumTimes < 2) {
		var ascNewTimer = new Array();
		ascNewTimer["name"] = ascTimerAggregate["name"];
		ascNewTimer["time"] = ascTimerAggregate["times"][0];

		strSummary = this.getTimerSummaryString(ascNewTimer, ascTimerAggregate["indent"]);
	} else {

		//get the num list statistics of the time array
		var ascStats = getNumListStats(arrTimes);

		//generate the summary string
		var strSummary = ascTimerAggregate["indent"] + ascTimerAggregate["name"] + ": total time: " + ascStats["sum"].toFixed(0) +
						"; calls: " + intNumTimes + "; avg. time: " + ascStats["average"].toFixed(intDecimals) +
						"; stddev: " + ascStats["stddev"].toFixed(intDecimals) + GT_getTimerSummaryString.lineEndChar;
	} //end if

	return strSummary;
} //end function GT_summarizeAggregate
//******
//--------------------------------------------