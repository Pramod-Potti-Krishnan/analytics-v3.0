#!/bin/bash
# Test Atomic Chart Endpoints on Railway Production
# Waits for deployment then tests all 14 chart types

ANALYTICS_URL="https://analytics-v30-production.up.railway.app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/atomic_railway_${TIMESTAMP}"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Atomic Chart Endpoints - Railway Test"
echo "=============================================="
echo "URL: $ANALYTICS_URL"
echo "Output: $OUTPUT_DIR"
echo ""

# Wait for Railway deployment
echo "Waiting 70 seconds for Railway deployment..."
sleep 70

# Health check first
echo ""
echo "--- Health Check ---"
HEALTH=$(curl -s "$ANALYTICS_URL/health")
echo "$HEALTH" | jq . 2>/dev/null || echo "$HEALTH"

if [ "$(echo "$HEALTH" | jq -r '.status // empty')" != "healthy" ]; then
    echo "WARNING: Service may not be healthy, continuing anyway..."
fi
echo ""

# Test catalog endpoint
echo "--- Testing Catalog Endpoint ---"
CATALOG=$(curl -s "$ANALYTICS_URL/api/v1/charts/atomic/catalog")
echo "$CATALOG" | jq . > "$OUTPUT_DIR/catalog.json" 2>/dev/null

CHART_COUNT=$(echo "$CATALOG" | jq -r '.count // 0')
if [ "$CHART_COUNT" = "14" ]; then
    echo "✅ Catalog: Found all 14 chart types"
else
    echo "❌ Catalog: Expected 14, got $CHART_COUNT"
    echo "Response: $CATALOG"
fi
echo ""

# All 14 chart types with test narratives
declare -A CHARTS=(
    ["line"]="Show quarterly revenue growth for 2024"
    ["bar_vertical"]="Compare department performance"
    ["bar_horizontal"]="Top 10 products by revenue"
    ["pie"]="Market share distribution"
    ["doughnut"]="Budget allocation breakdown"
    ["scatter"]="Customer satisfaction correlation"
    ["bubble"]="Product positioning analysis"
    ["polar_area"]="Seasonal patterns"
    ["radar"]="Team performance metrics"
    ["area"]="Cumulative revenue trend"
    ["area_stacked"]="Revenue by region"
    ["bar_grouped"]="Q1 vs Q2 comparison"
    ["bar_stacked"]="Sales by channel"
    ["waterfall"]="Net income bridge"
)

SUCCESS=0
FAILED=0

echo "--- Testing All 14 Chart Types ---"
echo ""

for chart_type in line bar_vertical bar_horizontal pie doughnut scatter bubble polar_area radar area area_stacked bar_grouped bar_stacked waterfall; do
    NARRATIVE="${CHARTS[$chart_type]}"

    RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/$chart_type" \
        -H "Content-Type: application/json" \
        -d "{
            \"narrative\": \"$NARRATIVE\",
            \"include_insights\": false,
            \"width\": 850,
            \"height\": 500
        }")

    echo "$RESPONSE" | jq . > "$OUTPUT_DIR/${chart_type}.json" 2>/dev/null

    IS_SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    ELEMENT_ID=$(echo "$RESPONSE" | jq -r '.element_id // "none"')
    GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
    DATA_COUNT=$(echo "$RESPONSE" | jq -r '.data_used | length // 0')

    if [ "$IS_SUCCESS" = "true" ]; then
        echo "✅ $chart_type: OK (${GEN_TIME}ms, ${DATA_COUNT} points)"
        echo "$RESPONSE" | jq -r '.chart_html // empty' > "$OUTPUT_DIR/${chart_type}.html"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌ $chart_type: FAILED"
        ERROR=$(echo "$RESPONSE" | jq -r '.detail.message // .error // .detail // "Unknown"' 2>/dev/null)
        echo "   Error: $ERROR"
        FAILED=$((FAILED + 1))
    fi
done

echo ""

# Test with insights
echo "--- Testing Chart with Insights ---"
INSIGHTS_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/line" \
    -H "Content-Type: application/json" \
    -d '{
        "narrative": "Show quarterly revenue with insights",
        "include_insights": true,
        "width": 850,
        "height": 500
    }')

echo "$INSIGHTS_RESPONSE" | jq . > "$OUTPUT_DIR/line_with_insights.json" 2>/dev/null

HAS_INSIGHTS=$(echo "$INSIGHTS_RESPONSE" | jq -r '.insights_html // "null"')
if [ "$HAS_INSIGHTS" != "null" ] && [ "$HAS_INSIGHTS" != "" ]; then
    echo "✅ Line with insights: OK"
    echo "$INSIGHTS_RESPONSE" | jq -r '.insights_html' > "$OUTPUT_DIR/line_insights_panel.html"
else
    echo "❌ Line with insights: Missing insights_html"
fi

echo ""

# Test error handling
echo "--- Testing Error Handling ---"
ERROR_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/invalid_type" \
    -H "Content-Type: application/json" \
    -d '{"narrative": "test"}')

ERROR_CODE=$(echo "$ERROR_RESPONSE" | jq -r '.detail.error_code // "none"')
if [ "$ERROR_CODE" = "INVALID_CHART_TYPE" ]; then
    echo "✅ Invalid chart type: Correctly rejected"
else
    echo "❌ Invalid chart type: Unexpected response"
    echo "$ERROR_RESPONSE" | jq .
fi

echo ""
echo "=============================================="
echo "  RESULTS"
echo "=============================================="
echo "Success: $SUCCESS / 14"
echo "Failed:  $FAILED / 14"
echo ""
echo "Output: $OUTPUT_DIR"
echo ""

# Summary
if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed"
    exit 1
fi
