"""Full-corpus acquisition (new for the full-corpus run; the pack's code is untouched).

For every book in 02-availability.csv:
  1. choose, validate and download the RATIONALISED edition (print-year stamp "Rationalised 2023-24")
  2. choose, validate and download the last PRE-RATIONALISATION edition (stamp year <= 2022-23, no
     "Rationalised" text)
from Wayback Machine captures of the NCERT per-book zips (exact capture timestamps from
data/meta/cdx_allzips.txt, taken from the pack).  One request every SLEEP seconds, sequential.
Every attempt (accepted or rejected) is one row of retrieval-log.csv.

Usage: python -I code/acquire.py [book ...]     (no args = all 56 books, resumable)
"""
import csv
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

UA = "ncert-diff-research/0.2 (non-commercial research; polite; sequential; one request per 5 s)"
SLEEP = 5
LOG = ROOT / "retrieval-log.csv"
FIELDS = ["logged_utc", "book", "role", "capture_ts", "url", "http_note", "bytes", "sha256", "n_pdfs",
          "print_stamps", "n_pages_body", "low_text_share_body", "verdict", "note"]
RAT_RE = re.compile(r"rationalised", re.I)
STAMP2 = re.compile(r"^\s*(rationalised[\s-]*)?(reprint[\s-]*)?20\d\d\s*[-–]\s*\d\d(\d\d)?\s*$", re.I)  # also matches "Rationalised-2023-24"
YEAR_RE = re.compile(r"(20\d\d)\s*[-–]\s*(\d\d)")


def load_cdx():
    cd = defaultdict(list)
    for line in open(ROOT / "data" / "meta" / "cdx_allzips.txt"):
        p = line.split()
        if len(p) < 3:
            continue
        book = p[1].rsplit("/", 1)[1][:-6]
        cd[book].append((p[0], p[1], int(p[2])))
    for b in cd:
        cd[b].sort()
    return cd


def pack_downloads():
    """sha256 / final timestamp of files the pilot already fetched, so they can be copied, not re-requested."""
    out = {}
    f = PACK / "data" / "meta" / "downloads.csv"
    for r in csv.DictReader(open(f, newline="", encoding="utf-8")):
        m = re.search(r"/web/(\d{14})id_/", r["final_url"])
        if m and r["sha256"]:
            out[(r["book"], m.group(1))] = r
    return out


def log_row(**kw):
    new = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        row = {k: "" for k in FIELDS}
        row["logged_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        row.update(kw)
        w.writerow(row)


def fetch(url, dest, tries=8):
    """Stream to disk; the archive often cuts large transfers short, so check Content-Length and
    resume with a Range request until the file is complete."""
    total = None
    status = None
    dest = Path(dest)
    if dest.exists():
        dest.unlink()
    for i in range(tries):
        have = dest.stat().st_size if dest.exists() else 0
        try:
            hdr = {"User-Agent": UA}
            if have:
                hdr["Range"] = f"bytes={have}-"
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req, timeout=300) as r:
                status = f"HTTP {r.status}" + (" (resumed)" if have else "") if not status else status
                if total is None:
                    cl = r.headers.get("x-archive-orig-content-length") or r.headers.get("Content-Length")
                    total = int(cl) if cl and cl.isdigit() else None
                    if have == 0 and r.headers.get("Content-Length", "").isdigit():
                        total = int(r.headers["Content-Length"])
                with open(dest, "ab" if have else "wb") as f:
                    while True:
                        b = r.read(1 << 16)
                        if not b:
                            break
                        f.write(b)
        except Exception as e:  # noqa
            msg = repr(e)[:100]
            print("  retry", i + 1, msg, flush=True)
            if "404" in msg:
                return "HTTP 404"
            time.sleep(15 * (i + 1))
        size = dest.stat().st_size if dest.exists() else 0
        if total is None or size >= total:
            return (status or "HTTP 200") + (f" size {size}" if total is None else "")
        time.sleep(SLEEP)
    return None


def scan_pdf_dir(folder: Path):
    """Print-year stamps and text-layer share, scanning every page's text (no images decoded)."""
    import pymupdf
    stamps = Counter()
    n_pages = low = 0
    n_pdfs = 0
    per = []
    for pdf in sorted(folder.glob("*.pdf")):
        n_pdfs += 1
        try:
            doc = pymupdf.open(str(pdf))
        except Exception as e:  # noqa
            per.append((pdf.name, "UNREADABLE " + repr(e)[:60]))
            continue
        body = not nd.is_front_matter(pdf.stem)
        for page in doc:
            t = page.get_text("text")
            for ln in t.splitlines():
                c = nd.clean(ln)
                if STAMP2.match(c):
                    stamps[re.sub(r"\s+", " ", c)] += 1
            if body:
                n_pages += 1
                if len(t.split()) < 40:
                    low += 1
    return n_pdfs, stamps, n_pages, (low / n_pages if n_pages else 1.0)


def stamp_class(stamps):
    """-> ('rationalised'|'reprint'|'old'|'none', years string)"""
    if not stamps:
        return "none", ""
    top = stamps.most_common(1)[0][0]
    if RAT_RE.search(top):
        return "rationalised", top
    if re.match(r"\s*reprint", top, re.I):
        return "reprint", top
    return "old", top


def old_year_ok(top):
    m = YEAR_RE.search(top)
    return bool(m) and int(m.group(1)) <= 2022


def download_and_check(book, role, ts, url, size, pack_dl):
    """Returns (folder, info dict) ; folder is data/books/<role>/<book>/ (replaced per attempt)."""
    base = ROOT / "data" / "books" / role
    base.mkdir(parents=True, exist_ok=True)
    z = base / f"{book}_{ts}.zip"
    out = base / book
    wb = f"https://web.archive.org/web/{ts}id_/{url}"
    note = ""
    if out.exists():
        shutil.rmtree(out)
    pk = pack_dl.get((book, ts))
    fetched = False
    http = ""
    if pk:
        # copy from the pilot's folder instead of asking the archive again; sha256 must match
        for lab in ("old", "rat2023", "latest"):
            cand = PACK / "data" / "books" / lab / f"{book}_{pk['requested_ts']}.zip"
            if cand.exists() and hashlib.sha256(cand.read_bytes()).hexdigest() == pk["sha256"]:
                shutil.copyfile(cand, z)
                http, note = "copied from pack", "copied from pilot download (sha256 matches pack's downloads.csv)"
                break
    if not z.exists():
        time.sleep(SLEEP)
        part = z.with_suffix(".part")
        http = fetch(wb, part)
        fetched = True
        if http is None or not part.exists():
            return None, {"http": http or "FAILED", "bytes": 0, "sha": "", "n": 0, "verdict": "download_failed", "note": note}
        part.replace(z)
    sha = hashlib.sha256(z.read_bytes()).hexdigest() if z.stat().st_size < 400_000_000 else "skipped(big)"
    n = 0
    try:
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(z) as zz:
            for info in zz.infolist():
                name = Path(info.filename).name
                if name.lower().endswith(".pdf"):
                    (out / name).write_bytes(zz.read(info))
                    n += 1
    except zipfile.BadZipFile:
        return None, {"http": http, "bytes": z.stat().st_size, "sha": sha, "n": 0, "verdict": "bad_zip", "note": note}
    return out, {"http": http, "bytes": z.stat().st_size, "sha": sha, "n": n, "note": note, "fetched": fetched}


def acquire_book(book, cdx, pack_dl):
    caps = [c for c in cdx[book]]
    res = {}
    # ---- rationalised edition
    rat_order = [c for c in caps if "20231201" <= c[0] <= "20240101"]
    rat_order += [c for c in caps if "20230101" <= c[0] < "20231201"][::-1]
    rat_order += [c for c in caps if c[0] > "20240101"]
    # ---- pre-rationalisation: latest first, among captures before 2023-06
    old_order = [c for c in caps if c[0] < "20230601"][::-1]
    for role, order in (("rat2023", rat_order), ("old", old_order)):
        accepted = None
        for ts, url, size in order:
            folder, info = download_and_check(book, role, ts, url, size, pack_dl)
            if folder is None:
                log_row(book=book, role=role, capture_ts=ts, url=url, http_note=info["http"], bytes=info["bytes"],
                        sha256=info["sha"], verdict=info["verdict"], note=info["note"])
                continue
            n_pdfs, stamps, n_pages, low = scan_pdf_dir(folder)
            cls, top = stamp_class(stamps)
            verdict, why = "accepted", ""
            if role == "rat2023":
                if cls != "rationalised":
                    verdict, why = "rejected", f"stamp not 'Rationalised' ({cls}: {top or 'none found'})"
                    if cls == "none" and low > 0.5:
                        verdict, why = "needs_ocr", "no text layer; stamp must be read by OCR"
            else:
                rn = res.get("rat_n_pdfs", 0)
                if cls == "rationalised":
                    verdict, why = "rejected", f"already rationalised ({top})"
                elif cls == "reprint":
                    verdict, why = "rejected", f"post-2023 reprint stamp ({top})"
                elif cls == "old" and not old_year_ok(top):
                    verdict, why = "rejected", f"stamp year > 2022-23 ({top})"
                elif n_pdfs < rn - 1:
                    verdict, why = "rejected", f"incomplete: {n_pdfs} PDFs vs {rn} in rationalised edition"
                elif cls == "none" and low > 0.5:
                    verdict, why = "needs_ocr", "no text layer; stamp must be read by OCR"
                elif cls == "none":
                    verdict, why = "rejected", "no stamp found in text layer"
            if verdict == "accepted" and low > 0.5:
                verdict, why = "needs_ocr", f"text layer missing on {low:.0%} of body pages; OCR needed"
            elif verdict == "accepted" and low > 0.25:
                why = f"accepted; {low:.0%} of body pages under 40 words"
            log_row(book=book, role=role, capture_ts=ts, url=url, http_note=info["http"], bytes=info["bytes"],
                    sha256=info["sha"], n_pdfs=n_pdfs, print_stamps="; ".join(f"{k} x{v}" for k, v in stamps.most_common(3)),
                    n_pages_body=n_pages, low_text_share_body=round(low, 3), verdict=verdict,
                    note=(info.get("note", "") + " " + why).strip())
            print(book, role, ts, verdict, top, why, flush=True)
            if verdict in ("accepted", "needs_ocr"):
                accepted = (ts, folder, verdict)
                if role == "rat2023":
                    res["rat_n_pdfs"] = n_pdfs
                break
            shutil.rmtree(folder, ignore_errors=True)
            # keep the rejected zip's bytes only if small; delete big rejected zips to save disk
            zz = ROOT / "data" / "books" / role / f"{book}_{ts}.zip"
            if zz.exists():
                zz.unlink()
        res[role] = accepted
    return res


def main(books):
    cdx = load_cdx()
    pack_dl = pack_downloads()
    state_f = ROOT / "logs" / "acquire_state.json"
    state = json.load(open(state_f)) if state_f.exists() else {}
    avail = [r["ncert_file_code"] for r in csv.DictReader(open(PACK / "02-availability.csv", encoding="utf-8-sig"))]
    for b in (books or avail):
        if state.get(b, {}).get("done"):
            continue
        print("=== ", b, flush=True)
        r = acquire_book(b, cdx, pack_dl)
        state[b] = {"done": True, "rat2023": r.get("rat2023") and [r["rat2023"][0], r["rat2023"][2]],
                    "old": r.get("old") and [r["old"][0], r["old"][2]]}
        json.dump(state, open(state_f, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
