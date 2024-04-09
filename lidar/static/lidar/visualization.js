const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);
const graphStatus = JSON.parse(
  document.getElementById("graph_str").textContent
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
  if (graphStatus) {
    let exampleContainer = document.getElementById("graph_container");
    exampleContainer.style.display = "flex";
  } else {
    let graphContainer = document.getElementById("example_container");
    graphContainer.style.display = "flex";
  }
}
