#!/bin/bash

echo "🚀 Starting deployment with cache clearing..."
echo "Version: 2025-01-24-1259-aggressive-nocache"
echo ""

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Make sure you're in the project root directory."
    exit 1
fi

echo "📝 Changes implemented:"
echo "- Added aggressive no-cache headers (max-age=0, s-maxage=0, proxy-revalidate)"
echo "- Added version timestamps to all static resources"
echo "- Added console logging to verify version"
echo "- Updated Vercel configuration with Surrogate-Control headers"
echo ""

echo "⚡ Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps to clear cache:"
echo "1. Go to your Vercel dashboard"
echo "2. Navigate to your project settings"
echo "3. Force a redeploy with 'Use existing Build Cache: No'"
echo "4. Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo ""
echo "🔍 To verify deployment:"
echo "1. Open browser console (F12)"
echo "2. You should see:"
echo "   - Script version: 2025-01-24-1259-aggressive-nocache"
echo "   - Page loaded at: [timestamp]"
echo "   - Domain: [your-domain]"
