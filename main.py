from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
import os
import uvicorn
from contextlib import asynccontextmanager

import bot

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure static directory exists
    os.makedirs("static", exist_ok=True)
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    import os
    import httpx
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API Key is missing or invalid.")
    
    try:
        formatted_messages = [{"role": "system", "content": bot.SYSTEM_INSTRUCTION}]
        for msg in request.messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": formatted_messages,
                    "max_tokens": 1024
                },
                timeout=15.0
            )
            
            if res.status_code != 200:
                # This will extract the exact error message from Groq
                error_detail = res.text
                raise Exception(f"Groq API Error {res.status_code}: {error_detail}")
                
            data = res.json()
            return {"response": data["choices"][0]["message"]["content"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
