# ClawTick Integration Templates

Complete examples for integrating ClawTick with popular AI frameworks.

## Table of Contents

- [LangChain](#langchain)
- [CrewAI](#crewai)
- [AutoGPT](#autogpt)
- [Custom Python Agent](#custom-python-agent)
- [N8n Workflows](#n8n-workflows)
- [Make.com Scenarios](#makecom-scenarios)
- [Zapier Webhooks](#zapier-webhooks)

---

## LangChain

### Option 1: FastAPI + LangChain (Python)

**File: `agent_server.py`**

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os

app = FastAPI()

# API Key for authentication
API_KEY = os.getenv("AGENT_API_KEY", "your-secret-key")

class AgentRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location"""
    # Implement your weather API logic here
    return f"Weather in {location}: Sunny, 72°F"

@tool
def search_web(query: str) -> str:
    """Search the web for information"""
    # Implement your search logic here
    return f"Search results for: {query}"

# Initialize LangChain agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
tools = [get_weather, search_web]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.post("/trigger")
async def trigger_agent(
    request: AgentRequest,
    authorization: str = Header(None)
):
    # Validate API key
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Execute agent with the message from ClawTick
        result = agent_executor.invoke({"input": request.message})

        return {
            "success": True,
            "result": result["output"],
            "jobId": request.jobId,
            "runId": request.runId
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Requirements: `requirements.txt`**

```txt
fastapi==0.109.0
uvicorn==0.27.0
langchain==0.1.0
langchain-openai==0.0.5
pydantic==2.5.0
```

**Deploy & Run:**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export AGENT_API_KEY="your-secret-key"

# Run server
python agent_server.py
```

**ClawTick Configuration:**

**Via Dashboard:**
- Integration Type: Webhook
- Webhook URL: `https://your-server.com/trigger`
- HTTP Method: POST
- Headers: `{"Authorization": "Bearer your-secret-key", "Content-Type": "application/json"}`
- Body Template: `{"message": "{{message}}", "jobId": "{{jobId}}", "jobName": "{{jobName}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}`

**Via CLI:**
```bash
clawtick job create \
  --integration webhook \
  --cron "0 9 * * *" \
  --message "Check my calendar and summarize today's meetings" \
  --webhook-url "https://your-server.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --webhook-body '{"message": "{{message}}", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "langchain-daily-summary"
```

### Option 2: Next.js API Route + LangChain (TypeScript)

**File: `app/api/agent/route.ts`**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { ChatOpenAI } from '@langchain/openai';
import { DynamicStructuredTool } from '@langchain/core/tools';
import { createOpenAIFunctionsAgent, AgentExecutor } from 'langchain/agents';
import { ChatPromptTemplate, MessagesPlaceholder } from '@langchain/core/prompts';
import { z } from 'zod';

const API_KEY = process.env.AGENT_API_KEY!;

const weatherTool = new DynamicStructuredTool({
  name: 'get_weather',
  description: 'Get the current weather for a location',
  schema: z.object({
    location: z.string().describe('The city name'),
  }),
  func: async ({ location }) => {
    // Implement your weather API logic
    return `Weather in ${location}: Sunny, 72°F`;
  },
});

export async function POST(request: NextRequest) {
  // Validate API key
  const authHeader = request.headers.get('authorization');
  if (!authHeader || authHeader !== `Bearer ${API_KEY}`) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  try {
    const body = await request.json();
    const { message, jobId, runId } = body;

    // Initialize LangChain agent
    const llm = new ChatOpenAI({ modelName: 'gpt-4', temperature: 0 });
    const tools = [weatherTool];

    const prompt = ChatPromptTemplate.fromMessages([
      ['system', 'You are a helpful AI assistant.'],
      new MessagesPlaceholder('agent_scratchpad'),
      ['human', '{input}'],
    ]);

    const agent = await createOpenAIFunctionsAgent({
      llm,
      tools,
      prompt,
    });

    const agentExecutor = new AgentExecutor({
      agent,
      tools,
    });

    // Execute agent
    const result = await agentExecutor.invoke({ input: message });

    return NextResponse.json({
      success: true,
      result: result.output,
      jobId,
      runId,
    });
  } catch (error) {
    console.error('Agent error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal error' },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ status: 'healthy' });
}
```

**Deploy to Vercel:**

```bash
# Install dependencies
npm install langchain @langchain/openai @langchain/core zod

# Set environment variables in Vercel
OPENAI_API_KEY=sk-...
AGENT_API_KEY=your-secret-key

# Deploy
vercel deploy --prod
```

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 8 * * 1-5" \
  --message "Good morning! What's on my agenda today?" \
  --webhook-url "https://your-app.vercel.app/api/agent" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --name "langchain-morning-brief"
```

---

## CrewAI

### Multi-Agent Crew Workflow

**File: `crew_server.py`**

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os

app = FastAPI()
API_KEY = os.getenv("AGENT_API_KEY", "your-secret-key")

class CrewRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Define agents
researcher = Agent(
    role='Research Analyst',
    goal='Research and gather information on given topics',
    backstory='Expert researcher with strong analytical skills',
    llm=llm,
    verbose=True
)

writer = Agent(
    role='Content Writer',
    goal='Create compelling content based on research',
    backstory='Experienced writer skilled at turning research into engaging content',
    llm=llm,
    verbose=True
)

editor = Agent(
    role='Content Editor',
    goal='Review and refine content for quality',
    backstory='Detail-oriented editor ensuring high-quality output',
    llm=llm,
    verbose=True
)

@app.post("/execute")
async def execute_crew(
    request: CrewRequest,
    authorization: str = Header(None)
):
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Create tasks based on the message
        research_task = Task(
            description=f"Research the following topic: {request.message}",
            agent=researcher,
            expected_output="Comprehensive research findings"
        )

        write_task = Task(
            description="Write an article based on the research findings",
            agent=writer,
            expected_output="Well-written article",
            context=[research_task]
        )

        edit_task = Task(
            description="Review and polish the article",
            agent=editor,
            expected_output="Final polished article",
            context=[write_task]
        )

        # Create and run crew
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, write_task, edit_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        return {
            "success": True,
            "result": str(result),
            "jobId": request.jobId,
            "runId": request.runId,
            "crew": "research-write-edit"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Requirements: `requirements.txt`**

```txt
fastapi==0.109.0
uvicorn==0.27.0
crewai==0.1.26
langchain-openai==0.0.5
```

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 10 * * 1" \
  --message "Write an article about AI trends in 2025" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --name "crewai-weekly-article"
```

---

## AutoGPT

### AutoGPT Task Execution

**File: `autogpt_server.py`**

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os
import json

# Note: This is a simplified example
# You'll need to adapt based on your AutoGPT setup

app = FastAPI()
API_KEY = os.getenv("AGENT_API_KEY", "your-secret-key")

class AutoGPTRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

@app.post("/execute")
async def execute_autogpt(
    request: AutoGPTRequest,
    authorization: str = Header(None)
):
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Initialize AutoGPT with the task
        # This is pseudo-code - adapt to your AutoGPT version
        from autogpt.agent import Agent
        from autogpt.config import Config

        config = Config()
        agent = Agent(
            ai_name="TaskExecutor",
            memory=config.memory,
            next_action_count=config.continuous_limit,
            command_registry=config.command_registry,
            config=config,
            system_prompt=request.message,
            triggering_prompt=config.triggering_prompt,
        )

        # Run agent
        result = agent.run()

        return {
            "success": True,
            "result": result,
            "jobId": request.jobId,
            "runId": request.runId
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 9 * * *" \
  --message "Research and summarize top tech news from yesterday" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --name "autogpt-daily-news"
```

---

## Custom Python Agent

### Simple Custom Agent

**File: `custom_agent.py`**

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import openai
import os

app = FastAPI()
API_KEY = os.getenv("AGENT_API_KEY", "your-secret-key")
openai.api_key = os.getenv("OPENAI_API_KEY")

class AgentRequest(BaseModel):
    message: str
    jobId: str
    jobName: str
    runId: str
    timestamp: str

def execute_agent_task(prompt: str) -> str:
    """Your custom agent logic here"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

@app.post("/run")
async def run_agent(
    request: AgentRequest,
    authorization: str = Header(None)
):
    if not authorization or authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = execute_agent_task(request.message)

        # Optional: Save to database, send notification, etc.
        # save_result_to_db(request.jobId, request.runId, result)

        return {
            "success": True,
            "result": result,
            "jobId": request.jobId,
            "runId": request.runId,
            "timestamp": request.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 */6 * * *" \
  --message "Check system health and alert if issues found" \
  --webhook-url "https://your-server.com/run" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --name "custom-health-monitor"
```

---

## N8n Workflows

### N8n Webhook Trigger

**Setup in N8n:**

1. Create new workflow in N8n
2. Add "Webhook" node as trigger
3. Set Authentication: "Header Auth"
4. Header Name: `Authorization`
5. Header Value: `Bearer your-secret-key`
6. Copy webhook URL

**Example N8n Workflow:**

```
Webhook Trigger
    ↓
[Extract message from body]
    ↓
[OpenAI Chat]
    ↓
[Send to Slack/Email/etc]
```

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 12 * * *" \
  --message "Generate daily status report" \
  --webhook-url "https://your-n8n-instance.com/webhook/abc123" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-key"}' \
  --webhook-body '{"message": "{{message}}", "timestamp": "{{timestamp}}"}' \
  --name "n8n-daily-report"
```

---

## Make.com Scenarios

### Make.com Webhook

**Setup in Make.com:**

1. Create new scenario
2. Add "Webhooks" → "Custom Webhook" as first module
3. Copy webhook URL
4. Add subsequent modules (HTTP, OpenAI, Slack, etc.)

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 8 * * 1" \
  --message "Send weekly team update" \
  --webhook-url "https://hook.us1.make.com/abc123xyz" \
  --webhook-method POST \
  --webhook-body '{"task": "{{message}}", "job": "{{jobName}}", "time": "{{timestamp}}"}' \
  --name "make-weekly-update"
```

---

## Zapier Webhooks

### Zapier Webhook Trigger

**Setup in Zapier:**

1. Create new Zap
2. Choose "Webhooks by Zapier" as trigger
3. Select "Catch Hook"
4. Copy webhook URL
5. Add action steps (OpenAI, Gmail, Slack, etc.)

**ClawTick Configuration:**

```bash
clawtick job create \
  --integration webhook \
  --cron "0 18 * * 5" \
  --message "Prepare weekend summary email" \
  --webhook-url "https://hooks.zapier.com/hooks/catch/123456/abc123/" \
  --webhook-method POST \
  --webhook-body '{"message": "{{message}}", "source": "clawtick"}' \
  --name "zapier-weekend-summary"
```

---

## General Tips

### 1. Authentication

Always use authentication for your webhooks:

```python
# Option 1: Bearer token
authorization: str = Header(None)
if authorization != f"Bearer {API_KEY}":
    raise HTTPException(401)

# Option 2: API key header
api_key: str = Header(None, alias="X-Api-Key")
if api_key != API_KEY:
    raise HTTPException(401)

# Option 3: Basic auth
import base64
auth = request.headers.get('Authorization')
if not auth or not auth.startswith('Basic '):
    raise HTTPException(401)
```

### 2. Error Handling

Return proper status codes:

```python
try:
    result = execute_task()
    return {"success": True, "result": result}
except ValueError as e:
    # Bad request
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Server error
    raise HTTPException(status_code=500, detail=str(e))
```

### 3. Idempotency

Use `runId` to prevent duplicate executions:

```python
# Check if this runId was already processed
if is_run_already_processed(request.runId):
    return cached_result(request.runId)

# Process and cache result
result = execute_task(request.message)
cache_result(request.runId, result)
return result
```

### 4. Async Processing

For long-running tasks:

```python
from fastapi import BackgroundTasks

async def execute_long_task(message: str, run_id: str):
    # Long running task
    result = await process_task(message)
    # Store result or send notification
    save_result(run_id, result)

@app.post("/trigger")
async def trigger(request: AgentRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_long_task, request.message, request.runId)
    return {"success": True, "status": "processing", "runId": request.runId}
```

### 5. Logging

Log important events:

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/trigger")
async def trigger(request: AgentRequest):
    logger.info(f"Job triggered: {request.jobId}, RunId: {request.runId}")
    try:
        result = execute_task(request.message)
        logger.info(f"Job completed: {request.runId}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Job failed: {request.runId}, Error: {str(e)}")
        raise
```

### 6. Testing Locally

Use ngrok to test webhooks locally:

```bash
# Start your server
python agent_server.py

# In another terminal, expose with ngrok
ngrok http 8000

# Use the ngrok URL in ClawTick
# https://abc123.ngrok.io/trigger
```

---

## Docker Deployment

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AGENT_API_KEY=${AGENT_API_KEY}
    restart: unless-stopped
```

**Deploy:**

```bash
docker-compose up -d
```

---

## Support

- **Documentation**: https://clawtick.com/docs
- **Examples Repository**: https://github.com/clawtick/examples
- **Community**: https://discord.gg/clawtick
- **Issues**: https://github.com/clawtick/cli/issues

---

**Last Updated**: February 14, 2025
