# 训练数据生成系统设计文档

## 一、项目概述

### 1.1 背景与目标

本系统旨在为基于 Qwen 2.5 系列模型的微调提供高质量的训练数据，使模型具备以下能力：
- 理解和回答关于本地代码仓的业务流程和规则
- 基于代码仓架构生成合理的设计方案

### 1.2 核心功能

1. **场景 1**：自动化生成代码相关的问答对，包含原文代码段和详细的推理过程
2. **场景 2**：根据需求生成基于现有架构的设计方案，提供实现步骤和推理轨迹
3. 数据质量验证和统计分析
4. 多种格式导出（JSONL、JSON）和数据集划分

---

## 二、系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     输入层                                   │
│  - 本地代码仓库                                              │
│  - 配置文件 (config.yaml)                                    │
│  - API密钥 (.env)                                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  代码分析层                                  │
│  ┌───────────────────────────────────────────────┐          │
│  │  Repository Analyzer                          │          │
│  │  - 代码文件扫描                                │          │
│  │  - AST 解析 (Python/JS/Java)                  │          │
│  │  - 函数/类提取                                 │          │
│  │  - 复杂度计算                                  │          │
│  │  - 架构模式识别                                │          │
│  │  - 技术栈检测                                  │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  数据生成层                                  │
│  ┌──────────────────────┐  ┌──────────────────────────┐    │
│  │  QA Generator        │  │  Design Generator        │    │
│  │  (场景 1)            │  │  (场景 2)                │    │
│  │                      │  │                          │    │
│  │  - 选择代码片段      │  │  - 生成需求              │    │
│  │  - 生成问题          │  │  - 架构分析              │    │
│  │  - 生成答案          │  │  - 设计方案              │    │
│  │  - 推理轨迹          │  │  - 实现步骤              │    │
│  └──────────┬───────────┘  └───────────┬──────────────┘    │
│             │                          │                    │
│             └──────────┬───────────────┘                    │
│                        │                                    │
│              ┌─────────▼──────────┐                         │
│              │   LLM Service      │                         │
│              │  - OpenAI GPT-4    │                         │
│              │  - Anthropic Claude│                         │
│              └────────────────────┘                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  数据处理层                                  │
│  ┌───────────────────────────────────────────────┐          │
│  │  Data Validator                               │          │
│  │  - 数据质量评分                                │          │
│  │  - 完整性检查                                  │          │
│  │  - 一致性验证                                  │          │
│  └───────────────────────────────────────────────┘          │
│  ┌───────────────────────────────────────────────┐          │
│  │  Data Processor                               │          │
│  │  - 格式转换 (JSONL/JSON)                       │          │
│  │  - 数据集划分 (Train/Val/Test)                 │          │
│  │  - 微调格式导出                                │          │
│  └───────────────────────────────────────────────┘          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     输出层                                   │
│  - 训练数据文件 (JSONL/JSON)                                │
│  - 质量报告 (JSON)                                           │
│  - 统计信息                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块

#### 2.2.1 代码分析模块 (analyzer.py)

**功能**：
- 扫描代码仓库并解析代码结构
- 提取函数、类、方法等代码元素
- 计算代码复杂度
- 识别设计模式和技术栈

**关键类**：
```python
class RepositoryAnalyzer:
    - analyze()                    # 执行完整分析
    - _scan_files()                # 扫描文件
    - _analyze_python_file()       # 分析 Python 文件
    - _identify_patterns()         # 识别设计模式
    - _identify_tech_stack()       # 识别技术栈
    - get_functions_by_complexity() # 获取复杂函数
    - search_code()                # 代码搜索
```

#### 2.2.2 LLM 服务模块 (llm_service.py)

**功能**：
- 与 LLM API 交互
- 生成问答对
- 生成设计方案
- 错误重试机制

**支持的 LLM**：
- OpenAI GPT-4
- Anthropic Claude

#### 2.2.3 问答生成模块 (qa_generator.py)

**功能**：
- 根据代码生成问答对
- 生成推理轨迹
- 确保问题多样性

**问题类型**：
- `code_explanation`: 代码解释
- `business_logic`: 业务逻辑
- `design_pattern`: 设计模式
- `error_handling`: 错误处理
- `performance_optimization`: 性能优化

#### 2.2.4 设计方案生成模块 (design_generator.py)

**功能**：
- 生成设计需求
- 分析架构上下文
- 生成设计方案和实现步骤

**需求类型**：
- `new_feature`: 新功能
- `refactoring`: 重构
- `integration`: 集成
- `optimization`: 优化

#### 2.2.5 数据处理模块 (data_processor.py)

**功能**：
- 数据质量验证
- 格式转换和导出
- 数据集划分
- 统计报告生成

---

## 三、训练集结构设计

### 3.1 场景 1：问答对 (QAPair)

#### 3.1.1 数据结构

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
      "code_snippet": "def function_name():\\n    ...",
      "language": "python"
    }
  ],
  
  "reasoning_trace": {
    "steps": [
      {
        "step_number": 1,
        "description": "首先分析函数签名和参数",
        "code_reference": "def function_name(param1, param2)",
        "confidence": 0.9
      },
      {
        "step_number": 2,
        "description": "检查函数体中的主要逻辑",
        "code_reference": "for item in items: ...",
        "confidence": 0.85
      }
    ],
    "overall_confidence": 0.87,
    "methodology": "自顶向下分析法：先理解函数签名，再分析实现细节"
  },
  
  "difficulty": "medium",
  "tags": ["authentication", "security", "jwt"],
  "created_at": "2025-12-18T10:00:00"
}
```

#### 3.1.2 字段说明

| 字段 | 类型 | 说明 | 重要性 |
|------|------|------|--------|
| `id` | string | 唯一标识符 | 必需 |
| `question` | string | 问题文本 | 必需 |
| `answer` | string | 答案文本 | 必需 |
| `question_type` | enum | 问题类型 | 必需 |
| `code_contexts` | array | 相关代码上下文（可多个） | 必需 |
| `reasoning_trace` | object | 推理轨迹 | 必需 |
| `difficulty` | enum | 难度级别 (easy/medium/hard) | 可选 |
| `tags` | array | 标签 | 可选 |

#### 3.1.3 推理轨迹结构

推理轨迹 (`reasoning_trace`) 是训练数据的**核心创新点**，它记录了从问题到答案的思考过程：

```json
{
  "steps": [
    {
      "step_number": 1,
      "description": "第一步：识别函数的输入参数",
      "code_reference": "def authenticate(username, password)",
      "confidence": 0.95
    },
    {
      "step_number": 2,
      "description": "第二步：分析主要业务逻辑",
      "code_reference": "user = db.query(User).filter_by(username=username).first()",
      "confidence": 0.90
    }
  ],
  "overall_confidence": 0.92,
  "methodology": "代码流程追踪法"
}
```

**推理轨迹的作用**：
1. **可解释性**：让模型学会解释推理过程
2. **可验证性**：每步都有代码引用，可追溯
3. **置信度评估**：提供每步的可信度分数

### 3.2 场景 2：设计方案 (DesignSolution)

#### 3.2.1 数据结构

```json
{
  "id": "uuid",
  "requirement": "添加用户认证功能，支持 JWT token",
  "requirement_type": "new_feature",
  
  "solution_overview": "采用 JWT 进行无状态认证，使用中间件拦截请求...",
  "detailed_design": "详细设计说明...",
  "implementation_steps": [
    "1. 安装 PyJWT 库",
    "2. 创建 JWT 工具类",
    "3. 实现认证中间件",
    "4. 添加登录/登出接口"
  ],
  
  "architecture_context": {
    "components": [
      {
        "name": "AuthService",
        "type": "service",
        "description": "认证服务",
        "file_path": "src/services/auth.py",
        "dependencies": ["UserRepository", "JWTUtil"]
      }
    ],
    "design_patterns": ["Repository Pattern", "Middleware Pattern"],
    "tech_stack": {
      "web_framework": "FastAPI",
      "database": "PostgreSQL"
    },
    "architecture_type": "RESTful API"
  },
  
  "affected_components": ["AuthService", "UserController", "Middleware"],
  
  "code_examples": [
    {
      "file_path": "src/auth/jwt_util.py",
      "start_line": 1,
      "end_line": 20,
      "code_snippet": "class JWTUtil:\\n    ...",
      "language": "python"
    }
  ],
  
  "reasoning_trace": {
    "steps": [
      {
        "step_number": 1,
        "description": "分析现有架构，发现使用 FastAPI 框架",
        "code_reference": "from fastapi import FastAPI",
        "confidence": 0.95
      },
      {
        "step_number": 2,
        "description": "选择 JWT 作为认证方案，因为系统是 RESTful API",
        "code_reference": null,
        "confidence": 0.90
      }
    ],
    "overall_confidence": 0.88,
    "methodology": "架构分析 -> 方案选型 -> 实现设计"
  },
  
  "complexity": "medium",
  "estimated_effort": "3-5 天",
  "risks": [
    "需要考虑 token 刷新机制",
    "需要实现权限控制"
  ],
  "tags": ["authentication", "security", "jwt"],
  "created_at": "2025-12-18T10:00:00"
}
```

#### 3.2.2 字段说明

| 字段 | 类型 | 说明 | 重要性 |
|------|------|------|--------|
| `requirement` | string | 设计需求 | 必需 |
| `requirement_type` | enum | 需求类型 | 必需 |
| `solution_overview` | string | 方案概述 | 必需 |
| `detailed_design` | string | 详细设计 | 必需 |
| `implementation_steps` | array | 实现步骤 | 必需 |
| `architecture_context` | object | 架构上下文 | 必需 |
| `affected_components` | array | 受影响的组件 | 必需 |
| `code_examples` | array | 代码示例 | 必需 |
| `reasoning_trace` | object | 推理轨迹 | 必需 |
| `complexity` | enum | 复杂度 | 可选 |
| `estimated_effort` | string | 工作量估算 | 可选 |
| `risks` | array | 风险点 | 可选 |

### 3.3 数据集元数据

为确保数据集的可追溯性和可重现性，每个数据集包含以下元数据：

```json
{
  "dataset_version": "1.0.0",
  "created_at": "2025-12-18T10:00:00",
  "repository": {
    "path": "/path/to/repo",
    "commit_hash": "abc123",
    "total_files": 150,
    "total_lines": 50000,
    "languages": ["python", "javascript"]
  },
  "generation_config": {
    "llm_provider": "openai",
    "llm_model": "gpt-4-turbo-preview",
    "temperature": 0.7
  },
  "statistics": {
    "total_samples": 100,
    "qa_pairs": 70,
    "design_solutions": 30,
    "avg_quality_score": 0.85
  }
}
```

---

## 四、数据生成策略

### 4.1 多样性保证

#### 4.1.1 问题多样性

1. **类型多样性**：覆盖 5 种问题类型
2. **难度多样性**：简单、中等、困难
3. **代码覆盖**：从不同文件、不同模块选择代码
4. **去重机制**：检测相似问题（词汇重叠 > 80%）

#### 4.1.2 代码选择策略

```python
# 优先选择复杂度 >= 2 的函数
candidates = analyzer.get_functions_by_complexity(min_complexity=2)

# 选择有文档字符串的类
candidates = analyzer.get_classes_with_docstrings()

# 选择不同目录的代码
directory_distribution = balance_by_directory(code_files)
```

### 4.2 代表性保证

#### 4.2.1 业务逻辑覆盖

- 核心业务流程（如认证、授权、数据处理）
- 错误处理和边界情况
- 性能优化和资源管理
- 设计模式应用

#### 4.2.2 架构覆盖

- 不同层次的组件（服务层、数据层、API 层）
- 组件间的依赖关系
- 技术栈的关键部分

### 4.3 质量控制

#### 4.3.1 自动验证规则

```python
# Q&A 对验证
- 问题长度 >= 5 个单词
- 答案长度 >= 20 个单词
- 至少包含 1 个代码上下文
- 推理步骤 >= 2 步
- 整体置信度 >= 0.5

# 设计方案验证
- 需求描述 >= 5 个单词
- 详细设计 >= 50 个单词
- 实现步骤 >= 3 步
- 推理步骤 >= 3 步
```

#### 4.3.2 质量评分

```python
质量分数 = 0.2 * 问题质量分
          + 0.3 * 答案质量分
          + 0.2 * 代码上下文分
          + 0.3 * 推理质量分

# 推理质量分 = 步骤完整性 * 0.5 + 置信度 * 0.5
```

---

## 五、系统特性

### 5.1 可扩展性

#### 5.1.1 支持新语言

```python
# 在 analyzer.py 中添加新的解析器
def _analyze_java_file(self, code_file: CodeFile):
    # 实现 Java AST 解析
    pass
```

#### 5.1.2 支持新问题类型

```python
# 在 schema.py 中扩展枚举
class QuestionType(str, Enum):
    CODE_EXPLANATION = "code_explanation"
    # ... 现有类型
    NEW_TYPE = "new_type"  # 添加新类型
```

#### 5.1.3 支持新 LLM

```python
# 在 llm_service.py 中添加新的 provider
if self.provider == "new_provider":
    self.client = NewProviderClient(api_key=...)
```

### 5.2 可配置性

所有关键参数可通过 `config/config.yaml` 配置：

```yaml
generation:
  samples_per_scenario: 50    # 每个场景的样本数
  quality_threshold: 0.7      # 质量阈值
  llm:
    provider: "openai"
    model: "gpt-4-turbo-preview"
    temperature: 0.7
```

### 5.3 可维护性

- **模块化设计**：每个功能模块独立
- **类型提示**：使用 Pydantic 进行类型验证
- **错误处理**：完善的异常捕获和重试机制
- **日志记录**：详细的进度和错误日志

---

## 六、使用流程

### 6.1 环境准备

```bash
# 1. 克隆项目
git clone <repository>
cd training_data_generation

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥
```

### 6.2 生成数据

```bash
# 生成两种场景的数据
python main.py \
  --repo-path /path/to/your/repo \
  --scenario both \
  --num-qa 50 \
  --num-design 20

# 只生成问答对
python main.py \
  --repo-path /path/to/your/repo \
  --scenario qa \
  --num-qa 100

# 只生成设计方案
python main.py \
  --repo-path /path/to/your/repo \
  --scenario design \
  --num-design 30
```

### 6.3 输出文件

```
data/processed/
├── qa_pairs.jsonl              # Q&A 对（JSONL 格式）
├── qa_pairs.json               # Q&A 对（JSON 格式）
├── design_solutions.jsonl      # 设计方案（JSONL 格式）
├── design_solutions.json       # 设计方案（JSON 格式）
├── finetuning_data.jsonl       # 微调格式数据
├── train.jsonl                 # 训练集
├── validation.jsonl            # 验证集
├── test.jsonl                  # 测试集
└── quality_report.json         # 质量报告
```

---

## 七、数据格式示例

### 7.1 微调格式 (OpenAI Fine-tuning)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert software engineer helping with code understanding and design."
    },
    {
      "role": "user",
      "content": "Question Type: code_explanation\n\nCode Context:\nFile: src/auth.py (Lines 10-30)\n```python\ndef authenticate(username, password):\n    ...\n```\n\nQuestion: 这个函数的认证流程是什么？"
    },
    {
      "role": "assistant",
      "content": "Answer: 这个函数实现了用户认证...\n\nReasoning Process:\n1. 首先验证用户名格式\n2. 查询数据库获取用户信息\n3. 验证密码哈希\n4. 生成认证 token"
    }
  ]
}
```

### 7.2 质量报告示例

```json
{
  "qa_pairs": {
    "total": 50,
    "valid": 48,
    "invalid": 2,
    "avg_quality_score": 0.856,
    "question_types": {
      "code_explanation": 15,
      "business_logic": 12,
      "design_pattern": 10,
      "error_handling": 8,
      "performance_optimization": 5
    },
    "languages": {
      "python": 45,
      "javascript": 5
    }
  },
  "design_solutions": {
    "total": 20,
    "valid": 19,
    "invalid": 1,
    "avg_quality_score": 0.823,
    "requirement_types": {
      "new_feature": 8,
      "refactoring": 6,
      "integration": 4,
      "optimization": 2
    },
    "complexity": {
      "low": 5,
      "medium": 10,
      "high": 5
    }
  },
  "overall": {
    "total_samples": 70,
    "overall_quality": 0.845
  }
}
```

---

## 八、创新点

### 8.1 推理轨迹 (Reasoning Trace)

**创新描述**：
- 每个问答和设计方案都包含详细的推理步骤
- 每步都有代码引用和置信度分数
- 记录推理方法论

**优势**：
1. 提升模型的可解释性
2. 训练模型的推理能力，而不仅是记忆
3. 支持思维链 (Chain-of-Thought) 训练

### 8.2 多上下文学习

**创新描述**：
- 每个问答可以关联多个代码上下文
- 不同文件间的关联关系
- 架构层面的上下文信息

**优势**：
1. 训练模型理解代码间的依赖关系
2. 支持跨文件的代码理解
3. 更贴近真实的代码理解场景

### 8.3 架构感知设计

**创新描述**：
- 自动识别代码仓的架构类型
- 检测设计模式和技术栈
- 生成符合现有架构的设计方案

**优势**：
1. 确保设计方案的可行性
2. 保持设计一致性
3. 降低实现难度

### 8.4 质量驱动生成

**创新描述**：
- 自动质量评分和验证
- 多维度的质量指标
- 低质量数据过滤

**优势**：
1. 保证训练数据质量
2. 减少噪声数据
3. 提升模型性能

---

## 九、局限性与未来改进

### 9.1 当前局限性

1. **语言支持**：目前主要支持 Python，其他语言的 AST 解析不够完善
2. **复杂度计算**：使用简化的复杂度指标，可以引入更准确的工具（如 Radon）
3. **推理轨迹生成**：依赖 LLM 生成，质量取决于 prompt 设计
4. **成本**：使用 GPT-4 生成数据成本较高

### 9.2 改进方向

1. **多语言增强**：
   - 集成 tree-sitter 支持更多语言
   - 为 Java、TypeScript 等添加专门的解析器

2. **推理质量提升**：
   - 设计更好的 prompt 模板
   - 引入思维链 few-shot 示例
   - 使用更强大的模型（GPT-4 Turbo）

3. **成本优化**：
   - 使用本地模型（如 Llama 2）进行初步生成
   - 使用 GPT-3.5 生成，GPT-4 验证
   - 实现缓存机制避免重复生成

4. **质量提升**：
   - 引入人工审核流程
   - 实现主动学习选择最有价值的样本
   - 添加数据增强技术

5. **功能扩展**：
   - 支持增量生成（基于代码变更）
   - 添加多语言问答支持（中英文）
   - 实现自动化测试生成

---

## 十、评估指标

### 10.1 数据质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 平均质量分 | ≥ 0.8 | 综合质量评分 |
| 有效样本率 | ≥ 90% | 通过验证的样本比例 |
| 推理完整性 | ≥ 3 步 | 平均推理步骤数 |
| 代码覆盖率 | ≥ 70% | 代码文件覆盖比例 |

### 10.2 多样性指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 问题类型分布 | 均衡 | 各类型问题数量差异 < 30% |
| 难度分布 | 均衡 | 简单:中等:困难 = 3:5:2 |
| 代码来源分布 | 分散 | 不同目录的样本分布 |

### 10.3 模型效果指标（微调后）

| 指标 | 评估方法 | 说明 |
|------|----------|------|
| 代码理解准确率 | 人工评估 | 答案的正确性 |
| 推理逻辑性 | 人工评估 | 推理步骤的合理性 |
| 设计方案可行性 | 专家评审 | 设计方案的实用性 |
| 响应相关性 | ROUGE/BLEU | 与参考答案的相似度 |

---

## 十一、总结

本系统提供了一个**完整、可扩展、质量可控**的训练数据生成解决方案，具有以下特点：

✅ **自动化程度高**：从代码分析到数据生成全自动化  
✅ **数据质量优**：多重验证机制确保高质量数据  
✅ **创新性强**：推理轨迹、多上下文、架构感知等创新设计  
✅ **可扩展性好**：支持新语言、新类型、新 LLM  
✅ **实用性强**：直接可用于模型微调，格式兼容主流平台  

通过本系统生成的训练数据，可以有效训练模型：
1. 理解代码的业务逻辑和实现细节
2. 提供带推理过程的代码解释
3. 基于现有架构生成合理的设计方案
4. 考虑实现复杂度和潜在风险

这些能力将使模型成为优秀的**代码理解助手**和**架构设计顾问**。
