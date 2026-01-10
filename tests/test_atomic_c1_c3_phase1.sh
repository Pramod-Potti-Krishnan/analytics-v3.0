#!/bin/bash
#
# Test Script: Atomic Charts Phase 1 - C1-text & C3-chart Layouts
# Version: 3.6.1
# Charts: line, bar_vertical, bar_horizontal, pie, doughnut (5 total)
# v3.6.1: Pass enable_editor=true and presentation_id for edit button support
#
# This script tests atomic chart endpoints and publishes them to both
# C1-text and C3-chart layouts via the Layout Service.
#

# Configuration
ANALYTICS_URL="${ANALYTICS_URL:-https://analytics-v30-production.up.railway.app}"
LAYOUT_URL="${LAYOUT_URL:-https://web-production-f0d13.up.railway.app}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_c1_c3_phase1_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=============================================="
echo "  Atomic Charts Phase 1 - C1 & C3 Layouts"
echo "  Version: 3.6.1 (with edit button support)"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout:    $LAYOUT_URL"
echo "Output:    $OUTPUT_DIR"
echo ""

# Phase 1 Charts (5 total) - using indexed arrays for bash 3.x compatibility
CHART_TYPES="line bar_vertical bar_horizontal pie doughnut"
NARRATIVES_line="Show quarterly revenue growth for 2024 with strong Q3-Q4 performance"
NARRATIVES_bar_vertical="Compare department performance rankings across the organization"
NARRATIVES_bar_horizontal="Top 10 products by revenue contribution to total sales"
NARRATIVES_pie="Market share distribution by company segment"
NARRATIVES_doughnut="Annual budget allocation by department for fiscal year"

# Function to get narrative for chart type
get_narrative() {
    local chart_type=$1
    case $chart_type in
        line) echo "$NARRATIVES_line" ;;
        bar_vertical) echo "$NARRATIVES_bar_vertical" ;;
        bar_horizontal) echo "$NARRATIVES_bar_horizontal" ;;
        pie) echo "$NARRATIVES_pie" ;;
        doughnut) echo "$NARRATIVES_doughnut" ;;
        *) echo "Chart analysis" ;;
    esac
}

# ============================================
# Health Checks
# ============================================
echo "--- Health Checks ---"

# Check Analytics Service
ANALYTICS_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$ANALYTICS_URL/health" 2>/dev/null || echo "000")
if [ "$ANALYTICS_HEALTH" = "200" ]; then
    echo -e "${GREEN}Analytics Service: OK${NC}"
else
    echo -e "${RED}Analytics Service: FAILED (HTTP $ANALYTICS_HEALTH)${NC}"
    echo "Cannot proceed without Analytics Service"
    exit 1
fi

# Check Layout Service
LAYOUT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$LAYOUT_URL/health" 2>/dev/null || echo "000")
if [ "$LAYOUT_HEALTH" = "200" ]; then
    echo -e "${GREEN}Layout Service: OK${NC}"
else
    echo -e "${YELLOW}Layout Service: Warning (HTTP $LAYOUT_HEALTH) - may still work${NC}"
fi

# Check Atomic Catalog
echo ""
echo "--- Checking Atomic Catalog ---"
CATALOG_RESPONSE=$(curl -s "$ANALYTICS_URL/api/v1/charts/atomic/catalog")
echo "$CATALOG_RESPONSE" | jq . > "$OUTPUT_DIR/catalog.json" 2>/dev/null

CATALOG_COUNT=$(echo "$CATALOG_RESPONSE" | jq -r '.count // 0')
echo "Available chart types: $CATALOG_COUNT"

if [ "$CATALOG_COUNT" != "14" ]; then
    echo -e "${YELLOW}Warning: Expected 14 chart types, got $CATALOG_COUNT${NC}"
fi

echo ""

# ============================================
# Generate Atomic Charts
# ============================================
echo "--- Generating Atomic Charts (Phase 1: 5 Charts) ---"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
ATOMIC_RESULTS="[]"

# Arrays to store slide JSON
C1_SLIDES=""
C3_SLIDES=""
CHART_TITLES=""

slide_num=0
for chart_type in $CHART_TYPES; do
    slide_num=$((slide_num + 1))
    narrative=$(get_narrative "$chart_type")

    echo -e "${BLUE}[$slide_num/5] Testing: $chart_type${NC}"
    echo "  Narrative: $narrative"

    # Call atomic endpoint
    # v3.6.1: Pass presentation_id="placeholder" - JavaScript will extract actual ID from URL at runtime
    RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"narrative\": \"$narrative\",
            \"include_insights\": true,
            \"width\": 850,
            \"height\": 500,
            \"enable_editor\": true,
            \"presentation_id\": \"placeholder\"
        }")

    # Save full response
    echo "$RESPONSE" | jq . > "$OUTPUT_DIR/${slide_num}_${chart_type}_response.json" 2>/dev/null

    # Extract fields
    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    CHART_HTML=$(echo "$RESPONSE" | jq -r '.chart_html // ""')
    INSIGHTS_HTML=$(echo "$RESPONSE" | jq -r '.insights_html // ""')
    CHART_TITLE=$(echo "$RESPONSE" | jq -r '.chart_title // "Chart"')
    ELEMENT_ID=$(echo "$RESPONSE" | jq -r '.element_id // "none"')
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
    DATA_COUNT=$(echo "$RESPONSE" | jq -r '.data_used | length // 0')

    if [ "$SUCCESS" = "true" ] && [ -n "$CHART_HTML" ] && [ "$CHART_HTML" != "null" ]; then
        echo -e "  ${GREEN}Status: SUCCESS${NC}"
        echo "  Title: $CHART_TITLE"
        echo "  Element ID: $ELEMENT_ID"
        echo "  Data Points: $DATA_COUNT"
        echo "  Generation Time: ${GEN_TIME}ms"

        # Save chart HTML
        echo "$CHART_HTML" > "$OUTPUT_DIR/${slide_num}_${chart_type}_chart.html"

        # Save insights HTML if present
        if [ -n "$INSIGHTS_HTML" ] && [ "$INSIGHTS_HTML" != "null" ]; then
            echo "$INSIGHTS_HTML" > "$OUTPUT_DIR/${slide_num}_${chart_type}_insights.html"
            echo "  Insights: Present"
        fi

        # Store title for later
        CHART_TITLES="$CHART_TITLES|$chart_type:$CHART_TITLE:$GEN_TIME:$DATA_COUNT"

        # Escape HTML for JSON
        CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)
        TITLE_ESCAPED=$(echo "$CHART_TITLE" | jq -Rs . | sed 's/^"//;s/"$//')

        # Build C1-text slide JSON
        C1_SLIDE="{
            \"layout\": \"C1-text\",
            \"content\": {
                \"slide_title\": \"$TITLE_ESCAPED\",
                \"subtitle\": \"$chart_type chart - Atomic Endpoint Test\",
                \"body\": $CHART_ESCAPED,
                \"footer_text\": \"Phase 1 - Atomic Charts Test\",
                \"logo\": \" \"
            }
        }"

        # Build C3-chart slide JSON
        C3_SLIDE="{
            \"layout\": \"C3-chart\",
            \"content\": {
                \"slide_title\": \"$TITLE_ESCAPED\",
                \"subtitle\": \"$chart_type visualization\",
                \"chart_html\": $CHART_ESCAPED,
                \"presentation_name\": \"Atomic Charts Phase 1\",
                \"logo\": \" \"
            }
        }"

        # Append to slides arrays
        if [ -z "$C1_SLIDES" ]; then
            C1_SLIDES="$C1_SLIDE"
            C3_SLIDES="$C3_SLIDE"
        else
            C1_SLIDES="$C1_SLIDES,$C1_SLIDE"
            C3_SLIDES="$C3_SLIDES,$C3_SLIDE"
        fi

        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ATOMIC_RESULTS=$(echo "$ATOMIC_RESULTS" | jq ". + [{\"chart_id\": \"$chart_type\", \"status\": \"success\", \"generation_time_ms\": $GEN_TIME, \"data_points\": $DATA_COUNT}]")
    else
        echo -e "  ${RED}Status: FAILED${NC}"
        ERROR=$(echo "$RESPONSE" | jq -r '.detail.message // .error // .detail // "Unknown error"')
        echo "  Error: $ERROR"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        ATOMIC_RESULTS=$(echo "$ATOMIC_RESULTS" | jq ". + [{\"chart_id\": \"$chart_type\", \"status\": \"failed\", \"error\": \"$ERROR\"}]")
    fi

    echo ""
done

# ============================================
# Create C1-text Presentation
# ============================================
echo "--- Creating C1-text Presentation ---"

C1_REQUEST="{
    \"title\": \"Atomic Charts Phase 1 - C1-text Layout - $TIMESTAMP\",
    \"template_id\": \"L25\",
    \"slides\": [$C1_SLIDES]
}"

echo "$C1_REQUEST" | jq . > "$OUTPUT_DIR/c1_presentation_request.json"

C1_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations" \
    -H "Content-Type: application/json" \
    -d "$C1_REQUEST")

echo "$C1_RESPONSE" | jq . > "$OUTPUT_DIR/c1_presentation_response.json"

C1_PRES_ID=$(echo "$C1_RESPONSE" | jq -r '.id // .presentation_id // ""')
C1_URL=""

if [ -n "$C1_PRES_ID" ] && [ "$C1_PRES_ID" != "null" ]; then
    C1_URL="$LAYOUT_URL/p/$C1_PRES_ID"
    echo -e "${GREEN}C1-text Presentation: SUCCESS${NC}"
    echo "  ID: $C1_PRES_ID"
    echo "  URL: $C1_URL"
else
    echo -e "${RED}C1-text Presentation: FAILED${NC}"
    echo "$C1_RESPONSE" | jq .
fi

echo ""

# ============================================
# Create C3-chart Presentation
# ============================================
echo "--- Creating C3-chart Presentation ---"

C3_REQUEST="{
    \"title\": \"Atomic Charts Phase 1 - C3-chart Layout - $TIMESTAMP\",
    \"template_id\": \"L25\",
    \"slides\": [$C3_SLIDES]
}"

echo "$C3_REQUEST" | jq . > "$OUTPUT_DIR/c3_presentation_request.json"

C3_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations" \
    -H "Content-Type: application/json" \
    -d "$C3_REQUEST")

echo "$C3_RESPONSE" | jq . > "$OUTPUT_DIR/c3_presentation_response.json"

C3_PRES_ID=$(echo "$C3_RESPONSE" | jq -r '.id // .presentation_id // ""')
C3_URL=""

if [ -n "$C3_PRES_ID" ] && [ "$C3_PRES_ID" != "null" ]; then
    C3_URL="$LAYOUT_URL/p/$C3_PRES_ID"
    echo -e "${GREEN}C3-chart Presentation: SUCCESS${NC}"
    echo "  ID: $C3_PRES_ID"
    echo "  URL: $C3_URL"
else
    echo -e "${RED}C3-chart Presentation: FAILED${NC}"
    echo "$C3_RESPONSE" | jq .
fi

echo ""

# ============================================
# Generate Preview HTML
# ============================================
echo "--- Generating Preview HTML ---"

cat > "$OUTPUT_DIR/preview_charts.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Atomic Charts Phase 1 - Preview</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; padding: 20px; background: #f5f5f5; margin: 0; }
        h1 { color: #1f2937; margin-bottom: 8px; }
        .subtitle { color: #6b7280; margin-bottom: 24px; }
        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .chart-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .chart-title { font-weight: 600; margin-bottom: 8px; color: #374151; font-size: 16px; }
        .chart-type { font-size: 12px; color: #9ca3af; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .chart-frame { width: 100%; height: 350px; border: none; border-radius: 8px; background: #fafafa; }
        .stats { display: flex; gap: 16px; margin-top: 12px; font-size: 12px; color: #6b7280; }
        .stat { display: flex; align-items: center; gap: 4px; }
        .stat-value { font-weight: 600; color: #374151; }
        .urls { margin-top: 24px; padding: 16px; background: white; border-radius: 8px; }
        .urls h3 { margin: 0 0 12px 0; color: #374151; }
        .urls a { display: block; color: #3b82f6; margin: 4px 0; }
    </style>
</head>
<body>
    <h1>Atomic Charts Phase 1 - Preview</h1>
    <p class="subtitle">Charts: line, bar_vertical, bar_horizontal, pie, doughnut | Generated: $TIMESTAMP</p>
    <div class="urls">
        <h3>Presentation URLs</h3>
        <a href="$C1_URL" target="_blank">C1-text Layout: $C1_URL</a>
        <a href="$C3_URL" target="_blank">C3-chart Layout: $C3_URL</a>
    </div>
    <div class="chart-grid">
EOF

slide_num=0
for chart_type in $CHART_TYPES; do
    slide_num=$((slide_num + 1))
    html_file="${slide_num}_${chart_type}_chart.html"

    if [ -f "$OUTPUT_DIR/$html_file" ]; then
        CHART_CONTENT=$(cat "$OUTPUT_DIR/$html_file" | sed 's/"/\&quot;/g' | tr '\n' ' ')
        cat >> "$OUTPUT_DIR/preview_charts.html" << EOF
        <div class="chart-card">
            <div class="chart-type">$chart_type</div>
            <div class="chart-title">Chart $slide_num</div>
            <iframe class="chart-frame" srcdoc="$CHART_CONTENT"></iframe>
        </div>
EOF
    fi
done

cat >> "$OUTPUT_DIR/preview_charts.html" << 'EOF'
    </div>
</body>
</html>
EOF

echo "Preview HTML: $OUTPUT_DIR/preview_charts.html"

# ============================================
# Generate Test Report JSON
# ============================================
echo ""
echo "--- Generating Test Report ---"

cat > "$OUTPUT_DIR/test_report.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "phase": 1,
    "charts_tested": ["line", "bar_vertical", "bar_horizontal", "pie", "doughnut"],
    "atomic_results": {
        "success": $SUCCESS_COUNT,
        "failed": $FAIL_COUNT,
        "details": $ATOMIC_RESULTS
    },
    "layout_results": {
        "c1_text": {
            "presentation_id": "$C1_PRES_ID",
            "url": "$C1_URL",
            "slides": $SUCCESS_COUNT,
            "status": "$([ -n "$C1_PRES_ID" ] && [ "$C1_PRES_ID" != "null" ] && echo "success" || echo "failed")"
        },
        "c3_chart": {
            "presentation_id": "$C3_PRES_ID",
            "url": "$C3_URL",
            "slides": $SUCCESS_COUNT,
            "status": "$([ -n "$C3_PRES_ID" ] && [ "$C3_PRES_ID" != "null" ] && echo "success" || echo "failed")"
        }
    },
    "output_directory": "$OUTPUT_DIR"
}
EOF

echo "Test Report: $OUTPUT_DIR/test_report.json"

# ============================================
# Summary
# ============================================
echo ""
echo "=============================================="
echo "  PHASE 1 TEST RESULTS"
echo "=============================================="
echo ""
echo "Charts Tested: $CHART_TYPES"
echo ""
echo -e "Atomic Generation: ${GREEN}$SUCCESS_COUNT${NC} / 5 success"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "                   ${RED}$FAIL_COUNT${NC} / 5 failed"
fi
echo ""
echo "Presentations Created:"
if [ -n "$C1_URL" ]; then
    echo -e "  C1-text: ${GREEN}$C1_URL${NC}"
else
    echo -e "  C1-text: ${RED}FAILED${NC}"
fi
if [ -n "$C3_URL" ]; then
    echo -e "  C3-chart: ${GREEN}$C3_URL${NC}"
else
    echo -e "  C3-chart: ${RED}FAILED${NC}"
fi
echo ""
echo "Output Directory: $OUTPUT_DIR"
echo ""

# Open presentations in browser (macOS)
if [ -n "$C1_URL" ]; then
    echo "Opening C1-text presentation..."
    open "$C1_URL" 2>/dev/null || echo "  Open manually: $C1_URL"
fi
if [ -n "$C3_URL" ]; then
    echo "Opening C3-chart presentation..."
    open "$C3_URL" 2>/dev/null || echo "  Open manually: $C3_URL"
fi

echo ""

# Exit with appropriate code
if [ $FAIL_COUNT -gt 0 ] || [ -z "$C1_PRES_ID" ] || [ "$C1_PRES_ID" = "null" ] || [ -z "$C3_PRES_ID" ] || [ "$C3_PRES_ID" = "null" ]; then
    exit 1
else
    exit 0
fi
