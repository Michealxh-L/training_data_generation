# 智能训练数据生成与处理系统

> 为 Qwen 2.5 系列模型微调自动生成高质量训练数据

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 项目概述

本系统旨在自动化生成和处理训练数据，支持基于本地代码仓的 LLM 模型微调。系统可以：

- 🎯 **场景 1**：自动生成代码问答对，包含完整的推理轨迹
- 🏗️ **场景 2**：根据需求生成架构设计方案，提供详细实现步骤
- 📊 **数据验证**：自动评估数据质量，确保训练效果
- 🔄 **多格式导出**：支持 JSONL、JSON 等多种格式

### 核心特性

- ✅ 自动化代码分析（Python、JavaScript、Java、TypeScript）
- ✅ LLM 驱动的智能问答生成
- ✅ 推理轨迹 (Reasoning Trace) 生成
- ✅ 架构感知的设计方案生成
- ✅ 多维度数据质量评估
- ✅ 支持 OpenAI 和 Anthropic API
- ✅ 数据集自动划分（Train/Val/Test）
- ✅ 开箱即用的微调格式

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd training_data_generation

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
# OPENAI_API_KEY=your_key_here
# 或
# ANTHROPIC_API_KEY=your_key_here
```

### 3. 运行示例

```bash
# 生成示例数据（不调用 API）
python examples/generate_samples.py

# 或使用 demo 脚本
bash examples/demo.sh
```

### 4. 从真实代码仓生成数据

```bash
# 使用公开的 GitHub 仓库
git clone https://github.com/pallets/flask.git repos/flask

# 生成训练数据
python main.py \
  --repo-path repos/flask \
  --scenario both \
  --num-qa 30 \
  --num-design 10
```

---

## 📖 详细文档

### 文档导航

- 📘 [设计文档](docs/DESIGN.md) - 完整的系统设计、数据结构、架构说明
- 📋 [交付总结](docs/SUMMARY.md) - 项目完成情况、评判标准对照
- ⚡ [快速参考](docs/QUICK_REFERENCE.md) - 命令速查、配置说明、常见问题

### 系统架构

系统采用模块化设计，分为以下核心模块：

```
📦 training_data_generation
├── 📁 src/
│   ├── analyzer.py          # 代码仓库分析
│   ├── llm_service.py       # LLM API 服务
│   ├── qa_generator.py      # 问答对生成
│   ├── design_generator.py  # 设计方案生成
│   ├── data_processor.py    # 数据处理与验证
│   └── schema.py            # 数据模型定义
├── 📁 config/               # 配置文件
├── 📁 docs/                 # 详细文档
├── 📁 examples/             # 示例代码
├── 📁 data/                 # 数据输出目录
└── main.py                  # 主程序入口
```

详细设计文档：[docs/DESIGN.md](docs/DESIGN.md)

### 数据格式

#### 场景 1：问答对格式

```json
{
  "id": "uuid",
  "question": "这个函数的主要功能是什么？",
  "answer": "详细的答案...",
  "question_type": "code_explanation",
  "code_contexts": [
    {
      "file_path": "src/module.py",
      "start_line": 10,
      "end_line": 30,
      "code_snippet": "def function_name():\n    ...",
      "language": "python"
    }
  ],
  "reasoning_trace": {
    "steps": [
      {
        "step_number": 1,
        "description": "分析函数签名",
        "code_reference": "def function_name(params)",
        "confidence": 0.9
      }
    ],
    "overall_confidence": 0.87,
    "methodology": "自顶向下分析法"
  },
  "difficulty": "medium",
  "tags": ["authentication", "security"]
}
```

#### 场景 2：设计方案格式

```json
{
  "id": "uuid",
  "requirement": "添加用户认证功能",
  "requirement_type": "new_feature",
  "solution_overview": "采用 JWT 进行无状态认证...",
  "detailed_design": "详细设计说明...",
  "implementation_steps": [
    "1. 安装 PyJWT 库",
    "2. 创建 JWT 工具类",
    "3. 实现认证中间件"
  ],
  "architecture_context": {
    "components": [...],
    "design_patterns": ["Repository Pattern"],
    "tech_stack": {"web_framework": "FastAPI"},
    "architecture_type": "RESTful API"
  },
  "reasoning_trace": { ... },
  "complexity": "medium",
  "estimated_effort": "3-5 天"
}
```

---

## 🎯 使用指南

### 基本用法

```bash
# 生成问答对
python main.py --repo-path /path/to/repo --scenario qa --num-qa 50

# 生成设计方案
python main.py --repo-path /path/to/repo --scenario design --num-design 20

# 同时生成两种数据
python main.py --repo-path /path/to/repo --scenario both --num-qa 30 --num-design 10
```

### 高级配置

编辑 `config/config.yaml` 自定义生成参数：

```yaml
generation:
  samples_per_scenario: 50
  quality_threshold: 0.7
  llm:
    provider: "openai"  # 或 "anthropic"
    model: "gpt-4-turbo-preview"
    temperature: 0.7

scenario1_qa:
  question_types:
    - "code_explanation"
    - "business_logic"
    - "design_pattern"

scenario2_design:
  requirement_types:
    - "new_feature"
    - "refactoring"
    - "integration"
```

### 输出文件

生成的数据保存在 `data/processed/` 目录：

```
data/processed/
├── qa_pairs.jsonl              # Q&A 对（JSONL）
├── qa_pairs.json               # Q&A 对（JSON）
├── design_solutions.jsonl      # 设计方案（JSONL）
├── design_solutions.json       # 设计方案（JSON）
├── finetuning_data.jsonl       # 微调格式数据
├── train.jsonl                 # 训练集
├── validation.jsonl            # 验证集
├── test.jsonl                  # 测试集
└── quality_report.json         # 质量报告
```

---

## 📊 数据质量

### 质量评估维度

| 维度 | 评估标准 | 权重 |
|------|----------|------|
| 问题质量 | 长度、清晰度、相关性 | 20% |
| 答案质量 | 完整性、准确性、详细度 | 30% |
| 代码上下文 | 相关性、完整性 | 20% |
| 推理质量 | 步骤完整性、逻辑性、置信度 | 30% |

### 自动验证

系统自动验证每个样本：

- ✅ 问题长度 ≥ 5 个单词
- ✅ 答案长度 ≥ 20 个单词
- ✅ 至少包含 1 个代码上下文
- ✅ 推理步骤 ≥ 2 步
- ✅ 整体置信度 ≥ 0.5

### 质量报告示例

```json
{
  "qa_pairs": {
    "total": 50,
    "valid": 48,
    "avg_quality_score": 0.856,
    "question_types": {
      "code_explanation": 15,
      "business_logic": 12
    }
  },
  "overall": {
    "total_samples": 70,
    "overall_quality": 0.845
  }
}
```

---

## 🔧 核心功能

### 1. 代码分析

```python
from src.analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer("/path/to/repo")
analyzer.analyze(languages=['python', 'javascript'])

# 获取复杂函数
complex_functions = analyzer.get_functions_by_complexity(min_complexity=3)

# 搜索代码
results = analyzer.search_code("authenticate")
```

### 2. 问答生成

```python
from src.qa_generator import QAGenerator

generator = QAGenerator(analyzer, llm_service)
qa_pairs = generator.generate_qa_pairs(
    num_samples=50,
    question_types=['code_explanation', 'business_logic']
)
```

### 3. 设计方案生成

```python
from src.design_generator import DesignSolutionGenerator

generator = DesignSolutionGenerator(analyzer, llm_service)
solutions = generator.generate_design_solutions(
    num_samples=20,
    requirement_types=['new_feature', 'refactoring']
)
```

### 4. 数据处理

```python
from src.data_processor import DataProcessor, DataValidator

# 验证数据
validator = DataValidator()
report = validator.generate_report(qa_pairs, design_solutions)

# 导出数据
processor = DataProcessor("data/processed")
processor.export_to_jsonl(qa_pairs, "qa_pairs.jsonl")
processor.export_for_finetuning(qa_pairs, design_solutions)
```

---

## 🎓 模型微调

### OpenAI Fine-tuning

```bash
# 准备数据
python main.py --repo-path /path/to/repo --scenario both

# 上传训练文件
openai api fine_tunes.create \
  -t data/processed/finetuning_data.jsonl \
  -m gpt-3.5-turbo

# 查看微调状态
openai api fine_tunes.follow -i <YOUR_FINE_TUNE_ID>
```

### 自定义微调（可选）

如果使用开源模型（如 Qwen）：

```python
# examples/finetune_qwen.py
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer

# 加载数据
dataset = load_dataset('json', data_files={
    'train': 'data/processed/train.jsonl',
    'validation': 'data/processed/validation.jsonl'
})

# 加载模型
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# 微调配置
training_args = TrainingArguments(
    output_dir="./models/qwen-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-5
)

# 开始训练
trainer = Trainer(model=model, args=training_args, train_dataset=dataset['train'])
trainer.train()
```

---

## 📈 性能与成本

### 生成速度

- 单个 Q&A 对：约 5-10 秒（取决于 LLM 响应速度）
- 单个设计方案：约 10-15 秒
- 100 个样本：约 10-15 分钟

### API 成本估算（GPT-4）

- Q&A 对：约 $0.02-0.03 per sample
- 设计方案：约 $0.05-0.08 per sample
- 100 样本总成本：约 $3-5

💡 **成本优化建议**：
- 使用 GPT-3.5 Turbo 降低成本（质量略降）
- 批量生成时使用缓存避免重复
- 对于简单问题使用本地模型

---

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系维护者。

---

## 🎯 项目目标

通过本系统生成的训练数据，期望模型具备：

✅ 深入理解代码的业务逻辑和实现细节  
✅ 提供带推理过程的代码解释  
✅ 基于现有架构生成合理的设计方案  
✅ 考虑实现复杂度和潜在风险  
✅ 成为优秀的代码理解助手和架构设计顾问  

---

**Happy Training! 🚀**