"""
build_report.py - convert docs/final_report.md to docs/final_report.pdf

Pipeline:
  1. Read the markdown source
  2. Convert markdown to HTML using the `markdown` package
  3. Resolve relative image paths so xhtml2pdf can embed the figures
  4. Wrap in a CSS-styled HTML template (academic paper look)
  5. Render to PDF using xhtml2pdf (pure Python - no system libs needed)

Run from the project root: `python docs/build_report.py`
"""

from pathlib import Path
import markdown
from xhtml2pdf import pisa

# === Paths ===
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
MD_PATH = HERE / "final_report.md"
PDF_PATH = HERE / "final_report.pdf"

# === CSS - academic paper look, A4, page numbers ===
CSS = """
@page {
    size: A4;
    margin: 2.2cm 2.0cm 2.4cm 2.0cm;
    @frame footer {
        -pdf-frame-content: footerContent;
        bottom: 1cm;
        margin-left: 2cm;
        margin-right: 2cm;
        height: 1cm;
    }
}
body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1a1a1a;
}
h1 {
    font-size: 18pt;
    margin-bottom: 0.2em;
    margin-top: 0;
    color: #1a1a1a;
}
h2 {
    font-size: 13pt;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    color: #1a1a1a;
    border-bottom: 1px solid #888;
    padding-bottom: 2px;
}
h3 {
    font-size: 11pt;
    margin-top: 0.9em;
    margin-bottom: 0.3em;
    color: #1a1a1a;
}
p {
    margin-top: 0;
    margin-bottom: 0.6em;
    text-align: justify;
}
hr {
    border: 0;
    border-top: 1px solid #ccc;
    margin: 1.2em 0;
}
strong { color: #1a1a1a; }
em { color: #333; }
table {
    border-collapse: collapse;
    margin: 0.8em auto;
    font-size: 7.5pt;
    width: 100%;
    table-layout: fixed;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #888;
    padding: 2px 3px;
    text-align: center;
}
th {
    background-color: #e8e8e8;
    font-weight: bold;
}
img {
    max-width: 100%;
    margin: 0.5em auto;
    display: block;
    -pdf-keep-with-next: true;
}
ul, ol {
    margin-top: 0.3em;
    margin-bottom: 0.6em;
    padding-left: 1.8em;
}
li { margin-bottom: 0.2em; }
img {
    max-width: 100%;
    margin: 0.5em auto;
    display: block;
}
blockquote {
    margin: 0.5em 1.5em;
    color: #333;
    border-left: 3px solid #888;
    padding-left: 0.8em;
}
code {
    font-family: Courier, monospace;
    font-size: 9pt;
    background-color: #f0f0f0;
    padding: 1px 3px;
}
"""

# === Build ===
def main() -> int:
    print("Reading markdown source...", flush=True)
    md_text = MD_PATH.read_text(encoding="utf-8")

    print("Converting markdown to HTML...", flush=True)
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list"],
    )

    # We use a custom link_callback (defined below) to resolve image paths,
    # so the markdown's "../outputs/" srcs can be left alone.

    print("Wrapping in styled HTML template...", flush=True)
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Final Report - ECC3479</title>
    <style>{CSS}</style>
</head>
<body>
{html_body}
<div id="footerContent" style="text-align: center; font-size: 8pt; color: #666;">
    Anton Kozlovsky (36194239) - ECC3479 Final Report - Page <pdf:pagenumber />
</div>
</body>
</html>
"""

    def link_callback(uri: str, rel: str) -> str:
        """Resolve image src paths in the HTML to absolute filesystem paths.

        The markdown uses '../outputs/<file>.png' which is relative to docs/.
        xhtml2pdf's URI resolver chokes on spaces in absolute file paths, so we
        normalise the path ourselves and return the bare path.
        """
        if uri.startswith(("http://", "https://", "data:")):
            return uri
        # Strip leading ./ and resolve relative to docs/
        candidate = (HERE / uri).resolve()
        if candidate.exists():
            return str(candidate)
        # Fallback: resolve relative to project root
        alt = (PROJECT_ROOT / uri).resolve()
        if alt.exists():
            return str(alt)
        print(f"WARNING: link_callback could not resolve {uri!r}")
        return uri

    print(f"Rendering PDF to {PDF_PATH.name}...", flush=True)
    with open(PDF_PATH, "wb") as out_pdf:
        result = pisa.CreatePDF(
            html_doc, dest=out_pdf, encoding="utf-8", link_callback=link_callback
        )

    if result.err:
        print(f"ERROR: xhtml2pdf reported {result.err} errors during render.")
        return 1

    size_kb = PDF_PATH.stat().st_size / 1024
    print(f"OK - wrote {PDF_PATH} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
