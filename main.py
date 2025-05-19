from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from g4f.client import Client
from g4f.Provider import DeepInfraChat

app = FastAPI()

# Allow all origins (for development and open access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the g4f client
client = Client()

# Define the request schema
class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]  # Example: [{"role": "user", "content": "Hello"}]

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
