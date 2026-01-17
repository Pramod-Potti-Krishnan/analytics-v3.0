#!/bin/bash
#
# Master Test Script: All Atomic Charts - C1-text & C3-chart Layouts
# Version: 3.6.0
#
# Runs all 3 phases to test all 14 gold standard atomic chart types
# against both C1-text and C3-chart layouts.
#
# Usage:
#   ./test_atomic_c1_c3_all.sh           # Run all phases
#   ./test_atomic_c1_c3_all.sh --phase1  # Run only phase 1
#   ./test_atomic_c1_c3_all.sh --phase2  # Run only phase 2
#   ./test_atomic_c1_c3_all.sh --phase3  # Run only phase 3
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ANALYTICS_URL="${ANALYTICS_URL:-https://analytics-v30-production.up.railway.app}"
LAYOUT_URL="${LAYOUT_URL:-https://web-production-f0d13.up.railway.app}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MASTER_OUTPUT_DIR="./test_outputs/atomic_c1_c3_all_${TIMESTAMP}"

mkdir -p "$MASTER_OUTPUT_DIR"

echo ""
echo -e "${CYAN}=============================================="
echo "  ATOMIC CHARTS COMPLETE TEST SUITE"
echo "  Version: 3.6.0"
echo "==============================================${NC}"
echo ""
echo "This script tests ALL 14 gold standard atomic chart types"
echo "against both C1-text and C3-chart layouts."
echo ""
echo "Analytics: $ANALYTICS_URL"
echo "Layout:    $LAYOUT_URL"
echo "Output:    $MASTER_OUTPUT_DIR"
echo ""

# Parse arguments
RUN_PHASE1=false
RUN_PHASE2=false
RUN_PHASE3=false

if [ $# -eq 0 ]; then
    # No arguments - run all phases
    RUN_PHASE1=true
    RUN_PHASE2=true
    RUN_PHASE3=true
else
    for arg in "$@"; do
        case $arg in
            --phase1)
                RUN_PHASE1=true
                ;;
            --phase2)
                RUN_PHASE2=true
                ;;
            --phase3)
                RUN_PHASE3=true
                ;;
            --help|-h)
                echo "Usage: $0 [--phase1] [--phase2] [--phase3]"
                echo ""
                echo "Options:"
                echo "  --phase1  Run Phase 1 (line, bar_vertical, bar_horizontal, pie, doughnut)"
                echo "  --phase2  Run Phase 2 (scatter, bubble, polar_area, radar, area)"
                echo "  --phase3  Run Phase 3 (area_stacked, bar_grouped, bar_stacked, waterfall)"
                echo ""
                echo "If no options specified, all phases are run."
                exit 0
                ;;
            *)
                echo "Unknown option: $arg"
                echo "Use --help for usage information."
                exit 1
                ;;
        esac
    done
fi

# Track results
PHASE1_STATUS="skipped"
PHASE2_STATUS="skipped"
PHASE3_STATUS="skipped"
TOTAL_SUCCESS=0
TOTAL_FAIL=0
PRESENTATION_URLS=()

# ============================================
# Phase 1: First 5 Charts
# ============================================
if [ "$RUN_PHASE1" = true ]; then
    echo -e "${BLUE}=============================================="
    echo "  PHASE 1: First 5 Charts"
    echo "  line, bar_vertical, bar_horizontal, pie, doughnut"
    echo "==============================================${NC}"
    echo ""

    if [ -f "$SCRIPT_DIR/test_atomic_c1_c3_phase1.sh" ]; then
        # Run phase 1 and capture output directory
        bash "$SCRIPT_DIR/test_atomic_c1_c3_phase1.sh" 2>&1 | tee "$MASTER_OUTPUT_DIR/phase1_output.log"
        PHASE1_EXIT=${PIPESTATUS[0]}

        if [ $PHASE1_EXIT -eq 0 ]; then
            PHASE1_STATUS="success"
            TOTAL_SUCCESS=$((TOTAL_SUCCESS + 5))
            echo -e "${GREEN}Phase 1: PASSED${NC}"
        else
            PHASE1_STATUS="failed"
            echo -e "${RED}Phase 1: FAILED${NC}"
        fi

        # Extract URLs from log
        PHASE1_C1_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase1_output.log" | head -1)
        PHASE1_C3_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase1_output.log" | tail -1)

        if [ -n "$PHASE1_C1_URL" ]; then
            PRESENTATION_URLS+=("Phase 1 C1-text: $PHASE1_C1_URL")
        fi
        if [ -n "$PHASE1_C3_URL" ]; then
            PRESENTATION_URLS+=("Phase 1 C3-chart: $PHASE1_C3_URL")
        fi
    else
        echo -e "${RED}Error: test_atomic_c1_c3_phase1.sh not found${NC}"
        PHASE1_STATUS="error"
    fi
    echo ""
fi

# ============================================
# Phase 2: Next 5 Charts
# ============================================
if [ "$RUN_PHASE2" = true ]; then
    echo -e "${BLUE}=============================================="
    echo "  PHASE 2: Next 5 Charts"
    echo "  scatter, bubble, polar_area, radar, area"
    echo "==============================================${NC}"
    echo ""

    if [ -f "$SCRIPT_DIR/test_atomic_c1_c3_phase2.sh" ]; then
        bash "$SCRIPT_DIR/test_atomic_c1_c3_phase2.sh" 2>&1 | tee "$MASTER_OUTPUT_DIR/phase2_output.log"
        PHASE2_EXIT=${PIPESTATUS[0]}

        if [ $PHASE2_EXIT -eq 0 ]; then
            PHASE2_STATUS="success"
            TOTAL_SUCCESS=$((TOTAL_SUCCESS + 5))
            echo -e "${GREEN}Phase 2: PASSED${NC}"
        else
            PHASE2_STATUS="failed"
            echo -e "${RED}Phase 2: FAILED${NC}"
        fi

        # Extract URLs from log
        PHASE2_C1_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase2_output.log" | head -1)
        PHASE2_C3_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase2_output.log" | tail -1)

        if [ -n "$PHASE2_C1_URL" ]; then
            PRESENTATION_URLS+=("Phase 2 C1-text: $PHASE2_C1_URL")
        fi
        if [ -n "$PHASE2_C3_URL" ]; then
            PRESENTATION_URLS+=("Phase 2 C3-chart: $PHASE2_C3_URL")
        fi
    else
        echo -e "${RED}Error: test_atomic_c1_c3_phase2.sh not found${NC}"
        PHASE2_STATUS="error"
    fi
    echo ""
fi

# ============================================
# Phase 3: Last 4 Charts
# ============================================
if [ "$RUN_PHASE3" = true ]; then
    echo -e "${BLUE}=============================================="
    echo "  PHASE 3: Last 4 Charts"
    echo "  area_stacked, bar_grouped, bar_stacked, waterfall"
    echo "==============================================${NC}"
    echo ""

    if [ -f "$SCRIPT_DIR/test_atomic_c1_c3_phase3.sh" ]; then
        bash "$SCRIPT_DIR/test_atomic_c1_c3_phase3.sh" 2>&1 | tee "$MASTER_OUTPUT_DIR/phase3_output.log"
        PHASE3_EXIT=${PIPESTATUS[0]}

        if [ $PHASE3_EXIT -eq 0 ]; then
            PHASE3_STATUS="success"
            TOTAL_SUCCESS=$((TOTAL_SUCCESS + 4))
            echo -e "${GREEN}Phase 3: PASSED${NC}"
        else
            PHASE3_STATUS="failed"
            echo -e "${RED}Phase 3: FAILED${NC}"
        fi

        # Extract URLs from log
        PHASE3_C1_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase3_output.log" | head -1)
        PHASE3_C3_URL=$(grep -o "https://web-production-f0d13.up.railway.app/p/[a-zA-Z0-9-]*" "$MASTER_OUTPUT_DIR/phase3_output.log" | tail -1)

        if [ -n "$PHASE3_C1_URL" ]; then
            PRESENTATION_URLS+=("Phase 3 C1-text: $PHASE3_C1_URL")
        fi
        if [ -n "$PHASE3_C3_URL" ]; then
            PRESENTATION_URLS+=("Phase 3 C3-chart: $PHASE3_C3_URL")
        fi
    else
        echo -e "${RED}Error: test_atomic_c1_c3_phase3.sh not found${NC}"
        PHASE3_STATUS="error"
    fi
    echo ""
fi

# ============================================
# Generate Combined Report
# ============================================
echo "--- Generating Combined Report ---"

cat > "$MASTER_OUTPUT_DIR/combined_report.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "test_suite": "Atomic Charts C1 & C3 Complete",
    "version": "3.6.0",
    "services": {
        "analytics": "$ANALYTICS_URL",
        "layout": "$LAYOUT_URL"
    },
    "phases": {
        "phase1": {
            "status": "$PHASE1_STATUS",
            "charts": ["line", "bar_vertical", "bar_horizontal", "pie", "doughnut"],
            "count": 5
        },
        "phase2": {
            "status": "$PHASE2_STATUS",
            "charts": ["scatter", "bubble", "polar_area", "radar", "area"],
            "count": 5
        },
        "phase3": {
            "status": "$PHASE3_STATUS",
            "charts": ["area_stacked", "bar_grouped", "bar_stacked", "waterfall"],
            "count": 4
        }
    },
    "summary": {
        "total_charts": 14,
        "phases_run": $([ "$RUN_PHASE1" = true ] && echo 1 || echo 0)$([ "$RUN_PHASE2" = true ] && echo "+1" || echo "+0")$([ "$RUN_PHASE3" = true ] && echo "+1" || echo "+0") | bc,
        "phase1_status": "$PHASE1_STATUS",
        "phase2_status": "$PHASE2_STATUS",
        "phase3_status": "$PHASE3_STATUS"
    },
    "output_directory": "$MASTER_OUTPUT_DIR"
}
EOF

echo "Combined Report: $MASTER_OUTPUT_DIR/combined_report.json"

# ============================================
# Final Summary
# ============================================
echo ""
echo -e "${CYAN}=============================================="
echo "  COMPLETE TEST SUITE RESULTS"
echo "==============================================${NC}"
echo ""
echo "14 Gold Standard Atomic Chart Types:"
echo ""
echo "Phase 1 (5 charts): line, bar_vertical, bar_horizontal, pie, doughnut"
if [ "$PHASE1_STATUS" = "success" ]; then
    echo -e "  Status: ${GREEN}PASSED${NC}"
elif [ "$PHASE1_STATUS" = "failed" ]; then
    echo -e "  Status: ${RED}FAILED${NC}"
else
    echo -e "  Status: ${YELLOW}$PHASE1_STATUS${NC}"
fi
echo ""

echo "Phase 2 (5 charts): scatter, bubble, polar_area, radar, area"
if [ "$PHASE2_STATUS" = "success" ]; then
    echo -e "  Status: ${GREEN}PASSED${NC}"
elif [ "$PHASE2_STATUS" = "failed" ]; then
    echo -e "  Status: ${RED}FAILED${NC}"
else
    echo -e "  Status: ${YELLOW}$PHASE2_STATUS${NC}"
fi
echo ""

echo "Phase 3 (4 charts): area_stacked, bar_grouped, bar_stacked, waterfall"
if [ "$PHASE3_STATUS" = "success" ]; then
    echo -e "  Status: ${GREEN}PASSED${NC}"
elif [ "$PHASE3_STATUS" = "failed" ]; then
    echo -e "  Status: ${RED}FAILED${NC}"
else
    echo -e "  Status: ${YELLOW}$PHASE3_STATUS${NC}"
fi
echo ""

echo "=============================================="
echo "  PRESENTATION URLs"
echo "=============================================="
echo ""
for url in "${PRESENTATION_URLS[@]}"; do
    echo "  $url"
done
echo ""

echo "Output Directory: $MASTER_OUTPUT_DIR"
echo ""

# Calculate overall status
ALL_SUCCESS=true
if [ "$RUN_PHASE1" = true ] && [ "$PHASE1_STATUS" != "success" ]; then
    ALL_SUCCESS=false
fi
if [ "$RUN_PHASE2" = true ] && [ "$PHASE2_STATUS" != "success" ]; then
    ALL_SUCCESS=false
fi
if [ "$RUN_PHASE3" = true ] && [ "$PHASE3_STATUS" != "success" ]; then
    ALL_SUCCESS=false
fi

if [ "$ALL_SUCCESS" = true ]; then
    echo -e "${GREEN}=============================================="
    echo "  ALL TESTS PASSED!"
    echo "==============================================${NC}"
    exit 0
else
    echo -e "${RED}=============================================="
    echo "  SOME TESTS FAILED"
    echo "==============================================${NC}"
    exit 1
fi
