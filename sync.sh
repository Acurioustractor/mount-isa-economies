#!/bin/bash
# Simple sync script - run this instead of manual git pull
# Handles unstaged changes automatically

echo "🔄 Syncing repository..."

# Check if there are any changes
if ! git diff-index --quiet HEAD --; then
    echo "📦 Stashing local changes..."
    git stash push -m "Auto-stash before sync $(date +%Y-%m-%d_%H:%M:%S)"
    STASHED=true
else
    STASHED=false
fi

# Pull latest changes
echo "⬇️  Pulling latest changes..."
git pull --rebase

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    echo "📤 Restoring your local changes..."
    if git stash pop; then
        echo "✅ Local changes restored successfully"
    else
        echo "⚠️  Conflict when restoring changes. Your changes are in the stash."
        echo "   Run 'git stash list' to see them"
        echo "   Run 'git stash pop' to try again after resolving conflicts"
    fi
fi

echo "✅ Sync complete!"
