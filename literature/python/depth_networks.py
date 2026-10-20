"""Depth layer 3: Kleinberg burst detection (keywords and in-corpus cited papers) with a burst timeline figure.
Main-path analysis already comes from figures.py (py_main_path_documents.csv / py_05_main_path); this script only reports its status.

Usage: python depth_networks.py <bibliometrics_dir>
Adds tables/py_bursts_keywords.csv, tables/py_bursts_cited_papers.csv, figures/py_11_bursts_timeline.png|svg and caption entries. Adds, never overwrites.
"""
import os, sys, math
from collections import Counter, defaultdict
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
M = M[M.year.notna()].copy(); M["year"] = M.year.astype(int)
Y0, Y1 = max(1995, int(M.year.min())), int(M.year.max())
years = list(range(Y0, Y1 + 1))


def log_binom(d, r):
    return math.lgamma(d + 1) - math.lgamma(r + 1) - math.lgamma(d - r + 1)


def kleinberg(r, d, s=2.0, gamma=1.0):
    """Two-state Kleinberg burst detection on batched counts r_t of d_t. Returns list of (start_idx, end_idx, weight)."""
    r, d = np.array(r, float), np.array(d, float)
    n = len(r)
    if r.sum() == 0 or d.sum() == 0:
        return []
    p0 = r.sum() / d.sum()
    p1 = min(0.95, s * p0)
    if p0 <= 0 or p0 >= 1 or p1 <= p0:
        return []
    def cost(p):
        return np.array([-(log_binom(d[t], r[t]) + (r[t] * math.log(p) + (d[t] - r[t]) * math.log(1 - p)) if d[t] > 0 else 0) for t in range(n)])
    c0, c1 = cost(p0), cost(p1)
    tau = gamma * math.log(max(n, 2))
    INF = 1e18
    V = np.full((n, 2), INF); back = np.zeros((n, 2), int)
    V[0, 0], V[0, 1] = c0[0], tau + c1[0]
    for t in range(1, n):
        for st, c in ((0, c0), (1, c1)):
            best = None
            for pr in (0, 1):
                v = V[t - 1, pr] + (tau if (st == 1 and pr == 0) else 0)
                if best is None or v < best[0]:
                    best = (v, pr)
            V[t, st] = best[0] + c[t]; back[t, st] = best[1]
    st = int(np.argmin(V[-1])); seq = [st]
    for t in range(n - 1, 0, -1):
        st = back[t, st]; seq.append(st)
    seq = seq[::-1]
    out, i = [], 0
    while i < n:
        if seq[i] == 1:
            j = i
            while j + 1 < n and seq[j + 1] == 1:
                j += 1
            out.append((i, j, float((c0[i:j + 1] - c1[i:j + 1]).sum())))
            i = j + 1
        else:
            i += 1
    return [o for o in out if o[2] > 1.0]


dpy = M.groupby("year").size().reindex(years, fill_value=0).values
# ---- keywords
kwc = defaultdict(lambda: np.zeros(len(years)))
for yr, kws in zip(M.year, M.keywords):
    if yr < Y0:
        continue
    for k in set(x.strip().lower() for x in str(kws).replace("|", ";").split(";") if x.strip()):
        kwc[k][yr - Y0] += 1
tot = {k: v.sum() for k, v in kwc.items()}
cand = [k for k, v in sorted(tot.items(), key=lambda kv: -kv[1]) if v >= 8][:150]
rows = []
for k in cand:
    for i, j, w in kleinberg(kwc[k], dpy):
        rows.append(dict(kind="keyword", term=k, start=years[i], end=years[j], weight=round(w, 2), total_records=int(tot[k])))
kb = pd.DataFrame(rows).sort_values("weight", ascending=False) if rows else pd.DataFrame(columns=["kind", "term", "start", "end", "weight", "total_records"])
kb.to_csv(os.path.join(B, "tables", "py_bursts_keywords.csv"), index=False, encoding="utf-8-sig")
# ---- cited papers (burst in the number of corpus papers citing them, by citing year)
E = pd.read_csv(os.path.join(B, "data", "clean", "citation_edges.csv"))
yr_of = dict(zip(M.oa_id, M.year))
E["cy"] = E.citing.map(yr_of)
E = E[E.cy.notna() & (E.cy >= Y0)]
dE = E.groupby("cy").size().reindex(years, fill_value=0).values   # edges per citing year = citing 'mass'
dfc = E.groupby(["cited", E.cy.astype(int)]).size().unstack(fill_value=0).reindex(columns=years, fill_value=0)
dfc = dfc[dfc.sum(axis=1) >= 8]
ttl = dict(zip(M.oa_id, M.title)); au = dict(zip(M.oa_id, M.first_author)); yo = dict(zip(M.oa_id, M.year))
cr = pd.read_csv(os.path.join(B, "data", "clean", "cited_references.csv"))
for _, x in cr.iterrows():
    ttl.setdefault(x.oa_id, x.title); au.setdefault(x.oa_id, x.first_author); yo.setdefault(x.oa_id, x.year)
rows = []
# per-year citing documents with reference links is the right denominator for 'share of citations going to X'
for oid, ser in dfc.iterrows():
    for i, j, w in kleinberg(ser.values, np.maximum(dE, ser.values)):
        rows.append(dict(kind="cited paper", term=f"{str(au.get(oid, ''))} ({int(float(yo.get(oid, 0) or 0))}) {str(ttl.get(oid, ''))[:70]}", oa_id=oid, start=years[i], end=years[j], weight=round(w, 2), total_records=int(ser.sum())))
cb = pd.DataFrame(rows).sort_values("weight", ascending=False) if rows else pd.DataFrame(columns=["kind", "term", "oa_id", "start", "end", "weight", "total_records"])
cb.to_csv(os.path.join(B, "tables", "py_bursts_cited_papers.csv"), index=False, encoding="utf-8-sig")

# ---- figure
fig, axs = plt.subplots(1, 2, figsize=(16, 8))
for ax, df, ttl_, col in ((axs[0], kb, "Keyword bursts", "#e76f51"), (axs[1], cb, "Cited-paper bursts (corpus papers citing them)", "#457b9d")):
    top = df.head(18).sort_values("start", ascending=False)
    if len(top) == 0:
        ax.text(0.5, 0.5, "no burst detected", ha="center"); ax.set_axis_off(); continue
    for y, r in enumerate(top.itertuples()):
        ax.plot([Y0, Y1 + 1], [y, y], color="#dddddd", lw=3, solid_capstyle="butt")
        ax.plot([r.start, r.end + 1], [y, y], color=col, lw=6, solid_capstyle="butt")
    ax.set_yticks(range(len(top))); ax.set_yticklabels([t[:48] for t in top.term], fontsize=8)
    ax.set_xlim(Y0, Y1 + 1); ax.set_xlabel("Publication year"); ax.set_title(ttl_ + f" (top {len(top)} by weight)", loc="left", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle(f"Burst timeline (Kleinberg, 2 states, s=2, gamma=1) - {cfg['paper_id']}, {len(M)} records", x=0.01, ha="left", fontweight="bold")
T.save(fig, B, "py_11_bursts_timeline")
T.caption(B, "py_11_bursts_timeline.png", "Burst timeline: keywords and cited papers",
          f"Years in which a keyword (left) or a cited paper (right) was used or cited unusually often relative to the corpus that year; coloured bar = burst interval. {len(kb)} keyword bursts and {len(cb)} cited-paper bursts found in total; tables/py_bursts_keywords.csv and py_bursts_cited_papers.csv list all.",
          "Kleinberg's two-state automaton, batched counts per publication year, base rate = overall share, burst state = 2x the base rate, transition cost gamma*ln(n_years) with gamma=1; keywords seen in >=8 records (top 150 by frequency); cited papers cited >=8 times inside the corpus; years from " + f"{Y0}.",
          "Bursts depend on the corpus build (my search terms and snowball), so a burst can reflect how the literature was sampled; the last 1-2 years are incompletely indexed and citation bursts for them are unreliable.")
print(len(kb), "keyword bursts;", len(cb), "cited-paper bursts")
