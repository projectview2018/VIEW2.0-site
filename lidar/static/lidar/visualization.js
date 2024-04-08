const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);
const graphStatus = JSON.parse(
  document.getElementById("graph_str").textContent
);

if (loadingStatus === true) {
  let contentWrapper = document.getElementsByClassName(
    "visualization-container"
  )[0];
  let content = document.getElementsByClassName("visualization-content")[0];

  let loadWrapper = document.createElement("div");
  loadWrapper.id = "load_wrapper";

  let loadHeader = document.createElement("h1");
  loadHeader.id = "load_header";
  loadHeader.classList.add("HeadingH3");
  loadHeader.innerText = "Processing your scan...";

  let loader = document.createElement("div");
  loader.classList.add("loader");

  let loadText = document.createElement("p");
  loadText.id = "load_text";
  loadText.classList.add("Body");
  loadText.innerText =
    "This can take up to five minutes, and the page may reload several times.";

  loadWrapper.appendChild(loadHeader);
  loadWrapper.appendChild(loader);
  loadWrapper.appendChild(loadText);

  contentWrapper.insertBefore(loadWrapper, content);
  content.style.display = "none";
  window.setTimeout(function () {
    window.location.reload();
  }, 30000);
} else {
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
    let exampleContainer = document.getElementById("example_container");
    exampleContainer.style.display = "none";
  } else {
    let graphContainer = document.getElementById("graph_container");
    graphContainer.style.display = "none";
  }
}
