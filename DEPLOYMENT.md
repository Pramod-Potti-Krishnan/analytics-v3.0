# Deployment Guide - Analytics Microservice v3

This guide provides step-by-step instructions for deploying the Analytics Microservice v3 to Railway with WebSocket support.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub account (for automatic deployments)
- OpenAI API key

## Quick Deploy to Railway

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub Repository**
   ```bash
   git add .
   git commit -m "Add Analytics Microservice v3"
   git push origin main
   ```

2. **Create New Railway Project**
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Choose the branch to deploy

3. **Configure Environment Variables**
   - In Railway dashboard, go to your service
   - Click "Variables" tab
   - Add the following variables:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   RAILWAY_ENVIRONMENT=production
   WEBSOCKET_PORT=${{PORT}}
   MAX_CONCURRENT_CONNECTIONS=100
   CHART_GENERATION_TIMEOUT=30
   MAX_CHART_SIZE_MB=10
   LOG_LEVEL=INFO
   ```

4. **Deploy**
   - Railway will automatically build and deploy using the Dockerfile
   - Monitor the deployment logs
   - Once deployed, get your service URL from the dashboard

### Option 2: Deploy Using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   cd agents/analytics_microservice_v3
   railway init
   ```

4. **Link to Service**
   ```bash
   railway link
   ```

5. **Set Environment Variables**
   ```bash
   railway variables set OPENAI_API_KEY=your-openai-api-key-here
   railway variables set RAILWAY_ENVIRONMENT=production
   railway variables set WEBSOCKET_PORT=\${{PORT}}
   railway variables set MAX_CONCURRENT_CONNECTIONS=100
   ```

6. **Deploy**
   ```bash
   railway up
   ```

## WebSocket Configuration

Railway automatically handles WebSocket connections. Your service URL will be:
- HTTP: `https://your-service.railway.app`
- WebSocket: `wss://your-service.railway.app/ws`

## Testing the Deployment

### 1. Health Check
```bash
curl https://your-service.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00.000000",
  "environment": "production",
  "active_connections": 0,
  "max_connections": 100
}
```

### 2. WebSocket Test
```python
import asyncio
import json
import websockets

async def test_production():
    uri = "wss://your-service.railway.app/ws"
    
    async with websockets.connect(uri) as websocket:
        # Send test request
        request = {
            "type": "analytics_request",
            "request_id": "test-prod-001",
            "content": "Test chart generation",
            "chart_type": "bar_vertical"
        }
        
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response type: {data['type']}")

asyncio.run(test_production())
```

## Monitoring

### Railway Dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and rollback options
- **Observability**: Request metrics and error tracking

### Application Logs
View logs in Railway dashboard or via CLI:
```bash
railway logs
```

### Health Monitoring
Set up monitoring for the `/health` endpoint:
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- Railway's built-in health checks

## Scaling

### Horizontal Scaling
Update `railway.json` to enable auto-scaling:
```json
{
  "deploy": {
    "replicas": 2,
    "maxReplicas": 5,
    "minReplicas": 1
  }
}
```

### Vertical Scaling
Upgrade your Railway plan for more resources:
- Hobby: $5/month - 512MB RAM, 0.5 vCPU
- Pro: $20/month - 8GB RAM, 2 vCPU
- Team: Custom resources

## Environment-Specific Configuration

### Development
```env
RAILWAY_ENVIRONMENT=development
LOG_LEVEL=DEBUG
DEBUG=true
```

### Staging
```env
RAILWAY_ENVIRONMENT=staging
LOG_LEVEL=INFO
DEBUG=false
```

### Production
```env
RAILWAY_ENVIRONMENT=production
LOG_LEVEL=WARNING
DEBUG=false
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Fails**
   - Check if WebSocket port is correctly set to `${{PORT}}`
   - Verify Railway supports WebSocket (it does by default)
   - Check client is using `wss://` protocol

2. **OpenAI API Errors**
   - Verify OPENAI_API_KEY is set correctly
   - Check API key has sufficient credits
   - Monitor rate limiting

3. **Chart Generation Timeout**
   - Increase CHART_GENERATION_TIMEOUT
   - Check matplotlib backend is set to "Agg"
   - Monitor memory usage

4. **High Memory Usage**
   - Matplotlib can be memory-intensive
   - Consider upgrading Railway plan
   - Implement chart caching (Redis)

### Debug Mode
Enable debug mode for verbose logging:
```bash
railway variables set DEBUG=true
railway variables set LOG_LEVEL=DEBUG
railway up
```

## Rollback

If deployment fails, rollback to previous version:

1. **Via Dashboard**
   - Go to Deployments tab
   - Click on previous successful deployment
   - Click "Rollback to this deployment"

2. **Via CLI**
   ```bash
   railway deployments
   railway rollback <deployment-id>
   ```

## Custom Domain

Add a custom domain in Railway:

1. Go to Settings → Domains
2. Add your domain
3. Update DNS records as instructed
4. SSL certificate is automatically provisioned

## CI/CD Integration

### GitHub Actions
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
    paths:
      - 'agents/analytics_microservice_v3/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: analytics-microservice-v3
```

### Get Railway Token
1. Go to Railway Dashboard → Account Settings
2. Generate new token
3. Add to GitHub Secrets as `RAILWAY_TOKEN`

## Security Best Practices

1. **API Keys**
   - Never commit API keys to repository
   - Use Railway's environment variables
   - Rotate keys regularly

2. **WebSocket Security**
   - Implement rate limiting
   - Add authentication if needed
   - Monitor for abuse

3. **Dependencies**
   - Keep dependencies updated
   - Use specific version pins
   - Regular security audits

## Performance Optimization

1. **Caching**
   - Add Redis for chart caching
   - Cache synthesized data
   - Implement CDN for static assets

2. **Connection Pooling**
   - Reuse OpenAI client connections
   - Implement WebSocket connection pooling
   - Database connection pooling (if added)

3. **Resource Limits**
   - Set appropriate timeout values
   - Limit chart size and complexity
   - Implement request queuing

## Support

For Railway-specific issues:
- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
- Railway Status: https://status.railway.app

For application issues:
- Check application logs in Railway dashboard
- Review error messages in WebSocket responses
- Create issue in GitHub repository

## Cost Estimation

Railway pricing (as of 2025):
- **Hobby Plan**: $5/month
  - 512MB RAM, 0.5 vCPU
  - $0.000463/GB egress
  - Suitable for development/testing

- **Pro Plan**: $20/month
  - 8GB RAM, 2 vCPU
  - $0.000463/GB egress
  - Suitable for production

- **Estimated Monthly Cost**:
  - Base: $20 (Pro plan)
  - Egress (10GB): ~$0.05
  - Total: ~$20.05/month

## Next Steps

1. Set up monitoring and alerting
2. Implement authentication if needed
3. Add Redis caching for improved performance
4. Set up staging environment
5. Configure automated backups
6. Implement rate limiting
7. Add custom domain
8. Set up CI/CD pipeline

---

**Successfully Deployed?** Your Analytics Microservice v3 is now live and ready to generate charts via WebSocket! 🎉