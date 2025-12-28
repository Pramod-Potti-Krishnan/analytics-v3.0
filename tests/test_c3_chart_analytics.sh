#!/bin/bash
#
# Test Script: C3-Chart Analytics Variants
#
# Tests all 10 analytics types with C3-chart layout:
#   - revenue_over_time
#   - quarterly_comparison
#   - market_share
#   - yoy_growth
#   - kpi_metrics
#   - category_ranking
#   - correlation_analysis
#   - multidimensional_analysis
#   - multi_metric_comparison
#   - radial_composition
#
# Uses: POST /api/v1/analytics/L02/{analytics_type} endpoint
# Note: Analytics service uses L02 internally, output maps to C3-chart layout
#
# Response Format:
#   - element_3 (or chart_html): Chart HTML with Canvas and Chart.js script
#   - element_2 (or body): AI-generated insights HTML
#
# Usage:
#   ./test_c3_chart_analytics.sh
#   SKIP_IMAGES=true ./test_c3_chart_analytics.sh  # Use synthetic data only
#

# Service URLs
ANALYTICS_SERVICE="https://analytics-v30-production.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/c3_analytics_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Presentation ID (generate unique one)
PRES_ID="test-$(date +%s)"

echo "=============================================="
echo "  C3-Chart Analytics Test Script"
echo "  Testing: 10 Analytics Types"
echo "=============================================="
echo ""
echo "Analytics Service: $ANALYTICS_SERVICE"
echo "Layout Service:    $LAYOUT_SERVICE"
echo "Output Dir:        $OUTPUT_DIR"
echo "Presentation ID:   $PRES_ID"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

# Analytics test configurations: analytics_type|title|narrative|chart_type
# Each test includes appropriate data for the analytics type
declare -a ANALYTICS_TESTS=(
  "revenue_over_time|Revenue Growth Trend|Show quarterly revenue growth from Q1 2023 to Q4 2024 highlighting the strong upward trend in the second half of 2024|line"
  "quarterly_comparison|Quarterly Performance Comparison|Compare Q1 through Q4 2024 revenue performance across different product lines|bar_vertical"
  "market_share|Market Share Distribution|Visualize our market share across different industry segments showing dominance in enterprise sector|pie"
  "yoy_growth|Year-over-Year Growth Analysis|Compare 2023 vs 2024 performance metrics showing significant improvement in key areas|bar_grouped"
  "kpi_metrics|Key Performance Indicators|Display the top 5 KPIs for 2024 including customer satisfaction, revenue per user, and churn rate|bar_horizontal"
  "category_ranking|Product Category Ranking|Rank top 10 product categories by revenue contribution for strategic planning|bar_horizontal"
  "correlation_analysis|Sales vs Marketing Correlation|Analyze the relationship between marketing spend and sales outcomes across regions|scatter"
  "multidimensional_analysis|Multi-Factor Performance|Evaluate performance across 6 key dimensions: quality, speed, cost, innovation, customer satisfaction, and market reach|radar"
  "multi_metric_comparison|Regional Metrics Comparison|Compare 4 key metrics across 5 different regional offices|bar_grouped"
  "radial_composition|Budget Allocation Overview|Show the breakdown of annual budget allocation across major departments|doughnut"
)

# Sample data sets for different analytics types
get_sample_data() {
  local analytics_type=$1

  case $analytics_type in
    "revenue_over_time")
      echo '[
        {"label": "Q1 2023", "value": 2500000},
        {"label": "Q2 2023", "value": 2750000},
        {"label": "Q3 2023", "value": 2900000},
        {"label": "Q4 2023", "value": 3200000},
        {"label": "Q1 2024", "value": 3450000},
        {"label": "Q2 2024", "value": 3800000},
        {"label": "Q3 2024", "value": 4200000},
        {"label": "Q4 2024", "value": 4650000}
      ]'
      ;;
    "quarterly_comparison")
      echo '[
        {"label": "Q1", "value": 1250000},
        {"label": "Q2", "value": 1450000},
        {"label": "Q3", "value": 1680000},
        {"label": "Q4", "value": 1920000}
      ]'
      ;;
    "market_share")
      echo '[
        {"label": "Enterprise", "value": 42},
        {"label": "SMB", "value": 28},
        {"label": "Startup", "value": 15},
        {"label": "Government", "value": 10},
        {"label": "Education", "value": 5}
      ]'
      ;;
    "yoy_growth")
      echo '[
        {"label": "Revenue", "value": 28},
        {"label": "Users", "value": 45},
        {"label": "Retention", "value": 12},
        {"label": "NPS", "value": 18}
      ]'
      ;;
    "kpi_metrics")
      echo '[
        {"label": "Customer Satisfaction", "value": 92},
        {"label": "Revenue per User", "value": 85},
        {"label": "Churn Rate", "value": 3.2},
        {"label": "Net Promoter Score", "value": 78},
        {"label": "Conversion Rate", "value": 24}
      ]'
      ;;
    "category_ranking")
      echo '[
        {"label": "Cloud Services", "value": 4500000},
        {"label": "Enterprise Software", "value": 3800000},
        {"label": "Consulting", "value": 2900000},
        {"label": "Training", "value": 1800000},
        {"label": "Support", "value": 1500000},
        {"label": "Hardware", "value": 1200000}
      ]'
      ;;
    "correlation_analysis")
      echo '[
        {"label": "North", "value": 85},
        {"label": "South", "value": 72},
        {"label": "East", "value": 91},
        {"label": "West", "value": 68},
        {"label": "Central", "value": 78}
      ]'
      ;;
    "multidimensional_analysis")
      echo '[
        {"label": "Quality", "value": 92},
        {"label": "Speed", "value": 85},
        {"label": "Cost Efficiency", "value": 78},
        {"label": "Innovation", "value": 88},
        {"label": "Customer Satisfaction", "value": 94},
        {"label": "Market Reach", "value": 72}
      ]'
      ;;
    "multi_metric_comparison")
      echo '[
        {"label": "Americas", "value": 4200000},
        {"label": "EMEA", "value": 3100000},
        {"label": "APAC", "value": 2800000},
        {"label": "LATAM", "value": 950000}
      ]'
      ;;
    "radial_composition")
      echo '[
        {"label": "R&D", "value": 35},
        {"label": "Sales & Marketing", "value": 28},
        {"label": "Operations", "value": 20},
        {"label": "G&A", "value": 12},
        {"label": "Other", "value": 5}
      ]'
      ;;
    *)
      echo '[]'
      ;;
  esac
}

echo "=============================================="
echo "  Generating Analytics Slides"
echo "=============================================="

for item in "${ANALYTICS_TESTS[@]}"; do
  IFS='|' read -r analytics_type title narrative chart_type <<< "$item"
  ((SLIDE_NUM++))

  echo ""
  echo "----------------------------------------------"
  echo ">>> Test $SLIDE_NUM: $analytics_type"
  echo "    Title: $title"
  echo "    Chart Type: $chart_type"

  # Get appropriate sample data
  SAMPLE_DATA=$(get_sample_data "$analytics_type")

  # Generate analytics content from Analytics Service
  # Using L02 layout as that's what Analytics Service supports
  ANALYTICS_RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/analytics/L02/$analytics_type?use_synthetic=false" \
    -H "Content-Type: application/json" \
    -d "{
      \"presentation_id\": \"$PRES_ID\",
      \"slide_id\": \"slide-$SLIDE_NUM\",
      \"slide_number\": $SLIDE_NUM,
      \"narrative\": \"$narrative\",
      \"data\": $SAMPLE_DATA,
      \"context\": {
        \"theme\": \"professional\",
        \"audience\": \"Executive leadership\",
        \"slide_title\": \"$title\"
      },
      \"chart_type\": \"$chart_type\"
    }")

  # Save raw response
  echo "$ANALYTICS_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_${analytics_type}_response.json"

  # Extract fields from response
  # Analytics service returns element_3 (chart) and element_2 (insights)
  # Also provides aliases: chart_html, body
  CHART_HTML=$(echo "$ANALYTICS_RESPONSE" | jq -r '.content.element_3 // .content.chart_html // ""')
  INSIGHTS_HTML=$(echo "$ANALYTICS_RESPONSE" | jq -r '.content.element_2 // .content.body // ""')

  # Extract metadata
  CHART_TYPE_USED=$(echo "$ANALYTICS_RESPONSE" | jq -r '.metadata.chart_type // "unknown"')
  DATA_POINTS=$(echo "$ANALYTICS_RESPONSE" | jq -r '.metadata.data_points // 0')
  GEN_TIME=$(echo "$ANALYTICS_RESPONSE" | jq -r '.metadata.generation_time_ms // 0')
  SYNTHETIC_USED=$(echo "$ANALYTICS_RESPONSE" | jq -r '.metadata.synthetic_data_used // false')

  if [ -z "$CHART_HTML" ] || [ "$CHART_HTML" == "null" ]; then
    echo "    ERROR: Analytics Service failed to generate chart"
    echo "$ANALYTICS_RESPONSE" | jq . 2>/dev/null || echo "$ANALYTICS_RESPONSE"
    ((FAIL_COUNT++))
    continue
  fi

  echo "    Analytics Service: OK"
  echo "    Chart Type Used: $CHART_TYPE_USED"
  echo "    Data Points: $DATA_POINTS"
  echo "    Generation Time: ${GEN_TIME}ms"
  echo "    Synthetic Data: $SYNTHETIC_USED"
  echo "    Chart HTML: ${#CHART_HTML} chars"
  echo "    Insights HTML: ${#INSIGHTS_HTML} chars"
  ((SUCCESS_COUNT++))

  # Save HTML for inspection
  echo "$CHART_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${analytics_type}_chart.html"
  echo "$INSIGHTS_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${analytics_type}_insights.html"

  # Escape for JSON
  CHART_ESCAPED=$(echo "$CHART_HTML" | jq -Rs .)

  # Build slide JSON for Layout Service using C3-chart layout
  # C3-chart expects: slide_title, subtitle, chart_html
  SLIDE_JSON="{
    \"layout\": \"C3-chart\",
    \"content\": {
      \"slide_title\": \"$title\",
      \"subtitle\": \"Analytics Type: $analytics_type | Chart: $CHART_TYPE_USED\",
      \"chart_html\": $CHART_ESCAPED,
      \"presentation_name\": \"C3 Analytics Test\",
      \"logo\": \" \"
    }
  }"

  # Add to slides array
  if [ "$FIRST_SLIDE" = true ]; then
    SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
    FIRST_SLIDE=false
  else
    SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
  fi
done

# Close slides array
SLIDES_JSON="$SLIDES_JSON]"

echo ""
echo "=============================================="
echo "  Creating Presentation"
echo "=============================================="
echo ""
echo "Slides generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

# Save slides JSON for debugging
echo "$SLIDES_JSON" > "$OUTPUT_DIR/all_slides.json"

# Create single presentation with all slides
LAYOUT_REQUEST="{
  \"title\": \"C3-Chart Analytics Test - 10 Analytics Types\",
  \"template_id\": \"L25\",
  \"slides\": $SLIDES_JSON
}"

echo "$LAYOUT_REQUEST" > "$OUTPUT_DIR/layout_request.json"

LAYOUT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d "$LAYOUT_REQUEST")

echo "$LAYOUT_RESPONSE" > "$OUTPUT_DIR/layout_response.json"

PRES_ID_RESULT=$(echo "$LAYOUT_RESPONSE" | jq -r '.id')

if [ "$PRES_ID_RESULT" == "null" ] || [ -z "$PRES_ID_RESULT" ]; then
  echo "ERROR: Layout Service failed to create presentation"
  echo "$LAYOUT_RESPONSE" | jq . 2>/dev/null || echo "$LAYOUT_RESPONSE"
  exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID_RESULT"

echo ""
echo "=============================================="
echo "  SUCCESS! C3-Chart Analytics Test Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID_RESULT"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT / $SLIDE_NUM"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] All 10 analytics types generated successfully"
echo "  [ ] Charts render correctly in C3-chart layout"
echo "  [ ] Chart.js interactive features work (hover, tooltips)"
echo "  [ ] Data labels visible on chart elements"
echo "  [ ] Professional color scheme applied"
echo "  [ ] Chart scales and axes properly formatted"
echo "  [ ] No overflow or truncation"
echo "  [ ] Responsive sizing within slide area"
echo ""
echo "Analytics Types Tested:"
echo "  1. revenue_over_time (line chart)"
echo "  2. quarterly_comparison (bar chart)"
echo "  3. market_share (pie chart)"
echo "  4. yoy_growth (grouped bar chart)"
echo "  5. kpi_metrics (horizontal bar chart)"
echo "  6. category_ranking (horizontal bar chart)"
echo "  7. correlation_analysis (scatter chart)"
echo "  8. multidimensional_analysis (radar chart)"
echo "  9. multi_metric_comparison (grouped bar chart)"
echo "  10. radial_composition (doughnut chart)"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
