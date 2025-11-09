document.addEventListener("DOMContentLoaded", () => {
  const highlightScript = document.currentScript || document.querySelector("script[data-highlightjs-import-theme-script]");
  const themeDark = highlightScript.getAttribute("data-theme-dark");
  const themeLight = highlightScript.getAttribute("data-theme-light");

  const highlightBaseUrl = `https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@latest/build/styles`;

  const loadHighlightStylesheet = () => {
    const scheme = document.documentElement.getAttribute("data-fr-scheme");

    document.querySelector("link[data-highlight-theme]")?.remove();

    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.setAttribute("data-highlight-theme", true);

    if (scheme === "dark") {
      stylesheet.href = `${highlightBaseUrl}/${themeDark}.css`;
    } else {
      stylesheet.href = `${highlightBaseUrl}/${themeLight}.css`;
    }

    document.head.appendChild(stylesheet);
  };

  loadHighlightStylesheet();
  new MutationObserver((mutations) => {
    if (mutations.some(m => m.attributeName === "data-fr-scheme")) {
      loadHighlightStylesheet();
    }
  }).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-fr-scheme"]
  });
});
