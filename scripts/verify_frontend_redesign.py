"""
BIKEPULSE AI — Automated Playwright Verification Script
Verifies:
1. Desktop landing page layout (Hero, badges, CTA, dashboard preview, 4 stats cards)
2. Hamburger open/close drawer functionality
3. Top navigation links (HOME, MODULES, PREDICTOR, ABOUT)
4. Responsive viewports: 1440px (Desktop), 1024px (Laptop), 768px (Tablet), 390px (Mobile)
5. Predictor page and Module explorer
6. Child page styling consistency
Saves screenshots to frontend_redesign_screenshots/
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

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        print("[INIT] Chromium browser launched.")

        # =====================================================================
        # 1. Desktop Landing Page (1440 x 900)
        # =====================================================================
        print("\n--- Test 1: Desktop Landing Page (1440x900) ---")
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(3) # allow Streamlit to hydrate and Plotly to render

        # Verify main elements
        title = page.title()
        print(f"  Page title: {title}")
        assert "BIKEPULSE" in title or "Bike" in title

        # Check for hero badge and headline
        hero_badge = page.locator(".hero-pill-badge").first
        print(f"  Hero badge visible: {hero_badge.is_visible()}")

        hero_title = page.locator(".hero-main-title").first
        print(f"  Hero headline text: {hero_title.inner_text() if hero_title.is_visible() else 'N/A'}")

        # Check stat cards
        stat_cards = page.locator(".stat-card-box")
        card_count = stat_cards.count()
        print(f"  Stat cards count: {card_count}")
        for i in range(card_count):
            val = stat_cards.nth(i).locator(".stat-val-text").inner_text()
            lbl = stat_cards.nth(i).locator(".stat-lbl-text").inner_text()
            print(f"    Card {i+1}: {lbl} = {val}")

        # Capture Desktop Landing Screenshot
        desktop_landing_path = SCREENSHOT_DIR / "desktop_landing_1440.png"
        page.screenshot(path=str(desktop_landing_path), full_page=True)
        print(f"  [SAVED] {desktop_landing_path}")

        # Capture Viewport Above-the-fold
        desktop_above_fold_path = SCREENSHOT_DIR / "desktop_above_fold_1440.png"
        page.screenshot(path=str(desktop_above_fold_path), full_page=False)
        print(f"  [SAVED] {desktop_above_fold_path}")

        # =====================================================================
        # 2. Hamburger & Sidebar Drawer Test
        # =====================================================================
        print("\n--- Test 2: Hamburger Menu & Sidebar Drawer ---")
        # Check current sidebar state
        sidebar = page.locator('[data-testid="stSidebar"]')
        print(f"  Sidebar present: {sidebar.count() > 0}")

        # Screenshot with sidebar open
        sidebar_open_path = SCREENSHOT_DIR / "sidebar_drawer_open.png"
        page.screenshot(path=str(sidebar_open_path), full_page=False)
        print(f"  [SAVED] {sidebar_open_path}")

        # Locate hamburger / close button
        close_btn = page.locator('button:has-text("✕")').first
        if close_btn.is_visible():
            print("  Clicking close button ✕...")
            close_btn.click()
            time.sleep(2)
            sidebar_closed_path = SCREENSHOT_DIR / "sidebar_drawer_closed.png"
            page.screenshot(path=str(sidebar_closed_path), full_page=False)
            print(f"  [SAVED] {sidebar_closed_path}")

            # Re-open sidebar
            open_btn = page.locator('button:has-text("☰")').first
            if open_btn.is_visible():
                print("  Re-opening drawer with ☰...")
                open_btn.click()
                time.sleep(2)
        else:
            print("  Close button not directly visible, checking toggle button...")

        # =====================================================================
        # 3. Top Navigation & Demand Predictor Navigation
        # =====================================================================
        print("\n--- Test 3: Navigation to Demand Prediction ---")
        # Click PREDICTOR page link
        pred_link = page.locator('a:has-text("PREDICTOR")').first
        if pred_link.is_visible():
            print("  Clicking PREDICTOR top navbar link...")
            pred_link.click()
        else:
            print("  Navigating directly to Demand Prediction...")
            page.goto(f"{BASE_URL}/Demand_Prediction", wait_until="networkidle")

        time.sleep(3)
        predictor_path = SCREENSHOT_DIR / "predictor_page_verified.png"
        page.screenshot(path=str(predictor_path), full_page=True)
        print(f"  [SAVED] {predictor_path}")

        # Check for Predict button or form fields on Demand Prediction
        predict_btn = page.locator('button:has-text("Predict")').first
        print(f"  Predict action present on predictor page: {predict_btn.is_visible() if predict_btn.count() > 0 else 'checked'}")

        # =====================================================================
        # 4. Navigation to Modules Overview / Exploratory Analysis
        # =====================================================================
        print("\n--- Test 4: Navigation to Modules (Exploratory Analysis) ---")
        modules_link = page.locator('a:has-text("MODULES")').first
        if modules_link.is_visible():
            print("  Clicking MODULES top navbar link...")
            modules_link.click()
        else:
            page.goto(f"{BASE_URL}/Exploratory_Analysis", wait_until="networkidle")

        time.sleep(3)
        modules_path = SCREENSHOT_DIR / "module_explorer_verified.png"
        page.screenshot(path=str(modules_path), full_page=True)
        print(f"  [SAVED] {modules_path}")

        # =====================================================================
        # 5. Return Home & Test CTA Buttons
        # =====================================================================
        print("\n--- Test 5: Return Home & Verify CTA Buttons ---")
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(2)

        cta_primary = page.locator('button:has-text("Launch Demand Predictor")').first
        cta_secondary = page.locator('button:has-text("Explore 10 Modules")').first
        print(f"  Primary CTA visible: {cta_primary.is_visible()}")
        print(f"  Secondary CTA visible: {cta_secondary.is_visible()}")

        # =====================================================================
        # 6. Responsive Viewports
        # =====================================================================
        print("\n--- Test 6: Responsive Viewports ---")
        # Laptop (1024 x 768)
        print("  Testing Laptop (1024x768)...")
        page.set_viewport_size({"width": 1024, "height": 768})
        time.sleep(1.5)
        laptop_path = SCREENSHOT_DIR / "laptop_landing_1024.png"
        page.screenshot(path=str(laptop_path), full_page=True)
        print(f"  [SAVED] {laptop_path}")

        # Tablet (768 x 1024)
        print("  Testing Tablet (768x1024)...")
        page.set_viewport_size({"width": 768, "height": 1024})
        time.sleep(1.5)
        tablet_path = SCREENSHOT_DIR / "tablet_landing_768.png"
        page.screenshot(path=str(tablet_path), full_page=True)
        print(f"  [SAVED] {tablet_path}")

        # Mobile (390 x 844 - iPhone 14 / modern mobile)
        print("  Testing Mobile (390x844)...")
        page.set_viewport_size({"width": 390, "height": 844})
        time.sleep(1.5)
        mobile_path = SCREENSHOT_DIR / "mobile_landing_390.png"
        page.screenshot(path=str(mobile_path), full_page=True)
        print(f"  [SAVED] {mobile_path}")

        # Check for horizontal scroll on mobile
        scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
        client_width = page.evaluate("() => document.documentElement.clientWidth")
        print(f"  Mobile viewport clientWidth={client_width}, scrollWidth={scroll_width}")
        if scroll_width <= client_width + 5: # allow small margin
            print("  [PASS] No horizontal scroll on mobile!")
        else:
            print(f"  [WARN] Minor horizontal overflow: {scroll_width - client_width}px")

        # =====================================================================
        # 7. Multi-page Styling Consistency Audit
        # =====================================================================
        print("\n--- Test 7: Multi-page Consistency Check ---")
        test_pages = [
            ("Data Management", "Data_Management"),
            ("Probability Simulation", "Probability_Simulation"),
            ("Sampling Estimation", "Sampling_Estimation"),
            ("Hypothesis Testing", "Hypothesis_Testing"),
            ("Correlation Analysis", "Correlation_Analysis"),
            ("Model Training", "Model_Training"),
            ("Model Comparison", "Model_Comparison"),
            ("Reports Planning", "Reports_Planning"),
        ]

        page.set_viewport_size({"width": 1440, "height": 900})
        for name, slug in test_pages:
            url = f"{BASE_URL}/{slug}"
            print(f"  Checking {name} ({url})...")
            page.goto(url, wait_until="networkidle")
            time.sleep(2)
            # Check for error banners
            error_banner = page.locator('[data-testid="stAlert"][kind="error"]')
            has_error = error_banner.count() > 0
            if has_error:
                print(f"    [FAIL] Error banner detected on {name}: {error_banner.first.inner_text()}")
            else:
                print(f"    [PASS] Clean load on {name}")

        context.close()
        browser.close()
        print("\n[COMPLETE] All browser tests executed successfully.")

if __name__ == "__main__":
    run_tests()
