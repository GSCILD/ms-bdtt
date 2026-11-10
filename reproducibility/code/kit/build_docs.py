# -*- coding: utf-8 -*-
"""Build the two deliverable .docx files via editor_sdk (edsdk.py direct RPC)."""
import sys, os, re, io, json
sys.path.insert(0, r"D:\Program Files (x86)\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit")
sys.path.insert(0, r"D:\Program Files (x86)\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\server")
import importlib.util
spec = importlib.util.spec_from_file_location("edsdk", r"D:\Program Files (x86)\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\edsdk.py")
edsdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edsdk)

WS = r"C:\Users\刘东\WorkBuddy\2026-11-10-11-58-48"
FIGS = os.path.join(WS, "figs")
OUT_DIR = r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110"
REV_FIG = {5: r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110\Fig5_修改版.png",
           10: r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110\Fig10_修改版.png"}

LOG = []

def call(name, args, timeout=120):
    res = edsdk._rpc("tools/call", {"name": name, "arguments": args})
    texts = [c.get("text", "") for c in (res.get("content") or []) if isinstance(c, dict) and c.get("type") == "text"]
    out = "\n".join(texts) if texts else json.dumps(res, ensure_ascii=False)
    LOG.append(f"[{name}] {out[:400]}")
    return out

def find_num(text, key):
    m = re.search(key + r'"?\s*[:=，,]\s*"?(-?\d+)', text)
    return int(m.group(1)) if m else None

def img_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return (1200, 800)

def read_md(parts):
    txt = []
    for p in parts:
        with io.open(p, encoding="utf-8") as f:
            txt.append(f.read())
    return "\n".join(txt).strip() + "\n"

def split_chunks(md):
    """Split markdown into alternating ('text', s) / ('fig', n) segments; text split at paragraph boundaries <=9000 chars."""
    segs = []
    pieces = re.split(r"\[\[FIG(\d+)\]\]", md)
    # pieces: [text, num, text, num, ...]
    for i, piece in enumerate(pieces):
        if i % 2 == 1:
            segs.append(("fig", int(piece)))
        else:
            segs.append(("text", piece))
    chunks = []
    for kind, val in segs:
        if kind == "fig":
            chunks.append(("fig", val))
            continue
        s = val.strip("\n")
        if not s.strip():
            continue
        if len(s) <= 9000:
            chunks.append(("text", s))
        else:
            paras = s.split("\n\n")
            buf = ""
            for p in paras:
                if len(buf) + len(p) + 2 > 9000 and buf:
                    chunks.append(("text", buf))
                    buf = p
                else:
                    buf = (buf + "\n\n" + p) if buf else p
            if buf:
                chunks.append(("text", buf))
    return chunks

def build_doc(md, out_path, fig_map=None):
    fig_map = fig_map or {}
    out = call("create_doc", {})
    m = re.search(r'file_id["\s:=]+([A-Za-z0-9_\-\.]+)', out)
    fid = m.group(1) if m else None
    LOG.append(f"create_doc -> file_id={fid}")
    assert fid, "create_doc failed: " + out[:500]
    # styles (best-effort)
    for name, args in [
        ("doc_set_document_style", {"file_id": fid, "default_text_style": {"font_family": "Times New Roman", "font_size": 11}}),
        ("doc_update_named_style", {"file_id": fid, "named_style_type": "HEADING_1", "text_style": {"font_size": 14, "font_family": "Times New Roman"}}),
        ("doc_update_named_style", {"file_id": fid, "named_style_type": "HEADING_2", "text_style": {"font_size": 12.5, "font_family": "Times New Roman"}}),
        ("doc_update_named_style", {"file_id": fid, "named_style_type": "HEADING_3", "text_style": {"font_size": 11.5, "font_family": "Times New Roman"}}),
    ]:
        try:
            call(name, args)
        except SystemExit:
            LOG.append(f"style call failed (ignored): {name}")
    cur = 0
    n_chunks = 0
    for kind, val in split_chunks(md):
        if kind == "text":
            r = call("doc_insert_markdown", {"file_id": fid, "idx": cur, "markdown": val})
            pos = find_num(r, "position") or find_num(r, "last_edit_index")
            if pos is None:
                LOG.append("WARN no position returned; keep cur")
            else:
                cur = pos
        else:
            fpath = fig_map.get(val)
            if not fpath or not os.path.exists(fpath):
                LOG.append(f"WARN figure {val} missing ({fpath}) - skipped")
                continue
            w0, h0 = img_size(fpath)
            W = 620
            H = max(1, round(W * h0 / w0))
            r = call("doc_insert_image", {"file_id": fid, "idx": cur, "image_path": fpath, "w": W, "h": H})
            pos = find_num(r, "position") or find_num(r, "last_edit_index")
            if pos is not None:
                r2 = call("doc_insert_paragraph", {"file_id": fid, "idx": pos})
                pos2 = find_num(r2, "position") or find_num(r2, "last_edit_index")
                cur = pos2 if pos2 is not None else pos
            else:
                LOG.append(f"WARN no position after image {val}")
        n_chunks += 1
    r = call("save_file", {"file_id": fid, "file_path": out_path})
    LOG.append(f"save_file -> {out_path}: {r[:200]}")
    return fid

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "ms"):
        md = read_md([os.path.join(WS, f"ms{i}.md") for i in range(1, 8)])
        fig_map = {}
        for n in range(1, 11):
            if n in REV_FIG:
                fig_map[n] = REV_FIG[n]
            else:
                for ext in ("png", "jpeg", "jpg", "emf"):
                    c = os.path.join(FIGS, f"orig_fig{n:02d}.{ext}")
                    if os.path.exists(c):
                        fig_map[n] = c
                        break
        build_doc(md, os.path.join(OUT_DIR, "manuscript_major_revision.docx"), fig_map)
    if which in ("all", "letter"):
        md = read_md([os.path.join(WS, "letter1.md"), os.path.join(WS, "letter2.md")])
        build_doc(md, os.path.join(OUT_DIR, "Response_to_Editor_and_Reviewers.docx"), {})
    with io.open(os.path.join(WS, "build_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("BUILD DONE")
