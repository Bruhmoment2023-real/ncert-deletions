"""leps2 (Politics in India since Independence): the zip captured Oct 2021 still held the 2020-21
printing; the pilot fetched the 2021-22 chapter PDFs one by one (see pack data/meta/downloads.csv).
This copies those files (sha256 checked) to data/books/old2122/leps2 and logs them."""
import csv, hashlib, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import acquire
dst = ROOT / "data" / "books" / "old2122" / "leps2"
dst.mkdir(parents=True, exist_ok=True)
for r in csv.DictReader(open(PACK / "data/meta/downloads.csv", newline="", encoding="utf-8")):
    if r["edition_label"] != "old2122":
        continue
    name = r["book"].split("/")[1]
    src = PACK / "data/books/old2122/leps2" / name
    ok = hashlib.sha256(src.read_bytes()).hexdigest() == r["sha256"]
    shutil.copyfile(src, dst / name)
    acquire.log_row(book="leps2", role="old2122", capture_ts=r["requested_ts"], url=f"per-chapter capture of ncert.nic.in/textbook/pdf/{name} (see pack downloads.csv)",
                    http_note="copied from pack", bytes=src.stat().st_size, sha256=r["sha256"], verdict="accepted" if ok else "SHA MISMATCH",
                    note="2021-22 chapter PDF; leps2ps.pdf is the 2020-21 prelims (pack note)")
n, st, pg, low = acquire.scan_pdf_dir(dst)
print(n, st, pg, low)
