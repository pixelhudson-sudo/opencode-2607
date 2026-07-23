#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <ticket-id>"
  echo "Example: $0 001"
  exit 1
fi

TICKET_ID="$1"
TICKET_FILE=""
for f in tickets/${TICKET_ID}-*.md; do
  if [ -f "$f" ]; then
    TICKET_FILE="$f"
    break
  fi
done

if [ -z "$TICKET_FILE" ]; then
  echo "ERROR: no ticket found matching tickets/${TICKET_ID}-*.md"
  exit 1
fi

# Extract PR URL from ticket frontmatter
PR_URL=$(grep -E '^pr: "' "$TICKET_FILE" | head -1 | sed 's/^pr: "//;s/"$//')

if [ -z "$PR_URL" ] || [ "$PR_URL" = "" ]; then
  echo "ERROR: ticket ${TICKET_ID} has no PR URL in its frontmatter"
  exit 1
fi

echo "Merging ${PR_URL} for ticket ${TICKET_ID}..."
gh pr merge --squash --delete-branch "$PR_URL"
echo "PR merged."

# Update ticket status to merged
sed -i '' "s/^status: .*/status: merged/" "$TICKET_FILE"
echo "Ticket ${TICKET_ID} status set to merged."
