

# 🖥️ Desktop Automation - Python SDK

**Complete GUI automation for Bunnyshell Sandboxes**

Control GUI applications, automate browser testing, capture screenshots, record videos, and more!

---

## 🎯 Quick Start

```python
from bunnyshell import Sandbox, DesktopNotAvailableError

# Create sandbox with desktop template
sandbox = Sandbox.create(template="desktop")

# Start VNC for remote access
vnc_info = sandbox.desktop.start_vnc()
print(f"VNC at: {vnc_info.url}")

# Automate GUI interactions
sandbox.desktop.click(100, 100)
sandbox.desktop.type("Hello, Desktop!")

# Capture screenshot
img = sandbox.desktop.screenshot()
with open('screenshot.png', 'wb') as f:
    f.write(img)
```

---

## 📋 Features

### ✅ Implemented

- **VNC Server** - Remote desktop access
- **Mouse Control** - Click, move, drag, scroll
- **Keyboard Control** - Type text, press keys, key combinations
- **Clipboard** - Set/get clipboard content, history
- **Screenshot** - Full screen or region capture
- **Screen Recording** - Record desktop activity as MP4
- **Window Management** - List, focus, resize, close windows
- **Display Control** - Get/set screen resolution

### 🔒 Requirements

Desktop automation requires specific dependencies in your sandbox template:

```dockerfile
RUN apt-get update && apt-get install -y \
    xvfb \
    tigervnc-standalone-server \
    xdotool \
    wmctrl \
    xclip \
    imagemagick \
    ffmpeg \
    tesseract-ocr
```

---

## 🚀 API Reference

### VNC Server

Start VNC server for remote desktop access:

```python
# Start VNC
vnc_info = sandbox.desktop.start_vnc(display=1)
print(f"Connect to: {vnc_info.url}")
print(f"Display: {vnc_info.display}")
print(f"Port: {vnc_info.port}")

# Check status
status = sandbox.desktop.get_vnc_status()
if status.running:
    print(f"VNC running at {status.url}")

# Stop VNC
sandbox.desktop.stop_vnc()
```

---

### Mouse Control

Automate mouse interactions:

```python
# Click at position
sandbox.desktop.click(100, 100)

# Right click
sandbox.desktop.click(200, 200, button="right")

# Double click
sandbox.desktop.click(150, 150, clicks=2)

# Move cursor
sandbox.desktop.move(300, 400)

# Drag and drop
sandbox.desktop.drag(from_x=100, from_y=100, to_x=300, to_y=300)

# Scroll
sandbox.desktop.scroll(amount=5, direction="down")
sandbox.desktop.scroll(amount=3, direction="up")
```

**Parameters**:
- `button`: `"left"`, `"right"`, `"middle"`
- `direction`: `"up"`, `"down"`, `"left"`, `"right"`

---

### Keyboard Control

Automate keyboard input:

```python
# Type text
sandbox.desktop.type("Hello, World!")

# Type with delay
sandbox.desktop.type("Slow typing", delay_ms=50)

# Press single key
sandbox.desktop.press("Return")
sandbox.desktop.press("Escape")
sandbox.desktop.press("Tab")
sandbox.desktop.press("F1")

# Key combinations
sandbox.desktop.combination(['ctrl'], 'c')  # Ctrl+C
sandbox.desktop.combination(['ctrl', 'shift'], 't')  # Ctrl+Shift+T
sandbox.desktop.combination(['alt'], 'F4')  # Alt+F4
```

**Common keys**:
- `Return`, `Escape`, `Tab`, `Space`
- `BackSpace`, `Delete`
- `Home`, `End`, `Page_Up`, `Page_Down`
- `Up`, `Down`, `Left`, `Right`
- `F1` through `F12`

**Modifiers**:
- `ctrl`, `shift`, `alt`, `super` (Windows/Command key)

---

### Clipboard Operations

Manage clipboard content:

```python
# Set clipboard
sandbox.desktop.set_clipboard("Hello from clipboard!")

# Get clipboard
text = sandbox.desktop.get_clipboard()
print(text)

# Get clipboard history
history = sandbox.desktop.get_clipboard_history()
for item in history:
    print(item)
```

---

### Screenshot Capture

Capture screen or regions:

```python
# Full screen screenshot
img_bytes = sandbox.desktop.screenshot()
with open('fullscreen.png', 'wb') as f:
    f.write(img_bytes)

# Region screenshot
region_bytes = sandbox.desktop.screenshot_region(
    x=100,
    y=100,
    width=500,
    height=300
)
with open('region.png', 'wb') as f:
    f.write(region_bytes)
```

---

### Screen Recording

Record desktop activity:

```python
# Start recording
rec = sandbox.desktop.start_recording(
    fps=30,
    format="mp4",
    quality="high"  # "low", "medium", "high"
)
print(f"Recording ID: {rec.recording_id}")

# ... do stuff ...

# Stop recording
final_rec = sandbox.desktop.stop_recording(rec.recording_id)
print(f"Duration: {final_rec.duration}s")
print(f"Size: {final_rec.file_size} bytes")

# Check status
status = sandbox.desktop.get_recording_status(rec.recording_id)
if status.is_ready:
    # Download video
    video_bytes = sandbox.desktop.download_recording(rec.recording_id)
    with open('recording.mp4', 'wb') as f:
        f.write(video_bytes)
```

**Recording options**:
- `fps`: Frames per second (default: 10, recommended: 30 for smooth video)
- `format`: `"mp4"` or `"webm"`
- `quality`: `"low"`, `"medium"`, `"high"`

---

### Window Management

List and manage windows:

```python
# Get all windows
windows = sandbox.desktop.get_windows()
for win in windows:
    print(f"{win.title}: {win.width}x{win.height} at ({win.x}, {win.y})")
    print(f"  ID: {win.id}")
    print(f"  PID: {win.pid}")

# Focus window
if windows:
    sandbox.desktop.focus_window(windows[0].id)

# Resize window
sandbox.desktop.resize_window(windows[0].id, width=800, height=600)

# Close window
sandbox.desktop.close_window(windows[0].id)
```

---

### Display Configuration

Manage screen resolution:

```python
# Get current resolution
display = sandbox.desktop.get_display()
print(f"Current: {display.resolution}")  # e.g., "1920x1080"
print(f"Size: {display.width}x{display.height}")
print(f"Depth: {display.depth}")

# Get available resolutions
resolutions = sandbox.desktop.get_available_resolutions()
for width, height in resolutions:
    print(f"{width}x{height}")

# Set resolution
new_display = sandbox.desktop.set_resolution(1920, 1080)
print(f"New resolution: {new_display.resolution}")
```

---

## 🎨 Complete Workflow Example

```python
from bunnyshell import Sandbox
import time

# Create desktop sandbox
sandbox = Sandbox.create(template="desktop")

try:
    # 1. Start VNC
    vnc = sandbox.desktop.start_vnc()
    print(f"VNC: {vnc.url}")
    
    # 2. Set resolution
    sandbox.desktop.set_resolution(1920, 1080)
    
    # 3. Open Firefox
    sandbox.commands.run('firefox &', background=True)
    time.sleep(3)
    
    # 4. Find Firefox window
    windows = sandbox.desktop.get_windows()
    firefox = next((w for w in windows if 'Firefox' in w.title), None)
    
    if firefox:
        # 5. Focus Firefox
        sandbox.desktop.focus_window(firefox.id)
        
        # 6. Start recording
        rec = sandbox.desktop.start_recording(fps=30, quality="high")
        
        # 7. Navigate to URL
        sandbox.desktop.combination(['ctrl'], 'l')  # Address bar
        sandbox.desktop.type("https://bunnyshell.com")
        sandbox.desktop.press("Return")
        time.sleep(2)
        
        # 8. Take screenshot
        img = sandbox.desktop.screenshot()
        with open('firefox.png', 'wb') as f:
            f.write(img)
        
        # 9. Stop recording
        final_rec = sandbox.desktop.stop_recording(rec.recording_id)
        
        # 10. Download video
        if final_rec.is_ready:
            video = sandbox.desktop.download_recording(rec.recording_id)
            with open('demo.mp4', 'wb') as f:
                f.write(video)
    
    # 11. Stop VNC
    sandbox.desktop.stop_vnc()

finally:
    sandbox.kill()
```

---

## ❌ Error Handling

### Desktop Not Available

If template doesn't have desktop dependencies:

```python
from bunnyshell import Sandbox, DesktopNotAvailableError

sandbox = Sandbox.create(template="code-interpreter")

try:
    sandbox.desktop.click(100, 100)
except DesktopNotAvailableError as e:
    print(f"Error: {e.message}")
    # "Desktop automation is not available in this sandbox."
    
    print(f"\nMissing:")
    for dep in e.missing_dependencies:
        print(f"  - {dep}")
    
    print(f"\nInstall command:")
    print(e.install_command)
    # "apt-get update && apt-get install -y xvfb xdotool ..."
    
    print(f"\nDocs: {e.docs_url}")
    # "https://docs.bunnyshell.com/desktop-automation"
```

### Custom Template

To enable desktop automation in your custom template:

```dockerfile
FROM ubuntu:22.04

# Install desktop automation dependencies
RUN apt-get update && apt-get install -y \
    # VNC & X11
    xvfb \
    tigervnc-standalone-server \
    xfce4 \
    xfce4-terminal \
    \
    # Desktop automation tools
    xdotool \
    wmctrl \
    xclip \
    xsel \
    \
    # Screenshot
    imagemagick \
    scrot \
    \
    # Recording
    ffmpeg \
    \
    # OCR (optional)
    tesseract-ocr \
    \
    && rm -rf /var/lib/apt/lists/*

# Your application code
# ...
```

---

## 🔍 Use Cases

### 1. Browser Testing

```python
# Automated browser testing
sandbox = Sandbox.create(template="desktop")

# Start browser
sandbox.commands.run('chromium-browser &', background=True)
time.sleep(2)

# Automate tests
sandbox.desktop.combination(['ctrl'], 'l')
sandbox.desktop.type("https://myapp.com/login")
sandbox.desktop.press("Return")
time.sleep(1)

# Fill form
sandbox.desktop.click(300, 200)  # Username field
sandbox.desktop.type("testuser")
sandbox.desktop.press("Tab")
sandbox.desktop.type("password123")
sandbox.desktop.press("Return")

# Capture result
img = sandbox.desktop.screenshot()
```

### 2. Demo Recording

```python
# Record product demo
rec = sandbox.desktop.start_recording(fps=30, quality="high")

# Perform demo actions...
sandbox.desktop.click(...)
sandbox.desktop.type(...)

# Stop and download
final_rec = sandbox.desktop.stop_recording(rec.recording_id)
video = sandbox.desktop.download_recording(rec.recording_id)
```

### 3. UI Testing

```python
# Test UI interactions
windows = sandbox.desktop.get_windows()
app_window = next((w for w in windows if 'MyApp' in w.title), None)

if app_window:
    sandbox.desktop.focus_window(app_window.id)
    
    # Test button click
    sandbox.desktop.click(400, 300)
    time.sleep(0.5)
    
    # Verify result
    img = sandbox.desktop.screenshot_region(400, 300, 200, 100)
    # ... analyze screenshot ...
```

### 4. Data Entry Automation

```python
# Automate repetitive data entry
for item in data:
    sandbox.desktop.click(field_x, field_y)
    sandbox.desktop.type(item['value'])
    sandbox.desktop.press("Tab")
```

---

## 📊 Performance Tips

1. **VNC**: Only start VNC if you need remote access
2. **Recording**: Use lower FPS (10-15) for smaller file sizes
3. **Screenshots**: Use region capture when possible
4. **Resolution**: Lower resolution = better performance
5. **Delays**: Add small delays after actions for UI to respond

---

## 🐛 Troubleshooting

### Desktop check fails

```python
# Check if desktop is available
try:
    status = sandbox.desktop.get_vnc_status()
    print("Desktop available!")
except DesktopNotAvailableError:
    print("Desktop not available - check template")
```

### VNC won't start

- Ensure `tigervnc-standalone-server` is installed
- Check if X server (Xvfb) is running
- Try different display number

### Mouse/keyboard not working

- Ensure `xdotool` is installed
- Check if window has focus
- Verify X11 is running

### Recording fails

- Ensure `ffmpeg` is installed
- Check disk space
- Try lower quality/fps

---

## 📚 Examples

See `/examples` directory:
- `desktop_vnc.py` - VNC server management
- `desktop_automation.py` - Mouse, keyboard, clipboard
- `desktop_screenshot_recording.py` - Screenshots and recording
- `desktop_windows.py` - Window and display management
- `desktop_complete_workflow.py` - Complete automation workflow

---

## 🔗 Related Docs

- [Main README](README.md) - General SDK documentation
- [Agent Issues](../AGENT_ISSUES_AND_IMPROVEMENTS.md) - Known agent limitations
- [Desktop Template](https://docs.bunnyshell.com/templates/desktop) - Desktop template setup

---

**Desktop automation is powerful! Use it to automate GUI testing, create demos, and build amazing workflows!** 🚀

