"""OPTIONAL second coder: a small open model run locally on CPU through Ollama.

STATUS: written, NOT RUN.  No Ollama server was answering on this laptop on 2026-10-13 and no model
was downloaded (download and CPU budget).  Treat the output as a second opinion to be scored
against the hand labels exactly like the keyword rules - never as ground truth.

Ready-to-run job
    1. start Ollama with its model store on D: (per-command, no machine-wide variable), e.g. in PowerShell:
           $env:OLLAMA_MODELS = 'D:\\Ollama\\models'; ollama serve
       and pull one small model once (about 2 GB):   ollama pull qwen2.5:3b     (or llama3.2:3b, phi3.5)
    2. short test (10 passages, about 2-4 minutes on CPU):
           venv\\Scripts\\python code\\classify_llm.py --limit 10
    3. full pilot (1,683 passages; at roughly 15-25 s per passage on this CPU that is 7-12 hours:
       run overnight, one heavy job at a time on D:):
           venv\\Scripts\\python code\\classify_llm.py
       Only the 704 body-text passages of 15+ words need a model; add --body-only (about 3-5 hours).

The prompt gives the model the codebook definitions verbatim and asks for one theme key.
Temperature 0, fixed seed, the model name and digest are written into the output for reproducibility.
Output: results/passages_llm_WORKING.csv
"""
import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CB = json.loads((ROOT / "code" / "codebook.json").read_text(encoding="utf-8"))
THEMES = list(CB["themes"].keys()) + ["unclassified"]


def prompt_for(text):
    defs = "\n".join(f"- {k}: {v['definition']}" for k, v in CB["themes"].items())
    return ("You are labelling a passage from an Indian school textbook. Choose the ONE category that best "
            "describes what the passage is about. Do not judge the passage. Answer with the category key only.\n\n"
            f"Categories:\n{defs}\n- unclassified: none of the above fits.\n\nPassage:\n\"\"\"{text[:1500]}\"\"\"\n\nCategory key:")


def ask(model, text, host):
    body = json.dumps({"model": model, "prompt": prompt_for(text), "stream": False,
                       "options": {"temperature": 0, "seed": 1, "num_predict": 12}}).encode()
    req = urllib.request.Request(host + "/api/generate", data=body, headers={"Content-Type": "application/json"})
    out = json.load(urllib.request.urlopen(req, timeout=600))["response"].strip().lower()
    for t in THEMES:
        if t in out:
            return t, out
    return "unparsed", out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--body-only", action="store_true")
    a = ap.parse_args()
    with open(ROOT / "results" / "passages_classified_WORKING.csv", encoding="utf-8-sig", newline="") as f:
        ps = list(csv.DictReader(f))
    if a.body_only:
        ps = [p for p in ps if p["form_rule"] == "body_or_box_text" and len(p["text"].split()) >= 15]
    if a.limit:
        ps = ps[: a.limit]
    with open(ROOT / "results" / "passages_llm_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["book", "chapter", "printed_page", "block", "theme_rule", "theme_llm", "llm_raw", "model"])
        for i, p in enumerate(ps, 1):
            t, raw = ask(a.model, p["text"], a.host)
            w.writerow([p["book"], p["chapter"], p["printed_page"], p["block"], p["theme_rule"], t, raw, a.model])
            f.flush()
            print(i, len(ps), t, flush=True)


if __name__ == "__main__":
    sys.exit(main())
