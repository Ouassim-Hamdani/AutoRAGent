"""Chunker module for splitting documents into manageable pieces."""

import os
import time
from pathlib import Path
from typing import List

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from langchain_core.documents import Document
from transformers import AutoTokenizer


class Chunker:
    """Handles document chunking using Docling's HybridChunker."""

    def __init__(
        self,
        embedding_model: str = "BAAI/bge-m3",
        max_tokens: int = 8192,
        overlap: int = 256,
    ):
        """
        Initialize the chunker with specified parameters.

        Args:
            embedding_model: Name of the HuggingFace embedding model
            max_tokens: Maximum number of tokens per chunk
            overlap: Number of overlapping tokens between chunks
        """
        self.chunker = HybridChunker(
            tokenizer=HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(embedding_model)
            ),
            max_tokens=max_tokens,
            merge_peers=True,
            overlap_tokens=overlap,
        )

    def chunk(self, doc) -> List[Document]:
        """
        Chunk a single document.

        Args:
            doc: Docling document to chunk

        Returns:
            List of LangChain Document objects with metadata
        """
        start = time.perf_counter()
        chunks = list(self.chunker.chunk(dl_doc=doc))
        elapsed = time.perf_counter() - start

        source_name = os.path.basename(doc.origin.filename)
        print(
            f"File '{source_name}' Chunked into {len(chunks)} chunks "
            f"(took {elapsed:.2f}s)"
        )

        return self._transform_to_documents(chunks)

    def chunk_list(self, docs: list) -> List[Document]:
        """
        Chunk multiple Docling Documents.

        Args:
            docs: List of Docling documents to chunk

        Returns:
            List of all chunks as LangChain Document objects
        """
        final_chunks = []
        for doc in docs:
            chunks = self.chunk(doc)
            final_chunks.extend(chunks)

        print(f"✅ Finished chunking. Total final chunks: {len(final_chunks)}.")
        return final_chunks

    def _transform_to_documents(self, chunks: List) -> List[Document]:
        """
        Transform Docling chunks into LangChain Documents.

        Args:
            chunks: List of Docling chunks

        Returns:
            List of LangChain Document objects with metadata
        """
        processed_chunks = [
            {
                "text": chunk.text,
                "metadata": {
                    "source": chunk.meta.origin.filename,
                    "page_numbers": ",".join(
                        [
                            str(pg_no)
                            for pg_no in sorted(
                                set(
                                    prov.page_no
                                    for item in chunk.meta.doc_items
                                    for prov in item.prov
                                )
                            )
                        ]
                    ),
                    "title": chunk.meta.headings[0] if chunk.meta.headings else None,
                },
            }
            for chunk in chunks
        ]

        docs = []
        for chunk in processed_chunks:
            doc = Document(
                page_content=chunk["text"], metadata=chunk["metadata"]
            )
            docs.append(doc)

        return docs