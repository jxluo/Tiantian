/**
 * Javascript for home view.
 */

home = {};

/**
 * Start run script when body is loaded.
 */
startScript = function () {
  var inputButtonElem = document.getElementsByClassName('home-input-button')[0];
  
  home.inputElem = document.getElementById('input');

  document.addEventListener('keydown', home.handleKeyDown, false);
};

home.navigateToResult = function(nameStr) {
  var url = '/result/' + nameStr;
  window.location.href = url;
};

home.handleInputButtonClick = function() {
  var value = home.inputElem.value;
  if (home.checkInputValue(value)) {
    home.navigateToResult(value);
  } else {
    home.handleInvalidInputValue(value);
  }
};

home.handleKeyDown = function(e) {
  if (!e.altKey && !e.ctrlKey && !e.shiftKey && e.keyCode == 13) {
    home.handleInputButtonClick();
  }
}


home.checkInputValue = function(str) {
  return true;
};

home.handleInvalidInputValue = function(str) {
};
