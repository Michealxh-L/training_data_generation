"""
Example script demonstrating training data generation
Uses Flask repository as an example
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import only schema for demonstration (no external dependencies)
try:
    from src.schema import CodeContext, ReasoningTrace, ReasoningStep, QAPair, DesignSolution
except ImportError:
    print("⚠️  Note: Running in demo mode without external dependencies")
    print("   For full functionality, install requirements: pip install -r requirements.txt\n")


def create_sample_qa_pair():
    """Create a sample Q&A pair manually"""
    
    qa_pair = QAPair(
        id="sample-qa-001",
        question="What is the purpose of the authenticate function in the auth module?",
        answer="""The authenticate function validates user credentials and generates a JWT token. 
        It performs the following operations:
        1. Validates the username format
        2. Queries the database for the user record
        3. Verifies the password hash using bcrypt
        4. Generates a JWT token with user claims
        5. Returns the token or raises an authentication error""",
        question_type="code_explanation",
        code_contexts=[
            CodeContext(
                file_path="src/auth.py",
                start_line=10,
                end_line=35,
                code_snippet="""def authenticate(username: str, password: str) -> str:
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
                language="python"
            )
        ],
        reasoning_trace=ReasoningTrace(
            steps=[
                ReasoningStep(
                    step_number=1,
                    description="First, I examine the function signature to understand inputs (username, password) and output (JWT token string)",
                    code_reference="def authenticate(username: str, password: str) -> str",
                    confidence=0.95
                ),
                ReasoningStep(
                    step_number=2,
                    description="Next, I identify the validation logic that checks username format",
                    code_reference="if not username or len(username) < 3",
                    confidence=0.90
                ),
                ReasoningStep(
                    step_number=3,
                    description="Then I see the database query to fetch user record",
                    code_reference="user = db.query(User).filter_by(username=username).first()",
                    confidence=0.92
                ),
                ReasoningStep(
                    step_number=4,
                    description="I observe the password verification using bcrypt",
                    code_reference="bcrypt.checkpw(password.encode(), user.password_hash)",
                    confidence=0.88
                ),
                ReasoningStep(
                    step_number=5,
                    description="Finally, I see JWT token generation with user claims and expiration",
                    code_reference="jwt.encode(payload, SECRET_KEY, algorithm='HS256')",
                    confidence=0.90
                )
            ],
            overall_confidence=0.91,
            methodology="Sequential code flow analysis: signature → validation → database → verification → token generation"
        ),
        difficulty="medium",
        tags=["authentication", "jwt", "security", "bcrypt"],
        created_at=datetime.now()
    )
    
    return qa_pair


def create_sample_design_solution():
    """Create a sample design solution manually"""
    from src.schema import DesignSolution, ArchitectureContext, ArchitectureComponent, RequirementType
    
    solution = DesignSolution(
        id="sample-design-001",
        requirement="Add caching layer for frequently accessed user data to improve API response time",
        requirement_type=RequirementType.OPTIMIZATION,
        solution_overview="""Implement a Redis-based caching layer with the following strategy:
        - Cache user profile data with 1-hour TTL
        - Use cache-aside pattern for data access
        - Implement cache invalidation on user updates
        - Add cache hit/miss metrics for monitoring""",
        detailed_design="""The caching solution will be implemented as follows:

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
        implementation_steps=[
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
        architecture_context=ArchitectureContext(
            components=[
                ArchitectureComponent(
                    name="CacheService",
                    type="service",
                    description="Redis cache wrapper service",
                    file_path="src/services/cache_service.py",
                    dependencies=["redis-py"]
                ),
                ArchitectureComponent(
                    name="UserRepository",
                    type="repository",
                    description="User data access layer",
                    file_path="src/repositories/user_repository.py",
                    dependencies=["CacheService", "Database"]
                ),
                ArchitectureComponent(
                    name="UserService",
                    type="service",
                    description="User business logic",
                    file_path="src/services/user_service.py",
                    dependencies=["UserRepository"]
                )
            ],
            design_patterns=["Repository Pattern", "Cache-Aside Pattern"],
            tech_stack={
                "web_framework": "FastAPI",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            architecture_type="RESTful API with caching layer"
        ),
        affected_components=["UserRepository", "UserService", "CacheService (new)"],
        code_examples=[
            CodeContext(
                file_path="src/services/cache_service.py",
                start_line=1,
                end_line=25,
                code_snippet="""import redis
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
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        '''Set value in cache with TTL'''
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        '''Delete key from cache'''
        self.client.delete(key)""",
                language="python"
            ),
            CodeContext(
                file_path="src/repositories/user_repository.py",
                start_line=20,
                end_line=40,
                code_snippet="""def get_by_id(self, user_id: int) -> Optional[User]:
    '''Get user by ID with caching'''
    cache_key = f"user:{user_id}"
    
    # Try cache first
    cached_user = self.cache_service.get(cache_key)
    if cached_user:
        return User(**cached_user)
    
    # Cache miss - query database
    user = db.query(User).filter_by(id=user_id).first()
    
    # Update cache
    if user:
        user_dict = user.to_dict()
        self.cache_service.set(cache_key, user_dict, ttl=3600)
    
    return user

def update(self, user: User):
    '''Update user and invalidate cache'''
    db.session.commit()
    # Invalidate cache
    cache_key = f"user:{user.id}"
    self.cache_service.delete(cache_key)""",
                language="python"
            )
        ],
        reasoning_trace=ReasoningTrace(
            steps=[
                ReasoningStep(
                    step_number=1,
                    description="Analyze the requirement: need to improve API response time for user data access",
                    code_reference=None,
                    confidence=0.95
                ),
                ReasoningStep(
                    step_number=2,
                    description="Identify that the system uses Repository pattern, making cache integration straightforward",
                    code_reference="class UserRepository",
                    confidence=0.92
                ),
                ReasoningStep(
                    step_number=3,
                    description="Choose Redis as cache solution due to its speed, simplicity, and good Python support",
                    code_reference=None,
                    confidence=0.88
                ),
                ReasoningStep(
                    step_number=4,
                    description="Select cache-aside pattern to maintain data consistency and handle cache failures gracefully",
                    code_reference=None,
                    confidence=0.85
                ),
                ReasoningStep(
                    step_number=5,
                    description="Design cache invalidation strategy to ensure data consistency on updates",
                    code_reference="self.cache_service.delete(cache_key)",
                    confidence=0.87
                ),
                ReasoningStep(
                    step_number=6,
                    description="Add monitoring to track cache effectiveness and system health",
                    code_reference=None,
                    confidence=0.80
                )
            ],
            overall_confidence=0.88,
            methodology="Requirements analysis → Architecture assessment → Technology selection → Pattern selection → Implementation design → Monitoring strategy"
        ),
        complexity="medium",
        estimated_effort="3-5 days",
        risks=[
            "Cache stampede on cold start or cache invalidation",
            "Redis failure causing performance degradation",
            "Cache inconsistency if invalidation logic is missed",
            "Increased system complexity and dependencies"
        ],
        tags=["caching", "redis", "performance", "optimization"],
        created_at=datetime.now()
    )
    
    return solution


def print_sample_data():
    """Print sample data in a formatted way"""
    
    print("="*70)
    print("Sample Training Data Examples")
    print("="*70)
    
    # Q&A Example
    print("\n" + "="*70)
    print("SCENARIO 1: Q&A Pair Example")
    print("="*70)
    
    qa = create_sample_qa_pair()
    print(f"\n📋 Question Type: {qa.question_type}")
    print(f"❓ Question: {qa.question}")
    print(f"\n✅ Answer: {qa.answer}")
    
    print(f"\n🧠 Reasoning Trace ({len(qa.reasoning_trace.steps)} steps):")
    for step in qa.reasoning_trace.steps:
        print(f"   {step.step_number}. {step.description}")
        print(f"      Confidence: {step.confidence:.2f}")
        if step.code_reference:
            print(f"      Code: {step.code_reference[:60]}...")
    
    print(f"\n📊 Overall Confidence: {qa.reasoning_trace.overall_confidence:.2f}")
    print(f"🎯 Difficulty: {qa.difficulty}")
    print(f"🏷️  Tags: {', '.join(qa.tags)}")
    
    # Design Solution Example
    print("\n" + "="*70)
    print("SCENARIO 2: Design Solution Example")
    print("="*70)
    
    solution = create_sample_design_solution()
    print(f"\n📋 Requirement Type: {solution.requirement_type}")
    print(f"📝 Requirement: {solution.requirement}")
    print(f"\n💡 Solution Overview:\n{solution.solution_overview}")
    
    print(f"\n📐 Implementation Steps:")
    for i, step in enumerate(solution.implementation_steps[:5], 1):
        print(f"   {i}. {step}")
    
    print(f"\n🧠 Design Reasoning ({len(solution.reasoning_trace.steps)} steps):")
    for step in solution.reasoning_trace.steps[:3]:
        print(f"   {step.step_number}. {step.description}")
        print(f"      Confidence: {step.confidence:.2f}")
    
    print(f"\n📊 Complexity: {solution.complexity}")
    print(f"⏱️  Estimated Effort: {solution.estimated_effort}")
    print(f"⚠️  Risks: {len(solution.risks)} identified")
    
    # Export as JSON
    print("\n" + "="*70)
    print("JSON Export Examples")
    print("="*70)
    
    # Create output directory
    output_dir = Path("examples/sample_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export Q&A
    qa_json = qa.model_dump()
    qa_path = output_dir / "sample_qa_pair.json"
    with open(qa_path, 'w', encoding='utf-8') as f:
        json.dump(qa_json, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ Q&A pair exported to: {qa_path}")
    
    # Export Design Solution
    solution_json = solution.model_dump()
    solution_path = output_dir / "sample_design_solution.json"
    with open(solution_path, 'w', encoding='utf-8') as f:
        json.dump(solution_json, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ Design solution exported to: {solution_path}")
    
    print("\n" + "="*70)
    print("✅ Sample data generation complete!")
    print("="*70)


if __name__ == "__main__":
    print_sample_data()
