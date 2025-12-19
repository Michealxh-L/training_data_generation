#!/usr/bin/env python
"""
API连接测试脚本 - 验证LLM服务是否可用
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.llm_service import LLMService


def test_api_connection(provider: str, model: str):
    """测试API连接"""
    print("="*70)
    print(f"🔍 测试 {provider.upper()} API 连接")
    print("="*70)
    
    try:
        # 初始化服务
        print(f"\n1️⃣  初始化 LLM 服务...")
        llm_service = LLMService(
            provider=provider,
            model=model,
            temperature=0.3
        )
        print(f"   ✅ 服务初始化成功")
        print(f"   📦 模型: {model}")
        
        # 简单测试
        print(f"\n2️⃣  测试 1: 简单文本生成...")
        response1 = llm_service.generate_completion(
            prompt="Return only the word 'HELLO'",
            max_tokens=10
        )
        print(f"   ✅ 响应: {response1.strip()}")
        
        # JSON模式测试
        print(f"\n3️⃣  测试 2: JSON响应...")
        response2 = llm_service.generate_completion(
            prompt='Generate a JSON object with keys "status" and "message". Set status to "ok" and message to "API working".',
            max_tokens=100,
            json_mode=True
        )
        print(f"   ✅ 响应: {response2.strip()[:100]}")
        
        # 代码理解测试
        print(f"\n4️⃣  测试 3: 代码理解能力...")
        code_test = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        response3 = llm_service.generate_completion(
            prompt=f"Explain this Python function in one sentence:\n{code_test}",
            max_tokens=100
        )
        print(f"   ✅ 响应: {response3.strip()[:150]}...")
        
        print("\n" + "="*70)
        print("✅ 所有测试通过！API连接正常")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n" + "="*70)
        print("⚠️  API连接失败")
        print("="*70)
        print("\n可能的原因：")
        print("  1. API密钥未配置或无效")
        print("  2. 网络连接问题")
        print("  3. API配额不足")
        print("  4. 模型名称错误")
        
        if provider == "gemini":
            print(f"\n📝 Gemini配置检查：")
            print(f"   环境变量: GEMINI_API_KEY")
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                print(f"   ✅ API密钥已设置 (前6位: {api_key[:6]}...)")
            else:
                print(f"   ❌ API密钥未设置")
        elif provider == "openai":
            print(f"\n📝 OpenAI配置检查：")
            print(f"   环境变量: OPENAI_API_KEY")
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                print(f"   ✅ API密钥已设置 (前7位: {api_key[:7]}...)")
            else:
                print(f"   ❌ API密钥未设置")
        
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 LLM API 连接测试工具")
    print("="*70)
    
    # 加载环境变量
    load_dotenv()
    
    # 测试配置
    test_configs = [
        ("gemini", "gemini-2.5-flash"),
        # ("openai", "gpt-4-turbo-preview"),
        # ("anthropic", "claude-3-sonnet-20240229"),
    ]
    
    results = {}
    for provider, model in test_configs:
        print("\n")
        success = test_api_connection(provider, model)
        results[provider] = success
        print("\n")
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    for provider, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"   {provider.upper()}: {status}")
    
    # 返回状态
    all_success = all(results.values())
    if all_success:
        print("\n🎉 所有配置的API都工作正常！")
        return 0
    else:
        print("\n⚠️  部分API连接失败，请检查配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
