"""
LLM provider module for Alprina CLI.
Handles connections to various LLM services (OpenAI, Anthropic, Ollama).
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
from loguru import logger


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMClient:
    """
    Unified interface for different LLM providers.
    """

    def __init__(self, provider: str = None):
        """
        Initialize LLM client.

        Args:
            provider: Provider name (openai, anthropic, ollama)
        """
        self.provider = provider or os.getenv("ALPRINA_LLM_PROVIDER", "openai")
        self.api_key = None
        self.client = None

        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.provider == LLMProvider.OPENAI.value:
                self._init_openai()
            elif self.provider == LLMProvider.ANTHROPIC.value:
                self._init_anthropic()
            elif self.provider == LLMProvider.OLLAMA.value:
                self._init_ollama()
            else:
                logger.warning(f"Unknown provider: {self.provider}, falling back to OpenAI")
                self._init_openai()
        except ImportError as e:
            logger.error(f"Failed to initialize {self.provider}: {e}")
            logger.info("Install with: pip install openai anthropic ollama")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("OPENAI_API_KEY not set. LLM features will be limited.")
                return

            self.client = OpenAI(api_key=self.api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"Initialized OpenAI client with model: {self.model}")

        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")

    def _init_anthropic(self):
        """Initialize Anthropic Claude client."""
        try:
            from anthropic import Anthropic

            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                logger.warning("ANTHROPIC_API_KEY not set.")
                return

            self.client = Anthropic(api_key=self.api_key)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            logger.info(f"Initialized Anthropic client with model: {self.model}")

        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")

    def _init_ollama(self):
        """Initialize Ollama local client."""
        try:
            import ollama

            self.client = ollama
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
            logger.info(f"Initialized Ollama client with model: {self.model}")

        except ImportError:
            logger.error("Ollama package not installed. Install with: pip install ollama")

    def analyze_code(self, code: str, filename: str, task: str = "security-scan") -> Dict[str, Any]:
        """
        Analyze code using LLM for security issues.

        Args:
            code: Source code to analyze
            filename: Name of the file
            task: Analysis task type

        Returns:
            Dict with findings
        """
        if not self.client:
            return self._mock_analysis(code, filename)

        prompt = self._build_security_prompt(code, filename, task)

        try:
            if self.provider == LLMProvider.OPENAI.value:
                return self._analyze_with_openai(prompt)
            elif self.provider == LLMProvider.ANTHROPIC.value:
                return self._analyze_with_anthropic(prompt)
            elif self.provider == LLMProvider.OLLAMA.value:
                return self._analyze_with_ollama(prompt)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._mock_analysis(code, filename)

    def _build_security_prompt(self, code: str, filename: str, task: str) -> str:
        """Build security analysis prompt."""
        return f"""You are a security expert analyzing code for vulnerabilities.

File: {filename}
Task: {task}

Analyze this code for security issues:

```
{code[:2000]}  # Limit to first 2000 chars
```

Identify:
1. Hardcoded secrets (API keys, passwords, tokens)
2. SQL injection vulnerabilities
3. XSS vulnerabilities
4. Insecure configurations
5. Outdated dependencies
6. Authentication issues
7. Authorization flaws
8. Data exposure risks

For each finding, provide:
- Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Type (e.g., "Hardcoded Secret", "SQL Injection")
- Description (brief explanation)
- Line number (if applicable)
- Recommendation (how to fix)

Return ONLY a JSON array of findings, no other text:
[
  {{
    "severity": "HIGH",
    "type": "Hardcoded Secret",
    "description": "API key found in code",
    "line": 10,
    "recommendation": "Move to environment variable"
  }}
]

If no issues found, return: []
"""

    def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze with OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a security analysis expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        return self._parse_llm_response(content)

    def _analyze_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Analyze with Anthropic Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.content[0].text
        return self._parse_llm_response(content)

    def _analyze_with_ollama(self, prompt: str) -> Dict[str, Any]:
        """Analyze with Ollama local model."""
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a security analysis expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response['message']['content']
        return self._parse_llm_response(content)

    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured findings."""
        import json
        import re

        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)

            # Try direct JSON parse
            findings = json.loads(content)

            return {
                "findings": findings if isinstance(findings, list) else [findings],
                "raw_response": content
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")

            # Fallback: extract findings from text
            return {
                "findings": self._extract_findings_from_text(content),
                "raw_response": content
            }

    def _extract_findings_from_text(self, text: str) -> list:
        """Extract findings from unstructured text."""
        findings = []

        # Simple pattern matching for common issues
        if "password" in text.lower() or "api_key" in text.lower() or "secret" in text.lower():
            findings.append({
                "severity": "HIGH",
                "type": "Potential Hardcoded Secret",
                "description": "LLM detected potential secrets in code",
                "recommendation": "Review manually and move to secure storage"
            })

        if "sql" in text.lower() and "injection" in text.lower():
            findings.append({
                "severity": "CRITICAL",
                "type": "SQL Injection Risk",
                "description": "LLM detected SQL injection vulnerability",
                "recommendation": "Use parameterized queries"
            })

        return findings

    def _mock_analysis(self, code: str, filename: str) -> Dict[str, Any]:
        """Fallback mock analysis when LLM is unavailable."""
        findings = []

        # Simple pattern matching
        if "password" in code.lower() or "api_key" in code.lower():
            findings.append({
                "severity": "HIGH",
                "type": "Hardcoded Secret",
                "description": "Potential hardcoded secret detected",
                "recommendation": "Move secrets to environment variables"
            })

        if "debug" in code.lower() and "true" in code.lower():
            findings.append({
                "severity": "MEDIUM",
                "type": "Debug Mode",
                "description": "Debug mode appears to be enabled",
                "recommendation": "Disable debug mode in production"
            })

        return {"findings": findings, "mock": True}

    def chat(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Chat with LLM (non-streaming).

        Args:
            messages: List of message dicts with role and content
            system_prompt: System prompt to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Returns:
            Assistant's response text
        """
        if not self.client:
            return "LLM client not initialized. Please set API keys."

        try:
            if self.provider == LLMProvider.OPENAI.value:
                return self._chat_openai(messages, system_prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.ANTHROPIC.value:
                return self._chat_anthropic(messages, system_prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.OLLAMA.value:
                return self._chat_ollama(messages, system_prompt, max_tokens, temperature)
            else:
                return "Unsupported provider for chat."
        except Exception as e:
            logger.error(f"Chat failed: {e}", exc_info=True)
            return f"Error: {e}"

    def chat_streaming(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Chat with LLM (streaming).

        Args:
            messages: List of message dicts with role and content
            system_prompt: System prompt to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Yields:
            Text chunks as they arrive
        """
        if not self.client:
            yield "LLM client not initialized. Please set API keys."
            return

        try:
            if self.provider == LLMProvider.OPENAI.value:
                yield from self._chat_streaming_openai(messages, system_prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.ANTHROPIC.value:
                yield from self._chat_streaming_anthropic(messages, system_prompt, max_tokens, temperature)
            elif self.provider == LLMProvider.OLLAMA.value:
                yield from self._chat_streaming_ollama(messages, system_prompt, max_tokens, temperature)
            else:
                yield "Unsupported provider for streaming chat."
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}", exc_info=True)
            yield f"\n\nError: {e}"

    def _chat_openai(self, messages, system_prompt, max_tokens, temperature) -> str:
        """Chat with OpenAI (non-streaming)."""
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def _chat_anthropic(self, messages, system_prompt, max_tokens, temperature) -> str:
        """Chat with Anthropic (non-streaming)."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _chat_ollama(self, messages, system_prompt, max_tokens, temperature) -> str:
        """Chat with Ollama (non-streaming)."""
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        response = self.client.chat(
            model=self.model,
            messages=chat_messages
        )
        return response['message']['content']

    def _chat_streaming_openai(self, messages, system_prompt, max_tokens, temperature):
        """Chat with OpenAI (streaming)."""
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _chat_streaming_anthropic(self, messages, system_prompt, max_tokens, temperature):
        """Chat with Anthropic (streaming)."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text

    def _chat_streaming_ollama(self, messages, system_prompt, max_tokens, temperature):
        """Chat with Ollama (streaming)."""
        chat_messages = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        stream = self.client.chat(
            model=self.model,
            messages=chat_messages,
            stream=True
        )

        for chunk in stream:
            if chunk['message']['content']:
                yield chunk['message']['content']


# Global LLM client instance
_llm_client = None


def get_llm_client(model: Optional[str] = None) -> LLMClient:
    """
    Get or create global LLM client.

    Args:
        model: Optional model override

    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    if model and hasattr(_llm_client, 'model'):
        _llm_client.model = model
    return _llm_client
