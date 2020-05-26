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
/******/ 	return __webpack_require__(__webpack_require__.s = 6);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/assets/scripts/pages/ch_apexcharts.js":
/*!***************************************************!*\
  !*** ./src/assets/scripts/pages/ch_apexcharts.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

window.Apex = {
  chart: {
    foreColor: '#999'
  }
};

var Apex = function () {
  var trigoStrength = 3;
  var iteration = 11;

  var chart1 = function chart1() {
    var optionsChart1 = {
      chart: {
        height: 350,
        type: 'bar',
        foreColor: '#999',
        animations: {
          enabled: true,
          easing: 'linear',
          dynamicAnimation: {
            speed: 1000
          }
        },
        dropShadow: {
          enabled: true,
          left: -14,
          top: -10,
          opacity: 0.05
        },
        events: {
          animationEnd: function animationEnd(chartCtx) {
            var newData = chartCtx.w.config.series[0].data.slice();
            newData.shift();
            window.setTimeout(function () {
              chartCtx.updateOptions({
                series: [{
                  data: newData
                }],
                xaxis: {
                  min: chartCtx.minX,
                  max: chartCtx.maxX
                },
                subtitle: {
                  text: parseInt(Apex.getRangeRandom({
                    min: 1,
                    max: 20
                  })).toString() + '%'
                }
              }, false, false);
            }, 300);
          }
        },
        toolbar: {
          show: false
        },
        zoom: {
          enabled: false
        }
      },
      colors: ['#FCCF31', '#17ead9', '#f02fc2'],
      grid: {
        borderColor: "#999"
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        width: 0
      },
      series: [{
        name: 'Load Average',
        data: Apex.generateMinuteWiseTimeSeries(new Date("12/12/2016 00:20:00").getTime(), 12, {
          min: 10,
          max: 110
        })
      }],
      title: {
        text: 'Load Average',
        align: 'left',
        style: {
          fontSize: '12px'
        }
      },
      subtitle: {
        text: '20%',
        floating: true,
        align: 'right',
        offsetY: 0,
        style: {
          fontSize: '22px'
        }
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          type: 'vertical',
          shadeIntensity: 0.5,
          inverseColors: false,
          opacityFrom: 1,
          opacityTo: 0.8,
          stops: [0, 100],
          gradientToColors: ['#F55555', '#6078ea', '#6094ea']
        }
      },
      xaxis: {
        type: 'datetime',
        range: 2700000,
        axisTicks: {
          color: '#333'
        },
        axisBorder: {
          color: "#333"
        }
      },
      yaxis: {
        decimalsInFloat: 2,
        opposite: true,
        labels: {
          offsetX: -10
        }
      },
      legend: {
        show: true
      }
    };
    var chartColumn = new ApexCharts(document.querySelector("#chart1"), optionsChart1);
    chartColumn.render();
    setInterval(function () {
      iteration++;
      chartColumn.updateSeries([{
        data: [].concat(_toConsumableArray(chartColumn.w.config.series[0].data), [[chartColumn.w.globals.maxX + 210000, Apex.getRandom()]])
      }]);
    }, 3000);
  };

  var chart2 = function chart2() {
    var options = {
      series: [{
        name: 'Likes',
        data: [4, 3, 10, 9, 29, 19, 22, 9, 12, 7, 19, 5, 13, 9, 17, 2, 7, 5]
      }],
      chart: {
        height: 350,
        type: 'line'
      },
      stroke: {
        width: 7,
        curve: 'smooth'
      },
      xaxis: {
        type: 'datetime',
        categories: ['1/11/2000', '2/11/2000', '3/11/2000', '4/11/2000', '5/11/2000', '6/11/2000', '7/11/2000', '8/11/2000', '9/11/2000', '10/11/2000', '11/11/2000', '12/11/2000', '1/11/2001', '2/11/2001', '3/11/2001', '4/11/2001', '5/11/2001', '6/11/2001']
      },
      title: {
        text: 'Social Media',
        align: 'left',
        style: {
          fontSize: "16px",
          color: '#666'
        }
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          gradientToColors: ['#FDD835'],
          shadeIntensity: 1,
          type: 'horizontal',
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100, 100, 100]
        }
      },
      markers: {
        size: 4,
        colors: ["#FFA41B"],
        strokeColors: "#fff",
        strokeWidth: 2,
        hover: {
          size: 7
        }
      },
      yaxis: {
        min: -10,
        max: 40,
        title: {
          text: 'Engagement'
        }
      }
    };
    var chart = new ApexCharts(document.querySelector("#chart2"), options);
    chart.render();
  };

  var chart3 = function chart3() {
    var options = {
      series: [{
        name: 'TEAM A',
        type: 'column',
        data: [23, 11, 22, 27, 13, 22, 37, 21, 44, 22, 30]
      }, {
        name: 'TEAM B',
        type: 'area',
        data: [44, 55, 41, 67, 22, 43, 21, 41, 56, 27, 43]
      }, {
        name: 'TEAM C',
        type: 'line',
        data: [30, 25, 36, 30, 45, 35, 64, 52, 59, 36, 39]
      }],
      chart: {
        height: 350,
        type: 'line',
        stacked: false
      },
      stroke: {
        width: [0, 2, 5],
        curve: 'smooth'
      },
      plotOptions: {
        bar: {
          columnWidth: '50%'
        }
      },
      fill: {
        opacity: [0.85, 0.25, 1],
        gradient: {
          inverseColors: false,
          shade: 'light',
          type: "vertical",
          opacityFrom: 0.85,
          opacityTo: 0.55,
          stops: [0, 100, 100, 100]
        }
      },
      labels: ['01/01/2003', '02/01/2003', '03/01/2003', '04/01/2003', '05/01/2003', '06/01/2003', '07/01/2003', '08/01/2003', '09/01/2003', '10/01/2003', '11/01/2003'],
      markers: {
        size: 0
      },
      xaxis: {
        type: 'datetime'
      },
      yaxis: {
        title: {
          text: 'Points'
        },
        min: 0
      },
      tooltip: {
        shared: true,
        intersect: false,
        y: {
          formatter: function formatter(y) {
            if (typeof y !== "undefined") {
              return y.toFixed(0) + " points";
            }

            return y;
          }
        }
      }
    };
    var chart = new ApexCharts(document.querySelector("#chart3"), options);
    chart.render();
  };

  var chart4 = function chart4() {
    var options = {
      series: [44, 55, 41, 17, 15],
      chart: {
        type: 'donut'
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    };
    var chart = new ApexCharts(document.querySelector("#chart4"), options);
    chart.render();
  };

  var chart5 = function chart5() {
    var options = {
      series: [76, 67, 61, 90],
      chart: {
        height: 390,
        type: 'radialBar'
      },
      plotOptions: {
        radialBar: {
          offsetY: 0,
          startAngle: 0,
          endAngle: 270,
          hollow: {
            margin: 5,
            size: '30%',
            background: 'transparent',
            image: undefined
          },
          dataLabels: {
            name: {
              show: false
            },
            value: {
              show: false
            }
          }
        }
      },
      colors: ['#E84A67', '#17BA91', '#0080FE', '#F9A602'],
      labels: ['Vimeo', 'Messenger', 'Facebook', 'LinkedIn'],
      legend: {
        show: true,
        floating: true,
        fontSize: '16px',
        position: 'left',
        offsetX: 60,
        offsetY: 15,
        labels: {
          useSeriesColors: true
        },
        markers: {
          size: 0
        },
        formatter: function formatter(seriesName, opts) {
          return seriesName + ":  " + opts.w.globals.series[opts.seriesIndex];
        },
        itemMargin: {
          vertical: 3
        }
      },
      responsive: [{
        breakpoint: 480,
        options: {
          legend: {
            show: false
          }
        }
      }]
    };
    var chart = new ApexCharts(document.querySelector("#chart5"), options);
    chart.render();
  };

  var chart6 = function chart6() {
    var options = {
      series: [{
        name: 'Website Blog',
        type: 'column',
        data: [440, 505, 414, 671, 227, 413, 201, 352, 752, 320, 257, 160]
      }, {
        name: 'Social Media',
        type: 'line',
        data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16]
      }],
      chart: {
        height: 350,
        type: 'line'
      },
      stroke: {
        width: [0, 4]
      },
      title: {
        text: 'Traffic Sources'
      },
      dataLabels: {
        enabled: true,
        enabledOnSeries: [1]
      },
      labels: ['01 Jan 2001', '02 Jan 2001', '03 Jan 2001', '04 Jan 2001', '05 Jan 2001', '06 Jan 2001', '07 Jan 2001', '08 Jan 2001', '09 Jan 2001', '10 Jan 2001', '11 Jan 2001', '12 Jan 2001'],
      xaxis: {
        type: 'datetime'
      },
      yaxis: [{
        title: {
          text: 'Website Blog'
        }
      }, {
        opposite: true,
        title: {
          text: 'Social Media'
        }
      }]
    };
    var chart = new ApexCharts(document.querySelector("#chart6"), options);
    chart.render();
  };

  var chart7 = function chart7() {
    var options = {
      series: [{
        name: 'Servings',
        data: [44, 55, 41, 67, 22, 43, 21, 33, 45, 31, 87, 65, 35]
      }],
      annotations: {
        points: [{
          x: 'Bananas',
          seriesIndex: 0,
          label: {
            borderColor: '#775DD0',
            offsetY: 0,
            style: {
              color: '#fff',
              background: '#775DD0'
            },
            text: 'Bananas are good'
          }
        }]
      },
      chart: {
        height: 350,
        type: 'bar'
      },
      plotOptions: {
        bar: {
          columnWidth: '50%',
          endingShape: 'rounded'
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        width: 2
      },
      xaxis: {
        labels: {
          rotate: -45
        },
        categories: ['Apples', 'Oranges', 'Strawberries', 'Pineapples', 'Mangoes', 'Bananas', 'Blackberries', 'Pears', 'Watermelons', 'Cherries', 'Pomegranates', 'Tangerines', 'Papayas'],
        tickPlacement: 'on'
      },
      yaxis: {
        title: {
          text: 'Servings'
        }
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'light',
          type: "horizontal",
          shadeIntensity: 0.25,
          gradientToColors: undefined,
          inverseColors: true,
          opacityFrom: 0.85,
          opacityTo: 0.85,
          stops: [50, 0, 100]
        }
      }
    };
    var chart = new ApexCharts(document.querySelector("#chart7"), options);
    chart.render();
  };

  return {
    init: function init() {
      chart1();
      chart2();
      chart3();
      chart4();
      chart5();
      chart6();
      chart7();
    },
    getRandom: function getRandom() {
      var i = iteration;
      return (Math.sin(i / trigoStrength) * (i / trigoStrength) + i / trigoStrength + 1) * (trigoStrength * 2);
    },
    getRangeRandom: function getRangeRandom(yrange) {
      return Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
    },
    generateMinuteWiseTimeSeries: function generateMinuteWiseTimeSeries(baseval, count, yrange) {
      var i = 0;
      var series = [];

      while (i < count) {
        var x = baseval;
        var y = (Math.sin(i / trigoStrength) * (i / trigoStrength) + i / trigoStrength + 1) * (trigoStrength * 2);
        series.push([x, y]);
        baseval += 300000;
        i++;
      }

      return series;
    }
  };
}();

$(function () {
  Apex.init();
});

/***/ }),

/***/ 6:
/*!*********************************************************!*\
  !*** multi ./src/assets/scripts/pages/ch_apexcharts.js ***!
  \*********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! C:\temp\siqtheme\src\assets\scripts\pages\ch_apexcharts.js */"./src/assets/scripts/pages/ch_apexcharts.js");


/***/ })

/******/ });