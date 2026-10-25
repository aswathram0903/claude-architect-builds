"""P3 session 2: check each extraction, retry once with the specific errors, then route."""
import json
import pathlib
import random
import re

from extract import INVOICE_TOOL, MODEL, SYSTEM, client, extract

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(d: dict) -> list[dict]:
    """Checks the schema cannot do. Each error says whether a retry can fix it."""
    errors = []
    items_sum = round(sum(item["amount"] for item in d.get("line_items", [])), 2)
    if abs(items_sum - d.get("calculated_total", 0)) > 0.01:
        errors.append({"field": "calculated_total", "retry": True,
                       "problem": f"calculated_total is {d.get('calculated_total')}, but the line item amounts add up to {items_sum}."})
    for field in ("invoice_date", "due_date"):
        value = d.get(field)
        if value is not None and not DATE.match(str(value)):
            errors.append({"field": field, "retry": True,
                           "problem": f"{field} is '{value}', which is not in YYYY-MM-DD format."})
    if d.get("stated_total") is not None and abs(d["stated_total"] - items_sum) > 0.01:
        errors.append({"field": "stated_total", "retry": True,
                       "problem": f"The stated total is {d['stated_total']}, but the line items add up to {items_sum}. "
                                  "Check that each amount is the line total, not the unit price."})
    if d.get("due_date") is None:
        errors.append({"field": "due_date", "retry": False,
                       "problem": "No due date in the document. Payment cannot be scheduled."})
    if d.get("currency") == "unknown":
        errors.append({"field": "currency", "retry": False,
                       "problem": "No currency in the document."})
    return errors


def retry_with_errors(text: str, failed: dict, errors: list[dict]) -> dict:
    """Send the document, the failed extraction and the specific errors back to Claude."""
    feedback = "\n".join(f"- {e['problem']}" for e in errors)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        tools=[INVOICE_TOOL],
        messages=[{"role": "user", "content":
            f"<document>\n{text}\n</document>\n\n"
            f"Your earlier extraction was:\n<extraction>\n{json.dumps(failed, indent=2)}\n</extraction>\n\n"
            f"It failed these checks:\n{feedback}\n\n"
            "Read the document again and call record_invoice with a corrected extraction. "
            "Fix only what the document supports. If the document itself is inconsistent, "
            "keep its values exactly as written and set conflict_detected to true."}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise RuntimeError(f"No tool call on retry. stop_reason={response.stop_reason}")


def process(path: pathlib.Path, simulate_slip: bool = False) -> dict:
    text = path.read_text()
    data = extract(text)
    if simulate_slip:
        data["invoice_date"] = "14.09.2026"  # a format slip, planted on purpose
    print(f"\n=== {path.stem} ===")
    errors = validate(data)
    for e in errors:
        print(f"  check 1: {e['field']}: {e['problem']}  [retry can fix: {e['retry']}]")
    fixable = [e for e in errors if e["retry"]]
    retried = False
    if fixable:
        data = retry_with_errors(text, data, fixable)
        retried = True
        errors = validate(data)
        for e in errors:
            print(f"  check 2 (after 1 retry): {e['field']}: {e['problem']}")
    decision = "AUTO-APPROVE" if not errors else "HUMAN REVIEW"
    print(f"  -> {decision}" + (" (fixed by retry)" if retried and not errors else ""))
    return {"document": path.stem, "decision": decision, "retried": retried,
            "reasons": [e["problem"] for e in errors], "extraction": data}


if __name__ == "__main__":
    results = []
    for p in sorted(pathlib.Path("docs").glob("*.txt")):
        results.append(process(p, simulate_slip=(p.stem == "a-tidy")))
    approved = [r for r in results if r["decision"] == "AUTO-APPROVE"]
    if approved:
        spot = random.choice(approved)
        spot["decision"] = "AUTO-APPROVE + SPOT CHECK"
        print(f"\nSpot check (random sample of auto-approved): {spot['document']}")
    out = pathlib.Path("out")
    out.mkdir(exist_ok=True)
    (out / "review_queue.json").write_text(json.dumps(results, indent=2))
    print("\nSummary:")
    for r in results:
        print(f"  {r['document']:14} {r['decision']}")
