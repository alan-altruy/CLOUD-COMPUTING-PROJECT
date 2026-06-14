const applyTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
};

const params = new URLSearchParams(window.location.search);
let theme = params.get("theme");

// 1. mode forcé Android
if (theme === "dark" || theme === "light") {
    applyTheme(theme);
}

// 2. mode auto
else {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");

    const update = () => {
        applyTheme(mq.matches ? "dark" : "light");
    };

    update(); // initial load

    // 👇 écoute les changements système
    mq.addEventListener("change", update);
}