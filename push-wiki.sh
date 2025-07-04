#!/bin/bash

echo "📤 Pushing wiki changes..."
cd ../claude-hooks.wiki
git add .
git commit -m "Add comprehensive wiki documentation

- Home page with project overview  
- Installation and Getting Started guides
- Complete hooks reference (all 18 hooks)
- Custom hooks creation guide
- Configuration and troubleshooting
- FAQ and Contributing guidelines  
- API reference for developers
- Navigation sidebar and footer"

git push

echo ""
echo "✅ Wiki has been updated!"
echo "🎉 View your wiki at: https://github.com/webdevtodayjason/claude-hooks/wiki"