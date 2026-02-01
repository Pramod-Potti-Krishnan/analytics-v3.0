#!/bin/bash
#
# Test Script: DATA_ARCHITECTURE Atomic Endpoint v1.0
# Tests ER diagram generation with explicit entities, LLM generation, and placeholder mode
#
# v1.0.0 Initial Release:
# - Explicit entity/relationship definitions
# - LLM-generated schemas from prompts
# - Placeholder mode with fallback schemas
# - Light/dark theme support
# - Grid positioning verification
#

ANALYTICS_SERVICE="${ANALYTICS_SERVICE:-https://analytics-v30-production.up.railway.app}"
# For local testing: ANALYTICS_SERVICE="http://localhost:8080"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="./test_outputs/data_architecture_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "  DATA_ARCHITECTURE Atomic Endpoint Test v1.0"
echo "=============================================="
echo "Service: $ANALYTICS_SERVICE"
echo "Output:  $OUTPUT_DIR"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local description="$2"
    local payload="$3"
    local expected_check="$4"  # jq expression that should return "true"

    echo "--- Test: $test_name ---"
    echo "Description: $description"

    # Make request
    RESPONSE=$(curl -s -X POST "$ANALYTICS_SERVICE/api/v1/charts/atomic/DATA_ARCHITECTURE" \
        -H "Content-Type: application/json" \
        -d "$payload")

    # Save response
    echo "$RESPONSE" | jq . > "$OUTPUT_DIR/${test_name}.json" 2>/dev/null

    # Check success
    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

    if [ "$SUCCESS" = "true" ]; then
        # Run expected check if provided
        if [ -n "$expected_check" ]; then
            CHECK_RESULT=$(echo "$RESPONSE" | jq -r "$expected_check")
            if [ "$CHECK_RESULT" = "true" ]; then
                echo -e "${GREEN}✓ PASSED${NC}"
                TESTS_PASSED=$((TESTS_PASSED + 1))
            else
                echo -e "${RED}✗ FAILED - Check failed: $expected_check${NC}"
                TESTS_FAILED=$((TESTS_FAILED + 1))
            fi
        else
            echo -e "${GREEN}✓ PASSED${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        fi

        # Extract and save HTML for inspection
        echo "$RESPONSE" | jq -r '.html_content // empty' > "$OUTPUT_DIR/${test_name}.html" 2>/dev/null

        # Show stats
        ENTITY_COUNT=$(echo "$RESPONSE" | jq -r '.entities | length // 0')
        REL_COUNT=$(echo "$RESPONSE" | jq -r '.relationships | length // 0')
        GEN_TIME=$(echo "$RESPONSE" | jq -r '.generation_time_ms // 0')
        SOURCE=$(echo "$RESPONSE" | jq -r '.source // "unknown"')
        echo "  Entities: $ENTITY_COUNT, Relationships: $REL_COUNT"
        echo "  Source: $SOURCE, Time: ${GEN_TIME}ms"
    else
        echo -e "${RED}✗ FAILED - Request failed${NC}"
        echo "$RESPONSE" | jq -r '.message // .detail // .' | head -5
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# ===== TEST 1: Explicit Entities =====
echo ""
echo "========== TEST GROUP 1: EXPLICIT MODE =========="
echo ""

run_test "explicit_simple" "Simple explicit entities with 2 tables" '{
    "presentation_id": "test-pres-001",
    "slide_id": "slide-1",
    "diagram_index": 0,
    "entities": [
        {
            "name": "users",
            "type": "table",
            "fields": [
                {"name": "id", "data_type": "INT", "is_primary_key": true, "is_nullable": false},
                {"name": "email", "data_type": "VARCHAR(255)", "is_nullable": false},
                {"name": "name", "data_type": "VARCHAR(100)"}
            ],
            "x_position": 25,
            "y_position": 40
        },
        {
            "name": "posts",
            "type": "table",
            "fields": [
                {"name": "id", "data_type": "INT", "is_primary_key": true, "is_nullable": false},
                {"name": "user_id", "data_type": "INT", "is_foreign_key": true, "references": "users.id"},
                {"name": "title", "data_type": "VARCHAR(200)", "is_nullable": false},
                {"name": "content", "data_type": "TEXT"}
            ],
            "x_position": 65,
            "y_position": 40
        }
    ],
    "relationships": [
        {
            "from_entity": "ent-posts",
            "from_field": "user_id",
            "to_entity": "ent-users",
            "to_field": "id",
            "cardinality": "many_to_one",
            "label": "authored by"
        }
    ],
    "title": "Simple Blog Schema"
}' '.source == "explicit" and (.entities | length) == 2'

run_test "explicit_with_junction" "Explicit with junction table (M:N)" '{
    "presentation_id": "test-pres-002",
    "slide_id": "slide-1",
    "entities": [
        {
            "name": "students",
            "type": "table",
            "fields": [
                {"name": "id", "data_type": "INT", "is_primary_key": true},
                {"name": "name", "data_type": "VARCHAR(100)"}
            ],
            "x_position": 15,
            "y_position": 40
        },
        {
            "name": "courses",
            "type": "table",
            "fields": [
                {"name": "id", "data_type": "INT", "is_primary_key": true},
                {"name": "title", "data_type": "VARCHAR(200)"}
            ],
            "x_position": 75,
            "y_position": 40
        },
        {
            "name": "enrollments",
            "type": "junction",
            "fields": [
                {"name": "student_id", "data_type": "INT", "is_foreign_key": true},
                {"name": "course_id", "data_type": "INT", "is_foreign_key": true},
                {"name": "enrolled_at", "data_type": "TIMESTAMP"}
            ],
            "x_position": 45,
            "y_position": 40
        }
    ],
    "relationships": [],
    "title": "Student-Course Enrollment"
}' '.source == "explicit" and (.entities | length) == 3'

# ===== TEST 2: LLM Generation =====
echo ""
echo "========== TEST GROUP 2: LLM GENERATION =========="
echo ""

run_test "llm_ecommerce" "LLM generates e-commerce schema" '{
    "presentation_id": "test-pres-003",
    "slide_id": "slide-1",
    "prompt": "Design a database schema for an e-commerce platform with users, products, orders, and reviews",
    "theme_mode": "light"
}' '.source == "llm" or .source == "placeholder"'

run_test "llm_blog" "LLM generates blog/CMS schema" '{
    "presentation_id": "test-pres-004",
    "slide_id": "slide-1",
    "prompt": "Create a blog database with posts, categories, tags, and comments"
}' '(.entities | length) >= 3'

run_test "llm_auth" "LLM generates authentication schema" '{
    "presentation_id": "test-pres-005",
    "slide_id": "slide-1",
    "prompt": "Design an authentication system with users, roles, permissions, and sessions"
}' '(.entities | length) >= 3'

# ===== TEST 3: Placeholder Mode =====
echo ""
echo "========== TEST GROUP 3: PLACEHOLDER MODE =========="
echo ""

run_test "placeholder_basic" "Placeholder mode with no prompt" '{
    "presentation_id": "test-pres-006",
    "slide_id": "slide-1",
    "placeholder_mode": true
}' '.source == "placeholder" and (.entities | length) >= 3'

run_test "placeholder_ecommerce" "Placeholder mode with ecommerce hint" '{
    "presentation_id": "test-pres-007",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "prompt": "online store with shopping cart"
}' '.source == "placeholder"'

run_test "placeholder_social" "Placeholder mode with social hint" '{
    "presentation_id": "test-pres-008",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "prompt": "social network with followers and messages"
}' '.source == "placeholder"'

# ===== TEST 4: Theme Support =====
echo ""
echo "========== TEST GROUP 4: THEME SUPPORT =========="
echo ""

run_test "theme_light" "Light theme rendering" '{
    "presentation_id": "test-pres-009",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "theme_mode": "light"
}' '.html_content | contains("theme-light")'

run_test "theme_dark" "Dark theme rendering" '{
    "presentation_id": "test-pres-010",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "theme_mode": "dark"
}' '.html_content | contains("theme-dark")'

# ===== TEST 5: Display Options =====
echo ""
echo "========== TEST GROUP 5: DISPLAY OPTIONS =========="
echo ""

run_test "hide_data_types" "Hide data type annotations" '{
    "presentation_id": "test-pres-011",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "show_data_types": false
}' '.success == true'

run_test "hide_nullable" "Hide nullable indicators" '{
    "presentation_id": "test-pres-012",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "show_nullable": false
}' '.success == true'

run_test "hide_title" "Hide diagram title" '{
    "presentation_id": "test-pres-013",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "show_title": false
}' '.success == true'

# ===== TEST 6: Grid Positioning =====
echo ""
echo "========== TEST GROUP 6: GRID POSITIONING =========="
echo ""

run_test "position_preset_full" "Full content position preset" '{
    "presentation_id": "test-pres-014",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "position_preset": "full_content"
}' '.grid_position.start_col == 2 and .grid_position.start_row == 4'

run_test "position_manual" "Manual grid positioning" '{
    "presentation_id": "test-pres-015",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "start_col": 5,
    "start_row": 6,
    "gridWidth": 20,
    "gridHeight": 10
}' '.grid_position.start_col == 5 and .grid_position.start_row == 6'

# ===== TEST 7: Element ID Persistence =====
echo ""
echo "========== TEST GROUP 7: ELEMENT ID PERSISTENCE =========="
echo ""

run_test "element_id_provided" "Preserve provided element_id" '{
    "presentation_id": "test-pres-016",
    "slide_id": "slide-1",
    "placeholder_mode": true,
    "element_id": "my-custom-element-id-12345"
}' '.element_id == "my-custom-element-id-12345"'

run_test "element_id_generated" "Generate new element_id when not provided" '{
    "presentation_id": "test-pres-017",
    "slide_id": "slide-1",
    "placeholder_mode": true
}' '.element_id | startswith("data-arch-")'

# ===== Summary =====
echo "=============================================="
echo "                TEST SUMMARY"
echo "=============================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "Total:  $((TESTS_PASSED + TESTS_FAILED))"
echo ""
echo "Output files saved to: $OUTPUT_DIR"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Some tests failed. Check the output files for details.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
