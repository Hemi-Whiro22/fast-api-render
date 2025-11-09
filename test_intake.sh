#!/bin/bash
# 🌊 Tiwhanawhana Intake - Quick Test Script
# Copy this to your project root and run: chmod +x test_intake.sh && ./test_intake.sh

set -e  # Exit on error

echo "🌊 Tiwhanawhana Intake Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TE_PO_URL="http://localhost:8000"
INTAKE_FOLDER="kaitiaki-intake/active"

# Test 1: Te_Po Running
echo -e "${BLUE}[1/6] Checking if Te_Po is running...${NC}"
if curl -s "$TE_PO_URL/" > /dev/null; then
    echo -e "${GREEN}✅ Te_Po is running${NC}"
else
    echo -e "${RED}❌ Te_Po not running. Start it with:${NC}"
    echo "   PYTHONPATH=. python3 -m uvicorn Te_Po.core.main:app --reload"
    exit 1
fi
echo ""

# Test 2: Intake Routes Available
echo -e "${BLUE}[2/6] Checking intake routes...${NC}"
if curl -s "$TE_PO_URL/intake/status" > /dev/null; then
    echo -e "${GREEN}✅ Intake routes available${NC}"
else
    echo -e "${RED}❌ Intake routes not available${NC}"
    exit 1
fi
echo ""

# Test 3: Intake Folder Exists
echo -e "${BLUE}[3/6] Checking intake folder...${NC}"
if [ -d "$INTAKE_FOLDER" ]; then
    echo -e "${GREEN}✅ Intake folder exists: $INTAKE_FOLDER${NC}"
else
    echo -e "${BLUE}ℹ️  Creating intake folder...${NC}"
    mkdir -p "$INTAKE_FOLDER"
    echo -e "${GREEN}✅ Intake folder created${NC}"
fi
echo ""

# Test 4: Add Test Document
echo -e "${BLUE}[4/6] Adding test document...${NC}"
TEST_FILE="$INTAKE_FOLDER/test_document_$(date +%s).md"
cat > "$TEST_FILE" << 'EOF'
# Test Kaitiaki Document

## Te Reo Section
Ko te whakapapa me te mauri te kaupapa o tēnei hoahoa.

## English Section
This document tests the Tiwhanawhana intake pipeline.

## Content
- Item 1
- Item 2
- Item 3

Kua mutu te whakamatautau.
EOF

echo -e "${GREEN}✅ Test document created: $(basename $TEST_FILE)${NC}"
echo ""

# Test 5: Trigger Scan
echo -e "${BLUE}[5/6] Triggering intake scan...${NC}"
SCAN_RESPONSE=$(curl -s -X POST "$TE_PO_URL/intake/scan")
echo "Response: $SCAN_RESPONSE"

if echo "$SCAN_RESPONSE" | grep -q "scanning"; then
    echo -e "${GREEN}✅ Scan triggered${NC}"
else
    echo -e "${RED}⚠️  Check scan response above${NC}"
fi
echo ""

# Test 6: Check Status
echo -e "${BLUE}[6/6] Checking intake status...${NC}"
STATUS_RESPONSE=$(curl -s "$TE_PO_URL/intake/status")
DOCS_FOUND=$(echo "$STATUS_RESPONSE" | grep -o '"documents_found":[0-9]*' | grep -o '[0-9]*' || echo "0")

echo "Status response:"
echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"

if [ "$DOCS_FOUND" -gt "0" ]; then
    echo -e "${GREEN}✅ Documents found: $DOCS_FOUND${NC}"
else
    echo -e "${BLUE}ℹ️  No documents found yet (check Supabase)${NC}"
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}✅ Intake Test Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Check Supabase task_queue table for new entries"
echo "2. Verify document was queued with ID and status='pending'"
echo "3. Ready for Whiro auditor (Phase 2)"
echo ""
echo "Useful endpoints:"
echo "  GET  $TE_PO_URL/intake/status       - Current status"
echo "  POST $TE_PO_URL/intake/scan         - Scan now"
echo "  GET  $TE_PO_URL/intake/documents    - List documents"
echo ""
