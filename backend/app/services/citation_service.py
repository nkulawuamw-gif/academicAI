import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.citation import Citation, CitationStyle
from app.services.llm_service import LLMService
from app.core.exceptions import NotFoundException
from loguru import logger
from typing import Optional


class CitationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def generate_citation(self, style: str, source_text: str) -> Citation:
        style_guide = {
            "apa": "APA 7th Edition: Author, A. A. (Year). Title of work. Publisher. DOI",
            "mla": "MLA: Author Last, First. Title of Work. Publisher, Year.",
            "harvard": "Harvard: Author(s) Last name, Initial(s). (Year). Title. Edition. Place of publication: Publisher.",
            "chicago": "Chicago: Author Last, First. Year. Title. Place: Publisher.",
            "ieee": "IEEE: A. Author, 'Title,' Publisher, Year.",
        }

        system_prompt = f"You are a citation generator. Generate a {style.upper()} citation from the provided source information. Format: {style_guide.get(style, '')}"
        prompt = f"Generate a {style.upper()} citation for:\n\n{source_text}"

        citation_text = await self.llm.generate(prompt, system_prompt=system_prompt, max_tokens=500)

        return citation_text

    async def create_citation(self, user_id: uuid.UUID, style: str, title: str, authors: str = None,
                               year: int = None, **kwargs) -> Citation:
        citation_data = {
            "style": style, "title": title, "authors": authors, "year": year,
            **{k: v for k, v in kwargs.items() if v is not None},
        }

        citation = Citation(
            id=uuid.uuid4(),
            user_id=user_id,
            style=CitationStyle(style),
            title=title,
            authors=authors,
            year=year,
            citation_text=self._format_citation_text(style, citation_data),
            created_at=datetime.now(timezone.utc),
        )

        for key, value in citation_data.items():
            if hasattr(citation, key):
                setattr(citation, key, value)

        self.db.add(citation)
        await self.db.flush()
        return citation

    async def get_citations(self, user_id: uuid.UUID, page: int = 1, per_page: int = 20) -> dict:
        total_query = select(func.count()).select_from(Citation).where(Citation.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()

        query = (
            select(Citation)
            .where(Citation.user_id == user_id)
            .order_by(desc(Citation.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        citations = result.scalars().all()

        return {
            "citations": [
                {
                    "id": str(c.id),
                    "style": c.style.value,
                    "citation_text": c.citation_text,
                    "title": c.title,
                    "authors": c.authors,
                    "year": c.year,
                    "created_at": c.created_at,
                }
                for c in citations
            ],
            "total": total,
        }

    def _format_citation_text(self, style: str, data: dict) -> str:
        if style == "apa":
            return f"{data.get('authors', 'Author')} ({data.get('year', 'n.d.')}). {data['title']}. {data.get('publisher', 'Publisher')}."
        elif style == "mla":
            return f"{data.get('authors', 'Author')}. \"{data['title']}.\" {data.get('publisher', 'Publisher')}, {data.get('year', 'n.d.')}."
        elif style == "harvard":
            return f"{data.get('authors', 'Author')} ({data.get('year', 'n.d.')}). {data['title']}. {data.get('publisher', 'Publisher')}."
        elif style == "chicago":
            return f"{data.get('authors', 'Author')}. {data.get('year', 'n.d.')}. {data['title']}. {data.get('publisher', 'Publisher')}."
        elif style == "ieee":
            return f"{data.get('authors', 'A. Author')}, \"{data['title']},\" {data.get('publisher', 'Publisher')}, {data.get('year', 'n.d.')}."
        return data['title']
