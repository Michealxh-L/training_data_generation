"""
Scenario 2: Design Solution Generator
Generates design solutions based on requirements and architecture
"""
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime

from src.schema import (
    DesignSolution, ArchitectureContext, ArchitectureComponent,
    CodeContext, ReasoningTrace, ReasoningStep,
    RequirementType, LanguageType
)
from src.analyzer import RepositoryAnalyzer
from src.llm_service import LLMService


class DesignSolutionGenerator:
    """Generates design solutions from repository analysis"""
    
    def __init__(self, analyzer: RepositoryAnalyzer, llm_service: LLMService):
        self.analyzer = analyzer
        self.llm = llm_service
        self.generated_requirements = set()
    
    def generate_design_solutions(self, num_samples: int = 20,
                                 requirement_types: List[str] = None) -> List[DesignSolution]:
        """Generate design solutions"""
        
        if requirement_types is None:
            requirement_types = [rt.value for rt in RequirementType]
        
        print(f"\n🏗️  Generating {num_samples} design solutions...")
        
        # Build architecture context first
        arch_context = self._build_architecture_context()
        
        solutions = []
        attempts = 0
        max_attempts = num_samples * 3
        
        while len(solutions) < num_samples and attempts < max_attempts:
            attempts += 1
            
            # Select random requirement type
            req_type = random.choice(requirement_types)
            
            # Generate requirement
            requirement = self._generate_requirement(req_type)
            
            if requirement and requirement.lower() not in self.generated_requirements:
                solution = self._generate_solution(requirement, req_type, arch_context)
                
                if solution:
                    solutions.append(solution)
                    self.generated_requirements.add(requirement.lower())
                    print(f"   ✅ Generated {len(solutions)}/{num_samples}", end='\r')
        
        print(f"\n   📊 Successfully generated {len(solutions)} design solutions")
        return solutions
    
    def _build_architecture_context(self) -> ArchitectureContext:
        """Build architecture context from repository analysis"""
        
        # Extract components from directory structure
        components = []
        
        for dir_name, files in self.analyzer.architecture.get('directory_structure', {}).items():
            if dir_name != '.':
                component = ArchitectureComponent(
                    name=dir_name.split('/')[-1] or 'root',
                    type='module',
                    description=f"Module containing {len(files)} files",
                    file_path=dir_name,
                    dependencies=[]
                )
                components.append(component)
        
        # Add classes as components
        for cls in self.analyzer.classes[:10]:  # Limit to top 10 classes
            component = ArchitectureComponent(
                name=cls.name,
                type='class',
                description=cls.docstring or f"Class with {len(cls.methods)} methods",
                file_path=cls.file_path,
                dependencies=cls.base_classes
            )
            components.append(component)
        
        return ArchitectureContext(
            components=components,
            design_patterns=self.analyzer.architecture.get('design_patterns', []),
            tech_stack=self.analyzer.architecture.get('tech_stack', {}),
            architecture_type=self._infer_architecture_type()
        )
    
    def _infer_architecture_type(self) -> str:
        """Infer overall architecture type"""
        patterns = self.analyzer.architecture.get('design_patterns', [])
        tech_stack = self.analyzer.architecture.get('tech_stack', {})
        
        if 'MVC Architecture' in patterns:
            return 'MVC'
        elif 'web_framework' in tech_stack:
            if tech_stack['web_framework'] in ['FastAPI', 'Flask']:
                return 'RESTful API'
            else:
                return 'Web Application'
        elif 'microservices' in str(patterns).lower():
            return 'Microservices'
        else:
            return 'Modular Monolith'
    
    def _generate_requirement(self, requirement_type: str) -> str:
        """Generate a realistic requirement"""
        
        templates = {
            RequirementType.NEW_FEATURE.value: [
                "Add user authentication with JWT tokens",
                "Implement caching layer for frequently accessed data",
                "Add rate limiting to API endpoints",
                "Implement real-time notifications using WebSockets",
                "Add file upload functionality with S3 integration",
                "Implement search functionality with Elasticsearch",
                "Add analytics and logging for user actions"
            ],
            RequirementType.REFACTORING.value: [
                "Refactor the data access layer to use repository pattern",
                "Extract common validation logic into reusable validators",
                "Improve error handling and add custom exception classes",
                "Refactor configuration management to use environment variables",
                "Split large service class into smaller, focused services",
                "Improve code modularity by applying dependency injection"
            ],
            RequirementType.INTEGRATION.value: [
                "Integrate with third-party payment gateway (Stripe)",
                "Add integration with email service (SendGrid)",
                "Implement OAuth2 integration with Google/GitHub",
                "Integrate with message queue (RabbitMQ/Redis)",
                "Add monitoring integration with Prometheus",
                "Integrate with external API for data enrichment"
            ],
            RequirementType.OPTIMIZATION.value: [
                "Optimize database queries to reduce response time",
                "Implement connection pooling for database connections",
                "Add caching strategy to reduce API calls",
                "Optimize image processing pipeline",
                "Implement lazy loading for heavy resources",
                "Add background job processing for long-running tasks"
            ]
        }
        
        candidates = templates.get(requirement_type, ["Implement a new feature"])
        return random.choice(candidates)
    
    def _generate_solution(self, requirement: str, requirement_type: str,
                          arch_context: ArchitectureContext) -> DesignSolution:
        """Generate a design solution"""
        
        # Select relevant code examples
        code_examples = self._select_relevant_code_examples(requirement)
        
        try:
            # Prepare architecture context for LLM
            arch_dict = {
                'components': [
                    {
                        'name': c.name,
                        'type': c.type,
                        'description': c.description,
                        'dependencies': c.dependencies
                    }
                    for c in arch_context.components[:10]  # Limit for token count
                ],
                'design_patterns': arch_context.design_patterns,
                'tech_stack': arch_context.tech_stack,
                'architecture_type': arch_context.architecture_type
            }
            
            # Prepare code examples
            code_ex_list = [
                {
                    'file_path': ex.file_path,
                    'code': ex.code_snippet[:500]  # Limit code length
                }
                for ex in code_examples[:3]
            ]
            
            # Generate with LLM
            llm_response = self.llm.generate_design_solution(
                requirement=requirement,
                architecture_context=arch_dict,
                code_examples=code_ex_list,
                requirement_type=requirement_type
            )
            
            # Parse affected components
            affected_components = llm_response.get('affected_components', [])
            
            # Create code contexts from examples
            code_contexts = code_examples[:3]
            
            # Add generated code examples
            for gen_ex in llm_response.get('code_examples', [])[:2]:
                if 'code' in gen_ex:
                    code_contexts.append(
                        CodeContext(
                            file_path="generated_example.py",
                            start_line=1,
                            end_line=len(gen_ex['code'].split('\n')),
                            code_snippet=gen_ex['code'],
                            language=LanguageType.PYTHON
                        )
                    )
            
            # Create DesignSolution object
            solution = DesignSolution(
                id=str(uuid.uuid4()),
                requirement=requirement,
                requirement_type=RequirementType(requirement_type),
                solution_overview=llm_response['solution_overview'],
                detailed_design=llm_response['detailed_design'],
                implementation_steps=llm_response['implementation_steps'],
                architecture_context=arch_context,
                affected_components=affected_components,
                code_examples=code_contexts,
                reasoning_trace=ReasoningTrace(
                    steps=[
                        ReasoningStep(**step)
                        for step in llm_response['reasoning_trace']['steps']
                    ],
                    overall_confidence=llm_response['reasoning_trace']['overall_confidence'],
                    methodology=llm_response['reasoning_trace']['methodology']
                ),
                complexity=llm_response.get('complexity', 'medium'),
                estimated_effort=llm_response.get('estimated_effort', '1-2 weeks'),
                risks=llm_response.get('risks', []),
                tags=llm_response.get('tags', []),
                created_at=datetime.now()
            )
            
            return solution
        
        except Exception as e:
            print(f"\n   ⚠️  Error generating design solution: {e}")
            return None
    
    def _select_relevant_code_examples(self, requirement: str) -> List[CodeContext]:
        """Select code examples relevant to the requirement"""
        
        # Extract keywords from requirement
        keywords = [word.lower() for word in requirement.split() 
                   if len(word) > 4 and word.isalpha()]
        
        relevant_examples = []
        
        # Search for relevant code
        for keyword in keywords[:3]:  # Limit keyword search
            matching_files = self.analyzer.search_code(keyword)
            
            for code_file in matching_files[:2]:  # Limit files per keyword
                # Take a reasonable snippet
                snippet_lines = min(50, code_file.lines)
                
                context = CodeContext(
                    file_path=code_file.path,
                    start_line=1,
                    end_line=snippet_lines,
                    code_snippet=code_file.get_snippet(1, snippet_lines),
                    language=LanguageType(code_file.language)
                )
                relevant_examples.append(context)
        
        # If no keyword matches, use random complex functions
        if not relevant_examples:
            complex_funcs = self.analyzer.get_functions_by_complexity(min_complexity=3)
            
            for func in complex_funcs[:3]:
                code_file = next((f for f in self.analyzer.code_files 
                                if f.path == func.file_path), None)
                if code_file:
                    context = CodeContext(
                        file_path=func.file_path,
                        start_line=func.start_line,
                        end_line=func.end_line,
                        code_snippet=func.code,
                        language=LanguageType(code_file.language)
                    )
                    relevant_examples.append(context)
        
        return relevant_examples[:5]  # Return top 5
