# AAR（After Action Review）— C2A-C9 衡量 AGI 的认知能力

> 七维复盘：学到了什么 / 过程 / 与 AI 协作 / 完成了什么 / 卡点与突破 / 改进方向 / ΔR 归因。

## 一、学到了什么
- "测学习"与"测正确率"是两件事：静态 benchmark 一个 accuracy 就完事，测学习必须用**跨阶段增量**，否则"背过"和"现学"在分数上无法区分。
- 一个基准的设计，最难的不是代码，而是**隔离目标能力**：abstract token 隔离语言/记忆，差值隔离先验，novelty 隔离刷题，三者缺一不可。
- 拿来主义 = 拿方法骨架 + 升级测量对象，而不是复制数据/代码。

## 二、过程
1. 精读 DeepMind 认知框架 → 锁定 Track 1 Learning 缺口最大；
2. 调研 ARC/ARC-AGI-3/SCAN → 提炼"少样本抽象 + 组合泛化 + 跨时间"三块骨架；
3. 定死 GRASP 设计（四阶段 + LQ + 五基线）→ 一次定死，避免反复改指标；
4. 实现 generate/benchmark/run 三脚本 → 跑出 40 宇宙 × 5 模型基线；
5. 定位 memorizer 偷看真值 bug → 修正后区分度成立；
6. 写 proposal/AI日志/拿来说明/task说明/测试结果/反思/AAR 全套交付物。

## 三、与 AI 的协作
- AI 主导：论文精读、benchmark 调研、代码实现、文档撰写、测试运行。
- 我主导：赛道定夺、设计取舍（LQ 权重、Phase D novelty 强度）、bug 定位、逐条核对数据、提交确认。
- 边界：AI 不拥有 GitHub 凭据、不替我做提交确认；凭据用完需自行 Revoke。

## 四、完成了什么（可验证）
| 产物 | 内容 |
|---|---|
| 提案 | 2025105400130_C2A_proposal.md（约 1300 字，四部分）|
| Benchmark 代码 | benchmark/generate.py + benchmark.py + run.py（纯标准库，可复现）|
| 数据 | data.json（40 宇宙）+ results.json（200 行）|
| 测试结果 | 5 档基线梯度：random/copy/memorizer≈0，induction 0.47–0.70，oracle 0.40 |
| 文档 | C2A/C9 各 3 份 + task说明 + 测试结果 + 反思报告 + 本 AAR |

## 五、卡点与突破
- **卡点 1：基线模型"假聪明"**——memorizer 第一版偷看训练期真值，导致 dL 不为零、与 induction 拉不开。突破：回读代码定位到共享真值，改为"只背示例、D 阶段无真值可偷"，随机/记忆档才落到 ≈0。
- **卡点 2：Phase D 被"蒙混"**——第一版 D 直接复用 A/B/C 管线深度，induction 在 depth 4 不掉分。突破：改为未见过的更深/不同组合，depth 4 衰减（B 0.57/C 0.53）才真实暴露。
- **卡点 3：OCR 失败**——C2A-guide.pdf 是扫描件，文本层为空，ocr_file 又因 venv 冲突报 E_OCR_INSTALL_FAILED。突破：改渲染 PNG 人工判读，确认其内容被 DeepMind 摘要全覆盖，不阻塞方案；如实记录在 AI 日志中。

## 六、改进方向
1. 补人类基线（真人跑 depth 1–4，验证双峰假设）；
2. 扩大宇宙空间（原语 7→更多、深度 4→5）；
3. 接入真实 LLM API 跑前沿模型，补"至少一个前沿模型"的证据；
4. 加 GitHub Actions 自动跑 generate→run 做门禁。

## 七、ΔR 归因
- **"一次定死设计"贡献了最大质量（ΔR 正）**：避免指标反复漂移，四阶段 + LQ 从提案到实现全程一致。
- **"定位 memorizer bug"贡献了正确性（ΔR 正）**：若没回读代码，我会带着"假区分度"提交，基准的科学性就塌了。
- **"OCR/扫描件处理"是负但已知（ΔR 负）**：耗时且最终未提取出文字，靠 DeepMind 摘要兜底；已如实记录，不是遗漏。
