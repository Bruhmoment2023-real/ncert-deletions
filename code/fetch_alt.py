"""Fetch one specific alternative capture as the old edition (used when the QA step found the
preferred capture unusable).  Usage: python -I code/fetch_alt.py <book> <capture_ts> <role_label>
Downloads to data/books/<role_label>/<book>/ and logs the attempt in retrieval-log.csv."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import acquire
book, ts, role = sys.argv[1:4]
cdx = acquire.load_cdx()
url = next(u for t, u, s in cdx[book] if t == ts)
folder, info = acquire.download_and_check(book, role, ts, url, 0, acquire.pack_downloads())
if folder is None:
    acquire.log_row(book=book, role=role, capture_ts=ts, url=url, http_note=info["http"], bytes=info["bytes"], verdict=info["verdict"])
    sys.exit("failed")
n, st, pg, low = acquire.scan_pdf_dir(folder)
acquire.log_row(book=book, role=role, capture_ts=ts, url=url, http_note=info["http"], bytes=info["bytes"], sha256=info["sha"],
                n_pdfs=n, print_stamps="; ".join(f"{k} x{v}" for k, v in st.most_common(3)), n_pages_body=pg,
                low_text_share_body=round(low, 3), verdict="fetched_alt", note="alternative to preferred capture (text-layer QA)")
print(book, role, ts, n, st.most_common(2), pg, low)
