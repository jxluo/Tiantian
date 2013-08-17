/**
 * Javascript for base view.
 */

base = {};

/**
 * Init search events.
 */
base.initSearchComponent = function () {
  
  base.inputElem = document.getElementsByClassName('base-search-input')[0];
  document.addEventListener('keydown', base.handleKeyDown, false);
};

base.navigateToResult = function(nameStr) {
  var url = '/result/' + nameStr;
  window.location.href = url;
};

base.handleInputButtonClick = function() {
  var value = base.inputElem.value;
  if (base.checkInputValue(value)) {
    base.navigateToResult(value);
  } else {
    base.handleInvalidInputValue(value);
  }
};

base.handleKeyDown = function(e) {
  if (!e.altKey && !e.ctrlKey && !e.shiftKey && e.keyCode == 13) {
    base.handleInputButtonClick();
  }
}


base.checkInputValue = function(str) {
  return true;
};

base.handleInvalidInputValue = null;
