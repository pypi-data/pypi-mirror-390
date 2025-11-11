#!/bin/bash
# ============================================================================
# VALIDATE HOPX AGENT OPENAPI SPEC
# ============================================================================
#
# This script validates the OpenAPI specification for the HOPX Agent.
#
# Requirements:
#   - Node.js (for npx)
#   - @redocly/cli (installed automatically via npx)
#
# Usage:
#   ./scripts/validate-openapi.sh
#
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OPENAPI_FILE="${PROJECT_ROOT}/vm-agent/openapi.yaml"

echo "════════════════════════════════════════════════════════════════"
echo "  🔍 HOPX AGENT - OPENAPI SPEC VALIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if OpenAPI file exists
if [[ ! -f "${OPENAPI_FILE}" ]]; then
    echo "❌ ERROR: OpenAPI spec not found!"
    echo "   Expected: ${OPENAPI_FILE}"
    exit 1
fi

echo "📄 OpenAPI File: ${OPENAPI_FILE}"
echo ""

# ============================================================================
# VALIDATION 1: Redocly Lint
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  1️⃣  Redocly Lint (OpenAPI 3.0 Validation)"
echo "════════════════════════════════════════════════════════════════"
echo ""

if command -v npx &> /dev/null; then
    echo "Running: npx @redocly/cli lint openapi.yaml"
    echo ""
    
    cd "${PROJECT_ROOT}/vm-agent"
    
    if npx @redocly/cli lint openapi.yaml; then
        echo ""
        echo "✅ Redocly validation PASSED!"
    else
        echo ""
        echo "❌ Redocly validation FAILED!"
        echo "   Fix errors above and try again."
        exit 1
    fi
else
    echo "⚠️  npx not found - skipping Redocly lint"
    echo "   Install Node.js to enable validation"
fi

echo ""

# ============================================================================
# VALIDATION 2: Basic YAML Syntax
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  2️⃣  YAML Syntax Validation"
echo "════════════════════════════════════════════════════════════════"
echo ""

if command -v python3 &> /dev/null; then
    echo "Validating YAML syntax..."
    
    if python3 -c "
import yaml
import sys

try:
    with open('${OPENAPI_FILE}', 'r') as f:
        spec = yaml.safe_load(f)
    
    # Check required fields
    if 'openapi' not in spec:
        print('❌ Missing required field: openapi')
        sys.exit(1)
    
    if 'info' not in spec:
        print('❌ Missing required field: info')
        sys.exit(1)
    
    if 'paths' not in spec:
        print('❌ Missing required field: paths')
        sys.exit(1)
    
    print(f'✅ Valid YAML with {len(spec.get(\"paths\", {}))} endpoints')
    print(f'   OpenAPI Version: {spec.get(\"openapi\")}')
    print(f'   API Version: {spec.get(\"info\", {}).get(\"version\")}')
    print(f'   Title: {spec.get(\"info\", {}).get(\"title\")}')
    
except yaml.YAMLError as e:
    print(f'❌ YAML Syntax Error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Validation Error: {e}')
    sys.exit(1)
"; then
        echo ""
    else
        echo "❌ YAML validation failed!"
        exit 1
    fi
else
    echo "⚠️  Python3 not found - skipping YAML validation"
fi

echo ""

# ============================================================================
# VALIDATION 3: Coverage Check
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  3️⃣  API Coverage Check"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Checking endpoint coverage..."
echo ""

# Count endpoints in OpenAPI spec
SPEC_ENDPOINTS=$(grep -E "^  /[a-z]" "${OPENAPI_FILE}" | wc -l)

echo "📊 Documented Endpoints: ${SPEC_ENDPOINTS}"
echo ""

# Expected major endpoints
EXPECTED_ENDPOINTS=(
    "/ping"
    "/health"
    "/info"
    "/system"
    "/execute"
    "/execute/rich"
    "/execute/background"
    "/execute/processes"
    "/execute/kill"
    "/commands/run"
    "/commands/background"
    "/files/read"
    "/files/write"
    "/files/upload"
    "/files/download"
    "/files/list"
    "/files/exists"
    "/files/remove"
    "/files/mkdir"
    "/processes"
    "/metrics"
    "/metrics/prometheus"
    "/metrics/snapshot"
    "/cache/stats"
    "/cache/clear"
    "/terminal"
    "/stream"
    "/execute/stream"
    "/commands/stream"
    "/files/watch"
)

MISSING_COUNT=0

for endpoint in "${EXPECTED_ENDPOINTS[@]}"; do
    if grep -q "^  ${endpoint}:" "${OPENAPI_FILE}"; then
        echo "  ✅ ${endpoint}"
    else
        echo "  ❌ ${endpoint} (MISSING!)"
        ((MISSING_COUNT++))
    fi
done

echo ""

if [[ ${MISSING_COUNT} -eq 0 ]]; then
    echo "✅ All expected endpoints documented!"
else
    echo "⚠️  ${MISSING_COUNT} endpoints missing from spec!"
fi

echo ""

# ============================================================================
# VALIDATION 4: Error Codes Check
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  4️⃣  Error Codes Coverage"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Checking error code documentation..."
echo ""

# Expected error codes (from main.go)
ERROR_CODES=(
    "METHOD_NOT_ALLOWED"
    "INVALID_JSON"
    "MISSING_PARAMETER"
    "PATH_NOT_ALLOWED"
    "FILE_NOT_FOUND"
    "PERMISSION_DENIED"
    "COMMAND_FAILED"
    "EXECUTION_TIMEOUT"
    "EXECUTION_FAILED"
    "INTERNAL_ERROR"
    "INVALID_PATH"
    "FILE_ALREADY_EXISTS"
    "DIRECTORY_NOT_FOUND"
    "INVALID_REQUEST"
    "PROCESS_NOT_FOUND"
    "DESKTOP_NOT_AVAILABLE"
)

ERROR_MISSING=0

for code in "${ERROR_CODES[@]}"; do
    if grep -q "${code}" "${OPENAPI_FILE}"; then
        echo "  ✅ ${code}"
    else
        echo "  ❌ ${code} (MISSING!)"
        ((ERROR_MISSING++))
    fi
done

echo ""

if [[ ${ERROR_MISSING} -eq 0 ]]; then
    echo "✅ All error codes documented!"
else
    echo "⚠️  ${ERROR_MISSING} error codes missing from spec!"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  📊 VALIDATION SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

TOTAL_CHECKS=4
PASSED_CHECKS=0

# Check 1: Redocly
if command -v npx &> /dev/null; then
    ((PASSED_CHECKS++))
    echo "✅ Redocly Lint: PASSED"
else
    echo "⏭️  Redocly Lint: SKIPPED (npx not found)"
fi

# Check 2: YAML Syntax
if command -v python3 &> /dev/null; then
    ((PASSED_CHECKS++))
    echo "✅ YAML Syntax: PASSED"
else
    echo "⏭️  YAML Syntax: SKIPPED (python3 not found)"
fi

# Check 3: Coverage
if [[ ${MISSING_COUNT} -eq 0 ]]; then
    ((PASSED_CHECKS++))
    echo "✅ API Coverage: COMPLETE (${SPEC_ENDPOINTS} endpoints)"
else
    echo "⚠️  API Coverage: ${MISSING_COUNT} endpoints missing"
fi

# Check 4: Error Codes
if [[ ${ERROR_MISSING} -eq 0 ]]; then
    ((PASSED_CHECKS++))
    echo "✅ Error Codes: COMPLETE (16 codes)"
else
    echo "⚠️  Error Codes: ${ERROR_MISSING} codes missing"
fi

echo ""
echo "Score: ${PASSED_CHECKS}/${TOTAL_CHECKS} checks passed"
echo ""

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  💡 NEXT STEPS"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1. View interactive docs:"
echo "   npx @redocly/cli preview-docs vm-agent/openapi.yaml"
echo ""

echo "2. Generate Python SDK:"
echo "   npx @openapitools/openapi-generator-cli generate \\"
echo "     -i vm-agent/openapi.yaml \\"
echo "     -g python \\"
echo "     -o sdk/python"
echo ""

echo "3. Test against live agent:"
echo "   npx dredd vm-agent/openapi.yaml https://vm.hopx.dev"
echo ""

echo "4. Setup CI/CD validation:"
echo "   Add this script to .github/workflows/openapi.yml"
echo ""

echo "════════════════════════════════════════════════════════════════"

if [[ ${PASSED_CHECKS} -eq ${TOTAL_CHECKS} ]]; then
    echo "🎉 ALL VALIDATIONS PASSED! OpenAPI spec is production-ready!"
    echo "════════════════════════════════════════════════════════════════"
    exit 0
else
    echo "⚠️  Some validations failed or were skipped."
    echo "════════════════════════════════════════════════════════════════"
    exit 1
fi

