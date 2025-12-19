"""项目上下文分析器"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class ProjectContextAnalyzer:
    """项目上下文分析器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self._structure_cache = None
        
    def analyze_project_structure(self) -> Dict:
        """分析项目结构"""
        if self._structure_cache is not None:
            return self._structure_cache
            
        structure = {
            'project_name': self.project_name,
            'total_files': 0,
            'python_files': [],
            'core_modules': [],
            'readme_summary': '',
            'common_imports': set()
        }
        
        # 统计文件
        for py_file in self.project_path.rglob('*.py'):
            if '__pycache__' not in str(py_file) and '.venv' not in str(py_file):
                rel_path = py_file.relative_to(self.project_path)
                structure['python_files'].append(str(rel_path))
                structure['total_files'] += 1
                
                # 识别核心模块（根目录或src下的主要文件）
                if len(rel_path.parts) <= 2 and py_file.stem not in ['__init__', 'setup']:
                    structure['core_modules'].append(py_file.stem)
        
        # 读取 README 摘要
        readme_file = self.project_path / 'README.md'
        if readme_file.exists():
            try:
                content = readme_file.read_text(encoding='utf-8')
                # 提取第一段或前200字符
                first_paragraph = content.split('\n\n')[0]
                structure['readme_summary'] = first_paragraph[:200]
            except:
                pass
        
        self._structure_cache = structure
        return structure
    
    def analyze_file_role(self, file_path: str) -> str:
        """
        推断文件在架构中的角色
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件角色描述
        """
        path_lower = file_path.lower()
        
        # 基于路径和文件名的规则推断
        if 'test' in path_lower:
            return "测试文件"
        elif 'api' in path_lower or 'endpoint' in path_lower:
            return "API接口层"
        elif 'service' in path_lower or 'business' in path_lower:
            return "业务逻辑层"
        elif 'model' in path_lower or 'schema' in path_lower:
            return "数据模型层"
        elif 'util' in path_lower or 'helper' in path_lower:
            return "工具函数模块"
        elif 'config' in path_lower or 'setting' in path_lower:
            return "配置模块"
        elif 'main' in path_lower or 'app' in path_lower:
            return "应用入口"
        elif 'core' in path_lower or 'engine' in path_lower:
            return "核心逻辑"
        else:
            return "业务模块"
    
    def extract_imports(self, file_path: str) -> List[str]:
        """提取文件导入依赖"""
        try:
            full_path = self.project_path / file_path
            content = full_path.read_text(encoding='utf-8')
            lines = content.split('\n')[:50]
            imports = []
            for line in lines:
                if line.strip().startswith('import '):
                    match = re.search(r'import\s+([\w.]+)', line)
                    if match:
                        imports.append(match.group(1).split('.')[0])
                elif line.strip().startswith('from '):
                    match = re.search(r'from\s+([\w.]+)', line)
                    if match:
                        imports.append(match.group(1).split('.')[0])
            return list(set(imports))
        except:
            return []
    
    def extract_function_signatures(self, file_path: str) -> List[str]:
        """
        提取文件中的主要函数签名
        
        Args:
            file_path: 文件路径
            
        Returns:
            函数签名列表
        """
        try:
            full_path = self.project_path / file_path
            content = full_path.read_text(encoding='utf-8')
            
            # 使用正则提取函数定义
            pattern = r'def\s+(\w+)\s*\([^)]*\):'
            functions = re.findall(pattern, content)
            
            # 过滤私有函数和特殊方法
            public_functions = [
                f for f in functions 
                if not f.startswith('_') or f.startswith('__init__')
            ]
            
            return public_functions[:10]  # 最多返回10个
        except:
            return []
    
    def build_context(self, code_snippet: str, file_path: str, context_level: str = 'standard') -> str:
        """构建项目上下文"""
        structure = self.analyze_project_structure()
        file_role = self.analyze_file_role(file_path)
        
        context_parts = []
        
        # Minimal: 项目名称 + 文件名
        context_parts.append(f"【项目】{structure['project_name']}")
        context_parts.append(f"【文件】{file_path} ({file_role})")
        
        if context_level in ['standard', 'full']:
            # Standard: 添加核心模块和依赖
            imports = self.extract_imports(file_path)
            if imports:
                context_parts.append(f"【依赖】{', '.join(imports[:5])}")
            
            if structure['core_modules']:
                context_parts.append(f"【核心模块】{', '.join(structure['core_modules'][:5])}")
            
            # 添加主要函数
            functions = self.extract_function_signatures(file_path)
            if functions:
                context_parts.append(f"【主要函数】{', '.join(functions[:5])}")
        
        if context_level == 'full':
            # Full: 添加项目摘要和统计
            if structure['readme_summary']:
                context_parts.append(f"【项目简介】{structure['readme_summary']}")
            context_parts.append(f"【项目规模】{structure['total_files']}个文件")
        
        return '\n'.join(context_parts)
    
    def get_enhanced_prompt_prefix(
        self,
        code_snippet: str,
        file_path: str,
        context_level: str = 'standard'
    ) -> str:
        """
        生成增强的提示词前缀（用于 LLM 调用）
        
        Args:
            code_snippet: 代码片段
            file_path: 文件路径
            context_level: 上下文级别
            
        Returns:
            提示词前缀
        """
        context = self.build_context(code_snippet, file_path, context_level)
        
        prefix = f"""
## 项目上下文信息

{context}

## 注意事项
- 请结合项目整体架构理解代码
- 回答应体现对项目设计模式的理解
- 推理过程应考虑模块间的协作关系
"""
        return prefix


class GitHubIntegration:
    """GitHub 项目集成工具"""
    
    @staticmethod
    def clone_or_use_repo(repo_url_or_path: str, target_dir: Optional[str] = None) -> Path:
        """克隆 GitHub 仓库或使用本地路径"""
        import subprocess
        
        # 判断是 GitHub URL 还是本地路径
        if repo_url_or_path.startswith('https://github.com'):
            # GitHub URL: 需要克隆
            if target_dir is None:
                # 自动生成目标目录
                repo_name = repo_url_or_path.rstrip('/').split('/')[-1]
                repo_name = repo_name.replace('.git', '')
                target_dir = Path.home() / 'github_repos' / repo_name
            else:
                target_dir = Path(target_dir)
            
            # 检查是否已克隆
            if target_dir.exists():
                print(f"✅ 项目已存在: {target_dir}")
                return target_dir
            
            # 执行浅克隆
            print(f"🔄 正在克隆项目: {repo_url_or_path}")
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                subprocess.run(
                    ['git', 'clone', '--depth', '1', repo_url_or_path, str(target_dir)],
                    check=True,
                    timeout=300  # 5分钟超时
                )
                print(f"✅ 克隆成功: {target_dir}")
                return target_dir
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"克隆失败: {e}")
            except subprocess.TimeoutExpired:
                raise RuntimeError("克隆超时（5分钟）")
        else:
            # 本地路径: 直接使用
            local_path = Path(repo_url_or_path)
            if not local_path.exists():
                raise FileNotFoundError(f"路径不存在: {local_path}")
            print(f"✅ 使用本地项目: {local_path}")
            return local_path
