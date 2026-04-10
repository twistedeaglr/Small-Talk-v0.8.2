# Chat Widget Embed Guide

This guide explains how to embed the chat widget into Google Sites.

## Prerequisites

1. Your Flask chat server must be running and accessible online
2. Server URL (e.g., `https://your-server.com` or `http://your-ip:5000`)

## Method 1: Using Google Sites Embed

### Step 1: Host the Widget
You have two options:

**Option A: Host on the same server as the chat app**
- Place `embed-widget.html` in the same directory as your Flask app
- Access it at: `http://your-server:5000/embed-widget.html`

**Option B: Host on a separate static server**
- Upload `embed-widget.html` to any hosting service
- Examples: GitHub Pages, Netlify, Vercel, Firebase Hosting

### Step 2: Add to Google Sites

1. Go to your Google Site
2. Click **Insert** → **Embed code**
3. Paste this code (replace `YOUR_SERVER_URL` with your actual server):

```html
<iframe 
  src="http://YOUR_SERVER_URL:5000/embed-widget.html" 
  width="100%" 
  height="600px" 
  frameborder="0"
  allow="same-origin"
  style="border: 1px solid #ccc; border-radius: 8px;">
</iframe>
```

### Step 3: Customize Height
- Adjust `height="600px"` to your preferred height
- Use `height="100vh"` to fill the entire viewport

## Method 2: Direct Embed Code (No Server Setup)

If you want a pre-configured embed, use this:

```html
<!-- Replace YOUR_DOMAIN with your server domain -->
<div id="chat-widget" style="width:100%; height:600px; border:1px solid #ccc; border-radius:8px; overflow:hidden;">
  <iframe src="https://YOUR_DOMAIN/embed-widget.html" width="100%" height="100%" frameborder="0" style="border:none;"></iframe>
</div>
```

## Server Configuration

### Important: Update Server for CORS

If Google Sites is on a different domain, update your `server.py` to allow cross-origin requests:

```python
# In server.py, update the Flask-SocketIO initialization:
socketio = SocketIO(
    app, 
    cors_allowed_origins=[
        "https://sites.google.com",
        "https://*.google.com",
        "*"  # Allow all origins (less secure)
    ]
)
```

### Deploy Your Server

For Google Sites to access your server, it must be publicly accessible:

**Local Testing:**
```bash
python server.py
# Access at http://localhost:5000/embed-widget.html
```

**Production Deployment** (choose one):

1. **Heroku** (Free tier available):
```bash
# Install Heroku CLI
heroku create your-chat-app
git push heroku main
```

2. **PythonAnywhere**:
- Upload your files
- Configure WSGI app
- Get public URL

3. **AWS/Google Cloud**:
- Deploy Flask app to cloud
- Get cloud URL

4. **Replit**:
- Upload to Replit
- Get shareable link

## Width Configuration

The widget adjusts to container width. Use these styles:

```html
<!-- Full width -->
<iframe 
  src="..." 
  width="100%" 
  height="600px">
</iframe>

<!-- Fixed width -->
<iframe 
  src="..." 
  width="500px" 
  height="600px">
</iframe>

<!-- Responsive with aspect ratio -->
<div style="position:relative; width:100%; padding-bottom:75%; height:0; overflow:hidden;">
  <iframe 
    src="..." 
    style="position:absolute; top:0; left:0; width:100%; height:100%; border:none;">
  </iframe>
</div>
```

## Troubleshooting

### Widget doesn't load
- Check that server is running and publicly accessible
- Check browser console for CORS errors
- Verify server URL in iframe `src` attribute

### CORS errors
- Server must have CORS enabled
- Update `socketio = SocketIO(app, cors_allowed_origins="*")`
- Or add specific domain: `cors_allowed_origins=["https://sites.google.com"]`

### Socket.io connection fails
- Check Network tab in DevTools
- Verify server URL matches exactly
- May need `https://` instead of `http://`

### Widget stuck on login
- Verify username/password are correct
- Check server is running
- Try creating new user via signup

## Features in Embed

- ✅ User login/signup
- ✅ Channel creation
- ✅ Real-time messaging
- ✅ Message history
- ✅ Responsive design
- ✅ Mobile-friendly
- ✅ Dark mode compatible

## Files

- `embed-widget.html` - Standalone widget (single file)
- `index.html` - Full chat application (for standalone use)
- `server.py` - Flask backend server

## Example Google Sites Setup

```
1. Go to Google Sites
2. Click Pages → +
3. Name it "Chat"
4. Click Insert → Embed code
5. Paste iframe code
6. Set height to 600px or more
7. Click Insert
8. Done!
```

## Notes

- Widget automatically detects server URL from browser location
- All messages are real-time via WebSocket
- User data is stored in server memory (restarts clear data)
- For production, add database storage

## Support

If you encounter issues:
1. Check browser console (F12 → Console tab)
2. Check server logs
3. Verify network connectivity
4. Test direct access to `server.py` works
