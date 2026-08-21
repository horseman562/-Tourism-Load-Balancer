"""Phase 1: build data/index/datasets.csv -- every machine-readable dataset id
published on open.dosm.gov.my and data.gov.my, plus the dosm-malaysia/data-open
repo file list.

Source of truth is the __NEXT_DATA__ blob embedded in each catalogue page.
"""
import csv, json, os, re, subprocess

HERE = os.path.dirname(__file__)
TMP = os.path.join(HERE, "..", "data", "_tmp")
OUT = os.path.join(HERE, "..", "data", "index", "datasets.csv")

CATALOGUES = [
    ("open.dosm.gov.my", "https://open.dosm.gov.my/data-catalogue", "opendosm_catalogue.html"),
    ("data.gov.my", "https://data.gov.my/data-catalogue", "dgm_catalogue.html"),
]
NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)

FIELDS = ["site", "theme", "subtheme", "id", "title", "data_as_of", "data_source",
          "link_csv", "link_parquet", "has_editions", "description"]


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return open(path, encoding="utf-8", errors="replace").read()
    r = subprocess.run(["curl", "-sSL", "--compressed", "--max-time", "60", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    open(path, "w", encoding="utf-8").write(r.stdout)
    return r.stdout


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    for site, url, fname in CATALOGUES:
        h = fetch(url, os.path.join(TMP, fname))
        data = json.loads(NEXT_RE.search(h).group(1))
        coll = data["props"]["pageProps"]["collection"]
        for theme, subs in coll.items():
            for sub, items in subs.items():
                for it in items:
                    rows.append({
                        "site": site, "theme": theme, "subtheme": sub,
                        "id": it.get("id", ""), "title": it.get("title", ""),
                        "data_as_of": it.get("data_as_of", ""),
                        "data_source": "; ".join(it.get("data_source") or []),
                        "link_csv": it.get("link_csv") or "",
                        "link_parquet": it.get("link_parquet") or "",
                        "has_editions": "yes" if it.get("link_editions") else "no",
                        "description": (it.get("description") or "").replace("\n", " "),
                    })
        print(f"{site}: {sum(1 for r in rows if r['site']==site)} datasets")

    # dosm-malaysia/data-open repo contents (GitHub API, no auth needed for public repo)
    r = subprocess.run(["curl", "-sSL", "--max-time", "60",
                        "https://api.github.com/repos/dosm-malaysia/data-open/git/trees/main?recursive=1"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        tree = json.loads(r.stdout).get("tree", [])
    except json.JSONDecodeError:
        tree = []
    n = 0
    for node in tree:
        if node.get("type") != "blob":
            continue
        p = node["path"]
        if not p.lower().endswith((".csv", ".geojson", ".json", ".ipynb", ".parquet")):
            continue
        rows.append({
            "site": "github:dosm-malaysia/data-open", "theme": p.split("/")[0],
            "subtheme": "", "id": p, "title": os.path.basename(p), "data_as_of": "",
            "data_source": "DOSM",
            "link_csv": f"https://raw.githubusercontent.com/dosm-malaysia/data-open/main/{p}",
            "link_parquet": "", "has_editions": "no",
            "description": f"{node.get('size', '')} bytes",
        })
        n += 1
    print(f"github data-open: {n} files")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"DONE {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
