# Docker Setup for MCP Services

This guide explains how to run the MCP (Model Context Protocol) services using Docker.

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- At least 2GB RAM available

## Quick Start

### 1. Build and Run Services

```bash
# Build all Docker images
docker-compose build

# Start all MCP services in the background
docker-compose up -d

# View service logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 2. Verify Services Are Running

Each service will be accessible at:
- Math Service: `http://localhost:8000/mcp`
- Search Service: `http://localhost:8001/mcp`
- Trade Service: `http://localhost:8002/mcp`
- Prices Service: `http://localhost:8003/mcp`

Check health:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### 3. Run Trading Agent

Once all services are running:

```bash
# In another terminal
python main.py
```

## Service Details

### Math Service (Port 8000)
- Provides mathematical calculations
- Health check: `GET /health`
- Dockerfile: `agent_tools/Dockerfile.math`

### Search Service (Port 8001)
- Provides market research via Jina API
- Requires: `JINA_API_KEY` environment variable
- Health check: `GET /health`
- Dockerfile: `agent_tools/Dockerfile.search`

### Trade Service (Port 8002)
- Handles buy/sell operations
- Health check: `GET /health`
- Dockerfile: `agent_tools/Dockerfile.trade`

### Prices Service (Port 8003)
- Provides stock/crypto price lookups
- Health check: `GET /health`
- Dockerfile: `agent_tools/Dockerfile.prices`

## Environment Variables

Create a `.env` file in the project root:

```bash
JINA_API_KEY=your_jina_api_key
OPENAI_API_KEY=your_openai_api_key
ALPHAADVANTAGE_API_KEY=your_alpha_vantage_key
```

Docker Compose will automatically load these variables.

## Managing Services

```bash
# Stop all services
docker-compose down

# Stop a specific service
docker-compose stop math-service

# Start a specific service
docker-compose start math-service

# Restart a service
docker-compose restart search-service

# View logs for specific service
docker-compose logs search-service

# Follow logs in real-time
docker-compose logs -f trade-service
```

## Troubleshooting

### Service won't start
1. Check logs: `docker-compose logs service-name`
2. Verify environment variables are set
3. Ensure ports 8000-8003 are available
4. Check Docker has enough memory: `docker stats`

### Health check failing
- Wait longer for startup: services can take 10-15 seconds
- Check service logs for errors
- Verify all dependencies are installed

### Cannot connect to services from agent
- Ensure Docker network bridge is created: `docker network ls`
- Verify services are on same network: `docker-compose config`
- Check firewall settings

## Local Development

Run services locally without Docker:

```bash
# Terminal 1
python agent_tools/tool_math.py

# Terminal 2
python agent_tools/tool_jina_search.py

# Terminal 3
python agent_tools/tool_trade.py

# Terminal 4
python agent_tools/tool_get_price_local.py

# Terminal 5
python main.py
```

## CI/CD Integration

For GitHub Actions, use the Docker setup with services:

```yaml
services:
  math:
    image: ai-trader-math:latest
    ports:
      - 8000:8000
```

See `.github/workflows/hourly-trading.yml` for full setup.
