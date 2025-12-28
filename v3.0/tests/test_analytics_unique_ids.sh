#!/bin/bash
# test_analytics_unique_ids.sh
# Tests: Each slide gets its own Analytics call with unique slide_number
# This matches how the Director actually works (Option A)

set -e

ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

OUTPUT_DIR="./test_outputs/analytics_unique_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  Analytics Unique ID Test (C3 + V2)"
echo "=============================================="
echo "Analytics Service: $ANALYTICS_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Each slide gets its own Analytics call with unique slide_number"
echo ""

# Define slides: layout|chart_type|analytics_type|title
declare -a SLIDES=(
  "C3-chart|line|revenue_over_time|Revenue Trends (C3)"
  "V2-chart-text|line|revenue_over_time|Revenue Trends (V2)"
  "C3-chart|bar_vertical|category_ranking|Department Performance (C3)"
  "V2-chart-text|bar_vertical|category_ranking|Department Performance (V2)"
  "C3-chart|pie|market_share|Market Share (C3)"
  "V2-chart-text|pie|market_share|Market Share (V2)"
)

SLIDES_JSON="["
FIRST=true
SLIDE_NUM=1

for slide_def in "${SLIDES[@]}"; do
  IFS='|' read -r layout chart_type analytics_type title <<< "$slide_def"

  echo "--- [Slide $SLIDE_NUM] $layout - $chart_type ---"

  # Each slide gets its own Analytics call with unique slide_number
  RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/analytics/L02/$analytics_type?use_synthetic=true" \
    -H "Content-Type: application/json" \
    -d "{
      \"presentation_id\": \"test-unique-ids\",
      \"slide_id\": \"slide-$SLIDE_NUM\",
      \"slide_number\": $SLIDE_NUM,
      \"narrative\": \"Test chart for slide $SLIDE_NUM\",
      \"chart_type\": \"$chart_type\"
    }")

  # Extract chart HTML
  CHART_HTML=$(echo "$RESPONSE" | jq -r '.content.chart_html // .content.element_3 // empty')
  BODY_HTML=$(echo "$RESPONSE" | jq -r '.content.body // .content.element_2 // empty')

  if [ -z "$CHART_HTML" ]; then
    echo "  ERROR: No chart_html in response"
    continue
  fi

  # Check the canvas ID in the generated HTML
  CANVAS_ID=$(echo "$CHART_HTML" | grep -o 'id="chart-slide-[0-9]*"' | head -1)
  echo "  Canvas ID: $CANVAS_ID"

  # Save for debugging
  echo "$CHART_HTML" > "$OUTPUT_DIR/slide_${SLIDE_NUM}_chart.html"

  # Escape for JSON
  CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)
  BODY_ESCAPED=$(echo "$BODY_HTML" | jq -Rs .)

  # Build slide JSON based on layout
  if [ "$layout" = "C3-chart" ]; then
    SLIDE_JSON=$(cat <<EOF
{
  "layout": "C3-chart",
  "content": {
    "slide_title": "$title",
    "subtitle": "$chart_type chart - slide $SLIDE_NUM",
    "chart_html": $CHART_ESCAPED,
    "logo": " "
  }
}
EOF
)
  else
    SLIDE_JSON=$(cat <<EOF
{
  "layout": "V2-chart-text",
  "content": {
    "slide_title": "$title",
    "subtitle": "$chart_type chart - slide $SLIDE_NUM",
    "chart_html": $CHART_ESCAPED,
    "body": $BODY_ESCAPED,
    "logo": " "
  }
}
EOF
)
  fi

  # Add to slides array
  if [ "$FIRST" = true ]; then
    SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
    FIRST=false
  else
    SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
  fi

  SLIDE_NUM=$((SLIDE_NUM + 1))
done

SLIDES_JSON="$SLIDES_JSON]"

echo ""
echo "--- Verifying Unique Canvas IDs ---"
grep -h 'id="chart-slide-[0-9]*"' "$OUTPUT_DIR"/slide_*_chart.html | sort

echo ""
echo "--- Creating Presentation ---"

PRES_REQUEST=$(cat <<EOF
{
  "title": "Analytics Unique ID Test (C3 + V2)",
  "template_id": "L25",
  "slides": $SLIDES_JSON
}
EOF
)

echo "$PRES_REQUEST" > "$OUTPUT_DIR/presentation_request.json"

PRES_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d "$PRES_REQUEST")

echo "$PRES_RESPONSE" > "$OUTPUT_DIR/presentation_response.json"

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
echo "Expected canvas IDs (all unique):"
echo "  Slide 0 (C3): chart-slide-1"
echo "  Slide 1 (V2): chart-slide-2"
echo "  Slide 2 (C3): chart-slide-3"
echo "  Slide 3 (V2): chart-slide-4"
echo "  Slide 4 (C3): chart-slide-5"
echo "  Slide 5 (V2): chart-slide-6"
echo ""
echo "Output: $OUTPUT_DIR"

# Open in browser (macOS)
open "$URL"
