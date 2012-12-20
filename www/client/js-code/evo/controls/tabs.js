/*
tabs.js

Default handling methods for tabbed web interfaces.

NB: will only work if associated tab html template has been used to create
the interface.

Revision History:
Written 2003 by Amanda Birmingham
*/

//******
selectTab.selectedType = "basic";

function selectTab(strTabType) {
	strAction = "making the class of the current tab = offFormatTab";
	document.getElementById(selectTab.selectedType + "Cell").className = "offFormatCell";
	strAction = "making the display of the corresponding palette = none";
	document.getElementById(selectTab.selectedType + "Palette").style.display = "none";

	strAction = "changing the current tab to be the new strTabType: " + strTabType;
	selectTab.selectedType = strTabType;
	strAction = "making current tab's class = onFormatTab";
	document.getElementById(selectTab.selectedType + "Cell").className = "";
	strAction = "making the display of the corresponding palette = block";
	document.getElementById(selectTab.selectedType + "Palette").style.display = "block";
} //end function selectTab
//******