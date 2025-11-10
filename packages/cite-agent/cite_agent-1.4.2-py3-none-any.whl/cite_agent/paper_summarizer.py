#!/usr/bin/env python3
"""
Paper Summarization Service - The Magic Happens Here!
Turns full papers into structured summaries so you don't have to read them
"""

import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .pdf_extractor import ExtractedPaper

logger = logging.getLogger(__name__)


@dataclass
class PaperSummary:
    """Structured summary of an academic paper"""
    # Core info
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None

    # Summary sections
    research_question: Optional[str] = None
    methodology: Optional[str] = None
    key_findings: Optional[List[str]] = None
    limitations: Optional[str] = None
    implications: Optional[str] = None

    # Additional
    keywords: Optional[List[str]] = None
    citations_to: Optional[List[str]] = None  # Papers this cites
    tables_summary: Optional[List[Dict[str, Any]]] = None

    # Meta
    word_count: int = 0
    confidence: str = "medium"  # high, medium, low
    extraction_quality: str = "unknown"

    def to_markdown(self) -> str:
        """Convert to readable markdown format"""
        lines = []

        # Header
        if self.title:
            lines.append(f"# {self.title}")
        if self.authors:
            lines.append(f"**Authors:** {', '.join(self.authors[:3])}" +
                        (" et al." if len(self.authors) > 3 else ""))
        if self.year:
            lines.append(f"**Year:** {self.year}")
        if self.doi:
            lines.append(f"**DOI:** {self.doi}")

        lines.append("")

        # Research Question
        if self.research_question:
            lines.append("## Research Question")
            lines.append(self.research_question)
            lines.append("")

        # Methodology
        if self.methodology:
            lines.append("## Methodology")
            lines.append(self.methodology)
            lines.append("")

        # Key Findings
        if self.key_findings:
            lines.append("## Key Findings")
            for i, finding in enumerate(self.key_findings, 1):
                lines.append(f"{i}. {finding}")
            lines.append("")

        # Limitations
        if self.limitations:
            lines.append("## Limitations")
            lines.append(self.limitations)
            lines.append("")

        # Implications
        if self.implications:
            lines.append("## Implications")
            lines.append(self.implications)
            lines.append("")

        return "\n".join(lines)


class PaperSummarizer:
    """
    Summarize academic papers using LLM
    Extracts methodology, findings, and implications
    """

    def __init__(self, llm_client=None):
        """
        Initialize summarizer

        Args:
            llm_client: Optional LLM client (Groq, OpenAI, Anthropic)
                       If None, uses rule-based extraction
        """
        self.llm_client = llm_client
        self.use_llm = llm_client is not None

    async def summarize_paper(
        self,
        extracted: ExtractedPaper,
        doi: Optional[str] = None,
        authors: Optional[List[str]] = None,
        year: Optional[int] = None
    ) -> PaperSummary:
        """
        Summarize an extracted paper

        Args:
            extracted: ExtractedPaper from PDF extraction
            doi: DOI of paper
            authors: List of author names
            year: Publication year

        Returns:
            PaperSummary with structured information
        """
        if self.use_llm and self.llm_client:
            return await self._summarize_with_llm(extracted, doi, authors, year)
        else:
            return self._summarize_rule_based(extracted, doi, authors, year)

    async def _summarize_with_llm(
        self,
        extracted: ExtractedPaper,
        doi: Optional[str],
        authors: Optional[List[str]],
        year: Optional[int]
    ) -> PaperSummary:
        """Summarize using LLM (best quality)"""

        # Build prompt
        prompt = self._build_summary_prompt(extracted)

        try:
            # Call LLM
            response = await self._call_llm(prompt)

            # If LLM failed or unavailable, fall back to rule-based
            if response is None:
                logger.info("LLM not available, using rule-based extraction")
                return self._summarize_rule_based(extracted, doi, authors, year)

            # Parse structured response
            summary = self._parse_llm_response(response)

            # Add metadata
            summary.doi = doi
            summary.authors = authors
            summary.year = year
            summary.word_count = extracted.word_count
            summary.extraction_quality = extracted.extraction_quality
            summary.confidence = "high" if extracted.extraction_quality == "high" else "medium"

            return summary

        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            # Fallback to rule-based
            return self._summarize_rule_based(extracted, doi, authors, year)

    def _summarize_rule_based(
        self,
        extracted: ExtractedPaper,
        doi: Optional[str],
        authors: Optional[List[str]],
        year: Optional[int]
    ) -> PaperSummary:
        """Summarize using rules (fallback, no LLM needed)"""

        summary = PaperSummary(
            doi=doi,
            title=extracted.title,
            authors=authors,
            year=year,
            word_count=extracted.word_count,
            extraction_quality=extracted.extraction_quality,
            confidence="medium" if extracted.extraction_quality == "high" else "low"
        )

        # Extract research question from introduction
        if extracted.introduction:
            summary.research_question = self._extract_research_question(extracted.introduction)
        elif extracted.abstract:
            summary.research_question = self._extract_research_question(extracted.abstract)

        # Methodology
        if extracted.methodology:
            summary.methodology = self._truncate(extracted.methodology, 500)

        # Key findings from results
        if extracted.results:
            summary.key_findings = self._extract_key_findings(extracted.results)

        # Limitations from discussion
        if extracted.discussion:
            summary.limitations = self._extract_limitations(extracted.discussion)

        # Implications from conclusion
        if extracted.conclusion:
            summary.implications = self._truncate(extracted.conclusion, 500)

        # Tables
        if extracted.tables:
            summary.tables_summary = [
                {
                    'page': t.get('page'),
                    'rows': t.get('rows'),
                    'preview': str(t.get('data', [])[:2])
                }
                for t in extracted.tables[:3]  # First 3 tables
            ]

        return summary

    def _build_summary_prompt(self, extracted: ExtractedPaper) -> str:
        """Build prompt for LLM summarization"""

        sections = []

        if extracted.abstract:
            sections.append(f"ABSTRACT:\n{extracted.abstract[:2000]}")

        if extracted.introduction:
            sections.append(f"INTRODUCTION:\n{extracted.introduction[:2000]}")

        if extracted.methodology:
            sections.append(f"METHODOLOGY:\n{extracted.methodology[:2000]}")

        if extracted.results:
            sections.append(f"RESULTS:\n{extracted.results[:2000]}")

        if extracted.conclusion:
            sections.append(f"CONCLUSION:\n{extracted.conclusion[:1000]}")

        paper_text = "\n\n".join(sections)

        prompt = f"""Analyze this academic paper and extract key information.

{paper_text}

Provide a structured summary in JSON format:
{{
    "research_question": "What research question does this paper address?",
    "methodology": "What methods did they use? (2-3 sentences)",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "limitations": "What are the main limitations? (1-2 sentences)",
    "implications": "What are the implications/conclusions? (2-3 sentences)",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Be concise. Extract ONLY what's explicitly stated, do not infer."""

        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM client (Groq, OpenAI, Anthropic, etc.)"""
        if self.llm_client is None:
            logger.warning("No LLM client available, will use rule-based extraction")
            return None

        try:
            # Try Groq/OpenAI-compatible API
            if hasattr(self.llm_client, 'chat'):
                response = await self.llm_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a research assistant that summarizes academic papers. Be concise and accurate."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1000
                )
                return response.choices[0].message.content

            # Try Anthropic API
            elif hasattr(self.llm_client, 'messages'):
                response = await self.llm_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": f"You are a research assistant that summarizes academic papers. Be concise and accurate.\n\n{prompt}"}
                    ]
                )
                return response.content[0].text

            else:
                logger.warning(f"LLM client type not recognized: {type(self.llm_client).__name__}")
                logger.info("Falling back to rule-based extraction")
                return None

        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            logger.info("Falling back to rule-based extraction")
            return None

    def _parse_llm_response(self, response: str) -> PaperSummary:
        """Parse structured JSON from LLM"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]

            data = json.loads(json_str)

            return PaperSummary(
                research_question=data.get('research_question'),
                methodology=data.get('methodology'),
                key_findings=data.get('key_findings', []),
                limitations=data.get('limitations'),
                implications=data.get('implications'),
                keywords=data.get('keywords', []),
                confidence="high"
            )
        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return PaperSummary(confidence="low")

    def _extract_research_question(self, text: str) -> Optional[str]:
        """Extract research question from introduction/abstract"""
        # Look for common patterns
        patterns = [
            r"[Ww]e (?:investigate|examine|explore|study|analyze) (.+?)\.",
            r"[Tt]his (?:paper|study|research) (?:investigates|examines|explores) (.+?)\.",
            r"[Tt]he (?:aim|goal|objective|purpose) (?:is|was) to (.+?)\.",
            r"[Rr]esearch question[:\s]+(.+?)\.",
        ]

        import re
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()[:200]

        # Fallback: first sentence of abstract/intro
        sentences = text.split('.')
        if sentences:
            return sentences[0].strip()[:200]

        return None

    def _extract_key_findings(self, results_text: str) -> List[str]:
        """Extract key findings from results section"""
        findings = []

        # Look for sentences with statistical significance or strong claims
        sentences = results_text.split('.')

        import re
        for sentence in sentences:
            # Look for p-values, significant, correlation, etc.
            if any(keyword in sentence.lower() for keyword in [
                'significant', 'p <', 'p=', 'correlation', 'showed', 'demonstrated',
                'increased', 'decreased', 'higher', 'lower'
            ]):
                finding = sentence.strip()
                if 50 < len(finding) < 300:  # Reasonable length
                    findings.append(finding)
                    if len(findings) >= 5:
                        break

        return findings[:5] if findings else None

    def _extract_limitations(self, discussion_text: str) -> Optional[str]:
        """Extract limitations from discussion"""
        import re

        # Look for limitations section
        patterns = [
            r"[Ll]imitations?[:\s]+(.+?)(?:\.|$)",
            r"[Aa] limitation (?:is|was) (.+?)\.",
        ]

        for pattern in patterns:
            match = re.search(pattern, discussion_text)
            if match:
                return match.group(1).strip()[:300]

        return None

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."

    async def batch_summarize(
        self,
        papers: List[tuple[ExtractedPaper, str, List[str], int]]
    ) -> List[PaperSummary]:
        """
        Summarize multiple papers in parallel

        Args:
            papers: List of (extracted, doi, authors, year) tuples

        Returns:
            List of PaperSummary objects
        """
        import asyncio

        tasks = [
            self.summarize_paper(ext, doi, authors, year)
            for ext, doi, authors, year in papers
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)
