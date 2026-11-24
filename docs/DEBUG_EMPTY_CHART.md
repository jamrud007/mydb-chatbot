# 🔍 Debug Chart Kosong - Tanpa API Call

## Problem
Chart canvas kosong meskipun data sudah diterima dari server

## Possible Causes

### 1. Chart.js Console Error
**Action**: Buka browser → F12 → Console tab
**Look for**: Red error messages

Common errors:
- "Cannot read property 'x' of undefined"
- "Invalid chart type"
- "scales is not defined for pie chart"

---

### 2. Data Format Issue

Cek di Console → Network tab → klik request "execute/0" → Response tab

**Expected format**:
```json
{
  "visualization": {
    "can_visualize": true,
    "chart_type": "bar",
    "chart_data": {
      "type": "bar",
      "indexAxis": "y",
      "labels": ["city1", "city2", ...],
      "datasets": [{
        "label": "customer_count",
        "data": [1, 1, 1, ...],
        "backgroundColor": "rgba(...)"
      }]
    }
  }
}
```

**Check**:
- ✓ `indexAxis: "y"` ada?
- ✓ `datasets[0].data` ada values?
- ✓ `labels` array filled?

---

### 3. Quick Fix Attempt

Jika semua data OK tapi chart masih kosong, coba paksa vertical bar dulu:

**In browser console, paste this**:
```javascript
// Test render simple bar chart
const testCanvas = document.querySelector('canvas');
if (testCanvas) {
    const testCtx = testCanvas.getContext('2d');
    new Chart(testCtx, {
        type: 'bar',
        data: {
            labels: ['A', 'B', 'C'],
            datasets: [{
                label: 'Test',
                data: [1, 2, 3],
                backgroundColor: 'rgba(99, 102, 241, 0.8)'
            }]
        },
        options: {
            indexAxis: 'y'
        }
    });
}
```

If this works → data passing issue
If this fails → Chart.js installation issue

---

## Steps to Debug (NO API CALLS):

1. **Browser Console** (F12)
   - Check for red errors
   - Screenshot errors if any

2. **Network Tab**
   - Find request "execute/0"
   - Click → Response
   - Screenshot the `visualization` part

3. **Try Manual Chart**
   - Paste test code above in console
   - Does it render?

---

## Temporary Workaround

Change line in `visualization_helper.py`:

```python
# Line 150-155, change:
if len(results) > 8 or cls._has_long_labels(results, label_col):
    return cls._create_horizontal_bar_config(...)

# TO:
if False:  # Temporarily disable horizontal bar
    return cls._create_horizontal_bar_config(...)
```

This will force regular vertical bar chart (which we know works).

---

**Next Steps (for user)**:
1. F12 → Console → screenshot any errors
2. F12 → Network → find "execute/0" → Response → screenshot
3. Send screenshots (no new API calls needed!)

Then I can fix the exact issue.
