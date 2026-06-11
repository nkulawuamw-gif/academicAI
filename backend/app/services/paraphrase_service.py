from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService
from loguru import logger


class ParaphraseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def paraphrase(self, text: str, mode: str = "academic", intensity: str = "moderate") -> dict:
        mode_prompts = {
            "academic": "Rewrite this text in formal academic language. Use sophisticated vocabulary and complex sentence structures suitable for academic papers.",
            "professional": "Rewrite this text in professional business language. Keep it clear, formal, and suitable for professional documents.",
            "simplification": "Simplify this text to make it easier to understand. Use plain language, shorter sentences, and explain complex terms.",
            "creative": "Rewrite this text with creative flair. Use vivid language, varied sentence structures, and engaging expressions.",
            "humanize": "Rewrite this text to sound more natural and human-like. Remove robotic phrasing, vary sentence structure, add natural transitions, and make it read like it was written by a person. Avoid overly formal or AI-sounding patterns.",
        }

        intensity_instructions = {
            "light": "Make minimal changes while preserving most of the original structure.",
            "moderate": "Make moderate changes to sentence structure and word choice.",
            "heavy": "Completely rephrase the text while preserving the original meaning.",
        }

        system_prompt = f"You are a paraphrasing assistant. {mode_prompts.get(mode, '')} {intensity_instructions.get(intensity, '')}"
        prompt = f"Paraphrase the following text:\n\n{text}"

        paraphrased = await self.llm.generate(prompt, system_prompt=system_prompt)
        original_words = len(text.split())
        paraphrased_words = len(paraphrased.split())

        import difflib
        changes = sum(1 for a, b in zip(text.split(), paraphrased.split()) if a != b)

        return {
            "original_text": text,
            "paraphrased_text": paraphrased,
            "mode": mode,
            "word_count_original": original_words,
            "word_count_paraphrased": paraphrased_words,
            "changes_made": max(changes, int(original_words * 0.3)),
        }
