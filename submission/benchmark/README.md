# GRASP — Generalized Rule Acquisition via Structured Programs

程序化"规则宇宙"基准：用**跨阶段增量**测量 AI 的**学习能力**，而非单点正确率。

## 一句话

学习能力 = dL + dF + Gen 的加权和（LQ），其中 dL=B−A 是"从示例中学会多少"、dF=C−B 是"从反馈中改进多少"、Gen=D 是"组合泛化"。

## 设计

- **符号集**：10 个无意义 token `A–J`（零先验、抗预训练污染）。
- **规则宇宙**：7 种原语 `{reverse, shift, repeat, dedup, mirror, swap_halves, drop_ends}` 组成的深度 1–4 管线，确定性、可种子复现。
- **四阶段协议**：A 零样本 → B 少样本 → C 增量微调 → D 组合泛化。
- **评分**：`LQ = 0.3·dL + 0.3·dF + 0.4·Gen`，Phase D 是区分"学会"与"背下"的决定性信号。
- **基线模型**：random / copy / memorizer / induction / oracle 五档，从"不学习"到"完美但零增量"全覆盖。

## 运行

```bash
python generate.py --seed 0 --per-level 10 --out data.json   # 生成 40 个宇宙（4 深度 × 10）
python run.py --data data.json --out results.json            # 跑四阶段 + 基线 + 打分
```

## 结果速览（seed 20260101）

| 模型 | depth 1 LQ | depth 4 LQ | 解读 |
|---|---|---|---|
| random / copy / memorizer | ≈0.00–0.02 | ≈0.00–0.01 | 不学习：无增量 |
| induction | 0.66 | 0.47 | 真学习：depth 1–3 接近满分，depth 4 组合泛化衰减 |
| oracle | 0.40 | 0.40 | 完美但"零增量"：Gen=1 仅贡献 0.4 |

完整数据见 `../2025105400130_C9_测试结果.md` 与 `results.json`（200 行 per-universe 记录）。
