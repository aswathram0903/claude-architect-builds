"""Run the two ambiguous invoices 3 times each, without and with few-shot examples."""
import pathlib

from extract import FEW_SHOT, extract

DOCS = ["docs/b-email.txt", "docs/e-ambiguous.txt"]

for label, extra in [("WITHOUT examples", ""), ("WITH examples", FEW_SHOT)]:
    print(f"\n--- {label} ---")
    for d in DOCS:
        text = pathlib.Path(d).read_text()
        results = []
        for _ in range(3):
            r = extract(text, extra)
            results.append(f"{r['category']} ({r['category_detail']})")
        print(f"{pathlib.Path(d).stem:14} {results}")
