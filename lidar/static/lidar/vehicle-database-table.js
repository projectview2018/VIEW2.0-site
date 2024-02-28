const data = JSON.parse(document.getElementById('vehicle_list').textContent);

class Model {
    constructor() {
        this.vehicle_list = data;
        
        this.cars_per_page = 10;
        
        this.page = null;
        this.start_vehicle_num = null;
        this.end_vehicle_num = null;
        this.total_vehicle_num = this.vehicle_list.length;
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
        let start_index = 10 * (p - 1);
        let end_index = this.vehicle_list.length >= 10 * p ? 10 * p : this.vehicle_list.length;
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

class TableView {
    constructor(m) {
        this.model = m;
        this.table = document.getElementById('vehicle_table');
        m.subChangedPage(() => this.handleChangedPage());
    }

    handleChangedPage() {
        let children = this.table.children;
        for (let i = 1; i < children.length; i++) {
            this.table.removeChild(children[i]);
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
    model.changePage(1);
}

window.addEventListener('load', init);
