"""Shared helpers for the topic-specific charts (run after figures.py). Appends to figures/_captions_py.json and figures/captions.md."""
import json, os, sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C


def load(B):
    M = pd.read_csv(os.path.join(B, "data", "clean", "master.csv"), encoding="utf-8-sig", keep_default_na=False)
    M["year"] = pd.to_numeric(M.year, errors="coerce")
    M["txt"] = (M.title + " . " + M.abstract).str.lower()
    cfg = C.jload(os.path.join(B, "config.json"))
    return M, cfg


def save(fig, B, name, svg=True):
    fig.savefig(os.path.join(B, "figures", name + ".png"), dpi=220, bbox_inches="tight")
    if svg:
        fig.savefig(os.path.join(B, "figures", name + ".svg"), bbox_inches="tight")
    plt.close(fig)


def caption(B, file, title, what, how, caution, tool="Python"):
    fp = os.path.join(B, "figures", "_captions_py.json")
    caps = [c for c in (C.jload(fp, []) or []) if c["file"] != file]
    caps.append(dict(file=file, title=title, what=what, how=how, caution=caution, tool=tool))
    C.jdump(caps, fp, indent=1)
    with open(os.path.join(B, "figures", "captions.md"), "a", encoding="utf-8") as f:
        f.write(f"## {file}\n**{title}** ({tool})\n\n- **Shows:** {what}\n- **Data and settings:** {how}\n- **Caution:** {caution}\n\n")
