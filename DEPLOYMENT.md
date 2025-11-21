# Deployment Guide - Crypto MCP Server

This guide covers various deployment options for the Crypto MCP Server.

## Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring](#monitoring)

## Local Development

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd crypto-mcp-server

# Run setup script
python setup.py

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run server
python main.py
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest

# Start server
python main.py
```

## Production Deployment

### Prerequisites

- Python 3.9+
- Virtual environment
- Process manager (systemd, supervisor, or pm2)
- Reverse proxy (nginx or caddy) - optional

### Setup Steps

1. **Prepare Environment**
   ```bash
   # Create production directory
   mkdir -p /opt/crypto-mcp-server
   cd /opt/crypto-mcp-server

   # Clone repository
   git clone <repository-url> .

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   nano .env
   ```

   Production settings:
   ```env
   LOG_LEVEL=WARNING
   CACHE_TTL=60
   RATE_LIMIT_REQUESTS=20
   RATE_LIMIT_PERIOD=60
   DEFAULT_EXCHANGE=binance
   ```

3. **Create Systemd Service**

   Create `/etc/systemd/system/crypto-mcp-server.service`:
   ```ini
   [Unit]
   Description=Crypto MCP Server
   After=network.target

   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/crypto-mcp-server
   Environment="PATH=/opt/crypto-mcp-server/venv/bin"
   ExecStart=/opt/crypto-mcp-server/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable crypto-mcp-server
   sudo systemctl start crypto-mcp-server
   sudo systemctl status crypto-mcp-server
   ```

5. **View Logs**
   ```bash
   sudo journalctl -u crypto-mcp-server -f
   ```

## Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY crypto_mcp_server/ ./crypto_mcp_server/
COPY main.py .
COPY .env.example .env

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run server
CMD ["python", "main.py"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  crypto-mcp-server:
    build: .
    container_name: crypto-mcp-server
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
      - CACHE_TTL=60
      - RATE_LIMIT_REQUESTS=10
      - RATE_LIMIT_PERIOD=60
      - DEFAULT_EXCHANGE=binance
    volumes:
      - ./logs:/app/logs
    stdin_open: true
    tty: true
```

### Build and Run

```bash
# Build image
docker build -t crypto-mcp-server .

# Run container
docker run -it --rm crypto-mcp-server

# Or use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t2.micro or larger
   - Security group: Allow SSH (22)

2. **Connect and Setup**
   ```bash
   ssh ubuntu@<ec2-ip>

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python
   sudo apt install python3 python3-venv python3-pip -y

   # Clone and setup
   git clone <repository-url>
   cd crypto-mcp-server
   python3 setup.py
   ```

3. **Configure Systemd** (see Production Deployment)

### Google Cloud Platform

1. **Create Compute Engine Instance**
   ```bash
   gcloud compute instances create crypto-mcp-server \
       --image-family=ubuntu-2204-lts \
       --image-project=ubuntu-os-cloud \
       --machine-type=e2-micro
   ```

2. **SSH and Setup**
   ```bash
   gcloud compute ssh crypto-mcp-server
   # Follow production deployment steps
   ```

### Azure VM

1. **Create VM**
   ```bash
   az vm create \
       --resource-group myResourceGroup \
       --name crypto-mcp-server \
       --image UbuntuLTS \
       --size Standard_B1s \
       --admin-username azureuser
   ```

2. **SSH and Setup**
   ```bash
   ssh azureuser@<vm-ip>
   # Follow production deployment steps
   ```

## Monitoring

### Health Checks

Create `healthcheck.py`:
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def health_check():
    try:
        server_params = StdioServerParameters(
            command="python", args=["main.py"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    exit(0 if result else 1)
```

### Logging

Configure logging in production:
```env
LOG_LEVEL=WARNING
```

Rotate logs with logrotate:
```
/opt/crypto-mcp-server/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Metrics

Monitor:
- Cache hit rate
- Request rate
- Error rate
- Response time
- API rate limit usage

### Alerts

Set up alerts for:
- Service downtime
- High error rate
- Rate limit exceeded
- Low cache hit rate

## Security Best Practices

1. **Use Environment Variables**
   - Never commit API keys
   - Use `.env` file or secrets manager

2. **Limit Permissions**
   - Run as non-root user
   - Minimal file permissions

3. **Network Security**
   - Use firewall rules
   - Enable only required ports
   - Use VPN for sensitive deployments

4. **Update Regularly**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

5. **Backup Configuration**
   - Backup `.env` file
   - Version control configuration

## Troubleshooting

### Server Won't Start

```bash
# Check logs
journalctl -u crypto-mcp-server -n 50

# Verify Python version
python --version

# Check dependencies
pip list

# Test manually
python main.py
```

### High Memory Usage

```bash
# Monitor resources
top -p $(pgrep -f main.py)

# Reduce cache size
# Edit .env: MAX_CACHE_SIZE=500
```

### Rate Limiting Issues

```bash
# Increase rate limits
# Edit .env: RATE_LIMIT_REQUESTS=20
```

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:
```nginx
upstream crypto_mcp {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

### Vertical Scaling

Increase resources:
- More RAM for larger cache
- More CPU for concurrent requests

## Backup and Recovery

### Backup

```bash
# Backup configuration
tar -czf backup.tar.gz .env crypto_mcp_server/

# Backup to S3 (AWS)
aws s3 cp backup.tar.gz s3://my-bucket/backups/
```

### Recovery

```bash
# Restore from backup
tar -xzf backup.tar.gz

# Restart service
sudo systemctl restart crypto-mcp-server
```

## Performance Tuning

### Cache Optimization

```env
# For high-traffic
CACHE_TTL=30
MAX_CACHE_SIZE=5000

# For low-latency
CACHE_TTL=5
```

### Rate Limiting

```env
# Conservative
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60

# Aggressive (if exchange allows)
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_PERIOD=60
```

## Support

For deployment issues:
- Check logs: `journalctl -u crypto-mcp-server`
- Review documentation: README.md
- Open issue on GitHub

---

**Last Updated**: November 21, 2025
