"""
Scenario 1: Q&A Pair Generator
Generates question-answer pairs based on code analysis
"""
import random
import uuid
from typing import List, Dict, Any
from datetime import datetime

from src.schema import (
    QAPair, CodeContext, ReasoningTrace, ReasoningStep,
    QuestionType, LanguageType
)
from src.analyzer import RepositoryAnalyzer, FunctionInfo, ClassInfo
from src.llm_service import LLMService


class QAGenerator:
    """Generates Q&A pairs from code repository"""
    
    def __init__(self, analyzer: RepositoryAnalyzer, llm_service: LLMService):
        self.analyzer = analyzer
        self.llm = llm_service
        self.generated_questions = set()
    
    def generate_qa_pairs(self, num_samples: int = 50, 
                         question_types: List[str] = None) -> List[QAPair]:
        """Generate Q&A pairs"""
        
        if question_types is None:
            question_types = [qt.value for qt in QuestionType]
        
        print(f"\n🎯 Generating {num_samples} Q&A pairs...")
        
        qa_pairs = []
        attempts = 0
        max_attempts = num_samples * 3
        
        while len(qa_pairs) < num_samples and attempts < max_attempts:
            attempts += 1
            
            # Select a random question type
            question_type = random.choice(question_types)
            
            # Generate based on type
            if question_type in [QuestionType.CODE_EXPLANATION.value, 
                                QuestionType.BUSINESS_LOGIC.value]:
                qa = self._generate_function_qa(question_type)
            elif question_type == QuestionType.DESIGN_PATTERN.value:
                qa = self._generate_class_qa(question_type)
            else:
                qa = self._generate_general_qa(question_type)
            
            if qa and self._is_unique_question(qa.question):
                qa_pairs.append(qa)
                self.generated_questions.add(qa.question.lower())
                print(f"   ✅ Generated {len(qa_pairs)}/{num_samples}", end='\r')
        
        print(f"\n   📊 Successfully generated {len(qa_pairs)} Q&A pairs")
        return qa_pairs
    
    def _generate_function_qa(self, question_type: str) -> QAPair:
        """Generate Q&A for a function"""
        # Select a function with decent complexity
        candidates = self.analyzer.get_functions_by_complexity(min_complexity=2)
        
        if not candidates:
            candidates = self.analyzer.functions
        
        if not candidates:
            return None
        
        func = random.choice(candidates)
        
        # Get code context
        code_file = next((f for f in self.analyzer.code_files if f.path == func.file_path), None)
        if not code_file:
            return None
        
        # Build context
        additional_context = f"Function: {func.name}\n"
        if func.docstring:
            additional_context += f"Docstring: {func.docstring}\n"
        
        try:
            # Generate with LLM
            llm_response = self.llm.generate_qa_pair(
                code_context=func.code,
                file_path=func.file_path,
                question_type=question_type,
                additional_context=additional_context
            )
            
            # Check if LLM returned valid response
            if llm_response is None:
                return None
            
            # Create QAPair object
            qa_pair = QAPair(
                id=str(uuid.uuid4()),
                question=llm_response['question'],
                answer=llm_response['answer'],
                question_type=QuestionType(question_type),
                code_contexts=[
                    CodeContext(
                        file_path=func.file_path,
                        start_line=func.start_line,
                        end_line=func.end_line,
                        code_snippet=func.code,
                        language=LanguageType(code_file.language)
                    )
                ],
                reasoning_trace=ReasoningTrace(
                    steps=[
                        ReasoningStep(**step) 
                        for step in llm_response['reasoning_trace']['steps']
                    ],
                    overall_confidence=llm_response['reasoning_trace']['overall_confidence'],
                    methodology=llm_response['reasoning_trace']['methodology']
                ),
                difficulty=llm_response.get('difficulty', 'medium'),
                tags=llm_response.get('tags', []),
                created_at=datetime.now()
            )
            
            return qa_pair
        
        except Exception as e:
            print(f"\n   ⚠️  Error generating function Q&A: {e}")
            return None
    
    def _generate_class_qa(self, question_type: str) -> QAPair:
        """Generate Q&A for a class"""
        # Select a class with docstring
        candidates = self.analyzer.get_classes_with_docstrings()
        
        if not candidates:
            candidates = self.analyzer.classes
        
        if not candidates:
            return None
        
        cls = random.choice(candidates)
        
        # Get code context
        code_file = next((f for f in self.analyzer.code_files if f.path == cls.file_path), None)
        if not code_file:
            return None
        
        # Get class code
        class_code = code_file.get_snippet(cls.start_line, cls.end_line)
        
        # Build context
        additional_context = f"Class: {cls.name}\n"
        if cls.docstring:
            additional_context += f"Docstring: {cls.docstring}\n"
        if cls.base_classes:
            additional_context += f"Inherits from: {', '.join(cls.base_classes)}\n"
        additional_context += f"Methods: {', '.join([m.name for m in cls.methods])}\n"
        
        try:
            # Generate with LLM
            llm_response = self.llm.generate_qa_pair(
                code_context=class_code,
                file_path=cls.file_path,
                question_type=question_type,
                additional_context=additional_context
            )
            
            # Create QAPair object
            qa_pair = QAPair(
                id=str(uuid.uuid4()),
                question=llm_response['question'],
                answer=llm_response['answer'],
                question_type=QuestionType(question_type),
                code_contexts=[
                    CodeContext(
                        file_path=cls.file_path,
                        start_line=cls.start_line,
                        end_line=cls.end_line,
                        code_snippet=class_code,
                        language=LanguageType(code_file.language)
                    )
                ],
                reasoning_trace=ReasoningTrace(
                    steps=[
                        ReasoningStep(**step) 
                        for step in llm_response['reasoning_trace']['steps']
                    ],
                    overall_confidence=llm_response['reasoning_trace']['overall_confidence'],
                    methodology=llm_response['reasoning_trace']['methodology']
                ),
                difficulty=llm_response.get('difficulty', 'medium'),
                tags=llm_response.get('tags', []),
                created_at=datetime.now()
            )
            
            return qa_pair
        
        except Exception as e:
            print(f"\n   ⚠️  Error generating class Q&A: {e}")
            return None
    
    def _generate_general_qa(self, question_type: str) -> QAPair:
        """Generate general Q&A about the codebase"""
        # For error handling and optimization questions, select any function
        if not self.analyzer.functions:
            return None
        
        func = random.choice(self.analyzer.functions)
        return self._generate_function_qa(question_type)
    
    def _is_unique_question(self, question: str) -> bool:
        """Check if question is sufficiently unique"""
        question_lower = question.lower()
        
        # Check for exact duplicates
        if question_lower in self.generated_questions:
            return False
        
        # Check for similar questions (simple similarity check)
        for existing_q in self.generated_questions:
            # If questions are very similar (>80% word overlap), consider as duplicate
            q_words = set(question_lower.split())
            e_words = set(existing_q.split())
            
            if len(q_words) > 0 and len(e_words) > 0:
                overlap = len(q_words & e_words) / len(q_words | e_words)
                if overlap > 0.8:
                    return False
        
        return True
    
    def enhance_with_multi_context(self, qa_pairs: List[QAPair]) -> List[QAPair]:
        """Enhance Q&A pairs by adding related code contexts"""
        print("\n🔗 Enhancing Q&A pairs with additional contexts...")
        
        for i, qa in enumerate(qa_pairs):
            # Find related code
            primary_file = qa.code_contexts[0].file_path if qa.code_contexts else None
            
            if primary_file:
                # Search for related imports or references
                related_files = self.analyzer.search_code(primary_file.split('/')[-1].replace('.py', ''))
                
                for related_file in related_files[:2]:  # Add up to 2 related contexts
                    if related_file.path != primary_file:
                        qa.code_contexts.append(
                            CodeContext(
                                file_path=related_file.path,
                                start_line=1,
                                end_line=min(50, related_file.lines),
                                code_snippet=related_file.get_snippet(1, min(50, related_file.lines)),
                                language=LanguageType(related_file.language)
                            )
                        )
            
            print(f"   Enhanced {i+1}/{len(qa_pairs)}", end='\r')
        
        print(f"\n   ✅ Enhanced {len(qa_pairs)} Q&A pairs")
        return qa_pairs
