const data = JSON.parse(document.getElementById('vehicle_list').textContent);

class Model {
    constructor() {
        this.vehicle_list = data;
        
        this.cars_per_page = 10;
        
        this.page = null;
        this.start_vehicle_num = null;
        this.end_vehicle_num = null;
        this.total_vehicle_num = this.vehicle_list.length;
        this.num_pages = Math.ceil(this.total_vehicle_num / this.cars_per_page)
        this.current_vehicles = [];
        this.changedPageSubscribers = [];
    }

    getVehicles() {
        return this.current_vehicles;
    }

    subChangedPage(f) {
        this.changedPageSubscribers.push(f);
    }

    changePage(p) {
        this.page = p;

        this.current_vehicles = []
        let start_index = this.cars_per_page * (p - 1);
        let end_index = this.vehicle_list.length >= this.cars_per_page * p ? this.cars_per_page * p : this.vehicle_list.length;
        for (let i = start_index; i < end_index; i++) {
            this.current_vehicles.push(this.vehicle_list[i]);
        }
        this.start_vehicle_num = start_index + 1;
        this.end_vehicle_num = end_index;

        this.changedPageSubscribers.forEach((f) => f(p))
    }
}

class LabelView {
    constructor(m) {
        this.model = m;
        this.label = document.getElementById('entry_indicator');
        m.subChangedPage(() => this.handleChangedPage());
    }

    handleChangedPage() {
        this.label.innerText = `Showing ${this.model.start_vehicle_num}-${this.model.end_vehicle_num} of ${this.model.total_vehicle_num} entries`;
    }
}

class PageSelectorView {
    constructor(m) {
        this.model = m;
        this.pageSelector = document.getElementById('pagination');
        m.subChangedPage(() => this.handleChangedPage());
    }

    handleChangedPage() {
        while (this.pageSelector.children.length > 0) {
            this.pageSelector.removeChild(this.pageSelector.children[0]);
        }

        let start_page = this.model.page - 2 > 0 ? this.model.page - 2 : 1
        let end_page = this.model.page + 2 <= this.model.num_pages ? this.model.page + 2 : this.model.num_pages

        let first_page = document.createElement('a');
        first_page.innerText = "<< First";
        first_page.dataset.pagenum = 1;
        first_page.classList.add('pagination_elt');
        if (this.model.page !== 1) {
            first_page.addEventListener('click', (e) => this.handlePageChange(e));
            first_page.classList.add('clickable_page');
        } else {
            first_page.classList.add('unclickable_page');
        }
        this.pageSelector.appendChild(first_page);

        let prev_page = document.createElement('a');
        prev_page.innerText = "< Previous";
        prev_page.dataset.pagenum = this.model.page - 1;
        prev_page.classList.add('pagination_elt');
        if (this.model.page !== 1) {
            prev_page.addEventListener('click', (e) => this.handlePageChange(e));
            prev_page.classList.add('clickable_page');
        } else {
            prev_page.classList.add('unclickable_page');
        }
        this.pageSelector.appendChild(prev_page);

        for (let i = start_page; i <= end_page; i++) {
            let curr_page = document.createElement('a');
            curr_page.innerText = `${i}`;
            curr_page.dataset.pagenum = i;
            curr_page.classList.add('pagination_elt');
            if (i !== this.model.page) {
                curr_page.addEventListener('click', (e) => this.handlePageChange(e));
                curr_page.classList.add('clickable_page');
            } else {
                curr_page.classList.add('current_page');
            }
            this.pageSelector.appendChild(curr_page);
        }

        let next_page = document.createElement('a');
        next_page.innerText = "Next >";
        next_page.dataset.pagenum = this.model.page + 1;
        next_page.classList.add('pagination_elt');
        if (this.model.page !== this.model.num_pages) {
            next_page.addEventListener('click', (e) => this.handlePageChange(e));
            next_page.classList.add('clickable_page');
        } else {
            next_page.classList.add('unclickable_page');
        }
        this.pageSelector.appendChild(next_page);

        let last_page = document.createElement('a');
        last_page.innerText = "Last >>";
        last_page.dataset.pagenum = this.model.num_pages;
        last_page.classList.add('pagination_elt');
        if (this.model.page !== this.model.num_pages) {
            last_page.addEventListener('click', (e) => this.handlePageChange(e));
            last_page.classList.add('clickable_page');
        } else {
            last_page.classList.add('unclickable_page');
        }
        this.pageSelector.appendChild(last_page);
    }

    handlePageChange(e) {
        this.model.changePage(+e.target.dataset.pagenum);
    }
}

class TableView {
    constructor(m) {
        this.model = m;
        this.table = document.getElementById('vehicle_table');
        m.subChangedPage(() => this.handleChangedPage());
    }

    handleChangedPage() {
        while (this.table.children.length > 1) {
            this.table.removeChild(this.table.children[1]);
        }
        for (let vehicle of this.model.getVehicles()) {
            let row = document.createElement('tr');
            this.table.appendChild(row);
            const keys = ['vehicle_updated', 'vehicle_make', 'vehicle_model', 'vehicle_year'];
            for (let key of keys) {
                let col = document.createElement('td');
                col.innerText = vehicle.fields[key];
                row.appendChild(col);
            }
        }
    }
}

function init() {
    const model = new Model();
    const tableV = new TableView(model);
    const labelV = new LabelView(model);
    const pageSelectorV = new PageSelectorView(model);
    model.changePage(1);
}

window.addEventListener('load', init);
