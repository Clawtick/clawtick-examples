# LangChain + ClawTick Integration

Complete example of integrating ClawTick with LangChain agents using FastAPI.

## Features

- ✅ LangChain OpenAI Functions Agent
- ✅ Custom tools (time, search, calculator)
- ✅ FastAPI webhook endpoint
- ✅ Bearer token authentication
- ✅ Comprehensive error handling
- ✅ Production-ready logging
- ✅ Health check endpoint

## Prerequisites

- Python 3.8+
- OpenAI API key
- ClawTick account ([clawtick.com](https://clawtick.com))

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
AGENT_API_KEY=your-secret-api-key-here
PORT=8000
```

### 3. Run the Server

```bash
python fastapi-agent.py
```

The server will start on `http://localhost:8000`

### 4. Test Locally (Optional)

Use curl to test the endpoint:

```bash
curl -X POST http://localhost:8000/trigger \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What time is it?",
    "jobId": "test-123",
    "jobName": "test-job",
    "runId": "run-456",
    "timestamp": "2025-02-14T10:00:00Z"
  }'
```

Expected response:

```json
{
  "success": true,
  "result": "The current time is 2025-02-14 10:00:00",
  "jobId": "test-123",
  "jobName": "test-job",
  "runId": "run-456",
  "timestamp": "2025-02-14T10:00:00Z"
}
```

## Deploy to Production

### Option 1: Docker

See `../docker/` directory for Dockerfile and docker-compose.yml

### Option 2: Cloud Platforms

**Heroku:**
```bash
heroku create my-langchain-agent
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set AGENT_API_KEY=your-key
git push heroku main
```

**Railway:**
```bash
railway login
railway init
railway up
```

**Render:**
- Connect your GitHub repository
- Set environment variables
- Deploy

### Option 3: VPS (Ubuntu)

```bash
# Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv

# Clone repository
git clone https://github.com/yourname/your-repo.git
cd your-repo/examples/langchain

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-..."
export AGENT_API_KEY="your-key"

# Run with systemd (recommended)
sudo nano /etc/systemd/system/langchain-agent.service
```

Systemd service file:

```ini
[Unit]
Description=LangChain ClawTick Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/examples/langchain
Environment="OPENAI_API_KEY=sk-..."
Environment="AGENT_API_KEY=your-key"
ExecStart=/path/to/venv/bin/python fastapi-agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable langchain-agent
sudo systemctl start langchain-agent
sudo systemctl status langchain-agent
```

## Configure ClawTick

### Via Dashboard

1. Go to [clawtick.com/dashboard/jobs](https://clawtick.com/dashboard/jobs)
2. Click "Create Job"
3. Select "Webhook" integration
4. Fill in the form:
   - **Job Name**: `LangChain Daily Summary`
   - **Schedule**: `0 9 * * *` (Daily at 9 AM)
   - **Message**: `Summarize the top 3 tech news from yesterday`
   - **Webhook URL**: `https://your-server.com/trigger`
   - **HTTP Method**: `POST`
   - Click "Advanced Options"
   - **Headers** (JSON):
     ```json
     {
       "Authorization": "Bearer your-secret-api-key-here"
     }
     ```
5. Click "Test Webhook" to verify
6. Click "Create Job"

### Via CLI

```bash
clawtick job create \
  --integration webhook \
  --cron "0 9 * * *" \
  --message "Summarize the top 3 tech news from yesterday" \
  --webhook-url "https://your-server.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-secret-api-key-here"}' \
  --name "langchain-daily-summary"
```

## Customize the Agent

### Add Custom Tools

Edit `fastapi-agent.py` and add new tools:

```python
@tool
def get_weather(location: str) -> str:
    """Get weather for a location"""
    # Add your weather API logic
    import requests
    response = requests.get(f"https://wttr.in/{location}?format=3")
    return response.text

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email"""
    # Add your email sending logic
    import smtplib
    # ... email logic ...
    return f"Email sent to {to}"

# Add tools to the list
tools = [get_current_time, search_documentation, calculate, get_weather, send_email]
```

### Change the LLM Model

```python
# Use GPT-3.5 Turbo (faster, cheaper)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Use GPT-4 Turbo
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.7)

# Use Claude (via Anthropic)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-opus-20240229")
```

### Add Conversation Memory

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,  # Add memory
    verbose=True
)
```

## Monitoring

### Logs

View logs in real-time:

```bash
# Local
python fastapi-agent.py

# Systemd
sudo journalctl -u langchain-agent -f

# Docker
docker logs -f langchain-agent
```

### Health Check

The health check endpoint returns service status:

```bash
curl https://your-server.com/health
```

Response:

```json
{
  "status": "healthy",
  "service": "langchain-agent",
  "version": "1.0.0"
}
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"

**Solution**: Make sure you've set the environment variable:

```bash
export OPENAI_API_KEY="sk-your-key"
```

Or add it to `.env` file.

### Issue: "401 Unauthorized" from ClawTick

**Solution**: Verify the API key in ClawTick matches your `AGENT_API_KEY`:

```bash
curl -X POST https://your-server.com/trigger \
  -H "Authorization: Bearer your-actual-key" \
  -d '{"message": "test", ...}'
```

### Issue: Agent responses are slow

**Solution**:
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Reduce `max_iterations` in AgentExecutor
- Optimize tool functions

### Issue: Connection timeout from ClawTick

**Solution**:
- Ensure server is publicly accessible
- Check firewall rules
- Verify DNS is resolving correctly
- ClawTick timeout is 30 seconds - optimize agent execution

## Examples

### Daily Email Summary

```bash
clawtick job create \
  --integration webhook \
  --cron "0 8 * * 1-5" \
  --message "Summarize my unread emails and prioritize top 3" \
  --webhook-url "https://your-server.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --name "email-morning-summary"
```

### Weekly Report

```bash
clawtick job create \
  --integration webhook \
  --cron "0 17 * * 5" \
  --message "Generate a weekly report of completed tasks" \
  --webhook-url "https://your-server.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --name "weekly-report"
```

### Hourly Data Check

```bash
clawtick job create \
  --integration webhook \
  --cron "0 * * * *" \
  --message "Check database for anomalies and alert if found" \
  --webhook-url "https://your-server.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --name "hourly-data-check"
```

## Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ClawTick Documentation](https://clawtick.com/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## Support

- **Issues**: [GitHub Issues](https://github.com/clawtick/examples/issues)
- **Discord**: [ClawTick Community](https://discord.gg/clawtick)
- **Email**: support@clawtick.com
