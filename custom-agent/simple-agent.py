"""
Simple Custom AI Agent with OpenAI
Minimal example for ClawTick integration
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="Simple AI Agent", version="1.0.0")

# Configuration
API_KEY = os.getenv("AGENT_API_KEY", "change-me")
openai.api_key = os.getenv("OPENAI_API_KEY")

class AgentRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

@app.post("/run")
async def run_agent(request: AgentRequest, authorization: str = Header(None)):
    # Validate API key
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        result = response.choices[0].message.content

        return {
            "success": True,
            "result": result,
            "jobId": request.jobId,
            "runId": request.runId
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
