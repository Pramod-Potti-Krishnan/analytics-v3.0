#!/bin/bash
# Test Script for Atomic Chart Endpoints (v3.5.0)
# Tests all 14 gold standard chart types

# Configuration
ANALYTICS_URL="${ANALYTICS_URL:-http://localhost:8080}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_charts_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Atomic Chart Endpoints Test Suite (v3.5.0)"
echo "=============================================="
echo "Analytics URL: $ANALYTICS_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Test catalog endpoint first
echo "--- Testing Catalog Endpoint ---"
CATALOG_RESPONSE=$(curl -s "$ANALYTICS_URL/api/v1/charts/atomic/catalog")
echo "$CATALOG_RESPONSE" | jq . > "$OUTPUT_DIR/catalog.json" 2>/dev/null

CHART_COUNT=$(echo "$CATALOG_RESPONSE" | jq -r '.count // 0')
echo "Available chart types: $CHART_COUNT"
echo ""

# All 14 gold standard chart types
CHART_TYPES=(
    "line"
    "bar_vertical"
    "bar_horizontal"
    "pie"
    "doughnut"
    "scatter"
    "bubble"
    "polar_area"
    "radar"
    "area"
    "area_stacked"
    "bar_grouped"
    "bar_stacked"
    "waterfall"
)

# Narratives for each chart type
declare -A NARRATIVES=(
    ["line"]="Show quarterly revenue growth for 2024"
    ["bar_vertical"]="Compare department performance rankings"
    ["bar_horizontal"]="Top 10 products by revenue"
    ["pie"]="Market share distribution by company"
    ["doughnut"]="Budget allocation by department"
    ["scatter"]="Customer satisfaction vs revenue correlation"
    ["bubble"]="Product positioning by revenue, growth, and market size"
    ["polar_area"]="Seasonal sales patterns throughout the year"
    ["radar"]="Team performance across 8 key metrics"
    ["area"]="Cumulative revenue over 12 months"
    ["area_stacked"]="Revenue breakdown by region over time"
    ["bar_grouped"]="Q1 vs Q2 performance by product line"
    ["bar_stacked"]="Sales composition by channel per quarter"
    ["waterfall"]="Net income bridge from revenue to profit"
)

SUCCESS_COUNT=0
FAIL_COUNT=0

echo "--- Testing All 14 Chart Types ---"
echo ""

for chart_type in "${CHART_TYPES[@]}"; do
    NARRATIVE="${NARRATIVES[$chart_type]}"
    echo "Testing: $chart_type"
    echo "  Narrative: $NARRATIVE"

    # Test without insights
    RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"narrative\": \"$NARRATIVE\",
            \"include_insights\": false,
            \"width\": 850,
            \"height\": 500
        }")

    echo "$RESPONSE" | jq . > "$OUTPUT_DIR/${chart_type}_response.json" 2>/dev/null

    # Check success
    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    ELEMENT_ID=$(echo "$RESPONSE" | jq -r '.element_id // "none"')
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
    DATA_COUNT=$(echo "$RESPONSE" | jq -r '.data_used | length // 0')

    if [ "$SUCCESS" = "true" ]; then
        echo "  Result: SUCCESS"
        echo "  Element ID: $ELEMENT_ID"
        echo "  Data Points: $DATA_COUNT"
        echo "  Generation Time: ${GEN_TIME}ms"

        # Extract and save chart HTML
        echo "$RESPONSE" | jq -r '.chart_html // empty' > "$OUTPUT_DIR/${chart_type}.html"

        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  Result: FAILED"
        ERROR=$(echo "$RESPONSE" | jq -r '.detail.message // .error // "Unknown error"')
        echo "  Error: $ERROR"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo ""
done

echo "--- Testing With Insights ---"
echo ""

# Test line chart with insights
echo "Testing: line (with insights)"
RESPONSE_INSIGHTS=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/line" \
    -H "Content-Type: application/json" \
    -d "{
        \"narrative\": \"Show quarterly revenue growth for 2024 with key business insights\",
        \"include_insights\": true,
        \"width\": 850,
        \"height\": 500
    }")

echo "$RESPONSE_INSIGHTS" | jq . > "$OUTPUT_DIR/line_with_insights_response.json" 2>/dev/null

SUCCESS=$(echo "$RESPONSE_INSIGHTS" | jq -r '.success // false')
HAS_INSIGHTS=$(echo "$RESPONSE_INSIGHTS" | jq -r '.insights_html // "null"')

if [ "$SUCCESS" = "true" ] && [ "$HAS_INSIGHTS" != "null" ]; then
    echo "  Result: SUCCESS (with insights)"
    echo "$RESPONSE_INSIGHTS" | jq -r '.chart_html // empty' > "$OUTPUT_DIR/line_with_insights_chart.html"
    echo "$RESPONSE_INSIGHTS" | jq -r '.insights_html // empty' > "$OUTPUT_DIR/line_with_insights_panel.html"
else
    echo "  Result: FAILED or missing insights"
fi
echo ""

# Test with custom title
echo "Testing: bar_vertical (with custom title)"
RESPONSE_TITLE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/bar_vertical" \
    -H "Content-Type: application/json" \
    -d "{
        \"narrative\": \"Department rankings\",
        \"chart_title\": \"Q4 2024 Department Performance\",
        \"include_insights\": false,
        \"width\": 900,
        \"height\": 600
    }")

echo "$RESPONSE_TITLE" | jq . > "$OUTPUT_DIR/bar_vertical_custom_title.json" 2>/dev/null

TITLE=$(echo "$RESPONSE_TITLE" | jq -r '.chart_title // "none"')
echo "  Chart Title: $TITLE"
echo ""

# Test invalid chart type
echo "Testing: invalid_chart (should fail)"
RESPONSE_INVALID=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/invalid_chart" \
    -H "Content-Type: application/json" \
    -d "{\"narrative\": \"Test invalid type\"}")

echo "$RESPONSE_INVALID" | jq . > "$OUTPUT_DIR/invalid_chart_response.json" 2>/dev/null

ERROR_CODE=$(echo "$RESPONSE_INVALID" | jq -r '.detail.error_code // "none"')
if [ "$ERROR_CODE" = "INVALID_CHART_TYPE" ]; then
    echo "  Result: Correctly rejected with INVALID_CHART_TYPE"
else
    echo "  Result: Unexpected response"
fi
echo ""

# Generate combined preview HTML
echo "--- Generating Preview HTML ---"
cat > "$OUTPUT_DIR/preview.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Atomic Charts Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <style>
        body { font-family: system-ui; padding: 20px; background: #f5f5f5; }
        h1 { color: #1f2937; }
        .chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .chart-card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .chart-title { font-weight: 600; margin-bottom: 12px; color: #374151; }
        iframe { width: 100%; height: 400px; border: none; }
    </style>
</head>
<body>
    <h1>Atomic Charts Test Preview</h1>
    <p>Generated: TIMESTAMP</p>
    <div class="chart-grid">
EOF

for chart_type in "${CHART_TYPES[@]}"; do
    if [ -f "$OUTPUT_DIR/${chart_type}.html" ]; then
        cat >> "$OUTPUT_DIR/preview.html" << EOF
        <div class="chart-card">
            <div class="chart-title">$chart_type</div>
            <iframe srcdoc="$(cat "$OUTPUT_DIR/${chart_type}.html" | sed 's/"/\&quot;/g')"></iframe>
        </div>
EOF
    fi
done

cat >> "$OUTPUT_DIR/preview.html" << 'EOF'
    </div>
</body>
</html>
EOF

# Replace timestamp placeholder
sed -i '' "s/TIMESTAMP/$TIMESTAMP/" "$OUTPUT_DIR/preview.html" 2>/dev/null || \
sed -i "s/TIMESTAMP/$TIMESTAMP/" "$OUTPUT_DIR/preview.html" 2>/dev/null

echo ""
echo "=============================================="
echo "  TEST RESULTS"
echo "=============================================="
echo "Success: $SUCCESS_COUNT / ${#CHART_TYPES[@]}"
echo "Failed:  $FAIL_COUNT / ${#CHART_TYPES[@]}"
echo ""
echo "Output: $OUTPUT_DIR"
echo "Preview: $OUTPUT_DIR/preview.html"
echo ""

# Return exit code based on results
if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
else
    exit 0
fi
