from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from agent.agent import AutoRAGENT
import os,shutil,json
app = FastAPI()
agent = AutoRAGENT()



@app.get("/")
async def root():
    # return status okay
    return {"status": "API is running."}

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
