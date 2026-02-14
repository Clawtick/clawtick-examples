"""
CrewAI Multi-Agent System with FastAPI
A production-ready webhook endpoint for ClawTick integration
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from typing import Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CrewAI ClawTick Integration",
    description="Multi-agent crew execution via scheduled webhooks",
    version="1.0.0"
)

# Configuration
API_KEY = os.getenv("AGENT_API_KEY", "change-me-in-production")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Request model
class CrewRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str
    crewType: Optional[str] = "default"  # default, research, content, analysis

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# Define agents
def create_agents():
    """Create the crew agents"""

    researcher = Agent(
        role='Research Analyst',
        goal='Research and gather comprehensive information on given topics',
        backstory="""You are an expert research analyst with years of experience
        in gathering, analyzing, and synthesizing information from various sources.
        You excel at finding relevant data and presenting it in a clear, structured manner.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    writer = Agent(
        role='Content Writer',
        goal='Create compelling, well-structured content based on research',
        backstory="""You are a professional content writer with exceptional skills
        in transforming research findings into engaging, readable content.
        You know how to adapt your writing style to different audiences and formats.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    editor = Agent(
        role='Content Editor',
        goal='Review and refine content for clarity, accuracy, and quality',
        backstory="""You are a meticulous editor with a keen eye for detail.
        You ensure content is polished, error-free, and maintains consistent
        quality standards while preserving the writer's voice.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    analyst = Agent(
        role='Data Analyst',
        goal='Analyze data and extract meaningful insights',
        backstory="""You are a skilled data analyst who can identify patterns,
        trends, and insights from various data sources. You excel at presenting
        complex information in an understandable way.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    return {
        "researcher": researcher,
        "writer": writer,
        "editor": editor,
        "analyst": analyst
    }

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

def create_default_crew(message: str, agents: dict) -> Crew:
    """Create a default research-write-edit crew"""

    research_task = Task(
        description=f"""Research the following topic thoroughly: {message}
        Gather relevant information, facts, and insights.
        Provide a comprehensive research summary.""",
        agent=agents["researcher"],
        expected_output="Comprehensive research findings with sources and key points"
    )

    write_task = Task(
        description="""Based on the research findings, write a well-structured article.
        Make it engaging, informative, and easy to understand.
        Include an introduction, main body with key points, and conclusion.""",
        agent=agents["writer"],
        expected_output="Well-written article based on research",
        context=[research_task]
    )

    edit_task = Task(
        description="""Review the article for clarity, grammar, and flow.
        Polish the content and ensure it meets high quality standards.
        Provide the final, publication-ready version.""",
        agent=agents["editor"],
        expected_output="Final polished article ready for publication",
        context=[write_task]
    )

    crew = Crew(
        agents=[agents["researcher"], agents["writer"], agents["editor"]],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

def create_research_crew(message: str, agents: dict) -> Crew:
    """Create a research-focused crew"""

    research_task = Task(
        description=f"""Conduct in-depth research on: {message}
        Focus on finding accurate, up-to-date information from reliable sources.""",
        agent=agents["researcher"],
        expected_output="Detailed research report with sources"
    )

    analysis_task = Task(
        description="""Analyze the research findings and extract key insights.
        Identify patterns, trends, and important takeaways.""",
        agent=agents["analyst"],
        expected_output="Analysis report with key insights and recommendations",
        context=[research_task]
    )

    crew = Crew(
        agents=[agents["researcher"], agents["analyst"]],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

def create_content_crew(message: str, agents: dict) -> Crew:
    """Create a content creation crew"""

    write_task = Task(
        description=f"""Create engaging content on: {message}
        Focus on clarity, engagement, and value to the reader.""",
        agent=agents["writer"],
        expected_output="Draft content piece"
    )

    edit_task = Task(
        description="""Edit and polish the content.
        Ensure it's error-free, well-structured, and publication-ready.""",
        agent=agents["editor"],
        expected_output="Final polished content",
        context=[write_task]
    )

    crew = Crew(
        agents=[agents["writer"], agents["editor"]],
        tasks=[write_task, edit_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

@app.post("/execute")
async def execute_crew(
    request: CrewRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute a CrewAI crew with the provided message

    This endpoint is called by ClawTick on schedule.
    """
    logger.info(f"Crew execution started - JobId: {request.jobId}, RunId: {request.runId}, Type: {request.crewType}")

    try:
        # Create agents
        agents = create_agents()

        # Select crew type
        crew_type = request.crewType or "default"

        if crew_type == "research":
            crew = create_research_crew(request.message, agents)
        elif crew_type == "content":
            crew = create_content_crew(request.message, agents)
        elif crew_type == "default":
            crew = create_default_crew(request.message, agents)
        else:
            crew = create_default_crew(request.message, agents)

        # Execute crew
        logger.info(f"Kicking off crew - RunId: {request.runId}")
        result = crew.kickoff()

        logger.info(f"Crew completed - RunId: {request.runId}")

        return {
            "success": True,
            "result": str(result),
            "jobId": request.jobId,
            "jobName": request.jobName,
            "runId": request.runId,
            "timestamp": request.timestamp,
            "crewType": crew_type,
            "agentsUsed": len(crew.agents),
            "tasksCompleted": len(crew.tasks)
        }

    except Exception as e:
        logger.error(f"Crew execution failed - RunId: {request.runId}, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Crew execution failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crewai-integration",
        "version": "1.0.0",
        "crewTypes": ["default", "research", "content"]
    }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "CrewAI ClawTick Integration",
        "version": "1.0.0",
        "endpoints": {
            "execute": "POST /execute",
            "health": "GET /health"
        },
        "crewTypes": {
            "default": "Research → Write → Edit",
            "research": "Research → Analyze",
            "content": "Write → Edit"
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
