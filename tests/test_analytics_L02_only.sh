#!/bin/bash
# test_analytics_L02_only.sh
# Tests charts using L02 layout directly to verify Chart.js rendering works in L02

set -e

ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

OUTPUT_DIR="./test_outputs/analytics_L02_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Analytics L02 Layout Test (Chart Rendering)"
echo "=============================================="
echo "Analytics Service: $ANALYTICS_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output: $OUTPUT_DIR"
echo ""

# Define charts: chart_type|analytics_type|title|narrative
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

  # Call analytics service with L02 layout
  RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/analytics/L02/$analytics_type?use_synthetic=true" \
    -H "Content-Type: application/json" \
    -d "{
      \"presentation_id\": \"test-L02-charts\",
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

  # Build L02 slide (chart + insights - the native analytics layout)
  L02_SLIDE=$(cat <<EOF
{
  "layout": "L02",
  "content": {
    "slide_title": "$title",
    "subtitle": "$chart_type chart via L02",
    "element_3": $CHART_ESCAPED,
    "element_2": $BODY_ESCAPED,
    "logo": " "
  }
}
EOF
)

  # Add slide to array
  if [ "$FIRST" = true ]; then
    SLIDES_JSON="$SLIDES_JSON$L02_SLIDE"
    FIRST=false
  else
    SLIDES_JSON="$SLIDES_JSON,$L02_SLIDE"
  fi

  ((SUCCESS_COUNT++))
  SLIDE_NUM=$((SLIDE_NUM + 1))
  echo "  OK: Generated L02 slide for $chart_type"
done

SLIDES_JSON="$SLIDES_JSON]"

# Save slides JSON for debugging
echo "$SLIDES_JSON" | jq . > "$OUTPUT_DIR/all_slides.json"

echo ""
echo "--- Creating Presentation ---"
echo "Charts generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"
echo "Total slides: $SUCCESS_COUNT"

if [ $SUCCESS_COUNT -eq 0 ]; then
  echo "ERROR: No charts were generated successfully. Check $OUTPUT_DIR for responses."
  exit 1
fi

# Create presentation request
PRES_REQUEST=$(cat <<EOF
{
  "title": "Analytics Test: L02 Layout (Chart Rendering)",
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
echo "Charts tested (all via L02):"
echo "  - line"
echo "  - bar_vertical"
echo "  - pie"
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""

# Open in browser (macOS)
open "$URL"
