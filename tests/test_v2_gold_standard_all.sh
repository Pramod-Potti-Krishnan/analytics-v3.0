#!/bin/bash
# V2 Gold Standard Test: All 9 Approved Chart Types
# Tests: line, bar_vertical, pie, bar_horizontal, doughnut, scatter, bubble, polar_area, radar

ANALYTICS_URL="https://analytics-v30-production.up.railway.app"
LAYOUT_URL="https://web-production-f0d13.up.railway.app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/v2_gold_standard_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  V2 Gold Standard Test: All 9 Chart Types"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout: $LAYOUT_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# All 9 gold standard charts
# Format: "analytics_type|chart_type|title"
CHART_CONFIGS=(
    # First set (basic charts)
    "revenue_over_time|line|Revenue Trends Over Time"
    "category_ranking|bar_vertical|Department Performance Rankings"
    "market_share|pie|Market Share Distribution"
    # Second set (next charts)
    "category_ranking|bar_horizontal|Category Performance (Horizontal)"
    "market_share|doughnut|Market Share (Doughnut)"
    "correlation_analysis|scatter|Correlation Analysis"
    "multidimensional_analysis|bubble|Multi-Dimensional Metrics"
    "radial_composition|polar_area|Radial Composition View"
    "multi_metric_comparison|radar|Performance Across Dimensions"
)

# Generate slides array
SLIDES_JSON="["
SUCCESS_COUNT=0
FAIL_COUNT=0

for i in "${!CHART_CONFIGS[@]}"; do
    CONFIG="${CHART_CONFIGS[$i]}"
    ANALYTICS_TYPE=$(echo "$CONFIG" | cut -d'|' -f1)
    CHART_TYPE=$(echo "$CONFIG" | cut -d'|' -f2)
    TITLE=$(echo "$CONFIG" | cut -d'|' -f3)
    SLIDE_NUM=$((i + 1))

    echo "--- [Slide $SLIDE_NUM] $CHART_TYPE (via $ANALYTICS_TYPE) ---"

    # Call analytics API
    CHART_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/analytics/L02/$ANALYTICS_TYPE?use_synthetic=true" \
        -H "Content-Type: application/json" \
        -d "{
            \"presentation_id\": \"v2-gold-standard-test\",
            \"slide_id\": \"slide-$SLIDE_NUM\",
            \"slide_number\": $SLIDE_NUM,
            \"narrative\": \"Analysis showing $CHART_TYPE visualization with key performance metrics.\",
            \"chart_type\": \"$CHART_TYPE\"
        }")

    # Save full response
    echo "$CHART_RESPONSE" | jq . > "$OUTPUT_DIR/slide_${SLIDE_NUM}_${CHART_TYPE}_response.json"

    # Extract chart HTML
    CHART_HTML=$(echo "$CHART_RESPONSE" | jq -r '.content.chart_html // empty')

    if [ -z "$CHART_HTML" ]; then
        echo "  ERROR: No chart HTML returned"
        ERROR_MSG=$(echo "$CHART_RESPONSE" | jq -r '.metadata.error // .detail // .error // "Unknown error"')
        echo "  Error: $ERROR_MSG"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Save chart HTML
    echo "$CHART_HTML" > "$OUTPUT_DIR/slide_${SLIDE_NUM}_${CHART_TYPE}.html"

    # Check for canvas ID
    CHART_ID=$(echo "$CHART_HTML" | grep -o 'id="chart-[^"]*"' | head -1)
    echo "  Chart ID: $CHART_ID"

    # Check for Key Insights
    KEY_INSIGHTS=$(echo "$CHART_RESPONSE" | jq -r '.content.body // empty')
    if [ -n "$KEY_INSIGHTS" ]; then
        echo "  Key Insights: Present"
    else
        echo "  Key Insights: Missing"
    fi

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

    # Build slide JSON
    ESCAPED_CHART=$(echo "$CHART_HTML" | jq -Rs .)
    ESCAPED_INSIGHTS=$(echo "$KEY_INSIGHTS" | jq -Rs .)

    if [ $i -gt 0 ]; then
        SLIDES_JSON+=","
    fi

    SLIDES_JSON+="{
        \"layout\": \"V2-chart-text\",
        \"content\": {
            \"slide_title\": \"$TITLE\",
            \"subtitle\": \"$CHART_TYPE visualization - Gold Standard\",
            \"chart_html\": $ESCAPED_CHART,
            \"body\": $ESCAPED_INSIGHTS,
            \"logo\": \" \"
        }
    }"
done

SLIDES_JSON+="]"

echo ""
echo "--- Creating Presentation ---"

# Create presentation request
REQUEST_JSON="{
    \"title\": \"V2 Gold Standard - All 9 Charts - $TIMESTAMP\",
    \"theme\": \"starter\",
    \"slides\": $SLIDES_JSON
}"

echo "$REQUEST_JSON" | jq . > "$OUTPUT_DIR/presentation_request.json"

# Create presentation
PRES_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_JSON")

echo "$PRES_RESPONSE" | jq . > "$OUTPUT_DIR/presentation_response.json"

PRES_ID=$(echo "$PRES_RESPONSE" | jq -r '.id // .presentation_id // empty')

if [ -z "$PRES_ID" ]; then
    echo ""
    echo "ERROR: Failed to create presentation"
    echo "$PRES_RESPONSE" | jq .
    exit 1
fi

PRES_URL="$LAYOUT_URL/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  RESULTS"
echo "=============================================="
echo "Success: $SUCCESS_COUNT / 9"
echo "Failed:  $FAIL_COUNT / 9"
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $PRES_URL"
echo ""
echo "Gold Standard Charts (V2-chart-text layout):"
echo ""
for i in "${!CHART_CONFIGS[@]}"; do
    CONFIG="${CHART_CONFIGS[$i]}"
    CHART_TYPE=$(echo "$CONFIG" | cut -d'|' -f2)
    TITLE=$(echo "$CONFIG" | cut -d'|' -f3)
    echo "  Slide $((i + 1)): $CHART_TYPE - $TITLE"
done
echo ""
echo "Output: $OUTPUT_DIR"
echo ""

# Return URL for opening
echo "$PRES_URL"
