const completed_scan_list_raw = document.getElementById("completed_scan_list");
const completed_scan_data = JSON.parse(completed_scan_list_raw.textContent);

const vehicle_list_raw = document.getElementById("vehicle_list");
const data = JSON.parse(vehicle_list_raw.textContent);

let vehicle_to_scan_dict = [];
for (let car of data) {
  vehicle_to_scan_dict[car["pk"]] = [];
}
for (let scan of completed_scan_data) {
  vehicle_to_scan_dict[scan["vehicle"]].push({
    fields: {
      raw_scan: scan["fields"]["raw_scan"],
      date_added: scan["fields"]["completed_scan_added"].slice(0, 10),
    },
  });
}

const table_base_uri = vehicle_list_raw.baseURI;
const visual_page_extension = document.currentScript.dataset.visualUrl.slice(
  0,
  -2
);
const table_page_extension = document.currentScript.dataset.currentUrl;
const vis_page_url =
  table_base_uri.slice(0, table_base_uri.indexOf(table_page_extension)) +
  visual_page_extension;

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
const body_class_dict = {};
body_class_list.forEach((item, index) => {
  body_class_dict[index + 1] = item;
});
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
const weight_class_dict = {};
weight_class_list.forEach((item, index) => {
  weight_class_dict[index + 1] = item;
});

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

function createDropdown(vehicle_id) {
  let select_items = vehicle_to_scan_dict[vehicle_id];
  let wrapper = document.createElement("div");
  if (select_items.length === 0) {
    wrapper.innerText = "No Associated Scans";
    return wrapper;
  }

  select_items = select_items.sort(compareByField("date_added")).toReversed();

  let dropdown = document.createElement("select");
  dropdown.classList.add("scan_selector");
  for (ind in select_items) {
    let choice = document.createElement("option");
    choice.value = select_items[ind]["fields"]["raw_scan"];
    choice.innerText = `${select_items[ind]["fields"]["date_added"]}`;
    dropdown.appendChild(choice);
  }

  let submit_button = document.createElement("button");
  submit_button.innerText = "View";
  submit_button.classList.add("containedbutton-inline");

  new ViewButtonController(dropdown, submit_button);

  wrapper.appendChild(dropdown);
  wrapper.appendChild(submit_button);
  return wrapper;
}

class Model {
  constructor() {
    this.table_fields = [
      "vehicle_updated",
      "vehicle_make",
      "vehicle_model",
      "vehicle_year",
      "vehicle_body_class",
      "vehicle_weight_class",
    ];
    this.vehicle_lists = [
      data,
      [...data].sort(compareByField("vehicle_updated")),
      [...data].sort(compareByField("vehicle_make")),
      [...data].sort(compareByField("vehicle_model")),
      [...data].sort(compareByField("vehicle_year")),
    ];
    this.current_list = this.vehicle_lists[1];

    // search controller
    this.search_field_index = 2;
    this.seach_value = "";

    // row controller
    this.cars_per_page = 25;
    this.num_pages = Math.ceil(this.current_list.length / this.cars_per_page);

    // sort controller
    this.vehicle_lists_index = 1;
    this.reverse = true;

    // page controller
    this.page = null;
    this.start_vehicle_num = null;
    this.end_vehicle_num = null;

    this.shown_vehicles = [];
    this.changedPageSubscribers = [];
  }

  getShownVehicles() {
    return this.shown_vehicles;
  }

  subChangedPage(f) {
    this.changedPageSubscribers.push(f);
  }

  updateNumPages() {
    this.num_pages = Math.ceil(this.current_list.length / this.cars_per_page);
    this.changePage(1);
  }

  updateCurrentList() {
    let list = [];
    let search_field = this.table_fields[this.search_field_index];
    for (let vehicle of this.vehicle_lists[this.vehicle_lists_index]) {
      if (
        isSubsequence(this.seach_value, vehicle.fields[search_field].toString())
      ) {
        list.push(vehicle);
      }
    }
    this.current_list = list;
    this.updateNumPages();
  }

  changePage(p) {
    this.page = p;

    this.shown_vehicles = [];

    let start_index = this.cars_per_page * (p - 1);
    let end_index =
      this.current_list.length >= this.cars_per_page * p
        ? this.cars_per_page * p
        : this.current_list.length;

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

    this.start_vehicle_num = start_index + 1;
    this.end_vehicle_num = end_index;

    this.changedPageSubscribers.forEach((f) => f(p));
  }
}

class SearchController {
  constructor(m) {
    this.model = m;
    this.seachColSelector = document.getElementById("search_col_select");
    this.searchBar = document.getElementById("search_bar");
    this.clearButton = document.getElementById("clear_search_bar");
    this.seachColSelector.value = "2";
    this.seachColSelector.addEventListener("change", () =>
      this.handleSeachFieldChange()
    );
    this.searchBar.addEventListener("input", (e) => this.handleSearchInput(e));
    this.clearButton.addEventListener("click", () => this.handleClearSearch());
  }

  handleSeachFieldChange() {
    this.model.search_field_index = +this.seachColSelector.value;
    this.searchBar.placeholder = `Search for ${
      this.seachColSelector.options[this.model.search_field_index].text
    }`;
    if (this.model.seach_value !== "") {
      this.model.updateCurrentList();
    }
  }

  handleSearchInput(e) {
    this.model.seach_value = e.target.value;
    this.model.updateCurrentList();
  }

  handleClearSearch() {
    this.searchBar.value = "";
    this.model.seach_value = "";
    this.model.updateCurrentList();
  }
}

class NumRowController {
  constructor(m) {
    this.model = m;
    this.numSelect = document.getElementById("num_row_select");
    this.numSelect.addEventListener("change", () => this.handleChangedRowNum());
    m.subChangedPage(() => this.handleChangedPage());
  }

  handleChangedRowNum() {
    let new_num_cars = this.numSelect.value;
    if (new_num_cars === "All") {
      this.model.cars_per_page = this.model.current_list.length;
    } else {
      this.model.cars_per_page = +this.numSelect.value;
    }
    this.model.updateNumPages();
  }

  handleChangedPage() {
    if (this.model.current_list.length === this.model.cars_per_page) {
      this.numSelect.value = "All";
    } else {
      this.numSelect.value = this.model.cars_per_page;
    }
  }
}

class SortController {
  constructor(m) {
    this.model = m;
    this.sortSelect = document.getElementById("sort_select");
    this.sortSelect.addEventListener("change", () => this.handleChangedSort());
    m.subChangedPage(() => this.handleChangedPage());
  }

  handleChangedSort() {
    this.model.vehicle_lists_index = Math.ceil(this.sortSelect.value / 2);
    if (this.sortSelect.value % 2 === 0 && this.sortSelect.value != 0) {
      this.model.reverse = true;
    } else {
      this.model.reverse = false;
    }
    this.model.updateCurrentList();
  }

  handleChangedPage() {
    this.sortSelect.value =
      this.model.vehicle_lists_index === 0
        ? this.model.vehicle_lists_index
        : 2 * this.model.vehicle_lists_index - !this.model.reverse;
  }
}

class TableView {
  constructor(m) {
    this.model = m;
    this.table = document.getElementById("vehicle_table");
    m.subChangedPage(() => this.handleChangedPage());
  }

  handleChangedPage() {
    while (this.table.children.length > 1) {
      this.table.removeChild(this.table.children[1]);
    }
    for (let vehicle of this.model.getShownVehicles()) {
      let row = document.createElement("tr");
      row.classList.add("elevation01");
      this.table.appendChild(row);
      for (let index in this.model.table_fields) {
        let col = document.createElement("td");
        if (this.model.table_fields[index] === "vehicle_body_class") {
          col.innerText =
            body_class_dict[vehicle.fields[this.model.table_fields[index]]];
        } else if (this.model.table_fields[index] === "vehicle_weight_class") {
          col.innerText =
            weight_class_dict[vehicle.fields[this.model.table_fields[index]]];
        } else {
          col.innerText = vehicle.fields[this.model.table_fields[index]];
        }
        if (+index === 0) {
          col.classList.add("left_cell");
        }
        row.appendChild(col);
      }
      let id = document.createElement("td");
      id.classList.add("right_cell");
      let dropdown = createDropdown(vehicle.pk);
      row.appendChild(id);
      id.appendChild(dropdown);
    }
  }
}

class ViewButtonController {
  constructor(d, b) {
    this.dropdown = d;
    this.button = b;
    this.scan_num = this.dropdown.value;

    this.dropdown.addEventListener("change", () => this.handleChangedView());
    this.button.addEventListener("click", () => this.handleViewButtonClick());
  }

  handleChangedView() {
    this.scan_num = this.dropdown.value;
  }

  handleViewButtonClick() {
    let link = document.createElement("a");
    link.href = vis_page_url + "/" + this.scan_num;
    link.click();
  }
}

class LabelView {
  constructor(m) {
    this.model = m;
    this.label = document.getElementById("entry_indicator");
    m.subChangedPage(() => this.handleChangedPage());
  }

  handleChangedPage() {
    this.label.innerText = `Showing ${this.model.start_vehicle_num}-${this.model.end_vehicle_num} of ${this.model.current_list.length} entries`;
  }
}

class PageSelectorViewController {
  constructor(m) {
    this.model = m;
    this.pageSelector = document.getElementById("pagination");
    m.subChangedPage(() => this.handleChangedPage());
  }

  handleChangedPage() {
    while (this.pageSelector.children.length > 0) {
      this.pageSelector.removeChild(this.pageSelector.children[0]);
    }

    let start_page = this.model.page - 2 > 0 ? this.model.page - 2 : 1;
    let end_page =
      start_page + 4 <= this.model.num_pages
        ? start_page + 4
        : this.model.num_pages;

    let first_page = document.createElement("a");
    first_page.innerText = "<< First";
    first_page.dataset.pagenum = 1;
    first_page.classList.add("pagination_elt", "page_turn");
    if (this.model.page !== 1) {
      first_page.addEventListener("click", (e) => this.handlePageChange(e));
      first_page.classList.add("clickable_page");
    } else {
      first_page.classList.add("unclickable_page");
    }
    this.pageSelector.appendChild(first_page);

    let prev_page = document.createElement("a");
    prev_page.innerText = "< Previous";
    prev_page.dataset.pagenum = this.model.page - 1;
    prev_page.classList.add("pagination_elt", "page_turn");
    if (this.model.page !== 1) {
      prev_page.addEventListener("click", (e) => this.handlePageChange(e));
      prev_page.classList.add("clickable_page");
    } else {
      prev_page.classList.add("unclickable_page");
    }
    this.pageSelector.appendChild(prev_page);

    for (let i = start_page; i <= end_page; i++) {
      let curr_page = document.createElement("a");
      curr_page.innerText = `${i}`;
      curr_page.dataset.pagenum = i;
      curr_page.classList.add("pagination_elt");
      if (i !== this.model.page) {
        curr_page.addEventListener("click", (e) => this.handlePageChange(e));
        curr_page.classList.add("clickable_page");
      } else {
        curr_page.classList.add("current_page");
      }
      this.pageSelector.appendChild(curr_page);
    }

    let next_page = document.createElement("a");
    next_page.innerText = "Next >";
    next_page.dataset.pagenum = this.model.page + 1;
    next_page.classList.add("pagination_elt", "page_turn");
    if (this.model.page !== this.model.num_pages) {
      next_page.addEventListener("click", (e) => this.handlePageChange(e));
      next_page.classList.add("clickable_page");
    } else {
      next_page.classList.add("unclickable_page");
    }
    this.pageSelector.appendChild(next_page);

    let last_page = document.createElement("a");
    last_page.innerText = "Last >>";
    last_page.dataset.pagenum = this.model.num_pages;
    last_page.classList.add("pagination_elt", "page_turn");
    if (this.model.page !== this.model.num_pages) {
      last_page.addEventListener("click", (e) => this.handlePageChange(e));
      last_page.classList.add("clickable_page");
    } else {
      last_page.classList.add("unclickable_page");
    }
    this.pageSelector.appendChild(last_page);
  }

  handlePageChange(e) {
    this.model.changePage(+e.target.dataset.pagenum);
  }
}

function init() {
  const model = new Model();
  const searchC = new SearchController(model);
  const numRowC = new NumRowController(model);
  const sortC = new SortController(model);
  const tableV = new TableView(model);
  const labelV = new LabelView(model);
  const pageSelectorVC = new PageSelectorViewController(model);
  model.changePage(1);
}

window.addEventListener("load", init);
