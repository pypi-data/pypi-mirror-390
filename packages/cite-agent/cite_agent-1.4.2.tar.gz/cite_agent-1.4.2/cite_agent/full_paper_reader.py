#!/usr/bin/env python3
"""
Full Paper Reader Integration
Combines search + PDF extraction + summarization into one killer feature
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


async def read_full_papers_workflow(
    agent,  # EnhancedNocturnalAgent instance
    query: str,
    limit: int = 5,
    summarize: bool = True
) -> Dict[str, Any]:
    """
    🔥 KILLER FEATURE: Search, download, and READ full academic papers

    This is the game-changer - skip reading papers yourself!

    Args:
        agent: Agent instance with search capabilities
        query: Search query
        limit: Number of papers to find and read
        summarize: If True, summarize each paper (methodology, findings, etc.)

    Returns:
        {
            'query': str,
            'papers_found': int,
            'papers_read': int,
            'papers': [
                {
                    'title': str,
                    'doi': str,
                    'pdf_url': str,
                    'summary': {
                        'research_question': str,
                        'methodology': str,
                        'key_findings': [str, ...],
                        'limitations': str,
                        'implications': str
                    },
                    'full_text_available': bool,
                    'word_count': int
                },
                ...
            ],
            'synthesis': str  # Overall summary across all papers
        }

    Example:
        >>> result = await read_full_papers_workflow(agent, "ESG investing performance", limit=3)
        >>> print(result['synthesis'])
        "Based on 3 papers:
        - All 3 found positive ESG-performance correlation
        - Effect sizes range from +1.2% to +4.1% annually
        - Methodological gap: most studies focus on large-cap stocks"
    """
    logger.info(f"🔥 FULL PAPER READING: {query} (limit={limit})")

    # Import the services
    try:
        from .pdf_extractor import pdf_extractor
        from .unpaywall_client import unpaywall
        from .paper_summarizer import PaperSummarizer, PaperSummary
    except ImportError as e:
        logger.error(f"PDF reading libraries not installed: {e}")
        return {
            'error': 'PDF reading not available. Install: pip install pypdf2 pdfplumber pymupdf',
            'papers_found': 0,
            'papers_read': 0
        }

    # Step 1: Search for papers
    search_results = await agent.search_academic_papers(query, limit=limit)
    papers_data = search_results.get('results', [])

    if not papers_data:
        return {
            'query': query,
            'papers_found': 0,
            'papers_read': 0,
            'papers': [],
            'message': 'No papers found'
        }

    logger.info(f"Found {len(papers_data)} papers, attempting to read full text...")

    # Step 2: For each paper, try to get PDF and extract
    papers_output = []
    successfully_read = 0

    for paper in papers_data:
        title = paper.get('title', 'Unknown')
        doi = paper.get('doi')
        pdf_url = paper.get('pdf_url')
        authors = paper.get('authors', [])
        year = paper.get('year')

        logger.info(f"Processing: {title}")

        paper_result = {
            'title': title,
            'doi': doi,
            'authors': [a.get('name') if isinstance(a, dict) else a for a in authors],
            'year': year,
            'pdf_url': pdf_url,
            'full_text_available': False
        }

        # Try to get PDF URL if not provided
        if not pdf_url and doi:
            logger.info(f"  No PDF URL, checking Unpaywall for DOI: {doi}")
            pdf_url = await unpaywall.get_pdf_url(doi)
            if pdf_url:
                logger.info(f"  ✅ Found open access PDF via Unpaywall")
                paper_result['pdf_url'] = pdf_url
                paper_result['source'] = 'unpaywall'

        # Try to extract full text
        if pdf_url:
            logger.info(f"  Extracting PDF from: {pdf_url[:80]}...")
            try:
                extracted = await pdf_extractor.extract_from_url(pdf_url)

                if extracted.extraction_quality in ('high', 'medium'):
                    logger.info(f"  ✅ Successfully extracted {extracted.word_count} words")
                    successfully_read += 1
                    paper_result['full_text_available'] = True
                    paper_result['word_count'] = extracted.word_count
                    paper_result['page_count'] = extracted.page_count
                    paper_result['extraction_quality'] = extracted.extraction_quality

                    # Summarize if requested
                    if summarize and agent.client:
                        logger.info(f"  Summarizing paper...")
                        summarizer = PaperSummarizer(agent.client)
                        summary = await summarizer.summarize_paper(
                            extracted,
                            doi=doi,
                            authors=paper_result['authors'],
                            year=year
                        )
                        paper_result['summary'] = {
                            'research_question': summary.research_question,
                            'methodology': summary.methodology,
                            'key_findings': summary.key_findings,
                            'limitations': summary.limitations,
                            'implications': summary.implications,
                            'confidence': summary.confidence
                        }
                    else:
                        # Basic extraction without LLM
                        paper_result['sections'] = {
                            'abstract': extracted.abstract,
                            'introduction': extracted.introduction[:500] if extracted.introduction else None,
                            'methodology': extracted.methodology[:500] if extracted.methodology else None,
                            'results': extracted.results[:500] if extracted.results else None,
                            'conclusion': extracted.conclusion[:500] if extracted.conclusion else None
                        }
                else:
                    logger.warning(f"  ⚠️ Low quality extraction: {extracted.error_message}")
                    paper_result['extraction_error'] = extracted.error_message

            except Exception as e:
                logger.error(f"  ❌ PDF extraction failed: {e}")
                paper_result['extraction_error'] = str(e)
        else:
            logger.info(f"  ⚠️ No PDF URL available (paywalled)")
            paper_result['note'] = 'Paywalled - no open access version found'

        papers_output.append(paper_result)

    # Step 3: Generate synthesis across all successfully read papers
    synthesis = _synthesize_multiple_papers(papers_output, query)

    result = {
        'query': query,
        'papers_found': len(papers_data),
        'papers_read': successfully_read,
        'papers': papers_output,
        'synthesis': synthesis,
        'success_rate': f"{successfully_read}/{len(papers_data)} ({100*successfully_read//len(papers_data) if papers_data else 0}%)"
    }

    logger.info(f"✅ COMPLETE: Read {successfully_read}/{len(papers_data)} papers successfully")

    return result


def _synthesize_multiple_papers(papers: List[Dict[str, Any]], query: str) -> str:
    """Generate synthesis across multiple papers"""
    readable_papers = [p for p in papers if p.get('full_text_available')]

    if not readable_papers:
        return "No papers could be read (all paywalled or extraction failed)"

    synthesis_parts = []
    synthesis_parts.append(f"Based on {len(readable_papers)} papers analyzed:\n")

    # Collect all findings
    all_findings = []
    all_methodologies = []

    for paper in readable_papers:
        summary = paper.get('summary', {})
        if summary:
            findings = summary.get('key_findings', [])
            if findings:
                all_findings.extend(findings)

            methodology = summary.get('methodology')
            if methodology:
                all_methodologies.append(methodology)

    # Methodology overview
    if all_methodologies:
        synthesis_parts.append(f"METHODOLOGIES USED:")
        for i, method in enumerate(all_methodologies[:3], 1):
            synthesis_parts.append(f"  {i}. {method}")
        synthesis_parts.append("")

    # Key findings
    if all_findings:
        synthesis_parts.append(f"KEY FINDINGS ACROSS PAPERS:")
        for i, finding in enumerate(all_findings[:5], 1):
            synthesis_parts.append(f"  • {finding}")
        synthesis_parts.append("")

    # Success rate
    total = len(papers)
    success = len(readable_papers)
    synthesis_parts.append(f"Coverage: {success}/{total} papers successfully analyzed")

    return "\n".join(synthesis_parts)
