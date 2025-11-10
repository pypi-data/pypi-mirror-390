#!/usr/bin/env python3
"""
Paper Deduplication - Remove Duplicate Papers

When searching multiple sources (Semantic Scholar, OpenAlex, PubMed),
the same paper often appears multiple times.

This module provides intelligent deduplication:
- By DOI (most reliable)
- By title similarity (fuzzy matching)
- By arXiv ID
- Merge metadata from multiple sources
"""

import logging
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class PaperIdentifiers:
    """All possible identifiers for a paper"""
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pmid: Optional[str] = None  # PubMed ID
    semantic_scholar_id: Optional[str] = None
    openalex_id: Optional[str] = None
    title: Optional[str] = None


class PaperDeduplicator:
    """
    Intelligent paper deduplication

    Strategy:
    1. Exact DOI match (highest confidence)
    2. arXiv ID match
    3. PubMed ID match
    4. Title fuzzy match (>90% similarity)
    5. Keep best version (most complete metadata)
    """

    def __init__(self, title_similarity_threshold: float = 0.9):
        """
        Initialize deduplicator

        Args:
            title_similarity_threshold: Minimum similarity for title matching (0.0-1.0)
        """
        self.title_threshold = title_similarity_threshold

    def deduplicate(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate list of papers

        Args:
            papers: List of papers from multiple sources

        Returns:
            Deduplicated list with merged metadata
        """
        if not papers:
            return []

        # Group papers by identifiers
        groups = self._group_duplicates(papers)

        # Merge each group into best representation
        deduplicated = []
        for group in groups:
            merged = self._merge_papers(group)
            deduplicated.append(merged)

        original_count = len(papers)
        final_count = len(deduplicated)
        removed = original_count - final_count

        if removed > 0:
            logger.info(f"🔍 Deduplicated: {original_count} → {final_count} papers ({removed} duplicates removed)")

        return deduplicated

    def _group_duplicates(self, papers: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group duplicate papers together

        Args:
            papers: List of papers

        Returns:
            List of groups, where each group contains duplicate papers
        """
        # Track which papers are already grouped
        grouped_indices: Set[int] = set()
        groups: List[List[Dict[str, Any]]] = []

        for i, paper1 in enumerate(papers):
            if i in grouped_indices:
                continue

            # Start new group with this paper
            group = [paper1]
            grouped_indices.add(i)

            # Find all duplicates
            for j, paper2 in enumerate(papers[i+1:], start=i+1):
                if j in grouped_indices:
                    continue

                if self._are_duplicates(paper1, paper2):
                    group.append(paper2)
                    grouped_indices.add(j)

            groups.append(group)

        return groups

    def _are_duplicates(self, paper1: Dict[str, Any], paper2: Dict[str, Any]) -> bool:
        """
        Check if two papers are duplicates

        Args:
            paper1: First paper
            paper2: Second paper

        Returns:
            True if papers are duplicates
        """
        # Extract identifiers
        id1 = self._extract_identifiers(paper1)
        id2 = self._extract_identifiers(paper2)

        # Check DOI match (most reliable)
        if id1.doi and id2.doi:
            # Normalize DOIs (remove https://doi.org/ prefix)
            doi1 = id1.doi.lower().replace("https://doi.org/", "").strip()
            doi2 = id2.doi.lower().replace("https://doi.org/", "").strip()
            if doi1 == doi2:
                logger.debug(f"DOI match: {doi1}")
                return True

        # Check arXiv ID match
        if id1.arxiv_id and id2.arxiv_id:
            if id1.arxiv_id.lower() == id2.arxiv_id.lower():
                logger.debug(f"arXiv match: {id1.arxiv_id}")
                return True

        # Check PubMed ID match
        if id1.pmid and id2.pmid:
            if id1.pmid == id2.pmid:
                logger.debug(f"PMID match: {id1.pmid}")
                return True

        # Check title similarity (fuzzy matching)
        if id1.title and id2.title:
            similarity = self._title_similarity(id1.title, id2.title)
            if similarity >= self.title_threshold:
                logger.debug(f"Title match: {similarity:.2%} - '{id1.title[:50]}...'")
                return True

        return False

    def _extract_identifiers(self, paper: Dict[str, Any]) -> PaperIdentifiers:
        """
        Extract all identifiers from paper

        Args:
            paper: Paper dictionary

        Returns:
            PaperIdentifiers object
        """
        # Handle different API formats
        return PaperIdentifiers(
            doi=paper.get("doi") or paper.get("DOI"),
            arxiv_id=paper.get("arxivId") or paper.get("arxiv_id"),
            pmid=paper.get("pmid") or paper.get("pubmed_id"),
            semantic_scholar_id=paper.get("paperId") or paper.get("semantic_scholar_id"),
            openalex_id=paper.get("id") if isinstance(paper.get("id"), str) and paper.get("id", "").startswith("https://openalex.org/") else None,
            title=paper.get("title")
        )

    def _title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity score (0.0-1.0)
        """
        # Normalize titles
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)

        # Calculate similarity using SequenceMatcher
        return SequenceMatcher(None, t1, t2).ratio()

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison

        Args:
            title: Original title

        Returns:
            Normalized title
        """
        # Convert to lowercase
        normalized = title.lower()

        # Remove common punctuation
        for char in [".", ",", ":", ";", "!", "?", "-", "(", ")", "[", "]", "{", "}"]:
            normalized = normalized.replace(char, " ")

        # Normalize whitespace
        normalized = " ".join(normalized.split())

        return normalized

    def _merge_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge duplicate papers into best representation

        Strategy:
        - Keep most complete metadata
        - Prefer DOI > arXiv > Semantic Scholar
        - Merge citation counts (take max)
        - Merge sources

        Args:
            papers: List of duplicate papers

        Returns:
            Merged paper with best metadata
        """
        if len(papers) == 1:
            return papers[0]

        # Start with paper that has most fields
        merged = max(papers, key=lambda p: len([v for v in p.values() if v is not None]))

        # Merge citation counts (take maximum)
        citation_counts = [p.get("citationCount", 0) for p in papers]
        if citation_counts:
            merged["citationCount"] = max(citation_counts)

        # Merge sources (track which APIs returned this paper)
        sources = set()
        for paper in papers:
            if paper.get("paperId"):  # Semantic Scholar
                sources.add("semantic_scholar")
            if paper.get("id", "").startswith("https://openalex.org/"):
                sources.add("openalex")
            if paper.get("pmid"):
                sources.add("pubmed")

        merged["_sources"] = list(sources)
        merged["_duplicate_count"] = len(papers)

        # Fill in any missing fields from other papers
        for paper in papers:
            for key, value in paper.items():
                if value is not None and merged.get(key) is None:
                    merged[key] = value

        return merged

    def get_deduplication_stats(self, original: List[Dict[str, Any]], deduplicated: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about deduplication

        Args:
            original: Original paper list
            deduplicated: Deduplicated list

        Returns:
            Deduplication statistics
        """
        removed = len(original) - len(deduplicated)
        removal_rate = (removed / len(original) * 100) if original else 0

        # Count by source
        sources = {}
        for paper in deduplicated:
            for source in paper.get("_sources", []):
                sources[source] = sources.get(source, 0) + 1

        return {
            "original_count": len(original),
            "deduplicated_count": len(deduplicated),
            "removed_count": removed,
            "removal_rate": removal_rate,
            "sources": sources
        }


# Global deduplicator instance
_deduplicator = None


def get_deduplicator() -> PaperDeduplicator:
    """Get global deduplicator instance"""
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = PaperDeduplicator()
    return _deduplicator


def deduplicate_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to deduplicate papers

    Args:
        papers: List of papers

    Returns:
        Deduplicated list
    """
    return get_deduplicator().deduplicate(papers)
