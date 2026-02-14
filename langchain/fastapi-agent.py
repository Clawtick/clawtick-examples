"""
LangChain Agent with FastAPI
A production-ready webhook endpoint for ClawTick integration
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LangChain ClawTick Agent",
    description="Webhook endpoint for scheduled LangChain agent execution",
    version="1.0.0"
)

# Configuration
API_KEY = os.getenv("AGENT_API_KEY", "change-me-in-production")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Request model
class AgentRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

# Define custom tools
@tool
def get_current_time() -> str:
    """Get the current time"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def search_documentation(query: str) -> str:
    """Search through documentation for information"""
    # Implement your documentation search logic here
    # This is a placeholder
    return f"Documentation search results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations. Use Python syntax."""
    try:
        # Note: eval is dangerous in production - use a safe math parser instead
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"

# Initialize LangChain components
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

tools = [get_current_time, search_documentation, calculate]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant with access to various tools.
    You help users by answering questions and performing tasks using the available tools.
    Always be concise and accurate in your responses."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

# Authentication dependency
async def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return token

@app.post("/trigger")
async def trigger_agent(
    request: AgentRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute the LangChain agent with the provided message

    This endpoint is called by ClawTick on schedule.
    """
    logger.info(f"Agent triggered - JobId: {request.jobId}, RunId: {request.runId}")

    try:
        # Execute agent
        result = agent_executor.invoke({
            "input": request.message,
            "chat_history": []  # Add conversation memory if needed
        })

        logger.info(f"Agent completed - RunId: {request.runId}")

        return {
            "success": True,
            "result": result["output"],
            "jobId": request.jobId,
            "jobName": request.jobName,
            "runId": request.runId,
            "timestamp": request.timestamp
        }

    except Exception as e:
        logger.error(f"Agent execution failed - RunId: {request.runId}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "langchain-agent",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "LangChain ClawTick Agent",
        "version": "1.0.0",
        "endpoints": {
            "trigger": "POST /trigger",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )
