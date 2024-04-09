const vru_labels = [
  "pre-school child",
  "elementary school child on bike",
  "elementary school child",
  "wheelchair user",
  "adult on bike",
  "adult",
];

const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);
const graphStr1 = JSON.parse(document.getElementById("graph_str1").textContent);
const graphStr2 = JSON.parse(document.getElementById("graph_str2").textContent);
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
  if (graphStr1) {
    let graphContainer = document.getElementById("graph_container");
    graphContainer.style.display = "flex";

    let graphContainerHeading = document.getElementById("vissVRUshown");
    graphContainerHeading.innerText =
      vrusSelected.length > 1
        ? `${vru_labels[vrusSelected[0] - 1]} and ${
            vru_labels[vrusSelected[1] - 1]
          }`
        : `${vru_labels[vrusSelected[0] - 1]}`;

    let vru1Text = document.getElementById("vru1_entry_text");
    vru1Text.innerText = `${vru_labels[vrusSelected[0] - 1]} blindzone`;

    if (graphStr2) {
      let vru2 = document.getElementById("vru2_entry");
      vru2.style.display = "flex";
      let vru2Text = document.getElementById("vru2_entry_text");
      vru2Text.innerText = `${vru_labels[vrusSelected[1] - 1]} blindzone`;
    }
  }
}
