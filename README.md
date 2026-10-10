# C2A-C9：衡量 AGI 的认知能力 — GRASP Benchmark

> 提交身份：2025105400130 · 赛道：Track 1 Learning · 关联论文：Measuring Progress Toward AGI（DeepMind, 2026-03-16）

## 这是什么

本仓库是 C2A 提案 + C9 正式提交的完整交付物：一个名为 **GRASP** 的程序化规则宇宙基准，用**跨阶段增量（LQ）**测量 AI 的**学习能力**，区分"现学"与"背过"。

## 交付物清单

| 文件 | 说明 |
|---|---|
| `2025105400130_C2A_proposal.md` | 提案（约 1300 字，四部分）|
| `2025105400130_C2A_AI日志.md` / `2025105400130_C2A_拿来说明.md` | 提案 AI 日志 + 拿来说明 |
| `benchmark/` | 完整可运行 benchmark（generate/benchmark/run + data + results）|
| `2025105400130_C9_task说明.md` | 评估任务 + 评分标准 |
| `2025105400130_C9_测试结果.md` | 5 档基线测试数据 |
| `2025105400130_C9_反思报告.md` | 反思（500–800 字）|
| `2025105400130_C9_AI日志.md` / `2025105400130_C9_拿来说明.md` | 开发日志 + 拿来说明 |
| `AAR复盘.md` | 七维复盘 |

## 快速复现

```bash
cd benchmark
python generate.py --seed 0 --per-level 10 --out data.json
python run.py --data data.json --out results.json
```

## 核心结果

- 不学习（random/copy/memorizer）LQ ≈ 0
- 真学习（induction）LQ 0.47–0.70，depth 4 组合泛化衰减到 0.47
- 零增量天花板（oracle）LQ 恒 0.40

## 关联

- 论文：Measuring Progress Toward AGI: A Cognitive Framework（Google DeepMind, 2026-03-16）
- Kaggle：Measuring Progress Toward AGI: Cognitive Abilities（$200,000）
