"""GRASP — four-phase learning protocol, baseline models, and metrics.

Measures LEARNING as a DELTA across phases, not a single accuracy:

  Phase A  zero-shot           -> prior / pretrained bias            (A)
  Phase B  few-shot demos      -> rule acquisition from examples     (B)
  Phase C  + error feedback    -> learning from feedback             (C)
                                 [operationalizes KSTAR K->S->T->A->R]
  Phase D  generalization      -> compositional transfer             (D)

Metrics (all in [0,1]):
  dL = B - A    example learning
  dF = C - B    feedback learning
  Gen = D       generalization (the decisive learner-vs-memorizer signal)
  LQ  = 0.3*dL + 0.3*dF + 0.4*Gen   Learning Quotient
"""
from __future__ import annotations

import itertools

from generate import PRIMITIVES, apply_pipeline


def accuracy(preds, golds):
    if not golds:
        return 0.0
    return sum(1 for p, g in zip(preds, golds) if p == g) / len(golds)


class BaseModel:
    name = "base"

    def phase_a(self, inputs):
        raise NotImplementedError

    def phase_b(self, demos, inputs):
        raise NotImplementedError

    def phase_c(self, demos, feedback, inputs):
        raise NotImplementedError

    def phase_d(self, demos, inputs):
        raise NotImplementedError


class RandomModel(BaseModel):
    name = "random"

    def __init__(self, rng):
        self.rng = rng

    def _rand(self, x):
        n = self.rng.randint(1, max(2, len(x) * 2))
        return "".join(self.rng.choice("ABCDEFGHIJ") for _ in range(n))

    def phase_a(self, inputs):
        return [self._rand(x) for x in inputs]

    def phase_b(self, demos, inputs):
        return [self._rand(x) for x in inputs]

    def phase_c(self, demos, feedback, inputs):
        return [self._rand(x) for x in inputs]

    def phase_d(self, demos, inputs):
        return [self._rand(x) for x in inputs]


class CopyModel(BaseModel):
    name = "copy"

    def phase_a(self, inputs):
        return inputs

    def phase_b(self, demos, inputs):
        return inputs

    def phase_c(self, demos, feedback, inputs):
        return inputs

    def phase_d(self, demos, inputs):
        return inputs


class MemorizerModel(BaseModel):
    """Memorizes demo I/O pairs exactly; falls back to copy on unseen input.

    Scores only where an output is recoverable from memory; near-zero on
    compositional generalization (Phase D) — the classic non-learner profile.
    """

    name = "memorizer"

    @staticmethod
    def _memo(demos):
        d = {}
        for x, y in demos:
            d[x] = y
        return d

    def phase_a(self, inputs):
        return list(inputs)

    def _run(self, demos, inputs):
        d = self._memo(demos)
        return [d.get(x, x) for x in inputs]

    def phase_b(self, demos, inputs):
        return self._run(demos, inputs)

    def phase_c(self, demos, feedback, inputs):
        d = self._memo(demos)
        for x, y in feedback:
            d[x] = y
        return [d.get(x, x) for x in inputs]

    def phase_d(self, demos, inputs):
        return self._run(demos, inputs)


class InductionModel(BaseModel):
    """Brute-force program-synthesis learner.

    Given demos, searches the primitive-composition space (bounded depth) for
    the shortest pipeline consistent with all demos, then applies it to unseen
    inputs — a genuine rule inducer in the spirit of ARC's program-induction.
    """

    name = "induction"

    def _search(self, demos, max_depth):
        names = list(PRIMITIVES)
        for d in range(1, max_depth + 1):
            for combo in itertools.product(names, repeat=d):
                if all(apply_pipeline(x, combo) == y for x, y in demos):
                    return combo
        return None

    def _apply(self, demos, inputs, max_depth=3):
        pipe = self._search(demos, max_depth)
        if pipe is None:
            return list(inputs)
        return [apply_pipeline(x, pipe) for x in inputs]

    def phase_a(self, inputs):
        return list(inputs)

    def phase_b(self, demos, inputs):
        return self._apply(demos, inputs)

    def phase_c(self, demos, feedback, inputs):
        return self._apply(demos + feedback, inputs)

    def phase_d(self, demos, inputs):
        return self._apply(demos, inputs, max_depth=4)


class OracleModel(BaseModel):
    """Knows the true pipeline (ceiling / upper bound)."""

    name = "oracle"

    def __init__(self, apply_fn):
        self.apply_fn = apply_fn

    def _run(self, inputs):
        return [self.apply_fn(x) for x in inputs]

    def phase_a(self, inputs):
        return self._run(inputs)

    def phase_b(self, demos, inputs):
        return self._run(inputs)

    def phase_c(self, demos, feedback, inputs):
        return self._run(inputs)

    def phase_d(self, demos, inputs):
        return self._run(inputs)


def run_universe(uni, model):
    demo_x = [x for x, _ in uni["demos"]]
    test_x = [x for x, _ in uni["test"]]
    test_y = [y for _, y in uni["test"]]
    ctest_x = [x for x, _ in uni["c_test"]]
    ctest_y = [y for _, y in uni["c_test"]]
    gen_x = [x for x, _ in uni["generalization"]]
    gen_y = [y for _, y in uni["generalization"]]

    A = accuracy(model.phase_a(test_x), test_y)
    B = accuracy(model.phase_b(uni["demos"], test_x), test_y)

    # Phase C: feed back the model's own B-phase errors (with correct answers),
    # then evaluate on a FRESH held-out set so feedback must generalize.
    b_preds = model.phase_b(uni["demos"], test_x)
    feedback = [(x, y) for x, y, p in zip(test_x, test_y, b_preds) if p != y]
    C = accuracy(model.phase_c(uni["demos"], feedback, ctest_x), ctest_y)

    D = accuracy(model.phase_d(uni["demos"], gen_x), gen_y)

    return {
        "depth": uni["depth"],
        "pipeline": uni["pipeline"],
        "A": A,
        "B": B,
        "C": C,
        "D": D,
        "dL": B - A,
        "dF": C - B,
        "LQ": 0.3 * (B - A) + 0.3 * (C - B) + 0.4 * D,
    }
