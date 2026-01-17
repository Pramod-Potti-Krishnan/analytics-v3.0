#!/bin/bash
# V2-only Test: Next Set of Chart Types
# bar_horizontal, doughnut, scatter, bubble, radar, polar_area

ANALYTICS_URL="https://analytics-v30-production.up.railway.app"
LAYOUT_URL="https://web-production-f0d13.up.railway.app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/v2_next_charts_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  V2-only Test: Next Chart Types"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout: $LAYOUT_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Chart types to test with their appropriate analytics_type and chart_type override
# Format: "analytics_type|chart_type|title"
CHART_CONFIGS=(
    "category_ranking|bar_horizontal|Category Performance Rankings"
    "market_share|doughnut|Market Share Distribution"
    "correlation_analysis|scatter|Correlation Analysis"
    "multidimensional_analysis|bubble|Multi-Dimensional Metrics"
    "multi_metric_comparison|radar|Performance Across Dimensions"
    "radial_composition|polar_area|Radial Composition View"
)

# Generate slides array
SLIDES_JSON="["

for i in "${!CHART_CONFIGS[@]}"; do
    CONFIG="${CHART_CONFIGS[$i]}"
    ANALYTICS_TYPE=$(echo "$CONFIG" | cut -d'|' -f1)
    CHART_TYPE=$(echo "$CONFIG" | cut -d'|' -f2)
    TITLE=$(echo "$CONFIG" | cut -d'|' -f3)
    SLIDE_NUM=$((i + 1))

    echo "--- [Slide $SLIDE_NUM] V2 - $CHART_TYPE (via $ANALYTICS_TYPE) ---"

    # Use the API with chart_type override in request body
    CHART_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/analytics/L02/$ANALYTICS_TYPE?use_synthetic=true" \
        -H "Content-Type: application/json" \
        -d "{
            \"presentation_id\": \"test-v2-next-charts\",
            \"slide_id\": \"slide-$SLIDE_NUM\",
            \"slide_number\": $SLIDE_NUM,
            \"narrative\": \"Analysis showing $CHART_TYPE visualization with key performance metrics.\",
            \"chart_type\": \"$CHART_TYPE\"
        }")

    # Save full response for debugging
    echo "$CHART_RESPONSE" | jq . > "$OUTPUT_DIR/slide_${SLIDE_NUM}_response.json"

    # Extract chart HTML using correct field name (chart_html, not element_3)
    CHART_HTML=$(echo "$CHART_RESPONSE" | jq -r '.content.chart_html // empty')

    if [ -z "$CHART_HTML" ]; then
        echo "  ERROR: No chart HTML returned"
        echo "  Response:"
        echo "$CHART_RESPONSE" | jq -r '.detail // .error // .message // "Unknown error"' | head -5
        continue
    fi

    # Save chart HTML for inspection
    echo "$CHART_HTML" > "$OUTPUT_DIR/slide_${SLIDE_NUM}_${CHART_TYPE}.html"

    # Check for canvas/svg ID
    CHART_ID=$(echo "$CHART_HTML" | grep -o 'id="chart-[^"]*"' | head -1)
    if [ -z "$CHART_ID" ]; then
        CHART_ID=$(echo "$CHART_HTML" | grep -o 'id="[^"]*"' | head -1)
    fi
    echo "  Chart ID: $CHART_ID"

    # Check for subtitle
    SUBTITLE=$(echo "$CHART_HTML" | grep -o '<strong>[^<]*</strong>' | head -1)
    echo "  Subtitle: $SUBTITLE"

    # Extract Key Insights using correct field name (body, not element_2)
    KEY_INSIGHTS=$(echo "$CHART_RESPONSE" | jq -r '.content.body // empty')

    if [ -z "$KEY_INSIGHTS" ]; then
        echo "  WARNING: No Key Insights in response"
    else
        echo "  Key Insights: Present"
    fi

    # Build V2 slide JSON with correct field names for Layout Service
    ESCAPED_CHART=$(echo "$CHART_HTML" | jq -Rs .)
    ESCAPED_INSIGHTS=$(echo "$KEY_INSIGHTS" | jq -Rs .)

    if [ $i -gt 0 ]; then
        SLIDES_JSON+=","
    fi

    # Use correct field names: chart_html, body (not element_3, element_2)
    # Also add slide_title, subtitle, logo for proper rendering
    SLIDES_JSON+="{
        \"layout\": \"V2-chart-text\",
        \"content\": {
            \"slide_title\": \"$TITLE\",
            \"subtitle\": \"$CHART_TYPE visualization - slide $SLIDE_NUM\",
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
    \"title\": \"V2 Next Charts Test - $TIMESTAMP\",
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

echo ""
echo "=============================================="
echo "  SUCCESS"
echo "=============================================="
echo "Presentation ID: $PRES_ID"
echo "URL: $LAYOUT_URL/p/$PRES_ID"
echo ""
echo "Chart Types Tested (V2 layout):"
for i in "${!CHART_CONFIGS[@]}"; do
    CONFIG="${CHART_CONFIGS[$i]}"
    CHART_TYPE=$(echo "$CONFIG" | cut -d'|' -f2)
    TITLE=$(echo "$CONFIG" | cut -d'|' -f3)
    echo "  Slide $((i + 1)): $CHART_TYPE - $TITLE"
done
echo ""
echo "Output: $OUTPUT_DIR"
