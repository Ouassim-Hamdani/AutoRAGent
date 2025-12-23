from src.core.parser import Parser
from src.core.chunker import Chunker
from src.core.DBHandler import VectorDBManager
class RagifyPipe:
    def __init__(self):
        self.parser = Parser()
        self.chunker = Chunker()
        self.db_manager = VectorDBManager()
    def __call__(self, file_path :str, collection_name: str):
        # 1. Parse the document
        doc = self.parser.parse(file_path)
        
        # 2. Chunk the document
        chunks = self.chunker.chunk(doc)
        
        # 3. Add chunks to the vector database
        self.db_manager.add_documents(collection_name, chunks)
        
        
if __name__ == "__main__":
    ragify = RagifyPipe()
    ragify("../../samples/sample2.pdf","test_collection")
    