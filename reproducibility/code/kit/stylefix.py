# -*- coding: utf-8 -*-
"""Apply real heading pStyle to all heading paragraphs via doc_modify_paragraph."""
import sys, os, re, io, json, importlib.util

spec = importlib.util.spec_from_file_location("edsdk", r"D:\Program Files (x86)\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\edsdk.py")
edsdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edsdk)

WS = r"C:\Users\刘东\WorkBuddy\2026-11-10-11-58-48"
OUT_DIR = r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110"
LOG = []

def call(name, args, optional=False):
    try:
        res = edsdk._rpc("tools/call", {"name": name, "arguments": args})
    except SystemExit as e:
        if optional:
            LOG.append(f"[{name}] OPTIONAL-FAIL {str(e)[:100]}")
            return None
        raise RuntimeError(f"{name} system-exited: {e}")
    texts = [c.get("text", "") for c in (res.get("content") or []) if isinstance(c, dict) and c.get("type") == "text"]
    out = "\n".join(texts) if texts else json.dumps(res, ensure_ascii=False)
    if out.startswith("error") or '"ok": false' in out:
        if optional:
            LOG.append(f"[{name}] OPTIONAL-FAIL {out[:120]}")
            return None
        raise RuntimeError(f"{name} failed: {out[:300]}")
    LOG.append(f"[{name}] ok")
    return out

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def headings_from_md(files):
    hs = []
    for fp in files:
        with io.open(fp, encoding="utf-8") as f:
            first = True
            for line in f:
                if first:
                    first = False
                    t = line.strip()
                    if t and not t.startswith("#"):
                        hs.append((11, norm(t)))
                        continue
                m = re.match(r"^(#{1,3})\s+(.+)$", line)
                if m:
                    hs.append((len(m.group(1)), norm(m.group(2))))
    seen, out = set(), []
    for lvl, t in hs:
        if t.lower() in seen:
            continue
        seen.add(t.lower())
        out.append((lvl, t))
    return out

def get_all_nodes(fid):
    import time
    nodes = []
    offset = 0
    retries = 0
    while True:
        try:
            r = call("doc_resolve_document_structure", {"file_id": fid, "mode": "full", "limit": 150, "offset": offset, "text_preview_length": 200})
        except RuntimeError as e:
            retries += 1
            if retries > 5:
                raise
            time.sleep(3)
            continue
        s = r.strip()
        try:
            data = json.loads(s)
        except Exception:
            m = re.search(r"(\[.*\]|\{.*\})", r, re.S)
            data = json.loads(m.group(1))
        batch = data if isinstance(data, list) else (data.get("nodes") or [])
        if not batch:
            break
        nodes.extend(batch)
        if len(batch) < 150:
            break
        offset += 150
    return nodes

def find_fid(path, wait=0):
    import time
    for attempt in range(6):
        pool = call("get_pool_status", {})
        try:
            pdata = json.loads(pool[pool.index("{"):])
            cands = [ed for ed in pdata.get("open_editors", [])
                     if norm(str(ed.get("file_path", ""))) == norm(path) and ed.get("last_saved_ms", -1) != -1]
            if cands:
                cands.sort(key=lambda e: e.get("last_saved_ms", 0), reverse=True)
                return cands[0].get("file_id")
        except Exception:
            pass
        if wait:
            time.sleep(wait)
    return None

def process(path, md_files):
    fid = find_fid(path)
    if not fid:
        call("open_file", {"file_path": path})
        fid = find_fid(path, wait=2)
    if not fid:
        raise RuntimeError(f"no open editor for {path}")
    LOG.append(f"{os.path.basename(path)}: fid={fid}")
    heads = headings_from_md(md_files)
    nodes = get_all_nodes(fid)
    LOG.append(f"{os.path.basename(path)}: {len(nodes)} nodes, {len(heads)} expected headings")
    matched = 0
    idx = 0
    for lvl, text in heads:
        hit = None
        for j in range(idx, len(nodes)):
            t = norm(str(nodes[j].get("text_preview") or ""))
            if t and (t == text or t.startswith(text[:min(len(text), 180)]) or text.startswith(t[:60])):
                hit = (j, nodes[j])
                break
        if not hit:
            LOG.append(f"WARN not found: {text[:70]}")
            continue
        j, nd = hit
        idx = j + 1
        pid = nd.get("paragraph_id")
        b, e = nd.get("start_index"), nd.get("end_index")
        if pid:
            args = {"file_id": fid, "paragraph_id": pid, "heading_lvl": lvl}
        elif isinstance(b, int) and isinstance(e, int):
            args = {"file_id": fid, "ranges": [{"begin": b, "end": e}], "heading_lvl": lvl}
        else:
            LOG.append(f"WARN no id/range for: {text[:70]}")
            continue
        try:
            call("doc_modify_paragraph", args, optional=(lvl == 11))
        except RuntimeError:
            if lvl == 11:
                continue
            # stale id -> re-resolve structure once and retry this heading
            nodes = get_all_nodes(fid)
            idx = 0
            done = False
            for j2 in range(len(nodes)):
                if norm(str(nodes[j2].get("text_preview") or "")) == text:
                    n2 = nodes[j2]
                    p2 = n2.get("paragraph_id")
                    b2, e2 = n2.get("start_index"), n2.get("end_index")
                    if p2:
                        call("doc_modify_paragraph", {"file_id": fid, "paragraph_id": p2, "heading_lvl": lvl})
                        done = True
                    elif isinstance(b2, int) and isinstance(e2, int):
                        call("doc_modify_paragraph", {"file_id": fid, "ranges": [{"begin": b2, "end": e2}], "heading_lvl": lvl})
                        done = True
                    break
            if not done:
                LOG.append(f"WARN retry failed: {text[:70]}")
                matched -= 1
        matched += 1
    call("save_file", {"file_id": fid})
    LOG.append(f"saved {os.path.basename(path)}: styled {matched}/{len(heads)}")
    return matched

if __name__ == "__main__":
    res = []
    res.append(("letter", process(os.path.join(OUT_DIR, "Response_to_Editor_and_Reviewers.docx"),
                                  [os.path.join(WS, "letter1.md"), os.path.join(WS, "letter2.md")])))
    res.append(("ms", process(os.path.join(OUT_DIR, "manuscript_major_revision.docx"),
                              [os.path.join(WS, f"ms{i}.md") for i in range(1, 8)])))
    with io.open(os.path.join(WS, "stylefix_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))
    print("STYLEFIX DONE", res)
