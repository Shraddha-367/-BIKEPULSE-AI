"""
BIKEPULSE AI — Premium UI Theme
Design System: Quiet Luxury + Modern Enterprise Analytics + Restrained Glassmorphism

Color Palette:
  Background:       #0D1B2A  (Deep Navy)
  Primary Surface:  #1B263B  (Royal Navy)
  Accent:           #E5C07B  (Champagne Gold)
  Primary Text:     #F3E9D2  (Luxury Cream)
  Muted Text:       #8A9BB8  (Steel Blue-Grey)
  Success:          #4DAA7A  (Muted Sage Green)
  Warning:          #C9954A  (Warm Amber)
  Error:            #C05A5A  (Muted Crimson)
"""
from pathlib import Path
import streamlit as st


# ── Plotly Template ────────────────────────────────────────────────────────────
DARK_THEME = "plotly_dark"
PLOT_BG    = "rgba(13,27,42,0.0)"
PAPER_BG   = "rgba(13,27,42,0.0)"


# ── Design Tokens ─────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":       "#0D1B2A",
    "bg_secondary":     "#111E2E",
    "surface":          "#1B263B",
    "surface_2":        "#1F2D40",
    "surface_3":        "#243348",

    # Brand
    "gold":             "#E5C07B",
    "gold_soft":        "rgba(229,192,123,0.15)",
    "gold_border":      "rgba(229,192,123,0.22)",
    "gold_hover":       "#F0D49B",

    # Text
    "text_primary":     "#F3E9D2",
    "text_secondary":   "#D4C9B0",
    "text_muted":       "#8A9BB8",
    "text_faint":       "#4A5A70",
    "tag_text":         "#1F2937",
    "tag_icon":         "#1F2937",

    # Glass
    "glass_fill":       "rgba(27,38,59,0.68)",
    "glass_border":     "rgba(229,192,123,0.15)",
    "glass_shadow":     "0 8px 32px rgba(7,14,22,0.38), inset 0 1px 0 rgba(243,233,210,0.08)",

    # Semantic
    "success":          "#4DAA7A",
    "success_soft":     "rgba(77,170,122,0.14)",
    "warning":          "#C9954A",
    "warning_soft":     "rgba(201,149,74,0.14)",
    "error":            "#C05A5A",
    "error_soft":       "rgba(192,90,90,0.14)",

    # Chart colors — professional palette derived from the brand
    "chart_gold":       "#E5C07B",
    "chart_cream":      "#C8B89A",
    "chart_steel":      "#7A9EC9",
    "chart_sage":       "#6AAD8E",
    "chart_rust":       "#C07A5A",
    "chart_slate":      "#9AAECC",
}

# Chart palette for multiple series (ordered by visual priority)
CHART_PALETTE = [
    COLORS["chart_gold"],
    COLORS["chart_steel"],
    COLORS["chart_sage"],
    COLORS["chart_rust"],
    COLORS["chart_cream"],
    COLORS["chart_slate"],
]

CHART_PALETTE_HEX = [
    "#E5C07B",   # Champagne Gold
    "#7A9EC9",   # Steel Blue
    "#6AAD8E",   # Sage Green
    "#C07A5A",   # Terracotta Rust
    "#C8B89A",   # Warm Cream
    "#9AAECC",   # Light Slate
]

# Diverging scale for correlation heatmaps (scientifically correct)
DIVERGING_COLORSCALE = [
    [0.0,  "#2C4A7C"],   # Strong negative — deep blue
    [0.25, "#4A7AA8"],   # Moderate negative
    [0.5,  "#243348"],   # Neutral — dark surface
    [0.75, "#B08A4A"],   # Moderate positive — warm
    [1.0,  "#E5C07B"],   # Strong positive — Champagne Gold
]


def apply_chart_theme(fig, height: int = 400, title: str = ""):
    """Apply premium Navy + Champagne Gold theme to any Plotly figure."""
    layout_args = dict(
        template=DARK_THEME,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor="rgba(27,38,59,0.40)",
        font=dict(
            family="Inter, Manrope, -apple-system, BlinkMacSystemFont, sans-serif",
            color=COLORS["text_secondary"],
            size=12,
        ),
        height=height,
        margin=dict(l=16, r=16, t=40 if title else 20, b=20),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(11,20,33,0.95)",
            bordercolor=COLORS["gold_border"],
            font=dict(
                color=COLORS["text_primary"],
                family="Inter, sans-serif",
                size=12,
            ),
        ),
        xaxis=dict(
            gridcolor="rgba(138,155,184,0.08)",
            linecolor="rgba(243,233,210,0.06)",
            tickfont=dict(color=COLORS["text_muted"], size=11),
            zerolinecolor="rgba(243,233,210,0.06)",
        ),
        yaxis=dict(
            gridcolor="rgba(138,155,184,0.08)",
            linecolor="rgba(243,233,210,0.06)",
            tickfont=dict(color=COLORS["text_muted"], size=11),
            zerolinecolor="rgba(243,233,210,0.06)",
        ),
        legend=dict(
            bgcolor="rgba(13,27,42,0.75)",
            bordercolor=COLORS["gold_border"],
            borderwidth=1,
            font=dict(color=COLORS["text_secondary"], size=12),
        ),
    )
    if title:
        layout_args["title"] = dict(
            text=title,
            font=dict(
                color=COLORS["text_primary"],
                size=14,
                family="Manrope, Inter, sans-serif",
            ),
            x=0.01,
            y=0.97,
        )
    fig.update_layout(**layout_args)
    return fig


def inject_global_css():
    """Inject the premium Navy + Champagne Gold stylesheet."""
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
            html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        </style>
        """, unsafe_allow_html=True)


def get_logo_svg_inline() -> str:
    """Return the BIKEPULSE logo as an inline SVG string."""
    logo_path = Path(__file__).parent / "assets" / "bikepulse-logo.svg"
    if logo_path.exists():
        return logo_path.read_text(encoding="utf-8")
    # Fallback inline SVG
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 48" width="160" height="40">
  <g transform="translate(0, 4)">
    <circle cx="20" cy="20" r="14" fill="none" stroke="#E5C07B" stroke-width="2.2" stroke-dasharray="65 22" stroke-linecap="round"/>
    <polyline points="10,20 14,14 18,24 22,10 26,26 30,20" fill="none" stroke="#E5C07B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="20" cy="20" r="2.2" fill="#E5C07B"/>
  </g>
  <text x="46" y="30" font-family="Manrope,Inter,-apple-system,sans-serif" font-size="17" font-weight="700" letter-spacing="0.5" fill="#F3E9D2">BIKEPULSE</text>
  <text x="166" y="22" font-family="Inter,sans-serif" font-size="9" font-weight="600" letter-spacing="0.5" fill="#E5C07B">AI</text>
</svg>"""
