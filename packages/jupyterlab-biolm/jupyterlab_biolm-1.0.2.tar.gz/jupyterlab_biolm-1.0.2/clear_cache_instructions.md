# Clear Browser Cache Instructions

The browser is still using cached JavaScript. To fix:

## Option 1: Hard Refresh (Recommended)
- **Mac**: Press `Cmd + Shift + R` or `Cmd + Option + R`
- **Windows/Linux**: Press `Ctrl + Shift + R` or `Ctrl + F5`

## Option 2: Clear Cache Manually
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## Option 3: Clear All Site Data
1. Open DevTools (F12)
2. Go to Application tab
3. Click "Clear site data"
4. Refresh the page

## Verify New Endpoint
After refreshing, check the console - you should see requests to:
`https://biolm.ai/api/ui/community-api-models/`

NOT the old:
`https://api.biolm.ai/models`
