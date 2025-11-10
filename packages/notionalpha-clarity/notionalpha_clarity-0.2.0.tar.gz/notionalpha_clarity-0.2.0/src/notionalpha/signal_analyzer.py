"""
Signal Analyzer
Feature: 002-agent-architecture-implementation (T201-T205)

Lightweight LLM-based signal analysis for automatic enrichment
Uses OpenAI gpt-4o-mini for cost-effective signal intelligence
"""

import json
import re
from typing import Dict, List, Literal, Optional, TypedDict
import httpx


class SignalData(TypedDict, total=False):
    """Signal metadata captured from LLM call"""
    prompt: str
    response: str
    model: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    processing_time_ms: Optional[int]


class SignalAnalysis(TypedDict):
    """Enriched signal analysis result"""
    context_classification: str
    intent_analysis: str
    complexity_score: int  # 1-10 scale
    estimated_value_category: Literal['high', 'medium', 'low']
    query_type: Literal['simple', 'moderate', 'complex']


class SignalAnalyzerConfig(TypedDict, total=False):
    """Configuration for SignalAnalyzer"""
    openai_api_key: Optional[str]  # OpenAI API key for gpt-4o-mini analysis
    llm_endpoint: Optional[str]  # Custom LLM endpoint (optional, defaults to OpenAI)
    enabled: bool  # Enable/disable signal enrichment (default: False)


class SignalAnalyzer:
    """
    SignalAnalyzer

    Analyzes LLM signals to extract intelligence for agents:
    - Context classification (customer_support, code_generation, etc.)
    - Complexity scoring (1-10 scale)
    - Intent analysis
    - Value estimation

    Example:
        >>> analyzer = SignalAnalyzer({
        ...     'openai_api_key': os.environ['OPENAI_API_KEY'],
        ...     'enabled': True
        ... })
        >>>
        >>> signal = {
        ...     'prompt': 'Write a function to calculate fibonacci',
        ...     'response': 'Here is a fibonacci function...',
        ...     'model': 'gpt-4o',
        ...     'input_tokens': 50,
        ...     'output_tokens': 150
        ... }
        >>>
        >>> analysis = await analyzer.analyze(signal)
        >>> # {
        >>> #   'context_classification': 'code_generation',
        >>> #   'intent_analysis': 'User wants to generate a fibonacci function',
        >>> #   'complexity_score': 3,
        >>> #   'estimated_value_category': 'medium',
        >>> #   'query_type': 'simple'
        >>> # }
    """

    def __init__(self, config: Optional[SignalAnalyzerConfig] = None):
        config = config or {}
        self.config = config
        self.enabled = config.get('enabled', False)
        self.openai_api_key = config.get('openai_api_key')
        self.llm_endpoint = config.get('llm_endpoint', 'https://api.openai.com/v1/chat/completions')

    async def analyze(self, signal: SignalData) -> SignalAnalysis:
        """
        Analyze signal and return enriched metadata

        If enrichment is disabled, returns basic classification only
        """
        # If enrichment disabled, return basic analysis
        if not self.enabled or not self.openai_api_key:
            return self._basic_analysis(signal)

        try:
            # Use LLM to analyze signal with structured output
            analysis = await self._llm_analysis(signal)
            return analysis
        except Exception as e:
            print(f'Signal enrichment failed, falling back to basic analysis: {e}')
            return self._basic_analysis(signal)

    def _analyze_context(self, prompt: str, response: str) -> str:
        """T202: Analyze context classification from prompt/response"""
        prompt_lower = prompt.lower()

        # Pattern matching for common contexts
        if 'support' in prompt_lower or 'help' in prompt_lower or 'issue' in prompt_lower:
            return 'customer_support'
        if 'code' in prompt_lower or 'function' in prompt_lower or 'debug' in prompt_lower:
            return 'code_generation'
        if 'write' in prompt_lower or 'create' in prompt_lower or 'draft' in prompt_lower:
            return 'content_creation'
        if 'lead' in prompt_lower or 'sales' in prompt_lower or 'marketing' in prompt_lower:
            return 'sales_marketing'
        if 'analyze' in prompt_lower or 'data' in prompt_lower or 'report' in prompt_lower:
            return 'data_analysis'
        if 'summarize' in prompt_lower or 'summary' in prompt_lower:
            return 'summarization'
        if 'translate' in prompt_lower:
            return 'translation'

        return 'general_query'

    def _calculate_complexity(self, signal: SignalData) -> int:
        """T203: Calculate complexity score (1-10) based on prompt characteristics"""
        score = 1
        prompt = signal['prompt']

        # Prompt length (longer = more complex)
        prompt_length = len(prompt)
        if prompt_length > 2000:
            score += 3
        elif prompt_length > 1000:
            score += 2
        elif prompt_length > 500:
            score += 1

        # Technical terminology detection
        technical_terms = [
            'algorithm', 'function', 'class', 'api', 'database', 'sql', 'optimization',
            'architecture', 'microservice', 'kubernetes', 'docker', 'async', 'promise',
            'authentication', 'authorization', 'encryption', 'security', 'compliance'
        ]
        prompt_lower = prompt.lower()
        tech_term_count = sum(1 for term in technical_terms if term in prompt_lower)
        score += min(tech_term_count, 3)

        # Multi-step reasoning indicators
        if 'step by step' in prompt or ('first' in prompt and 'then' in prompt):
            score += 2

        # Token ratio (output/input suggests complexity)
        input_tokens = signal.get('input_tokens')
        output_tokens = signal.get('output_tokens')
        if input_tokens and output_tokens:
            ratio = output_tokens / input_tokens
            if ratio > 5:
                score += 2
            elif ratio > 3:
                score += 1

        # Clamp to 1-10 range
        return max(1, min(10, score))

    def _extract_intent(self, prompt: str) -> str:
        """T204: Extract user intent from prompt"""
        prompt_lower = prompt.lower()

        if prompt_lower.startswith('how to') or prompt_lower.startswith('how do i'):
            return 'User wants to learn how to do something'
        if prompt_lower.startswith('what is') or prompt_lower.startswith('what are'):
            return 'User wants to understand a concept'
        if prompt_lower.startswith('write') or prompt_lower.startswith('create') or prompt_lower.startswith('generate'):
            return 'User wants to create content'
        if prompt_lower.startswith('fix') or prompt_lower.startswith('debug') or 'error' in prompt_lower:
            return 'User wants to resolve an issue'
        if prompt_lower.startswith('explain') or prompt_lower.startswith('describe'):
            return 'User wants an explanation'
        if prompt_lower.startswith('summarize') or prompt_lower.startswith('tldr'):
            return 'User wants a summary'

        # Extract first sentence as intent
        first_sentence = re.split(r'[.!?]', prompt)[0]
        return f'User wants to: {first_sentence[:100]}'

    def _estimate_value(self, context: str, complexity: int) -> Literal['high', 'medium', 'low']:
        """T205: Estimate value category based on context and complexity"""
        # High-value contexts
        high_value_contexts = ['sales_marketing', 'code_generation', 'data_analysis']
        if context in high_value_contexts and complexity >= 5:
            return 'high'

        # Medium-value contexts
        medium_value_contexts = ['customer_support', 'content_creation']
        if context in medium_value_contexts or complexity >= 6:
            return 'medium'

        # Everything else is low-medium value
        return 'low'

    def _basic_analysis(self, signal: SignalData) -> SignalAnalysis:
        """Basic analysis without LLM (rule-based)"""
        prompt = signal['prompt']
        response = signal['response']

        context = self._analyze_context(prompt, response)
        complexity = self._calculate_complexity(signal)
        intent = self._extract_intent(prompt)
        value = self._estimate_value(context, complexity)

        query_type: Literal['simple', 'moderate', 'complex']
        if complexity <= 3:
            query_type = 'simple'
        elif complexity <= 6:
            query_type = 'moderate'
        else:
            query_type = 'complex'

        return {
            'context_classification': context,
            'intent_analysis': intent,
            'complexity_score': complexity,
            'estimated_value_category': value,
            'query_type': query_type
        }

    async def _llm_analysis(self, signal: SignalData) -> SignalAnalysis:
        """LLM-based analysis using gpt-4o-mini"""
        if not self.openai_api_key:
            raise ValueError('OpenAI API key required for LLM analysis')

        system_prompt = """You are a signal intelligence analyzer. Analyze LLM interactions to classify context, complexity, intent, and value.

Return JSON with this exact structure:
{
  "contextClassification": "customer_support|code_generation|content_creation|sales_marketing|data_analysis|summarization|translation|general_query",
  "intentAnalysis": "Brief description of what user wants to accomplish",
  "complexityScore": 1-10 (integer),
  "estimatedValueCategory": "high|medium|low",
  "queryType": "simple|moderate|complex"
}

Guidelines:
- contextClassification: Choose the most relevant category
- complexityScore: 1-3=simple, 4-6=moderate, 7-10=complex
- estimatedValueCategory: high=generates revenue/saves significant time, medium=moderate impact, low=informational
- queryType: Based on complexity score"""

        user_prompt = f"""Analyze this LLM interaction:

**Prompt:** {signal['prompt'][:1000]}
**Response:** {signal['response'][:1000]}
**Model:** {signal.get('model', 'unknown')}
**Tokens:** {signal.get('input_tokens', 0)} input, {signal.get('output_tokens', 0)} output

Provide structured analysis."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.llm_endpoint,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.openai_api_key}'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 500,
                    'response_format': {'type': 'json_object'}
                },
                timeout=30.0
            )

        if response.status_code != 200:
            raise Exception(f'LLM analysis failed: {response.text}')

        data = response.json()
        content = data['choices'][0]['message']['content']
        analysis = json.loads(content)

        return {
            'context_classification': analysis.get('contextClassification', 'general_query'),
            'intent_analysis': analysis.get('intentAnalysis', 'Unknown intent'),
            'complexity_score': max(1, min(10, analysis.get('complexityScore', 1))),
            'estimated_value_category': analysis.get('estimatedValueCategory', 'low'),
            'query_type': analysis.get('queryType', 'simple')
        }
