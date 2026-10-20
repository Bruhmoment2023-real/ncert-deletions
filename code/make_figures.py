"""Figures for the pilot. One measure, one hue, one axis; chapters in book order.

Usage: python code/make_figures.py
Reads results/chapter_summary.csv ; writes results/fig1_share_removed_by_chapter.png and
results/fig2_listed_vs_unlisted.png
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INK, MUTED, GRID, BAR, BAR2 = "#1f2328", "#57606a", "#d8dee4", "#2f6fb0", "#9db8d6"

rows = [r for r in csv.DictReader(open(ROOT / "results" / "chapter_summary.csv", encoding="utf-8-sig"))
        if r["new_edition"] == "rat2023" and r["front_or_back_matter"] == "0"]
books = []
for r in rows:
    if r["book"] not in [b for b, _ in books]:
        books.append((r["book"], r["title"]))

fig, axes = plt.subplots(1, len(books), figsize=(15, 4.6), sharex=True)
for ax, (b, title) in zip(axes, books):
    rs = [r for r in rows if r["book"] == b]
    labels = [r["old_chapter_file"][-2:].lstrip("0") for r in rs]
    vals = [100 * float(r["share_removed"]) for r in rs]
    y = range(len(rs))
    ax.barh(list(y), vals, color=BAR, height=0.62)
    for yi, v, r in zip(y, vals, rs):
        if v >= 1:
            inside = v >= 60
            ax.text(v - 2 if inside else v + 2, yi,
                    (f"dropped: {int(r['removed_words']):,} w" if r["chapter_dropped"] == "1" else f"{v:.0f}% ({int(r['removed_words']):,} w)"),
                    va="center", ha="right" if inside else "left", fontsize=7.5, color="white" if inside else INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"Ch. {l}" for l in labels], fontsize=8, color=MUTED)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_title(title.replace("Themes in Indian History", "Themes in Indian\nHistory").replace(" since ", "\nsince ").replace("World ", "World\n"),
                 fontsize=9, color=INK, loc="left")
    ax.xaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, labelsize=8, colors=MUTED)
    ax.set_xlabel("% of chapter's words removed", fontsize=8, color=MUTED)
fig.suptitle("Share of each chapter's words removed between the last pre-rationalisation printing and the 'Rationalised 2023-24' edition (Class 12, English)",
             fontsize=10.5, color=INK, x=0.01, ha="left")
fig.text(0.01, 0.005, "Pilot measurement. Word-level 5-gram test; chapter numbers are those of the old edition. Source: NCERT PDFs via the Wayback Machine.",
         fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.03, 1, 0.94))
fig.savefig(ROOT / "results" / "fig1_share_removed_by_chapter.png", dpi=160, facecolor="white")

# ---- figure 2: removed words by whether NCERT's list covers the page
off = list(csv.DictReader(open(ROOT / "results" / "official_vs_measured.csv", encoding="utf-8-sig")))
fig, ax = plt.subplots(figsize=(8.5, 3.4))
names = [o["title"] for o in off]
a = [int(o["on_pages_listed_2022"]) for o in off]
b = [int(o["on_pages_listed_only_in_revised_booklet"]) for o in off]
c = [int(o["on_unlisted_pages"]) for o in off]
y = list(range(len(off)))
ax.barh(y, a, color=BAR2, height=0.6, label="on pages in the June 2022 list", edgecolor="white", linewidth=1.5)
ax.barh(y, b, left=a, color=BAR, height=0.6, label="on pages added to the list later", edgecolor="white", linewidth=1.5)
ax.barh(y, c, left=[i + j for i, j in zip(a, b)], color="#b3541e", height=0.6, label="on pages in neither list", edgecolor="white", linewidth=1.5)
for yi, (i, j, k) in enumerate(zip(a, b, c)):
    ax.text(i + j + k + 250, yi, f"{j + k:,} words not on the 2022 list" if (i + j + k) else "no change", va="center", fontsize=8, color=INK)
ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=8.5, color=INK)
ax.invert_yaxis()
ax.set_xlim(0, max(i + j + k for i, j, k in zip(a, b, c)) * 1.45)
ax.xaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(length=0, labelsize=8, colors=MUTED)
ax.set_xlabel("words removed (old edition)", fontsize=8, color=MUTED)
ax.legend(frameon=False, fontsize=8, loc="upper right", bbox_to_anchor=(1.0, 1.02))
ax.set_title("Measured removals against NCERT's own list (page-level test, pilot)", fontsize=10.5, color=INK, loc="left")
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig2_listed_vs_unlisted.png", dpi=160, facecolor="white")
print("figures written")
