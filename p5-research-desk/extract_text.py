"""Turn the annual report PDF into one text file with page markers, so an agent can search it and cite pages."""
from pypdf import PdfReader

reader = PdfReader("tcs-annual-report.pdf")
with open("tcs-report.txt", "w") as out:
    for number, page in enumerate(reader.pages, start=1):
        out.write(f"\n=== PAGE {number} ===\n")
        out.write(page.extract_text() or "")
print(f"pages: {len(reader.pages)}")
