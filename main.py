from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from g4f.client import Client
from g4f.Provider import DeepInfraChat
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow all origins (for development and open access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the g4f client
client = Client()

# Define the request schema
class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "Hello"}]

@app.post("/chat/stream")
async def stream_chat(chat_request: ChatRequest):
    async def generate():
        try:
            stream_response = client.chat.completions.create(
                provider=DeepInfraChat,
                model=chat_request.model,
                messages=chat_request.messages,
                stream=True
            )
            for chunk in stream_response:
                try:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        await asyncio.sleep(0.01)  # Optional: To smooth streaming
                except Exception as chunk_err:
                    logger.error(f"Chunk processing error: {chunk_err}")
                    yield f"\n[STREAM CHUNK ERROR]: {str(chunk_err)}\n"
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"\n[STREAM ERROR]: {str(e)}\n"

    return StreamingResponse(generate(), media_type="text/plain")

# Custom exception handler (optional but good for all other routes)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc)}
    )
