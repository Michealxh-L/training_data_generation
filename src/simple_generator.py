"""训练数据生成器"""
import os
import json
import random
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class SimpleGenerator:
    """简化版训练数据生成器"""
    
    def __init__(
        self,
        project_path: str,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.3
    ):
        self.project_path = Path(project_path)
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = model
        self.temperature = temperature
        
        # 导入依赖
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.llm = genai.GenerativeModel(model)
                self.llm_available = True
            else:
                self.llm = None
                self.llm_available = False
                print("⚠️  未找到API密钥，将使用模拟模式")
        except ImportError:
            self.llm = None
            self.llm_available = False
            print("⚠️  未安装google-generativeai，将使用模拟模式")
        
        # 导入上下文分析器
        try:
            from src.context_analyzer import ProjectContextAnalyzer
            self.analyzer = ProjectContextAnalyzer(str(project_path))
            self.context_enabled = True
        except ImportError:
            self.analyzer = None
            self.context_enabled = False
            print("⚠️  上下文分析器未启用")
    
    def discover_python_files(self) -> List[Path]:
        """发现项目中的Python文件"""
        files = []
        for py_file in self.project_path.rglob('*.py'):
            if all(x not in str(py_file) for x in ['__pycache__', '.venv', 'test', '.git']):
                files.append(py_file)
        return files[:20]
    
    def extract_code_snippet(self, file_path: Path, length: int = 800) -> str:
        """提取代码片段"""
        try:
            content = file_path.read_text(encoding='utf-8')
            if len(content) <= length:
                return content
            max_start = len(content) - length
            start = random.randint(0, max_start)
            return content[start:start + length]
        except:
            return ""
    
    def _calculate_qa_quality_score(self, qa_data: Dict) -> float:
        """计算问答对的质量评分
        
        评分标准：
        - 问题质量 (0-0.25): 长度、具体性
        - 答案质量 (0-0.35): 详细程度、深度
        - 推理步骤 (0-0.25): 步骤数量和质量
        - 代码上下文 (0-0.15): 是否包含相关代码
        """
        score = 0.0
        
        # 问题质量
        question = qa_data.get('question', '')
        q_words = len(question.split())
        score += min(0.25, (q_words / 20) * 0.25)  # 20词为标准
        
        # 答案质量
        answer = qa_data.get('answer', '')
        a_words = len(answer.split())
        score += min(0.35, (a_words / 100) * 0.35)  # 100词为标准
        
        # 推理步骤
        reasoning = qa_data.get('reasoning_steps', [])
        if reasoning:
            num_steps = len(reasoning)
            score += min(0.25, (num_steps / 5) * 0.25)  # 5步为标准
        
        # 代码上下文
        if qa_data.get('code_context'):
            score += 0.15
        
        return min(1.0, round(score, 3))
    
    def _calculate_design_quality_score(self, design_data: Dict) -> float:
        """计算设计方案的质量评分
        
        评分标准：
        - 方案概述 (0-0.20): 清晰度和完整性
        - 实施步骤 (0-0.30): 步骤数量和详细度
        - 文件修改 (0-0.25): 具体性和合理性
        - 挑战分析 (0-0.25): 风险识别和应对
        """
        score = 0.0
        
        # 方案概述
        solution = design_data.get('solution', '')
        s_words = len(solution.split())
        score += min(0.20, (s_words / 50) * 0.20)
        
        # 实施步骤
        steps = design_data.get('implementation_steps', [])
        if steps:
            num_steps = len(steps)
            score += min(0.30, (num_steps / 7) * 0.30)
        
        # 文件修改
        files = design_data.get('files_to_modify', [])
        if files:
            score += min(0.25, (len(files) / 5) * 0.25)
        
        # 挑战分析
        challenges = design_data.get('challenges', [])
        if challenges:
            score += min(0.25, (len(challenges) / 3) * 0.25)
        
        return min(1.0, round(score, 3))
    
    def generate_qa_pair(self, code_snippet: str, file_path: str, use_context: bool = True, context_level: str = 'standard') -> Optional[Dict]:
        """生成单个问答对
        
        Args:
            code_snippet: 代码片段
            file_path: 文件路径
            use_context: 是否使用上下文
            context_level: 上下文级别 ('minimal', 'standard', 'full')
        """
        # 定义问题层次映射
        question_focus = {
            'minimal': {
                'level': '代码实现层',
                'topics': '算法逻辑、数据结构、API使用、代码细节',
                'examples': '函数实现原理、变量命名规范、异常处理方式、代码优化建议'
            },
            'standard': {
                'level': '模块设计层',
                'topics': '设计模式、模块交互、职责划分、组件协作',
                'examples': '模块间依赖关系、接口设计合理性、设计模式应用、代码重构建议'
            },
            'full': {
                'level': '系统架构层',
                'topics': '技术选型、扩展性设计、性能优化、安全考量',
                'examples': '整体架构设计、技术栈选择、可扩展性分析、系统级优化策略'
            }
        }
        
        focus = question_focus.get(context_level, question_focus['standard'])
        
        prompt = ""
        if use_context and self.context_enabled:
            context = self.analyzer.build_context(code_snippet, file_path, context_level=context_level)
            prompt += f"{context}\n"
            prompt += f"【上下文级别】{context_level.capitalize()}（{focus['level']}）\n\n"
        
        prompt += f"""
请基于以下代码和上下文信息生成一个技术问答对。

【代码】
```python
{code_snippet}
```

【问题层次要求】
根据上下文级别生成对应层次的问题：
- Minimal级别（代码实现层）：{question_focus['minimal']['topics']}
  示例：{question_focus['minimal']['examples']}
  
- Standard级别（模块设计层）：{question_focus['standard']['topics']}
  示例：{question_focus['standard']['examples']}
  
- Full级别（系统架构层）：{question_focus['full']['topics']}
  示例：{question_focus['full']['examples']}

当前要求：生成【{focus['level']}】的问题，聚焦于{focus['topics']}

【内容要求】
1. 问题要具体且有深度，严格匹配指定的问题层次
2. 答案要详细准确，包含相应层次的技术分析
3. 推理步骤要清晰，展示从上下文到结论的分析过程

【输出格式】（请严格遵循）
Question: <你的问题>

Answer: <详细答案>

Reasoning Steps:
1. <推理步骤1>
2. <推理步骤2>
3. <推理步骤3>
"""
        
        # 调用LLM
        if self.llm_available:
            try:
                response = self.llm.generate_content(prompt)
                text = response.text
            except Exception as e:
                print(f"❌ LLM调用失败: {e}")
                return None
        else:
            # 模拟模式
            text = self._generate_mock_response(code_snippet, file_path, context_level)
        
        # 解析响应
        parsed = self._parse_qa_response(text)
        if parsed:
            # 添加元数据
            parsed['code_context'] = code_snippet
            parsed['source_file'] = file_path
            parsed['metadata'] = {
                'model': self.model,
                'temperature': self.temperature,
                'timestamp': datetime.now().isoformat(),
                'context_enabled': use_context and self.context_enabled,
                'context_level': context_level,
                'question_layer': {
                    'minimal': '代码实现层',
                    'standard': '模块设计层',
                    'full': '系统架构层'
                }.get(context_level, '未知')
            }
            # 计算质量评分
            parsed['quality_score'] = self._calculate_qa_quality_score(parsed)
        
        return parsed
    
    def generate_design_solution(self, requirement: str, use_context: bool = True) -> Optional[Dict]:
        """生成设计方案"""
        prompt = ""
        if use_context and self.context_enabled:
            structure = self.analyzer.analyze_project_structure()
            prompt += f"""
## 项目信息
- 项目名称: {structure['project_name']}
- 文件数量: {structure['total_files']}
- 核心模块: {', '.join(structure['core_modules'][:5])}

"""
        
        prompt += f"""
请为以下需求生成一个详细的设计方案。

【需求】
{requirement}

【要求】
1. 解决方案要结合项目现有架构
2. 实施步骤要清晰具体
3. 列出需要修改的文件和原因
4. 分析可能遇到的挑战

【输出格式】
Requirement: {requirement}

Solution: <解决方案概述>

Implementation Steps:
1. <步骤1>
2. <步骤2>
3. <步骤3>

Files to Modify:
- file1.py: <修改原因>
- file2.py: <修改原因>

Challenges:
- <挑战1>
- <挑战2>
"""
        
        # 调用LLM
        if self.llm_available:
            try:
                response = self.llm.generate_content(prompt)
                text = response.text
            except Exception as e:
                print(f"❌ LLM调用失败: {e}")
                return None
        else:
            # 模拟模式
            text = self._generate_mock_design_response(requirement)
        
        # 解析响应
        parsed = self._parse_design_response(text, requirement)
        if parsed:
            parsed['metadata'] = {
                'model': self.model,
                'temperature': self.temperature,
                'timestamp': datetime.now().isoformat()
            }
            # 计算质量评分
            parsed['quality_score'] = self._calculate_design_quality_score(parsed)
        
        return parsed
    
    def generate_batch(self, num_qa: int = 5, num_design: int = 3, use_context: bool = True, context_level: str = 'standard') -> Dict:
        """批量生成训练数据"""
        print("="*70)
        print("🚀 开始生成训练数据")
        print("="*70)
        
        dataset = {
            'qa_pairs': [],
            'design_solutions': [],
            'metadata': {
                'project': str(self.project_path),
                'generation_time': datetime.now().isoformat(),
                'model': self.model,
                'context_enabled': use_context and self.context_enabled
            }
        }
        
        # 发现文件
        print("\n📁 发现Python文件...")
        files = self.discover_python_files()
        print(f"   找到 {len(files)} 个文件")
        
        # 生成问答对
        if num_qa > 0:
            level_name = {
                'minimal': '代码实现层',
                'standard': '模块设计层',
                'full': '系统架构层'
            }.get(context_level, context_level)
            print(f"\n📝 生成 {num_qa} 个问答对（{level_name}）...")
            for i in range(num_qa):
                file = random.choice(files)
                rel_path = file.relative_to(self.project_path)
                code = self.extract_code_snippet(file)
                
                print(f"   [{i+1}/{num_qa}] 处理文件: {rel_path}")
                
                qa = self.generate_qa_pair(code, str(rel_path), use_context, context_level)
                if qa:
                    dataset['qa_pairs'].append(qa)
                    print(f"       ✅ 成功（{level_name}）")
                else:
                    print(f"       ❌ 失败")
        
        # 生成设计方案
        if num_design > 0:
            print(f"\n🏗️  生成 {num_design} 个设计方案...")
            
            # 动态生成多样化需求
            requirements = self._generate_diverse_requirements(num_design, files)
            
            for i, req in enumerate(requirements[:num_design]):
                print(f"   [{i+1}/{num_design}] 需求: {req[:50]}...")
                
                design = self.generate_design_solution(req, use_context)
                if design:
                    dataset['design_solutions'].append(design)
                    print(f"       ✅ 成功")
                else:
                    print(f"       ❌ 失败")
        
        # 统计
        print("\n" + "="*70)
        print("📊 生成完成")
        print("="*70)
        print(f"   问答对: {len(dataset['qa_pairs'])}/{num_qa}")
        print(f"   设计方案: {len(dataset['design_solutions'])}/{num_design}")
        print(f"   成功率: {((len(dataset['qa_pairs']) + len(dataset['design_solutions'])) / (num_qa + num_design) * 100):.1f}%")
        
        return dataset
    
    def save_dataset(self, dataset: Dict, output_path: str):
        """
        保存数据集
        
        Args:
            dataset: 数据集
            output_path: 输出路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存: {output_file}")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")
    
    def _generate_diverse_requirements(self, num_requirements: int, files: List[Path]) -> List[str]:
        """基于项目上下文动态生成多样化需求"""
        templates = [
            "为{module}添加{feature}功能",
            "优化{module}的{aspect}性能",
            "重构{module}以支持{capability}",
            "在{module}中实现{pattern}设计模式",
            "为{module}添加{quality}保障机制",
            "扩展{module}以支持{scenario}场景",
            "改进{module}的{attribute}体验",
            "集成{technology}到{module}中"
        ]
        
        features = ["批量处理", "异步处理", "缓存", "数据验证", "错误处理", "监控告警", "配置管理", "插件系统"]
        aspects = ["查询效率", "内存使用", "响应时间", "并发能力", "扩展性", "可维护性"]
        capabilities = ["多租户", "国际化", "版本控制", "热更新", "灰度发布", "降级熔断"]
        patterns = ["工厂模式", "策略模式", "观察者模式", "责任链模式", "装饰器模式", "适配器模式"]
        qualities = ["单元测试", "集成测试", "日志记录", "性能监控", "安全审计", "容错恢复"]
        scenarios = ["高并发", "大数据量", "弱网环境", "跨平台", "微服务", "边缘计算"]
        attributes = ["用户", "开发者", "运维", "安全", "性能"]
        technologies = ["Redis", "Kafka", "Elasticsearch", "GraphQL", "gRPC", "Docker"]
        
        modules = list(set([f.stem for f in files[:10]]))
        if not modules:
            modules = ["核心模块", "数据层", "服务层", "API层"]
        
        requirements = []
        used_combinations = set()
        
        for _ in range(num_requirements * 3):
            template = random.choice(templates)
            module = random.choice(modules)
            
            req = template.format(
                module=module,
                feature=random.choice(features),
                aspect=random.choice(aspects),
                capability=random.choice(capabilities),
                pattern=random.choice(patterns),
                quality=random.choice(qualities),
                scenario=random.choice(scenarios),
                attribute=random.choice(attributes),
                technology=random.choice(technologies)
            )
            
            if req not in used_combinations:
                requirements.append(req)
                used_combinations.add(req)
                if len(requirements) >= num_requirements:
                    break
        
        return requirements if requirements else [
            "优化系统架构，提升整体性能和可扩展性",
            "实现完整的错误处理和日志记录机制",
            "添加自动化测试框架，提高代码质量"
        ]
    
    def _parse_qa_response(self, text: str) -> Optional[Dict]:
        """解析问答响应"""
        try:
            question_match = re.search(r'Question:\s*(.+?)(?=\n\nAnswer:|\nAnswer:)', text, re.DOTALL)
            answer_match = re.search(r'Answer:\s*(.+?)(?=\n\nReasoning|$)', text, re.DOTALL)
            reasoning_match = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)', text, re.DOTALL)
            if question_match and answer_match:
                return {
                    'question': question_match.group(1).strip(),
                    'answer': answer_match.group(1).strip(),
                    'reasoning_steps': [r.strip() for r in reasoning_match] if reasoning_match else []
                }
        except:
            pass
        return None
    
    def _parse_design_response(self, text: str, requirement: str) -> Optional[Dict]:
        """解析设计方案响应"""
        try:
            solution_match = re.search(r'Solution:\s*(.+?)(?=\n\nImplementation|\nImplementation)', text, re.DOTALL)
            steps_match = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)', text, re.DOTALL)
            files_match = re.findall(r'-\s*([^:]+):\s*(.+?)(?=\n-|\n\n|$)', text, re.DOTALL)
            challenges_match = re.findall(r'-\s*(.+?)(?=\n-|\n\n|$)', text.split('Challenges:')[-1] if 'Challenges:' in text else '', re.DOTALL)
            if solution_match:
                return {
                    'requirement': requirement,
                    'solution': solution_match.group(1).strip(),
                    'steps': [s.strip() for s in steps_match][:10],
                    'files_to_modify': [{'file': f.strip(), 'reason': r.strip()} for f, r in files_match],
                    'challenges': [c.strip() for c in challenges_match if c.strip()]
                }
        except:
            pass
        return None
    
    def _generate_mock_response(self, code: str, file_path: str, context_level: str = 'standard') -> str:
        """生成模拟响应（根据上下文层次生成不同层次的问题）"""
        mock_templates = {
            'minimal': f"""
Question: {file_path}中这段代码使用了什么数据结构？算法复杂度是多少？

Answer: 这段代码主要使用了哈希表(dict)和列表(list)数据结构。核心算法采用迭代方式处理数据，时间复杂度为O(n)，其中n是输入数据的规模。空间复杂度为O(n)，用于存储中间结果。代码中使用了集合(set)来去重，提高了查找效率。

Reasoning Steps:
1. 识别代码中使用的主要数据结构(dict、list、set)
2. 分析核心循环和迭代逻辑
3. 计算时间复杂度：单次遍历O(n)
4. 评估空间使用：需要额外存储空间O(n)
""",
            'standard': f"""
Question: {file_path}模块在整个系统中承担什么职责？它遵循了哪些设计模式？

Answer: 该模块作为数据处理层的核心组件，负责协调验证器和转换器，采用了策略模式和装饰器模式。通过依赖注入实现了与存储层的解耦，使用观察者模式通知其他模块处理结果。这种设计保证了单一职责原则，提高了代码的可维护性和可扩展性。

Reasoning Steps:
1. 分析模块的主要职责和在架构中的位置
2. 识别使用的设计模式：策略模式处理多种算法、装饰器增强功能
3. 评估模块间的依赖关系和解耦程度
4. 说明设计如何支持扩展和维护
""",
            'full': f"""
Question: 从系统架构角度分析，{file_path}所在子系统的设计如何满足性能和扩展性要求？在高并发场景下有哪些优化策略？

Answer: 该子系统采用分层架构和插件化设计，通过抽象工厂模式支持多数据源扩展。性能优化包括：1) 使用LRU缓存减少重复计算；2) 采用异步IO和线程池处理并发请求；3) 通过消息队列实现削峰填谷。扩展性方面，配置中心支持动态调整，水平扩展通过无状态设计实现。监控指标包括吞吐量、响应时间和资源使用率。

Reasoning Steps:
1. 分析整体架构：分层设计、插件化、可扩展性
2. 识别性能优化策略：缓存、异步、并发控制
3. 评估扩展机制：配置动态化、无状态设计
4. 说明监控和运维考量
"""
        }
        return mock_templates.get(context_level, mock_templates['standard'])
    
    def _generate_mock_design_response(self, requirement: str) -> str:
        """生成模拟设计响应"""
        return f"""
Requirement: {requirement}

Solution: 采用模块化设计，引入任务队列和缓存层。通过异步处理提升性能，使用Redis作为缓存存储，确保系统可扩展性。

Implementation Steps:
1. 创建任务队列模块，使用Celery实现异步处理
2. 设计缓存层接口，集成Redis
3. 重构核心业务逻辑，添加缓存支持
4. 实现监控和日志记录功能
5. 编写单元测试和集成测试

Files to Modify:
- core/processor.py: 添加异步处理支持
- utils/cache.py: 新建缓存管理模块
- config/settings.py: 添加任务队列配置

Challenges:
- 异步任务的错误处理和重试机制
- 缓存一致性保证
- 性能监控和优化
"""


def quick_generate(project_path: str, num_qa: int = 5, num_design: int = 3, 
                  output_path: str = "output/training_data.json", use_context: bool = True,
                  context_level: str = 'standard') -> Dict:
    """快速生成训练数据
    
    Args:
        project_path: 项目路径
        num_qa: 问答对数量
        num_design: 设计方案数量
        output_path: 输出文件路径
        use_context: 是否使用上下文
        context_level: 上下文级别 ('minimal'/'standard'/'full')
    """
    generator = SimpleGenerator(project_path)
    dataset = generator.generate_batch(num_qa, num_design, use_context, context_level)
    generator.save_dataset(dataset, output_path)
    return dataset
