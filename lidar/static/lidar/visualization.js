const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);

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

if (loadingStatus === true) {
  contentWrapper.insertBefore(loadWrapper, content);
  content.style.display = "none";
  window.setTimeout(function () {
    window.location.reload();
  }, 30000);
}
