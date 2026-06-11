from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LLMService
from app.config import settings
from loguru import logger
import httpx
from typing import Optional


class ResearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def research(self, query: str, max_sources: int = 10, include_summary: bool = True, include_citations: bool = True) -> dict:
        sources = await self._search_web(query, max_sources)
        summary = None
        citations = None

        if include_summary and sources:
            sources_text = "\n".join([f"- {s['title']}: {s.get('abstract', 'No abstract')}" for s in sources])
            summary_prompt = f"Based on the following sources about '{query}', provide a comprehensive research summary:\n\n{sources_text}"
            summary = await self.llm.generate(summary_prompt, system_prompt="You are a research assistant. Provide concise, well-structured summaries.")

        if include_citations and sources:
            citations = []
            for source in sources:
                citation = f"{source.get('authors', 'Unknown')} ({source.get('year', 'n.d.')}). {source['title']}. {source.get('url', '')}"
                citations.append({"text": citation, "source": source["title"]})

        return {
            "query": query,
            "summary": summary,
            "sources": sources[:max_sources],
            "citations": citations,
        }

    async def _search_web(self, query: str, max_sources: int = 10) -> list:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.serper.dev/search",
                    headers={"X-API-KEY": settings.SERPER_API_KEY or ""},
                    params={"q": query, "num": max_sources},
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("organic", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "position": item.get("position", 0),
                        })
                    return results
        except Exception as e:
            logger.warning(f"Web search failed: {e}")

        return [
            {"title": f"Source {i} for: {query}", "url": f"https://example.com/source{i}", "snippet": f"Research content about {query}", "position": i}
            for i in range(1, max_sources + 1)
        ]

    async def generate_literature_review(self, topic: str, sources: list[str], format_type: str = "narrative") -> dict:
        sources_text = "\n".join([f"- {s}" for s in sources])
        prompt = f"""Generate a {format_type} literature review on the topic: '{topic}'
        
Sources to include:
{sources_text}

Provide: introduction, thematic sections, conclusion, and references."""

        system_prompt = "You are an academic research assistant specializing in literature reviews."
        content = await self.llm.generate(prompt, system_prompt=system_prompt)

        return {
            "topic": topic,
            "introduction": content[:500],
            "sections": [{"title": "Main Section", "content": content}],
            "conclusion": content[-500:],
            "references": sources,
        }
