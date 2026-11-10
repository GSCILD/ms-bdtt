# -*- coding: utf-8 -*-
"""insert_doi.py -- put the Zenodo DOI into the manuscript and the response
letter, then rebuild both documents.

Usage:
    python insert_doi.py --doi 10.5281/zenodo.1234567
    python insert_doi.py --from-file doi.txt        # first line = the DOI
    python insert_doi.py --doi ... --tag v2.0-confirmatory --commit abc1234

It writes kit/results/f1_zenodo.json (dry_run = false) and then runs
fill_and_rebuild.py, which replaces the three DOI slots (one in the
manuscript, two in the letter) and rebuilds both .docx files.
"""
import argparse, json, os, re, subprocess, sys

KIT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(KIT, "results")
DOI_RE = re.compile(r"^10\.5281/zenodo\.\d{4,}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi", default="")
    ap.add_argument("--from-file", default="")
    ap.add_argument("--tag", default="v2.0-confirmatory")
    ap.add_argument("--commit", default="")
    ap.add_argument("--dry", action="store_true", help="write the DOI file only")
    a = ap.parse_args()

    doi = a.doi.strip()
    if a.from_file:
        with open(a.from_file, encoding="utf-8") as f:
            doi = f.read().strip().splitlines()[0].strip()
    if not DOI_RE.match(doi):
        print(f"[refused] '{doi}' is not a Zenodo DOI of the form 10.5281/zenodo.NNNNN")
        return 2

    os.makedirs(RES, exist_ok=True)
    payload = {"doi": doi, "release_tag": a.tag, "commit_hash": a.commit,
               "dry_run": False}
    with open(os.path.join(RES, "f1_zenodo.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"[written] {os.path.join(RES, 'f1_zenodo.json')} -> {doi}")

    # Idempotent re-insertion: if a DOI string is already present in the
    # markdown sources (previous insertion), rewrite it to the new value so
    # that a corrected DOI can be substituted without restoring the token.
    existing = re.compile(r"10\.5281/zenodo\.\d{4,}")
    md_dirs = [os.path.join(KIT, "md_source"),
               os.environ.get("KIT_WS", r"C:\Users\刘东\WorkBuddy\2026-11-10-11-58-48")]
    for d in md_dirs:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            p = os.path.join(d, fn)
            with open(p, encoding="utf-8") as f:
                txt = f.read()
            if existing.search(txt) and doi not in txt:
                txt2 = existing.sub(doi, txt)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(txt2)
                print(f"[replaced] previous DOI -> {doi} in {os.path.basename(p)}")
    if a.dry:
        return 0

    r = subprocess.run([sys.executable, os.path.join(KIT, "fill_and_rebuild.py")],
                       cwd=KIT, text=True, capture_output=True)
    print((r.stdout or "")[-1200:])
    if r.returncode != 0:
        print((r.stderr or "")[-800:])
        return r.returncode
    # verification: no DOI slot may remain
    import re as _re
    from docx import Document
    out_dir = os.environ.get("KIT_OUT_DIR", r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110")
    for fn in ["manuscript_major_revision.docx", "Response_to_Editor_and_Reviewers.docx"]:
        p = os.path.join(out_dir, fn)
        doc = Document(p)
        txt = "\n".join(pp.text for pp in doc.paragraphs)
        for tb in doc.tables:
            for row in tb.rows:
                txt += "\n" + " | ".join(c.text for c in row.cells)
        left = _re.findall(r"⟦FILL-[^⟧]*⟧", txt)
        print(f"  {fn}: placeholders left={len(left)} {sorted(set(left))} "
              f"| DOI present={doi in txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
