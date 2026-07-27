#!/usr/bin/env python3
"""
Nácar & Ledger — guide deck -> web PDF pipeline.

Converts branded .pptx decks into the slug-named PDFs that resources.html
links to, using LibreOffice headless conversion.

Usage:
    python3 build_guides.py

To add a new guide later: drop the source .pptx in SOURCE_DIR, add one
line to MANIFEST below with its slug (must match the href used in
resources.html), then re-run.
"""

import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "source"
OUTPUT_DIR = Path(__file__).parent / "guides"
SOFFICE_SCRIPT = Path("/mnt/skills/public/pptx/scripts/office/soffice.py")

# slug -> source .pptx filename (source lives in SOURCE_DIR)
MANIFEST = {
    "pay-yourself-single-member-llc": "Single-Owner LLC Draws - Nacar Ledger Branded.pptx",
    "gifted-products-taxable-income": "Creator Basics - Gifted Products Are Taxable - Nacar Ledger Branded.pptx",
    "multi-platform-1099-reconciliation": "Multi-Platform 1099 Reconciliation - Nacar Ledger Branded.pptx",
    "w2-vs-1099": "W-2 vs 1099 Hiring Guide - Nacar Ledger Branded.pptx",
    "irs-three-factor-test": "IRS Three-Factor Test Guide - Nacar Ledger Branded.pptx",
    "1099-to-w2-conversion": "1099 to W-2 Conversion Guide - Nacar Ledger Branded.pptx",
    "va-passes-irs-test-rhode-island": "RI-MA ABC Test Healthcare VA Guide - Nacar Ledger Branded.pptx",
    "intercompany-transfers-top-10": "Intercompany Transfers Top 10 - Nacar Ledger Branded.pptx",
    "intercompany-transfers-top-10-es": "Transferencias Entre Empresas Top 10 - Nacar Ledger Branded (ES).pptx",
}


def convert_one(slug: str, source_name: str) -> bool:
    src = SOURCE_DIR / source_name
    if not src.exists():
        print(f"  MISSING SOURCE: {source_name}")
        return False

    result = subprocess.run(
        [
            sys.executable, str(SOFFICE_SCRIPT),
            "--headless", "--convert-to", "pdf",
            "--outdir", str(OUTPUT_DIR),
            str(src),
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  CONVERT FAILED: {source_name}\n{result.stderr}")
        return False

    produced = OUTPUT_DIR / (src.stem + ".pdf")
    target = OUTPUT_DIR / f"{slug}.pdf"
    if not produced.exists():
        print(f"  NO OUTPUT PRODUCED for {source_name}")
        return False

    produced.replace(target)
    size_kb = target.stat().st_size // 1024
    print(f"  OK  {slug}.pdf  ({size_kb} KB)")
    return True


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Converting {len(MANIFEST)} guides -> {OUTPUT_DIR}/\n")

    ok, failed = 0, []
    for slug, source_name in MANIFEST.items():
        if convert_one(slug, source_name):
            ok += 1
        else:
            failed.append(slug)

    print(f"\n{ok}/{len(MANIFEST)} converted.")
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
