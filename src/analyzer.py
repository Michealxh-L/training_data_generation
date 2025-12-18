"""
Code Repository Analyzer
Analyzes code structure, patterns, and business logic
"""
import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import git
from collections import defaultdict


@dataclass
class CodeFile:
    """Represents a code file"""
    path: str
    language: str
    content: str
    lines: int
    
    def get_snippet(self, start_line: int, end_line: int) -> str:
        """Get a code snippet"""
        lines = self.content.split('\n')
        return '\n'.join(lines[start_line-1:end_line])


@dataclass
class FunctionInfo:
    """Represents a function/method"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str]
    parameters: List[str]
    code: str
    complexity: int


@dataclass
class ClassInfo:
    """Represents a class"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str]
    methods: List[FunctionInfo]
    base_classes: List[str]


class RepositoryAnalyzer:
    """Analyzes a code repository"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = None
        try:
            self.repo = git.Repo(repo_path)
        except:
            pass
        
        self.code_files: List[CodeFile] = []
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.architecture: Dict[str, Any] = {}
    
    def analyze(self, languages: List[str] = None):
        """Perform full repository analysis"""
        if languages is None:
            languages = ['python', 'javascript', 'java']
        
        print(f"📊 Analyzing repository: {self.repo_path}")
        
        # Scan files
        self._scan_files(languages)
        print(f"   Found {len(self.code_files)} code files")
        
        # Analyze code structure
        for code_file in self.code_files:
            if code_file.language == 'python':
                self._analyze_python_file(code_file)
        
        print(f"   Found {len(self.functions)} functions")
        print(f"   Found {len(self.classes)} classes")
        
        # Analyze architecture
        self._analyze_architecture()
        
        return self
    
    def _scan_files(self, languages: List[str]):
        """Scan repository for code files"""
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java']
        }
        
        valid_extensions = []
        for lang in languages:
            valid_extensions.extend(extensions.get(lang, []))
        
        exclude_dirs = {
            'node_modules', 'venv', 'env', '__pycache__', 
            'dist', 'build', '.git', 'test', 'tests'
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in valid_extensions):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Determine language
                        ext = file_path.suffix
                        language = next((lang for lang, exts in extensions.items() if ext in exts), 'unknown')
                        
                        code_file = CodeFile(
                            path=str(relative_path),
                            language=language,
                            content=content,
                            lines=len(content.split('\n'))
                        )
                        self.code_files.append(code_file)
                    except Exception as e:
                        print(f"   ⚠️  Error reading {relative_path}: {e}")
    
    def _analyze_python_file(self, code_file: CodeFile):
        """Analyze a Python file"""
        try:
            tree = ast.parse(code_file.content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, code_file)
                    self.functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, code_file)
                    self.classes.append(class_info)
        
        except SyntaxError:
            pass
    
    def _extract_function_info(self, node: ast.FunctionDef, code_file: CodeFile) -> FunctionInfo:
        """Extract function information"""
        docstring = ast.get_docstring(node)
        parameters = [arg.arg for arg in node.args.args]
        
        # Get function code
        lines = code_file.content.split('\n')
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
        code = '\n'.join(lines[start_line-1:end_line])
        
        # Calculate complexity (simplified)
        complexity = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler)))
        
        return FunctionInfo(
            name=node.name,
            file_path=code_file.path,
            start_line=start_line,
            end_line=end_line,
            docstring=docstring,
            parameters=parameters,
            code=code,
            complexity=complexity
        )
    
    def _extract_class_info(self, node: ast.ClassDef, code_file: CodeFile) -> ClassInfo:
        """Extract class information"""
        docstring = ast.get_docstring(node)
        base_classes = [base.id for base in node.bases if isinstance(base, ast.Name)]
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, code_file)
                methods.append(method_info)
        
        return ClassInfo(
            name=node.name,
            file_path=code_file.path,
            start_line=node.lineno,
            end_line=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 10,
            docstring=docstring,
            methods=methods,
            base_classes=base_classes
        )
    
    def _analyze_architecture(self):
        """Analyze repository architecture"""
        # Group by directories
        directory_structure = defaultdict(list)
        for code_file in self.code_files:
            dir_name = str(Path(code_file.path).parent)
            directory_structure[dir_name].append(code_file)
        
        # Identify patterns
        patterns = self._identify_patterns()
        
        # Build tech stack
        tech_stack = self._identify_tech_stack()
        
        self.architecture = {
            'directory_structure': dict(directory_structure),
            'design_patterns': patterns,
            'tech_stack': tech_stack,
            'total_files': len(self.code_files),
            'total_lines': sum(f.lines for f in self.code_files),
            'languages': list(set(f.language for f in self.code_files))
        }
    
    def _identify_patterns(self) -> List[str]:
        """Identify design patterns"""
        patterns = []
        
        # Check for common patterns
        class_names = [c.name.lower() for c in self.classes]
        
        if any('factory' in name for name in class_names):
            patterns.append('Factory Pattern')
        if any('singleton' in name for name in class_names):
            patterns.append('Singleton Pattern')
        if any('observer' in name for name in class_names):
            patterns.append('Observer Pattern')
        if any('strategy' in name for name in class_names):
            patterns.append('Strategy Pattern')
        
        # Check for MVC
        dirs = set(Path(f.path).parent.name.lower() for f in self.code_files)
        if 'models' in dirs and 'views' in dirs and 'controllers' in dirs:
            patterns.append('MVC Architecture')
        
        return patterns
    
    def _identify_tech_stack(self) -> Dict[str, str]:
        """Identify technology stack"""
        tech_stack = {}
        
        # Check for framework files
        for code_file in self.code_files:
            content_lower = code_file.content.lower()
            
            # Python frameworks
            if 'from flask import' in content_lower or 'import flask' in content_lower:
                tech_stack['web_framework'] = 'Flask'
            elif 'from django' in content_lower or 'import django' in content_lower:
                tech_stack['web_framework'] = 'Django'
            elif 'from fastapi' in content_lower or 'import fastapi' in content_lower:
                tech_stack['web_framework'] = 'FastAPI'
            
            # JavaScript frameworks
            if 'from react' in content_lower or 'import react' in content_lower:
                tech_stack['frontend_framework'] = 'React'
            elif 'from vue' in content_lower or 'import vue' in content_lower:
                tech_stack['frontend_framework'] = 'Vue'
            
            # Databases
            if 'pymongo' in content_lower:
                tech_stack['database'] = 'MongoDB'
            elif 'psycopg' in content_lower or 'postgresql' in content_lower:
                tech_stack['database'] = 'PostgreSQL'
            elif 'mysql' in content_lower:
                tech_stack['database'] = 'MySQL'
        
        return tech_stack
    
    def get_functions_by_complexity(self, min_complexity: int = 3) -> List[FunctionInfo]:
        """Get functions with complexity >= threshold"""
        return [f for f in self.functions if f.complexity >= min_complexity]
    
    def get_classes_with_docstrings(self) -> List[ClassInfo]:
        """Get classes that have docstrings"""
        return [c for c in self.classes if c.docstring]
    
    def search_code(self, query: str) -> List[CodeFile]:
        """Search for code containing query"""
        results = []
        for code_file in self.code_files:
            if query.lower() in code_file.content.lower():
                results.append(code_file)
        return results
    
    def export_summary(self) -> Dict[str, Any]:
        """Export analysis summary"""
        return {
            'repository_path': str(self.repo_path),
            'total_files': len(self.code_files),
            'total_lines': sum(f.lines for f in self.code_files),
            'languages': list(set(f.language for f in self.code_files)),
            'total_functions': len(self.functions),
            'total_classes': len(self.classes),
            'architecture': self.architecture
        }
