"""Run GRASP over generated universes with baseline models; report metrics.

Usage:
    python generate.py --seed 0 --per-level 10 --out data.json
    python run.py --data data.json --out results.json
"""
from __future__ import annotations

import argparse
import json
import random

from generate import apply_pipeline
from benchmark import (CopyModel, InductionModel, MemorizerModel, OracleModel,
                       RandomModel, run_universe)

MODEL_ORDER = ["random", "copy", "memorizer", "induction", "oracle"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data.json")
    ap.add_argument("--out", default="results.json")
    args = ap.parse_args()

    data = json.load(open(args.data))
    rng = random.Random(20260101)

    base_models = [RandomModel(rng), CopyModel(), MemorizerModel(),
                   InductionModel()]

    rows = []
    for uni in data["universes"]:
        oracle = OracleModel(lambda s, p=uni["pipeline"]: apply_pipeline(s, p))
        for m in base_models + [oracle]:
            r = run_universe(uni, m)
            r["model"] = m.name
            rows.append(r)

    with open(args.out, "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    hdr = (f"{'model':<10} {'depth':<6} {'A':>6} {'B':>6} {'C':>6} {'D':>6} "
           f"{'dL':>6} {'dF':>6} {'LQ':>6}")
    print(hdr)
    print("-" * len(hdr))
    for name in MODEL_ORDER:
        for depth in (1, 2, 3, 4):
            sel = [r for r in rows if r["model"] == name and r["depth"] == depth]
            if not sel:
                continue
            n = len(sel)
            mean = lambda k: sum(r[k] for r in sel) / n
            print(f"{name:<10} {depth:<6} {mean('A'):>6.2f} {mean('B'):>6.2f} "
                  f"{mean('C'):>6.2f} {mean('D'):>6.2f} {mean('dL'):>6.2f} "
                  f"{mean('dF'):>6.2f} {mean('LQ'):>6.2f}")
    print(f"\nwrote {len(rows)} per-universe rows -> {args.out}")


if __name__ == "__main__":
    main()
