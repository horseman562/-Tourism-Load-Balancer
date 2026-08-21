"""Resolve release_document_id -> real /uploads/... URL and record its HTTP status.

`portal-main/release-document-log?release_document_id=N` is a 302 logger, not a
file, and a listed link is frequently dead (33 of 34 files in the 2023 DTS state
release 404). This resolves without downloading: -I follows the redirect and
reports the final URL, content-type and length.

Usage:  resolve_docs.py <ids.txt|docid> [...]   -> data/index/resolved_docs.csv
"""
import csv, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "index", "resolved_docs.csv")
LOG = "https://www.dosm.gov.my/portal-main/release-document-log?release_document_id={}"
DELAY = 1.5
FIELDS = ["release_document_id", "http_status", "resolved_url", "server_filename",
          "content_type", "content_length_bytes"]


def resolve(docid):
    r = subprocess.run(
        ["curl", "-sSIL", "--max-time", "45", "-A",
         "Mozilla/5.0 (research; DOSM Datathon 2026 entry)",
         "-w", "\n__EFFECTIVE__%{url_effective}\n__CODE__%{http_code}\n",
         LOG.format(docid)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    body = r.stdout or ""
    url = (re.search(r"__EFFECTIVE__(.*)", body) or [None, ""])[1].strip()
    code = (re.search(r"__CODE__(\d+)", body) or [None, "000"])[1].strip()
    ctype = ""
    clen = ""
    for m in re.finditer(r"(?im)^content-type:\s*(.+)$", body):
        ctype = m.group(1).strip()
    for m in re.finditer(r"(?im)^content-length:\s*(\d+)$", body):
        clen = m.group(1).strip()
    return {
        "release_document_id": str(docid), "http_status": code, "resolved_url": url,
        "server_filename": url.rsplit("/", 1)[-1] if "/uploads/" in url else "",
        "content_type": ctype, "content_length_bytes": clen,
    }


def main():
    ids = []
    for a in sys.argv[1:]:
        if os.path.exists(a):
            ids += [l.strip() for l in open(a) if l.strip() and not l.startswith("#")]
        else:
            ids.append(a)
    seen, uniq = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            uniq.append(i)

    done = {}
    if os.path.exists(OUT):
        for row in csv.DictReader(open(OUT, encoding="utf-8")):
            done[row["release_document_id"]] = row

    rows = []
    for n, i in enumerate(uniq, 1):
        if i in done:
            rows.append(done[i])
            continue
        rec = resolve(i)
        rows.append(rec)
        ok = rec["http_status"] == "200" and "pdf" in rec["content_type"].lower()
        size = f"{int(rec['content_length_bytes'])/1e6:.1f}MB" if rec["content_length_bytes"] else "?"
        print(f"[{n}/{len(uniq)}] {i:>6s} {rec['http_status']} "
              f"{'OK ' if ok else 'DEAD'} {size:>8s} {rec['server_filename']}", flush=True)
        time.sleep(DELAY)

    for k, v in done.items():
        if k not in seen:
            rows.append(v)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    live = sum(1 for r in rows if r["http_status"] == "200")
    print(f"\n{live}/{len(rows)} live -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
