#!/bin/bash
#
# Test Script: Atomic Charts Batch 1 (5 Simple Charts) - v3.6.0
# Tests: line, bar_vertical, bar_horizontal, pie, doughnut
#
# v3.6.0 Changes:
# - Uses C3-chart layout as base with insight-style title
# - Adds charts as moveable elements via elements API
# - Charts can now be repositioned by users
#

ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_elements_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Atomic Charts Test - v3.6.0 Elements API"
echo "=============================================="
echo "Analytics: $ANALYTICS_SERVICE"
echo "Layout:    $LAYOUT_SERVICE"
echo "Output:    $OUTPUT_DIR"
echo ""
echo "Features tested:"
echo "  - LLM-generated insight-style titles"
echo "  - Edit button for interactive data editing"
echo "  - Moveable chart elements via elements API"
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
    "line|Show quarterly revenue growth for 2024"
    "bar_vertical|Compare department performance rankings"
    "bar_horizontal|Top 10 products by revenue contribution"
    "pie|Market share distribution by segment"
    "doughnut|Annual budget allocation by department"
)

# Step 1: Create slides with C3-chart layout (base for elements)
echo "--- Creating Base Slides with C3-chart Layout ---"
echo ""

SLIDES_JSON="["
FIRST_SLIDE=true

for item in "${CHARTS[@]}"; do
    IFS='|' read -r chart_type narrative <<< "$item"

    # C3-chart layout with placeholder - title will come from insight-style generation
    SLIDE_JSON="{
        \"layout\": \"C3-chart\",
        \"content\": {
            \"slide_title\": \"Loading...\",
            \"subtitle\": \"${chart_type} chart\",
            \"chart_html\": \"<div style='display:flex;align-items:center;justify-content:center;height:100%;color:#666;'>Chart loading via elements API...</div>\",
            \"presentation_name\": \"Atomic Charts v3.6.0\",
            \"logo\": \" \"
        }
    }"

    if [ "$FIRST_SLIDE" = true ]; then
        SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
        FIRST_SLIDE=false
    else
        SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
    fi
done

SLIDES_JSON="$SLIDES_JSON]"

# Create presentation with base slides
LAYOUT_REQUEST="{
    \"title\": \"Atomic Charts v3.6.0 - Elements API Test\",
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

echo "Presentation created: $PRES_ID"
echo ""

# Step 2: Generate charts and add as elements
echo "--- Generating Atomic Charts & Adding as Elements ---"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_INDEX=0

for item in "${CHARTS[@]}"; do
    IFS='|' read -r chart_type narrative <<< "$item"
    ((SLIDE_INDEX++))
    SLIDE_IDX=$((SLIDE_INDEX - 1))  # 0-based index

    echo "[$SLIDE_INDEX/5] $chart_type"

    # Call atomic endpoint with enable_editor=true
    RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"narrative\": \"$narrative\",
            \"include_insights\": false,
            \"width\": 1100,
            \"height\": 600,
            \"enable_editor\": true,
            \"presentation_id\": \"$PRES_ID\"
        }")

    # Save response
    echo "$RESPONSE" > "$OUTPUT_DIR/${SLIDE_INDEX}_${chart_type}_response.json"

    # Check success
    IS_SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    CHART_HTML=$(echo "$RESPONSE" | jq -r '.chart_html // ""')
    CHART_TITLE=$(echo "$RESPONSE" | jq -r '.chart_title // ""')
    ELEMENT_ID=$(echo "$RESPONSE" | jq -r '.element_id // "none"')
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
    DATA_COUNT=$(echo "$RESPONSE" | jq -r '.data_used | length // 0')

    if [ "$IS_SUCCESS" = "true" ] && [ -n "$CHART_HTML" ] && [ "$CHART_HTML" != "null" ]; then
        echo "  Status: OK (${GEN_TIME}ms, ${DATA_COUNT} points)"
        echo "  Title: $CHART_TITLE"
        echo "  Element: $ELEMENT_ID"

        # Save chart HTML
        echo "$CHART_HTML" > "$OUTPUT_DIR/${SLIDE_INDEX}_${chart_type}.html"

        # Escape chart HTML for JSON
        CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)

        # Add chart as moveable element via elements API
        # Grid position: rows 3-15 (chart area), columns 2-31 (near full width)
        ELEMENT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations/$PRES_ID/slides/$SLIDE_IDX/charts" \
            -H "Content-Type: application/json" \
            -d "{
                \"position\": {
                    \"grid_row\": \"3/16\",
                    \"grid_column\": \"2/31\"
                },
                \"chart_type\": \"$chart_type\",
                \"chart_html\": $CHART_ESCAPED,
                \"z_index\": 100
            }")

        echo "$ELEMENT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_INDEX}_${chart_type}_element.json"

        ELEMENT_SUCCESS=$(echo "$ELEMENT_RESPONSE" | jq -r '.success // false')
        ELEMENT_CHART_ID=$(echo "$ELEMENT_RESPONSE" | jq -r '.chart.id // "none"')

        if [ "$ELEMENT_SUCCESS" = "true" ]; then
            echo "  Element added: $ELEMENT_CHART_ID"

            # Update slide title with insight-style title
            TITLE_ESCAPED=$(echo "$CHART_TITLE" | jq -Rs .)
            curl -s -X PUT "$LAYOUT_SERVICE/api/presentations/$PRES_ID/slides/$SLIDE_IDX" \
                -H "Content-Type: application/json" \
                -d "{
                    \"content\": {
                        \"slide_title\": $TITLE_ESCAPED,
                        \"subtitle\": \"Interactive ${chart_type} chart with edit capability\"
                    }
                }" > /dev/null

            ((SUCCESS_COUNT++))
        else
            echo "  Element add FAILED"
            echo "$ELEMENT_RESPONSE" | jq . 2>/dev/null
            ((FAIL_COUNT++))
        fi
    else
        echo "  Status: FAILED"
        ERROR=$(echo "$RESPONSE" | jq -r '.detail.message // .error // .detail // "Unknown"' 2>/dev/null)
        echo "  Error: $ERROR"
        ((FAIL_COUNT++))
    fi
    echo ""
done

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  Atomic Charts v3.6.0 Test Complete"
echo "=============================================="
echo ""
echo "Presentation: $PRES_ID"
echo "URL: $URL"
echo ""
echo "v3.6.0 Features Tested:"
echo "  - LLM-generated insight-style titles (KEY TAKEAWAY: explanation)"
echo "  - Edit button on each chart for data editing"
echo "  - Moveable chart elements via Layout Service elements API"
echo ""
echo "Charts Tested (Batch 1):"
echo "  1. line - Quarterly revenue growth"
echo "  2. bar_vertical - Department performance"
echo "  3. bar_horizontal - Top products"
echo "  4. pie - Market share"
echo "  5. doughnut - Budget allocation"
echo ""
echo "Results: $SUCCESS_COUNT/5 success"
echo "Output: $OUTPUT_DIR"
echo ""

# Open in browser
echo "Opening presentation..."
open "$URL" 2>/dev/null || echo "Open manually: $URL"

echo ""
