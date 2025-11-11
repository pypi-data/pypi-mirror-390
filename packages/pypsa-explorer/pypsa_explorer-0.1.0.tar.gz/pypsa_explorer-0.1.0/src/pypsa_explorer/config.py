"""Configuration settings for PyPSA Explorer dashboard."""

import plotly.graph_objects as go
import plotly.io as pio

# Color scheme and theme settings - Energetic Coral palette
COLORS = {
    "primary": "#0066CC",  # Vibrant blue
    "secondary": "#FF6B6B",  # Coral red
    "accent": "#4ECDC4",  # Turquoise
    "warning": "#FFB84D",  # Warm amber
    "light_bg": "#FAFBFC",  # Crisp white-grey
    "dark_bg": "#1A1F36",  # Deep navy with warmth
    "text": "#2D3748",  # Warm dark grey
    "light_text": "#718096",  # Medium grey
    "background": "#F5F7FA",  # Soft neutral grey
    "gradient_start": "#667EEA",  # Soft blue-purple
    "gradient_end": "#FF6B6B",  # Coral - sunset effect
    "glass_bg": "rgba(255, 255, 255, 0.85)",  # Glass morphism
    "glass_border": "rgba(255, 107, 107, 0.15)",  # Warm coral tint
}

# Dark mode colors
COLORS_DARK = {
    "primary": "#4ECDC4",  # Turquoise (accent becomes primary)
    "secondary": "#FF6B6B",  # Coral red
    "accent": "#667EEA",  # Soft blue-purple
    "warning": "#FFB84D",  # Warm amber
    "light_bg": "#1A1F36",  # Deep navy
    "dark_bg": "#0F1419",  # Darker navy
    "text": "#E2E8F0",  # Light grey for text
    "light_text": "#94A3B8",  # Medium-light grey
    "background": "#131C2C",  # Solid dark background
    "gradient_start": "#667EEA",  # Soft blue-purple
    "gradient_end": "#FF6B6B",  # Coral - sunset effect
    "glass_bg": "rgba(26, 31, 54, 0.85)",  # Dark glass
    "glass_border": "rgba(78, 205, 196, 0.15)",  # Turquoise tint
}

# Plotly template configuration
PLOTLY_TEMPLATE_NAME = "dashboard_theme"
PLOTLY_TEMPLATE_NAME_DARK = "dashboard_theme_dark"


def setup_plotly_theme() -> None:
    """Configure Plotly theme for consistent styling across the dashboard."""
    pio.templates.default = "plotly_white"

    # Light mode template
    custom_template = go.layout.Template()
    custom_template.layout = go.Layout(
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        font={"family": "Roboto, 'Helvetica Neue', sans-serif", "color": COLORS["text"]},
        xaxis={"gridcolor": "#e9ecef", "zerolinecolor": "#e9ecef"},
        yaxis={"gridcolor": "#e9ecef", "zerolinecolor": "#e9ecef"},
    )
    pio.templates[PLOTLY_TEMPLATE_NAME] = custom_template

    # Dark mode template
    dark_template = go.layout.Template()
    dark_template.layout = go.Layout(
        plot_bgcolor=COLORS_DARK["background"],
        paper_bgcolor=COLORS_DARK["background"],
        font={"family": "Roboto, 'Helvetica Neue', sans-serif", "color": COLORS_DARK["text"]},
        xaxis={
            "gridcolor": "rgba(255, 255, 255, 0.1)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)",
            "color": COLORS_DARK["text"],
        },
        yaxis={
            "gridcolor": "rgba(255, 255, 255, 0.1)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)",
            "color": COLORS_DARK["text"],
        },
        legend={"font": {"color": COLORS_DARK["text"]}},
    )
    pio.templates[PLOTLY_TEMPLATE_NAME_DARK] = dark_template

    pio.templates.default = PLOTLY_TEMPLATE_NAME


# Dashboard layout configuration
LAYOUT_CONFIG = {
    "sidebar_width": 3,
    "main_content_width": 9,
    "chart_height": 500,
    "map_height": 700,
}

# Default carriers for initial selection
DEFAULT_CARRIERS = ["AC", "Hydrogen Storage", "Low Voltage"]

# Custom CSS for the dashboard
DASHBOARD_CSS = """
/* Modern Energy Dashboard - Enhanced Styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-color: #0066CC;
    --secondary-color: #FF6B6B;
    --accent-color: #4ECDC4;
    --warning-color: #FFB84D;
    --light-bg: #FAFBFC;
    --dark-bg: #1A1F36;
    --text-color: #2D3748;
    --light-text: #718096;
    --gradient-start: #667EEA;
    --gradient-end: #FF6B6B;
    --glass-bg: rgba(255, 255, 255, 0.85);
    --glass-border: rgba(255, 107, 107, 0.15);
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.15);
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--text-color);
    background: #F5F7FA;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

#app-container {
    position: relative;
    min-height: 100vh;
    z-index: 0;
    padding: 24px 0 40px;
}

#app-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.04) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255, 107, 107, 0.04) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(78, 205, 196, 0.03) 0%, transparent 50%),
        linear-gradient(135deg, #F5F7FA 0%, #E8EDF2 100%);
    background-blend-mode: screen, screen, screen, normal;
    pointer-events: none;
    z-index: -1;
}

#app-container > * {
    position: relative;
    z-index: 1;
}

#main-content {
    padding-top: 32px;
}

/* Utility bar */
.utility-bar {
    position: sticky;
    top: 0;
    z-index: 1100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;
    padding: 10px 24px;
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 18px;
    box-shadow: 0 12px 28px rgba(30, 64, 175, 0.22);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.utility-bar__brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.utility-brand__title {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    color: inherit;
}

.utility-brand__subtitle {
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.75);
}

.utility-bar__actions {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.utility-bar__meta,
.utility-bar__controls {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.top-bar__selector {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 300px;
    flex: 1 1 300px;
}
.network-selector {
    width: 100%;
    min-width: 260px;
    max-width: 360px;
}

.utility-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.78);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.utility-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.28);
}

.utility-meta {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.72) !important;
}

.dark-mode-toggle {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.28);
    box-shadow: var(--shadow-sm);
    transition: background var(--transition-base), border-color var(--transition-base), color var(--transition-base);
    color: #FFFFFF;
}

#dark-mode-toggle-container .form-check {
    margin: 0;
}

#dark-mode-toggle-container .form-switch .form-check-input {
    cursor: pointer;
}

@media (max-width: 768px) {
    .utility-bar {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
        padding: 12px 16px;
    }

    .utility-bar__actions {
        flex-direction: column;
        align-items: stretch;
        gap: 14px;
    }

    .top-bar__selector {
        min-width: 0;
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
    }

    .network-selector {
        min-width: 0;
        max-width: 100%;
    }

    .utility-bar__controls {
        justify-content: space-between;
    }

    .dark-mode-toggle {
        width: 100%;
        justify-content: space-between;
    }
}

/* ===== TYPOGRAPHY ===== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-color);
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.3;
}

h1 { font-size: 2.5rem; font-weight: 800; }
h2 { font-size: 2rem; font-weight: 700; }
h3 { font-size: 1.5rem; font-weight: 600; }
h4 { font-size: 1.25rem; font-weight: 600; }
h5 { font-size: 1.1rem; font-weight: 600; }

/* ===== CARDS & CONTAINERS ===== */
.card {
    border-radius: 16px;
    box-shadow: var(--shadow-md);
    margin-bottom: 24px;
    border: none;
    background: white;
    transition: all var(--transition-base);
    overflow: hidden;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.card-body {
    padding: 24px;
}

/* Empty state panels */
.empty-state {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 16px;
    border: 2px dashed rgba(78, 205, 196, 0.35);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: border-color var(--transition-base), background var(--transition-base);
}

.empty-state--warning {
    border-color: rgba(255, 184, 77, 0.45);
}

.empty-state:hover {
    border-color: rgba(78, 205, 196, 0.55);
}

.empty-state--warning:hover {
    border-color: rgba(255, 184, 77, 0.65);
}

.tab-content {
    background-color: transparent !important;
    border: none !important;
}

/* ===== TABS ===== */
/* Tabs parent container - the outer wrapper */
#tabs {
    border-radius: 16px !important;
    overflow: hidden !important;
    background: white !important;
    box-shadow: var(--shadow-md);
}

/* Ensure the parent div wrapper also has rounded corners */
#tabs > div {
    border-radius: 16px !important;
    overflow: hidden !important;
}

.tab-container {
    border-bottom: 2px solid rgba(0, 0, 0, 0.06);
    background: white;
    border-radius: 12px 12px 0 0;
    padding: 0 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.tab {
    border: none;
    color: var(--light-text);
    font-weight: 500;
    font-size: 0.95rem;
    padding: 16px 24px;
    margin-right: 4px;
    transition: all var(--transition-base);
    background-color: transparent !important;
    border-bottom: 3px solid transparent;
    position: relative;
    border-radius: 8px 8px 0 0;
}

.tab::before {
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
    transform: scaleX(0);
    transition: transform var(--transition-base);
}

.tab:hover {
    color: var(--primary-color);
    background-color: rgba(0, 102, 204, 0.08) !important;
}

.tab:hover::before {
    transform: scaleX(0.5);
}

.tab--selected {
    color: var(--primary-color) !important;
    background-color: rgba(0, 102, 204, 0.12) !important;
    font-weight: 600;
}

.tab--selected::before {
    transform: scaleX(1) !important;
}

.tab--selected, .tab {
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-bottom: 3px solid transparent !important;
}

/* ===== BUTTONS ===== */
.btn {
    border-radius: 10px;
    font-weight: 500;
    padding: 12px 24px;
    transition: all var(--transition-base);
    border: none;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    box-shadow: var(--shadow-sm);
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, #0052A3 100%);
    border: none;
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #0052A3 0%, #003D7A 100%);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.btn-lg {
    padding: 16px 32px;
    font-size: 1.05rem;
    border-radius: 12px;
}

.dashboard-container {
    padding: 24px;
    max-width: 1920px;
    margin: 0 auto;
}

/* ===== WELCOME PAGE ===== */
.welcome-card {
    text-align: center;
    padding: 48px 36px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
    border: 1px solid rgba(255, 255, 255, 0.5);
    position: relative;
    overflow: hidden;
}

.welcome-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
}

.welcome-header {
    font-size: 3.5rem;
    margin-bottom: 0.5em;
    font-weight: 800;
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}

.welcome-subtitle {
    font-size: 1.5rem;
    margin-bottom: 1.5em;
    color: var(--light-text);
    font-weight: 400;
}

.welcome-feature {
    background: white;
    border-radius: 16px;
    padding: 32px 24px;
    height: 100%;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
    border: 1px solid rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}

.welcome-feature::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, var(--accent-color) 0%, var(--secondary-color) 100%);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform var(--transition-base);
}

.welcome-feature:hover::before {
    transform: scaleX(1);
}

.welcome-feature:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-lg);
}

.feature-icon {
    font-size: 48px;
    margin-bottom: 20px;
    color: var(--accent-color);
    display: inline-block;
    transition: all var(--transition-base);
}

.welcome-feature:hover .feature-icon {
    transform: scale(1.1) rotate(5deg);
}

.network-item {
    padding: 20px;
    margin: 12px 0;
    background: white;
    border-radius: 12px;
    border-left: 4px solid var(--primary-color);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-base);
}

.network-item:hover {
    transform: translateX(8px);
    box-shadow: var(--shadow-md);
    border-left-color: var(--secondary-color);
}

/* Enter Dashboard Button */
#enter-dashboard-btn {
    position: relative;
    overflow: hidden;
}

#enter-dashboard-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s ease;
}

#enter-dashboard-btn:hover::before {
    left: 100%;
}

#enter-dashboard-btn:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 32px rgba(0, 102, 204, 0.4) !important;
}

#enter-dashboard-btn:active {
    transform: translateY(-2px) scale(1);
}

/* ===== SIDEBAR - GLASS MORPHISM ===== */
.sidebar-filter-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    min-height: calc(100vh - 200px);
    padding: 28px;
    margin-right: 20px;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}

.sidebar-filter-panel:hover {
    box-shadow: var(--shadow-lg);
}

.sidebar-filter-panel h5 {
    color: var(--text-color);
    margin-bottom: 20px;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.sidebar-filter-panel hr {
    margin: 16px 0;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.1), transparent);
}

.sidebar-filter-panel label {
    font-weight: 500;
    color: var(--text-color);
    margin-bottom: 8px;
}

/* Radio buttons styling */
.sidebar-filter-panel input[type="radio"] {
    margin-right: 8px;
    accent-color: var(--accent-color);
    cursor: pointer;
}

/* Checkbox styling */
.sidebar-filter-panel input[type="checkbox"] {
    margin-right: 8px;
    accent-color: var(--accent-color);
    cursor: pointer;
    width: 18px;
    height: 18px;
}

/* Improve label spacing */
.sidebar-filter-panel .form-check-label {
    cursor: pointer;
    padding: 4px 0;
    transition: color var(--transition-fast);
}

.sidebar-filter-panel .form-check-label:hover {
    color: var(--primary-color);
}

/* "Not applicable" text styling */
.sidebar-filter-panel small {
    display: block;
    padding: 12px;
    background: rgba(255, 184, 77, 0.08);
    border-left: 3px solid var(--warning-color);
    border-radius: 8px;
    color: var(--warning-color);
    font-weight: 500;
    margin-top: 12px;
}

.sidebar-container {
    position: sticky;
    top: 20px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
    overflow-x: hidden;
}

.sidebar-container::-webkit-scrollbar {
    width: 6px;
}

.sidebar-container::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 10px;
}

.sidebar-container::-webkit-scrollbar-thumb {
    background: var(--accent-color);
    border-radius: 10px;
}

.main-content-area {
    padding-left: 0;
}

/* ===== FORMS & INPUTS ===== */
/* Network Button Group Styling */

.network-button-group {
    display: flex;
    gap: 8px;
    align-items: center;
}

.network-button {
    padding: 8px 16px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.15);
    color: rgba(255, 255, 255, 0.85);
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.network-button:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.5);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.network-button-active {
    background: rgba(255, 255, 255, 0.95) !important;
    color: var(--primary-color) !important;
    border-color: white !important;
    font-weight: 600;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}

.network-button-active:hover {
    transform: none;
}

/* Ensure parent containers don't clip */
#top-bar-network-selector,
.top-bar__selector {
    overflow: visible !important;
}

/* Generic Select styling for other dropdowns */
.Select div[class*="control"] {
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.Select div[class*="menu"] {
    background: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 9999;
}

.Select div[class*="option"] {
    cursor: pointer;
    padding: 8px 12px;
}

/* Multi-select value tags */
.Select div[class*="multiValue"] {
    background: linear-gradient(135deg, var(--accent-color), #3DB9B0) !important;
    border: none !important;
    border-radius: 6px !important;
}

.Select div[class*="multiValue"] div[class*="label"] {
    color: white !important;
    padding: 4px 8px !important;
}

.Select div[class*="multiValue"] div[class*="remove"] {
    color: rgba(255, 255, 255, 0.8) !important;
    cursor: pointer;
}

.Select div[class*="multiValue"] div[class*="remove"]:hover {
    background-color: rgba(0, 0, 0, 0.1) !important;
    color: white !important;
}

/* Legacy class support for Dash 1.x compatibility (if needed) */
.Select-control {
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    transition: all var(--transition-base);
}

.network-selector .Select-control {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.Select-control:hover {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.VirtualizedSelectOption {
    transition: all var(--transition-fast);
}

.Select.is-focused .Select-control {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.15);
}

.Select-value {
    background: linear-gradient(135deg, var(--accent-color), #3DB9B0);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 4px 8px;
}

.Select-value-icon {
    border-right: 1px solid rgba(255, 255, 255, 0.3);
    padding: 2px 6px;
}

.Select-value-icon:hover {
    background-color: rgba(0, 0, 0, 0.1);
    color: white;
}

.Select-placeholder {
    color: var(--light-text);
    opacity: 0.9;
}

.Select-menu-outer {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
    border-radius: 12px;
    overflow: visible !important;
    max-height: none !important;
}

.Select-menu {
    max-height: 300px !important;
    overflow-y: auto !important;
}

.Select-option {
    color: var(--text-color);
}

.Select-option.is-focused,
.Select-option.is-selected {
    background: rgba(78, 205, 196, 0.12);
    color: var(--text-color);
}

.Select-arrow {
    border-color: rgba(0, 0, 0, 0.45) transparent transparent;
}

/* ===== ANIMATIONS ===== */
.fade-in {
    animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ===== FOOTER ===== */
footer {
    margin-top: 60px;
    padding: 24px 0;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(10px);
}

/* ===== PLOTLY CHARTS ===== */
.js-plotly-plot {
    background-color: transparent !important;
}

.js-plotly-plot .plotly {
    border-radius: 16px;
    overflow: hidden;
    background: white;
    box-shadow: var(--shadow-md);
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.modebar {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-radius: 8px;
    padding: 4px;
    box-shadow: var(--shadow-sm);
}

.modebar-btn {
    background-color: transparent !important;
    transition: all var(--transition-fast);
    border-radius: 6px;
}

.modebar-btn:hover {
    background-color: rgba(78, 205, 196, 0.15) !important;
}

.dash-graph {
    background-color: transparent !important;
    margin-bottom: 24px;
}

.dash-graph > div {
    border: none !important;
}

.tab-pane {
    background-color: transparent !important;
}

/* Chart container improvements */
#energy-balance-charts-container,
#agg-energy-balance-charts-container,
#capacity-charts-container,
#capex-charts-container,
#opex-charts-container {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

.chart-card-body {
    padding: 0;
}

/* Add subtle section headers */
.chart-section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(78, 205, 196, 0.3);
}

/* ===== NETWORK METADATA ===== */
#network-metadata {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border) !important;
    border-radius: 16px;
    padding: 24px;
    box-shadow: var(--shadow-md);
}

/* ===== HEADER & NAVIGATION ===== */
.app-header {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px 32px;
    border-radius: 20px;
    margin-bottom: 32px;
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(0, 0, 0, 0.05);
    color: var(--text-color);
}

.app-header h1 {
    color: var(--text-color);
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
}

/* Network selector dropdown styling - handled above in Dash 2.x styles */

/* ===== KPI CARDS ===== */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-base);
    border-left: 3px solid var(--accent-color);
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, transparent 50%, rgba(78, 205, 196, 0.06) 50%);
    border-radius: 0 10px 0 100%;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* Clickable KPI Cards */
.kpi-card-clickable {
    cursor: pointer;
    user-select: none;
}

.kpi-card-clickable:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.kpi-card-clickable:active {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-color);
    margin: 4px 0;
    position: relative;
    z-index: 1;
    line-height: 1;
}

.kpi-label {
    font-size: 0.7rem;
    color: var(--light-text);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    position: relative;
    z-index: 1;
}

.kpi-icon {
    font-size: 1.25rem;
    opacity: 0.85;
    position: relative;
    z-index: 1;
    margin-bottom: 2px;
    color: var(--accent-color);
}

/* ===== LOADING STATES ===== */
.loading-skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s ease-in-out infinite;
    border-radius: 8px;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(78, 205, 196, 0.1);
    border-top-color: var(--accent-color);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== UTILITIES ===== */
.text-gradient {
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    box-shadow: var(--shadow-md);
}

.pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ===== DARK MODE ===== */
.dark-mode {
    color-scheme: dark;
}

#app-container.dark-mode {
    color: #E2E8F0;
    background-image:
        radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 80% 80%, rgba(255, 107, 107, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 40% 20%, rgba(78, 205, 196, 0.06) 0%, transparent 55%),
        linear-gradient(135deg, #0F1419 0%, #1A1F36 100%);
    background-blend-mode: screen, screen, screen, normal;
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
}

#app-container.dark-mode::before {
    background:
        radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 80% 80%, rgba(255, 107, 107, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 40% 20%, rgba(78, 205, 196, 0.06) 0%, transparent 55%),
        linear-gradient(135deg, #0F1419 0%, #1A1F36 100%);
    background-blend-mode: screen, screen, screen, normal;
}

.dark-mode .utility-bar {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.35) 0%, rgba(78, 205, 196, 0.25) 100%);
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow: 0 18px 42px rgba(8, 12, 24, 0.6);
}

.dark-mode .utility-label {
    color: rgba(241, 245, 249, 0.85);
}

.dark-mode .utility-brand__title {
    color: #F8FAFC;
}

.dark-mode .utility-brand__subtitle {
    color: rgba(241, 245, 249, 0.75);
}

.dark-mode .utility-badge {
    background: rgba(15, 23, 42, 0.35);
    color: #F8FAFC;
    border-color: rgba(148, 163, 184, 0.45);
}

.dark-mode .utility-meta {
    color: rgba(226, 232, 240, 0.82) !important;
}

.dark-mode .dark-mode-toggle {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.5);
    box-shadow: 0 12px 26px rgba(8, 12, 24, 0.55);
    color: #E2E8F0;
}

.dark-mode .app-header {
    background: rgba(26, 31, 54, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 18px 40px rgba(15, 20, 25, 0.55);
    color: #E2E8F0;
}

.dark-mode .app-header h1,
.dark-mode .app-header p,
.dark-mode .app-header label {
    color: #E2E8F0 !important;
}

.dark-mode h1, .dark-mode h2, .dark-mode h3, .dark-mode h4, .dark-mode h5, .dark-mode h6 {
    color: #E2E8F0;
}

.dark-mode .card {
    background: #131C2C;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .card:hover {
    border-color: rgba(78, 205, 196, 0.3);
}

.dark-mode #tabs {
    background: #131C2C !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .tab-container {
    background: #131C2C;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .tab {
    color: #94A3B8;
}

.dark-mode .tab:hover {
    color: #4ECDC4;
    background-color: rgba(78, 205, 196, 0.1) !important;
}

.dark-mode .tab--selected {
    color: #4ECDC4 !important;
    background-color: rgba(78, 205, 196, 0.15) !important;
}

.dark-mode .sidebar-filter-panel {
    background: rgba(26, 31, 54, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .sidebar-filter-panel h5,
.dark-mode .sidebar-filter-panel label {
    color: #E2E8F0;
}

.dark-mode .sidebar-filter-panel hr {
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

.dark-mode .sidebar-filter-panel .form-check-label:hover {
    color: #4ECDC4;
}

/* Dark mode network button styles */
.dark-mode .network-button {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.15);
    color: rgba(226, 232, 240, 0.85);
}

.dark-mode .network-button:hover {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(78, 205, 196, 0.4);
    color: #E2E8F0;
}

.dark-mode .network-button-active {
    background: rgba(78, 205, 196, 0.25) !important;
    color: #4ECDC4 !important;
    border-color: rgba(78, 205, 196, 0.5) !important;
}

/* Generic dark mode selects */
.dark-mode .Select div[class*="control"] {
    background: rgba(15, 20, 25, 0.8);
    border-color: rgba(255, 255, 255, 0.2);
}

.dark-mode .Select div[class*="menu"] {
    background: rgba(15, 23, 42, 0.98);
}

.dark-mode .Select div[class*="option"] {
    color: #E2E8F0;
}

/* Legacy dark mode styles for Dash 1.x compatibility */
.dark-mode .Select-control {
    background: rgba(15, 20, 25, 0.8);
    border-color: rgba(255, 255, 255, 0.2);
    color: #E2E8F0;
}

.dark-mode .network-selector .Select-control {
    background: rgba(26, 31, 54, 0.9);
    border-color: rgba(78, 205, 196, 0.3);
}

.dark-mode .Select-control:hover {
    border-color: #4ECDC4;
}

.dark-mode .Select-placeholder,
.dark-mode .Select-value-label,
.dark-mode .Select-value-icon {
    color: #E2E8F0 !important;
}

.dark-mode .Select-menu-outer {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.35);
    box-shadow: 0 14px 32px rgba(8, 12, 24, 0.6);
}

.dark-mode .Select-option {
    color: #E2E8F0;
}

.dark-mode .Select-option.is-focused,
.dark-mode .Select-option.is-selected {
    background: rgba(78, 205, 196, 0.22);
    color: #0F172A;
}

.dark-mode .Select-arrow {
    border-color: rgba(226, 232, 240, 0.7) transparent transparent;
}

.dark-mode .empty-state {
    background: rgba(26, 31, 54, 0.92);
    border-color: rgba(78, 205, 196, 0.38);
    box-shadow: 0 12px 28px rgba(8, 12, 24, 0.45);
}

.dark-mode .empty-state:hover {
    border-color: rgba(78, 205, 196, 0.52);
}

.dark-mode .empty-state--warning {
    border-color: rgba(255, 184, 77, 0.55);
}

.dark-mode .empty-state--warning:hover {
    border-color: rgba(255, 184, 77, 0.7);
}

.dark-mode .kpi-card {
    background: rgba(26, 31, 54, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .kpi-card:hover {
    border-color: rgba(78, 205, 196, 0.3);
}

.dark-mode .kpi-value {
    color: #E2E8F0;
}

.dark-mode .kpi-label {
    color: #94A3B8;
}

.dark-mode .js-plotly-plot .plotly {
    background: rgba(26, 31, 54, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .modebar {
    background-color: rgba(15, 20, 25, 0.95) !important;
}

.dark-mode .modebar-btn:hover {
    background-color: rgba(78, 205, 196, 0.2) !important;
}

.dark-mode #energy-balance-charts-container,
.dark-mode #agg-energy-balance-charts-container,
.dark-mode #capacity-charts-container,
.dark-mode #capex-charts-container,
.dark-mode #opex-charts-container {
    background: #1C2437;
}

.dark-mode #network-metadata {
    background: rgba(26, 31, 54, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.dark-mode footer {
    background: rgba(26, 31, 54, 0.5);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .text-muted {
    color: #94A3B8 !important;
}

.dark-mode .welcome-card {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.dark-mode .welcome-feature {
    background: rgba(26, 31, 54, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .network-item {
    background: rgba(26, 31, 54, 0.9);
    border-left: 4px solid #4ECDC4;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .network-item:hover {
    border-left-color: #FF6B6B;
}

/* Dark mode toggle switch styling */
.dark-mode .form-switch .form-check-input {
    background-color: rgba(78, 205, 196, 0.3);
    border-color: rgba(78, 205, 196, 0.5);
}

.dark-mode .form-switch .form-check-input:checked {
    background-color: #4ECDC4;
    border-color: #4ECDC4;
}

/* Dark mode - welcome page specific styling */
/* Target the main welcome card wrapper */
.dark-mode .card.mt-3 {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.dark-mode .card.mt-3 .card-body {
    background: transparent !important;
}

/* Dark mode - feature badges in welcome hero */
.dark-mode .welcome-card span {
    background: rgba(26, 31, 54, 0.9) !important;
    color: #E2E8F0 !important;
    border: 1px solid rgba(78, 205, 196, 0.3);
}

/* Dark mode - network list heading */
.dark-mode h3 {
    color: #E2E8F0;
}

/* Dark mode - main container backgrounds */
.dark-mode .container-fluid,
.dark-mode .container {
    background: transparent !important;
}

/* Dark mode - Enter Dashboard button */
.dark-mode #enter-dashboard-btn {
    background: linear-gradient(135deg, #4ECDC4 0%, #667EEA 100%) !important;
    box-shadow: 0 8px 24px rgba(78, 205, 196, 0.4) !important;
}

.dark-mode #enter-dashboard-btn:hover {
    background: linear-gradient(135deg, #3DB9B0 0%, #5568D3 100%) !important;
    box-shadow: 0 12px 32px rgba(78, 205, 196, 0.5) !important;
}

/* Dark mode toggle label visibility */
.dark-mode-toggle-label {
    transition: color var(--transition-base);
}

.dark-mode .dark-mode-toggle-label {
    color: #E2E8F0 !important;
}

/* Better contrast for dark mode toggle on welcome page */
#dark-mode-toggle + label {
    cursor: pointer;
}
"""


def get_html_template() -> str:
    """Return the custom HTML template with embedded CSS and Font Awesome."""
    return f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
{DASHBOARD_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
        <script>
            // Keyboard accessibility for KPI cards and ARIA labels
            document.addEventListener('DOMContentLoaded', function() {{
                // Add keyboard support for KPI cards
                const kpiCards = document.querySelectorAll('.kpi-card-clickable[role="button"]');
                kpiCards.forEach(function(card) {{
                    card.addEventListener('keydown', function(event) {{
                        // Trigger click on Enter or Space key
                        if (event.key === 'Enter' || event.key === ' ') {{
                            event.preventDefault();
                            card.click();
                        }}
                    }});
                }});

                // Add aria-label to dark mode toggle and modal close button
                const observer = new MutationObserver(function(mutations) {{
                    // Dark mode toggle
                    const darkModeInput = document.querySelector('#dark-mode-toggle input[type="checkbox"]');
                    if (darkModeInput && !darkModeInput.hasAttribute('aria-label')) {{
                        darkModeInput.setAttribute('aria-label', 'Toggle dark mode');
                    }}

                    // Modal close button
                    const modalCloseBtn = document.querySelector('#data-explorer-modal .btn-close');
                    if (modalCloseBtn && !modalCloseBtn.hasAttribute('aria-label')) {{
                        modalCloseBtn.setAttribute('aria-label', 'Close data explorer modal');
                    }}
                }});

                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
            }});
        </script>
    </body>
</html>
"""
