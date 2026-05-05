"""
Islamic AI Agent - LLM Configuration & Training Best Practices
Implements production-grade LLM usage with optimization and best practices
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import lru_cache
import time
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("LLMBestPractices")
logging.basicConfig(level=logging.INFO)

# ============================================================================
# LLM MODEL DEFINITIONS & SELECTION
# ============================================================================

class ModelProvider(Enum):
    """Available LLM providers"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    LOCAL = "local"
    OPEN_SOURCE = "open_source"


@dataclass
class ModelConfig:
    """LLM Model Configuration with best practices"""
    provider: ModelProvider
    model_id: str
    name: str
    context_window: int
    max_output_tokens: int
    cost_per_1k_input: Optional[float] = None
    cost_per_1k_output: Optional[float] = None
    capabilities: List[str] = None
    recommended_temperature: float = 0.7
    recommended_top_p: float = 0.9
    supports_system_prompt: bool = True
    supports_function_calling: bool = False
    is_vision_capable: bool = False
    multilingual: bool = True
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


# Best practice model configurations for Islamic content
MODELS = {
    # GEMINI MODELS
    "gemini-2.5-flash": ModelConfig(
        provider=ModelProvider.GEMINI,
        model_id="gemini-2.5-flash",
        name="Google Gemini 2.5 Flash",
        context_window=1000000,
        max_output_tokens=8000,
        cost_per_1k_input=0.075,
        cost_per_1k_output=0.3,
        capabilities=["text_generation", "reasoning", "multilingual"],
        recommended_temperature=0.3,  # Lower for Islamic scholarship (more deterministic)
        recommended_top_p=0.8,
        is_vision_capable=True,
        multilingual=True
    ),
    
    "gemini-1.5-pro": ModelConfig(
        provider=ModelProvider.GEMINI,
        model_id="gemini-1.5-pro",
        name="Google Gemini 1.5 Pro",
        context_window=2000000,
        max_output_tokens=8000,
        cost_per_1k_input=3.5,
        cost_per_1k_output=10.5,
        capabilities=["text_generation", "reasoning", "advanced_reasoning"],
        recommended_temperature=0.2,  # Low for scholarly accuracy
        recommended_top_p=0.7,
        is_vision_capable=True,
        multilingual=True
    ),
    
    # CLAUDE MODELS
    "claude-3.5-sonnet": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-5-sonnet-20241022",
        name="Claude 3.5 Sonnet",
        context_window=200000,
        max_output_tokens=4096,
        cost_per_1k_input=3.0,
        cost_per_1k_output=15.0,
        capabilities=["text_generation", "reasoning", "code"],
        recommended_temperature=0.3,  # Low for Islamic context
        recommended_top_p=0.8,
        supports_function_calling=True,
        multilingual=True
    ),
    
    "claude-3-opus": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-opus-20240229",
        name="Claude 3 Opus",
        context_window=200000,
        max_output_tokens=4096,
        cost_per_1k_input=15.0,
        cost_per_1k_output=75.0,
        capabilities=["text_generation", "advanced_reasoning", "code"],
        recommended_temperature=0.2,
        recommended_top_p=0.7,
        supports_function_calling=True,
        multilingual=True
    ),
}

# ============================================================================
# MODEL SELECTION & ROUTING
# ============================================================================

class ModelSelector:
    """Intelligently select best model for Islamic content"""
    
    @staticmethod
    def get_best_model_for_query(query: str, context: Optional[str] = None) -> Optional[ModelConfig]:
        """Select optimal model based on query characteristics"""
        
        # Islamic knowledge detection
        islamic_keywords = [
            'quran', 'hadith', 'sunnah', 'fiqh', 'shariah', 'dua',
            'prophet', 'muhammad', 'allah', 'islam', 'salah', 'zakat',
            'hajj', 'fatwa', 'ayah', 'surah', 'tafsir', 'scholar',
            'sahih', 'imam', 'compilation', 'narration', 'authenticity'
        ]
        
        query_lower = query.lower()
        islamic_score = sum(1 for kw in islamic_keywords if kw in query_lower)
        
        # Length detection
        query_length = len(query.split())
        
        # Complexity scoring
        requires_reasoning = any(word in query_lower for word in [
            'why', 'explain', 'difference', 'compare', 'analysis', 'interpretation'
        ])
        
        # Selection logic
        if islamic_score >= 3:
            # Highly Islamic - use accuracy-focused model
            if os.getenv('ANTHROPIC_API_KEY'):
                return MODELS.get("claude-3.5-sonnet")  # Best for Islamic scholarship
        
        if requires_reasoning and query_length > 50:
            # Complex reasoning needed
            if os.getenv('ANTHROPIC_API_KEY'):
                return MODELS.get("claude-3-opus")
            else:
                return MODELS.get("gemini-1.5-pro")
        
        # Default: fast and efficient
        return MODELS.get("gemini-2.5-flash")
    
    @staticmethod
    def is_model_available(model_config: ModelConfig) -> bool:
        """Check if model's API key is configured"""
        if model_config.provider == ModelProvider.CLAUDE:
            return bool(os.getenv('ANTHROPIC_API_KEY'))
        elif model_config.provider == ModelProvider.GEMINI:
            return bool(os.getenv('GOOGLE_API_KEY'))
        return False


# ============================================================================
# PROMPT ENGINEERING FOR ISLAMIC CONTEXT
# ============================================================================

class IslamicPromptTemplate:
    """Best practice prompt templates for Islamic knowledge"""
    
    SYSTEM_PROMPT = """You are Noor, an expert Islamic AI Assistant. Your role is to provide accurate, 
scholarly Islamic knowledge based on authentic sources (Quran, Hadith, Tafsir, Islamic jurisprudence).

IMPORTANT GUIDELINES:
1. Always cite sources (Surah:Verse, Hadith reference, Islamic scholar)
2. Provide accurate, authentic Islamic information only
3. Acknowledge scholarly disagreement when it exists
4. Be respectful of Islamic traditions and beliefs
5. Provide balanced perspectives from mainstream Islamic scholarship
6. Clarify when something is opinion vs. definitive Islamic ruling
7. Always begin responses with "Assalamu Alaikum wa Rahmatullahi wa Barakatuh"
8. Include relevant Quranic verses and Hadith when appropriate
9. Explain complex Islamic concepts clearly for all knowledge levels
10. Use Islamic greeting conventions in responses"""
    
    QA_TEMPLATE = """Based on the provided Islamic sources, answer the following question:

Question: {question}

Sources:
{sources}

Please provide:
1. A clear, scholarly answer citing the sources
2. Relevant Quranic verses or Hadith if applicable
3. Clarification of any scholarly disagreement
4. Practical Islamic guidance where appropriate"""
    
    SYNTHESIS_TEMPLATE = """Synthesize the following Islamic sources into a comprehensive response:

Original Query: {query}

Retrieved Sources:
{sources}

Please create a unified, well-sourced Islamic response that:
1. Synthesizes information from all sources
2. Maintains source attribution
3. Provides scholarly context
4. Explains practical implications"""
    
    VERIFICATION_TEMPLATE = """Verify the authenticity of this Islamic information:

Claim: {claim}
Sources Referenced: {sources}

Please evaluate:
1. Is this claim supported by the sources?
2. What is the scholarly consensus?
3. Are there alternative perspectives?
4. How authenticated is this hadith (if applicable)?"""
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get system prompt for Islamic context"""
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def format_qa_prompt(cls, question: str, sources: str) -> str:
        """Format Q&A prompt"""
        return cls.QA_TEMPLATE.format(question=question, sources=sources)
    
    @classmethod
    def format_synthesis_prompt(cls, query: str, sources: str) -> str:
        """Format synthesis prompt"""
        return cls.SYNTHESIS_TEMPLATE.format(query=query, sources=sources)


# ============================================================================
# LLM PARAMETERS & OPTIMIZATION
# ============================================================================

@dataclass
class InferenceParams:
    """Optimized inference parameters for Islamic content"""
    temperature: float = 0.3  # Lower for scholarly accuracy
    top_p: float = 0.8
    top_k: Optional[int] = 40
    max_tokens: int = 2048
    frequency_penalty: float = 0.0  # No penalty for Islamic terms
    presence_penalty: float = 0.0
    repetition_penalty: Optional[float] = 1.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API parameters"""
        params = {
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens,
        }
        if self.top_k is not None:
            params['top_k'] = self.top_k
        if self.frequency_penalty:
            params['frequency_penalty'] = self.frequency_penalty
        if self.presence_penalty:
            params['presence_penalty'] = self.presence_penalty
        return params


class ParameterOptimizer:
    """Optimize parameters for different Islamic content types"""
    
    @staticmethod
    def get_params_for_content_type(content_type: str) -> InferenceParams:
        """Get optimized parameters based on content type"""
        
        if content_type == "hadith_authentication":
            # Very low temp for accuracy
            return InferenceParams(temperature=0.1, top_p=0.7, max_tokens=1024)
        
        elif content_type == "quranic_interpretation":
            # Moderate temp for scholarly discussion
            return InferenceParams(temperature=0.4, top_p=0.85, max_tokens=2048)
        
        elif content_type == "fiqh_ruling":
            # Low temp for accuracy, respect for differences
            return InferenceParams(temperature=0.2, top_p=0.75, max_tokens=1500)
        
        elif content_type == "scholarly_synthesis":
            # Balanced for comprehensive response
            return InferenceParams(temperature=0.5, top_p=0.9, max_tokens=3000)
        
        elif content_type == "spiritual_guidance":
            # Moderate temp for warmth and accuracy
            return InferenceParams(temperature=0.4, top_p=0.85, max_tokens=2000)
        
        else:
            # Default for general Islamic knowledge
            return InferenceParams(temperature=0.3, top_p=0.8, max_tokens=2048)


# ============================================================================
# RESPONSE VALIDATION & QUALITY
# ============================================================================

class ResponseValidator:
    """Validate LLM responses for Islamic accuracy and quality"""
    
    MIN_RESPONSE_LENGTH = 100
    MAX_RESPONSE_LENGTH = 10000
    REQUIRED_ELEMENTS = ['greeting', 'content', 'source_attribution']
    
    @staticmethod
    def validate(response: str, query: str) -> Dict[str, Any]:
        """Validate response quality"""
        issues = []
        warnings = []
        
        # Length check
        if len(response) < ResponseValidator.MIN_RESPONSE_LENGTH:
            issues.append("Response too short")
        if len(response) > ResponseValidator.MAX_RESPONSE_LENGTH:
            warnings.append("Response very long, may need summarization")
        
        # Islamic greeting check
        if not any(greeting in response for greeting in [
            "Assalamu Alaikum", "As-salamu", "Wa alaikum"
        ]):
            warnings.append("Missing Islamic greeting")
        
        # Source attribution check
        if not any(attr in response.lower() for attr in [
            "quran", "hadith", "sahih", "reference", "source", "scholar", "imam"
        ]):
            warnings.append("May lack proper source attribution")
        
        # Relevance check (simple keyword overlap)
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words) / len(query_words) if query_words else 0
        
        if overlap < 0.2:
            warnings.append(f"Low relevance score: {overlap:.1%}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "length": len(response),
            "relevance_score": overlap
        }


# ============================================================================
# CACHING & PERFORMANCE
# ============================================================================

class ResponseCache:
    """Cache LLM responses for performance"""
    
    def __init__(self, cache_dir: str = "/tmp/llm_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}
    
    def _get_cache_key(self, query: str, model_id: str) -> str:
        """Generate cache key"""
        import hashlib
        key = f"{model_id}:{query}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, query: str, model_id: str) -> Optional[str]:
        """Get cached response"""
        cache_key = self._get_cache_key(query, model_id)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.memory_cache[cache_key] = data['response']
                    return data['response']
            except:
                pass
        
        return None
    
    def set(self, query: str, model_id: str, response: str):
        """Cache response"""
        cache_key = self._get_cache_key(query, model_id)
        
        # Memory cache
        self.memory_cache[cache_key] = response
        
        # Disk cache
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'query': query,
                    'model_id': model_id,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }, f)
        except:
            pass


# ============================================================================
# LLM INTERFACE
# ============================================================================

class IslamicLLMProvider:
    """Unified interface for Islamic LLM operations"""
    
    def __init__(self):
        self.selector = ModelSelector()
        self.prompt_template = IslamicPromptTemplate()
        self.param_optimizer = ParameterOptimizer()
        self.validator = ResponseValidator()
        self.cache = ResponseCache()
    
    def generate(
        self,
        query: str,
        context: Optional[str] = None,
        content_type: str = "general",
        use_cache: bool = True,
        validate: bool = True
    ) -> Dict[str, Any]:
        """Generate response for Islamic query"""
        
        try:
            # Select model
            model_config = self.selector.get_best_model_for_query(query, context)
            if not model_config:
                return {
                    "status": "error",
                    "error": "No suitable model available",
                    "recommendation": "Configure ANTHROPIC_API_KEY or GOOGLE_API_KEY"
                }
            
            # Check cache
            if use_cache:
                cached = self.cache.get(query, model_config.model_id)
                if cached:
                    return {
                        "status": "success",
                        "response": cached,
                        "model": model_config.name,
                        "cached": True
                    }
            
            # Get optimized parameters
            params = self.param_optimizer.get_params_for_content_type(content_type)
            
            # Generate response
            response = self._call_model(model_config, query, context, params)
            
            # Validate
            if validate:
                validation = self.validator.validate(response, query)
                if not validation['valid']:
                    logger.warning(f"Validation issues: {validation['issues']}")
            
            # Cache
            self.cache.set(query, model_config.model_id, response)
            
            return {
                "status": "success",
                "response": response,
                "model": model_config.name,
                "model_id": model_config.model_id,
                "provider": model_config.provider.value,
                "cached": False
            }
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _call_model(
        self,
        model_config: ModelConfig,
        query: str,
        context: Optional[str],
        params: InferenceParams
    ) -> str:
        """Call actual LLM API"""
        
        if model_config.provider == ModelProvider.CLAUDE:
            return self._call_claude(model_config, query, context, params)
        elif model_config.provider == ModelProvider.GEMINI:
            return self._call_gemini(model_config, query, context, params)
        else:
            raise ValueError(f"Unsupported provider: {model_config.provider}")
    
    def _call_claude(
        self,
        model_config: ModelConfig,
        query: str,
        context: Optional[str],
        params: InferenceParams
    ) -> str:
        """Call Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            messages = []
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": query
                })
            
            response = client.messages.create(
                model=model_config.model_id,
                max_tokens=params.max_tokens,
                temperature=params.temperature,
                top_p=params.top_p,
                system=self.prompt_template.get_system_prompt(),
                messages=messages
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def _call_gemini(
        self,
        model_config: ModelConfig,
        query: str,
        context: Optional[str],
        params: InferenceParams
    ) -> str:
        """Call Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            
            client = genai.GenerativeModel(
                model_name=model_config.model_id,
                system_instruction=self.prompt_template.get_system_prompt(),
                generation_config=genai.types.GenerationConfig(
                    temperature=params.temperature,
                    top_p=params.top_p,
                    top_k=params.top_k or 40,
                    max_output_tokens=params.max_tokens
                )
            )
            
            prompt = f"Context: {context}\n\nQuestion: {query}" if context else query
            response = client.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Initialize provider
    provider = IslamicLLMProvider()
    
    # Example 1: General Islamic knowledge
    result1 = provider.generate(
        query="What is the importance of Zakat in Islam?",
        content_type="fiqh_ruling"
    )
    print("Result 1:", json.dumps(result1, indent=2))
    
    # Example 2: With context
    result2 = provider.generate(
        query="Explain this hadith",
        context="'The best among you are those who have the best character' - Sahih Bukhari",
        content_type="hadith_authentication"
    )
    print("Result 2:", json.dumps(result2, indent=2))
    
    # Example 3: Model availability check
    for model_id, config in MODELS.items():
        available = ModelSelector.is_model_available(config)
        print(f"{config.name}: {'✅ Available' if available else '❌ Not configured'}")
