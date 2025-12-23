from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from agent.agent import AutoRAGENT

app = FastAPI()
agent = AutoRAGENT()

class ChatRequest(BaseModel):
    message: str
    history: Optional[str] = None
    session_id: Optional[str] = None

@app.get("/")
async def root():
    # return status okay
    return {"status": "API is running."}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        agent(
            query=request.message,
            history=request.history,
            session_id=request.session_id,
            stream=True
        ),
        media_type="application/x-ndjson"
    )




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2003)
