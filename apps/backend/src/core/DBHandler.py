import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Optional, Dict
from dotenv import load_dotenv
load_dotenv()
class VectorDBManager:
    """
    Central Manager for the ChromaDB Server.
    Allows interacting with multiple collections dynamically.
    """
    
    def __init__(self, embedding_model: str = "BAAI/bge-m3"):
        # 1. Initialize Embedding Function (Shared across all collections)
        self.embedding_function = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"}, 
            encode_kwargs={"normalize_embeddings": True}
        )

        # 2. Connect to ChromaDB Server
        chroma_host = os.getenv("DATABASE_HOST", "localhost")
        chroma_port = int(os.getenv("DATABASE_PORT", 1989))
        print(f"Connecting to ChromaDB at {chroma_host}:{chroma_port}...")
        self.client = chromadb.HttpClient(
            host=chroma_host, 
            port=chroma_port,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        
        # Cache for collection objects to avoid re-initializing
        self._collections: Dict[str, Chroma] = {}
        
        print(f"✅ Connected to ChromaDB Manager at {chroma_host}:{chroma_port}")

    def _get_collection_store(self, collection_name: str) -> Chroma:
        """
        Internal helper to get or create a LangChain Chroma wrapper for a specific collection.
        """
        if collection_name not in self._collections:
            self._collections[collection_name] = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=self.embedding_function,
            )
        return self._collections[collection_name]

    def add_documents(self, collection_name: str, documents: List[Document]):
        """
        Embeds and adds documents to a specific collection.
        Creates the collection if it doesn't exist.
        """
        if not documents:
            return
        
        store = self._get_collection_store(collection_name)
        store.add_documents(documents)
        print(f"Added {len(documents)} documents to collection '{collection_name}'")

    def query(self, collection_name: str, query_text: str, k: int = 5, filter_metadata: Optional[dict] = None) -> List[Document]:
        """
        Semantic search within a specific collection.
        """
        store = self._get_collection_store(collection_name)
        return store.similarity_search(
            query=query_text,
            k=k,
            filter=filter_metadata
        )
    
    def list_collections(self) -> List[str]:
        """Returns a list of all collection names in the DB."""
        return [col.name for col in self.client.list_collections()]
        
    def delete_collection(self, collection_name: str):
        """Deletes a collection and removes it from cache."""
        try:
            self.client.delete_collection(collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            print(f"Deleted collection '{collection_name}'")
        except Exception as e:
            print(f"Error deleting collection '{collection_name}': {e}")

if __name__ == "__main__":
    db_manager = VectorDBManager()
    print("Existing Collections:", db_manager.list_collections())
    print(db_manager.query("test_collection", ""))
    