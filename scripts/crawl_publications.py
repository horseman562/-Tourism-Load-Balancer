"""Phase 1: crawl every page of dosm.gov.my/portal-main/publication into a CSV index.

Uses curl (Python's TLS stack fails on dosm.gov.my's incomplete chain).
Sequential, 1.5s delay. Does NOT download PDFs and does NOT resolve document
URLs -- that is deferred to resolve_docs.py so the index crawl stays cheap.
"""
import csv, html, os, re, subprocess, sys, time

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "index", "dosm_publications.csv")
CACHE = os.path.join(os.path.dirname(__file__), "..", "data", "_tmp", "pubpages")
DELAY = 1.5
BASE = "https://www.dosm.gov.my/portal-main/publication?page={}"

ROW_RE = re.compile(
    r'<tr data-key="\d+">\s*<td>(?P<date>.*?)</td>\s*<td>(?P<title>.*?)</td>.*?'
    r'(?:release_document_id=(?P<docid>\d+))?\s*"?\s*target',
    re.S,
)
CELL_RE = re.compile(r"<tr data-key=\"\d+\">(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
DOCID_RE = re.compile(r"release_document_id=(\d+)")
TAG_RE = re.compile(r"<[^>]+>")


def clean(s):
    return html.unescape(TAG_RE.sub("", s)).strip().replace("\r", " ")


def fetch(page):
    path = os.path.join(CACHE, f"p{page:04d}.html")
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return open(path, encoding="utf-8", errors="replace").read()
    r = subprocess.run(
        ["curl", "-sSL", "--compressed", "--max-time", "60", "-A",
         "Mozilla/5.0 (research; DOSM Datathon 2026 entry; contact via dosm.gov.my)",
         BASE.format(page)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode != 0 or len(r.stdout) < 5000:
        return None
    open(path, "w", encoding="utf-8").write(r.stdout)
    return r.stdout


def parse(h, page):
    out = []
    for block in CELL_RE.findall(h):
        tds = TD_RE.findall(block)
        if len(tds) < 2:
            continue
        m = DOCID_RE.search(block)
        out.append({
            "page": page,
            "release_date": clean(tds[0]),
            "title": clean(tds[1]),
            "release_document_id": m.group(1) if m else "",
        })
    return out


def main():
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    last = int(sys.argv[1]) if len(sys.argv) > 1 else 307
    rows, failed = [], []
    for p in range(1, last + 1):
        h = fetch(p)
        if h is None:
            failed.append(p)
            print(f"page {p}: FETCH FAILED", flush=True)
            time.sleep(DELAY)
            continue
        got = parse(h, p)
        rows.extend(got)
        if p % 20 == 0 or p == 1:
            print(f"page {p}/{last}: {len(got)} rows (total {len(rows)})", flush=True)
        if not got:
            print(f"page {p}: 0 rows -- check parser", flush=True)
        time.sleep(DELAY)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["page", "release_date", "title", "release_document_id"])
        w.writeheader()
        w.writerows(rows)
    print(f"DONE {len(rows)} rows -> {OUT}; failed pages: {failed}", flush=True)


if __name__ == "__main__":
    main()
