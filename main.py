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
    if bot.client is None:
        raise HTTPException(status_code=500, detail="Groq API Key is missing or invalid.")
    
    try:
        # Prepend the system instruction message
        formatted_messages = [{"role": "system", "content": bot.SYSTEM_INSTRUCTION}]
        
        for msg in request.messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        # Using Llama 3 8B or 70B via Groq
        response = bot.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=formatted_messages,
            max_tokens=1024
        )
        
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
