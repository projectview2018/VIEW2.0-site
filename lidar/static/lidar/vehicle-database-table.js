// get the array of completed scan objects and parse into JSON format
const completed_scan_list_raw = document.getElementById("completed_scan_list");
const completed_scan_data = JSON.parse(completed_scan_list_raw.textContent);

// get the array of vehicle objects and parse into JSON format
const vehicle_list_raw = document.getElementById("vehicle_list");
const data = JSON.parse(vehicle_list_raw.textContent);

// initialize empty object for matching car ids to completed scans
let vehicle_to_scan_dict = {};
// each car id points to an array of objects representing completed scans,
// initially empty
for (let car of data) {
  vehicle_to_scan_dict[car["pk"]] = [];
}
// iterate through the completed scans
// push an object holding the raw scan id and the date added to the array of
// the correct vehicle id
// the info is nested one level down under the `fields` key to make objects
// compatible with sorting function below
for (let scan of completed_scan_data) {
  vehicle_to_scan_dict[scan["vehicle"]].push({
    fields: {
      raw_scan: scan["fields"]["raw_scan"],
      date_added: scan["fields"]["completed_scan_added"].slice(0, 10),
    },
  });
}

// get the base uri of the current page
const table_base_uri = vehicle_list_raw.baseURI;
// get the extension of the vis page - to be used for redirecting when the
// `View` button is clicked
const visual_page_extension = document.currentScript.dataset.visualUrl.slice(
  0,
  -2
);
// get the extension of the current page
const table_page_extension = document.currentScript.dataset.currentUrl;
// make the url of the vis page by removing the current extension from the base
// uri and adding the extension of the vis page
const vis_page_url =
  table_base_uri.slice(0, table_base_uri.indexOf(table_page_extension)) +
  visual_page_extension;

// body classes - used for populating the table
const body_class_list = [
  "N/A",
  "Passenger Cars",
  "Four Tire, Single Unit",
  "Buses",
  "Two Axle, Six Tire, Single Unit",
  "Three Axle, Single Unit",
  "Four or More Axle, Single Unit",
  "Four or Less Axle, Single Trailer",
  "5-Axle Tractor Semitrailer",
  "Six or More Axle, Single Trailer",
  "Five or Less Axle, Multi-Trailer",
  "Six Axle, Multi-Trailer",
  "Seven or More Axle, Multi-Trailer",
];
// make a dict mapping the integer representing the body class to its correct
// string representation
const body_class_dict = {};
body_class_list.forEach((item, index) => {
  body_class_dict[index + 1] = item;
});

// weight classes - used for populating the table
const weight_class_list = [
  "Class 1",
  "Class 2",
  "Class 3",
  "Class 4",
  "Class 5",
  "Class 6",
  "Class 7",
  "Class 8",
];
// make a dict mapping the integer representing the weight class to its correct
// string representation
const weight_class_dict = {};
weight_class_list.forEach((item, index) => {
  weight_class_dict[index + 1] = item;
});

/**
 * Sort a dictionary of objects by a certain field
 *
 * The objects must have the following heirarchy:
 * {
 *  fields: {
 *   field: ...
 *  }
 * }
 *
 * @param {string} field - the field to sort by
 * @returns {function} A sorting function to be passed to Array.prototype.sort()
 */
function compareByField(field) {
  return function (a, b) {
    if (a.fields[field] < b.fields[field]) {
      return -1;
    }
    if (a.fields[field] > b.fields[field]) {
      return 1;
    }
    return 0;
  };
}

/**
 * Check if a is a subsequence of b
 *
 * Letters in a need not be consecutive in b, but must be in the correct order
 *
 * @param {string} a - the potential subsequence
 * @param {string} b - the main string
 * @returns {boolean} true if a is a subsequence of b, false otherwise
 */
function isSubsequence(a, b) {
  // convert to lowercase
  a = a.toLowerCase();
  b = b.toLowerCase();

  // remove non-alphanumeric characters
  a = a.replace(/[^a-zA-Z0-9]/g, "");
  b = b.replace(/[^a-zA-Z0-9]/g, "");

  // check if a is a subsequence of b
  // not need to be consecutive, but need to be in order
  for (let letter of a) {
    if (!b.includes(letter)) {
      return false;
    }
    b = b.slice(b.indexOf(letter) + 1);
  }
  return true;
}

/**
 * Make dropdown of completed scans and view button for last column of each row
 *
 * If there are no completed scans for the vehicle id, return a div with text
 * indicating that there are no associated scans.
 *
 * @param {string} vehicle_id - the number of the vehicle
 * @returns {HTMLDivElement} The element to populate the `Scan Details` field of the table
 */
function createDropdown(vehicle_id) {
  // the completed scans associated with the id
  let select_items = vehicle_to_scan_dict[vehicle_id];
  // wrapper element for the dropdown and button
  let wrapper = document.createElement("div");
  // if no completed scans, return div with text instead
  if (select_items.length === 0) {
    wrapper.innerText = "No Associated Scans";
    return wrapper;
  }
  // sort completed scans by date added, newest to oldest
  select_items = select_items.sort(compareByField("date_added")).toReversed();

  // create select element, add styling, append each completed scan as an
  // option to the dropdown
  let dropdown = document.createElement("select");
  dropdown.classList.add("scan_selector");
  for (ind in select_items) {
    let choice = document.createElement("option");
    choice.value = select_items[ind]["fields"]["raw_scan"];
    choice.innerText = `${select_items[ind]["fields"]["date_added"]}`;
    dropdown.appendChild(choice);
  }

  // create a button that will link to the correct vis page for the date
  // selected
  let submit_button = document.createElement("a");
  submit_button.innerText = "View";
  submit_button.classList.add("containedbutton-inline");

  // instantiate controller for the dropdown and button
  new ViewButtonController(dropdown, submit_button);

  // add dropdown and button to wrapper and return wrapper element
  wrapper.appendChild(dropdown);
  wrapper.appendChild(submit_button);
  return wrapper;
}

class Model {
  /**
   * Create a Model instance
   *
   * Responsible for holding the state of the database table
   */
  constructor() {
    // vehicle fields to be populated into the table
    this.table_fields = [
      "vehicle_updated",
      "vehicle_make",
      "vehicle_model",
      "vehicle_year",
      "vehicle_body_class",
      "vehicle_weight_class",
    ];
    // vehicle data sorted by each field
    this.vehicle_lists = [
      data,
      [...data].sort(compareByField("vehicle_updated")),
      [...data].sort(compareByField("vehicle_make")),
      [...data].sort(compareByField("vehicle_model")),
      [...data].sort(compareByField("vehicle_year")),
    ];
    // the current list from which to populate the table
    this.current_list = this.vehicle_lists[1];

    // modified by search controller
    this.search_field_index = 2; // which field to search into
    this.seach_value = ""; // holds the text entered into the search bar

    // modified by row controller
    this.cars_per_page = 25; // how many vehicle to display per page
    // how many pages are needed to display all vehicles
    this.num_pages = Math.ceil(this.current_list.length / this.cars_per_page);

    // modified by sort controller
    this.vehicle_lists_index = 1; // which of the sorted lists to pull data from
    // whether to reverse the sorted list for ascending vs. decending
    this.reverse = true;

    // modified by page controller
    this.page = null; // current page
    // the start and end vehicle number currently displayed in the table
    // to be shown in the table footer
    this.start_vehicle_num = null;
    this.end_vehicle_num = null;

    // the current set of vehicles displayed in the table - vehicle objects
    this.shown_vehicles = [];
    // a list of functions to call when the page changes
    this.changedPageSubscribers = [];
  }

  /**
   * Return the variable `shown_vehicles`
   *
   * @returns {object} The list of vehicle objects currently shown in the table
   */
  getShownVehicles() {
    return this.shown_vehicles;
  }

  /**
   * Append callback function to the list of page change subscriber functions
   *
   * @param {function} f - callback function to call when page changes
   */
  subChangedPage(f) {
    this.changedPageSubscribers.push(f);
  }

  /**
   * Update the number of pages and change to page 1
   *
   * This function is called when the dropdown selector for number of entries
   * per page is changed.
   */
  updateNumPages() {
    this.num_pages = Math.ceil(this.current_list.length / this.cars_per_page);
    this.changePage(1);
  }

  /**
   * Update the list of vehicles to pull from when populating the table
   *
   * This function is called when there is text entered into or deleted from
   * the search bar. This update preserves the current sorting.
   */
  updateCurrentList() {
    let list = []; // new list to replace current list

    // get the search field
    let search_field = this.table_fields[this.search_field_index];

    // iterate through the vehicles
    for (let vehicle of this.vehicle_lists[this.vehicle_lists_index]) {
      // if search value matches text in the vehicle's field to search from,
      // push it to the list
      if (
        isSubsequence(this.seach_value, vehicle.fields[search_field].toString())
      ) {
        list.push(vehicle);
      }
    }
    // update current list and update num pages needed
    this.current_list = list;
    this.updateNumPages();
  }

  /**
   * Update the list of vehicles shown in the table
   *
   * @param {number} p - the page number to change to
   */
  changePage(p) {
    this.page = p;

    this.shown_vehicles = [];

    // based on the page number choose the start and end index for indexing
    //into current_list
    let start_index = this.cars_per_page * (p - 1);
    let end_index =
      this.current_list.length >= this.cars_per_page * p
        ? this.cars_per_page * p
        : this.current_list.length;

    // populate shown_vehicles from current_list in the correct order
    if (!this.reverse) {
      for (let i = start_index; i < end_index; i++) {
        this.shown_vehicles.push(this.current_list[i]);
      }
    } else {
      for (
        let i = this.current_list.length - end_index;
        i < this.current_list.length - start_index;
        i++
      ) {
        this.shown_vehicles.push(this.current_list[i]);
      }
      this.shown_vehicles.reverse();
    }

    // set the values to be displayed in the table footer
    // i.e. `showing vehicle ___ to ___`
    this.start_vehicle_num = end_index === 0 ? 0 : start_index + 1;
    this.end_vehicle_num = end_index;

    // call all subscriber function that need to be notified when the page
    // changes
    this.changedPageSubscribers.forEach((f) => f(p));
  }
}

class SearchController {
  /**
   * Create a SearchController instance.
   *
   * Responsible for updating the current list of vehicle objects
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // associated model
    this.model = m;
    // get the search bar components from the DOM
    // field dropdown, search text field, clear button
    this.seachColSelector = document.getElementById("search_col_select");
    this.searchBar = document.getElementById("search_bar");
    this.clearButton = document.getElementById("clear_search_bar");
    // set the default field to search from
    this.seachColSelector.value = "2";
    // event handler for search field change
    this.seachColSelector.addEventListener("change", () =>
      this.handleSeachFieldChange()
    );
    // event handler for text input
    this.searchBar.addEventListener("input", (e) => this.handleSearchInput(e));
    // event handler for clear button
    this.clearButton.addEventListener("click", () => this.handleClearSearch());
  }

  /**
   * On search field change, change search field index and update current list.
   */
  handleSeachFieldChange() {
    // set index of field to search from
    this.model.search_field_index = +this.seachColSelector.value;
    // update placeholder text for empty search bar
    this.searchBar.placeholder = `Search for ${
      this.seachColSelector.options[this.model.search_field_index].text
    }`;
    // if text in searchbar, update current list
    if (this.model.seach_value !== "") {
      this.model.updateCurrentList();
    }
  }

  /**
   * Update current list of vehicles based on the value in the search field.
   *
   * @param {object} e - input event
   */
  handleSearchInput(e) {
    // set search value
    this.model.seach_value = e.target.value;
    // update current list
    this.model.updateCurrentList();
  }

  /**
   * Update search bar value and search text on clear button click.
   */
  handleClearSearch() {
    // set search bar value and search value to empty string
    this.searchBar.value = "";
    this.model.seach_value = "";
    // update current list
    this.model.updateCurrentList();
  }
}

class NumRowController {
  /**
   * Create a NumRowController instance
   *
   * Responsible for setting the number of rows in the table.
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // associated model
    this.model = m;
    // num row dropdown
    this.numSelect = document.getElementById("num_row_select");
    // event listener for changed number of rows
    this.numSelect.addEventListener("change", () => this.handleChangedRowNum());
    // callback function when page changes
    m.subChangedPage(() => this.handleChangedPage());
  }

  /**
   * Set the number of cars per page based on dropdown value.
   */
  handleChangedRowNum() {
    let new_num_cars = this.numSelect.value;
    // if value is "All", use the length of the current list
    // else, use the value of the dropdown
    if (new_num_cars === "All") {
      this.model.cars_per_page = this.model.current_list.length;
    } else {
      this.model.cars_per_page = +this.numSelect.value;
    }
    // update the number of pages based on cars per page
    this.model.updateNumPages();
  }

  /**
   * On page change, set value of dropdown to match cars per page.
   */
  handleChangedPage() {
    // if cars per page is the length of the current list, set value to "All"
    // else, use the value of cars per page
    if (this.model.current_list.length === this.model.cars_per_page) {
      this.numSelect.value = "All";
    } else {
      this.numSelect.value = this.model.cars_per_page;
    }
  }
}

class SortController {
  /**
   * Create a SortController instance.
   *
   * Responsible for setting sort parameters based on sort dropdown.
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // associated model
    this.model = m;
    // sort selector dropdown from DOM
    this.sortSelect = document.getElementById("sort_select");
    // event listener for change sort option
    this.sortSelect.addEventListener("change", () => this.handleChangedSort());
    // callback function when the page changes
    m.subChangedPage(() => this.handleChangedPage());
  }

  /**
   * Choose index of sorted list and reverse based on dropdown value.
   */
  handleChangedSort() {
    // index of vehicle list is the same for each asc./desc. pair
    this.model.vehicle_lists_index = Math.ceil(this.sortSelect.value / 2);
    // set reverse based on parity of dropdown value (every other is reversed)
    if (this.sortSelect.value % 2 === 0 && this.sortSelect.value != 0) {
      this.model.reverse = true;
    } else {
      this.model.reverse = false;
    }
    // update current list
    this.model.updateCurrentList();
  }

  /**
   * On page change, set the sort select value based on the vehicle list index.
   */
  handleChangedPage() {
    // if vehicle list index is 0, set the sort select value to 0
    // else, multiple by two and subtract 1 if not reversed
    this.sortSelect.value =
      this.model.vehicle_lists_index === 0
        ? this.model.vehicle_lists_index
        : 2 * this.model.vehicle_lists_index - !this.model.reverse;
  }
}

class TableView {
  /**
   * Create a TableView instance.
   *
   * Responsible for populating the rows of the table from the vehicle objects.
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // the associated model
    this.model = m;
    // the table element from the DOM
    this.table = document.getElementById("vehicle_table");
    // callback function on page change
    m.subChangedPage(() => this.handleChangedPage());
  }

  /**
   * On page change, clear the current table and populate the updated rows.
   */
  handleChangedPage() {
    // remove all of the old rows of the table
    while (this.table.children.length > 1) {
      this.table.removeChild(this.table.children[1]);
    }
    // iterate through each of the vehicles to be shown
    for (let vehicle of this.model.getShownVehicles()) {
      // create table row element and append to table
      let row = document.createElement("tr");
      row.classList.add("elevation01");
      this.table.appendChild(row);
      // iterate through the fields that go in the table
      for (let index in this.model.table_fields) {
        // create a table cell element
        let col = document.createElement("td");
        // if the field is body or weight class,
        // look up the correct text in the tables defined above
        // else, use the text in the vehicle object's field
        if (this.model.table_fields[index] === "vehicle_body_class") {
          col.innerText =
            body_class_dict[vehicle.fields[this.model.table_fields[index]]];
        } else if (this.model.table_fields[index] === "vehicle_weight_class") {
          col.innerText =
            weight_class_dict[vehicle.fields[this.model.table_fields[index]]];
        } else {
          col.innerText = vehicle.fields[this.model.table_fields[index]];
        }
        // add special class to leftmost (first) field
        if (+index === 0) {
          col.classList.add("left_cell");
        }
        // append cell to row
        row.appendChild(col);
      }
      // create an extra cell for the view button
      let id = document.createElement("td");
      // add special class to rightmost (last) field
      id.classList.add("right_cell");
      // create dropdown
      let dropdown = createDropdown(vehicle.pk);
      // append cell to row
      row.appendChild(id);
      // append dropdown to cell
      id.appendChild(dropdown);
    }
  }
}

class ViewButtonController {
  /**
   * Create a ViewButtonController instance.
   *
   * Responsible for updating link on view button based on dropdown value.
   *
   * @param {HTMLSelectElement} d - dropdown select element
   * @param {HTMLAnchorElement} b - link element (view button)
   */
  constructor(d, b) {
    // associated dropdown
    this.dropdown = d;
    // associated button
    this.button = b;
    // the value of the dropdown corresponding to a scan number
    this.scan_num = this.dropdown.value;
    // create the link to the vis page based on the scan number
    this.button.href = vis_page_url + "/" + this.scan_num;

    // event listener for dropdown change
    this.dropdown.addEventListener("change", () => this.handleChangedView());
  }

  /**
   * On scan dropdown change, edit the button url.
   */
  handleChangedView() {
    // set the new scan number
    this.scan_num = this.dropdown.value;
    // set the new url
    this.button.href = vis_page_url + "/" + this.scan_num;
  }
}

class LabelView {
  /**
   *  Create a LabelView instance.
   *
   * Responsible for setting the text at the bottom left of the table.
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // associated model
    this.model = m;
    // label element from the DOM
    this.label = document.getElementById("entry_indicator");
    // callback function for changed page
    m.subChangedPage(() => this.handleChangedPage());
  }

  /**
   * On page change, set the start/end vehicle text at the bottom of the table.
   */
  handleChangedPage() {
    this.label.innerText = `Showing ${this.model.start_vehicle_num}-${this.model.end_vehicle_num} of ${this.model.current_list.length} entries`;
  }
}

class PageSelectorViewController {
  /**
   * Create a PageSelectorViewController instance
   *
   * Responsible for creating the page buttons at the bottom right of the table
   *
   * @param {object} m - an instance of the Model class
   */
  constructor(m) {
    // accociated model
    this.model = m;
    // page selector element from DOM
    this.pageSelector = document.getElementById("pagination");
    // callback function for page change
    m.subChangedPage(() => this.handleChangedPage());
  }

  /**
   * On page change, update the pagintation buttons at the bottom of the table.
   */
  handleChangedPage() {
    // remove the old pagination buttons
    while (this.pageSelector.children.length > 0) {
      this.pageSelector.removeChild(this.pageSelector.children[0]);
    }

    // set the start page - should be two behind the current page,
    // unless current page is 1 or 2
    let start_page = this.model.page - 2 > 0 ? this.model.page - 2 : 1;
    // set the end page to be 4 more than start page (or max of num_pages)
    let end_page =
      start_page + 4 <= this.model.num_pages
        ? start_page + 4
        : this.model.num_pages;

    // create link element to jump to first page and add classes
    let first_page = document.createElement("a");
    first_page.innerText = "<< First";
    first_page.dataset.pagenum = 1;
    first_page.classList.add("pagination_elt", "page_turn");
    // button should be clickable if not alread on first page
    // add event listener for click
    if (this.model.page !== 1) {
      first_page.addEventListener("click", (e) => this.handlePageChange(e));
      first_page.classList.add("clickable_page");
    } else {
      first_page.classList.add("unclickable_page");
    }
    // append button to page selector
    this.pageSelector.appendChild(first_page);

    // create link element to jump back one page and add classes
    let prev_page = document.createElement("a");
    prev_page.innerText = "< Previous";
    prev_page.dataset.pagenum = this.model.page - 1;
    prev_page.classList.add("pagination_elt", "page_turn");
    // should be clickable if current page is not 1
    // add event listener for click
    if (this.model.page !== 1) {
      prev_page.addEventListener("click", (e) => this.handlePageChange(e));
      prev_page.classList.add("clickable_page");
    } else {
      prev_page.classList.add("unclickable_page");
    }
    // append button to page selector
    this.pageSelector.appendChild(prev_page);

    // loop through the page numbers
    for (let i = start_page; i <= end_page; i++) {
      // create link element and add classes
      let curr_page = document.createElement("a");
      curr_page.innerText = `${i}`;
      curr_page.dataset.pagenum = i;
      curr_page.classList.add("pagination_elt");
      // should be clickable if not current page
      // add event listener for click
      // else, add special styling for current page
      if (i !== this.model.page) {
        curr_page.addEventListener("click", (e) => this.handlePageChange(e));
        curr_page.classList.add("clickable_page");
      } else {
        curr_page.classList.add("current_page");
      }
      // append to page selector
      this.pageSelector.appendChild(curr_page);
    }

    // create link element to jump forward one page and add classes
    let next_page = document.createElement("a");
    next_page.innerText = "Next >";
    next_page.dataset.pagenum = this.model.page + 1;
    next_page.classList.add("pagination_elt", "page_turn");
    // should be clickable if not on last page
    // add event listener for click
    if (this.model.page !== this.model.num_pages) {
      next_page.addEventListener("click", (e) => this.handlePageChange(e));
      next_page.classList.add("clickable_page");
    } else {
      next_page.classList.add("unclickable_page");
    }
    // append to page selector
    this.pageSelector.appendChild(next_page);

    // create link to jump to last page and add classes
    let last_page = document.createElement("a");
    last_page.innerText = "Last >>";
    last_page.dataset.pagenum = this.model.num_pages;
    last_page.classList.add("pagination_elt", "page_turn");
    // should be clickable if not on last page
    // add event listener for click
    if (this.model.page !== this.model.num_pages) {
      last_page.addEventListener("click", (e) => this.handlePageChange(e));
      last_page.classList.add("clickable_page");
    } else {
      last_page.classList.add("unclickable_page");
    }
    // append to page selector
    this.pageSelector.appendChild(last_page);
  }

  /**
   * Callback function to change the page to the clicked vutton value
   *
   * @param {object} e - click event
   */
  handlePageChange(e) {
    this.model.changePage(+e.target.dataset.pagenum);
  }
}

/**
 * Initialize model, controllers, and views
 */
function init() {
  const model = new Model();
  new SearchController(model);
  new NumRowController(model);
  new SortController(model);
  new TableView(model);
  new LabelView(model);
  new PageSelectorViewController(model);

  // set initial state of the model
  model.changePage(1);
}

// on page load, run init function
window.addEventListener("load", init);
