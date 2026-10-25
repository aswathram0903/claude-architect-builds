"""P3 session 2: send all invoices as one Message Batch, then collect results by custom_id."""
import json
import pathlib
import sys

from extract import INVOICE_TOOL, MODEL, SYSTEM, client

ID_FILE = pathlib.Path("out/batch_id.txt")


def submit() -> None:
    requests = []
    for p in sorted(pathlib.Path("docs").glob("*.txt")):
        requests.append({
            "custom_id": p.stem,
            "params": {
                "model": MODEL,
                "max_tokens": 1024,
                "system": SYSTEM,
                "tools": [INVOICE_TOOL],
                "messages": [{"role": "user", "content": f"<document>\n{p.read_text()}\n</document>"}],
            },
        })
    # One request that is broken on purpose, so you can see a failure by custom_id.
    requests.append({
        "custom_id": "z-broken",
        "params": {"model": MODEL, "max_tokens": 1024,
                   "messages": [{"role": "user", "content": ""}]},
    })
    batch = client.messages.batches.create(requests=requests)
    ID_FILE.parent.mkdir(exist_ok=True)
    ID_FILE.write_text(batch.id)
    print(f"Submitted {len(requests)} requests. Batch id: {batch.id}")
    print("Status:", batch.processing_status)


def status() -> None:
    batch = client.messages.batches.retrieve(ID_FILE.read_text().strip())
    print("Status:", batch.processing_status)
    print("Counts:", batch.request_counts)
    if batch.processing_status != "ended":
        print("Not finished yet. Run this again in a few minutes.")
        return
    failed = []
    for entry in client.messages.batches.results(batch.id):
        kind = entry.result.type
        if kind == "succeeded":
            data = next((b.input for b in entry.result.message.content if b.type == "tool_use"), None)
            vendor = data.get("vendor") if data else "(no tool call)"
            print(f"  {entry.custom_id:14} succeeded  vendor={vendor!r}")
        else:
            failed.append(entry.custom_id)
            print(f"  {entry.custom_id:14} {kind}")
    print("\nResubmit only these custom_ids:", failed or "none")


if __name__ == "__main__":
    {"submit": submit, "status": status}[sys.argv[1] if len(sys.argv) > 1 else "status"]()
