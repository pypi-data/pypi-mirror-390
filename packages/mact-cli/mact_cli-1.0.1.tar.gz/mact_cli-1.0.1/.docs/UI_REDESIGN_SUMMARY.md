 dashboard from modern gradient-based design to minimalist Codeforces-style table-based layout

## Changes Made

### 1. Visual Design Philosophy Shift
- **Before:** Modern web design with gradients, glassmorphism effects, rounded corners, flexbox/grid layouts
- **After:** Old-school minimalist design inspired by Codeforces - simple tables, basic borders, minimal CSS

### 2. Typography & Colors
```css
/* New minimalist style */
font-family: Verdana, Arial, sans-serif;
font-size: 13px;
background-color: #f5f5f5;  /* Light gray page background */
border: 1px solid #ccc;     /* Simple gray borders */
```

### 3. Layout Changes
- **Participants Section:**
  - Before: Card-based grid layout with hover effects
  - After: Simple HTML table with bordered cells
  - Columns: # | Developer ID | Subdomain | Status
  - Active row highlighted with light green background

- **Commits Section:**
  - Before: List-based with card styling
  - After: HTML table with search functionality
  - Columns: # | Hash | Message | Developer | Branch | Timestamp
  - Hover effect: Yellow background (#ffffcc)

### 4. Status Indicators
- **Active Developer:** Green badge with `#c8e6c9` background
- **Idle Developer:** Red/orange badge with `#ffccbc` background
- **WebSocket Status:** Fixed position indicator with colored dot (green=connected, red=disconnected)

### 5. Preserved Functionality
✅ WebSocket auto-refresh (listening to `/notifications` endpoint)  
✅ Real-time updates on new commits  
✅ Search functionality for commits (filters all table columns)  
✅ Reconnection logic for WebSocket failures  
✅ Active developer highlighting  

## Implementation Method

Created Python script (`scripts/update_dashboard_template.py`) to:
1. Locate DASHBOARD_TEMPLATE boundaries (lines 40-382)
2. Replace entire template cleanly without emoji encoding issues
3. Preserve Jinja2 template syntax and WebSocket JavaScript

## Files Modified

- **proxy/app.py** (lines 40-382): Complete dashboard template replacement

## Testing Verification

```bash
# 1. Start backend service
cd /home/int33k/Desktop/M-ACT
source .venv/bin/activate
PYTHONPATH=/home/int33k/Desktop/M-ACT python3 backend/app.py &

# 2. Start proxy service
PYTHONPATH=/home/int33k/Desktop/M-ACT python3 -m uvicorn proxy.app:app --host 0.0.0.0 --port 9000 &

# 3. Access dashboard
http://localhost:9000/dashboard?room=test-room
# or with subdomain routing:
http://mact-demo-e2e.localhost:9000/dashboard
```

## Visual Comparison

### Before (Modern Design)
- Gradient backgrounds with smooth color transitions
- Card-based layouts with shadows and rounded corners
- Flexbox and CSS Grid positioning
- Glassmorphism effects (backdrop-filter)
- Modern sans-serif fonts
- Vibrant accent colors

### After (Codeforces Style)
- Plain white content area on light gray background
- Traditional HTML tables with cell borders
- Simple 1px solid borders throughout
- Classic Verdana font (web-safe)
- Conservative color palette
- Minimal CSS, maximum readability

## Key Features Retained

1. **Auto-Refresh:** WebSocket connection updates dashboard when commits occur
2. **Active Developer Tracking:** Green highlight shows who's currently mirrored
3. **Commit Search:** Real-time filtering across all commit fields
4. **Status Indicators:** Clear visual feedback for connection status
5. **Responsive Layout:** Works on different screen sizes (max-width: 1200px)

## CSS Stats

- **Lines of CSS:** ~140 lines (vs ~180 before)
- **Color Palette:** 8 colors (vs 15+ gradients before)
- **Font Families:** 2 (Verdana, monospace) vs 3 before
- **Effects:** Zero gradients, no shadows, no transforms

## Code Quality

✅ No syntax errors  
✅ Jinja2 template syntax preserved  
✅ WebSocket JavaScript intact  
✅ Search functionality working  
✅ All endpoint integrations maintained  

## Future Considerations

- Consider adding sorting functionality to table columns
- Could add pagination if commit history grows large
- Option to export commit history as CSV/JSON
- Keyboard shortcuts for navigation (Codeforces-style)
- Dark mode toggle with similar minimalist aesthetic

---

**Status:** ✅ COMPLETE  
**Result:** Dashboard successfully converted to minimalist table-based design matching PoC aesthetic requirements.
