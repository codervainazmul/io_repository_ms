from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from g4f.client import Client
from g4f.Provider import DeepInfraChat
import sys

app = FastAPI()
client = Client()

# Pydantic model for request body
class ChatRequest(BaseModel):
    model: str
    messages: list

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    def generate():
        try:
            stream_response = client.chat.completions.create(
                provider=DeepInfraChat,
                model=request.model,
                messages=request.messages,
                stream=True
            )
            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}\n"

    return StreamingResponse(generate(), media_type="text/plain")
