"""
Prompts for Data Ingestion Agent.

Contains prompt templates for LLM-based intent parsing
and other natural language tasks.
"""

# Intent parsing system prompt
INTENT_PARSING_SYSTEM_PROMPT = """You are a data visualization intent parser. Your task is to extract the user's visualization intent from their natural language description.

Given the user's narrative and available data columns, determine:

1. **Intent Type** - What type of visualization they want:
   - show_distribution: Distribution of values (histogram, bar chart)
   - compare_values: Comparison between categories (bar chart, grouped bars)
   - show_trend: Trends over time (line chart, area chart)
   - show_composition: Parts of a whole (pie, doughnut)
   - show_correlation: Relationship between variables (scatter plot)
   - show_ranking: Ranking/ordering of items (horizontal bars)
   - aggregate_data: Summary statistics (total, average)
   - filter_data: Filter and display subset
   - unknown: Intent unclear

2. **Target Columns** - Which columns contain the values to visualize

3. **Group By Columns** - Which columns to group/categorize by

4. **Aggregation** - What aggregation function to apply (sum, avg, count, min, max)

5. **Chart Type** - Suggested chart type:
   - line: For trends over time
   - bar_vertical: For category comparison
   - bar_horizontal: For many categories or long labels
   - pie: For composition (<=8 categories)
   - doughnut: Alternative to pie
   - scatter: For correlation between two numeric values
   - area: For cumulative trends
   - waterfall: For showing how values change

Respond with a valid JSON object containing these fields."""

# Intent parsing user prompt template
INTENT_PARSING_USER_TEMPLATE = """Available columns in the dataset:
{columns_context}

Data summary:
- Rows: {row_count}
- Numeric columns: {numeric_columns}
- Categorical columns: {categorical_columns}
- Datetime columns: {datetime_columns}

User's request: "{narrative}"

Parse the intent and return JSON with:
- intent_type: string (one of the intent types)
- confidence: float (0-1)
- target_columns: array of column names to visualize
- group_by_columns: array of columns to group by
- filter_columns: array of columns in any filters
- aggregation_function: string or null (sum, avg, count, min, max)
- filter_expression: string or null
- suggested_chart_type: string or null
- chart_title_suggestion: string

Return JSON only, no explanation."""

# Chart title generation prompt
CHART_TITLE_PROMPT = """Generate a concise, informative chart title based on:

Visualization type: {chart_type}
Data columns: {columns}
User request: "{narrative}"

The title should:
1. Be clear and descriptive (3-8 words)
2. Describe what is being shown
3. Include the main metric or dimension

Return only the title, no quotes or explanation."""

# Alternative suggestion prompt
ALTERNATIVES_PROMPT = """Given this visualization:

Current chart type: {chart_type}
Data points: {num_points}
Has negative values: {has_negative}
Has multiple series: {has_series}
Detected patterns: {patterns}

Suggest up to 3 alternative chart types that could work well for this data.
For each alternative, explain why it might be better.

Return as JSON array with objects containing:
- chart_type: string
- reason: string
- confidence: float (0-1)"""

# Data quality assessment prompt
DATA_QUALITY_PROMPT = """Analyze this data for visualization:

Columns: {columns}
Row count: {row_count}
Null percentage: {null_percentage}%
Duplicate rows: {duplicate_rows}

Column statistics:
{column_stats}

Identify any data quality issues that might affect visualization:
1. Missing data problems
2. Data type issues
3. Outliers
4. Inconsistent values
5. Recommendations for cleaning

Return as JSON with:
- issues: array of issue descriptions
- severity: "low", "medium", or "high"
- recommendations: array of suggested fixes"""
