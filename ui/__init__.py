"""
BIKEPULSE AI — UI Module
Exports theme, navigation, and component renderers.
"""
from ui.theme import inject_global_css, DARK_THEME, PLOT_BG
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import (
    render_hero_section,
    render_wide_dashboard_preview,
    render_four_stat_cards,
    render_capabilities_section,
    render_modules_grid,
    render_how_it_works,
    render_about_section,
    render_footer,
)

__all__ = [
    "inject_global_css",
    "DARK_THEME",
    "PLOT_BG",
    "render_top_navbar",
    "render_sidebar_drawer",
    "render_hero_section",
    "render_wide_dashboard_preview",
    "render_four_stat_cards",
    "render_capabilities_section",
    "render_modules_grid",
    "render_how_it_works",
    "render_about_section",
    "render_footer",
]
