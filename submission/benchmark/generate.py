"""GRASP — Procedural rule-universe generator (deterministic, seedable).

Generates "rule universes": short compositional pipelines of abstract
symbol-sequence transforms. An abstract alphabet + held-out seeds make the
benchmark anti-contamination by construction (no answer can appear in any
pretraining corpus).

Usage:
    python generate.py --seed 0 --per-level 10 --out data.json
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

ALPHABET = list("ABCDEFGHIJ")   # 10 abstract, language-free tokens


# ---------- primitive transforms: str -> str ----------
def _rev(seq):
    return seq[::-1]


def _shift(seq, k=1):
    return "".join(ALPHABET[(ALPHABET.index(c) + k) % len(ALPHABET)] for c in seq)


def _repeat(seq, k=2):
    return "".join(c * k for c in seq)


def _dedup(seq):
    out = ""
    for c in seq:
        if not out or out[-1] != c:
            out += c
    return out


def _mirror(seq):
    return seq + seq[::-1]


def _swap_halves(seq):
    n = len(seq) // 2
    return seq[n:] + seq[:n]


def _drop_ends(seq):
    return seq[1:-1] if len(seq) > 2 else seq


PRIMITIVES = {
    "reverse": _rev,
    "shift": _shift,
    "repeat": _repeat,
    "dedup": _dedup,
    "mirror": _mirror,
    "swap_halves": _swap_halves,
    "drop_ends": _drop_ends,
}


def build_pipeline(rng, depth):
    """Return a random pipeline of `depth` primitives (repetition allowed)."""
    names = list(PRIMITIVES)
    return [rng.choice(names) for _ in range(depth)]


def apply_pipeline(seq, pipeline):
    s = seq
    for name in pipeline:
        s = PRIMITIVES[name](s)
    return s


def gen_sequences(rng, n, minlen=2, maxlen=6):
    return [
        "".join(rng.choice(ALPHABET) for _ in range(rng.randint(minlen, maxlen)))
        for _ in range(n)
    ]


def make_universe(rng, depth, n_demo=5, n_test=20, n_ctest=20, n_gen=20):
    """One rule universe with disjoint held-out sets:
    - demos:          few-shot demonstrations (Phase B input)
    - test:           held-out eval for Phase B
    - c_test:         fresh held-out eval for Phase C (feedback must generalize)
    - generalization: longer sequences, the decisive compositional-transfer set
    """
    pipeline = build_pipeline(rng, depth)
    return {
        "depth": depth,
        "pipeline": pipeline,
        "demos": [(x, apply_pipeline(x, pipeline))
                  for x in gen_sequences(rng, n_demo)],
        "test": [(x, apply_pipeline(x, pipeline))
                 for x in gen_sequences(rng, n_test)],
        "c_test": [(x, apply_pipeline(x, pipeline))
                   for x in gen_sequences(rng, n_ctest)],
        "generalization": [(x, apply_pipeline(x, pipeline))
                           for x in gen_sequences(rng, n_gen, minlen=7, maxlen=9)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--per-level", type=int, default=10)
    ap.add_argument("--out", default="data.json")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    data = {"seed": args.seed, "alphabet": ALPHABET, "universes": []}
    for depth in (1, 2, 3, 4):
        for _ in range(args.per_level):
            data["universes"].append(make_universe(rng, depth))

    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=1))
    n = len(data["universes"])
    print(f"wrote {n} universes (4 levels x {args.per_level}) -> {args.out}")


if __name__ == "__main__":
    main()
