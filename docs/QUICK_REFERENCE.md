# 快速参考指南

## 🚀 5分钟快速体验

### 1. 查看示例数据（无需安装）
```bash
cd training_data_generation
python examples/generate_samples_standalone.py
```

查看生成的示例文件：
- `examples/sample_outputs/sample_qa_pair.json` - 问答对示例
- `examples/sample_outputs/sample_design_solution.json` - 设计方案示例
- `examples/sample_outputs/combined_sample.json` - 组合示例

---

## 📚 关键文档

| 文档 | 说明 | 链接 |
|------|------|------|
| README | 使用指南、快速开始 | [README.md](../README.md) |
| 设计文档 | 详细的系统设计、数据结构 | [DESIGN.md](DESIGN.md) |
| 交付总结 | 项目完成情况、评判标准对照 | [SUMMARY.md](SUMMARY.md) |

---

## 🎯 核心功能速查

### 场景 1：问答对生成

**数据结构：**
```json
{
  "question": "问题文本",
  "answer": "答案文本",
  "code_contexts": [{代码上下文}],
  "reasoning_trace": {
    "steps": [{推理步骤}],
    "overall_confidence": 0.91,
    "methodology": "推理方法"
  }
}
```

**问题类型：**
- `code_explanation` - 代码解释
- `business_logic` - 业务逻辑
- `design_pattern` - 设计模式
- `error_handling` - 错误处理
- `performance_optimization` - 性能优化

### 场景 2：设计方案生成

**数据结构：**
```json
{
  "requirement": "需求描述",
  "solution_overview": "方案概述",
  "detailed_design": "详细设计",
  "implementation_steps": ["步骤1", "步骤2"],
  "architecture_context": {架构信息},
  "reasoning_trace": {推理轨迹}
}
```

**需求类型：**
- `new_feature` - 新功能
- `refactoring` - 重构
- `integration` - 集成
- `optimization` - 优化

---

## 💻 命令速查

### 基本命令

```bash
# 生成问答对
python main.py --repo-path /path/to/repo --scenario qa --num-qa 50

# 生成设计方案
python main.py --repo-path /path/to/repo --scenario design --num-design 20

# 同时生成
python main.py --repo-path /path/to/repo --scenario both --num-qa 30 --num-design 10
```

### 高级选项

```bash
python main.py \
  --repo-path /path/to/repo \
  --scenario both \
  --num-qa 50 \
  --num-design 20 \
  --config config/config.yaml \
  --output-dir data/my_output
```

---

## 📂 输出文件说明

| 文件 | 说明 | 格式 |
|------|------|------|
| `qa_pairs.jsonl` | 问答对（每行一个JSON） | JSONL |
| `qa_pairs.json` | 问答对（数组格式） | JSON |
| `design_solutions.jsonl` | 设计方案 | JSONL |
| `design_solutions.json` | 设计方案 | JSON |
| `finetuning_data.jsonl` | 微调格式数据 | JSONL |
| `train.jsonl` | 训练集（80%） | JSONL |
| `validation.jsonl` | 验证集（10%） | JSONL |
| `test.jsonl` | 测试集（10%） | JSONL |
| `quality_report.json` | 质量报告 | JSON |

---

## ⚙️ 配置说明

### 环境变量（.env）

```bash
# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# 或 Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 配置文件（config/config.yaml）

```yaml
generation:
  samples_per_scenario: 50
  quality_threshold: 0.7
  llm:
    provider: "openai"
    model: "gpt-4-turbo-preview"
    temperature: 0.7
    max_tokens: 2048
```

---

## 🔧 常见问题

### Q: 如何降低 API 成本？
**A:** 
1. 使用 GPT-3.5 Turbo：`OPENAI_MODEL=gpt-3.5-turbo`
2. 减少样本数量：`--num-qa 20 --num-design 5`
3. 使用本地模型（需要额外配置）

### Q: 如何提高数据质量？
**A:** 
1. 提高质量阈值：`quality_threshold: 0.8`
2. 使用更强大的模型：`gpt-4-turbo-preview`
3. 增加推理步骤要求

### Q: 支持哪些编程语言？
**A:** 
- 完整支持：Python
- 基础支持：JavaScript, TypeScript, Java
- 可扩展：通过添加新的解析器支持更多语言

### Q: 生成速度慢怎么办？
**A:** 
1. 并行处理（目前未实现，可扩展）
2. 使用更快的模型
3. 减少样本数量
4. 使用缓存避免重复生成

---

## 📊 质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 平均质量分 | ≥ 0.8 | 综合质量评分 |
| 有效样本率 | ≥ 90% | 通过验证的比例 |
| 推理完整性 | ≥ 3 步 | 平均推理步骤数 |
| 代码覆盖率 | ≥ 70% | 代码文件覆盖比例 |
| 整体置信度 | ≥ 0.85 | 推理置信度 |

---

## 🎓 微调流程

### 1. 准备数据
```bash
python main.py --repo-path /path/to/repo --scenario both --num-qa 100 --num-design 30
```

### 2. OpenAI 微调
```bash
openai api fine_tunes.create \
  -t data/processed/finetuning_data.jsonl \
  -m gpt-3.5-turbo
```

### 3. 自定义模型微调（Qwen）
```python
from transformers import AutoModelForCausalLM, Trainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
trainer = Trainer(model=model, train_dataset=dataset['train'])
trainer.train()
```

---

## 📈 性能参考

| 操作 | 时间 | 成本 (GPT-4) |
|------|------|--------------|
| 单个Q&A | 5-10秒 | $0.02-0.03 |
| 单个设计方案 | 10-15秒 | $0.05-0.08 |
| 100样本 | 10-15分钟 | $3-5 |
| 1000样本 | 2-3小时 | $30-50 |

---

## 🔗 相关资源

- [Qwen 模型](https://github.com/QwenLM/Qwen)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com)
- [Pydantic 文档](https://docs.pydantic.dev)

---

## 📞 支持

遇到问题？
1. 查看 [README.md](../README.md)
2. 查看 [DESIGN.md](DESIGN.md)
3. 提交 Issue

---

**最后更新：** 2025-12-18
