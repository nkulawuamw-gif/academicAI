from openai import AsyncOpenAI
from app.config import settings
from loguru import logger
from typing import Optional


class LLMService:
    def __init__(self):
        self.providers = self._build_provider_chain()

    def _build_provider_chain(self):
        preferred = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER != "auto" else None
        chain = []

        if preferred:
            if preferred == "gemini" and settings.GOOGLE_GEMINI_API_KEY:
                chain.append(("gemini", "gemini-2.0-flash", None))
            elif preferred == "groq" and settings.GROQ_API_KEY:
                chain.append(("groq", "llama3-70b-8192", "https://api.groq.com/openai/v1"))
            elif preferred == "openai" and settings.OPENAI_API_KEY:
                chain.append(("openai", "gpt-4o-mini", None))
            elif preferred == "ollama":
                chain.append(("ollama", "llama3.2", "http://localhost:11434/v1"))
        else:
            if settings.GOOGLE_GEMINI_API_KEY:
                chain.append(("gemini", "gemini-2.0-flash", None))
            if settings.GROQ_API_KEY:
                chain.append(("groq", "llama3-70b-8192", "https://api.groq.com/openai/v1"))
            if settings.OPENAI_API_KEY:
                chain.append(("openai", "gpt-4o-mini", None))
            chain.append(("ollama", "llama3.2", "http://localhost:11434/v1"))

        if not chain:
            chain.append(("mock", "mock", None))
        return chain

    def _make_client(self, provider: str, base_url: str = None):
        if provider == "gemini":
            return None
        if provider == "groq":
            return AsyncOpenAI(base_url=base_url, api_key=settings.GROQ_API_KEY)
        if provider == "openai":
            return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if provider == "ollama":
            return AsyncOpenAI(base_url=base_url, api_key="ollama")
        return None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        last_error = None
        for provider, model, base_url in self.providers:
            try:
                if provider == "gemini":
                    return await self._generate_gemini(prompt, system_prompt, max_tokens, temperature)

                client = self._make_client(provider, base_url)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                )
                if stream:
                    return response
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}, trying next...")
                last_error = e

        logger.error(f"All providers failed. Last error: {last_error}")
        if stream:
            raise last_error or Exception("All LLM providers failed")
        return "I apologize, but I'm currently unable to process your request due to a temporary issue with the AI service. Please try again later."

    async def _generate_gemini(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        from google import genai
        client = genai.Client(api_key=settings.GOOGLE_GEMINI_API_KEY)
        contents = prompt
        if system_prompt:
            contents = f"{system_prompt}\n\n{contents}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config={"max_output_tokens": max_tokens, "temperature": temperature},
        )
        return response.text

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        return await self.generate(prompt=prompt, system_prompt=system_prompt, stream=True)

    async def generate_with_functions(self, prompt: str, functions: list, system_prompt: Optional[str] = None):
        for provider, model, base_url in self.providers:
            try:
                if provider == "gemini":
                    logger.warning("Function calling not supported with Gemini provider")
                    text = await self._generate_gemini(prompt, system_prompt)
                    return {"function": "mock", "arguments": text}

                client = self._make_client(provider, base_url)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    functions=functions,
                    function_call="auto",
                )
                return response.choices[0].message
            except Exception as e:
                logger.warning(f"Provider {provider} failed in function call: {e}")

        return {"function": "mock", "arguments": "{}"}
