# SWE-QA-Bench 测评方法设计文档（mini-swe-agent）

本文档说明 mini-swe-agent 在 SWE-QA-Bench 上的三种测评方法及其实现原理，便于迁移后快速理解。

---

## 1. 方法总览

| 方法 | 入口 | 是否用 LLM | 是否用 Docker | 检索方式 |
|------|------|------------|---------------|----------|
| Bash-only | `python -m minisweagent.run_swe_qa --mode bash` | ✅ | ✅ | 无 |
| Tools | `python -m minisweagent.run_swe_qa --mode tools` | ✅ | ✅ | `code_search` |
| Tools-Radar | `python -m minisweagent.run_swe_qa --mode tools_radar` | ✅ | ✅ | `file_radar_search` |

---

## 2. 输入与输出

**输入**
- `datasets/questions/{repo}.jsonl`
- `datasets/repos/{repo}/`（默认只读挂载到容器 `/repos/<repo>`）

**输出**
- `swe_qa_bench/results/answers/{MODEL}/{METHOD}/{repo}.jsonl`
- 每行输出字段（必须对齐）：

```json
{"question": "...", "answer": "...", "final_answer": "...", "relative_code_list": ["..."]}
```

说明：
- `answer` 与 `final_answer` 值一致（冗余写入）。
- `relative_code_list` 为相对路径列表，保序去重，最多 50 条。

---

## 3. 方法一：Bash-only（miniswe_bash）

**入口**
- Runner：`src/minisweagent/swe_qa_bench/runners/bash_runner.py`
- Prompt：`swe_qa_bench/config/agent_bash.yaml`

**执行流程**
1. Docker 容器默认只读挂载单仓库到 `/repos/<repo>`
2. 模型在容器内执行 bash（rg/cat/sed 等）
3. 输出 `MINI_SWE_AGENT_FINAL_OUTPUT` JSON
4. 写入 answers JSONL

**特点**
- 纯 bash 搜索，无语义检索
- 作为 baseline 方法

---

## 4. 方法二：Tools（miniswe_tools）

**入口**
- Runner：`src/minisweagent/swe_qa_bench/runners/tools_runner.py`
- Prompt：`swe_qa_bench/config/agent_tools.yaml`
- 工具配置：`swe_qa_bench/config/code_search.yaml`

**核心组件**
- `ToolAgent`：拦截 `@tool` 命令
- `ToolRegistry`：工具分发
- `code_search`：宿主机检索（embedding + index）

**执行流程**
1. LLM 在容器内执行 bash
2. 输出 `@tool code_search ...` 时，ToolAgent 拦截并在宿主机运行
3. 工具结果注入上下文，继续 bash 精读
4. 写入 answers JSONL

**关键点**
- 工具结果路径必须相对 repo 根目录
- repos 只读挂载，避免修改评测数据

---

## 5. 方法三：Tools-Radar（miniswe_tools_radar）

**入口**
- Runner：`src/minisweagent/swe_qa_bench/runners/tools_runner.py`
- Prompt：`swe_qa_bench/config/agent_tools_radar_neutral.yaml`
- 工具配置：`swe_qa_bench/config/file_radar_search.yaml`

**核心组件**
- `file_radar_search`：文件级语义召回，不返回代码正文
- `list_symbols`：候选文件骨架浏览
- `ProgressTrackingToolAgent`：在最终提交前强制进行 bash 验证

**执行流程**
1. LLM 先用 `file_radar_search` 召回候选文件
2. 可选用 `list_symbols` 看候选文件骨架
3. 必须用 bash 读取至少一个候选文件
4. 输出 `MINI_SWE_AGENT_FINAL_OUTPUT` JSON
5. 写入 answers JSONL

**约束**
- 当前只支持 `neutral` prompt
- `list_symbols` 不能替代 bash 验证
- 如果调用了 radar 但未读候选文件，提交会被 runner 拦截

## 6. relative_code_list 采集规则

**tools / tools_radar 模式**
- `tool_candidates`：`code_search` 或 `file_radar_search` 返回的路径
- `files_read`：实际读过的文件（cat/sed/head/tail/rg 等）
- `relative_code_list` = 并集（保序去重）

**bash-only 模式**
- `relative_code_list` = `files_read`

**统一约束**
- 最多 50 条，超出则追加 `"<<TRUNCATED>>"`（必须是最后一项）

---

## 7. 输出与日志

- 轨迹/日志：`mini-swe-agent/swe_qa_bench/outputs/<model>/<method>/<timestamp>/`
- 答案输出：`swe_qa_bench/results/answers/<model>/<method>/<repo>.jsonl`

---

## 8. 与 LocBench 的关键差异

- SWE-QA-Bench 不提供 `base_commit`，默认使用仓库 HEAD。
- 输出格式是 QA 文本，不是 `found_files`/`found_entities`。
- 评分采用 LLM-as-judge（五维度评分）。
- `tools_radar` 当前只迁移了 `neutral` 路线，没有迁移 `oracle_sniper`。
