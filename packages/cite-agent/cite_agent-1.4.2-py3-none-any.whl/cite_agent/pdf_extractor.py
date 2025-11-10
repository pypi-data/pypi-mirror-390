#!/usr/bin/env python3
"""
PDF Extraction Service - KILLER FEATURE
Extracts full text from academic papers so you don't have to read them!
"""

import io
import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import PyPDF2
    import pdfplumber
    import fitz  # PyMuPDF
    PDF_LIBRARIES_AVAILABLE = True
except ImportError:
    PDF_LIBRARIES_AVAILABLE = False

import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedPaper:
    """Fully extracted paper content"""
    title: Optional[str] = None
    abstract: Optional[str] = None
    introduction: Optional[str] = None
    methodology: Optional[str] = None
    results: Optional[str] = None
    discussion: Optional[str] = None
    conclusion: Optional[str] = None
    references: Optional[List[str]] = None
    full_text: Optional[str] = None
    tables: Optional[List[Dict[str, Any]]] = None
    figures_count: int = 0
    page_count: int = 0
    word_count: int = 0
    extraction_method: str = "unknown"
    extraction_quality: str = "unknown"  # high, medium, low
    error_message: Optional[str] = None


class PDFExtractor:
    """Extract and analyze full text from academic PDFs"""

    def __init__(self):
        if not PDF_LIBRARIES_AVAILABLE:
            logger.warning("PDF libraries not installed. Install: pip install pypdf2 pdfplumber pymupdf")

        self.max_file_size_mb = 50  # Don't download PDFs larger than 50MB
        self.timeout_seconds = 30

    async def extract_from_url(self, pdf_url: str) -> ExtractedPaper:
        """
        Download and extract full text from PDF URL

        Args:
            pdf_url: Direct link to PDF file

        Returns:
            ExtractedPaper with full content
        """
        if not PDF_LIBRARIES_AVAILABLE:
            return ExtractedPaper(
                error_message="PDF extraction libraries not installed",
                extraction_quality="low"
            )

        try:
            # Download PDF
            logger.info(f"Downloading PDF from {pdf_url}")
            response = requests.get(
                pdf_url,
                timeout=self.timeout_seconds,
                headers={'User-Agent': 'Mozilla/5.0 (Research Bot)'},
                stream=True
            )
            response.raise_for_status()

            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_file_size_mb * 1024 * 1024:
                return ExtractedPaper(
                    error_message=f"PDF too large ({int(content_length)/(1024*1024):.1f}MB > {self.max_file_size_mb}MB)",
                    extraction_quality="low"
                )

            pdf_bytes = response.content

            # Try extraction methods in order of quality
            # 1. PyMuPDF (best quality, fastest)
            extracted = self._extract_with_pymupdf(pdf_bytes)
            if extracted.extraction_quality == "high":
                return extracted

            # 2. pdfplumber (good for tables and layout)
            extracted = self._extract_with_pdfplumber(pdf_bytes)
            if extracted.extraction_quality in ("high", "medium"):
                return extracted

            # 3. PyPDF2 (basic fallback)
            extracted = self._extract_with_pypdf2(pdf_bytes)
            return extracted

        except requests.Timeout:
            return ExtractedPaper(
                error_message="PDF download timeout",
                extraction_quality="low"
            )
        except requests.RequestException as e:
            return ExtractedPaper(
                error_message=f"PDF download failed: {str(e)}",
                extraction_quality="low"
            )
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ExtractedPaper(
                error_message=f"Extraction error: {str(e)}",
                extraction_quality="low"
            )

    def _extract_with_pymupdf(self, pdf_bytes: bytes) -> ExtractedPaper:
        """Extract using PyMuPDF (fitz) - fastest and most accurate"""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            full_text = ""
            for page in doc:
                full_text += page.get_text()

            # Parse sections
            sections = self._parse_sections(full_text)

            # Count stats
            word_count = len(full_text.split())
            page_count = len(doc)

            # Extract tables (basic)
            tables = []
            for page in doc:
                tabs = page.find_tables()
                if tabs:
                    for tab in tabs:
                        tables.append({
                            'page': page.number + 1,
                            'rows': len(tab.extract()),
                            'data': tab.extract()[:5]  # First 5 rows only
                        })

            doc.close()

            quality = "high" if word_count > 500 else "medium"

            return ExtractedPaper(
                full_text=full_text,
                title=sections.get('title'),
                abstract=sections.get('abstract'),
                introduction=sections.get('introduction'),
                methodology=sections.get('methodology'),
                results=sections.get('results'),
                discussion=sections.get('discussion'),
                conclusion=sections.get('conclusion'),
                references=sections.get('references'),
                tables=tables if tables else None,
                page_count=page_count,
                word_count=word_count,
                extraction_method="pymupdf",
                extraction_quality=quality
            )

        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")
            return ExtractedPaper(
                error_message=f"PyMuPDF failed: {str(e)}",
                extraction_quality="low"
            )

    def _extract_with_pdfplumber(self, pdf_bytes: bytes) -> ExtractedPaper:
        """Extract using pdfplumber - good for tables"""
        try:
            pdf = pdfplumber.open(io.BytesIO(pdf_bytes))

            full_text = ""
            tables = []

            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        tables.append({
                            'page': page_num,
                            'rows': len(table),
                            'data': table[:5]  # First 5 rows
                        })

            pdf.close()

            # Parse sections
            sections = self._parse_sections(full_text)
            word_count = len(full_text.split())

            quality = "high" if word_count > 500 else "medium"

            return ExtractedPaper(
                full_text=full_text,
                title=sections.get('title'),
                abstract=sections.get('abstract'),
                introduction=sections.get('introduction'),
                methodology=sections.get('methodology'),
                results=sections.get('results'),
                discussion=sections.get('discussion'),
                conclusion=sections.get('conclusion'),
                references=sections.get('references'),
                tables=tables if tables else None,
                page_count=len(pdf.pages),
                word_count=word_count,
                extraction_method="pdfplumber",
                extraction_quality=quality
            )

        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            return ExtractedPaper(
                error_message=f"pdfplumber failed: {str(e)}",
                extraction_quality="low"
            )

    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> ExtractedPaper:
        """Extract using PyPDF2 - basic fallback"""
        try:
            pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            # Parse sections
            sections = self._parse_sections(full_text)
            word_count = len(full_text.split())

            quality = "medium" if word_count > 500 else "low"

            return ExtractedPaper(
                full_text=full_text,
                title=sections.get('title'),
                abstract=sections.get('abstract'),
                introduction=sections.get('introduction'),
                methodology=sections.get('methodology'),
                results=sections.get('results'),
                discussion=sections.get('discussion'),
                conclusion=sections.get('conclusion'),
                references=sections.get('references'),
                page_count=len(pdf.pages),
                word_count=word_count,
                extraction_method="pypdf2",
                extraction_quality=quality
            )

        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")
            return ExtractedPaper(
                error_message=f"PyPDF2 failed: {str(e)}",
                extraction_quality="low"
            )

    def _parse_sections(self, full_text: str) -> Dict[str, Optional[str]]:
        """
        Parse academic paper sections from full text
        Uses common section headers to split the paper
        """
        sections = {}

        # Common section patterns (case-insensitive)
        patterns = {
            'abstract': r'(?i)\bABSTRACT\b',
            'introduction': r'(?i)\b(INTRODUCTION|1\.\s*INTRODUCTION)\b',
            'methodology': r'(?i)\b(METHODOLOGY|METHODS|MATERIALS AND METHODS|2\.\s*METHOD)\b',
            'results': r'(?i)\b(RESULTS|FINDINGS|3\.\s*RESULTS)\b',
            'discussion': r'(?i)\b(DISCUSSION|4\.\s*DISCUSSION)\b',
            'conclusion': r'(?i)\b(CONCLUSION|CONCLUSIONS|5\.\s*CONCLUSION)\b',
            'references': r'(?i)\b(REFERENCES|BIBLIOGRAPHY)\b'
        }

        # Find all section positions
        section_positions = {}
        for section_name, pattern in patterns.items():
            match = re.search(pattern, full_text)
            if match:
                section_positions[section_name] = match.start()

        # Sort sections by position
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])

        # Extract text between sections
        for i, (section_name, start_pos) in enumerate(sorted_sections):
            # Get end position (start of next section, or end of text)
            if i + 1 < len(sorted_sections):
                end_pos = sorted_sections[i + 1][1]
            else:
                end_pos = len(full_text)

            # Extract section text
            section_text = full_text[start_pos:end_pos].strip()

            # Remove section header from text
            section_text = re.sub(patterns[section_name], '', section_text, count=1).strip()

            # Limit length (first 3000 chars per section)
            if len(section_text) > 3000:
                section_text = section_text[:3000] + "... [truncated]"

            sections[section_name] = section_text if section_text else None

        # Extract title (usually first few lines)
        title_match = re.search(r'^(.+?)(?:\n\n|\n[A-Z])', full_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 200:
                title = title[:200]
            sections['title'] = title

        # Extract references (last section, list of citations)
        if 'references' in sections and sections['references']:
            ref_text = sections['references']
            # Split by newlines and filter
            refs = [line.strip() for line in ref_text.split('\n') if line.strip()]
            # Keep only lines that look like citations (have year and authors)
            citations = [ref for ref in refs if re.search(r'\b(19|20)\d{2}\b', ref)]
            sections['references'] = citations[:20]  # First 20 refs

        return sections


# Global instance
pdf_extractor = PDFExtractor()
