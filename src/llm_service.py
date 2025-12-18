"""
LLM Service for generating Q&A pairs and design solutions
"""
import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic
import time

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LLMService:
    """Service for interacting with LLM APIs"""
    
    def __init__(self, provider: str = "openai", model: str = None, temperature: float = 0.7):
        self.provider = provider.lower()
        self.temperature = temperature
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        elif self.provider == "gemini":
            if genai is None:
                raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.client = genai.GenerativeModel(self.model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_completion(self, prompt: str, system_prompt: str = None, 
                          max_tokens: int = 2048, json_mode: bool = False) -> str:
        """Generate a completion"""
        try:
            if self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": max_tokens
                }
                
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                kwargs = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": self.temperature,
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                if system_prompt:
                    kwargs["system"] = system_prompt
                
                response = self.client.messages.create(**kwargs)
                return response.content[0].text
            
            elif self.provider == "gemini":
                # Combine system prompt and user prompt for Gemini
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                # Configure generation
                generation_config = {
                    "temperature": self.temperature,
                    "max_output_tokens": max_tokens,
                }
                
                if json_mode:
                    full_prompt += "\n\nPlease respond with valid JSON only."
                
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                return response.text
        
        except Exception as e:
            print(f"❌ Error generating completion: {e}")
            raise
    
    def generate_qa_pair(self, code_context: str, file_path: str, 
                        question_type: str, additional_context: str = "") -> Dict[str, Any]:
        """Generate a Q&A pair with reasoning trace"""
        
        system_prompt = """You are an expert software engineer and educator. Your task is to generate high-quality training data for fine-tuning an LLM to understand codebases.

Generate a question-answer pair about the provided code, including a detailed reasoning trace that shows your thought process."""
        
        prompt = f"""Based on the following code snippet, generate a question-answer pair.

Code Context:
File: {file_path}
{additional_context}

```
{code_context}
```

Question Type: {question_type}

Generate a JSON response with the following structure:
{{
    "question": "A clear, specific question about the code",
    "answer": "A comprehensive answer with explanations",
    "reasoning_trace": {{
        "steps": [
            {{
                "step_number": 1,
                "description": "First reasoning step",
                "code_reference": "Relevant code reference",
                "confidence": 0.9
            }}
        ],
        "overall_confidence": 0.85,
        "methodology": "Explanation of reasoning approach"
    }},
    "difficulty": "easy|medium|hard",
    "tags": ["tag1", "tag2"]
}}

Ensure the question is meaningful and the answer is detailed with proper reasoning steps."""
        
        response = self.generate_completion(prompt, system_prompt, json_mode=True)
        return json.loads(response)
    
    def generate_design_solution(self, requirement: str, architecture_context: Dict[str, Any],
                                code_examples: List[Dict[str, str]], 
                                requirement_type: str) -> Dict[str, Any]:
        """Generate a design solution with reasoning trace"""
        
        system_prompt = """You are a senior software architect. Your task is to generate comprehensive design solutions based on the existing codebase architecture.

Provide detailed design solutions with step-by-step reasoning that shows how you arrived at the solution."""
        
        # Format architecture context
        arch_summary = json.dumps(architecture_context, indent=2)
        
        # Format code examples
        code_examples_str = "\n\n".join([
            f"File: {ex['file_path']}\n```\n{ex['code']}\n```"
            for ex in code_examples[:3]  # Limit to 3 examples
        ])
        
        prompt = f"""Based on the following requirement and codebase architecture, generate a design solution.

Requirement: {requirement}
Requirement Type: {requirement_type}

Current Architecture:
{arch_summary}

Relevant Code Examples:
{code_examples_str}

Generate a JSON response with the following structure:
{{
    "solution_overview": "High-level solution summary",
    "detailed_design": "Comprehensive design explanation",
    "implementation_steps": [
        "Step 1: ...",
        "Step 2: ..."
    ],
    "affected_components": ["component1", "component2"],
    "code_examples": [
        {{
            "description": "Example description",
            "code": "Code snippet showing implementation"
        }}
    ],
    "reasoning_trace": {{
        "steps": [
            {{
                "step_number": 1,
                "description": "Design reasoning step",
                "code_reference": "Reference to existing code",
                "confidence": 0.9
            }}
        ],
        "overall_confidence": 0.85,
        "methodology": "Design methodology used"
    }},
    "complexity": "low|medium|high",
    "estimated_effort": "Time estimate",
    "risks": ["risk1", "risk2"],
    "tags": ["tag1", "tag2"]
}}

Provide a solution that fits well with the existing architecture."""
        
        response = self.generate_completion(prompt, system_prompt, max_tokens=3000, json_mode=True)
        return json.loads(response)
    
    def validate_and_improve_qa(self, qa_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and improve a Q&A pair"""
        
        system_prompt = """You are a quality assurance expert for training data. Review and improve the given Q&A pair."""
        
        prompt = f"""Review this Q&A pair and improve it if needed:

{json.dumps(qa_data, indent=2)}

Check for:
1. Question clarity and specificity
2. Answer completeness and accuracy
3. Reasoning trace logical flow
4. Code references accuracy

Return the improved version in the same JSON format, or the original if no improvements needed."""
        
        response = self.generate_completion(prompt, system_prompt, json_mode=True)
        return json.loads(response)
    
    def batch_generate_with_retry(self, generation_func, items: List[Any], 
                                 max_retries: int = 3, delay: float = 1.0) -> List[Dict[str, Any]]:
        """Batch generate with retry logic"""
        results = []
        
        for i, item in enumerate(items):
            print(f"   Generating {i+1}/{len(items)}...", end='\r')
            
            for attempt in range(max_retries):
                try:
                    result = generation_func(item)
                    results.append(result)
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"\n   ⚠️  Attempt {attempt+1} failed, retrying...")
                        time.sleep(delay * (attempt + 1))
                    else:
                        print(f"\n   ❌ Failed after {max_retries} attempts: {e}")
        
        print(f"\n   ✅ Generated {len(results)} items")
        return results
