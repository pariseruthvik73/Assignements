#!/bin/bash

# ─────────────────────────────────────────
#  check_permissions.sh - File Permission Checker
# ─────────────────────────────────────────

# ── Colors ──────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Helper: print section header ─────────
section() {
    echo -e "\n${CYAN}${BOLD}── $1 ──${RESET}"
}

# ── 1. Validate argument count ───────────
if [ $# -ne 2 ]; then
    echo -e "${RED}❌ Usage: $0 <file/directory> <expected_permissions>${RESET}"
    echo -e "   Example: $0 app/api.php 644"
    echo -e "   Example: $0 app 755"
    exit 3
fi

TARGET="$1"
EXPECTED="$2"
CURRENT_USER=$(whoami)

# ── 2. Validate permission format ────────
if ! [[ "$EXPECTED" =~ ^[0-7]{3,4}$ ]]; then
    echo -e "${RED}❌ Invalid permission format: '$EXPECTED'${RESET}"
    echo -e "   Use octal format like 644, 755, 700"
    exit 3
fi

# ── 3. Check if file/directory exists ────
section "Checking: $TARGET"

if [ ! -e "$TARGET" ]; then
    echo -e "${RED}❌ '$TARGET' does not exist${RESET}"
    exit 2
fi

# ── 4. File type ─────────────────────────
if [ -d "$TARGET" ]; then
    TYPE="Directory"
elif [ -f "$TARGET" ]; then
    TYPE="File"
else
    TYPE="Special file"
fi
echo -e "   📁 Type       : ${BOLD}$TYPE${RESET}"

# ── 5. Get actual permissions ─────────────
ACTUAL=$(stat -c %a "$TARGET")
OWNER=$(stat -c %U "$TARGET")

echo -e "   🔑 Permissions: ${BOLD}$ACTUAL${RESET} (expected: $EXPECTED)"
echo -e "   👤 Owner      : ${BOLD}$OWNER${RESET} (current user: $CURRENT_USER)"

# ── 6. Permission match check ─────────────
section "Permission Check"
EXIT_CODE=0

if [ "$ACTUAL" == "$EXPECTED" ]; then
    echo -e "${GREEN}✅ $TARGET has correct permissions ($ACTUAL)${RESET}"
else
    echo -e "${RED}❌ $TARGET has permissions $ACTUAL (expected $EXPECTED)${RESET}"
    EXIT_CODE=1
fi

# ── 7. Ownership check ────────────────────
section "Ownership Check"

if [ "$OWNER" == "$CURRENT_USER" ]; then
    echo -e "${GREEN}✅ File ownership is secure (owned by $CURRENT_USER)${RESET}"
else
    echo -e "${RED}❌ File owned by '$OWNER', not current user '$CURRENT_USER'${RESET}"
    EXIT_CODE=1
fi

# ── 8. Security checks ────────────────────
section "Security Analysis"

# World-writable check (last digit has write bit = 2 or 3 or 6 or 7)
LAST_DIGIT="${ACTUAL: -1}"
if [[ "$LAST_DIGIT" == "2" || "$LAST_DIGIT" == "3" || \
      "$LAST_DIGIT" == "6" || "$LAST_DIGIT" == "7" ]]; then
    echo -e "${YELLOW}⚠️  WARNING: '$TARGET' is world-writable! (permissions: $ACTUAL)${RESET}"
    EXIT_CODE=1
else
    echo -e "${GREEN}✅ Not world-writable${RESET}"
fi

# World-executable check for regular files
if [ -f "$TARGET" ]; then
    if [[ "$LAST_DIGIT" == "1" || "$LAST_DIGIT" == "3" || \
          "$LAST_DIGIT" == "5" || "$LAST_DIGIT" == "7" ]]; then
        echo -e "${YELLOW}⚠️  WARNING: '$TARGET' is world-executable!${RESET}"
    else
        echo -e "${GREEN}✅ Not world-executable${RESET}"
    fi
fi

# SUID/SGID check
FULL_PERM=$(stat -c %a "$TARGET")
if [ ${#FULL_PERM} -eq 4 ]; then
    SPECIAL="${FULL_PERM:0:1}"
    if [[ "$SPECIAL" == "4" || "$SPECIAL" == "6" || "$SPECIAL" == "7" ]]; then
        echo -e "${YELLOW}⚠️  WARNING: SUID/SGID bit is set! (permissions: $FULL_PERM)${RESET}"
        EXIT_CODE=1
    fi
else
    echo -e "${GREEN}✅ No SUID/SGID bits set${RESET}"
fi

# ── 9. Permissions breakdown via ls -l ────
section "Detailed Info (ls -l)"
ls -lah "$TARGET"

# ── 10. Final result ──────────────────────
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ All checks passed for '$TARGET'${RESET}"
else
    echo -e "${RED}${BOLD}❌ One or more checks failed for '$TARGET'${RESET}"
fi

echo -e "${BOLD}Exit code: $EXIT_CODE${RESET}\n"
exit $EXIT_CODE