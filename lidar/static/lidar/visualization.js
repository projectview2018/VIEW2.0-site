const loadingStatus = JSON.parse(
  document.getElementById("loading").textContent
);

let contentWrapper = document.getElementsByClassName(
  "visualization-container"
)[0];
let content = document.getElementsByClassName("visualization-content")[0];
let loader = document.createElement("div");
loader.classList.add("loader");

if (loadingStatus === true) {
  contentWrapper.insertBefore(loader, content);
  content.style.display = "none";
  window.setTimeout(function () {
    window.location.reload();
  }, 30000);
}
