"""
Audit all 10 pages for emojis, titles, headers, buttons, colors, and layout consistency.
"""
import glob
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

pages = sorted(glob.glob("pages/*.py"))
for p in pages:
    path = Path(p)
    text = path.read_text(encoding="utf-8")
    
    # Emojis regex
    emojis = re.findall(r'[\U00010000-\U0010ffff\u2600-\u27bf]', text)
    # Page config
    page_icon = re.findall(r'page_icon=([^\,\)]+)', text)
    # Titles
    titles = re.findall(r'st\.title\((.*?)\)', text)
    # Headers
    headers = re.findall(r'st\.header\((.*?)\)', text)
    # Subheaders
    subheaders = re.findall(r'st\.subheader\((.*?)\)', text)
    
    print(f"=== {path.name} ===")
    print(f"  page_icon: {page_icon}")
    print(f"  title: {titles}")
    print(f"  emoji count: {len(emojis)} -> {set(emojis)}")
    print(f"  sample headers: {headers[:3]}")
    print(f"  apply_chart_theme used: {'apply_chart_theme' in text}")
