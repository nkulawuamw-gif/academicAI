from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService
from loguru import logger


class WritingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def generate_writing(
        self,
        prompt: str,
        type: str = "essay",
        length: str = "medium",
        tone: str = "academic",
        additional_instructions: str = None,
    ) -> dict:
        length_map = {"short": 500, "medium": 1500, "long": 3000}
        target_words = length_map.get(length, 1000)

        system_prompt = f"""You are an academic writing assistant. Generate a {type} with:
- Tone: {tone}
- Target length: ~{target_words} words
- Follow academic writing standards
- Use proper structure and citations"""

        full_prompt = prompt
        if additional_instructions:
            full_prompt += f"\n\nAdditional instructions: {additional_instructions}"

        content = await self.llm.generate(full_prompt, system_prompt=system_prompt, max_tokens=4096)
        word_count = len(content.split())

        title = content.split("\n")[0] if content else type.capitalize()
        title = title.replace("#", "").strip()

        return {
            "title": title,
            "content": content,
            "word_count": word_count,
            "type": type,
        }

    async def generate_outline(self, topic: str, sections: int = 5, depth: str = "detailed") -> dict:
        system_prompt = f"Generate a {depth} outline for an academic paper on the given topic with {sections} main sections."
        prompt = f"Topic: {topic}\n\nGenerate a comprehensive outline with subsections and key points for each section."

        content = await self.llm.generate(prompt, system_prompt=system_prompt)
        outline_items = [
            {"title": f"Section {i+1}", "content": f"Content for section {i+1} of {topic}", "subsections": []}
            for i in range(sections)
        ]

        return {
            "topic": topic,
            "outline": outline_items,
            "suggested_sources": [f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}"],
        }
