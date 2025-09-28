# 🕌 Islamic AI Agent - Website Integration Guide

## Overview
This guide will help you integrate the Islamic AI Agent chat widget with your existing website **theislaminsights.com**. The widget provides a beautiful, responsive chat interface that connects to your Islamic AI backend.

---

## 🚀 Quick Start

### Option 1: Simple HTML Integration (Recommended for most websites)

1. **Upload the widget file** to your website:
   ```
   islamic-chat-widget.js
   ```

2. **Add to your website** (before closing `</body>` tag):
   ```html
   <!-- Islamic AI Chat Widget Configuration -->
   <script>
       window.IslamicChatConfig = {
           apiUrl: 'https://your-api-server.com',  // Your deployed API URL
           position: 'bottom-right',
           theme: 'islamic-green',
           title: 'Islamic AI Assistant',
           subtitle: 'Ask about Islam, Quran, Hadith & more'
       };
   </script>
   
   <!-- Load the Islamic Chat Widget -->
   <script src="path/to/islamic-chat-widget.js"></script>
   ```

3. **That's it!** The chat button will appear on your website.

---

## 🎨 Widget Features

### 🔥 Beautiful Design
- **Islamic Theme**: Green gradient colors with mosque emoji
- **Responsive**: Works perfectly on desktop and mobile
- **Smooth Animations**: Professional slide-up effects
- **Modern UI**: Clean, contemporary design

### 💬 Chat Functionality
- **4 Search Modes**: General, Quran, Hadith, Scholar consultation
- **Real-time Responses**: Connects to your Islamic AI backend
- **Typing Indicators**: Shows when AI is processing
- **Message History**: Maintains conversation context
- **Beautiful Formatting**: Supports emojis and structured responses

### ⚙️ Customization Options
- **Position**: Bottom-right or bottom-left
- **Colors**: Islamic green theme (customizable)
- **Text**: Custom title and subtitle
- **Size**: Responsive design adapts to screen size

---

## 🔧 Configuration Options

```javascript
window.IslamicChatConfig = {
    // Required: Your Islamic AI API server URL
    apiUrl: 'https://your-api-server.com',
    
    // Optional: Widget position (default: 'bottom-right')
    position: 'bottom-right', // or 'bottom-left'
    
    // Optional: Color theme (default: 'islamic-green')
    theme: 'islamic-green',
    
    // Optional: Widget title (default: 'Islamic AI Assistant')
    title: 'Islamic AI Assistant',
    
    // Optional: Widget subtitle
    subtitle: 'Ask about Islam, Quran, Hadith & more'
};
```

---

## 🌐 WordPress Integration

### Option 2: WordPress Plugin (Easy Installation)

1. **Upload the plugin folder** to your WordPress:
   ```
   /wp-content/plugins/islamic-ai-chat/
   ```

2. **Activate the plugin** in WordPress Admin:
   - Go to `Plugins > Installed Plugins`
   - Find "Islamic AI Chat Widget"
   - Click "Activate"

3. **Configure the plugin**:
   - Go to `Settings > Islamic AI Chat`
   - Enter your API URL
   - Customize title, subtitle, position
   - Save changes

4. **The widget will automatically appear** on all pages!

### WordPress Plugin Features
- ✅ **Easy Configuration**: Admin panel settings
- ✅ **Automatic Loading**: No code required
- ✅ **Enable/Disable**: Toggle widget on/off
- ✅ **Customization**: All options available in admin
- ✅ **Updates**: Easy plugin updates

---

## 🖥️ Backend Deployment

### Step 1: Deploy Your Islamic AI API

1. **Choose a hosting platform**:
   - **Recommended**: DigitalOcean, AWS, Google Cloud
   - **Budget-friendly**: Heroku, Railway, Render

2. **Deploy your Flask API**:
   ```bash
   # Your Islamic AI backend files
   simple_api.py
   multi_agent_islamic_system.py
   islamic_ai_agent.py
   enhanced_islamic_tools.py
   requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the server**:
   ```bash
   python simple_api.py
   ```

### Step 2: Configure CORS

Your API is already configured for theislaminsights.com:

```python
CORS(app, origins=[
    "https://theislaminsights.com",
    "https://www.theislaminsights.com", 
    "http://localhost:3000",  # For development
])
```

### Step 3: SSL Certificate (HTTPS)

For production, ensure your API server has SSL:
- Use Let's Encrypt for free SSL
- Most hosting platforms provide SSL automatically

---

## 🔒 Security Considerations

### Rate Limiting (Recommended)
Add rate limiting to prevent abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # Your existing chat endpoint
```

### API Key Protection
Consider adding API key authentication:

```python
@app.before_request
def check_api_key():
    if request.endpoint in ['chat', 'scholar']:
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
```

---

## 📱 Mobile Responsiveness

The widget is fully responsive and includes:

- **Mobile-First Design**: Optimized for small screens
- **Touch-Friendly**: Large buttons and easy scrolling
- **Adaptive Layout**: Adjusts to screen size automatically
- **Performance Optimized**: Lightweight and fast loading

### Mobile Features:
```css
@media (max-width: 480px) {
    .islamic-chat-container {
        width: calc(100vw - 40px);
        height: calc(100vh - 100px);
        bottom: 80px;
        right: 20px;
    }
}
```

---

## 🎯 Testing Your Integration

### 1. Local Testing
```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Islamic AI Widget</title>
</head>
<body>
    <h1>Test Page</h1>
    <p>The chat widget should appear in the bottom-right corner.</p>
    
    <script>
        window.IslamicChatConfig = {
            apiUrl: 'http://localhost:5002',
            title: 'Test Islamic AI'
        };
    </script>
    <script src="islamic-chat-widget.js"></script>
</body>
</html>
```

### 2. Production Testing Checklist
- [ ] Chat button appears in correct position
- [ ] Widget opens and closes smoothly
- [ ] All 4 search modes work correctly
- [ ] Messages send and receive properly
- [ ] Mobile responsiveness works
- [ ] HTTPS connection is secure
- [ ] No console errors

---

## 🚨 Troubleshooting

### Common Issues:

#### 1. Chat Widget Not Appearing
- **Check**: JavaScript file is loaded correctly
- **Check**: Configuration object is defined
- **Check**: No JavaScript errors in console

#### 2. API Connection Failed
- **Check**: API URL is correct and accessible
- **Check**: CORS is configured for your domain
- **Check**: API server is running and responding

#### 3. Messages Not Sending
- **Check**: Network tab in browser developer tools
- **Check**: API endpoints are responding correctly
- **Check**: Request format matches expected structure

#### 4. Mobile Display Issues
- **Check**: Viewport meta tag is present
- **Check**: CSS media queries are working
- **Check**: Touch events are responsive

### Debug Mode:
Add this to enable console logging:
```javascript
window.IslamicChatConfig = {
    apiUrl: 'your-api-url',
    debug: true  // Enable debug logging
};
```

---

## 🎨 Customization Examples

### Custom Colors:
```css
.islamic-chat-toggle {
    background: linear-gradient(135deg, #your-color1, #your-color2) !important;
}

.islamic-chat-header {
    background: linear-gradient(135deg, #your-color1, #your-color2) !important;
}
```

### Custom Position:
```javascript
window.IslamicChatConfig = {
    apiUrl: 'your-api-url',
    position: 'bottom-left',  // Move to left side
    customCSS: `
        .islamic-chat-widget.bottom-left {
            left: 20px;
            right: auto;
        }
    `
};
```

---

## 📊 Analytics Integration

### Track Chat Usage:
```javascript
// Add to your widget configuration
window.IslamicChatConfig = {
    apiUrl: 'your-api-url',
    onMessageSent: function(message) {
        // Google Analytics
        gtag('event', 'islamic_chat_message_sent', {
            'message_type': message.type,
            'message_length': message.text.length
        });
    },
    onWidgetOpened: function() {
        gtag('event', 'islamic_chat_opened');
    }
};
```

---

## 🔄 Updates and Maintenance

### Updating the Widget:
1. Replace `islamic-chat-widget.js` with new version
2. Clear browser cache
3. Test functionality

### Monitoring:
- Monitor API server performance
- Check error logs regularly
- Update dependencies periodically
- Backup configuration settings

---

## 📞 Support

### Documentation:
- **Full API Documentation**: Available in your project files
- **Widget Customization**: CSS and JavaScript examples provided
- **Troubleshooting**: Common issues and solutions included

### Contact:
- **Website**: theislaminsights.com
- **Technical Issues**: Check console logs and API responses
- **Feature Requests**: Document in project issues

---

## 🎉 Go Live Checklist

Before deploying to production:

- [ ] **API Server**: Deployed with HTTPS
- [ ] **CORS**: Configured for your domain
- [ ] **Widget**: Uploaded to your website
- [ ] **Configuration**: API URL updated to production
- [ ] **Testing**: All features tested on production
- [ ] **Mobile**: Responsive design verified
- [ ] **Performance**: Load times optimized
- [ ] **Security**: Rate limiting and API keys configured
- [ ] **Analytics**: Tracking implemented (optional)
- [ ] **Backup**: Configuration and files backed up

---

**🕌 Your Islamic AI Agent is now ready to serve visitors on theislaminsights.com!**

The widget provides a seamless, beautiful experience that combines authentic Islamic knowledge with modern web technology. Users can now easily access Quranic guidance, Hadith research, scholarly consultation, and general Islamic knowledge directly from your website.

*May Allah bless this effort and make it beneficial for the Muslim Ummah! 🤲*
