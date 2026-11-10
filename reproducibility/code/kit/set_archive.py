# -*- coding: utf-8 -*-
"""set_archive.py -- name the archive that holds the deposited package and the
identifier it issued, then rebuild both documents.

Works with any DOI-assigning archive: Zenodo, Software Heritage, Figshare,
OSF, Dataverse, a journal-hosted repository.

Usage:
    python set_archive.py --name "Software Heritage" --id "swh:1:rel:..." \
                          --url "https://archive.softwareheritage.org/swh:1:rel:..."
    python set_archive.py --name "Zenodo" --id "10.5281/zenodo.24112707"
    python set_archive.py --check          # verify the current identifier resolves
"""
import argparse, json, os, re, subprocess, sys, urllib.request, urllib.error

KIT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(KIT, "results")


def resolve(identifier: str, timeout=25):
    """Return (ok, final_url, status). DOIs are resolved through doi.org."""
    url = identifier if identifier.startswith("http") else (
        f"https://doi.org/{identifier}" if identifier.startswith("10.") else
        f"https://archive.softwareheritage.org/{identifier}")
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ms-bdtt-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, r.geturl(), r.status
    except urllib.error.HTTPError as e:
        # some archives reject HEAD; retry with GET
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ms-bdtt-check/1.0"}), timeout=timeout) as r:
                return True, r.geturl(), r.status
        except Exception:
            return False, url, e.code
    except Exception as e:
        return False, url, str(e)[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="")
    ap.add_argument("--id", dest="ident", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-swh", action="store_true",
                    help="remove the Software Heritage archival sentence (for archives "
                         "that do not archive to SWH)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    # optional: drop the SWH sentence when the chosen archive does not archive there
    if a.no_swh:
        swh_sentences = [
            " The archive is one of the DOI-assigning repositories accepted for this purpose, "
            "and the deposited snapshot is additionally archived in the Software Heritage "
            "long-term source-code archive, so that the reviewed version remains citable "
            "independently of the availability of the hosting platform.",
            " The snapshot reviewed for this submission is additionally archived in the Software "
            "Heritage long-term source-code archive, so that the deposited version remains "
            "permanently citable even if the hosting platform becomes unavailable.",
            " and the same snapshot is additionally archived in the Software Heritage long-term "
            "source-code archive.",
        ]
        for d in [os.path.join(KIT, "md_source"),
                  os.environ.get("KIT_WS", r"C:\Users\刘东\WorkBuddy\2026-11-10-11-58-48")]:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(d, fn)
                with open(p, encoding="utf-8") as f:
                    txt = f.read()
                new = txt
                for s in swh_sentences:
                    new = new.replace(s, "")
                if new != txt:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(new)
                    print(f"[no-swh] {fn}")

    arc_path = os.path.join(RES, "archive.json")
    if a.name or a.ident:
        payload = {"name": a.name.strip(), "identifier": a.ident.strip(),
                   "url": a.url.strip(), "dry_run": False}
        if not payload["name"] or not payload["identifier"]:
            print("[refused] both --name and --id are required")
            return 2
        os.makedirs(RES, exist_ok=True)
        with open(arc_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print(f"[written] {arc_path}: {payload['name']} / {payload['identifier']}")
        if a.dry:
            return 0

    # resolve check (always run for the stored identifier)
    stored = {}
    if os.path.exists(arc_path):
        with open(arc_path, encoding="utf-8") as f:
            stored = json.load(f)
    ident = a.ident or stored.get("identifier", "")
    if ident:
        ok, url, st = resolve(ident)
        print(f"[resolve] {ident} -> {st} {url} {'OK' if ok else 'NOT RESOLVABLE YET'}")
        if not ok and not a.check:
            print("           (a DOI that is not yet activated is normal before publication; "
                  "the deposit must be published for it to resolve)")

    if a.check:
        return 0 if ident else 2

    r = subprocess.run([sys.executable, os.path.join(KIT, "fill_and_rebuild.py")],
                       cwd=KIT, text=True, capture_output=True)
    print((r.stdout or "")[-1200:])
    if r.returncode != 0:
        print((r.stderr or "")[-600:])
        return r.returncode
    from docx import Document
    out_dir = os.environ.get("KIT_OUT_DIR", r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110")
    for fn in ["manuscript_major_revision.docx", "Response_to_Editor_and_Reviewers.docx"]:
        p = os.path.join(out_dir, fn)
        if not os.path.exists(p):
            print(f"  {fn}: MISSING")
            continue
        doc = Document(p)
        txt = "\n".join(pp.text for pp in doc.paragraphs)
        for tb in doc.tables:
            for row in tb.rows:
                txt += "\n" + " | ".join(c.text for c in row.cells)
        left = re.findall(r"⟦FILL-[^⟧]*⟧", txt)
        print(f"  {fn}: placeholders={len(left)} {sorted(set(left))} "
              f"| archive mentioned={stored.get('name','') in txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
