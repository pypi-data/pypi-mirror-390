#!/usr/bin/env python3
"""
Unpaywall Integration - Find Legal Open Access PDFs
Unpaywall.org provides free, legal access to millions of research papers
"""

import logging
from typing import Optional, Dict, Any
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class UnpaywallClient:
    """
    Client for Unpaywall API - finds legal open access versions of papers

    Unpaywall indexes 30M+ open access papers from:
    - University repositories
    - Author websites
    - Preprint servers (arXiv, bioRxiv)
    - Journal websites

    Usage:
        client = UnpaywallClient(email="your@email.edu")
        pdf_url = await client.get_pdf_url(doi="10.1234/example")
    """

    BASE_URL = "https://api.unpaywall.org/v2"

    def __init__(self, email: str = "research@cite-agent.com"):
        """
        Initialize Unpaywall client

        Args:
            email: Your email (required by Unpaywall API for rate limiting)
        """
        self.email = email
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def get_pdf_url(self, doi: str) -> Optional[str]:
        """
        Get free, legal PDF URL for a paper by DOI

        Args:
            doi: DOI of the paper (e.g., "10.1016/j.cell.2023.01.001")

        Returns:
            PDF URL if open access version exists, None otherwise

        Example:
            >>> client = UnpaywallClient()
            >>> url = await client.get_pdf_url("10.1371/journal.pone.0000001")
            >>> print(url)
            'https://journals.plos.org/plosone/article/file?id=10.1371/...'
        """
        try:
            # Clean DOI
            doi = doi.strip().replace("https://doi.org/", "")

            url = f"{self.BASE_URL}/{doi}"
            params = {"email": self.email}

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 404:
                        logger.debug(f"DOI not found in Unpaywall: {doi}")
                        return None

                    if response.status != 200:
                        logger.warning(f"Unpaywall API error {response.status} for DOI: {doi}")
                        return None

                    data = await response.json()
                    return self._extract_best_pdf_url(data)

        except asyncio.TimeoutError:
            logger.warning(f"Unpaywall timeout for DOI: {doi}")
            return None
        except Exception as e:
            logger.error(f"Unpaywall error for DOI {doi}: {e}")
            return None

    async def get_full_metadata(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get full metadata including all OA locations

        Returns:
            {
                'is_oa': bool,
                'best_oa_location': {...},
                'oa_locations': [...],
                'doi': str,
                'title': str,
                'year': int,
                ...
            }
        """
        try:
            doi = doi.strip().replace("https://doi.org/", "")
            url = f"{self.BASE_URL}/{doi}"
            params = {"email": self.email}

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None
                    return await response.json()

        except Exception as e:
            logger.error(f"Unpaywall metadata error: {e}")
            return None

    def _extract_best_pdf_url(self, unpaywall_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract the best PDF URL from Unpaywall response
        Preference: publisher version > accepted manuscript > submitted manuscript
        """
        if not unpaywall_data.get('is_oa'):
            return None

        # Try best OA location first
        best_location = unpaywall_data.get('best_oa_location')
        if best_location:
            pdf_url = best_location.get('url_for_pdf') or best_location.get('url')
            if pdf_url and pdf_url.endswith('.pdf'):
                return pdf_url

        # Try all OA locations
        oa_locations = unpaywall_data.get('oa_locations', [])
        for location in oa_locations:
            # Prefer publisher or repository versions
            version = location.get('version', '')
            if version in ('publishedVersion', 'acceptedVersion'):
                pdf_url = location.get('url_for_pdf') or location.get('url')
                if pdf_url:
                    return pdf_url

        # Fallback: any PDF URL
        for location in oa_locations:
            pdf_url = location.get('url_for_pdf') or location.get('url')
            if pdf_url:
                return pdf_url

        return None

    async def batch_get_pdfs(self, dois: list[str]) -> Dict[str, Optional[str]]:
        """
        Get PDF URLs for multiple DOIs in parallel

        Args:
            dois: List of DOIs

        Returns:
            Dict mapping DOI -> PDF URL (or None if not available)

        Example:
            >>> client = UnpaywallClient()
            >>> dois = ["10.1371/journal.pone.0000001", "10.1038/s41586-023-06221-2"]
            >>> results = await client.batch_get_pdfs(dois)
            >>> print(results)
            {
                '10.1371/journal.pone.0000001': 'https://...',
                '10.1038/s41586-023-06221-2': None  # Paywalled
            }
        """
        tasks = [self.get_pdf_url(doi) for doi in dois]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for doi, result in zip(dois, results):
            if isinstance(result, Exception):
                output[doi] = None
            else:
                output[doi] = result

        return output

    async def check_availability(self, doi: str) -> Dict[str, Any]:
        """
        Check if paper is available and get status

        Returns:
            {
                'is_available': bool,
                'access_type': str,  # 'open_access' | 'paywalled' | 'unknown'
                'pdf_url': str | None,
                'version': str | None,  # 'publishedVersion' | 'acceptedVersion' | etc
                'license': str | None
            }
        """
        metadata = await self.get_full_metadata(doi)

        if not metadata:
            return {
                'is_available': False,
                'access_type': 'unknown',
                'pdf_url': None,
                'version': None,
                'license': None
            }

        is_oa = metadata.get('is_oa', False)
        best_location = metadata.get('best_oa_location')

        if is_oa and best_location:
            return {
                'is_available': True,
                'access_type': 'open_access',
                'pdf_url': self._extract_best_pdf_url(metadata),
                'version': best_location.get('version'),
                'license': best_location.get('license')
            }
        else:
            return {
                'is_available': False,
                'access_type': 'paywalled',
                'pdf_url': None,
                'version': None,
                'license': None
            }


# Global instance
unpaywall = UnpaywallClient()
