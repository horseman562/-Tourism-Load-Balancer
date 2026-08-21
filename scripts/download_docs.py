"""Download resolved DOSM release documents into data/raw/dosm-publications/.

Only downloads ids already proven live by resolve_docs.py, keeps the server's
original filename alongside a readable name, and appends provenance to
data/manifest.json.

Usage: download_docs.py <docid>[:<slug>] ...
"""
import csv, hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESOLVED = os.path.join(ROOT, "data", "index", "resolved_docs.csv")
PUBS = os.path.join(ROOT, "data", "index", "dosm_publications.csv")
DEST = os.path.join(ROOT, "data", "raw", "dosm-publications")
MANIFEST = os.path.join(ROOT, "data", "manifest.json")
DELAY = 1.5
LICENCE = ("Open Data Terms of Use (Terma Penggunaan Data Terbuka), "
           "https://www.data.gov.my/terms-of-use -- attribution required")


def load_manifest():
    if os.path.exists(MANIFEST):
        return json.load(open(MANIFEST, encoding="utf-8"))
    return {"generated": "", "files": []}


def main():
    resolved = {r["release_document_id"]: r for r in csv.DictReader(open(RESOLVED, encoding="utf-8"))}
    titles = {}
    for r in csv.DictReader(open(PUBS, encoding="utf-8")):
        if r["release_document_id"]:
            titles.setdefault(r["release_document_id"], (r["title"], r["release_date"]))

    os.makedirs(DEST, exist_ok=True)
    man = load_manifest()
    have = {f.get("release_document_id") for f in man["files"]}

    for arg in sys.argv[1:]:
        docid, _, slug = arg.partition(":")
        rec = resolved.get(docid)
        if not rec:
            print(f"{docid}: not in resolved_docs.csv -- run resolve_docs.py first")
            continue
        if rec["http_status"] != "200":
            print(f"{docid}: HTTP {rec['http_status']}, skipping (dead link)")
            continue
        title, date = titles.get(docid, ("", ""))
        name = f"{slug or docid}.pdf"
        path = os.path.join(DEST, name)
        if docid in have and os.path.exists(path):
            print(f"{docid}: already downloaded -> {name}")
            continue
        r = subprocess.run(["curl", "-sSL", "--max-time", "600", "-o", path,
                            "-w", "%{http_code} %{size_download}", rec["resolved_url"]],
                           capture_output=True, text=True)
        code, _, size = (r.stdout or "0 0").partition(" ")
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else ""
        print(f"{docid}: {code} {int(size or 0)/1e6:.1f}MB -> {name}")
        man["files"] = [f for f in man["files"] if f.get("release_document_id") != docid]
        man["files"].append({
            "release_document_id": docid,
            "dosm_release_name": title,
            "release_date": date,
            "savedAs": os.path.relpath(path, ROOT).replace("\\", "/"),
            "sourceUrl": f"https://www.dosm.gov.my/portal-main/release-document-log?release_document_id={docid}",
            "resolvedFileUrl": rec["resolved_url"],
            "serverFilename": rec["server_filename"],
            "bytes": int(size or 0),
            "sha256": sha,
            "retrieved": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "publisher": "Department of Statistics Malaysia (DOSM)",
            "licence": LICENCE,
            "status": "REAL",
        })
        time.sleep(DELAY)

    man["generated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    man["files"].sort(key=lambda f: str(f.get("savedAs") or f.get("release_document_id")))
    json.dump(man, open(MANIFEST, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\nmanifest: {len(man['files'])} files -> {os.path.relpath(MANIFEST, ROOT)}")


if __name__ == "__main__":
    main()
