from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from agent.agent import AutoRAGENT
from core.DBHandler import VectorDBManager
import os,shutil,json
app = FastAPI()
agent = AutoRAGENT()
try:
    db_manager = VectorDBManager()
except Exception as e:
    print(f"Warning: Could not connect to VectorDBManager. Collections endpoint may fail. Error: {e}")

@app.get("/")
async def root():
    # return status okay
    return {"status": "API is running."}

@app.get("/collections")
async def get_collections():
    """
    Returns a list of all available collections and their first 5 documents.
    Structure:
    [
        {
            "name": "collection_name",
            "preview": ["doc1_content", "doc2_content", ...]
        },
        ...
    ]
    """
    try:
        collections = db_manager.list_collections()
        result = []
        
        for col_name in collections:
            collection = db_manager.client.get_collection(col_name)
            peek_data = collection.peek(limit=5)            
            documents = peek_data.get("documents", [])
            
            result.append({
                "name": col_name,
                "preview": documents
            })
            
        return {"collections": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching collections: {str(e)}")

@app.post("/chat")
async def chat_endpoint(
    history: Optional[str] = Form(None), # Received as JSON string
    session_id: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
    ):
    if history:
            try:
                history = json.loads(history)
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid history format. Must be a valid JSON string.")
    if files:
        sid = session_id if session_id else "temp"
        upload_dir = os.path.abspath(os.path.join(os.environ["SESSIONS_FOLDER"], sid))
        os.makedirs(upload_dir, exist_ok=True)
        
        
        saved_file_paths = []
        for file in files:
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(file_path)
        history[-1]["files_paths"] = saved_file_paths
        
    return StreamingResponse(
        agent(
            history=history,
            session_id=session_id,
            stream=True
        ),
        media_type="application/x-ndjson"
    )




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2003)
