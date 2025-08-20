/**
 * Theme Management System
 * Handles switching between light, dark, and system themes
 */

// Theme configuration
const THEMES = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
};

const THEME_LABELS = {
  [THEMES.LIGHT]: "☀️ Light",
  [THEMES.DARK]: "🌙 Dark",
  [THEMES.SYSTEM]: "🔧 System",
};

const THEME_ORDER = [THEMES.LIGHT, THEMES.DARK, THEMES.SYSTEM];

class ThemeManager {
  constructor() {
    this.currentTheme = this.getStoredTheme() || THEMES.SYSTEM;
    this.init();
  }

  init() {
    this.applyTheme(this.currentTheme);
    this.createThemeToggle();
  }

  getStoredTheme() {
    return localStorage.getItem("monopoly-deal-theme");
  }

  storeTheme(theme) {
    localStorage.setItem("monopoly-deal-theme", theme);
  }

  applyTheme(theme) {
    const html = document.documentElement;

    // Remove existing theme classes
    html.removeAttribute("data-theme");

    // Apply new theme
    if (theme === THEMES.SYSTEM) {
      html.setAttribute("data-theme", "system");
    } else {
      html.setAttribute("data-theme", theme);
    }

    this.currentTheme = theme;
    this.storeTheme(theme);
  }

  getNextTheme() {
    const currentIndex = THEME_ORDER.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % THEME_ORDER.length;
    return THEME_ORDER[nextIndex];
  }

  toggleTheme() {
    const nextTheme = this.getNextTheme();
    this.applyTheme(nextTheme);
    this.updateToggleDropdown();
  }

  createThemeToggle() {
    // Check if toggle already exists
    if (document.getElementById("theme-toggle")) {
      this.updateToggleDropdown();
      return;
    }

    const toggle = document.createElement("select");
    toggle.id = "theme-toggle";
    toggle.className = "theme-toggle";
    toggle.setAttribute("aria-label", "Select theme");
    toggle.setAttribute(
      "title",
      "Switch between light, dark, and system themes",
    );

    // Create options for the dropdown
    THEME_ORDER.forEach((theme) => {
      const option = document.createElement("option");
      option.value = theme;
      option.textContent = THEME_LABELS[theme];
      toggle.appendChild(option);
    });

    toggle.addEventListener("change", (e) => {
      this.applyTheme(e.target.value);
      this.updateToggleDropdown();
    });

    // Insert the toggle dropdown into the page
    document.body.appendChild(toggle);

    this.updateToggleDropdown();
  }

  updateToggleDropdown() {
    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.value = this.currentTheme;
    }
  }
}

// Initialize theme manager when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  window.themeManager = new ThemeManager();
});

// Export for use in other scripts if needed
if (typeof module !== "undefined" && module.exports) {
  module.exports = { ThemeManager, THEMES };
}
