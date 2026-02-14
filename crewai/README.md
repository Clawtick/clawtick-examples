# CrewAI + ClawTick Integration

Multi-agent CrewAI workflow integrated with ClawTick for scheduled execution.

## Features

- ✅ Multiple crew types (Research, Content, Analysis)
- ✅ Sequential multi-agent workflows
- ✅ FastAPI webhook endpoint
- ✅ Production-ready error handling
- ✅ Configurable crew selection

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export AGENT_API_KEY="your-secret-key"

# Run server
python crew-server.py
```

## Crew Types

### 1. Default Crew (Research → Write → Edit)

Perfect for creating well-researched articles.

**Agents**: Researcher, Writer, Editor

**ClawTick Configuration**:
```bash
clawtick job create \
  --integration webhook \
  --cron "0 10 * * 1" \
  --message "Write an article about AI trends in 2025" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "default", "jobId": "{{jobId}}", "jobName": "{{jobName}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "weekly-article-generation"
```

### 2. Research Crew (Research → Analyze)

Focused on deep research and analysis.

**Agents**: Researcher, Analyst

**ClawTick Configuration**:
```bash
clawtick job create \
  --integration webhook \
  --cron "0 9 * * *" \
  --message "Research latest developments in quantum computing" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "research", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "daily-research-brief"
```

### 3. Content Crew (Write → Edit)

Fast content creation and editing.

**Agents**: Writer, Editor

**ClawTick Configuration**:
```bash
clawtick job create \
  --integration webhook \
  --cron "0 8 * * 1-5" \
  --message "Write a motivational quote and explanation" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "content", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "daily-motivation"
```

## Customize Your Crew

### Add New Agents

```python
coordinator = Agent(
    role='Project Coordinator',
    goal='Coordinate tasks between team members',
    backstory='Expert at managing workflows and ensuring quality',
    llm=llm,
    verbose=True
)
```

### Create Custom Crew Type

```python
def create_social_media_crew(message: str, agents: dict) -> Crew:
    """Create social media content crew"""

    content_task = Task(
        description=f"Create engaging social media post: {message}",
        agent=agents["writer"],
        expected_output="Social media post with hashtags"
    )

    review_task = Task(
        description="Review for tone and engagement",
        agent=agents["editor"],
        expected_output="Approved social post",
        context=[content_task]
    )

    crew = Crew(
        agents=[agents["writer"], agents["editor"]],
        tasks=[content_task, review_task],
        process=Process.sequential
    )

    return crew

# Add to execute_crew endpoint:
if crew_type == "social":
    crew = create_social_media_crew(request.message, agents)
```

### Change Agent Process

```python
# Sequential (default)
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.sequential  # One after another
)

# Hierarchical (requires manager_llm)
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    process=Process.hierarchical,  # Manager delegates
    manager_llm=ChatOpenAI(model="gpt-4")
)
```

## Examples

### Weekly Market Analysis

```bash
clawtick job create \
  --integration webhook \
  --cron "0 17 * * 5" \
  --message "Analyze this week's stock market trends and provide insights" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "research", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "weekly-market-analysis"
```

### Daily Content Generation

```bash
clawtick job create \
  --integration webhook \
  --cron "0 6 * * *" \
  --message "Create a blog post about productivity tips" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "default", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "daily-blog-post"
```

### Monthly Report

```bash
clawtick job create \
  --integration webhook \
  --cron "0 9 1 * *" \
  --message "Generate monthly performance report and key metrics analysis" \
  --webhook-url "https://your-server.com/execute" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --webhook-body '{"message": "{{message}}", "crewType": "research", "jobId": "{{jobId}}", "runId": "{{runId}}", "timestamp": "{{timestamp}}"}' \
  --name "monthly-report"
```

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
- [ClawTick Documentation](https://clawtick.com/docs)
