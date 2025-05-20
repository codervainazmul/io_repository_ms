# Import necessary modules from FastAPI and related packages
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# Import g4f (unofficial ChatGPT wrapper) and provider
from g4f.client import Client
from g4f.Provider import DeepInfraChat

# Create a FastAPI app instance
app = FastAPI()

# Configure CORS middleware to allow requests from all origins (useful for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the g4f client for making chat requests
client = Client()

# Define the expected structure of the incoming chat request using Pydantic
class ChatRequest(BaseModel):
    model: str  # The model name to use (e.g., "gpt-3.5-turbo")
    messages: List[Dict[str, str]]  # A list of message dictionaries with "role" and "content"

# Define a POST endpoint for streaming chat responses
@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    # Generator function to stream content as it's received
    def generate():
        try:
            # Create a streaming chat completion using the specified provider and model
            stream_response = client.chat.completions.create(
                provider=DeepInfraChat,      # Provider used for the model
                model=request.model,         # Model name from request
                messages=request.messages,   # Chat history from request
                stream=True                  # Enable streaming response
            )
            # Iterate over streamed chunks of the response
            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    # Yield the content of the chunk as it's received
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # If there's an error, yield an error message
            yield f"\n[ERROR]: {str(e)}\n"

    # Return a streaming response with MIME type 'text/plain'
    return StreamingResponse(generate(), media_type="text/plain")
