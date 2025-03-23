"""Service for interacting with arXiv API and processing papers.

This module includes functionalities for searching, downloading,
and processing arXiv papers including PDF download and text extraction.

Dependencies:
    - arxiv: For interfacing with the arXiv API.
    - fitz (PyMuPDF): For PDF text extraction.
"""

import json
import os
import re

import arxiv
import fitz  # PyMuPDF

from .llm_service import LLMService


class ArxivService:
    """Service for interacting with arXiv API and processing papers."""

    @staticmethod
    def search(query: str, max_results: int = 10) -> str:
        """Search the arXiv database for papers matching the given query.

        Args:
            query: The search query string.
            max_results: Maximum number of search results to return.
            
        Returns:
            JSON-formatted string of search results.
        """
        arxiv_client = arxiv.Client()
        search = arxiv.Search(
            query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
        )

        results = arxiv_client.results(search)
        results_list = []

        for paper in results:
            paper_info = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "summary": paper.summary,
                "published": paper.published.isoformat(),
                "primary_category": paper.primary_category,
                "categories": paper.categories,
                "entry_id": paper.entry_id.split("/")[-1],
                "pdf_url": paper.pdf_url,
            }
            results_list.append(paper_info)

        return json.dumps(results_list, indent=4)
    
    """
    This method is used as a tool in the LangGraph workflow (if env variable USE_SUMMARIZATION is set to True)
    """
    @staticmethod
    def summarize_papers(entry_ids_to_summarize: list[str], chat_summarization: str, user_question: str) -> str:
        """Fetches arXiv papers, downloads and extracts content from PDFs, and summarizes the content."""

        # Fetch paper content for each entry_id
        summarizations = {}
        for entry_id in entry_ids_to_summarize:
            content = ArxivService.fetch_paper_content_as_str(entry_id)

            # Summarize the content
            try:
                paper_summary = LLMService.invoke_summarization_chain(
                    chat_summarization, user_question, content
                )
            except Exception:
                print(f"Error summarizing paper {entry_id}")
                paper_summary = "Error summarizing paper content"

            summarizations[f"Paper_{entry_id}"] = paper_summary

            print(f"Summarized content for {entry_id}")

        return json.dumps(summarizations, ensure_ascii=False, indent=2)
    

    @staticmethod
    def fetch_paper_content(entry_id: str) -> str:
        """Fetches an arXiv paper, downloads PDF, extracts text, and returns data as JSON.

        Args:
            entry_id: The arXiv paper ID.
            
        Returns:
            JSON string containing paper title, authors, abstract, and extracted content.
        """
        # Fetch arXiv metadata
        search = arxiv.Search(id_list=[entry_id])
        paper = next(search.results(), None)

        if not paper:
            return json.dumps({"error": "Paper not found"})

        title = paper.title
        authors = [author.name for author in paper.authors]
        abstract = paper.summary
        file_pointer = f"#pdf/{entry_id}"

        # Download PDF if not already available
        assets_dir = os.path.join(os.getcwd(), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        file_name = f"{entry_id}.pdf"
        file_path = os.path.join(assets_dir, file_name)
        
        if not os.path.exists(file_path):
            paper.download_pdf(filename=file_path)

        try:
            content = ArxivService._extract_text_from_pdf(file_path)

            paper_data = {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "content": content,
                "file_pointer": file_pointer,
            }

            return json.dumps(paper_data, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Error processing PDF: {str(e)}"})
        

    @staticmethod
    def fetch_paper_content_as_str(entry_id: str) -> str:
        """Fetches an arXiv paper, downloads and extracts content from PDF if not cached.

        Args:
            entry_id: The arXiv paper ID (e.g., "2405.12345v1").
            
        Returns:
            The content of a paper as a string.
        """
        # Download PDF if not already available
        assets_dir = os.path.join(os.getcwd(), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        file_name = f"{entry_id}.pdf"
        file_path = os.path.join(assets_dir, file_name)
        
        if not os.path.exists(file_path):
            search = arxiv.Search(id_list=[entry_id])
            paper = next(search.results(), None)

            if not paper:
                return f"Paper with id {entry_id} not found"

            paper.download_pdf(filename=file_path)

        try:
            content = ArxivService._extract_text_from_pdf(file_path)
            paper_data = f"Paper_{entry_id}: {content}"

            # remove curly braces as they interfere with with the tool call
            paper_data = re.sub(r"{|}", "", paper_data)

            print(f"Extracted content for {entry_id}")

            return paper_data
        except Exception:
            return "Error extracting text from PDF"


    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> dict[str, str]:
        """Extracts text from a PDF using PyMuPDF with block-based ordering.

        Args:
            pdf_path: The path to the PDF file.
            
        Returns:
            A dictionary mapping block identifiers to extracted text.
        """
        doc = fitz.open(pdf_path)
        extracted_text = {}
        block_count = 1

        for page in doc:
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

            for block in blocks:
                block_text = block[4].strip()
                block_text = ArxivService._remove_headers_and_footers(block_text)
                block_text = ArxivService._clean_arxiv_text(block_text)
                extracted_text[f"block_{block_count}"] = block_text
                block_count += 1

        return extracted_text

    @staticmethod
    def _remove_headers_and_footers(text: str) -> str:
        """Removes typical arXiv headers and footers from text.

        Args:
            text: The original text block.
            
        Returns:
            The text block with headers and footers removed.
        """
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            if re.search(r"arXiv:\d{4}\.\d{5}", line):
                continue
            if re.search(r"\bPage \d+\b", line):
                continue
            if "arXiv" in line.lower():
                continue
            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    @staticmethod
    def _clean_arxiv_text(text: str) -> str:
        """Cleans extracted text by removing unnecessary whitespace and hyphenated line breaks.

        Args:
            text: The text to clean.
            
        Returns:
            Cleaned text.
        """
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"-\n", "", text)
        return text.strip()

    @staticmethod
    def download_and_store_pdf(entry_id: str) -> str:
        """Downloads the PDF of an arXiv paper and stores it in the root/assets directory.

        Args:
            entry_id: The arXiv paper ID (e.g., "2405.12345v1").
            
        Returns:
            The file path to the stored PDF.
            
        Raises:
            ValueError: If the paper is not found.
        """
        assets_dir = os.path.join(os.getcwd(), "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # check if the file already exists, if yes return the path
        file_name = f"{entry_id}.pdf"
        file_path = os.path.join(assets_dir, file_name)
        if os.path.exists(file_path):
            return file_path

        # Fetch the paper using the entry_id
        search = arxiv.Search(id_list=[entry_id])
        paper = next(search.results(), None)
        if not paper:
            raise ValueError(f"Paper with entry_id '{entry_id}' not found")

        file_name = f"{entry_id}.pdf"
        file_path = os.path.join(assets_dir, file_name)

        paper.download_pdf(filename=file_path)

        return file_path
