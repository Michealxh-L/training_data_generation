"""
Main entry point for training data generation
"""
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
import yaml

from src.analyzer import RepositoryAnalyzer
from src.llm_service import LLMService
from src.qa_generator import QAGenerator
from src.design_generator import DesignSolutionGenerator
from src.data_processor import DataProcessor, DataValidator
from src.schema import TrainingDataset


def load_config(config_path: str = "config/config.yaml"):
    """Load configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution flow"""
    parser = argparse.ArgumentParser(description="Generate training data from code repository")
    parser.add_argument("--repo-path", type=str, required=True, help="Path to code repository")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Config file path")
    parser.add_argument("--output-dir", type=str, default="data/processed", help="Output directory")
    parser.add_argument("--scenario", type=str, choices=['qa', 'design', 'both'], default='both',
                       help="Which scenario to generate")
    parser.add_argument("--num-qa", type=int, default=30, help="Number of Q&A pairs to generate")
    parser.add_argument("--num-design", type=int, default=10, help="Number of design solutions to generate")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    config = load_config(args.config)
    
    print("="*70)
    print("🚀 Training Data Generation System")
    print("="*70)
    print(f"\n📁 Repository: {args.repo_path}")
    print(f"📊 Scenario: {args.scenario}")
    print(f"💾 Output: {args.output_dir}\n")
    
    # Step 1: Analyze repository
    print("\n" + "="*70)
    print("STEP 1: Repository Analysis")
    print("="*70)
    
    analyzer = RepositoryAnalyzer(args.repo_path)
    analyzer.analyze(languages=config['code_analysis']['languages'])
    
    summary = analyzer.export_summary()
    print(f"\n✅ Analysis complete:")
    print(f"   Files: {summary['total_files']}")
    print(f"   Lines of code: {summary['total_lines']}")
    print(f"   Functions: {summary['total_functions']}")
    print(f"   Classes: {summary['total_classes']}")
    print(f"   Languages: {', '.join(summary['languages'])}")
    
    # Step 2: Initialize LLM service
    print("\n" + "="*70)
    print("STEP 2: Initialize LLM Service")
    print("="*70)
    
    llm_config = config['generation']['llm']
    llm_service = LLMService(
        provider=llm_config['provider'],
        model=llm_config['model'],
        temperature=llm_config['temperature']
    )
    print(f"✅ LLM service initialized: {llm_config['provider']} - {llm_config['model']}")
    
    # Initialize dataset
    dataset = TrainingDataset(
        metadata={
            'repository': args.repo_path,
            'analysis_summary': summary,
            'config': config
        }
    )
    
    # Step 3: Generate Q&A pairs (Scenario 1)
    if args.scenario in ['qa', 'both']:
        print("\n" + "="*70)
        print("STEP 3: Scenario 1 - Q&A Generation")
        print("="*70)
        
        qa_generator = QAGenerator(analyzer, llm_service)
        qa_pairs = qa_generator.generate_qa_pairs(
            num_samples=args.num_qa,
            question_types=config['scenario1_qa']['question_types']
        )
        
        # Enhance with multi-context if enabled
        if config['scenario1_qa'].get('include_reasoning', True):
            qa_pairs = qa_generator.enhance_with_multi_context(qa_pairs)
        
        for qa in qa_pairs:
            dataset.add_qa_pair(qa)
        
        print(f"\n✅ Generated {len(qa_pairs)} Q&A pairs")
    
    # Step 4: Generate design solutions (Scenario 2)
    if args.scenario in ['design', 'both']:
        print("\n" + "="*70)
        print("STEP 4: Scenario 2 - Design Solution Generation")
        print("="*70)
        
        design_generator = DesignSolutionGenerator(analyzer, llm_service)
        design_solutions = design_generator.generate_design_solutions(
            num_samples=args.num_design,
            requirement_types=config['scenario2_design']['requirement_types']
        )
        
        for solution in design_solutions:
            dataset.add_design_solution(solution)
        
        print(f"\n✅ Generated {len(design_solutions)} design solutions")
    
    # Step 5: Validate and process data
    print("\n" + "="*70)
    print("STEP 5: Data Validation and Processing")
    print("="*70)
    
    validator = DataValidator()
    report = validator.generate_report(dataset.scenario1_data, dataset.scenario2_data)
    
    # Step 6: Export data
    print("\n" + "="*70)
    print("STEP 6: Export Data")
    print("="*70)
    
    processor = DataProcessor(args.output_dir)
    
    # Export full dataset
    if dataset.scenario1_data:
        processor.export_to_jsonl(dataset.scenario1_data, "qa_pairs.jsonl")
        processor.export_to_json(dataset.scenario1_data, "qa_pairs.json")
    
    if dataset.scenario2_data:
        processor.export_to_jsonl(dataset.scenario2_data, "design_solutions.jsonl")
        processor.export_to_json(dataset.scenario2_data, "design_solutions.json")
    
    # Export for fine-tuning
    if dataset.scenario1_data or dataset.scenario2_data:
        processor.export_for_finetuning(
            dataset.scenario1_data,
            dataset.scenario2_data,
            format="openai"
        )
    
    # Split dataset
    all_data = dataset.scenario1_data + dataset.scenario2_data
    if all_data:
        splits = processor.split_dataset(
            all_data,
            train_ratio=config['output']['split_ratios']['train'],
            val_ratio=config['output']['split_ratios']['validation'],
            test_ratio=config['output']['split_ratios']['test']
        )
        
        processor.export_to_jsonl(splits['train'], "train.jsonl")
        processor.export_to_jsonl(splits['validation'], "validation.jsonl")
        processor.export_to_jsonl(splits['test'], "test.jsonl")
    
    # Export report
    import json
    report_path = Path(args.output_dir) / "quality_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"   💾 Quality report saved to {report_path}")
    
    # Final summary
    print("\n" + "="*70)
    print("✅ GENERATION COMPLETE")
    print("="*70)
    stats = dataset.get_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"   Total samples: {stats['total_samples']}")
    print(f"   Q&A pairs: {stats['qa_pairs']}")
    print(f"   Design solutions: {stats['design_solutions']}")
    print(f"   Languages covered: {', '.join(stats['languages'])}")
    print(f"   Quality score: {report['overall']['overall_quality']:.3f}")
    print(f"\n📁 Output directory: {args.output_dir}")
    print("="*70)


if __name__ == "__main__":
    main()
