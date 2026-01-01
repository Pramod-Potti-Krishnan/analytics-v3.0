#!/bin/bash
#
# Test Script: Atomic Charts Batch 1 (5 Simple Charts)
# Tests: line, bar_vertical, bar_horizontal, pie, doughnut
#
# Uses atomic endpoints with C3-chart layout for presentation
#

ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_c3_batch1_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Atomic Charts Test - Batch 1 (5 Charts)"
echo "=============================================="
echo "Analytics: $ANALYTICS_SERVICE"
echo "Layout:    $LAYOUT_SERVICE"
echo "Output:    $OUTPUT_DIR"
echo ""

# First check if atomic endpoints are available
echo "--- Checking Atomic Endpoints ---"
VERSION=$(curl -s "$ANALYTICS_SERVICE/" | jq -r '.version // "unknown"')
echo "Service Version: $VERSION"

CATALOG=$(curl -s "$ANALYTICS_SERVICE/api/v1/charts/atomic/catalog")
CATALOG_COUNT=$(echo "$CATALOG" | jq -r '.count // 0')
echo "Atomic Chart Types: $CATALOG_COUNT"

if [ "$CATALOG_COUNT" != "14" ]; then
    echo ""
    echo "WARNING: Atomic endpoints not available yet (expected 14, got $CATALOG_COUNT)"
    echo "Catalog response:"
    echo "$CATALOG" | jq . 2>/dev/null || echo "$CATALOG"
    echo ""
    echo "Deployment may still be in progress. Try again in a few minutes."
    exit 1
fi

echo "Catalog: OK"
echo ""

# Batch 1: 5 simple charts
declare -a CHARTS=(
    "line|Revenue Trend Analysis|Show quarterly revenue growth for 2024"
    "bar_vertical|Department Performance|Compare department performance rankings"
    "bar_horizontal|Top Products|Top 10 products by revenue contribution"
    "pie|Market Share|Market share distribution by segment"
    "doughnut|Budget Allocation|Annual budget allocation by department"
)

SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

echo "--- Generating Atomic Charts ---"
echo ""

for item in "${CHARTS[@]}"; do
    IFS='|' read -r chart_type title narrative <<< "$item"
    ((SLIDE_NUM++))

    echo "[$SLIDE_NUM/5] $chart_type: $title"

    # Call atomic endpoint
    RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"narrative\": \"$narrative\",
            \"include_insights\": false,
            \"width\": 1100,
            \"height\": 650
        }")

    # Save response
    echo "$RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_${chart_type}_response.json"

    # Check success
    IS_SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    CHART_HTML=$(echo "$RESPONSE" | jq -r '.chart_html // ""')
    ELEMENT_ID=$(echo "$RESPONSE" | jq -r '.element_id // "none"')
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
    DATA_COUNT=$(echo "$RESPONSE" | jq -r '.data_used | length // 0')

    if [ "$IS_SUCCESS" = "true" ] && [ -n "$CHART_HTML" ] && [ "$CHART_HTML" != "null" ]; then
        echo "  Status: OK (${GEN_TIME}ms, ${DATA_COUNT} points)"
        echo "  Element: $ELEMENT_ID"

        # Save chart HTML
        echo "$CHART_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${chart_type}.html"
        ((SUCCESS_COUNT++))

        # Escape for JSON
        CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)

        # Build slide JSON for C3-chart layout
        SLIDE_JSON="{
            \"layout\": \"C3-chart\",
            \"content\": {
                \"slide_title\": \"$title\",
                \"subtitle\": \"Atomic Chart: $chart_type\",
                \"chart_html\": $CHART_ESCAPED,
                \"presentation_name\": \"Atomic Charts Test\",
                \"logo\": \" \"
            }
        }"

        if [ "$FIRST_SLIDE" = true ]; then
            SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
            FIRST_SLIDE=false
        else
            SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
        fi
    else
        echo "  Status: FAILED"
        ERROR=$(echo "$RESPONSE" | jq -r '.detail.message // .error // .detail // "Unknown"' 2>/dev/null)
        echo "  Error: $ERROR"
        ((FAIL_COUNT++))
    fi
    echo ""
done

SLIDES_JSON="$SLIDES_JSON]"

echo "--- Creating Presentation ---"
echo ""
echo "Charts generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

if [ $SUCCESS_COUNT -eq 0 ]; then
    echo "No charts generated successfully. Exiting."
    exit 1
fi

# Save slides JSON
echo "$SLIDES_JSON" > "$OUTPUT_DIR/slides.json"

# Create presentation
LAYOUT_REQUEST="{
    \"title\": \"Atomic Charts Batch 1 - Simple Charts\",
    \"template_id\": \"L25\",
    \"slides\": $SLIDES_JSON
}"

echo "$LAYOUT_REQUEST" > "$OUTPUT_DIR/layout_request.json"

LAYOUT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
    -H "Content-Type: application/json" \
    -d "$LAYOUT_REQUEST")

echo "$LAYOUT_RESPONSE" > "$OUTPUT_DIR/layout_response.json"

PRES_ID=$(echo "$LAYOUT_RESPONSE" | jq -r '.id // ""')

if [ -z "$PRES_ID" ] || [ "$PRES_ID" = "null" ]; then
    echo "ERROR: Failed to create presentation"
    echo "$LAYOUT_RESPONSE" | jq . 2>/dev/null || echo "$LAYOUT_RESPONSE"
    exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  SUCCESS! Batch 1 Test Complete"
echo "=============================================="
echo ""
echo "Presentation: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Charts Tested (Batch 1):"
echo "  1. line - Revenue Trend Analysis"
echo "  2. bar_vertical - Department Performance"
echo "  3. bar_horizontal - Top Products"
echo "  4. pie - Market Share"
echo "  5. doughnut - Budget Allocation"
echo ""
echo "Results: $SUCCESS_COUNT/5 success"
echo "Output: $OUTPUT_DIR"
echo ""

# Open in browser
echo "Opening presentation..."
open "$URL" 2>/dev/null || echo "Open manually: $URL"

echo ""
