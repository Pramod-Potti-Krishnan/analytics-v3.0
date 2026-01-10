#!/bin/bash
# ==============================================
#   Test: Create Element API v3.7.0
#   Creates charts as independent Layout Service elements
# ==============================================

set -e

# Configuration
ANALYTICS_URL="${ANALYTICS_URL:-https://analytics-v30-production.up.railway.app}"
LAYOUT_URL="${LAYOUT_URL:-https://web-production-f0d13.up.railway.app}"
OUTPUT_DIR="./test_outputs/create_element_v37_$(date +%Y%m%d_%H%M%S)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=============================================="
echo "  Create Element API Test v3.7.0"
echo "  Charts as Independent Layout Service Elements"
echo "=============================================="
echo "Analytics: $ANALYTICS_URL"
echo "Layout:    $LAYOUT_URL"
echo "Output:    $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# -----------------------------------------
# Step 1: Create a presentation
# -----------------------------------------
echo -e "${BLUE}--- Step 1: Creating Presentation ---${NC}"

PRES_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Create Element Test v3.7.0",
    "subtitle": "Charts as Independent Elements",
    "theme": "professional"
  }')

PRES_ID=$(echo "$PRES_RESPONSE" | jq -r '.presentation.id // .id // empty')

if [ -z "$PRES_ID" ]; then
  echo -e "${RED}Failed to create presentation${NC}"
  echo "$PRES_RESPONSE" | jq .
  exit 1
fi

echo -e "${GREEN}Created presentation: $PRES_ID${NC}"
echo "$PRES_RESPONSE" > "$OUTPUT_DIR/1_presentation_created.json"

# -----------------------------------------
# Step 2: Add a slide
# -----------------------------------------
echo -e "${BLUE}--- Step 2: Adding Slide ---${NC}"

SLIDE_RESPONSE=$(curl -s -X POST "$LAYOUT_URL/api/presentations/$PRES_ID/slides" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "C1-text",
    "title": "Create Element Test",
    "subtitle": "Testing chart as independent element"
  }')

echo "$SLIDE_RESPONSE" > "$OUTPUT_DIR/2_slide_created.json"
echo -e "${GREEN}Slide added${NC}"

# -----------------------------------------
# Step 3: Create chart element via new API
# -----------------------------------------
echo -e "${BLUE}--- Step 3: Creating Chart Element (Line) ---${NC}"

ELEMENT_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/create-element" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "'$PRES_ID'",
    "slide_index": 0,
    "chart_type": "line",
    "layout_service_url": "'$LAYOUT_URL'",
    "narrative": "Show quarterly revenue growth for 2024 with strong Q3-Q4 performance",
    "theme": "professional",
    "enable_editor": true
  }')

echo "$ELEMENT_RESPONSE" | jq . > "$OUTPUT_DIR/3_element_created.json"

ELEMENT_SUCCESS=$(echo "$ELEMENT_RESPONSE" | jq -r '.success // false')
ELEMENT_ID=$(echo "$ELEMENT_RESPONSE" | jq -r '.element_id // empty')
POSITION=$(echo "$ELEMENT_RESPONSE" | jq -r '.position')
SIZE=$(echo "$ELEMENT_RESPONSE" | jq -r '.size')

if [ "$ELEMENT_SUCCESS" = "true" ]; then
  echo -e "${GREEN}Element created successfully!${NC}"
  echo "  Element ID: $ELEMENT_ID"
  echo "  Position: $POSITION"
  echo "  Size: $SIZE"
  echo "  Chart Type: $(echo "$ELEMENT_RESPONSE" | jq -r '.chart_type')"
  echo "  Data Points: $(echo "$ELEMENT_RESPONSE" | jq -r '.data_points')"
  echo "  Generation Time: $(echo "$ELEMENT_RESPONSE" | jq -r '.generation_time_ms')ms"
else
  echo -e "${RED}Element creation failed!${NC}"
  echo "$ELEMENT_RESPONSE" | jq .
fi

# -----------------------------------------
# Step 4: Create second chart element (Pie)
# -----------------------------------------
echo -e "${BLUE}--- Step 4: Creating Second Chart Element (Pie) ---${NC}"

ELEMENT2_RESPONSE=$(curl -s -X POST "$ANALYTICS_URL/api/v1/charts/atomic/create-element" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "'$PRES_ID'",
    "slide_index": 0,
    "chart_type": "pie",
    "layout_service_url": "'$LAYOUT_URL'",
    "narrative": "Market share distribution by company segment",
    "theme": "professional",
    "enable_editor": true
  }')

echo "$ELEMENT2_RESPONSE" | jq . > "$OUTPUT_DIR/4_element2_created.json"

ELEMENT2_SUCCESS=$(echo "$ELEMENT2_RESPONSE" | jq -r '.success // false')

if [ "$ELEMENT2_SUCCESS" = "true" ]; then
  echo -e "${GREEN}Second element created successfully!${NC}"
  echo "  Element ID: $(echo "$ELEMENT2_RESPONSE" | jq -r '.element_id')"
  echo "  Position: $(echo "$ELEMENT2_RESPONSE" | jq -r '.position')"
  echo "  Size: $(echo "$ELEMENT2_RESPONSE" | jq -r '.size')"
else
  echo -e "${YELLOW}Second element creation failed (may be expected if slide is full)${NC}"
  echo "$ELEMENT2_RESPONSE" | jq -r '.message // .error_code // empty'
fi

# -----------------------------------------
# Step 5: Generate summary
# -----------------------------------------
echo ""
echo "=============================================="
echo "  TEST RESULTS"
echo "=============================================="
echo ""
echo "Presentation URL:"
echo -e "${GREEN}$LAYOUT_URL/p/$PRES_ID${NC}"
echo ""
echo "Output Directory: $OUTPUT_DIR"
echo ""
echo "Files generated:"
ls -la "$OUTPUT_DIR/"
echo ""

# Save summary
cat > "$OUTPUT_DIR/test_summary.json" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "3.7.0",
  "test": "create-element",
  "presentation_id": "$PRES_ID",
  "presentation_url": "$LAYOUT_URL/p/$PRES_ID",
  "element_1": {
    "success": $ELEMENT_SUCCESS,
    "element_id": "$ELEMENT_ID"
  },
  "element_2": {
    "success": $ELEMENT2_SUCCESS
  }
}
EOF

echo "Summary saved to $OUTPUT_DIR/test_summary.json"
echo ""

# Open in browser
if command -v open &> /dev/null; then
  echo "Opening presentation in browser..."
  open "$LAYOUT_URL/p/$PRES_ID"
fi

echo "Done!"
