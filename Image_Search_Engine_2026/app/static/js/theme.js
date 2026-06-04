const theme = new URLSearchParams(window.location.search).get("theme");
document.documentElement.setAttribute("data-theme", theme);