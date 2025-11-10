#!/bin/bash
#
# ToDoWrite Git Commit Message Hook
# Enforces Conventional Commits format with ToDoWrite-specific scopes
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Read the commit message from file
commit_message_file="$1"
commit_message=$(cat "$commit_message_file")

# Skip validation for merge commits
if echo "$commit_message" | grep -q "^Merge"; then
    echo -e "${GREEN}✓ Merge commit detected, skipping validation${NC}"
    exit 0
fi

# Skip validation for revert commits
if echo "$commit_message" | grep -q "^Revert"; then
    echo -e "${GREEN}✓ Revert commit detected, skipping validation${NC}"
    exit 0
fi

# Conventional Commits pattern
# Format: <type>(<scope>): <description>
# Optional: <type>(<scope>)!: <description> for breaking changes
PATTERN="^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?(!)?: .{1,72}$"

# ToDoWrite-specific scopes
VALID_SCOPES=(
    "goal" "concept" "context" "constraints" "req" "ac" "iface"
    "phase" "step" "task" "subtask" "cmd" "schema" "lint" "trace"
    "docs" "cli" "api" "validation" "build" "test" "tools"
)

# Validate format
if ! echo "$commit_message" | grep -qE "$PATTERN"; then
    echo -e "${RED}✗ COMMIT MESSAGE REJECTED${NC}"
    echo ""
    echo "Your commit message does not follow Conventional Commits format:"
    echo -e "${YELLOW}$commit_message${NC}"
    echo ""
    echo "Required format: <type>(<scope>): <description>"
    echo ""
    echo "Valid types:"
    echo "  feat     - A new feature"
    echo "  fix      - A bug fix"
    echo "  docs     - Documentation only changes"
    echo "  style    - Code style changes (formatting, etc.)"
    echo "  refactor - Code change that neither fixes bug nor adds feature"
    echo "  perf     - Performance improvement"
    echo "  test     - Adding missing tests or correcting existing tests"
    echo "  build    - Changes affecting build system or dependencies"
    echo "  ci       - Changes to CI configuration files and scripts"
    echo "  chore    - Other changes that don't modify src or test files"
    echo "  revert   - Reverts a previous commit"
    echo ""
    echo "ToDoWrite-specific scopes:"
    echo "  Layer scopes: goal, concept, context, constraints, req, ac, iface"
    echo "               phase, step, task, subtask, cmd"
    echo "  System scopes: schema, lint, trace, docs, cli, api, validation"
    echo "                build, test, tools"
    echo ""
    echo "Examples:"
    echo "  feat(goal): add new agricultural automation goal"
    echo "  fix(validation): correct schema validation error handling"
    echo "  docs(api): update REST endpoint documentation"
    echo "  build(schema): generate updated todowrite.schema.json"
    echo "  test(trace): add traceability matrix validation tests"
    echo ""
    exit 1
fi

# Extract scope from commit message if present
scope=""
if echo "$commit_message" | grep -qE "\([a-zA-Z0-9_-]+\)"; then
    scope=$(echo "$commit_message" | sed -n 's/^[^(]*(\([^)]*\)).*$/\1/p')
fi

# Validate scope if present
if [ -n "$scope" ]; then
    valid_scope=false
    for valid in "${VALID_SCOPES[@]}"; do
        if [ "$scope" = "$valid" ]; then
            valid_scope=true
            break
        fi
    done

    if [ "$valid_scope" = false ]; then
        echo -e "${YELLOW}⚠ WARNING: Unrecognized scope '$scope'${NC}"
        echo "Valid ToDoWrite scopes are:"
        printf "  %s\n" "${VALID_SCOPES[@]}"
        echo ""
        echo "Consider using a recognized scope for better categorization."
        echo "Continuing with commit (scope validation is advisory only)..."
    fi
fi

# Check for work-type tags in commit body (optional)
commit_body=$(tail -n +2 "$commit_message_file" | tr -d '\n' | tr -d ' ')
if echo "$commit_body" | grep -q "work:"; then
    echo -e "${GREEN}✓ Work-type tag detected in commit body${NC}"
fi

# Validate description length
first_line=$(echo "$commit_message" | head -n 1)
description=$(echo "$first_line" | sed 's/^[^:]*: //')
if [ ${#description} -gt 72 ]; then
    echo -e "${YELLOW}⚠ WARNING: Description is ${#description} characters (max recommended: 72)${NC}"
    echo "Consider shortening the description for better readability."
fi

# All validations passed
echo -e "${GREEN}✓ Commit message format is valid${NC}"
exit 0
