const vruLabels = [
  "pre-school child",
  "elementary school child on bike",
  "elementary school child",
  "wheelchair user",
  "adult on bike",
  "adult",
];
const colors = ["#A6DDE7a6", "#A34D9Da6"];
const borders = ["1px solid #A6DDE7", "1px solid #A34D9D"];

const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);
const vrusSelected = JSON.parse(
  document.getElementById("vrus_selected").textContent
);

if (loadingStatus === true) {
  let loader = document.getElementById("load_wrapper");
  loader.style.display = "block";

  window.setTimeout(function () {
    window.location.reload();
  }, 30000);
} else {
  let content = document.getElementsByClassName("visualization-content")[0];
  content.style.display = "flex";

  let checks = document.getElementsByName("vru_selected");
  const max = 2;
  for (let check of checks) {
    check.onclick = selectiveCheck;
  }
  function selectiveCheck() {
    let checkedChecks = document.querySelectorAll(
      "input[name='vru_selected']:checked"
    );
    if (checkedChecks.length >= max + 1) {
      return false;
    }
  }
  if (vrusSelected) {
    let graphContainer = document.getElementById("graph_container");
    graphContainer.style.display = "flex";

    let graphContainerHeading = document.getElementById("vissVRUshown");
    graphContainerHeading.innerText =
      vrusSelected.length > 1
        ? `${vruLabels[vrusSelected[0] - 1]} and ${
            vruLabels[vrusSelected[1] - 1]
          }`
        : `${vruLabels[vrusSelected[0] - 1]}`;

    let vru1Text = document.getElementById("vru1_entry_text");
    vru1Text.innerText = `${vruLabels[vrusSelected[0] - 1]} blindzone`;

    let vru1Color = document.getElementById("vru1_entry_color");
    vru1Color.style.backgroundColor = colors[0];
    vru1Color.style.border = borders[0];

    if (vrusSelected.length > 1) {
      let vru2 = document.getElementById("vru2_entry");
      vru2.style.display = "flex";
      let vru2Text = document.getElementById("vru2_entry_text");
      vru2Text.innerText = `${vruLabels[vrusSelected[1] - 1]} blindzone`;
      let vru2Color = document.getElementById("vru2_entry_color");
      vru2Color.style.backgroundColor = colors[0];
      vru2Color.style.border = borders[0];
      vru1Color.style.backgroundColor = colors[1];
      vru1Color.style.border = borders[1];
    }
  }
}
