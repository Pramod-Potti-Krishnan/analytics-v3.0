# Analytics Microservice v3 - Tool Specifications

## Tool Architecture Overview

The Analytics Microservice v3 agent requires 4 ESSENTIAL tools that work together to create comprehensive chart generation with real-time WebSocket streaming. Each tool has a single, focused purpose with minimal parameters.

---

## Tool 1: Chart Generator

### Purpose
Generate matplotlib-based charts from data with specified visualization type and styling parameters.

### Implementation Pattern
```python
@agent.tool
async def chart_generator(
    ctx: RunContext[AgentDependencies],
    chart_type: str,
    data: Dict[str, Any],
    theme: str = "default"
) -> Dict[str, Any]:
    """
    Generate matplotlib chart from provided data and parameters.
    
    Args:
        chart_type: Type of chart (bar, line, pie, scatter, heatmap, etc.)
        data: Dictionary containing chart data (x, y, labels, values)
        theme: Visual theme to apply (default, dark, professional, colorful)
    
    Returns:
        Dictionary with chart image (base64), metadata, and generation status
    """
```

### Core Functionality
- Support 20+ chart types: bar, line, pie, scatter, heatmap, violin, box, histogram, area, treemap
- Accept structured data in standard format: `{"x": [...], "y": [...], "labels": [...]}`
- Apply matplotlib styling based on theme parameter
- Return base64-encoded PNG image with chart metadata
- Handle data validation and chart type compatibility

### Error Handling
- Invalid chart type → return error with supported types list
- Malformed data → return validation error with expected format
- Matplotlib rendering failure → return fallback chart with error message
- Memory/timeout issues → return simple error chart

---

## Tool 2: Data Synthesizer

### Purpose
Generate realistic datasets using LLM when user-provided data is incomplete or missing.

### Implementation Pattern
```python
@agent.tool
async def data_synthesizer(
    ctx: RunContext[AgentDependencies],
    data_description: str,
    sample_size: int = 50
) -> Dict[str, Any]:
    """
    Synthesize realistic dataset using LLM based on description.
    
    Args:
        data_description: Natural language description of desired data
        sample_size: Number of data points to generate (10-1000)
    
    Returns:
        Dictionary with synthesized data in chart-ready format
    """
```

### Core Functionality
- Generate realistic data based on natural language descriptions
- Support common data patterns: time series, categorical, numerical distributions
- Return data in standardized chart format: `{"x": [...], "y": [...], "categories": [...]}`
- Use OpenAI API to understand context and generate appropriate values
- Handle data relationships and realistic value ranges

### Error Handling
- Vague description → request more specific parameters
- Invalid sample size → clamp to 10-1000 range
- LLM API failure → return simple default dataset with warning
- JSON parsing error → return structured error response

---

## Tool 3: Theme Applier

### Purpose
Apply consistent visual themes and styling to matplotlib charts across all chart types.

### Implementation Pattern
```python
@agent.tool_plain
def theme_applier(
    chart_config: Dict[str, Any],
    theme_name: str,
    custom_colors: List[str] = None
) -> Dict[str, Any]:
    """
    Apply visual theme configuration to chart parameters.
    
    Args:
        chart_config: Base chart configuration dictionary
        theme_name: Theme to apply (default, dark, professional, colorful, minimal)
        custom_colors: Optional list of hex colors to override theme palette
    
    Returns:
        Updated chart configuration with theme styling applied
    """
```

### Core Functionality
- Pre-defined themes: default, dark, professional, colorful, minimal
- Apply consistent color palettes, fonts, grid styles, and spacing
- Support custom color overrides while maintaining theme consistency
- Return matplotlib-compatible styling configuration
- Handle theme inheritance and parameter merging

### Error Handling
- Unknown theme → fallback to "default" theme with warning
- Invalid custom colors → filter out invalid hex codes
- Configuration conflict → theme takes precedence over conflicting options
- Missing theme parameters → use matplotlib defaults

---

## Tool 4: Progress Streamer

### Purpose
Send real-time progress updates via WebSocket during chart generation process.

### Implementation Pattern
```python
@agent.tool
async def progress_streamer(
    ctx: RunContext[AgentDependencies],
    connection_id: str,
    progress_data: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Stream progress updates to WebSocket connection.
    
    Args:
        connection_id: WebSocket connection identifier
        progress_data: Progress information (stage, percentage, message)
    
    Returns:
        Dictionary indicating successful message delivery
    """
```

### Core Functionality
- Send structured progress messages via WebSocket
- Support progress stages: "data_processing", "chart_rendering", "theme_applying", "complete"
- Include percentage completion (0-100) and descriptive message
- Handle connection state validation before sending
- Maintain non-blocking operation for main chart generation

### Error Handling
- Invalid connection ID → log error but continue chart generation
- WebSocket connection closed → skip progress updates gracefully
- Message formatting error → send simple status message
- Network timeout → retry once then continue silently

---

## Tool Integration Pattern

### Typical Workflow
1. **Data Synthesizer** (if needed) → Generate missing data
2. **Progress Streamer** → Send "data_processing" update (25%)
3. **Theme Applier** → Apply visual styling
4. **Progress Streamer** → Send "theme_applying" update (50%)
5. **Chart Generator** → Create final chart
6. **Progress Streamer** → Send "chart_rendering" update (75%)
7. **Progress Streamer** → Send "complete" update (100%)

### Error Recovery
- If any tool fails, stream error status and attempt graceful degradation
- Always attempt to return some form of chart (even if basic error visualization)
- Log all errors for debugging while maintaining WebSocket communication

---

## Dependencies Required

### Python Packages
```python
# Chart generation
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
numpy>=1.24.0

# WebSocket streaming
websockets>=11.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Data processing
scipy>=1.10.0
plotly>=5.17.0  # For interactive charts if needed

# Base64 encoding
base64
io
```

### External Services
- OpenAI API for data synthesis
- Railway WebSocket infrastructure
- Matplotlib backend for chart rendering

---

## Testing Strategy

### Unit Tests
- Each tool tested in isolation with mock data
- Error handling scenarios for each tool
- Theme application consistency across chart types
- Data synthesis validation with various descriptions

### Integration Tests
- Full workflow: data synthesis → theme application → chart generation → progress streaming
- WebSocket connection handling
- Concurrent chart generation
- Memory usage and cleanup

### Performance Tests
- Chart generation time under 30 seconds
- WebSocket message delivery latency
- Memory usage with large datasets
- Concurrent connection limits

---

## Security Considerations

### Input Validation
- Sanitize chart type parameters to prevent code injection
- Validate data structure and size limits
- Restrict theme names to predefined options
- Validate WebSocket connection IDs

### Resource Limits
- Limit synthesized data sample sizes (max 1000 points)
- Timeout chart generation at 30 seconds
- Restrict matplotlib figure size and DPI
- Rate limit WebSocket messages per connection

---

Generated: 2025-09-01  
Archon Project ID: 9da83cf1-ab6b-4195-9e2c-699e24d44129

**Note**: These are PLANNING specifications for tool development. The main agent will implement the actual Python code based on these specifications during the implementation phase.