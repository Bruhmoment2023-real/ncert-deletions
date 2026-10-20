"""Fetch legal open-access PDFs for chosen records of a paper's master.csv.
Usage: python fetch_pdfs.py <bibliometrics_dir> "<title substring>" ["<title substring>" ...] [--url <title substring>=<direct url> ...]
Tries best_pdf_url, all_pdf_urls, oa_url, s2_pdf_url in turn, accepts only responses that start with %PDF, saves to pdfs/extra/<Author>_<year>_<words>.pdf.
No evasion: a bot challenge, 403 or HTML page is logged and skipped. Log: pdfs/extra/fetch_log.csv"""
import os, sys, re, csv, time
import pandas as pd, requests

B = os.path.abspath(sys.argv[1]); args = sys.argv[2:]
direct = {}
subs = []
i = 0
while i < len(args):
    if args[i] == "--url":
        k, v = args[i + 1].split("=", 1); direct[k] = v; i += 2
    else:
        subs.append(args[i]); i += 1
for k in direct:
    if k not in subs: subs.append(k)
M = pd.read_csv(os.path.join(B, "data", "clean", "master.csv"), keep_default_na=False)
out = os.path.join(B, "pdfs", "extra"); os.makedirs(out, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (research; open-access fetch)"}
log = []
for s in subs:
    rows = M[M.title.str.contains(re.escape(s), case=False, regex=True)]
    if rows.empty:
        log.append((s, "", "no record in master.csv", "")); print("no record:", s); continue
    r = rows.sort_values("cited_by_count", ascending=False, key=lambda c: pd.to_numeric(c, errors="coerce")).iloc[0]
    urls = ([direct[s]] if s in direct else []) + [u for u in [r.best_pdf_url] + str(r.all_pdf_urls).split("|") + [r.oa_url, r.s2_pdf_url] if u]
    fa = re.sub(r"[^A-Za-z]", "", str(r.first_author).split()[-1]) if r.first_author else "anon"
    name = f"{fa}_{r.year}_{re.sub(r'[^A-Za-z0-9]+', '-', r.title)[:50].strip('-')}.pdf"
    ok = False; seen = set()
    for u in urls:
        if u in seen or not u.startswith("http"): continue
        seen.add(u)
        try:
            resp = requests.get(u, headers=UA, timeout=60, allow_redirects=True)
            if resp.status_code == 200 and resp.content[:5] == b"%PDF-":
                open(os.path.join(out, name), "wb").write(resp.content)
                log.append((s, r.oa_id, "downloaded", u)); ok = True; print("OK  ", name, len(resp.content)); break
            log.append((s, r.oa_id, f"not a pdf / HTTP {resp.status_code}", u))
        except Exception as e:
            log.append((s, r.oa_id, f"error {type(e).__name__}", u))
        time.sleep(1.5)
    if not ok: print("FAIL", s)
with open(os.path.join(out, "fetch_log.csv"), "a", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerows(log)
