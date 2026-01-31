# Canvas Skill

Control the Canvas display on paired nodes (iOS, Android, macOS). Show web content, run JS, capture screenshots, and display real-time UI.

## Requirements

- **Paired node required** — canvas only works with connected nodes
- **Node must be foregrounded** — background calls return `NODE_BACKGROUND_UNAVAILABLE`
- Check node availability: `nodes action=status`

## Core Actions

### Present Content

Display a URL or inline HTML on the node's canvas:

```
canvas action=present url="https://example.com"
canvas action=present url="data:text/html,<html>...</html>"
```

**Parameters:**
- `url` — URL or data URI to display
- `width`, `height` — canvas dimensions (optional)
- `x`, `y` — position offset (optional)
- `node` — target node ID/name (required if multiple nodes)

### Navigate

Change the current canvas URL:

```
canvas action=navigate url="https://new-url.com"
```

### Hide Canvas

```
canvas action=hide
```

### Evaluate JavaScript

Run JS in the canvas context and get results:

```
canvas action=eval javaScript="document.title"
canvas action=eval javaScript="document.querySelector('h1').textContent"
```

**Use cases:**
- Extract data from displayed page
- Modify DOM dynamically
- Trigger interactions

### Capture Screenshot

Get a snapshot of the current canvas:

```
canvas action=snapshot outputFormat=png
canvas action=snapshot outputFormat=jpg quality=0.9 maxWidth=1200
```

**Parameters:**
- `outputFormat` — `png`, `jpg`, or `jpeg`
- `quality` — 0-1 for JPEG compression (default: 0.9)
- `maxWidth` — resize if wider (optional)

Returns: Image attachment (MEDIA path)

## A2UI (Real-time UI)

Push structured content to the canvas in real-time:

### Push Content

```
canvas action=a2ui_push jsonl='{"type":"text","content":"Hello world"}'
```

Or from a file:
```
canvas action=a2ui_push jsonlPath="./content.jsonl"
```

### Reset A2UI

Clear all A2UI content:

```
canvas action=a2ui_reset
```

**Note:** Only A2UI v0.8 JSONL format is supported.

## Interactive Content Examples

### Display a Dashboard

```javascript
// Present a live dashboard
canvas action=present url="data:text/html,
<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <style>
    body { font-family: system-ui; background: #1a1a2e; color: white; padding: 20px; }
    .metric { font-size: 48px; font-weight: bold; }
    .label { font-size: 14px; color: #888; }
  </style>
</head>
<body>
  <div class='label'>Current Time</div>
  <div class='metric' id='time'></div>
  <script>
    setInterval(() => {
      document.getElementById('time').textContent = new Date().toLocaleTimeString();
    }, 1000);
  </script>
</body>
</html>"
```

### Display an Image

```
canvas action=present url="https://example.com/image.jpg"
```

Or with inline base64:
```
canvas action=present url="data:image/png;base64,..."
```

### Interactive Chart

Present a chart library (e.g., Chart.js, D3) with live data:

```javascript
canvas action=present url="data:text/html,
<html>
<head>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
</head>
<body style='background:#111;padding:20px'>
  <canvas id='chart'></canvas>
  <script>
    new Chart(document.getElementById('chart'), {
      type: 'line',
      data: {
        labels: ['Mon','Tue','Wed','Thu','Fri'],
        datasets: [{
          label: 'Value',
          data: [12, 19, 3, 5, 2],
          borderColor: '#4CAF50'
        }]
      }
    });
  </script>
</body>
</html>"
```

## Video Display

Canvas can display video content via HTML5 video elements:

### Embed a Video

```
canvas action=present url="data:text/html,
<html>
<body style='margin:0;background:black'>
  <video autoplay controls style='width:100%;height:100vh;object-fit:contain'>
    <source src='https://example.com/video.mp4' type='video/mp4'>
  </video>
</body>
</html>"
```

### YouTube Embed

```
canvas action=present url="data:text/html,
<html>
<body style='margin:0'>
  <iframe 
    width='100%' 
    height='100%' 
    style='position:fixed;top:0;left:0;border:0'
    src='https://www.youtube.com/embed/VIDEO_ID?autoplay=1'
    allow='autoplay;encrypted-media'
    allowfullscreen>
  </iframe>
</body>
</html>"
```

### Video with Controls via JS

```javascript
// Present video then control via eval
canvas action=present url="data:text/html,<video id='v' src='...' style='width:100%'></video>"

// Play/pause
canvas action=eval javaScript="document.getElementById('v').play()"
canvas action=eval javaScript="document.getElementById('v').pause()"

// Seek
canvas action=eval javaScript="document.getElementById('v').currentTime = 30"

// Get duration/position
canvas action=eval javaScript="document.getElementById('v').duration"
```

## Workflow Patterns

### 1. Display → Interact → Capture

```
1. canvas action=present url="..."
2. canvas action=eval javaScript="..."  // modify/interact
3. canvas action=snapshot  // capture result
```

### 2. Live Updates

```
1. canvas action=present url="data:text/html,..."  // with update placeholder
2. canvas action=eval javaScript="document.getElementById('data').textContent = 'new value'"
```

### 3. Web Scraping with Visual

```
1. canvas action=present url="https://target-site.com"
2. canvas action=snapshot  // see what loaded
3. canvas action=eval javaScript="..." // extract data
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `node required` | No node specified | Check `nodes action=status`, specify node |
| `NODE_BACKGROUND_UNAVAILABLE` | Node app is backgrounded | User must foreground the app |
| Timeout | Page load too slow | Use `timeoutMs` parameter |

## Tips

1. **Data URIs for quick content** — Inline HTML is fast, no network needed
2. **Use snapshot after present** — Verify content loaded correctly
3. **JS eval for extraction** — Cheaper than full browser automation
4. **A2UI for streaming** — Push incremental updates without full reloads
5. **Responsive design** — Use viewport-relative units (vh, vw, %)
