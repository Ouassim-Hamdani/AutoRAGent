"""Parser module for converting PDF documents to text/markdown."""

import os,time,logging
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)


class Parser:
    """Handles parsing of PDF files into structured documents."""

    def __init__(self):
        """Initialize the document converter."""
        self.converter = DocumentConverter()

    def parse(self, path: str, save_to_folder: str = None) -> str:
        """
        Parse a single PDF file.

        Args:
            path: Path to the PDF file to parse
            save_to_folder: Optional folder to save the converted markdown

        Returns:
            Parsed document object

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        start = time.perf_counter()
        resp = self.converter.convert(path).document
        elapsed = time.perf_counter() - start
        logger.info(f"Parsed {len(resp.export_to_text())} chars in {elapsed:.2f}s")

        if save_to_folder:
            os.makedirs(save_to_folder, exist_ok=True)
            save_path = os.path.join(
                save_to_folder, f"{os.path.splitext(os.path.basename(path))[0]}.md"
            )
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(resp.export_to_markdown())

            logger.info(f"Saved converted markdown to {save_path}")

        return resp
    
    def export_to_markdown_with_page_numbers(self,doc,first_page_idx=1)-> str:
        """
        Exports the document to markdown including page numbers with clear LLM-friendly separators.
        """
        resp = f"\n{'='*80}\n[START OF PAGE {first_page_idx}]\n{'='*80}\n\n"+doc.export_to_markdown(page_break_placeholder="<-- Page Break -->")
        page_index = first_page_idx
        while "<-- Page Break -->" in resp:
            resp = resp.replace("<-- Page Break -->", f"\n\n{'='*80}\n[END OF PAGE {page_index}]\n[START OF PAGE {page_index+1}]\n{'='*80}\n\n", 1)
            page_index += 1
        resp +=f"\n\n{'='*80}\n[END OF PAGE {page_index}]\n{'='*80}\n"
        
        return resp
    