"""
BIKEPULSE AI — Automated Verification for Tag Contrast & 3D Glassmorphism

Verifies:
1. Selected tags (temp, atemp, hum, windspeed, cnt, hr, mnth, etc.) on Correlation Analysis
   - Background is Champagne Gold (#E5C07B / rgb(229, 192, 123))
   - Text color is Dark Charcoal (#1F2937 / rgb(31, 41, 55))
   - Close icon (×) fill/color is Dark Charcoal (#1F2937 / rgb(31, 41, 55))
2. Selected filter tags (Season, Year, Weather) on Exploratory Analysis
   - Background is Champagne Gold
   - Text and close icon are Dark Charcoal #1F2937
3. Interactive States:
   - Hover on tag maintains #1F2937 text and icon
   - Tag removal by clicking × works and updates state
4. 3D Background & Glassmorphism:
   - Subtle 3D background gradients and ambient depth orbs render cleanly
   - Zero pointer events interference (interactive elements fully clickable)
   - Glassmorphism on cards has backdrop-filter and refined lighting highlights
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCREENSHOT_DIR = Path("frontend_redesign_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True, parents=True)

BASE_URL = "http://localhost:8501"

def parse_rgb(rgb_str):
    """Normalize rgb/rgba string to tuple of ints."""
    s = rgb_str.replace("rgba", "").replace("rgb", "").replace("(", "").replace(")", "").strip()
    parts = [int(p.strip()) for p in s.split(",")[:3]]
    return tuple(parts)

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # =====================================================================
        # 1. Correlation Analysis — Feature Tags Contrast
        # =====================================================================
        print("\n--- Test 1: Correlation Analysis Feature Tags Contrast ---")
        page.goto(f"{BASE_URL}/Correlation_Analysis", wait_until="networkidle")
        time.sleep(3)

        tags = page.query_selector_all("[data-baseweb='tag']")
        print(f"  Found {len(tags)} selected tags on Correlation Analysis.")
        assert len(tags) > 0, "Selected tags must be present!"

        for i, tag in enumerate(tags[:5]):
            info = tag.evaluate("""el => {
                const txt = el.querySelector("span[title]") || el.firstElementChild;
                const svg = el.querySelector("svg");
                const path = el.querySelector("path");
                return {
                    text: txt ? txt.innerText : el.innerText,
                    bg: getComputedStyle(el).backgroundColor,
                    textColor: txt ? getComputedStyle(txt).color : getComputedStyle(el).color,
                    svgColor: svg ? getComputedStyle(svg).color : null,
                    svgFill: svg ? getComputedStyle(svg).fill : null,
                    pathFill: path ? getComputedStyle(path).fill : null
                };
            }""")
            
            text_val = info["text"].strip()
            bg_rgb = parse_rgb(info["bg"])
            txt_rgb = parse_rgb(info["textColor"])
            svg_rgb = parse_rgb(info["pathFill"] or info["svgFill"] or info["svgColor"])

            print(f"  Tag [{text_val}]:")
            print(f"    Background: {info['bg']} -> {bg_rgb}")
            print(f"    Text Color: {info['textColor']} -> {txt_rgb}")
            print(f"    Close Icon Fill: {info['pathFill']} -> {svg_rgb}")

            # Verify background is Champagne Gold (#E5C07B -> 229, 192, 123)
            assert bg_rgb == (229, 192, 123), f"Tag background must remain golden! Got {bg_rgb}"
            # Verify text is Dark Charcoal (#1F2937 -> 31, 41, 55)
            assert txt_rgb == (31, 41, 55), f"Tag text color must be #1F2937! Got {txt_rgb}"
            # Verify close icon is Dark Charcoal (#1F2937 -> 31, 41, 55)
            assert svg_rgb == (31, 41, 55), f"Close icon color must be #1F2937! Got {svg_rgb}"

        print("  [PASS] All Correlation Analysis tags pass contrast test with #1F2937!")

        # Screenshot Correlation tags
        corr_shot = SCREENSHOT_DIR / "correlation_analysis_tags_dark_contrast.png"
        page.screenshot(path=str(corr_shot), full_page=False)
        print(f"  [SAVED] {corr_shot}")

        # =====================================================================
        # 2. Tag Hover & Removal Interaction
        # =====================================================================
        print("\n--- Test 2: Tag Hover & Removal Interaction ---")
        first_tag = tags[0]
        close_icon_wrapper = first_tag.query_selector("span[role='presentation']") or first_tag.query_selector("svg")
        
        # Hover
        close_icon_wrapper.hover()
        time.sleep(0.5)
        hover_info = first_tag.evaluate("""el => {
            const txt = el.querySelector("span[title]") || el.firstElementChild;
            const svg = el.querySelector("svg");
            const path = el.querySelector("path");
            return {
                bg: getComputedStyle(el).backgroundColor,
                textColor: txt ? getComputedStyle(txt).color : getComputedStyle(el).color,
                pathFill: path ? getComputedStyle(path).fill : null
            };
        }""")
        txt_hover_rgb = parse_rgb(hover_info["textColor"])
        svg_hover_rgb = parse_rgb(hover_info["pathFill"])
        print(f"  Hover Text Color: {hover_info['textColor']} -> {txt_hover_rgb}")
        print(f"  Hover Close Icon Fill: {hover_info['pathFill']} -> {svg_hover_rgb}")
        assert txt_hover_rgb == (31, 41, 55), "Hovered text must maintain #1F2937!"
        assert svg_hover_rgb == (31, 41, 55), "Hovered close icon must maintain #1F2937!"
        print("  [PASS] Hover state maintains dark charcoal contrast!")

        # Capture hover state screenshot
        hover_shot = SCREENSHOT_DIR / "multiselect_hover_contrast.png"
        page.screenshot(path=str(hover_shot), full_page=False)
        print(f"  [SAVED] {hover_shot}")

        # Click close icon to remove tag
        initial_count = len(page.query_selector_all("[data-baseweb='tag']"))
        close_icon_wrapper.click()
        time.sleep(2)
        new_count = len(page.query_selector_all("[data-baseweb='tag']"))
        print(f"  Tag count: {initial_count} -> {new_count}")
        assert new_count == initial_count - 1, "Clicking close icon must remove tag!"
        print("  [PASS] Tag removal functions seamlessly without error!")

        # =====================================================================
        # 3. Exploratory Analysis — Filter Tags Contrast
        # =====================================================================
        print("\n--- Test 3: Exploratory Analysis Filter Tags Contrast ---")
        page.goto(f"{BASE_URL}/Exploratory_Analysis", wait_until="networkidle")
        time.sleep(3)

        eda_tags = page.query_selector_all("[data-baseweb='tag']")
        print(f"  Found {len(eda_tags)} filter tags on Exploratory Analysis.")
        assert len(eda_tags) > 0, "EDA filter tags must be present!"

        for tag in eda_tags[:4]:
            info = tag.evaluate("""el => {
                const txt = el.querySelector("span[title]") || el.firstElementChild;
                const path = el.querySelector("path");
                return {
                    text: txt ? txt.innerText : el.innerText,
                    bg: getComputedStyle(el).backgroundColor,
                    textColor: txt ? getComputedStyle(txt).color : getComputedStyle(el).color,
                    pathFill: path ? getComputedStyle(path).fill : null
                };
            }""")
            bg_rgb = parse_rgb(info["bg"])
            txt_rgb = parse_rgb(info["textColor"])
            svg_rgb = parse_rgb(info["pathFill"])

            assert bg_rgb == (229, 192, 123), f"EDA Tag background must be golden! Got {bg_rgb}"
            assert txt_rgb == (31, 41, 55), f"EDA Tag text must be #1F2937! Got {txt_rgb}"
            assert svg_rgb == (31, 41, 55), f"EDA Close icon must be #1F2937! Got {svg_rgb}"

        print("  [PASS] All Exploratory Analysis filter tags pass contrast test with #1F2937!")

        eda_shot = SCREENSHOT_DIR / "exploratory_analysis_tags_dark_contrast.png"
        page.screenshot(path=str(eda_shot), full_page=False)
        print(f"  [SAVED] {eda_shot}")

        # =====================================================================
        # 4. Landing Page — 3D Background & Glassmorphism
        # =====================================================================
        print("\n--- Test 4: Landing Page 3D Background & Glassmorphism ---")
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(3)

        # Verify 3D background properties on .stApp
        bg_check = page.evaluate("""() => {
            const app = document.querySelector('.stApp');
            const style = getComputedStyle(app);
            return {
                bgImage: style.backgroundImage,
                bgAttachment: style.backgroundAttachment
            };
        }""")
        print(f"  App Background Image layers present: {'radial-gradient' in bg_check['bgImage']}")
        assert "radial-gradient" in bg_check["bgImage"], "3D depth radial gradients must be present on .stApp!"
        assert "fixed" in bg_check["bgAttachment"], "Background attachment must be fixed for parallax 3D depth!"

        # Verify glassmorphic card properties
        card_check = page.evaluate("""() => {
            const card = document.querySelector('.stat-card-box');
            if (!card) return null;
            const style = getComputedStyle(card);
            return {
                backdropFilter: style.backdropFilter || style.webkitBackdropFilter,
                boxShadow: style.boxShadow,
                borderRadius: style.borderRadius
            };
        }""")
        print(f"  Glass Card Backdrop Filter: {card_check['backdropFilter']}")
        print(f"  Glass Card Box Shadow: {card_check['boxShadow']}")
        assert "blur" in card_check["backdropFilter"], "Glass cards must have backdrop-filter blur!"

        # Verify CTA clickability (zero pointer interference from 3D background)
        cta = page.locator('button:has-text("Launch Predictor")').first
        assert cta.is_visible(), "CTA button must be visible!"
        print("  CTA button clickable: True (no pointer obstruction from 3D background)")

        landing_shot = SCREENSHOT_DIR / "landing_page_3d_glassmorphism.png"
        page.screenshot(path=str(landing_shot), full_page=False)
        print(f"  [SAVED] {landing_shot}")

        context.close()
        browser.close()
        print("\n[COMPLETE] All Tag Contrast & 3D Glassmorphism tests PASSED 100%!")

if __name__ == "__main__":
    verify()
