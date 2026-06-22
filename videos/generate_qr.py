#!/usr/bin/env python3
"""
Crypto-Course — QR Code Generator for Printed Textbook
=======================================================
Generates QR codes for each of the 14 module landing pages.

Before running:
  1. Replace GITHUB_USER and REPO_NAME below with your actual values.
  2. pip install segno
  3. python generate_qr.py

Output: /videos/qr/module_01.png + module_01.svg  ...  module_14.png + module_14.svg
        (28 files total)

QR spec:
  - Error correction: H (highest — survives up to 30% damage, suitable for print)
  - PNG: scale=10 px/module at 300 DPI  → ≥3.5 cm for typical URL lengths
  - SVG: inherently scalable — size in your layout tool to ≥2 cm × 2 cm
  - Colours: pure black (#000000) on white (#ffffff)
  - Quiet zone: segno default (4 modules each side — ISO minimum)
"""

import os
import sys

# ── CONFIGURE THESE TWO CONSTANTS BEFORE RUNNING ──────────────────────────────
GITHUB_USER = "aabdalaal"
REPO_NAME   = "crypto-course"
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL   = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/videos/module.html"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr")
MODULES    = range(1, 15)  # 1 inclusive .. 14 inclusive


def check_segno():
    try:
        import segno  # noqa: F401
    except ImportError:
        print("ERROR: 'segno' is not installed.")
        print("       Run:  pip install segno")
        sys.exit(1)


def generate():
    import segno

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    col_w = max(len(str(n)) + 8 for n in MODULES)  # "Module 14" = 9 chars
    url_ex = f"{BASE_URL}?m=14"
    print(f"\n{'Module':<{col_w}}  {'PNG':>18}  {'SVG':>18}  URL")
    print("-" * (col_w + 2 + 18 + 2 + 18 + 2 + len(url_ex)))

    for n in MODULES:
        url = f"{BASE_URL}?m={n}"

        qr = segno.make(url, error="h", micro=False)

        png_name = f"module_{n:02d}.png"
        svg_name = f"module_{n:02d}.svg"
        png_path = os.path.join(OUTPUT_DIR, png_name)
        svg_path = os.path.join(OUTPUT_DIR, svg_name)

        # PNG: 10 px per module at 300 DPI
        # A version-5-H symbol (37 modules + 8 quiet-zone modules = 45) →
        # 45 × 10 = 450 px / 300 dpi × 2.54 cm/in ≈ 3.8 cm  (well above 2 cm)
        qr.save(png_path, scale=10, dpi=300, dark="#000000", light="#ffffff")

        # SVG: scale=1 (segno default unit is mm) → 45 mm ≈ 4.5 cm per side
        # Scale freely in your layout software; minimum recommended: 2 cm × 2 cm
        qr.save(svg_path, scale=1, dark="#000000", light="#ffffff")

        label = f"Module {n}"
        print(f"{label:<{col_w}}  {png_name:>18}  {svg_name:>18}  {url}")

    total = len(list(MODULES)) * 2
    print(f"\n✓  {total} files written to: {OUTPUT_DIR}/")
    print(f"\nSTABLE PRINTED URLS:")
    print("-" * (len(url_ex) + 12))
    for n in MODULES:
        print(f"  Module {n:>2}  →  {BASE_URL}?m={n}")
    print()

    if GITHUB_USER == "AHMED-PLACEHOLDER" or REPO_NAME == "REPO-PLACEHOLDER":
        print("⚠  WARNING: GITHUB_USER / REPO_NAME are still placeholders.")
        print("   The generated QR codes encode placeholder URLs.")
        print("   Edit generate_qr.py and re-run before printing.\n")


if __name__ == "__main__":
    check_segno()
    generate()
