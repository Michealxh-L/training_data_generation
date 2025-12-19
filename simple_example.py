#!/usr/bin/env python
"""
简单命令行示例 - 快速生成训练数据
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.simple_generator import quick_generate
from src.context_analyzer import GitHubIntegration


def main():
    """主函数"""
    print("="*70)
    print("🚀 训练数据生成系统 - 简单示例")
    print("="*70)
    
    # 步骤1: 选择项目
    print("\n📁 步骤1: 选择项目")
    print("-" * 70)
    
    # 默认使用示例项目
    default_project = "https://github.com/qzc438-research/ontology-llm"
    
    print(f"\n默认项目: {default_project}")
    print("\n选项:")
    print("  1. 使用默认项目")
    print("  2. 输入GitHub URL")
    print("  3. 输入本地路径")
    
    choice = input("\n请选择 (1/2/3) [默认=1]: ").strip() or "1"
    
    if choice == "1":
        project_source = default_project
    elif choice == "2":
        project_source = input("请输入GitHub URL: ").strip()
    elif choice == "3":
        project_source = input("请输入本地路径: ").strip()
    else:
        print("❌ 无效选择")
        return
    
    # 克隆或使用项目
    try:
        project_path = GitHubIntegration.clone_or_use_repo(project_source)
    except Exception as e:
        print(f"❌ 项目加载失败: {e}")
        return
    
    # 步骤2: 配置生成参数
    print("\n⚙️  步骤2: 配置生成参数")
    print("-" * 70)
    
    num_qa = input("\n问答对数量 [默认=5]: ").strip() or "5"
    num_design = input("设计方案数量 [默认=3]: ").strip() or "3"
    use_context = input("启用上下文增强? (y/n) [默认=y]: ").strip().lower() or "y"
    
    try:
        num_qa = int(num_qa)
        num_design = int(num_design)
        use_context = use_context == 'y'
    except ValueError:
        print("❌ 参数格式错误")
        return
    
    # 步骤3: 生成数据
    print("\n🚀 步骤3: 生成训练数据")
    print("-" * 70)
    
    output_dir = Path("outputs") / project_path.name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "training_data.json"
    
    print(f"\n📊 配置摘要:")
    print(f"   项目: {project_path.name}")
    print(f"   问答对: {num_qa}")
    print(f"   设计方案: {num_design}")
    print(f"   上下文增强: {use_context}")
    print(f"   输出路径: {output_path}")
    print(f"\n⏱️  预计耗时: {(num_qa + num_design) * 15 / 60:.1f} 分钟\n")
    
    confirm = input("开始生成? (y/n) [默认=y]: ").strip().lower() or "y"
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    # 执行生成
    try:
        dataset = quick_generate(
            project_path=str(project_path),
            num_qa=num_qa,
            num_design=num_design,
            output_path=str(output_path),
            use_context=use_context
        )
        
        # 显示结果
        print("\n" + "="*70)
        print("✅ 生成完成！")
        print("="*70)
        print(f"\n📊 数据统计:")
        print(f"   问答对: {len(dataset['qa_pairs'])}")
        print(f"   设计方案: {len(dataset['design_solutions'])}")
        print(f"   成功率: {((len(dataset['qa_pairs']) + len(dataset['design_solutions'])) / (num_qa + num_design) * 100):.1f}%")
        print(f"\n💾 文件已保存:")
        print(f"   {output_path}")
        print(f"   大小: {output_path.stat().st_size / 1024:.1f} KB")
        
        # 显示示例
        if dataset['qa_pairs']:
            print("\n📝 问答对示例:")
            sample = dataset['qa_pairs'][0]
            print(f"   Q: {sample['question'][:60]}...")
            print(f"   A: {sample['answer'][:60]}...")
        
        print("\n🎉 完成！")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
