#!/bin/bash
# test_analytics_basic_charts.sh
# Tests: line, bar_vertical, pie charts in C3 and V2 layouts
# Each chart is generated once, then rendered in both C3 (full-width) and V2 (chart+insights) layouts

set -e

ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

OUTPUT_DIR="./test_outputs/analytics_basic_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Analytics Basic Charts Test (C3 + V2)"
echo "=============================================="
echo "Analytics Service: $ANALYTICS_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output: $OUTPUT_DIR"
echo ""

# Define charts: chart_type|analytics_type|title|narrative
# Supported analytics types: revenue_over_time, quarterly_comparison, market_share, yoy_growth,
#   kpi_metrics, category_ranking, correlation_analysis, multidimensional_analysis,
#   multi_metric_comparison, radial_composition
declare -a CHARTS=(
  "line|revenue_over_time|Revenue Trends|Quarterly revenue growth over 4 years showing consistent upward trajectory"
  "bar_vertical|category_ranking|Department Performance|Performance ranking across departments highlighting top performers"
  "pie|market_share|Market Share|Market share distribution by product category in current fiscal year"
)

SLIDES_JSON="["
FIRST=true
SLIDE_NUM=1
SUCCESS_COUNT=0
FAIL_COUNT=0

for chart_def in "${CHARTS[@]}"; do
  IFS='|' read -r chart_type analytics_type title narrative <<< "$chart_def"

  echo ""
  echo "--- [$SLIDE_NUM] Generating: $chart_type ($analytics_type) ---"

  # Call analytics service with L02 layout (which provides both chart and insights)
  RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/analytics/L02/$analytics_type?use_synthetic=true" \
    -H "Content-Type: application/json" \
    -d "{
      \"presentation_id\": \"test-basic-charts\",
      \"slide_id\": \"slide-$SLIDE_NUM\",
      \"slide_number\": $SLIDE_NUM,
      \"narrative\": \"$narrative\",
      \"chart_type\": \"$chart_type\"
    }")

  # Save response for debugging
  echo "$RESPONSE" > "$OUTPUT_DIR/${chart_type}_response.json"

  # Check for error response
  ERROR=$(echo "$RESPONSE" | jq -r '.error // empty')
  if [ -n "$ERROR" ]; then
    echo "  ERROR: Analytics service returned error: $ERROR"
    ((FAIL_COUNT++))
    continue
  fi

  # Extract fields - try aliases first, then original field names
  CHART_HTML=$(echo "$RESPONSE" | jq -r '.content.chart_html // .content.element_3 // empty')
  BODY_HTML=$(echo "$RESPONSE" | jq -r '.content.body // .content.element_2 // empty')

  if [ -z "$CHART_HTML" ]; then
    echo "  ERROR: No chart_html in response"
    echo "  Response preview: $(echo "$RESPONSE" | head -c 500)"
    ((FAIL_COUNT++))
    continue
  fi

  # Save extracted HTML for inspection
  echo "$CHART_HTML" > "$OUTPUT_DIR/${chart_type}_chart.html"
  echo "$BODY_HTML" > "$OUTPUT_DIR/${chart_type}_body.html"

  # Escape HTML for JSON embedding
  CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)
  BODY_ESCAPED=$(echo "$BODY_HTML" | jq -Rs .)

  # Build C3 slide (full-width chart only)
  C3_SLIDE=$(cat <<EOF
{
  "layout": "C3-chart",
  "content": {
    "slide_title": "$title",
    "subtitle": "$chart_type chart - Full Width",
    "chart_html": $CHART_ESCAPED,
    "logo": " "
  }
}
EOF
)

  # Build V2 slide (chart left + insights right)
  V2_SLIDE=$(cat <<EOF
{
  "layout": "V2-chart-text",
  "content": {
    "slide_title": "$title",
    "subtitle": "$chart_type chart with AI Insights",
    "chart_html": $CHART_ESCAPED,
    "body": $BODY_ESCAPED,
    "logo": " "
  }
}
EOF
)

  # Add slides to array (C3 first, then V2 for comparison)
  if [ "$FIRST" = true ]; then
    SLIDES_JSON="$SLIDES_JSON$C3_SLIDE,$V2_SLIDE"
    FIRST=false
  else
    SLIDES_JSON="$SLIDES_JSON,$C3_SLIDE,$V2_SLIDE"
  fi

  ((SUCCESS_COUNT++))
  SLIDE_NUM=$((SLIDE_NUM + 1))
  echo "  OK: Generated C3 + V2 slides for $chart_type"
done

SLIDES_JSON="$SLIDES_JSON]"

# Save slides JSON for debugging
echo "$SLIDES_JSON" | jq . > "$OUTPUT_DIR/all_slides.json"

echo ""
echo "--- Creating Presentation ---"
echo "Charts generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"
echo "Total slides: $((SUCCESS_COUNT * 2))"

if [ $SUCCESS_COUNT -eq 0 ]; then
  echo "ERROR: No charts were generated successfully. Check $OUTPUT_DIR for responses."
  exit 1
fi

# Create presentation request
PRES_REQUEST=$(cat <<EOF
{
  "title": "Analytics Test: Basic Charts (C3 + V2)",
  "template_id": "L25",
  "slides": $SLIDES_JSON
}
EOF
)

echo "$PRES_REQUEST" > "$OUTPUT_DIR/presentation_request.json"

# Call layout service to create presentation
PRES_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d "$PRES_REQUEST")

echo "$PRES_RESPONSE" > "$OUTPUT_DIR/presentation_response.json"

# Extract presentation ID
PRES_ID=$(echo "$PRES_RESPONSE" | jq -r '.id // empty')

if [ -z "$PRES_ID" ]; then
  echo "ERROR: Failed to create presentation"
  echo "Response: $PRES_RESPONSE"
  exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  SUCCESS"
echo "=============================================="
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Charts tested:"
echo "  - line (C3 + V2)"
echo "  - bar_vertical (C3 + V2)"
echo "  - pie (C3 + V2)"
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""

# Open in browser (macOS)
open "$URL"
