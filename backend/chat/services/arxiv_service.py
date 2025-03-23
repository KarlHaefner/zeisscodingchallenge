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
            content = ArxivService.fetch_paper_content(entry_id)

            # Summarize the content
            try:
                paper_summary = LLMService.invoke_summarization_chain(
                    chat_summarization, user_question, content
                )
            except Exception:
                paper_summary = "Error summarizing paper content"

            summarizations[f"Paper_{entry_id}"] = paper_summary

        # summarizations["Paper_2405.13599v1"] ="""The paper "LogRCA: Log-based Root Cause Analysis for Distributed Services" by Thorsten Wittkopp, Philipp Wiesner, and Odej Kao addresses significant challenges in root cause analysis (RCA) within complex IT service environments. The authors identify three main challenges: \n\n1. **Uncertainty in Identifying Root Causes**: It is often unclear which log lines represent the root cause of a failure, leading to a large number of potential candidates that complicate the analysis process.\n2. **Variable Number of Log Lines**: Unlike traditional binary classification, the number of log lines that may represent a root cause can vary significantly from case to case, making it difficult to apply a one-size-fits-all approach.\n3. **Imbalanced Training Data**: The occurrence of certain root causes may be rare, resulting in imbalanced datasets that can negatively affect model performance due to biases towards more common classes.\n\nTo address these challenges, the authors propose LogRCA, a semi-supervised learning method that identifies a minimal set of log lines indicative of a root cause. LogRCA employs a transformer model that can handle noisy data and is trained to rank log lines based on their relevance to the identified root cause. The authors state, "LogRCA determines a set of log lines that together describe the root cause of a failure," and it allows users to dynamically adjust the number of log lines to analyze based on their relevance scores.\n\nAdditionally, the authors introduce a data balancing strategy to improve performance on rare failures by leveraging automatic clustering to estimate the distribution of root causes in the training data. This approach helps mitigate the effects of class imbalance, enhancing the model\'s ability to detect less frequent root causes.\n\nIn evaluations on a large-scale dataset, LogRCA demonstrated superior performance compared to baseline methods, achieving high recall rates for identifying root causes, particularly for rare failures. The authors conclude that their method significantly improves the efficiency of root cause analysis in complex distributed systems, making it a valuable tool for IT service developers and operators."""

        print(f"Summarizations: \n{summarizations}\n")
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
