"""Second-pass doorway-page localisation. Handles prose-level Gold Coast → Darwin
replacements that bulk_replace's URL/brand mode missed.

Run AFTER _bulk_replace.py. Idempotent.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).name

# Order matters — longer phrases first to avoid partial-match collisions.
REPLACE = [
    # Phrases / multi-word
    ("City of Gold Coast LGA", "Greater Darwin"),
    ("City of Gold Coast", "Greater Darwin"),
    ("Gold Coast LGA", "Greater Darwin"),
    ("Gold Coast canal-estate", "rural Litchfield acreage"),
    ("Gold Coast canal estates", "rural Litchfield acreage and bushland-boundary blocks"),
    ("canal-estate properties (Sovereign Islands, Sanctuary Cove, Hope Island, Robina Quays)",
     "rural Litchfield acreage and bushland-boundary blocks (Howard Springs, Humpty Doo, Berry Springs, Marlow Lagoon)"),
    ("Sovereign Islands, Sanctuary Cove", "Howard Springs, Humpty Doo"),
    ("Mermaid Beach, Burleigh Heads, Palm Beach, Coolangatta, Broadbeach",
     "Parap, Stuart Park, Coconut Grove, Berrimah, Karama"),
    ("Coolangatta to Coomera", "Casuarina to Humpty Doo"),
    ("Mudgeeraba, Tallai, Currumbin Valley", "Howard Springs, Humpty Doo, Berry Springs"),
    ("Mudgeeraba", "Howard Springs"),
    ("Tallai", "Berry Springs"),
    ("Currumbin Valley", "Humpty Doo"),
    ("(Mudgeeraba, Tallai", "(Howard Springs, Humpty Doo"),
    ("(Sovereign Islands, Sanctuary Cove", "(Howard Springs, Humpty Doo"),
    ("Pier-and-beam Gold Coast homes",
     "Older high-set Darwin and Nightcliff homes on stumps"),
    ("Beachside (Mermaid, Burleigh, Currumbin, Coolangatta)",
     "Coastal Darwin (Nightcliff, Rapid Creek, Casuarina foreshore)"),
    ("beachside (Mermaid, Burleigh, Currumbin, Coolangatta)",
     "coastal Darwin (Nightcliff, Rapid Creek, Casuarina foreshore)"),
    ("Wetlands / lake edge (Coombabah, Robina Quays)",
     "Bushland-boundary acreage (Howard Springs, Humpty Doo)"),
    ("wetlands / lake edge (Coombabah, Robina Quays)",
     "bushland-boundary acreage (Howard Springs, Humpty Doo)"),
    ("Surfers Paradise 0800, Robina 4226, Coombabah 4216",
     "Palmerston 0830, Casuarina 0810, Humpty Doo 0836"),

    # Hero / section headings (replace by exact match)
    (">in Gold Coast homes<", ">in Top End homes<"),
    (">in Gold Coast conditions<", ">in Top End conditions<"),
    ("For Gold Coast home buyers", "For Greater Darwin home buyers"),
    ("Termite Conducive Conditions Gold Coast", "Termite Conducive Conditions Darwin"),
    ("Pre-Purchase Termite Inspection Checklist Gold Coast", "Pre-Purchase Termite Inspection Checklist Darwin"),
    ("Termite Treatment Warranties &amp; Insurance Gold Coast", "Termite Treatment Warranties &amp; Insurance Darwin"),
    ("Termite Treatment Warranties & Insurance Gold Coast", "Termite Treatment Warranties & Insurance Darwin"),
    ("Termidor vs Sentricon Gold Coast", "Termidor vs Sentricon Darwin"),
    ("Signs of Termites Gold Coast", "Signs of Termites Darwin"),

    # Section h2 / h3 headings
    ("The Gold Coast specific factor", "The Top End-specific factor"),
    ("The Gold Coast specific risks", "The Top End-specific risks"),
    ("The Gold Coast environment factor", "The Top End environment factor"),

    # Specific phrases in body prose
    ("Gold Coast inspections in within 24", "Greater Darwin inspections within 24"),
    ("Gold Coast canal-estate and inland properties", "rural Litchfield acreage and urban Darwin"),
    ("Gold Coast canal-estate", "rural Litchfield acreage"),
    ("Gold Coast home", "Top End home"),
    ("Gold Coast subsoil", "Top End subsoil"),
    ("Gold Coast insurers", "NT insurers"),
    ("Properties at higher pre-purchase termite risk on the Gold Coast",
     "Properties at higher pre-purchase termite risk in Greater Darwin"),
    ("coastal Gold Coast subsoil", "Top End subsoil"),
    ("Gold Coast termite inspection", "Darwin termite inspection"),
    ("Book a Gold Coast termite inspection",
     "Book a Greater Darwin termite inspection"),
    ("we&rsquo;ve seen this on the Gold Coast in 2025",
     "we&rsquo;ve seen this in Darwin in 2025-2026"),
    ("spring (September&ndash;November on the Gold Coast)",
     "wet-season build-up (September&ndash;November in the Top End)"),

    # Plain phrases (catch-all — must come AFTER more specific ones)
    ("approaches work for Gold Coast conditions",
     "approaches work in Top End conditions"),
    ("the Gold Coast", "Greater Darwin"),
    ("Gold Coast inspectors", "NT pest controllers"),

    # Drywood / regional rarity note
    ("Rare on Gold Coast", "Rare in the NT"),

    # QBCC → NT licensing
    ("QBCC pest-licensed", "NT Pest Control licensed"),
    ("QBCC pest-management", "NT Pest Control"),
    ("QBCC-licensed", "NT Pest Control licensed"),
    ("look up at QBCC online", "look up at the NT Government Pest Management licence register"),
    ("QBCC", "NT Pest Control"),

    # Area-pill link text (visible labels in <a> body) — match per-line
    ('href="/palmerston/">Surfers Paradise</a>', 'href="/palmerston/">Palmerston</a>'),
    ('href="/casuarina/">Southport</a>',         'href="/casuarina/">Casuarina</a>'),
    ('href="/nightcliff/">Robina</a>',           'href="/nightcliff/">Nightcliff</a>'),
    ('href="/humpty-doo/">Coombabah</a>',        'href="/humpty-doo/">Humpty Doo</a>'),
    ('href="/howard-springs/">Currumbin</a>',    'href="/howard-springs/">Howard Springs</a>'),
    ('href="/greater-darwin/">All City of Gold Coast</a>',
     'href="/greater-darwin/">All Greater Darwin</a>'),
    ('href="/greater-darwin/">All Greater Darwin LGA</a>',
     'href="/greater-darwin/">All Greater Darwin</a>'),

    # As3660-barriers specific: high-risk Currumbin/Mudgeeraba example
    ("High-risk area or wooded surrounds (Currumbin, Mudgeeraba",
     "High-risk area or wooded surrounds (Howard Springs, Humpty Doo, Berry Springs"),

    # Postcode + suburb common typos (already covered by bulk_replace; safe to repeat)
    ("Surfers Paradise 4217", "Palmerston 0830"),

    # Generic plain "Gold Coast" (last-resort) → Darwin
    # Disabled — too broad. We've handled all named Gold Coast contexts above.
    # ("Gold Coast", "Darwin"),
]

EXTENSIONS = {".astro", ".md", ".html", ".js", ".toml", ".mjs", ".json", ".xml", ".txt", ".css"}


def patch(p: Path) -> bool:
    try:
        s = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    out = s
    for a, b in REPLACE:
        out = out.replace(a, b)
    if out != s:
        p.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in EXTENSIONS:
            continue
        if any(seg in p.parts for seg in ("node_modules", "dist", ".astro")):
            continue
        if p.name == SELF:
            continue
        if patch(p):
            print("patched:", p.relative_to(ROOT))
            n += 1
    print(f"Done. {n} files patched.")


if __name__ == "__main__":
    main()
