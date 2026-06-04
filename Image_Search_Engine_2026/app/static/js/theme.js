const params = new URLSearchParams(window.location.search);
let theme = params.get("theme");

// 1. si Android impose un thème
if (theme === "dark" || theme === "light") {
    document.documentElement.setAttribute("data-theme", theme);
}

// 2. sinon AUTO
else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    document.documentElement.setAttribute(
        "data-theme",
        prefersDark ? "dark" : "light"
    );
}