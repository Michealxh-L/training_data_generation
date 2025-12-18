"""
Data Processing and Validation Utilities
"""
import json
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from collections import Counter

from src.schema import QAPair, DesignSolution, TrainingDataset


class DataProcessor:
    """Process and export training data"""
    
    def __init__(self, output_dir: str = "./data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_jsonl(self, data: List[Any], filename: str):
        """Export data to JSONL format"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                if hasattr(item, 'model_dump'):
                    json_str = json.dumps(item.model_dump(), ensure_ascii=False, default=str)
                else:
                    json_str = json.dumps(item, ensure_ascii=False, default=str)
                f.write(json_str + '\n')
        
        print(f"   💾 Exported {len(data)} items to {output_path}")
        return output_path
    
    def export_to_json(self, data: List[Any], filename: str):
        """Export data to JSON format"""
        output_path = self.output_dir / filename
        
        json_data = []
        for item in data:
            if hasattr(item, 'model_dump'):
                json_data.append(item.model_dump())
            else:
                json_data.append(item)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"   💾 Exported {len(data)} items to {output_path}")
        return output_path
    
    def split_dataset(self, data: List[Any], 
                     train_ratio: float = 0.8,
                     val_ratio: float = 0.1,
                     test_ratio: float = 0.1) -> Dict[str, List[Any]]:
        """Split dataset into train/val/test"""
        import random
        
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.01, \
            "Split ratios must sum to 1.0"
        
        # Shuffle data
        data_copy = data.copy()
        random.shuffle(data_copy)
        
        total = len(data_copy)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        splits = {
            'train': data_copy[:train_end],
            'validation': data_copy[train_end:val_end],
            'test': data_copy[val_end:]
        }
        
        print(f"\n📊 Dataset split:")
        print(f"   Train: {len(splits['train'])} samples")
        print(f"   Validation: {len(splits['validation'])} samples")
        print(f"   Test: {len(splits['test'])} samples")
        
        return splits
    
    def export_for_finetuning(self, qa_pairs: List[QAPair], 
                             design_solutions: List[DesignSolution],
                             format: str = "openai"):
        """Export data in format suitable for fine-tuning"""
        
        if format == "openai":
            # OpenAI fine-tuning format
            training_data = []
            
            # Process Q&A pairs
            for qa in qa_pairs:
                training_data.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert software engineer helping with code understanding and design."
                        },
                        {
                            "role": "user",
                            "content": self._format_qa_input(qa)
                        },
                        {
                            "role": "assistant",
                            "content": self._format_qa_output(qa)
                        }
                    ]
                })
            
            # Process design solutions
            for solution in design_solutions:
                training_data.append({
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a senior software architect providing design solutions."
                        },
                        {
                            "role": "user",
                            "content": self._format_design_input(solution)
                        },
                        {
                            "role": "assistant",
                            "content": self._format_design_output(solution)
                        }
                    ]
                })
            
            return self.export_to_jsonl(training_data, "finetuning_data.jsonl")
    
    def _format_qa_input(self, qa: QAPair) -> str:
        """Format Q&A input for fine-tuning"""
        context = f"Question Type: {qa.question_type}\n\n"
        
        if qa.code_contexts:
            context += "Code Context:\n"
            for ctx in qa.code_contexts[:2]:  # Limit contexts
                context += f"\nFile: {ctx.file_path} (Lines {ctx.start_line}-{ctx.end_line})\n"
                context += f"```{ctx.language}\n{ctx.code_snippet[:500]}\n```\n"
        
        context += f"\nQuestion: {qa.question}"
        return context
    
    def _format_qa_output(self, qa: QAPair) -> str:
        """Format Q&A output for fine-tuning"""
        output = f"Answer: {qa.answer}\n\n"
        
        if qa.reasoning_trace:
            output += "Reasoning Process:\n"
            for step in qa.reasoning_trace.steps[:5]:  # Limit steps
                output += f"{step.step_number}. {step.description}\n"
        
        return output
    
    def _format_design_input(self, solution: DesignSolution) -> str:
        """Format design solution input for fine-tuning"""
        context = f"Requirement Type: {solution.requirement_type}\n\n"
        context += f"Requirement: {solution.requirement}\n\n"
        
        context += "Current Architecture:\n"
        context += f"Type: {solution.architecture_context.architecture_type}\n"
        context += f"Tech Stack: {solution.architecture_context.tech_stack}\n"
        context += f"Design Patterns: {', '.join(solution.architecture_context.design_patterns)}\n"
        
        return context
    
    def _format_design_output(self, solution: DesignSolution) -> str:
        """Format design solution output for fine-tuning"""
        output = f"Solution Overview:\n{solution.solution_overview}\n\n"
        output += f"Detailed Design:\n{solution.detailed_design}\n\n"
        output += "Implementation Steps:\n"
        for i, step in enumerate(solution.implementation_steps, 1):
            output += f"{i}. {step}\n"
        
        if solution.reasoning_trace:
            output += "\nDesign Reasoning:\n"
            for step in solution.reasoning_trace.steps[:5]:
                output += f"{step.step_number}. {step.description}\n"
        
        return output


class DataValidator:
    """Validate training data quality"""
    
    def validate_qa_pair(self, qa: QAPair) -> Dict[str, Any]:
        """Validate a Q&A pair"""
        issues = []
        
        # Check question length
        if len(qa.question.split()) < 5:
            issues.append("Question too short")
        
        # Check answer length
        if len(qa.answer.split()) < 20:
            issues.append("Answer too short")
        
        # Check code context
        if not qa.code_contexts:
            issues.append("No code context provided")
        
        # Check reasoning trace
        if not qa.reasoning_trace or len(qa.reasoning_trace.steps) < 2:
            issues.append("Insufficient reasoning steps")
        
        # Check confidence
        if qa.reasoning_trace and qa.reasoning_trace.overall_confidence < 0.5:
            issues.append("Low reasoning confidence")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'quality_score': self._calculate_quality_score(qa)
        }
    
    def validate_design_solution(self, solution: DesignSolution) -> Dict[str, Any]:
        """Validate a design solution"""
        issues = []
        
        # Check requirement clarity
        if len(solution.requirement.split()) < 5:
            issues.append("Requirement too vague")
        
        # Check solution completeness
        if len(solution.detailed_design.split()) < 50:
            issues.append("Design description too brief")
        
        # Check implementation steps
        if len(solution.implementation_steps) < 3:
            issues.append("Too few implementation steps")
        
        # Check reasoning trace
        if not solution.reasoning_trace or len(solution.reasoning_trace.steps) < 3:
            issues.append("Insufficient design reasoning")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'quality_score': self._calculate_design_quality_score(solution)
        }
    
    def _calculate_quality_score(self, qa: QAPair) -> float:
        """Calculate quality score for Q&A"""
        score = 0.0
        
        # Question quality (0-0.2)
        score += min(0.2, len(qa.question.split()) / 50 * 0.2)
        
        # Answer quality (0-0.3)
        score += min(0.3, len(qa.answer.split()) / 100 * 0.3)
        
        # Code context (0-0.2)
        score += min(0.2, len(qa.code_contexts) / 3 * 0.2)
        
        # Reasoning quality (0-0.3)
        if qa.reasoning_trace:
            score += min(0.3, len(qa.reasoning_trace.steps) / 5 * 0.15)
            score += qa.reasoning_trace.overall_confidence * 0.15
        
        return min(1.0, score)
    
    def _calculate_design_quality_score(self, solution: DesignSolution) -> float:
        """Calculate quality score for design solution"""
        score = 0.0
        
        # Solution overview (0-0.2)
        score += min(0.2, len(solution.solution_overview.split()) / 50 * 0.2)
        
        # Detailed design (0-0.3)
        score += min(0.3, len(solution.detailed_design.split()) / 150 * 0.3)
        
        # Implementation steps (0-0.2)
        score += min(0.2, len(solution.implementation_steps) / 7 * 0.2)
        
        # Reasoning quality (0-0.3)
        if solution.reasoning_trace:
            score += min(0.3, len(solution.reasoning_trace.steps) / 6 * 0.15)
            score += solution.reasoning_trace.overall_confidence * 0.15
        
        return min(1.0, score)
    
    def generate_report(self, qa_pairs: List[QAPair], 
                       design_solutions: List[DesignSolution]) -> Dict[str, Any]:
        """Generate quality report"""
        print("\n📈 Generating quality report...")
        
        # Validate Q&A pairs
        qa_validations = [self.validate_qa_pair(qa) for qa in qa_pairs]
        qa_valid_count = sum(1 for v in qa_validations if v['valid'])
        qa_avg_quality = sum(v['quality_score'] for v in qa_validations) / len(qa_validations) if qa_validations else 0
        
        # Validate design solutions
        design_validations = [self.validate_design_solution(sol) for sol in design_solutions]
        design_valid_count = sum(1 for v in design_validations if v['valid'])
        design_avg_quality = sum(v['quality_score'] for v in design_validations) / len(design_validations) if design_validations else 0
        
        # Collect statistics
        report = {
            'qa_pairs': {
                'total': len(qa_pairs),
                'valid': qa_valid_count,
                'invalid': len(qa_pairs) - qa_valid_count,
                'avg_quality_score': round(qa_avg_quality, 3),
                'question_types': dict(Counter([qa.question_type for qa in qa_pairs])),
                'languages': dict(Counter([ctx.language for qa in qa_pairs for ctx in qa.code_contexts]))
            },
            'design_solutions': {
                'total': len(design_solutions),
                'valid': design_valid_count,
                'invalid': len(design_solutions) - design_valid_count,
                'avg_quality_score': round(design_avg_quality, 3),
                'requirement_types': dict(Counter([sol.requirement_type for sol in design_solutions])),
                'complexity': dict(Counter([sol.complexity for sol in design_solutions]))
            },
            'overall': {
                'total_samples': len(qa_pairs) + len(design_solutions),
                'overall_quality': round((qa_avg_quality * len(qa_pairs) + design_avg_quality * len(design_solutions)) / 
                                       (len(qa_pairs) + len(design_solutions)), 3) if (qa_pairs or design_solutions) else 0
            }
        }
        
        self._print_report(report)
        return report
    
    def _print_report(self, report: Dict[str, Any]):
        """Print quality report"""
        print("\n" + "="*60)
        print("📊 QUALITY REPORT")
        print("="*60)
        
        print("\n🎯 Q&A Pairs:")
        print(f"   Total: {report['qa_pairs']['total']}")
        print(f"   Valid: {report['qa_pairs']['valid']} ({report['qa_pairs']['valid']/max(1,report['qa_pairs']['total'])*100:.1f}%)")
        print(f"   Avg Quality Score: {report['qa_pairs']['avg_quality_score']:.3f}")
        print(f"   Question Types: {report['qa_pairs']['question_types']}")
        
        print("\n🏗️  Design Solutions:")
        print(f"   Total: {report['design_solutions']['total']}")
        print(f"   Valid: {report['design_solutions']['valid']} ({report['design_solutions']['valid']/max(1,report['design_solutions']['total'])*100:.1f}%)")
        print(f"   Avg Quality Score: {report['design_solutions']['avg_quality_score']:.3f}")
        print(f"   Requirement Types: {report['design_solutions']['requirement_types']}")
        
        print("\n📈 Overall:")
        print(f"   Total Samples: {report['overall']['total_samples']}")
        print(f"   Overall Quality: {report['overall']['overall_quality']:.3f}")
        print("="*60)
