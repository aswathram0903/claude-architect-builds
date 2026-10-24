"""P3: extract invoice data with tool_use and a JSON schema."""
import json
import pathlib
import sys

import anthropic

MODEL = "claude-haiku-5-5"  # check docs.claude.com for current model names
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

INVOICE_TOOL = {
    "name": "record_invoice",
    "description": "Record the data from ONE invoice. Use null for any field the document does not state. Never guess.",
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor": {"type": "string"},
            "invoice_number": {"type": ["string", "null"]},
            "invoice_date": {"type": ["string", "null"], "description": "YYYY-MM-DD"},
            "due_date": {"type": ["string", "null"], "description": "YYYY-MM-DD. null if the document gives no date."},
            "currency": {"type": "string", "enum": ["EUR", "USD", "GBP", "INR", "other", "unknown"]},
            "currency_detail": {"type": ["string", "null"], "description": "Only when currency is 'other'"},
            "category": {"type": "string", "enum": ["software", "hardware", "services", "other"]},
            "category_detail": {"type": ["string", "null"], "description": "Only when category is 'other'"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "amount": {"type": "number"},
                    },
                    "required": ["description", "quantity", "amount"],
                },
            },
            "stated_total": {"type": ["number", "null"], "description": "The total exactly as written on the invoice"},
            "calculated_total": {"type": "number", "description": "The sum of the line item amounts"},
            "conflict_detected": {"type": "boolean", "description": "True if stated_total and calculated_total differ"},
        },
        "required": [
            "vendor", "invoice_number", "invoice_date", "due_date", "currency", "currency_detail",
            "category", "category_detail", "line_items", "stated_total", "calculated_total", "conflict_detected",
        ],
    },
}

SYSTEM = "You extract invoice data. Copy what the document states. If a value is not in the document, use null. Do not infer or invent values."

FEW_SHOT = """

Category rules, with examples:
- "Annual licence for design software" -> software (the thing bought is the software itself).
- "Engineer installed and configured the firewall, 5 hours" -> services (people's time, even when the subject is software or hardware).
- "Two monitors delivered and installed" -> hardware (the thing bought is a device; installation is a small part).
- Laptops bought AND engineer hours billed, with neither clearly the main item -> other, category_detail "mixed: hardware + services".
"""


def extract(text: str, extra_system: str = "") -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM + extra_system,
        tools=[INVOICE_TOOL],
        tool_choice={"type": "tool", "name": "record_invoice"},
        messages=[{"role": "user", "content": f"\n{text}\n"}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    raise RuntimeError(f"No tool call. stop_reason={response.stop_reason}")


if __name__ == "__main__":
    use_examples = "--few-shot" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = files or sorted(str(p) for p in pathlib.Path("docs").glob("*.txt"))
    out = pathlib.Path("out")
    out.mkdir(exist_ok=True)
    for f in files:
        data = extract(pathlib.Path(f).read_text(), FEW_SHOT if use_examples else "")
        name = pathlib.Path(f).stem
        (out / f"{name}.json").write_text(json.dumps(data, indent=2))
        print(f"\n=== {name} ===\n{json.dumps(data, indent=2)}")
