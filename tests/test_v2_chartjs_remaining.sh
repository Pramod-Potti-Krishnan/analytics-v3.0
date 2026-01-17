#!/bin/bash
# V2 Test: Remaining Chart.js Chart Types (beyond gold standard)
# Tests: area, stacked_area, grouped_bar, stacked_bar, waterfall, mixed, boxplot, candlestick, treemap, heatmap

ANALYTICS_URL="https://analytics-v30-production.up.railway.app"
LAYOUT_URL="https://web-production-f0d13.up.railway.app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/v2_chartjs_remaining_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  V2 Test: Remaining Chart.js Types"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout: $LAYOUT_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Remaining Chart.js charts (beyond gold standard)
# Format: "analytics_type|chart_type|title"
# Note: Use underscore naming (area_stacked, bar_grouped, bar_stacked)
# Note: Only charts supported by synthetic data generator are included
CHART_CONFIGS=(
    # Standard Chart.js types that work with synthetic data
    "revenue_over_time|area|Area Chart - Trends"
    "revenue_over_time|area_stacked|Stacked Area - Cumulative Trends"
    "category_ranking|bar_grouped|Grouped Bar - Multi-Series Comparison"
    "category_ranking|bar_stacked|Stacked Bar - Cumulative Categories"
    "revenue_over_time|waterfall|Waterfall - Sequential Changes"
    # Note: mixed, boxplot, candlestick, treemap, heatmap require real data
    # They are not supported by the synthetic data generator yet
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
            \"presentation_id\": \"v2-chartjs-remaining-test\",
            \"slide_id\": \"slide-$SLIDE_NUM\",
            \"slide_number\": $SLIDE_NUM,
            \"narrative\": \"Analysis showing $CHART_TYPE visualization with performance metrics.\",
            \"chart_type\": \"$CHART_TYPE\"
        }")

    # Save full response
    echo "$CHART_RESPONSE" | jq . > "$OUTPUT_DIR/slide_${SLIDE_NUM}_${CHART_TYPE}_response.json" 2>/dev/null

    # Extract chart HTML
    CHART_HTML=$(echo "$CHART_RESPONSE" | jq -r '.content.chart_html // empty')

    if [ -z "$CHART_HTML" ]; then
        echo "  ERROR: No chart HTML returned"
        ERROR_MSG=$(echo "$CHART_RESPONSE" | jq -r '.metadata.error // .detail // .error // "Unknown error"' 2>/dev/null)
        echo "  Error: $ERROR_MSG"
        FAIL_COUNT=$((FAIL_COUNT + 1))

        # Still add a placeholder slide for failed charts
        if [ $i -gt 0 ]; then
            SLIDES_JSON+=","
        fi
        SLIDES_JSON+="{
            \"layout\": \"V2-chart-text\",
            \"content\": {
                \"slide_title\": \"$TITLE - FAILED\",
                \"subtitle\": \"$CHART_TYPE - Error\",
                \"chart_html\": \"<div style='padding: 40px; color: red;'>Error: $ERROR_MSG</div>\",
                \"body\": \"<div style='padding: 20px;'>Chart generation failed</div>\",
                \"logo\": \" \"
            }
        }"
        continue
    fi

    # Save chart HTML
    echo "$CHART_HTML" > "$OUTPUT_DIR/slide_${SLIDE_NUM}_${CHART_TYPE}.html"

    # Check for canvas/svg ID
    CHART_ID=$(echo "$CHART_HTML" | grep -o 'id="chart-[^"]*"' | head -1)
    if [ -z "$CHART_ID" ]; then
        CHART_ID=$(echo "$CHART_HTML" | grep -o 'id="[^"]*"' | head -1)
    fi
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
            \"subtitle\": \"$CHART_TYPE visualization test\",
            \"chart_html\": $ESCAPED_CHART,
            \"body\": $ESCAPED_INSIGHTS,
            \"logo\": \" \"
        }
    }"
done

SLIDES_JSON+="]"

TOTAL_CHARTS=${#CHART_CONFIGS[@]}

echo ""
echo "--- Creating Presentation ---"

# Create presentation request
REQUEST_JSON="{
    \"title\": \"V2 Chart.js Remaining Types - $TIMESTAMP\",
    \"theme\": \"starter\",
    \"slides\": $SLIDES_JSON
}"

echo "$REQUEST_JSON" | jq . > "$OUTPUT_DIR/presentation_request.json" 2>/dev/null

# Create presentation
PRES_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_JSON")

echo "$PRES_RESPONSE" | jq . > "$OUTPUT_DIR/presentation_response.json" 2>/dev/null

PRES_ID=$(echo "$PRES_RESPONSE" | jq -r '.id // .presentation_id // empty')

if [ -z "$PRES_ID" ]; then
    echo ""
    echo "ERROR: Failed to create presentation"
    echo "$PRES_RESPONSE" | jq . 2>/dev/null || echo "$PRES_RESPONSE"
    exit 1
fi

PRES_URL="$LAYOUT_URL/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  RESULTS"
echo "=============================================="
echo "Success: $SUCCESS_COUNT / $TOTAL_CHARTS"
echo "Failed:  $FAIL_COUNT / $TOTAL_CHARTS"
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $PRES_URL"
echo ""
echo "Chart.js Remaining Types (V2-chart-text layout):"
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
