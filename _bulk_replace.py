"""Bulk find/replace + page rename for Darwin Termite Barriers.

CONSERVATIVE — only boilerplate (URLs, brand, suburb names, postcode/coords, file renames).
All deep content hand-rewritten per page.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELF_NAME = Path(__file__).name

REPLACEMENTS = [
    # URL + brand
    ("https://goldcoasttermite.com.au", "https://darwintermitebarriers.com.au"),
    ("https://goldcoasttermite.netlify.app", "https://darwintermitebarriers.netlify.app"),
    ("goldcoasttermite.netlify.app", "darwintermitebarriers.netlify.app"),
    ("goldcoasttermite.com.au", "darwintermitebarriers.com.au"),
    ("goldcoasttermite", "darwintermitebarriers"),
    ("Gold Coast Termite Specialists", "Darwin Termite Barriers"),
    ("Gold Coast Termite", "Darwin Termite Barriers"),

    # Suburb URL renames
    ("/surfers-paradise/", "/palmerston/"),
    ("/southport/", "/casuarina/"),
    ("/robina/", "/nightcliff/"),
    ("/coombabah/", "/humpty-doo/"),
    ("/currumbin/", "/howard-springs/"),
    ("/city-of-gold-coast/", "/greater-darwin/"),

    # Doorway page rename (species: Coptotermes is GC, Mastotermes is Darwin signature)
    ("/coptotermes-species/", "/mastotermes-darwiniensis/"),

    # State / postcode / coords
    ("QLD 4217", "NT 0800"),
    ('"QLD"', '"NT"'),
    ('"4217"', '"0800"'),
    ("Gold Coast QLD 4217", "Darwin NT 0800"),
    ("4217", "0800"),
    ("-28.0023", "-12.4634"),
    ("153.4145", "130.8456"),

    # Favicon letter (template has T already — keep as "D" for Darwin)
    (">T</text>", ">D</text>"),
]

EXTENSIONS = {".astro", ".md", ".toml", ".mjs", ".json", ".xml", ".txt", ".html", ".css", ".js"}


def patch_file(p):
    try:
        s = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    out = s
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    if out != s:
        p.write_text(out, encoding="utf-8")
        return True
    return False


def main():
    PAGES = ROOT / "src" / "pages"
    # Suburb page renames
    for old, new in [
        ("surfers-paradise.astro", "palmerston.astro"),
        ("southport.astro", "casuarina.astro"),
        ("robina.astro", "nightcliff.astro"),
        ("coombabah.astro", "humpty-doo.astro"),
        ("currumbin.astro", "howard-springs.astro"),
        ("city-of-gold-coast.astro", "greater-darwin.astro"),
        # Doorway: Coptotermes (Gold Coast signature species) → Mastotermes (Darwin signature)
        ("coptotermes-species.astro", "mastotermes-darwiniensis.astro"),
    ]:
        o, n = PAGES / old, PAGES / new
        if o.exists() and not n.exists():
            o.rename(n)
            print(f"renamed: {old} -> {new}")

    changed = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in EXTENSIONS:
            continue
        if "node_modules" in p.parts or "dist" in p.parts or ".astro" in p.parts:
            continue
        if p.name == SELF_NAME:
            continue
        if patch_file(p):
            changed += 1

    pkg = ROOT / "package.json"
    if pkg.exists():
        s = pkg.read_text(encoding="utf-8")
        s = s.replace('"name": "goldcoasttermite"', '"name": "darwintermitebarriers"')
        pkg.write_text(s, encoding="utf-8")

    print(f"Done. {changed} files patched.")


if __name__ == "__main__":
    main()
