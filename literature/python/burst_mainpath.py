"""Depth layer 3: Kleinberg burst detection (keywords, cited references) and main-path analysis (SPC) on the in-corpus citation network.
Usage: python burst_mainpath.py <bibliometrics_dir>
Writes: tables/py_burst_keywords.csv, tables/py_burst_references.csv, tables/py_mainpath_*.csv, figures/py_20_burst_keywords.*, py_21_burst_references.*, py_22_main_path.*
and appends captions to figures/captions.md. Skips (and says so in tables/py_burst_mainpath_notes.txt) any method the data cannot support."""
import os, sys, math, re, collections
import numpy as np, pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, r"D:\Research-Publishing\_tools\biblio-kit")
import topic_util as T

B = os.path.abspath(sys.argv[1])
M, cfg = T.load(B)
notes = []
M = M[(M.year >= 1900) & (M.year <= 2026)].copy()
M["year"] = M.year.astype(int)


def kleinberg(r, d, s=2.0, gamma=1.0):
    """Two-state Kleinberg automaton over time slots. r[t] = relevant, d[t] = total. Returns state sequence (0/1)."""
    r = np.asarray(r, float); d = np.asarray(d, float)
    T_ = len(r)
    if r.sum() == 0 or d.sum() == 0:
        return np.zeros(T_, int)
    p0 = r.sum() / d.sum(); p1 = min(s * p0, 0.999)
    def cost(p, t):
        p = min(max(p, 1e-9), 1 - 1e-9)
        return -(r[t] * math.log(p) + (d[t] - r[t]) * math.log(1 - p))
    tau = gamma * math.log(max(T_, 2))
    INF = 1e18
    C = np.full((T_, 2), INF); back = np.zeros((T_, 2), int)
    C[0, 0] = cost(p0, 0); C[0, 1] = tau + cost(p1, 0)
    for t in range(1, T_):
        for j, p in ((0, p0), (1, p1)):
            best, arg = INF, 0
            for i in (0, 1):
                c = C[t - 1, i] + (tau if (j == 1 and i == 0) else 0)
                if c < best:
                    best, arg = c, i
            C[t, j] = best + cost(p, t); back[t, j] = arg
    st = np.zeros(T_, int); st[-1] = int(np.argmin(C[-1]))
    for t in range(T_ - 1, 0, -1):
        st[t - 1] = back[t, st[t]]
    return st


def intervals(years, st, r, d):
    out, i = [], 0
    while i < len(st):
        if st[i] == 1:
            j = i
            while j + 1 < len(st) and st[j + 1] == 1:
                j += 1
            out.append((years[i], years[j], int(sum(r[i:j + 1]))))
            i = j + 1
        else:
            i += 1
    return out


# ---------- 1. keyword bursts ----------
yrs = list(range(int(M.year.min()), int(M.year.max()) + 1))
yrs = [y for y in yrs if y >= max(1970, int(M.year.min()))]
dtot = M.groupby("year").size().reindex(yrs, fill_value=0).values
kw = collections.defaultdict(lambda: collections.Counter())
for _, r in M.iterrows():
    ks = {k.strip().lower() for k in re.split(r"[;|]", str(r.keywords)) if k.strip()}
    if not ks:   # fall back to the OpenAlex topics
        ks = {k.strip().lower() for k in re.split(r"[;|]", str(r.topics)) if k.strip()}
    for k in ks:
        kw[k][r.year] += 1
tot = {k: sum(c.values()) for k, c in kw.items()}
cand = [k for k, v in sorted(tot.items(), key=lambda x: -x[1]) if v >= 4][:80]
rows = []
for k in cand:
    rr = np.array([kw[k].get(y, 0) for y in yrs])
    st = kleinberg(rr, dtot)
    for a, b, n in intervals(yrs, st, rr, dtot):
        # burst weight: excess count over expectation within the interval
        exp = tot[k] / dtot.sum() * sum(dtot[yrs.index(a):yrs.index(b) + 1])
        rows.append(dict(keyword=k, burst_start=a, burst_end=b, records_in_burst=n, total_records=tot[k], excess=round(n - exp, 2)))
KB = pd.DataFrame(rows).sort_values("excess", ascending=False) if rows else pd.DataFrame(columns=["keyword", "burst_start", "burst_end", "records_in_burst", "total_records", "excess"])
KB.to_csv(os.path.join(B, "tables", "py_burst_keywords.csv"), index=False, encoding="utf-8-sig")
if len(KB) >= 3:
    top = KB.head(25).sort_values("burst_start")
    fig, ax = plt.subplots(figsize=(10.5, 0.33 * len(top) + 2.2))
    for i, (_, r) in enumerate(top.iterrows()):
        ax.barh(i, r.burst_end - r.burst_start + 1, left=r.burst_start - 0.5, color="#c0392b", alpha=0.85)
    ax.set_yticks(range(len(top))); ax.set_yticklabels([f"{k} ({t})" for k, t in zip(top.keyword, top.total_records)], fontsize=8)
    ax.set_xlabel("Publication year"); ax.set_ylabel("Keyword or OpenAlex topic (records in corpus)")
    ax.set_title(f"Keyword burst detection (Kleinberg, 2 states, s=2, gamma=1)\nTop {len(top)} bursts by excess count; corpus {len(M)} records ({cfg['paper_id']})", loc="left", fontsize=11, fontweight="bold")
    ax.invert_yaxis(); ax.grid(axis="x", alpha=0.3); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color="#c0392b", alpha=0.85)], labels=["burst interval"], loc="lower right", fontsize=8)
    T.save(fig, B, "py_20_burst_keywords")
    T.caption(B, "py_20_burst_keywords.png", "Keyword burst timeline (Kleinberg)",
              "Years in which a keyword (or OpenAlex topic where a record has no keywords) appears in more corpus records than its overall share predicts.",
              "Kleinberg two-state automaton per keyword, yearly slots, s=2, gamma=1, keywords with at least 4 records (top 80 by frequency); ranked by excess count; table tables/py_burst_keywords.csv. Own Python implementation of the batch version.",
              "Small yearly counts make bursts fragile and the keywords are machine-assigned (OpenAlex), not author-chosen; a burst in the corpus can come from my search terms or snowballing rather than from the field.", tool="Python")
else:
    notes.append("Keyword bursts: fewer than 3 bursts found; figure not drawn.")

# ---------- 2. cited-reference bursts ----------
E = pd.read_csv(os.path.join(B, "data", "clean", "citation_edges.csv"))
CR = pd.read_csv(os.path.join(B, "data", "clean", "cited_references.csv"), keep_default_na=False)
yr = dict(zip(M.oa_id, M.year))
if len(E) >= 30:
    E["cy"] = E.citing.map(yr)
    E = E.dropna(subset=["cy"])
    top = E.groupby("cited").size().sort_values(ascending=False).head(40).index
    rows = []
    for c in top:
        rr = np.array([((E.cited == c) & (E.cy == y)).sum() for y in yrs])
        st = kleinberg(rr, dtot)
        for a, b, n in intervals(yrs, st, rr, dtot):
            rows.append(dict(oa_id=c, burst_start=a, burst_end=b, citing_in_burst=n, total_in_corpus_citations=int(rr.sum())))
    RB = pd.DataFrame(rows)
    if len(RB):
        lab = CR.set_index("oa_id")
        RB["reference"] = [f"{lab.first_author.get(c, '')} {int(float(lab.year.get(c, 0) or 0)) or ''} {str(lab.title.get(c, ''))[:55]}" for c in RB.oa_id]
        RB = RB.sort_values("citing_in_burst", ascending=False)
        RB.to_csv(os.path.join(B, "tables", "py_burst_references.csv"), index=False, encoding="utf-8-sig")
        t = RB.head(25).sort_values("burst_start")
        fig, ax = plt.subplots(figsize=(11, 0.33 * len(t) + 2.2))
        for i, (_, r) in enumerate(t.iterrows()):
            ax.barh(i, r.burst_end - r.burst_start + 1, left=r.burst_start - 0.5, color="#1f6f8b", alpha=0.85)
        ax.set_yticks(range(len(t))); ax.set_yticklabels(t.reference, fontsize=7.5)
        ax.set_xlabel("Year of the citing paper"); ax.set_ylabel("Cited work (first author, year, title)")
        ax.set_title(f"Burst detection on works cited inside the corpus (Kleinberg)\n{len(E)} in-corpus citation links ({cfg['paper_id']})", loc="left", fontsize=11, fontweight="bold")
        ax.invert_yaxis(); ax.grid(axis="x", alpha=0.3); ax.spines[["top", "right"]].set_visible(False)
        T.save(fig, B, "py_21_burst_references")
        T.caption(B, "py_21_burst_references.png", "Reference burst timeline (Kleinberg)",
                  "Years in which a heavily cited corpus paper receives more citations from other corpus papers than its overall share predicts.",
                  "Kleinberg two-state automaton, yearly slots, s=2, gamma=1, on the 40 most cited-within-corpus works; citing years from citation_edges.csv; table tables/py_burst_references.csv.",
                  "Only citations from inside the corpus count, so a burst shows what this map's papers cite, not total citation history; counts per year are small.", tool="Python")
    else:
        notes.append("Reference bursts: none found.")
else:
    notes.append(f"Reference bursts skipped: only {len(E)} in-corpus citation links.")

# ---------- 3. main path (search path count) ----------
if len(E) >= 30:
    meta = M.set_index("oa_id")
    G = nx.DiGraph()
    for c, d in zip(E.citing, E.cited):   # edge cited -> citing = knowledge flow
        if c in yr and d in yr and c != d and yr[d] <= yr[c]:
            G.add_edge(d, c)
    # break cycles (same-year mutual citations) by removing back edges found with DFS
    while True:
        try:
            cyc = nx.find_cycle(G)
        except nx.NetworkXNoCycle:
            break
        G.remove_edge(*cyc[-1])
    if G.number_of_edges() < 20:
        notes.append("Main path skipped: fewer than 20 usable edges.")
    else:
        comp = max(nx.weakly_connected_components(G), key=len)
        H = G.subgraph(comp).copy()
        order = list(nx.topological_sort(H))
        nin = {v: 0 for v in H}; nout = {v: 0 for v in H}
        for v in order:
            nin[v] = 1 if H.in_degree(v) == 0 else sum(nin[u] for u in H.predecessors(v))
        for v in reversed(order):
            nout[v] = 1 if H.out_degree(v) == 0 else sum(nout[w] for w in H.successors(v))
        spc = {(u, v): nin[u] * nout[v] for u, v in H.edges()}
        # global main path: maximise summed SPC
        best = {}; nxt = {}
        for v in reversed(order):
            bv, bw = 0, None
            for w in H.successors(v):
                val = spc[(v, w)] + best[w]
                if val > bv:
                    bv, bw = val, w
            best[v] = bv; nxt[v] = bw
        start = max(H.nodes, key=lambda v: best[v] if H.in_degree(v) == 0 else -1)
        gp = [start]
        while nxt[gp[-1]] is not None:
            gp.append(nxt[gp[-1]])
        # key-route: top 0.5% edges (min 3), extend both ways along max-SPC edges
        ke = sorted(spc, key=spc.get, reverse=True)[:max(3, int(0.005 * len(spc)))]
        kr = set()
        for u, v in ke:
            kr.add(u); kr.add(v)
            x = v
            while H.out_degree(x):
                w = max(H.successors(x), key=lambda w: spc[(x, w)]); kr.add(w); x = w
            x = u
            while H.in_degree(x):
                p = max(H.predecessors(x), key=lambda p: spc[(p, x)]); kr.add(p); x = p
        def tab(nodes, name):
            rows = [dict(oa_id=n, year=yr[n], first_author=meta.first_author.get(n, ""), title=meta.title.get(n, ""), doi=meta.doi.get(n, ""), cited_by=meta.cited_by_count.get(n, "")) for n in sorted(nodes, key=lambda n: yr[n])]
            pd.DataFrame(rows).to_csv(os.path.join(B, "tables", name), index=False, encoding="utf-8-sig")
            return rows
        r1 = tab(gp, "py_mainpath_global.csv"); r2 = tab(kr, "py_mainpath_keyroute.csv")
        # figure: year on x, jitter y; highlight global path
        fig, ax = plt.subplots(figsize=(11.5, 7))
        rng = np.random.default_rng(42)
        ypos = {n: rng.uniform(0, 1) for n in H.nodes}
        for (u, v), w in spc.items():
            ax.plot([yr[u], yr[v]], [ypos[u], ypos[v]], color="#bbbbbb", lw=0.3, alpha=0.5, zorder=1)
        ax.scatter([yr[n] for n in H.nodes], [ypos[n] for n in H.nodes], s=6, c="#999999", zorder=2)
        for a, b in zip(gp[:-1], gp[1:]):
            ax.plot([yr[a], yr[b]], [ypos[a], ypos[b]], color="#c0392b", lw=2.2, zorder=3)
        for i, n in enumerate(gp):
            ax.scatter(yr[n], ypos[n], s=45, c="#c0392b", zorder=4)
            ax.annotate(f"{str(meta.first_author.get(n, '')).split(',')[0][:18]} {yr[n]}", (yr[n], ypos[n]), fontsize=6.5, xytext=(3, 4 if i % 2 else -9), textcoords="offset points", zorder=5)
        ax.set_xlabel("Publication year"); ax.set_ylabel("Vertical position is random (no meaning)")
        ax.set_yticks([])
        ax.set_title(f"Main path through the in-corpus citation network (search path count, global main path in red)\n{H.number_of_nodes()} papers, {H.number_of_edges()} links in the largest component; path has {len(gp)} papers ({cfg['paper_id']})", loc="left", fontsize=10.5, fontweight="bold")
        ax.legend(handles=[plt.Line2D([0], [0], color="#c0392b", lw=2.2), plt.Line2D([0], [0], color="#bbbbbb", lw=1)], labels=["global main path", "other citation links"], loc="upper left", fontsize=8)
        ax.spines[["top", "right", "left"]].set_visible(False)
        T.save(fig, B, "py_22_main_path")
        T.caption(B, "py_22_main_path.png", "Main path of the citation network",
                  "The chain of papers that carries the most citation traffic from earliest to latest work inside the corpus.",
                  f"Search path count weights on the citation DAG (edges oriented cited to citing, same-year cycles broken); global main path maximises total weight; key-route list (top {len(ke)} edges extended both ways, {len(kr)} papers) in tables/py_mainpath_keyroute.csv; papers on the global path in tables/py_mainpath_global.csv.",
                  "Only citations between corpus papers count; the path is sensitive to which papers the search and snowball retrieved, and to the many papers outside the largest component that are left out.", tool="Python/networkx")
else:
    notes.append(f"Main path skipped: only {len(E)} in-corpus citation links (network too sparse).")
open(os.path.join(B, "tables", "py_burst_mainpath_notes.txt"), "w", encoding="utf-8").write("\n".join(notes) or "all three analyses ran")
print("\n".join(notes) or "all ran")
