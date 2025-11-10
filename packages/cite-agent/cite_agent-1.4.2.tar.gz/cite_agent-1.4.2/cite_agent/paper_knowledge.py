#!/usr/bin/env python3
"""
Paper Knowledge Base - Background Understanding

Reads papers quietly, stores knowledge, surfaces only when relevant.

NOT for info-dumping. Agent reads papers to understand them,
then only mentions details when user asks specific questions.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PaperKnowledge:
    """What the agent knows about a paper after reading it"""
    doi: str
    title: str
    read_at: str

    # Quick facts (always available)
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    citation_count: int = 0

    # Deep knowledge (from PDF reading)
    has_full_text: bool = False
    word_count: int = 0
    research_question: Optional[str] = None
    methodology: Optional[str] = None
    key_findings: List[str] = field(default_factory=list)
    limitations: Optional[str] = None

    # For retrieval
    abstract: Optional[str] = None
    full_text_excerpt: Optional[str] = None  # First 500 words


class PaperKnowledgeBase:
    """
    Stores what agent knows about papers

    Agent can query this when user asks questions like:
    - "What did that BERT paper say about fine-tuning?"
    - "Compare the methodologies of the first two papers"
    - "What are the limitations?"

    But doesn't auto-dump unless asked.
    """

    def __init__(self):
        self.papers: Dict[str, PaperKnowledge] = {}  # DOI -> knowledge
        self.last_search_results: List[str] = []  # DOI list from last search

    def add_paper(self, knowledge: PaperKnowledge):
        """Agent learns about a paper"""
        self.papers[knowledge.doi] = knowledge
        logger.debug(f"📚 Agent learned about: {knowledge.title[:50]}...")

    def remember_search(self, paper_dois: List[str]):
        """Remember what papers were in last search (for "first paper", "second paper" references)"""
        self.last_search_results = paper_dois

    def get_paper(self, identifier: str) -> Optional[PaperKnowledge]:
        """Get paper by DOI or reference like "first", "second", etc."""
        # Try DOI first
        if identifier in self.papers:
            return self.papers[identifier]

        # Try positional references
        position_map = {
            "first": 0, "1st": 0,
            "second": 1, "2nd": 1,
            "third": 2, "3rd": 2,
            "fourth": 3, "4th": 3,
            "fifth": 4, "5th": 4,
        }

        if identifier.lower() in position_map:
            idx = position_map[identifier.lower()]
            if idx < len(self.last_search_results):
                doi = self.last_search_results[idx]
                return self.papers.get(doi)

        # Try title matching
        query_lower = identifier.lower()
        for paper in self.papers.values():
            if query_lower in paper.title.lower():
                return paper

        return None

    def get_context_for_question(self, question: str) -> str:
        """
        Get relevant paper context for a question

        Only returns info that's relevant to the question.
        Doesn't dump everything.
        """
        question_lower = question.lower()

        # Check if question is asking about specific papers
        if any(word in question_lower for word in ["first", "second", "third", "paper", "study"]):
            # User asking about specific paper(s)
            relevant_papers = []

            for ref in ["first", "second", "third"]:
                if ref in question_lower:
                    paper = self.get_paper(ref)
                    if paper:
                        relevant_papers.append(paper)

            if relevant_papers:
                context = "Papers the agent has read:\n"
                for paper in relevant_papers:
                    context += f"\n- {paper.title} ({paper.year})\n"
                    if "method" in question_lower and paper.methodology:
                        context += f"  Methodology: {paper.methodology[:200]}...\n"
                    if "finding" in question_lower and paper.key_findings:
                        context += f"  Findings: {'; '.join(paper.key_findings[:2])}\n"
                    if "limitation" in question_lower and paper.limitations:
                        context += f"  Limitations: {paper.limitations[:200]}...\n"

                return context

        # Generic question - return high-level overview only
        if self.papers:
            context = f"Agent has read {len(self.papers)} papers. "
            context += "Ask about specific papers (e.g., 'first paper', 'BERT paper') for details."
            return context

        return ""

    def clear(self):
        """Forget all papers"""
        self.papers.clear()
        self.last_search_results.clear()


# Global knowledge base
_knowledge_base = None


def get_knowledge_base() -> PaperKnowledgeBase:
    """Get global paper knowledge base"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = PaperKnowledgeBase()
    return _knowledge_base


async def quietly_read_papers(agent, papers: List[Dict[str, Any]]) -> int:
    """
    Read papers in background without dumping summaries

    Returns number of papers successfully read
    """
    from .pdf_extractor import PDFExtractor
    from .unpaywall_client import UnpaywallClient

    kb = get_knowledge_base()
    papers_read = 0

    extractor = PDFExtractor()
    unpaywall = UnpaywallClient()

    for paper in papers[:5]:  # Limit to first 5 to avoid slowdown
        doi = paper.get('doi')
        if not doi:
            continue

        # Create basic knowledge
        knowledge = PaperKnowledge(
            doi=doi,
            title=paper.get('title', 'Unknown'),
            read_at=datetime.now().isoformat(),
            authors=[a.get('name', '') for a in paper.get('authors', [])[:3]],
            year=paper.get('year'),
            citation_count=paper.get('citationCount', 0),
            abstract=paper.get('abstract')
        )

        # Try to get PDF and extract
        pdf_url = paper.get('openAccessPdf', {}).get('url')
        if not pdf_url:
            # Try unpaywall
            pdf_url = await unpaywall.get_pdf_url(doi)

        if pdf_url:
            try:
                # Extract PDF content
                extracted = await extractor.extract_from_url(pdf_url)

                if extracted.extraction_quality != "failed":
                    knowledge.has_full_text = True
                    knowledge.word_count = extracted.word_count
                    knowledge.full_text_excerpt = extracted.abstract or extracted.introduction[:500] if extracted.introduction else None

                    # Extract key info without summarizing
                    if extracted.abstract:
                        knowledge.abstract = extracted.abstract

                    papers_read += 1
                    logger.info(f"📖 Read: {knowledge.title[:50]}... ({knowledge.word_count} words)")

            except Exception as e:
                logger.debug(f"Couldn't read PDF for {doi}: {e}")

        # Store knowledge
        kb.add_paper(knowledge)

    if papers_read > 0:
        logger.info(f"📚 Agent quietly read {papers_read}/{len(papers)} papers")

    return papers_read
