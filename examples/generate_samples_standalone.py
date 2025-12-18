"""
Standalone example demonstrating training data structure
No external dependencies required
"""
import json
from pathlib import Path
from datetime import datetime


def create_sample_qa_pair():
    """Create a sample Q&A pair"""
    return {
        "id": "sample-qa-001",
        "question": "What is the purpose of the authenticate function in the auth module?",
        "answer": """The authenticate function validates user credentials and generates a JWT token. 
It performs the following operations:
1. Validates the username format
2. Queries the database for the user record
3. Verifies the password hash using bcrypt
4. Generates a JWT token with user claims
5. Returns the token or raises an authentication error""",
        "question_type": "code_explanation",
        "code_contexts": [
            {
                "file_path": "src/auth.py",
                "start_line": 10,
                "end_line": 35,
                "code_snippet": """def authenticate(username: str, password: str) -> str:
    '''Authenticate user and return JWT token'''
    # Validate username
    if not username or len(username) < 3:
        raise ValueError("Invalid username")
    
    # Query database
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise AuthenticationError("User not found")
    
    # Verify password
    if not bcrypt.checkpw(password.encode(), user.password_hash):
        raise AuthenticationError("Invalid password")
    
    # Generate JWT token
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return token""",
                "language": "python"
            }
        ],
        "reasoning_trace": {
            "steps": [
                {
                    "step_number": 1,
                    "description": "First, I examine the function signature to understand inputs (username, password) and output (JWT token string)",
                    "code_reference": "def authenticate(username: str, password: str) -> str",
                    "confidence": 0.95
                },
                {
                    "step_number": 2,
                    "description": "Next, I identify the validation logic that checks username format",
                    "code_reference": "if not username or len(username) < 3",
                    "confidence": 0.90
                },
                {
                    "step_number": 3,
                    "description": "Then I see the database query to fetch user record",
                    "code_reference": "user = db.query(User).filter_by(username=username).first()",
                    "confidence": 0.92
                },
                {
                    "step_number": 4,
                    "description": "I observe the password verification using bcrypt",
                    "code_reference": "bcrypt.checkpw(password.encode(), user.password_hash)",
                    "confidence": 0.88
                },
                {
                    "step_number": 5,
                    "description": "Finally, I see JWT token generation with user claims and expiration",
                    "code_reference": "jwt.encode(payload, SECRET_KEY, algorithm='HS256')",
                    "confidence": 0.90
                }
            ],
            "overall_confidence": 0.91,
            "methodology": "Sequential code flow analysis: signature → validation → database → verification → token generation"
        },
        "difficulty": "medium",
        "tags": ["authentication", "jwt", "security", "bcrypt"],
        "created_at": str(datetime.now())
    }


def create_sample_design_solution():
    """Create a sample design solution"""
    return {
        "id": "sample-design-001",
        "requirement": "Add caching layer for frequently accessed user data to improve API response time",
        "requirement_type": "optimization",
        "solution_overview": """Implement a Redis-based caching layer with the following strategy:
- Cache user profile data with 1-hour TTL
- Use cache-aside pattern for data access
- Implement cache invalidation on user updates
- Add cache hit/miss metrics for monitoring""",
        "detailed_design": """The caching solution will be implemented as follows:

1. **Cache Service Layer**:
   - Create a `CacheService` class that wraps Redis operations
   - Implement get/set/delete operations with proper error handling
   - Add serialization/deserialization for complex objects

2. **Integration Points**:
   - Modify `UserRepository` to check cache before database queries
   - Add cache invalidation in user update/delete operations
   - Implement cache warming for critical user data

3. **Configuration**:
   - Redis connection pool with configurable size
   - TTL configuration per data type
   - Circuit breaker for Redis failures

4. **Monitoring**:
   - Track cache hit/miss ratio
   - Monitor cache memory usage
   - Alert on Redis connection failures""",
        "implementation_steps": [
            "Install redis-py library and configure Redis connection",
            "Create CacheService class with get/set/delete/exists methods",
            "Modify UserRepository.get_by_id() to implement cache-aside pattern",
            "Add cache invalidation in UserRepository.update() and delete()",
            "Implement cache key generation strategy (e.g., 'user:{user_id}')",
            "Add cache metrics collection using Prometheus",
            "Write unit tests for cache operations",
            "Deploy Redis instance and update configuration",
            "Monitor cache performance and adjust TTL values"
        ],
        "architecture_context": {
            "components": [
                {
                    "name": "CacheService",
                    "type": "service",
                    "description": "Redis cache wrapper service",
                    "file_path": "src/services/cache_service.py",
                    "dependencies": ["redis-py"]
                },
                {
                    "name": "UserRepository",
                    "type": "repository",
                    "description": "User data access layer",
                    "file_path": "src/repositories/user_repository.py",
                    "dependencies": ["CacheService", "Database"]
                }
            ],
            "design_patterns": ["Repository Pattern", "Cache-Aside Pattern"],
            "tech_stack": {
                "web_framework": "FastAPI",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            "architecture_type": "RESTful API with caching layer"
        },
        "affected_components": ["UserRepository", "UserService", "CacheService (new)"],
        "code_examples": [
            {
                "file_path": "src/services/cache_service.py",
                "start_line": 1,
                "end_line": 25,
                "code_snippet": """import redis
from typing import Optional, Any
import json

class CacheService:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        '''Get value from cache'''
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None""",
                "language": "python"
            }
        ],
        "reasoning_trace": {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Analyze the requirement: need to improve API response time for user data access",
                    "code_reference": None,
                    "confidence": 0.95
                },
                {
                    "step_number": 2,
                    "description": "Identify that the system uses Repository pattern, making cache integration straightforward",
                    "code_reference": "class UserRepository",
                    "confidence": 0.92
                },
                {
                    "step_number": 3,
                    "description": "Choose Redis as cache solution due to its speed, simplicity, and good Python support",
                    "code_reference": None,
                    "confidence": 0.88
                },
                {
                    "step_number": 4,
                    "description": "Select cache-aside pattern to maintain data consistency and handle cache failures gracefully",
                    "code_reference": None,
                    "confidence": 0.85
                }
            ],
            "overall_confidence": 0.88,
            "methodology": "Requirements analysis → Architecture assessment → Technology selection → Pattern selection → Implementation design"
        },
        "complexity": "medium",
        "estimated_effort": "3-5 days",
        "risks": [
            "Cache stampede on cold start or cache invalidation",
            "Redis failure causing performance degradation",
            "Cache inconsistency if invalidation logic is missed"
        ],
        "tags": ["caching", "redis", "performance", "optimization"],
        "created_at": str(datetime.now())
    }


def print_sample_data():
    """Print and export sample data"""
    
    print("="*70)
    print("📚 Training Data Generation System - Sample Output")
    print("="*70)
    
    # Q&A Example
    print("\n" + "="*70)
    print("📝 SCENARIO 1: Q&A Pair Example")
    print("="*70)
    
    qa = create_sample_qa_pair()
    print(f"\n❓ Question Type: {qa['question_type']}")
    print(f"\n💬 Question:\n   {qa['question']}")
    print(f"\n✅ Answer:\n   {qa['answer'][:200]}...")
    
    print(f"\n🧠 Reasoning Trace ({len(qa['reasoning_trace']['steps'])} steps):")
    for step in qa['reasoning_trace']['steps'][:3]:
        print(f"   {step['step_number']}. {step['description'][:80]}...")
        print(f"      Confidence: {step['confidence']:.2f}")
    
    print(f"\n📊 Overall Confidence: {qa['reasoning_trace']['overall_confidence']:.2f}")
    print(f"🎯 Difficulty: {qa['difficulty']}")
    print(f"🏷️  Tags: {', '.join(qa['tags'])}")
    
    # Design Solution Example
    print("\n" + "="*70)
    print("🏗️  SCENARIO 2: Design Solution Example")
    print("="*70)
    
    solution = create_sample_design_solution()
    print(f"\n📋 Requirement Type: {solution['requirement_type']}")
    print(f"\n📝 Requirement:\n   {solution['requirement']}")
    print(f"\n💡 Solution Overview:\n   {solution['solution_overview'][:200]}...")
    
    print(f"\n📐 Implementation Steps (first 3):")
    for i, step in enumerate(solution['implementation_steps'][:3], 1):
        print(f"   {i}. {step}")
    
    print(f"\n🧠 Design Reasoning ({len(solution['reasoning_trace']['steps'])} steps):")
    for step in solution['reasoning_trace']['steps'][:3]:
        print(f"   {step['step_number']}. {step['description'][:80]}...")
    
    print(f"\n📊 Complexity: {solution['complexity']}")
    print(f"⏱️  Estimated Effort: {solution['estimated_effort']}")
    print(f"⚠️  Risks: {len(solution['risks'])} identified")
    
    # Export as JSON
    print("\n" + "="*70)
    print("💾 Exporting Sample Data")
    print("="*70)
    
    # Create output directory
    output_dir = Path("examples/sample_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export Q&A
    qa_path = output_dir / "sample_qa_pair.json"
    with open(qa_path, 'w', encoding='utf-8') as f:
        json.dump(qa, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Q&A pair exported to: {qa_path}")
    
    # Export Design Solution
    solution_path = output_dir / "sample_design_solution.json"
    with open(solution_path, 'w', encoding='utf-8') as f:
        json.dump(solution, f, indent=2, ensure_ascii=False)
    print(f"✅ Design solution exported to: {solution_path}")
    
    # Export combined
    combined_path = output_dir / "combined_sample.json"
    combined = {
        "metadata": {
            "generated_at": str(datetime.now()),
            "system": "Training Data Generation System",
            "version": "1.0.0"
        },
        "scenario1_qa_example": qa,
        "scenario2_design_example": solution
    }
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f"✅ Combined sample exported to: {combined_path}")
    
    print("\n" + "="*70)
    print("✨ Sample Generation Complete!")
    print("="*70)
    print("\n📁 Check the examples/sample_outputs/ directory for JSON files")
    print("\n📖 For full functionality with real code repositories:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Configure API keys in .env file")
    print("   3. Run: python main.py --repo-path /path/to/repo --scenario both")
    print("\n" + "="*70)


if __name__ == "__main__":
    print_sample_data()
