#!/usr/bin/env python3
"""
Integration tests for workflow features

Tests:
- Library management (save/load papers)
- BibTeX export
- Session history
- Clipboard functionality
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from cite_agent.workflow_integration import WorkflowIntegration


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def workflow(temp_data_dir):
    """Create workflow integration instance with temp directory"""
    return WorkflowIntegration(data_dir=temp_data_dir)


@pytest.fixture
def sample_paper():
    """Sample paper data for testing"""
    return {
        "title": "Attention Is All You Need",
        "authors": [
            {"name": "Ashish Vaswani"},
            {"name": "Noam Shazeer"},
            {"name": "Niki Parmar"}
        ],
        "year": "2017",
        "venue": "NeurIPS",
        "doi": "10.5555/3295222.3295349",
        "citationCount": 50000,
        "abstract": "The dominant sequence transduction models..."
    }


class TestLibraryManagement:
    """Test paper library management features"""

    def test_save_paper_to_library(self, workflow, sample_paper):
        """Test saving a paper to library"""
        user_id = "test_user_001"

        paper_id = workflow.save_paper_to_library(sample_paper, user_id)

        # Verify paper_id is returned
        assert paper_id is not None
        assert len(paper_id) > 0

        # Verify file was created
        papers_dir = Path(workflow.data_dir) / "papers"
        paper_files = list(papers_dir.glob(f"{user_id}_*.json"))
        assert len(paper_files) == 1

        # Verify content
        with open(paper_files[0], 'r') as f:
            saved_data = json.load(f)

        assert saved_data["user_id"] == user_id
        assert saved_data["paper"]["title"] == sample_paper["title"]
        assert "saved_at" in saved_data
        assert "id" in saved_data

    def test_save_multiple_papers(self, workflow, sample_paper):
        """Test saving multiple papers"""
        user_id = "test_user_002"

        # Save 3 papers
        paper_ids = []
        for i in range(3):
            modified_paper = sample_paper.copy()
            modified_paper["title"] = f"Paper {i+1}"
            paper_id = workflow.save_paper_to_library(modified_paper, user_id)
            paper_ids.append(paper_id)

        # Verify all papers saved
        assert len(paper_ids) == 3
        assert len(set(paper_ids)) == 3  # All unique IDs

        # Verify files created
        papers_dir = Path(workflow.data_dir) / "papers"
        paper_files = list(papers_dir.glob(f"{user_id}_*.json"))
        assert len(paper_files) == 3


class TestBibTeXExport:
    """Test BibTeX export functionality"""

    def test_export_single_paper(self, workflow, sample_paper):
        """Test exporting a single paper to BibTeX"""
        papers = [sample_paper]

        bibtex_file = workflow.export_to_bibtex(papers, "test_single.bib")

        # Verify file was created
        assert Path(bibtex_file).exists()

        # Verify content
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "@article{" in content
        assert "Attention Is All You Need" in content
        assert "Ashish Vaswani" in content
        assert "2017" in content
        assert "10.5555/3295222.3295349" in content

    def test_export_multiple_papers(self, workflow):
        """Test exporting multiple papers to BibTeX"""
        papers = [
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}],
                "year": "2019",
                "venue": "NAACL",
                "doi": "10.18653/v1/N19-1423"
            },
            {
                "title": "GPT-3: Language Models are Few-Shot Learners",
                "authors": [{"name": "Tom Brown"}, {"name": "Benjamin Mann"}],
                "year": "2020",
                "venue": "NeurIPS",
                "doi": "10.5555/3495724.3495883"
            }
        ]

        bibtex_file = workflow.export_to_bibtex(papers, "test_multiple.bib")

        # Verify file exists
        assert Path(bibtex_file).exists()

        # Verify content
        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check both papers are in the export
        assert "BERT" in content
        assert "GPT-3" in content
        assert "Jacob Devlin" in content
        assert "Tom Brown" in content
        assert content.count("@article{") == 2

    def test_bibtex_citation_key_format(self, workflow, sample_paper):
        """Test BibTeX citation key generation"""
        papers = [sample_paper]

        bibtex_file = workflow.export_to_bibtex(papers)

        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Citation key should be lastname + year
        assert "@article{vaswani2017" in content.lower()

    def test_export_handles_missing_fields(self, workflow):
        """Test BibTeX export with incomplete paper data"""
        incomplete_paper = {
            "title": "Incomplete Paper",
            "authors": [],  # No authors
            "year": "2023"
            # No DOI, no venue
        }

        papers = [incomplete_paper]

        # Should not crash
        bibtex_file = workflow.export_to_bibtex(papers)

        assert Path(bibtex_file).exists()

        with open(bibtex_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "Incomplete Paper" in content


class TestSessionHistory:
    """Test session history functionality"""

    def test_save_session_history(self, workflow):
        """Test saving session history"""
        user_id = "test_user_003"
        query = "machine learning applications"
        response = {
            "papers": [{"title": "ML Paper 1"}],
            "count": 1
        }

        session_id = workflow.save_session_history(user_id, query, response)

        # Verify session_id returned
        assert session_id is not None
        assert len(session_id) > 0

        # Verify file created
        sessions_dir = Path(workflow.data_dir) / "sessions"
        session_files = list(sessions_dir.glob(f"{user_id}_*.json"))
        assert len(session_files) == 1

        # Verify content
        with open(session_files[0], 'r') as f:
            saved_data = json.load(f)

        assert saved_data["user_id"] == user_id
        assert saved_data["query"] == query
        assert saved_data["response"] == response

    def test_multiple_sessions(self, workflow):
        """Test saving multiple sessions for same user"""
        user_id = "test_user_004"

        # Save 3 sessions
        session_ids = []
        for i in range(3):
            query = f"Query {i+1}"
            response = {"result": f"Result {i+1}"}
            session_id = workflow.save_session_history(user_id, query, response)
            session_ids.append(session_id)

        # Verify all sessions saved
        assert len(session_ids) == 3
        assert len(set(session_ids)) == 3  # All unique

        # Verify files
        sessions_dir = Path(workflow.data_dir) / "sessions"
        session_files = list(sessions_dir.glob(f"{user_id}_*.json"))
        assert len(session_files) == 3


class TestWorkflowDirectories:
    """Test workflow directory structure"""

    def test_directory_creation(self, temp_data_dir):
        """Test that workflow creates required directories"""
        workflow = WorkflowIntegration(data_dir=temp_data_dir)

        # Verify all subdirectories created
        assert (Path(temp_data_dir) / "papers").exists()
        assert (Path(temp_data_dir) / "citations").exists()
        assert (Path(temp_data_dir) / "sessions").exists()

    def test_directory_already_exists(self, temp_data_dir):
        """Test that workflow handles existing directories"""
        # Create directories manually
        (Path(temp_data_dir) / "papers").mkdir(parents=True)
        (Path(temp_data_dir) / "citations").mkdir(parents=True)
        (Path(temp_data_dir) / "sessions").mkdir(parents=True)

        # Should not crash
        workflow = WorkflowIntegration(data_dir=temp_data_dir)

        assert workflow.data_dir == Path(temp_data_dir)


class TestEndToEndWorkflow:
    """Test complete workflow integration"""

    def test_research_workflow(self, workflow):
        """Test a complete research workflow"""
        user_id = "researcher_001"

        # Step 1: Create sample papers
        papers = [
            {
                "title": "Research Paper 1",
                "authors": [{"name": "Author A"}],
                "year": "2023",
                "venue": "Journal A",
                "doi": "10.1234/paper1"
            },
            {
                "title": "Research Paper 2",
                "authors": [{"name": "Author B"}],
                "year": "2023",
                "venue": "Journal B",
                "doi": "10.1234/paper2"
            }
        ]

        # Step 2: Save to library
        paper_ids = []
        for paper in papers:
            paper_id = workflow.save_paper_to_library(paper, user_id)
            paper_ids.append(paper_id)

        assert len(paper_ids) == 2

        # Step 3: Export to BibTeX
        bibtex_file = workflow.export_to_bibtex(papers, "workflow_test.bib")
        assert Path(bibtex_file).exists()

        # Step 4: Save session
        query = "research workflow test"
        response = {"papers": papers, "count": len(papers)}
        session_id = workflow.save_session_history(user_id, query, response)
        assert session_id is not None

        # Step 5: Verify everything saved
        papers_dir = Path(workflow.data_dir) / "papers"
        citations_dir = Path(workflow.data_dir) / "citations"
        sessions_dir = Path(workflow.data_dir) / "sessions"

        assert len(list(papers_dir.glob(f"{user_id}_*.json"))) == 2
        assert len(list(citations_dir.glob("*.bib"))) == 1
        assert len(list(sessions_dir.glob(f"{user_id}_*.json"))) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
