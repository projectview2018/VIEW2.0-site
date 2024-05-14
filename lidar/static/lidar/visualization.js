// labels for vrus, in order of ascending height
const vruLabels = [
  "pre-school child",
  "elementary school child on bike",
  "elementary school child",
  "wheelchair user",
  "adult on bike",
  "adult",
];
// plural labels for vrus, in same order
const vruLabelsPlural = [
  "pre-school children",
  "elementary school children on bikes",
  "elementary school children",
  "wheelchair users",
  "adults on bikes",
  "adults",
];
// colors for legend
const colors = ["#A6DDE7a6", "#A34D9Da6"];
// border styles for legend
const borders = ["1px solid #A6DDE7", "1px solid #A34D9D"];

const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);
const vrusSelected = JSON.parse(
  document.getElementById("vrus_selected").textContent
);
const num_vrus_in_vru_area = JSON.parse(
  document.getElementById("num_vrus_in_vru_nvp_area").textContent
);
const closest_forward_nvps = JSON.parse(
  document.getElementById("closest_forward_nvps").textContent
);

// check if page should be loading
// if so, show the loader and refresh the page every 30 seconds
// if not, continue to display content
if (loadingStatus === true) {
  // show the div that contains the loader
  let loader = document.getElementById("load_wrapper");
  loader.style.display = "block";

  // reload the window after 30sec
  window.setTimeout(function () {
    window.location.reload();
  }, 30000);
} else {
  // show the div that contains the content
  let content = document.getElementsByClassName("visualization-content")[0];
  content.style.display = "flex";

  // get a list of the checked vrus and attach the following onclick function
  // to them
  let checks = document.getElementsByName("vru_selected");
  const max = 2;
  for (let check of checks) {
    check.onclick = selectiveCheck;
  }
  /**
   * Onclick function for VRU checkboxes. Uncheck box if two already selected.
   *
   * @returns {boolean} false if number of checked boxes is greater than two
   */
  function selectiveCheck() {
    let checkedChecks = document.querySelectorAll(
      "input[name='vru_selected']:checked"
    );
    if (checkedChecks.length >= max + 1) {
      return false;
    }
  }
  if (vrusSelected) {
    // show the graph container if there are VRUs selected
    let graphContainer = document.getElementById("graph_container");
    graphContainer.style.display = "flex";

    // set the text for the header of the graph section to match the vru(s)
    // use the number of the vru as a lookup into vruLabels
    let graphContainerHeading = document.getElementById("vissVRUshown");
    graphContainerHeading.innerText =
      vrusSelected.length > 1
        ? `${vruLabels[vrusSelected[0] - 1]} and ${
            vruLabels[vrusSelected[1] - 1]
          }`
        : `${vruLabels[vrusSelected[0] - 1]}`;

    // set the text for each of the vru1 labels
    let vru1_fields = document.getElementsByClassName("vru1_label");
    for (let field of vru1_fields) {
      field.innerText = `${vruLabels[vrusSelected[0] - 1]}`;
    }

    // set the value for the min forward distance that vru1 is visible from
    let vru1_front = document.getElementById("vru1_front_dist");
    vru1_front.innerText = `${closest_forward_nvps[0]} ft`;

    // set the total number of vru1s hidden in blindzone
    let vru1_total_num = document.getElementById("vru1_total_num");
    vru1_total_num.innerText = `${num_vrus_in_vru_area[0]}`;

    // set the text for the plural vru1 labels
    let vru1_label_plural = document.getElementById("vru1_label_plural");
    vru1_label_plural.innerText = `${vruLabelsPlural[vrusSelected[0] - 1]}`;

    // make the text for vru1 visible
    let vru1String = document.getElementById("graph_str1");
    vru1String.style.display = "inline";

    // set the text in the legend for vru1
    let vru1Text = document.getElementById("vru1_entry_text");
    vru1Text.innerText = `${vruLabels[vrusSelected[0] - 1]} blindzone`;

    // set the color of the legend to match the graph color
    let vru1Color = document.getElementById("vru1_entry_color");
    vru1Color.style.backgroundColor = colors[0];
    vru1Color.style.border = borders[0];

    // repeat process if there is second vru
    if (vrusSelected.length > 1) {
      // show the second vru entry in legend
      let vru2 = document.getElementById("vru2_entry");
      vru2.style.display = "flex";

      // add the correct vru text for each of the vru2 labels
      let vru2_fields = document.getElementsByClassName("vru2_label");
      for (let field of vru2_fields) {
        field.innerText = `${vruLabels[vrusSelected[1] - 1]}`;
      }

      // fill in the value for the front dist for vru2
      let vru2_front = document.getElementById("vru2_front_dist");
      vru2_front.innerText = `${closest_forward_nvps[1]} ft`;

      // fill in the value for the total number of vru2s in the blindzone
      let vru2_total_num = document.getElementById("vru2_total_num");
      vru2_total_num.innerText = `${num_vrus_in_vru_area[1]}`;

      // fill in the plural vru2 text in the correct spots
      let vru2_label_plural = document.getElementById("vru2_label_plural");
      vru2_label_plural.innerText = `${vruLabelsPlural[vrusSelected[1] - 1]}`;

      // show the text for vru2
      let vru2String = document.getElementById("graph_str2");
      vru2String.style.display = "inline";

      // fill the vru2 label in the legend
      let vru2Text = document.getElementById("vru2_entry_text");
      vru2Text.innerText = `${vruLabels[vrusSelected[1] - 1]} blindzone`;

      // set the color for vru2 and adjust the color for vru1
      let vru2Color = document.getElementById("vru2_entry_color");
      vru2Color.style.backgroundColor = colors[0];
      vru2Color.style.border = borders[0];
      vru1Color.style.backgroundColor = colors[1];
      vru1Color.style.border = borders[1];
    }
  }
}
