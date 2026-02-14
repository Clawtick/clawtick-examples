# ClawTick Integration Examples

Production-ready examples for integrating ClawTick with popular AI frameworks.

## 📦 Available Templates

### 1. [LangChain](https://github.com/clawtick/clawtick-examples/tree/main/langchain)
Complete LangChain agent with custom tools and FastAPI webhook endpoint.

**Features:**
- OpenAI Functions Agent
- Custom tools (time, search, calculator)
- Production-ready error handling
- Comprehensive logging

**Use Cases:**
- Task automation
- Information retrieval
- Multi-step workflows

### 2. [CrewAI](https://github.com/clawtick/clawtick-examples/tree/main/crewai)
Multi-agent CrewAI workflow with configurable crew types.

**Features:**
- Multiple agent types (Research, Write, Edit, Analyze)
- Sequential and hierarchical workflows
- Three pre-built crew configurations

**Use Cases:**
- Content creation
- Research and analysis
- Report generation

### 3. [Custom Agent](https://github.com/clawtick/clawtick-examples/tree/main/custom-agent)
Minimal example using OpenAI API directly.

**Features:**
- Simple and lightweight
- Easy to understand and modify
- Great starting point for custom implementations

**Use Cases:**
- Simple Q&A bots
- Text generation
- Quick prototypes

### 4. [Docker](https://github.com/clawtick/clawtick-examples/tree/main/docker)
Docker and docker-compose configuration for easy deployment.

**Features:**
- Multi-service deployment
- Health checks
- Auto-restart
- Environment variable configuration

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Choose an example
cd langchain  # or crewai, custom-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the server
python *.py
```

### Option 2: Docker

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export AGENT_API_KEY="your-secret-key"

# Run all services
cd docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 3: Individual Docker Container

```bash
# Build
docker build -t my-agent -f docker/Dockerfile langchain/

# Run
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY="sk-..." \
  -e AGENT_API_KEY="your-key" \
  my-agent
```

## 🔧 Configuration

All examples use the same environment variables:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key
AGENT_API_KEY=your-secret-api-key-for-clawtick

# Optional
PORT=8000  # Server port (default: 8000)
```

## 🌐 Deploy to Cloud

### Heroku

```bash
cd langchain  # or crewai, custom-agent
heroku create my-clawtick-agent
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set AGENT_API_KEY=your-key
git push heroku main
```

### Railway

```bash
railway login
railway init
railway up
```

### Render

1. Connect GitHub repository
2. Select example directory
3. Add environment variables
4. Deploy

### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set AGENT_API_KEY=your-key
fly deploy
```

## 📝 Configure ClawTick

After deploying your agent, configure ClawTick:

### Via Dashboard

1. Go to [clawtick.com/dashboard/jobs](https://clawtick.com/dashboard/jobs)
2. Click "Create Job"
3. Select "Webhook" integration
4. Fill in:
   - **Webhook URL**: Your deployed endpoint
   - **HTTP Method**: POST
   - **Headers**: `{"Authorization": "Bearer your-secret-api-key"}`
5. Click "Test Webhook" to verify
6. Create job

### Via CLI

```bash
# Install ClawTick CLI
npm install -g clawtick

# Login
clawtick login --key cp_your_api_key

# Create job
clawtick job create \
  --integration webhook \
  --cron "0 9 * * *" \
  --message "Your task description" \
  --webhook-url "https://your-agent.com/trigger" \
  --webhook-method POST \
  --webhook-headers '{"Authorization": "Bearer your-key"}' \
  --name "my-scheduled-job"
```

## 🧪 Testing

### Test Locally

```bash
curl -X POST http://localhost:8000/trigger \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, world!",
    "jobId": "test-123",
    "jobName": "test-job",
    "runId": "run-456",
    "timestamp": "2025-02-14T10:00:00Z"
  }'
```

### Test with ngrok

```bash
# Start your server
python langchain/fastapi-agent.py

# In another terminal
ngrok http 8000

# Use the ngrok URL in ClawTick
```

## 📚 Request Format

All examples expect this request format:

```json
{
  "message": "Your task or question",
  "jobId": "unique-job-identifier",
  "jobName": "human-readable-job-name",
  "runId": "unique-execution-identifier",
  "timestamp": "2025-02-14T10:00:00.000Z"
}
```

ClawTick automatically populates these fields using template variables:

```json
{
  "message": "{{message}}",
  "jobId": "{{jobId}}",
  "jobName": "{{jobName}}",
  "runId": "{{runId}}",
  "timestamp": "{{timestamp}}"
}
```

## 📊 Response Format

Expected response format:

```json
{
  "success": true,
  "result": "Agent response or output",
  "jobId": "job-123",
  "runId": "run-456",
  "timestamp": "2025-02-14T10:00:00Z"
}
```

## 🔒 Security Best Practices

1. **Always use HTTPS** in production
2. **Use strong API keys** (32+ random characters)
3. **Store secrets in environment variables** (never commit to git)
4. **Implement rate limiting** for production endpoints
5. **Log security events** (failed auth attempts, etc.)
6. **Use webhook signatures** for additional security
7. **Validate all inputs** before processing

## 🐛 Troubleshooting

### "Connection refused"
- Check if server is running: `curl http://localhost:8000/health`
- Verify port is correct
- Check firewall rules

### "401 Unauthorized"
- Verify API key matches between ClawTick and server
- Check Authorization header format: `Bearer your-key`
- Ensure key is set in environment variables

### "500 Internal Server Error"
- Check server logs for detailed error
- Verify OpenAI API key is valid
- Ensure all dependencies are installed

### "Timeout"
- Optimize agent execution time
- Increase timeout (ClawTick timeout: 30s)
- Consider async processing for long tasks

## 📖 Additional Resources

- [ClawTick Documentation](https://clawtick.com/docs)
- [LangChain Docs](https://python.langchain.com/docs)
- [CrewAI Docs](https://docs.crewai.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## 💬 Support

- **GitHub Issues**: [clawtick/examples/issues](https://github.com/clawtick/examples/issues)
- **Discord**: [ClawTick Community](https://discord.gg/maKkUTCK)
- **Email**: support@clawtick.com

## 📄 License

MIT License - see individual example directories for details.

---

**Need help?** Check out our [detailed guide](https://github.com/clawtick/clawtick-examples/tree/main/INTEGRATION_TEMPLATES.md) or reach out on Discord!
