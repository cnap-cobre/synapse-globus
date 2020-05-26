/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 4);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/assets/scripts/pages/tb_datatables.js":
/*!***************************************************!*\
  !*** ./src/assets/scripts/pages/tb_datatables.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

var TB_datatables = function () {
  var initDatatable = function initDatatable() {
    $('.init-datatable').DataTable();
  };

  var initDatatableAddRows = function initDatatableAddRows() {
    var table = $('#dt-addrows').DataTable();
    var counter = 1;
    $('#btn-addrow').on('click', function (e) {
      e.preventDefault();
      table.row.add([counter + '.1', counter + '.2', counter + '.3', counter + '.4', counter + '.5']).draw(false);
      counter++;
    }); // Automatically add a first row of data

    $('#btn-addrow').click();
  };

  var initEventDatatable = function initEventDatatable() {
    var table = $('#dt-event').DataTable();
    $('#dt-event tbody').on('click', 'tr', function () {
      var data = table.row(this).data();
      alert('You clicked on ' + data[0] + '\'s row');
    });
  };

  var initMultiRowSelection = function initMultiRowSelection() {
    var table = $('#dt-multirowselection').DataTable();
    $('#dt-multirowselection tbody').on('click', 'tr', function () {
      $(this).toggleClass('selected');
    });
  };

  var initRowSelection = function initRowSelection() {
    var table = $('#dt-rowselection').DataTable();
    $('#dt-rowselection tbody').on('click', 'tr', function () {
      if ($(this).hasClass('selected')) {
        $(this).removeClass('selected');
      } else {
        table.$('tr.selected').removeClass('selected');
        $(this).addClass('selected');
      }
    });
    $('.btn-deleterow').click(function () {
      table.row('.selected').remove().draw(false);
    });
  };

  var initFormInputs = function initFormInputs() {
    var table = $('#dt-forminputs').DataTable();
    $('.btn-forminputs').click(function () {
      var data = table.$('input, select').serialize();
      alert("The following data would have been submitted to the server: \n\n" + data.substr(0, 120) + '...');
      return false;
    });
  };

  var initShowHideColumn = function initShowHideColumn() {
    var table = $('#dt-showhidecolumn').DataTable({
      'scrollY': '200px',
      'paging': false
    });
    $('.toggle-column').change(function () {
      var column = table.column($(this).attr('data-column'));

      if ($(this).prop('checked')) {
        column.visible(true);
      } else {
        column.visible(false);
      }
    });
  };

  return {
    init: function init() {
      initDatatable();
      initDatatableAddRows();
      initEventDatatable();
      initMultiRowSelection();
      initRowSelection();
      initFormInputs();
      initShowHideColumn();
    }
  };
}();

$(function () {
  TB_datatables.init();
});

/***/ }),

/***/ 4:
/*!*********************************************************!*\
  !*** multi ./src/assets/scripts/pages/tb_datatables.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! C:\temp\siqtheme\src\assets\scripts\pages\tb_datatables.js */"./src/assets/scripts/pages/tb_datatables.js");


/***/ })

/******/ });