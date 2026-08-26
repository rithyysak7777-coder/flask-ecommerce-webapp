(function () {
  const storageKey = "ractz-theme";
  const root = document.documentElement;

  function applyTheme(theme) {
    root.dataset.theme = theme;
    localStorage.setItem(storageKey, theme);
  }

  const savedTheme = localStorage.getItem(storageKey);
  const preferredTheme = window.matchMedia("(prefers-color-scheme: dark)")
    .matches
    ? "dark"
    : "light";

  applyTheme(savedTheme || preferredTheme);

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.querySelector("[data-theme-toggle]");

    if (!toggle) {
      return;
    }

    toggle.addEventListener("click", function () {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
  });
})();

function toggleAdminPassword() {
  const input = document.getElementById("admin-password") || document.getElementById("password");
  const icon = document.getElementById("passwordToggleIcon");
  if (input && icon) {
    if (input.type === "password") {
      input.type = "text";
      icon.classList.remove("bi-eye");
      icon.classList.add("bi-eye-slash");
    } else {
      input.type = "password";
      icon.classList.remove("bi-eye-slash");
      icon.classList.add("bi-eye");
    }
  }
}

