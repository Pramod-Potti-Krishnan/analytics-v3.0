#!/bin/bash
#
# Test Script: Atomic Charts Phase 3 - C1-text & C3-chart Layouts
# Version: 3.7.5
# Charts: area_stacked, bar_grouped, bar_stacked, waterfall (4 total)
#
# v3.7.5: Added required slide_id for deterministic chart IDs and persistence
#
# This script tests atomic chart endpoints and publishes them to both
# C1-text and C3-chart layouts via the Layout Service.
#

set -e

# Configuration
ANALYTICS_URL="${ANALYTICS_URL:-https://analytics-v30-production.up.railway.app}"
LAYOUT_URL="${LAYOUT_URL:-https://web-production-f0d13.up.railway.app}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_c1_c3_phase3_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=============================================="
echo "  Atomic Charts Phase 3 - C1 & C3 Layouts"
echo "  Version: 3.7.5 (deterministic chart IDs)"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout:    $LAYOUT_URL"
echo "Output:    $OUTPUT_DIR"
echo ""

# Phase 3 Charts (4 total) - Using parallel arrays for bash 3.2 compatibility
CHART_TYPES=("area_stacked" "bar_grouped" "bar_stacked" "waterfall")
NARRATIVES=(
    "Revenue breakdown by region over time showing North America, Europe, and Asia Pacific contribution"
    "Q1 vs Q2 performance comparison across product lines"
    "Sales composition by channel per quarter showing online, retail, and wholesale segments"
    "Net income bridge from revenue to profit showing income sources and expense deductions"
)

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
echo "--- Generating Atomic Charts (Phase 3: 4 Charts) ---"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
ATOMIC_RESULTS="[]"

# Arrays to store chart data for presentations
declare -a C1_SLIDES
declare -a C3_SLIDES
declare -a CHART_DETAILS

for i in "${!CHART_TYPES[@]}"; do
    chart_type="${CHART_TYPES[$i]}"
    narrative="${NARRATIVES[$i]}"
    slide_num=$((i + 1))

    echo -e "${BLUE}[$slide_num/4] Testing: $chart_type${NC}"
    echo "  Narrative: $narrative"

    # Call atomic endpoint
    # v3.7.5: presentation_id and slide_id are REQUIRED for deterministic chart IDs
    RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"presentation_id\": \"test-pres-phase3-$TIMESTAMP\",
            \"slide_id\": \"slide-$slide_num\",
            \"chart_index\": 0,
            \"narrative\": \"$narrative\",
            \"include_insights\": true,
            \"width\": 850,
            \"height\": 500,
            \"enable_editor\": true
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

        # Store for slides
        CHART_DETAILS+=("$chart_type|$CHART_TITLE|$GEN_TIME|$DATA_COUNT")

        # Escape HTML for JSON
        CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)
        TITLE_ESCAPED=$(echo "$CHART_TITLE" | jq -Rs . | sed 's/^"//;s/"$//')

        # Build C1-text slide
        C1_SLIDES+=("{
            \"layout\": \"C1-text\",
            \"content\": {
                \"slide_title\": \"$TITLE_ESCAPED\",
                \"subtitle\": \"$chart_type chart - Atomic Endpoint Test\",
                \"body\": $CHART_ESCAPED,
                \"footer_text\": \"Phase 3 - Atomic Charts Test\",
                \"logo\": \" \"
            }
        }")

        # Build C3-chart slide
        C3_SLIDES+=("{
            \"layout\": \"C3-chart\",
            \"content\": {
                \"slide_title\": \"$TITLE_ESCAPED\",
                \"subtitle\": \"$chart_type visualization\",
                \"chart_html\": $CHART_ESCAPED,
                \"presentation_name\": \"Atomic Charts Phase 3\",
                \"logo\": \" \"
            }
        }")

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

# Join slides array
C1_SLIDES_JSON=$(IFS=,; echo "${C1_SLIDES[*]}")

C1_REQUEST="{
    \"title\": \"Atomic Charts Phase 3 - C1-text Layout - $TIMESTAMP\",
    \"template_id\": \"L25\",
    \"slides\": [$C1_SLIDES_JSON]
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

# Join slides array
C3_SLIDES_JSON=$(IFS=,; echo "${C3_SLIDES[*]}")

C3_REQUEST="{
    \"title\": \"Atomic Charts Phase 3 - C3-chart Layout - $TIMESTAMP\",
    \"template_id\": \"L25\",
    \"slides\": [$C3_SLIDES_JSON]
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

cat > "$OUTPUT_DIR/preview_charts.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Atomic Charts Phase 3 - Preview</title>
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
    </style>
</head>
<body>
    <h1>Atomic Charts Phase 3 - Preview</h1>
    <p class="subtitle">Charts: area_stacked, bar_grouped, bar_stacked, waterfall | Generated: TIMESTAMP_PLACEHOLDER</p>
    <div class="chart-grid">
EOF

for i in "${!CHART_TYPES[@]}"; do
    chart_type="${CHART_TYPES[$i]}"
    slide_num=$((i + 1))
    html_file="${slide_num}_${chart_type}_chart.html"

    if [ -f "$OUTPUT_DIR/$html_file" ]; then
        # Get chart details
        IFS='|' read -r _ title gen_time data_count <<< "${CHART_DETAILS[$i]:-|Chart|0|0}"

        cat >> "$OUTPUT_DIR/preview_charts.html" << EOF
        <div class="chart-card">
            <div class="chart-type">$chart_type</div>
            <div class="chart-title">$title</div>
            <iframe class="chart-frame" srcdoc="$(cat "$OUTPUT_DIR/$html_file" | sed 's/"/\&quot;/g' | tr '\n' ' ')"></iframe>
            <div class="stats">
                <div class="stat">Time: <span class="stat-value">${gen_time}ms</span></div>
                <div class="stat">Points: <span class="stat-value">$data_count</span></div>
            </div>
        </div>
EOF
    fi
done

cat >> "$OUTPUT_DIR/preview_charts.html" << 'EOF'
    </div>
</body>
</html>
EOF

# Replace timestamp placeholder
sed -i.bak "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/" "$OUTPUT_DIR/preview_charts.html" 2>/dev/null || \
sed -i "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/" "$OUTPUT_DIR/preview_charts.html" 2>/dev/null
rm -f "$OUTPUT_DIR/preview_charts.html.bak"

echo "Preview HTML: $OUTPUT_DIR/preview_charts.html"

# ============================================
# Generate Test Report JSON
# ============================================
echo ""
echo "--- Generating Test Report ---"

cat > "$OUTPUT_DIR/test_report.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "phase": 3,
    "charts_tested": ["area_stacked", "bar_grouped", "bar_stacked", "waterfall"],
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
            "status": "$([ -n "$C1_PRES_ID" ] && echo "success" || echo "failed")"
        },
        "c3_chart": {
            "presentation_id": "$C3_PRES_ID",
            "url": "$C3_URL",
            "slides": $SUCCESS_COUNT,
            "status": "$([ -n "$C3_PRES_ID" ] && echo "success" || echo "failed")"
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
echo "  PHASE 3 TEST RESULTS"
echo "=============================================="
echo ""
echo "Charts Tested: ${CHART_TYPES[*]}"
echo ""
echo -e "Atomic Generation: ${GREEN}$SUCCESS_COUNT${NC} / 4 success"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "                   ${RED}$FAIL_COUNT${NC} / 4 failed"
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
if [ $FAIL_COUNT -gt 0 ] || [ -z "$C1_PRES_ID" ] || [ -z "$C3_PRES_ID" ]; then
    exit 1
else
    exit 0
fi
