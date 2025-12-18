"""
Training Data Schema Definitions
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class LanguageType(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"


class QuestionType(str, Enum):
    """Types of questions for Q&A generation"""
    CODE_EXPLANATION = "code_explanation"
    BUSINESS_LOGIC = "business_logic"
    DESIGN_PATTERN = "design_pattern"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class RequirementType(str, Enum):
    """Types of requirements for design solution generation"""
    NEW_FEATURE = "new_feature"
    REFACTORING = "refactoring"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"


class CodeContext(BaseModel):
    """Code context information"""
    file_path: str = Field(description="Relative path to the source file")
    start_line: int = Field(description="Starting line number")
    end_line: int = Field(description="Ending line number")
    code_snippet: str = Field(description="The actual code snippet")
    language: LanguageType = Field(description="Programming language")
    
    class Config:
        use_enum_values = True


class ReasoningStep(BaseModel):
    """A single step in the reasoning trace"""
    step_number: int = Field(description="Step sequence number")
    description: str = Field(description="Description of this reasoning step")
    code_reference: Optional[str] = Field(None, description="Reference to specific code")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for this step")


class ReasoningTrace(BaseModel):
    """Complete reasoning trace for a Q&A or design solution"""
    steps: List[ReasoningStep] = Field(description="List of reasoning steps")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence")
    methodology: str = Field(description="Reasoning methodology used")


# ============ Scenario 1: Q&A Generation ============

class QAPair(BaseModel):
    """Question-Answer pair with context and reasoning"""
    id: str = Field(description="Unique identifier")
    question: str = Field(description="The question about the codebase")
    answer: str = Field(description="The detailed answer")
    question_type: QuestionType = Field(description="Type of question")
    
    # Code context
    code_contexts: List[CodeContext] = Field(description="Relevant code contexts")
    
    # Reasoning trace
    reasoning_trace: ReasoningTrace = Field(description="Step-by-step reasoning")
    
    # Metadata
    difficulty: Literal["easy", "medium", "hard"] = Field(description="Question difficulty")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


# ============ Scenario 2: Design Solution Generation ============

class ArchitectureComponent(BaseModel):
    """A component in the architecture"""
    name: str = Field(description="Component name")
    type: str = Field(description="Component type (e.g., service, module, class)")
    description: str = Field(description="Component description")
    file_path: Optional[str] = Field(None, description="Related file path")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies")


class ArchitectureContext(BaseModel):
    """Architecture context of the codebase"""
    components: List[ArchitectureComponent] = Field(description="System components")
    design_patterns: List[str] = Field(description="Identified design patterns")
    tech_stack: Dict[str, str] = Field(description="Technology stack")
    architecture_type: str = Field(description="Overall architecture type")


class DesignSolution(BaseModel):
    """Design solution for a requirement"""
    id: str = Field(description="Unique identifier")
    requirement: str = Field(description="The design requirement")
    requirement_type: RequirementType = Field(description="Type of requirement")
    
    # Solution
    solution_overview: str = Field(description="High-level solution overview")
    detailed_design: str = Field(description="Detailed design explanation")
    implementation_steps: List[str] = Field(description="Implementation steps")
    
    # Architecture context
    architecture_context: ArchitectureContext = Field(description="Current architecture")
    affected_components: List[str] = Field(description="Components to be modified")
    
    # Code examples
    code_examples: List[CodeContext] = Field(description="Example code snippets")
    
    # Reasoning trace
    reasoning_trace: ReasoningTrace = Field(description="Design reasoning process")
    
    # Metadata
    complexity: Literal["low", "medium", "high"] = Field(description="Solution complexity")
    estimated_effort: str = Field(description="Estimated implementation effort")
    risks: List[str] = Field(default_factory=list, description="Potential risks")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


# ============ Training Dataset ============

class TrainingDataset(BaseModel):
    """Complete training dataset"""
    metadata: Dict[str, Any] = Field(description="Dataset metadata")
    scenario1_data: List[QAPair] = Field(default_factory=list, description="Q&A pairs")
    scenario2_data: List[DesignSolution] = Field(default_factory=list, description="Design solutions")
    
    def add_qa_pair(self, qa: QAPair):
        """Add a Q&A pair"""
        self.scenario1_data.append(qa)
    
    def add_design_solution(self, solution: DesignSolution):
        """Add a design solution"""
        self.scenario2_data.append(solution)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        return {
            "total_samples": len(self.scenario1_data) + len(self.scenario2_data),
            "qa_pairs": len(self.scenario1_data),
            "design_solutions": len(self.scenario2_data),
            "languages": list(set([ctx.language for qa in self.scenario1_data for ctx in qa.code_contexts])),
            "question_types": list(set([qa.question_type for qa in self.scenario1_data])),
            "requirement_types": list(set([sol.requirement_type for sol in self.scenario2_data]))
        }
