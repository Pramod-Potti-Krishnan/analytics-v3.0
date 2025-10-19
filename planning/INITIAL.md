# Analytics Microservice v3 - Simple Requirements

## What This Agent Does
A Pydantic AI-powered analytics microservice that generates comprehensive charts and visualizations through a WebSocket API with real-time progress streaming. Converts data requests into matplotlib-based charts with LLM-enhanced data synthesis and theme customization.

## Core Features (MVP)

1. **WebSocket Chart Generation**: Real-time chart creation with streaming progress updates during generation process
2. **LLM-Enhanced Data Processing**: Synthesize realistic datasets when user data is incomplete or generate insights from provided data
3. **Multi-Chart Support**: Generate 20+ chart types (bar, line, pie, scatter, heatmap, violin, etc.) with intelligent type selection
4. **Theme Customization**: Apply consistent visual themes and styling across all chart types

## Technical Setup

### Model
- **Provider**: OpenAI
- **Model**: gpt-4o-mini
- **Why**: Fast processing for data synthesis and chart type recommendations, cost-effective for high-volume analytics requests

### Required Tools
1. **chart_generator**: Create matplotlib charts with specified type, data, and theme parameters
2. **data_synthesizer**: Generate realistic datasets using LLM when user data is insufficient
3. **theme_applier**: Apply consistent visual themes and color schemes to charts
4. **progress_streamer**: Send real-time updates via WebSocket during chart generation

### External Services
- **OpenAI API**: For data synthesis and insights generation
- **Railway WebSocket**: Deployment platform with WebSocket support
- **Matplotlib**: Chart rendering engine

## Environment Variables
```bash
OPENAI_API_KEY=your-openai-api-key
RAILWAY_ENVIRONMENT=production
WEBSOCKET_PORT=8080
MAX_CONCURRENT_CONNECTIONS=100
CHART_GENERATION_TIMEOUT=30
```

## Success Criteria
- [ ] WebSocket API accepts chart generation requests and maintains bidirectional communication
- [ ] Streams progress updates during chart creation (data processing, rendering, completion)
- [ ] Generates high-quality charts for 20+ different visualization types
- [ ] Handles both user-provided data and LLM-synthesized datasets
- [ ] Applies consistent themes and returns chart as base64 image or SVG
- [ ] Supports multiple concurrent WebSocket connections without blocking

## Assumptions Made
- Stateless service design (no data persistence required)
- Chart output format: base64-encoded PNG or SVG strings
- WebSocket connections handle timeouts gracefully (30 second limit)
- Rate limiting handled at Railway infrastructure level
- LLM data synthesis for missing or incomplete datasets
- Standard matplotlib dependencies for chart rendering
- JSON-based WebSocket message protocol

---
Generated: 2025-09-01
Archon Project ID: 9da83cf1-ab6b-4195-9e2c-699e24d44129
Note: This is an MVP focused on core analytics and WebSocket functionality. Advanced features like caching, advanced statistical analysis, and custom chart templates can be added after the basic agent works.