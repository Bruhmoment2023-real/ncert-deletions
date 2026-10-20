"""Polite, sequential downloader for NCERT textbook zips from the Wayback Machine.

Usage:
    python code/fetch_books.py code/pilot_manifest.csv

Manifest columns: book,edition_label,wayback_timestamp
Each file is fetched from
    https://web.archive.org/web/<timestamp>id_/https://ncert.nic.in/textbook/pdf/<book>dd.zip
(the `id_` flag returns the original bytes with no Wayback toolbar), saved to
    data/books/<edition_label>/<book>_<timestamp>.zip
and unpacked to data/books/<edition_label>/<book>/ .
A sha256 for every zip is appended to data/meta/downloads.csv so that anybody
can check they hold the same bytes. The textbooks themselves are NOT to be
redistributed (see 03-design.md, "What may be released").
"""
import csv
import hashlib
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "ncert-diff-research/0.1 (polite; sequential; one request per 5s)"
SLEEP = 5


def fetch(url, dest, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
                final = r.geturl()
                while True:
                    b = r.read(1 << 16)
                    if not b:
                        break
                    f.write(b)
            return final
        except Exception as e:  # noqa
            print("  retry", i + 1, repr(e)[:120], flush=True)
            time.sleep(20 * (i + 1))
    return None


def main(manifest):
    log = ROOT / "data" / "meta" / "downloads.csv"
    new = not log.exists()
    with open(manifest, newline="") as f, open(log, "a", newline="") as lg:
        w = csv.writer(lg)
        if new:
            w.writerow(["book", "edition_label", "requested_ts", "final_url", "bytes", "sha256", "n_files"])
        for row in csv.DictReader(f):
            book, lab, ts = row["book"], row["edition_label"], row["wayback_timestamp"]
            d = ROOT / "data" / "books" / lab
            d.mkdir(parents=True, exist_ok=True)
            z = d / f"{book}_{ts}.zip"
            out = d / book
            if out.exists() and any(out.iterdir()):
                print("have", z.name, flush=True)
                continue
            url = f"https://web.archive.org/web/{ts}id_/https://ncert.nic.in/textbook/pdf/{book}dd.zip"
            print("get", url, flush=True)
            final = fetch(url, z)
            if not final:
                w.writerow([book, lab, ts, "FAILED", 0, "", 0])
                continue
            h = hashlib.sha256(z.read_bytes()).hexdigest()
            n = 0
            try:
                with zipfile.ZipFile(z) as zz:
                    out.mkdir(exist_ok=True)
                    for info in zz.infolist():
                        name = Path(info.filename).name
                        if not name.lower().endswith(".pdf"):
                            continue
                        (out / name).write_bytes(zz.read(info))
                        n += 1
            except zipfile.BadZipFile:
                print("  BAD ZIP", z, flush=True)
            w.writerow([book, lab, ts, final, z.stat().st_size, h, n])
            lg.flush()
            time.sleep(SLEEP)


if __name__ == "__main__":
    main(sys.argv[1])
