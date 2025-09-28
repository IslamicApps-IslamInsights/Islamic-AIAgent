/**
 * Islamic AI Agent Chat Widget for theislaminsights.com
 * Embeddable chat interface that connects to your Islamic AI backend
 */

class IslamicChatWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:5010',  // Updated default port to 5010
            position: config.position || 'bottom-right',
            theme: config.theme || 'islamic-green',
            title: config.title || 'Islamic AI Assistant',
            subtitle: config.subtitle || 'Ask about Islam, Quran, Hadith & more',
            ...config
        };
        
        this.isOpen = false;
        this.messages = [];
        this.searchMode = 'normal';
        
        this.init();
    }
    
    init() {
        this.createStyles();
        this.createWidget();
        this.attachEventListeners();
    }
    
    // Format message content with markdown-like syntax and user-centric improvements
    formatMessageContent(text) {
        if (!text) return '';

        // Handle section separators (3 or 5 asterisks on a line by themselves)
        text = text
            .replace(/^\s*\*{5,}\s*$/gm, '<div class="section-separator wide"></div>')  // 5+ asterisks = wide separator
            .replace(/^\s*\*{3,4}\s*$/gm, '<div class="section-separator"></div>');     // 3-4 asterisks = normal separator

        // Handle horizontal rules with text in the middle
        text = text.replace(/^\s*\*{3}\s+(.*?)\s+\*{3}\s*$/gm, 
            '<div class="section-separator with-text"><span>$1</span></div>');

        // Simple markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>')                // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>')               // Code
            .replace(/\n/g, '<br>')                               // Line breaks
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, 
                '<a href="$2" target="_blank" rel="noopener noreferrer" class="message-link">$1 <i class="fas fa-external-link-alt"></i></a>');  // Links with external icon
    }

    // Get appropriate icon for message type
    getMessageTypeIcon(type) {
        const icons = {
            quran: { emoji: '📖', label: 'Quran' },
            hadith: { emoji: '📜', label: 'Hadith' },
            fiqh: { emoji: '⚖️', label: 'Fiqh' },
            scholar: { emoji: '👨\u200d🏫', label: 'Scholar' },
            error: { emoji: '⚠️', label: 'Error' },
            greeting: { emoji: '👋', label: 'Welcome' },
            default: { emoji: '💬', label: 'Message' }
        };
        return icons[type] || icons.default;
    }
    
    createStyles() {
        const styles = `
            .islamic-chat-widget {
                position: fixed;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .islamic-chat-widget.bottom-right {
                bottom: 20px;
                right: 20px;
            }
            
            .islamic-chat-widget.bottom-left {
                bottom: 20px;
                left: 20px;
            }
            
            .islamic-chat-toggle {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #16a085, #27ae60);
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(22, 160, 133, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                color: white;
                font-size: 24px;
            }
            
            .islamic-chat-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 25px rgba(22, 160, 133, 0.4);
            }
            
            .islamic-chat-container {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 380px;
                height: 600px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
                display: none;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid #e0e0e0;
            }
            
            .islamic-chat-container.open {
                display: flex;
                animation: slideUp 0.3s ease-out;
            }
            
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .islamic-chat-header {
                background: linear-gradient(135deg, #16a085, #27ae60);
                color: white;
                padding: 20px;
                text-align: center;
                position: relative;
            }
            
            .islamic-chat-title {
                font-size: 18px;
                font-weight: 600;
                margin: 0 0 5px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            .islamic-chat-subtitle {
                font-size: 14px;
                opacity: 0.9;
                margin: 0;
            }
            
            .islamic-chat-close {
                position: absolute;
                top: 15px;
                right: 15px;
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                opacity: 0.8;
                transition: opacity 0.2s;
            }
            
            .islamic-chat-close:hover {
                opacity: 1;
            }
            
            .islamic-chat-expand {
                position: absolute;
                top: 15px;
                right: 45px;
                background: none;
                border: none;
                color: white;
                font-size: 16px;
                cursor: pointer;
                opacity: 0.8;
                transition: opacity 0.2s;
            }
            
            .islamic-chat-expand:hover {
                opacity: 1;
            }
            
            .islamic-chat-container.expanded {
                width: 600px;
                height: 700px;
            }
            
            .islamic-features-tabs {
                display: flex;
                background: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .islamic-tab {
                flex: 1;
                padding: 12px 8px;
                border: none;
                background: transparent;
                cursor: pointer;
                font-size: 12px;
                color: #666;
                transition: all 0.2s;
                border-bottom: 2px solid transparent;
            }
            
            .islamic-tab.active {
                color: #16a085;
                border-bottom-color: #16a085;
                background: white;
            }
            
            .islamic-tab:hover {
                background: #f0f0f0;
            }
            
            .islamic-tab-content {
                display: none;
                flex: 1;
                overflow-y: auto;
            }
            
            .islamic-tab-content.active {
                display: flex;
                flex-direction: column;
            }
            
            .islamic-search-modes {
                padding: 15px;
                background: #f8f9fa;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .islamic-search-modes-title {
                font-size: 12px;
                font-weight: 600;
                color: #666;
                margin-bottom: 8px;
            }
            
            .islamic-search-buttons {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
            }
            
            .islamic-search-mode {
                padding: 6px 12px;
                border: 1px solid #ddd;
                background: white;
                border-radius: 15px;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.2s;
                color: #666;
            }
            
            .islamic-search-mode.active {
                background: #16a085;
                color: white;
                border-color: #16a085;
            }
            
            .islamic-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #fafafa;
            }
            
            .islamic-message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
                gap: 10px;
            }
            
            .islamic-message.user {
                flex-direction: row-reverse;
            }
            
            .islamic-message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                flex-shrink: 0;
            }
            
            .islamic-message.agent .islamic-message-avatar {
                background: linear-gradient(135deg, #16a085, #27ae60);
                color: white;
            }
            
                border: 1px solid #e0e0e0;
            }
            
            .islamic-message.user .islamic-message-content {
                background: #16a085;
                color: white;
            }
            
            .islamic-message-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .islamic-message-badge.quran {
                background: #e8f5e8;
                color: #27ae60;
            }
            
            .islamic-message-badge.hadith {
                background: #f8f1d3;
                color: #8c6d1f;
                border: 1px solid #e8d9a0;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            /* Hadith Card Styling */
            .hadith-card {
                background: #fff9e6;
                border: 1px solid #f5e7b2;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                max-width: 100%;
            }
            
            .hadith-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid #f0e5b8;
            }
            
            .hadith-title {
                font-size: 16px;
                font-weight: 600;
                color: #8c6d1f;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .hadith-title i {
                color: #e6b800;
            }
            
            .hadith-text {
                font-size: 15px;
                line-height: 1.7;
                color: #333;
                margin-bottom: 16px;
            }
            
            .hadith-meta {
                background: #fffcf0;
                border-radius: 8px;
                padding: 12px;
                margin: 12px 0;
                border: 1px solid #f0e5b8;
            }
            
            .hadith-meta-item {
                display: flex;
                margin-bottom: 6px;
                font-size: 13px;
                line-height: 1.5;
            }
            
            .hadith-meta-item:last-child {
                margin-bottom: 0;
            }
            
            .hadith-meta-label {
                font-weight: 600;
                color: #8c6d1f;
                min-width: 70px;
                flex-shrink: 0;
            }
            
            .hadith-meta-value {
                color: #5a4a0f;
                flex-grow: 1;
            }
            
            .hadith-authenticity {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #e8f5e9;
                color: #2e7d32;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                margin-top: 8px;
            }
            
            .hadith-authenticity i {
                color: #4caf50;
            }
            
            .hadith-source {
                margin-top: 12px;
                font-size: 12px;
                color: #666;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .hadith-source i {
                color: #8c6d1f;
            }
            
            .islamic-message-badge.scholar {
                background: #f8d7da;
                color: #721c24;
            }
            
            /* Message content styling */
            .islamic-message-content {
                padding: 12px 16px;
                border-radius: 18px;
                max-width: 85%;
                word-wrap: break-word;
                line-height: 1.5;
                font-size: 14px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                position: relative;
                margin-bottom: 4px;
            }
            
            /* Section Separators */
            .section-separator {
                margin: 24px 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
                position: relative;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .section-separator.wide {
                height: 2px;
                margin: 32px 0;
                background: linear-gradient(90deg, transparent, #16a085, transparent);
            }
            
            .section-separator.with-text {
                background: none;
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin: 32px 0;
            }
            
            .section-separator.with-text span {
                background: white;
                padding: 0 12px;
                position: relative;
                color: #16a085;
                font-weight: 600;
            }
            
            .section-separator.with-text:before {
                content: '';
                position: absolute;
                top: 50%;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, #16a085, transparent);
                z-index: -1;
            }
            
            .islamic-message.agent .islamic-message-content {
                background: #f0f7ff;
                color: #1a1a1a;
                border-radius: 18px 18px 18px 4px;
                margin-left: 8px;
            }
            
            /* Error message styling */
            .islamic-message.agent .islamic-message-content.error-message {
                background: #fff0f0;
                border-left: 4px solid #ff6b6b;
                padding-left: 12px;
                border-radius: 18px 18px 18px 4px;
                color: #d32f2f;
            }
            
            .islamic-message.agent .islamic-message-content.error-message::before {
                content: '⚠️ ';
            }
            
            /* Message text styling */
            .message-text {
                margin: 5px 0;
                line-height: 1.5;
            }
            
            /* Agent info styling */
            .islamic-message-agent {
                margin-top: 8px;
                padding-top: 6px;
                border-top: 1px dashed rgba(0,0,0,0.1);
                color: #666;
                font-size: 0.8em;
                text-align: right;
            }
            
            /* Improved message layout */
            .islamic-message-content {
                display: flex;
                flex-direction: column;
                gap: 6px;
                width: 100%;
                position: relative;
                
                /* Add subtle animation */
                animation: messageAppear 0.3s ease-out;
                transform-origin: left bottom;
            }
            
            @keyframes messageAppear {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Enhanced Arabic text styling */
            .arabic-text {
                font-family: 'Traditional Arabic', 'Arial', sans-serif;
                font-size: 1.2em;
                line-height: 1.8;
                text-align: right;
                direction: rtl;
                padding: 10px 0;
                color: #1a1a1a;
            }
            
            /* Translation separator */
            .translation-separator {
                position: relative;
                text-align: center;
                margin: 10px 0;
                color: #666;
                font-size: 0.8em;
            }
            
            .translation-separator:before,
            .translation-separator:after {
                content: '';
                display: inline-block;
                width: 30%;
                height: 1px;
                background: #e0e0e0;
                position: relative;
                vertical-align: middle;
            }
            
            .translation-separator:before {
                right: 10px;
            }
            
            .translation-separator:after {
                left: 10px;
            }
            
            /* Improved references styling */
            .islamic-references {
                margin-top: 10px;
                padding: 8px 12px;
                background: #f8f9fa;
                border-radius: 8px;
                border-right: 3px solid #16a085;
            }
            
            .references-header {
                font-weight: 600;
                color: #16a085;
                margin-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .references-list {
                margin: 0;
                padding-left: 20px;
            }
            
            .reference-item {
                margin: 4px 0;
                color: #555;
                font-size: 0.9em;
                display: flex;
                align-items: flex-start;
                gap: 6px;
            }
            
            .reference-item i {
                color: #16a085;
                font-size: 0.8em;
                margin-top: 3px;
            }
            }
            
            .islamic-chat-input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
            }
            
            .islamic-chat-input-container {
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }
            
            .islamic-chat-input {
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 20px;
                padding: 12px 16px;
                font-size: 14px;
                resize: none;
                max-height: 80px;
                min-height: 40px;
                outline: none;
                transition: border-color 0.2s;
            }
            
            .islamic-chat-input:focus {
                border-color: #16a085;
            }
            
            .islamic-chat-send {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #16a085;
                border: none;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.2s;
            }
            
            .islamic-chat-send:hover {
                background: #138d75;
            }
            
            .islamic-chat-send:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .islamic-typing {
                display: flex;
                align-items: center;
                gap: 5px;
                color: #666;
                font-size: 12px;
                padding: 10px 0;
            }
            
            .islamic-typing-dots {
                display: flex;
                gap: 2px;
            }
            
            .islamic-typing-dot {
                width: 4px;
                height: 4px;
                border-radius: 50%;
                background: #16a085;
                animation: typing 1.4s infinite;
            }
            
            .islamic-typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }
            
            .islamic-typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }
            
            @keyframes typing {
                0%, 60%, 100% { opacity: 0.3; }
                30% { opacity: 1; }
            }
            
            /* Prayer Times Styles */
            .islamic-prayer-times {
                padding: 20px;
            }
            
            .islamic-date-info {
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: linear-gradient(135deg, #16a085, #27ae60);
                color: white;
                border-radius: 10px;
            }
            
            .islamic-gregorian-date {
                font-size: 16px;
                font-weight: 600;
            }
            
            .islamic-hijri-date {
                font-size: 14px;
                opacity: 0.9;
                margin-top: 5px;
            }
            
            .islamic-location-info {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                font-size: 12px;
            }
            
            .islamic-location-btn {
                background: #16a085;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 10px;
                cursor: pointer;
            }
            
            .islamic-prayer-list {
                margin-bottom: 20px;
            }
            
            .islamic-prayer-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 15px;
                margin-bottom: 8px;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                transition: all 0.2s;
            }
            
            .islamic-prayer-item:hover {
                background: #f8f9fa;
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .prayer-name {
                font-weight: 600;
                color: #333;
            }
            
            .prayer-time {
                font-weight: 600;
                color: #16a085;
                font-size: 16px;
            }
            
            .islamic-next-prayer {
                text-align: center;
                padding: 15px;
                background: linear-gradient(135deg, #f39c12, #e67e22);
                color: white;
                border-radius: 10px;
            }
            
            .next-prayer-text {
                font-size: 12px;
                opacity: 0.9;
            }
            
            .next-prayer-name {
                font-size: 18px;
                font-weight: 600;
                margin: 5px 0;
            }
            
            .next-prayer-countdown {
                font-size: 24px;
                font-weight: 700;
                font-family: monospace;
            }
            
            /* Qibla Finder Styles */
            .islamic-qibla-finder {
                padding: 20px;
                text-align: center;
            }
            
            .qibla-compass {
                margin: 20px auto;
                width: 200px;
                height: 200px;
                position: relative;
            }
            
            .compass-circle {
                width: 100%;
                height: 100%;
                border: 3px solid #16a085;
                border-radius: 50%;
                position: relative;
                background: radial-gradient(circle, #f8f9fa 0%, #e9ecef 100%);
            }
            
            .compass-needle {
                position: absolute;
                top: 10px;
                left: 50%;
                width: 4px;
                height: 80px;
                background: linear-gradient(to bottom, #e74c3c 0%, #c0392b 50%, #16a085 50%, #138d75 100%);
                transform-origin: bottom center;
                transform: translateX(-50%) rotate(0deg);
                border-radius: 2px;
                transition: transform 0.5s ease;
            }
            
            .compass-kaaba {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 24px;
            }
            
            .compass-directions {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }
            
            .compass-n, .compass-e, .compass-s, .compass-w {
                position: absolute;
                font-weight: 600;
                color: #16a085;
                font-size: 14px;
            }
            
            .compass-n { top: 5px; left: 50%; transform: translateX(-50%); }
            .compass-e { right: 5px; top: 50%; transform: translateY(-50%); }
            .compass-s { bottom: 5px; left: 50%; transform: translateX(-50%); }
            .compass-w { left: 5px; top: 50%; transform: translateY(-50%); }
            
            .qibla-info {
                margin: 20px 0;
                display: flex;
                justify-content: space-around;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
            }
            
            .qibla-direction, .qibla-distance {
                text-align: center;
            }
            
            .qibla-label {
                display: block;
                font-size: 12px;
                color: #666;
                margin-bottom: 5px;
            }
            
            .qibla-value {
                display: block;
                font-size: 18px;
                font-weight: 600;
                color: #16a085;
            }
            
            .islamic-qibla-btn {
                background: #16a085;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 14px;
                cursor: pointer;
                margin: 20px 0;
                transition: all 0.2s;
            }
            
            .islamic-qibla-btn:hover {
                background: #138d75;
                transform: translateY(-1px);
            }
            
            .qibla-dua {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
                text-align: center;
            }
            
            .qibla-dua h4 {
                margin: 0 0 10px 0;
                color: #16a085;
            }
            
            .arabic-text {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin: 10px 0;
                direction: rtl;
            }
            
            .transliteration {
                font-style: italic;
                color: #666;
                margin: 5px 0;
                font-size: 14px;
            }
            
            .translation {
                color: #333;
                font-size: 14px;
                margin-top: 5px;
            }
            
            /* Tools Grid Styles */
            .islamic-tools-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                padding: 20px;
            }
            
            .islamic-tool-card {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .islamic-tool-card:hover {
                background: #f8f9fa;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border-color: #16a085;
            }
            
            .tool-icon {
                font-size: 32px;
                margin-bottom: 10px;
            }
            
            .tool-title {
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
                font-size: 14px;
            }
            
            .tool-description {
                font-size: 12px;
                color: #666;
                line-height: 1.3;
            }
            
            @media (max-width: 480px) {
                .islamic-chat-container {
                    width: calc(100vw - 40px);
                    height: calc(100vh - 100px);
                    bottom: 80px;
                    right: 20px;
                }
                
                .islamic-chat-container.expanded {
                    width: calc(100vw - 20px);
                    height: calc(100vh - 80px);
                }
                
                .islamic-tools-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    createWidget() {
        const widget = document.createElement('div');
        widget.className = `islamic-chat-widget ${this.config.position}`;
        widget.innerHTML = `
            <button class="islamic-chat-toggle" id="islamic-chat-toggle">
                🕌
            </button>
            <div class="islamic-chat-container" id="islamic-chat-container">
                <div class="islamic-chat-header">
                    <button class="islamic-chat-close" id="islamic-chat-close">×</button>
                    <button class="islamic-chat-expand" id="islamic-chat-expand">⛶</button>
                    <h3 class="islamic-chat-title">
                        🕌 ${this.config.title}
                    </h3>
                    <p class="islamic-chat-subtitle">${this.config.subtitle}</p>
                </div>
                
                <div class="islamic-features-tabs" id="islamic-features-tabs">
                    <button class="islamic-tab active" data-tab="chat">💬 Chat</button>
                    <button class="islamic-tab" data-tab="prayer">🕐 Prayer</button>
                    <button class="islamic-tab" data-tab="qibla">🧭 Qibla</button>
                    <button class="islamic-tab" data-tab="tools">🛠️ Tools</button>
                </div>
                
                <!-- Chat Tab Content -->
                <div class="islamic-tab-content active" id="chat-content">
                    <div class="islamic-search-modes">
                        <div class="islamic-search-modes-title">Search Mode:</div>
                        <div class="islamic-search-buttons">
                            <button class="islamic-search-mode active" data-mode="normal">💬 General</button>
                            <button class="islamic-search-mode" data-mode="quran">📖 Quran</button>
                            <button class="islamic-search-mode" data-mode="hadith">⭐ Hadith</button>
                            <button class="islamic-search-mode" data-mode="scholar">👨‍🏫 Scholar</button>
                        </div>
                    </div>
                    
                    <div class="islamic-chat-messages" id="islamic-chat-messages"></div>
                    
                    <div class="islamic-chat-input-area">
                        <div class="islamic-chat-input-container">
                            <textarea 
                                class="islamic-chat-input" 
                                id="islamic-chat-input"
                                placeholder="Ask about Islam: prayers, Quran, halal food, duas..."
                                rows="1"
                            ></textarea>
                            <button class="islamic-chat-send" id="islamic-chat-send">
                                ➤
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Prayer Times Tab Content -->
                <div class="islamic-tab-content" id="prayer-content">
                    <div class="islamic-prayer-times">
                        <div class="islamic-date-info">
                            <div class="islamic-gregorian-date" id="gregorian-date"></div>
                            <div class="islamic-hijri-date" id="hijri-date"></div>
                        </div>
                        
                        <div class="islamic-location-info" id="location-info">
                            📍 <span id="location-text">Getting location...</span>
                            <button class="islamic-location-btn" id="get-location-btn">📍 Get Location</button>
                        </div>
                        
                        <div class="islamic-prayer-list" id="prayer-list">
                            <div class="islamic-prayer-item">
                                <span class="prayer-name">🌅 Fajr</span>
                                <span class="prayer-time" id="fajr-time">--:--</span>
                            </div>
                            <div class="islamic-prayer-item">
                                <span class="prayer-name">☀️ Dhuhr</span>
                                <span class="prayer-time" id="dhuhr-time">--:--</span>
                            </div>
                            <div class="islamic-prayer-item">
                                <span class="prayer-name">🌤️ Asr</span>
                                <span class="prayer-time" id="asr-time">--:--</span>
                            </div>
                            <div class="islamic-prayer-item">
                                <span class="prayer-name">🌅 Maghrib</span>
                                <span class="prayer-time" id="maghrib-time">--:--</span>
                            </div>
                            <div class="islamic-prayer-item">
                                <span class="prayer-name">🌙 Isha</span>
                                <span class="prayer-time" id="isha-time">--:--</span>
                            </div>
                        </div>
                        
                        <div class="islamic-next-prayer" id="next-prayer">
                            <div class="next-prayer-text">Next Prayer:</div>
                            <div class="next-prayer-name" id="next-prayer-name">--</div>
                            <div class="next-prayer-countdown" id="next-prayer-countdown">--:--:--</div>
                        </div>
                    </div>
                </div>
                
                <!-- Qibla Tab Content -->
                <div class="islamic-tab-content" id="qibla-content">
                    <div class="islamic-qibla-finder">
                        <div class="qibla-compass" id="qibla-compass">
                            <div class="compass-circle">
                                <div class="compass-needle" id="compass-needle"></div>
                                <div class="compass-kaaba">🕋</div>
                                <div class="compass-directions">
                                    <div class="compass-n">N</div>
                                    <div class="compass-e">E</div>
                                    <div class="compass-s">S</div>
                                    <div class="compass-w">W</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="qibla-info" id="qibla-info">
                            <div class="qibla-direction">
                                <span class="qibla-label">Direction:</span>
                                <span class="qibla-value" id="qibla-direction">--°</span>
                            </div>
                            <div class="qibla-distance">
                                <span class="qibla-label">Distance to Mecca:</span>
                                <span class="qibla-value" id="qibla-distance">-- km</span>
                            </div>
                        </div>
                        
                        <button class="islamic-qibla-btn" id="find-qibla-btn">🧭 Find Qibla Direction</button>
                        
                        <div class="qibla-dua">
                            <h4>🤲 Dua when facing Qibla:</h4>
                            <div class="arabic-text">وَجَّهْتُ وَجْهِيَ لِلَّذِي فَطَرَ السَّمَاوَاتِ وَالْأَرْضَ</div>
                            <div class="transliteration">Wajjahtu wajhiya lilladhi fatara as-samawati wal-arda</div>
                            <div class="translation">"I have turned my face toward Him who created the heavens and the earth"</div>
                        </div>
                    </div>
                </div>
                
                <!-- Tools Tab Content -->
                <div class="islamic-tab-content" id="tools-content">
                    <div class="islamic-tools-grid">
                        <div class="islamic-tool-card" id="zakat-calculator">
                            <div class="tool-icon">💰</div>
                            <div class="tool-title">Zakat Calculator</div>
                            <div class="tool-description">Calculate your Zakat obligation</div>
                        </div>
                        
                        <div class="islamic-tool-card" id="tasbih-counter">
                            <div class="tool-icon">📿</div>
                            <div class="tool-title">Digital Tasbih</div>
                            <div class="tool-description">Count your dhikr and prayers</div>
                        </div>
                        
                        <div class="islamic-tool-card" id="hijri-converter">
                            <div class="tool-icon">📅</div>
                            <div class="tool-title">Date Converter</div>
                            <div class="tool-description">Convert Hijri to Gregorian dates</div>
                        </div>
                        
                        <div class="islamic-tool-card" id="quran-audio">
                            <div class="tool-icon">🎧</div>
                            <div class="tool-title">Quran Audio</div>
                            <div class="tool-description">Listen to Quran recitation</div>
                        </div>
                        
                        <div class="islamic-tool-card" id="dua-collection">
                            <div class="tool-icon">🤲</div>
                            <div class="tool-title">Daily Duas</div>
                            <div class="tool-description">Essential Islamic supplications</div>
                        </div>
                        
                        <div class="islamic-tool-card" id="islamic-names">
                            <div class="tool-icon">👶</div>
                            <div class="tool-title">Islamic Names</div>
                            <div class="tool-description">Beautiful names with meanings</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(widget);
        this.widget = widget;
    }
    
    attachEventListeners() {
        const toggle = document.getElementById('islamic-chat-toggle');
        const close = document.getElementById('islamic-chat-close');
        const expand = document.getElementById('islamic-chat-expand');
        const input = document.getElementById('islamic-chat-input');
        const send = document.getElementById('islamic-chat-send');
        const searchModes = document.querySelectorAll('.islamic-search-mode');
        const tabs = document.querySelectorAll('.islamic-tab');
        const getLocationBtn = document.getElementById('get-location-btn');
        const findQiblaBtn = document.getElementById('find-qibla-btn');
        const toolCards = document.querySelectorAll('.islamic-tool-card');
        
        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.closeChat());
        expand.addEventListener('click', () => this.toggleExpanded());
        send.addEventListener('click', () => this.sendMessage());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        input.addEventListener('input', () => {
            this.autoResize(input);
        });
        
        searchModes.forEach(button => {
            button.addEventListener('click', () => {
                searchModes.forEach(b => b.classList.remove('active'));
                button.classList.add('active');
                this.searchMode = button.dataset.mode;
                this.updateInputPlaceholder();
            });
        });
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.switchTab(tab.dataset.tab);
            });
        });
        
        if (getLocationBtn) {
            getLocationBtn.addEventListener('click', () => this.getUserLocation());
        }
        
        if (findQiblaBtn) {
            findQiblaBtn.addEventListener('click', () => this.findQiblaDirection());
        }
        
        toolCards.forEach(card => {
            card.addEventListener('click', () => this.openTool(card.id));
        });
        
        // Initialize features
        this.initializeDates();
        this.getUserLocation();
        this.startPrayerTimeUpdates();
    }
    
    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 80) + 'px';
    }
    
    updateInputPlaceholder() {
        const input = document.getElementById('islamic-chat-input');
        const placeholders = {
            normal: "Ask about Islam: prayers, Quran, halal food, duas...",
            quran: "Search Quran: verse reference (2:255), surah name, or topic...",
            hadith: "Search Hadith: topic, narrator, collection, or authenticity grade...",
            scholar: "Ask Islamic Scholar: fiqh, aqeedah, contemporary issues..."
        };
        input.placeholder = placeholders[this.searchMode];
    }
    
    toggleChat() {
        const container = document.getElementById('islamic-chat-container');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            container.classList.add('open');
            document.getElementById('islamic-chat-input').focus();
        } else {
            container.classList.remove('open');
        }
    }
    
    closeChat() {
        const container = document.getElementById('islamic-chat-container');
        container.classList.remove('open');
        this.isOpen = false;
    }
    
    toggleExpanded() {
        const container = document.getElementById('islamic-chat-container');
        container.classList.toggle('expanded');
        this.isExpanded = !this.isExpanded;
    }
    
    switchTab(tabName) {
        const tabContents = document.querySelectorAll('.islamic-tab-content');
        tabContents.forEach(content => content.classList.remove('active'));
        
        const targetContent = document.getElementById(`${tabName}-content`);
        if (targetContent) {
            targetContent.classList.add('active');
        }
        
        // Initialize tab-specific features
        if (tabName === 'prayer') {
            this.updatePrayerTimes();
        } else if (tabName === 'qibla') {
            this.updateQiblaDisplay();
        }
    }
    
    initializeDates() {
        const now = new Date();
        const gregorianDate = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        const hijriDate = this.getHijriDate(now);
        
        const gregorianEl = document.getElementById('gregorian-date');
        const hijriEl = document.getElementById('hijri-date');
        
        if (gregorianEl) gregorianEl.textContent = gregorianDate;
        if (hijriEl) hijriEl.textContent = hijriDate;
    }
    
    getHijriDate(date) {
        // Simple Hijri date approximation
        const hijriEpoch = new Date('622-07-16');
        const daysDiff = Math.floor((date - hijriEpoch) / (1000 * 60 * 60 * 24));
        const hijriYear = Math.floor(daysDiff / 354.37) + 1;
        const dayOfYear = daysDiff % 354;
        const hijriMonth = Math.floor(dayOfYear / 29.5) + 1;
        const hijriDay = Math.floor(dayOfYear % 29.5) + 1;
        
        const hijriMonths = [
            'Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani',
            'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
            'Ramadan', 'Shawwal', 'Dhu al-Qidah', 'Dhu al-Hijjah'
        ];
        
        return `${hijriDay} ${hijriMonths[Math.min(hijriMonth - 1, 11)]} ${hijriYear} AH`;
    }
    
    getUserLocation() {
        const locationText = document.getElementById('location-text');
        if (locationText) locationText.textContent = 'Getting location...';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    this.updateLocationDisplay();
                    this.fetchPrayerTimes();
                    this.updateQiblaDirection();
                },
                (error) => {
                    console.log('Location access denied:', error);
                    if (locationText) {
                        locationText.textContent = 'Location access denied';
                    }
                }
            );
        } else {
            if (locationText) {
                locationText.textContent = 'Location not supported';
            }
        }
    }
    
    updateLocationDisplay() {
        const locationText = document.getElementById('location-text');
        if (locationText && this.userLocation) {
            locationText.textContent = `${this.userLocation.latitude.toFixed(2)}, ${this.userLocation.longitude.toFixed(2)}`;
        }
    }
    
    async fetchPrayerTimes() {
        if (!this.userLocation) return;
        
        try {
            const response = await fetch(`http://api.aladhan.com/v1/timings?latitude=${this.userLocation.latitude}&longitude=${this.userLocation.longitude}&method=2`);
            const data = await response.json();
            
            if (data.code === 200) {
                this.prayerTimes = data.data.timings;
                this.updatePrayerTimes();
            }
        } catch (error) {
            console.log('Error fetching prayer times:', error);
        }
    }
    
    updatePrayerTimes() {
        if (!this.prayerTimes) return;
        
        const prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'];
        prayers.forEach(prayer => {
            const timeEl = document.getElementById(`${prayer.toLowerCase()}-time`);
            if (timeEl && this.prayerTimes[prayer]) {
                timeEl.textContent = this.formatTime(this.prayerTimes[prayer]);
            }
        });
        
        this.updateNextPrayer();
    }
    
    formatTime(timeString) {
        const [hours, minutes] = timeString.split(':');
        const hour12 = hours % 12 || 12;
        const ampm = hours >= 12 ? 'PM' : 'AM';
        return `${hour12}:${minutes} ${ampm}`;
    }
    
    updateNextPrayer() {
        if (!this.prayerTimes) return;
        
        const now = new Date();
        const currentTime = now.getHours() * 60 + now.getMinutes();
        
        const prayers = [
            { name: 'Fajr', time: this.prayerTimes.Fajr },
            { name: 'Dhuhr', time: this.prayerTimes.Dhuhr },
            { name: 'Asr', time: this.prayerTimes.Asr },
            { name: 'Maghrib', time: this.prayerTimes.Maghrib },
            { name: 'Isha', time: this.prayerTimes.Isha }
        ];
        
        let nextPrayer = null;
        for (const prayer of prayers) {
            const [hours, minutes] = prayer.time.split(':');
            const prayerTime = parseInt(hours) * 60 + parseInt(minutes);
            
            if (prayerTime > currentTime) {
                nextPrayer = { ...prayer, timeInMinutes: prayerTime };
                break;
            }
        }
        
        if (!nextPrayer) {
            // Next prayer is tomorrow's Fajr
            nextPrayer = { ...prayers[0], timeInMinutes: prayers[0].time.split(':').reduce((h, m) => parseInt(h) * 60 + parseInt(m)) + 24 * 60 };
        }
        
        const nextPrayerName = document.getElementById('next-prayer-name');
        if (nextPrayerName) {
            nextPrayerName.textContent = nextPrayer.name;
        }
        
        this.startCountdown(nextPrayer.timeInMinutes - currentTime);
    }
    
    startCountdown(minutesUntilPrayer) {
        const countdownEl = document.getElementById('next-prayer-countdown');
        if (!countdownEl) return;
        
        let totalMinutes = minutesUntilPrayer;
        
        const updateCountdown = () => {
            const hours = Math.floor(totalMinutes / 60);
            const minutes = totalMinutes % 60;
            const seconds = 0; // Simplified for demo
            
            countdownEl.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
            
            if (totalMinutes > 0) {
                totalMinutes--;
                setTimeout(updateCountdown, 60000); // Update every minute
            }
        };
        
        updateCountdown();
    }
    
    startPrayerTimeUpdates() {
        // Update prayer times every hour
        setInterval(() => {
            this.fetchPrayerTimes();
        }, 3600000);
    }
    
    findQiblaDirection() {
        if (!this.userLocation) {
            this.getUserLocation();
            return;
        }
        
        this.updateQiblaDirection();
    }
    
    updateQiblaDirection() {
        if (!this.userLocation) return;
        
        const qiblaDirection = this.calculateQiblaDirection(
            this.userLocation.latitude,
            this.userLocation.longitude
        );
        
        const distance = this.calculateDistanceToMecca(
            this.userLocation.latitude,
            this.userLocation.longitude
        );
        
        // Update display
        const directionEl = document.getElementById('qibla-direction');
        const distanceEl = document.getElementById('qibla-distance');
        const needle = document.getElementById('compass-needle');
        
        if (directionEl) directionEl.textContent = `${Math.round(qiblaDirection)}°`;
        if (distanceEl) distanceEl.textContent = `${Math.round(distance)} km`;
        if (needle) needle.style.transform = `translateX(-50%) rotate(${qiblaDirection}deg)`;
    }
    
    calculateQiblaDirection(lat, lng) {
        const kaabaLat = 21.4225;
        const kaabaLng = 39.8262;
        
        const dLng = (kaabaLng - lng) * Math.PI / 180;
        const lat1 = lat * Math.PI / 180;
        const lat2 = kaabaLat * Math.PI / 180;
        
        const y = Math.sin(dLng) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
        
        let bearing = Math.atan2(y, x) * 180 / Math.PI;
        return (bearing + 360) % 360;
    }
    
    calculateDistanceToMecca(lat, lng) {
        const kaabaLat = 21.4225;
        const kaabaLng = 39.8262;
        
        const R = 6371; // Earth's radius in km
        const dLat = (kaabaLat - lat) * Math.PI / 180;
        const dLng = (kaabaLng - lng) * Math.PI / 180;
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat * Math.PI / 180) * Math.cos(kaabaLat * Math.PI / 180) *
                  Math.sin(dLng/2) * Math.sin(dLng/2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    updateQiblaDisplay() {
        if (this.userLocation) {
            this.updateQiblaDirection();
        }
    }
    
    openTool(toolId) {
        // Handle tool opening - can be expanded based on specific tools
        switch(toolId) {
            case 'zakat-calculator':
                this.openZakatCalculator();
                break;
            case 'tasbih-counter':
                this.openTasbihCounter();
                break;
            case 'hijri-converter':
                this.openHijriConverter();
                break;
            case 'quran-audio':
                this.openQuranAudio();
                break;
            case 'dua-collection':
                this.openDuaCollection();
                break;
            case 'islamic-names':
                this.openIslamicNames();
                break;
        }
    }
    
    openZakatCalculator() {
        // Simple Zakat calculator modal or redirect to chat
        this.switchTab('chat');
        const input = document.getElementById('islamic-chat-input');
        if (input) {
            input.value = 'Help me calculate my Zakat obligation';
            this.sendMessage();
        }
    }
    
    openTasbihCounter() {
        // Digital Tasbih counter
        alert('🕌 Digital Tasbih Counter\n\nSubhanAllah (33)\nAlhamdulillah (33)\nAllahu Akbar (34)\n\nClick to count your dhikr!');
    }
    
    openHijriConverter() {
        this.switchTab('chat');
        const input = document.getElementById('islamic-chat-input');
        if (input) {
            input.value = 'Convert today\'s date to Hijri calendar';
            this.sendMessage();
        }
    }
    
    openQuranAudio() {
        this.switchTab('chat');
        const input = document.getElementById('islamic-chat-input');
        if (input) {
            input.value = 'I want to listen to Quran recitation';
            this.sendMessage();
        }
    }
    
    openDuaCollection() {
        this.switchTab('chat');
        const input = document.getElementById('islamic-chat-input');
        if (input) {
            input.value = 'Show me daily Islamic duas and supplications';
            this.sendMessage();
        }
    }
    
    openIslamicNames() {
        this.switchTab('chat');
        const input = document.getElementById('islamic-chat-input');
        if (input) {
            input.value = 'Suggest beautiful Islamic names with meanings';
            this.sendMessage();
        }
    }
    
    addWelcomeMessage() {
        const welcomeMessage = {
            id: 'welcome',
            text: `السلام عليكم ورحمة الله وبركاته

Welcome to your Islamic AI Assistant! I'm here to help you with:

🕐 Prayer times and guidance
📖 Quran verses and meanings  
⭐ Authentic Hadith
🤲 Duas for all occasions
🧭 Qibla direction
👨‍🏫 Scholar consultation

How can I assist you today?`,
            sender: 'agent',
            timestamp: new Date(),
            type: 'greeting'
        };
        
        this.messages.push(welcomeMessage);
        this.renderMessage(welcomeMessage);
    }
    
    async sendMessage() {
        const input = document.getElementById('islamic-chat-input');
        const send = document.getElementById('islamic-chat-send');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        const userMessage = {
            id: Date.now(),
            text: message,
            sender: 'user',
            timestamp: new Date(),
            type: 'user'
        };
        
        this.messages.push(userMessage);
        this.renderMessage(userMessage);
        
        // Clear input and disable send button
        input.value = '';
        input.style.height = 'auto';
        send.disabled = true;
        
        // Show typing indicator
        const typingId = this.showTyping();
        
        try {
            if (this.config.debug) {
                console.log('[DEBUG] Sending message:', message);
            }
            
            // Get AI response
            const response = await this.getAIResponse(message);
            
            if (this.config.debug) {
                console.log('[DEBUG] Received response:', response);
            }
            
            // Remove typing indicator
            this.hideTyping(typingId);
            
            // Add AI response
            const aiMessage = {
                id: Date.now() + 1,
                text: response.text,
                sender: 'agent',
                timestamp: new Date(),
                type: response.type || 'response',
                isError: response.type === 'error',
                ...response // Spread any additional properties (arabic, translation, reference, etc.)
            };
            
            this.messages.push(aiMessage);
            this.renderMessage(aiMessage);
            
            // Auto-scroll to bottom after a short delay to ensure rendering is complete
            setTimeout(() => {
                const chatBody = document.getElementById('islamic-chat-body');
                if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
            }, 100);
            
        } catch (error) {
            console.error('Error getting AI response:', error);
            
            // Remove typing indicator
            this.hideTyping(typingId);
            
            // Format error message with Islamic phrases
            let errorText = `
                <div style="margin-bottom: 8px;">
                    <span style="color: #e74c3c;">❌ </span>
                    <strong>Astaghfirullah</strong> - I apologize for the inconvenience.
                </div>
                <div style="margin-bottom: 8px;">
            `;
            
            if (error.message.includes('Failed to fetch')) {
                errorText += 'I\'m having trouble connecting to the server. Please check your internet connection and try again.';
            } else if (error.message.includes('timeout') || error.message.includes('timed out')) {
                errorText += 'The request is taking longer than expected. Please try again in a moment.';
            } else if (error.message.includes('500') || error.message.includes('server')) {
                errorText += 'The server is currently unavailable. Please try again later or contact support if the issue persists.';
            } else {
                errorText += 'An unexpected error occurred while processing your request.';
            }
            
            errorText += `
                </div>
                <div style="font-size: 0.9em; color: #7f8c8d; font-style: italic;">
                    <em>Bismillah, please try again or ask a different question.</em>
                </div>
            `;
            
            const errorMessage = {
                id: Date.now() + 2,
                text: errorText,
                sender: 'agent',
                timestamp: new Date(),
                type: 'error',
                isError: true
            };
            
            this.messages.push(errorMessage);
            this.renderMessage(errorMessage);
        } finally {
            // Re-enable send button
            send.disabled = false;
            input.focus();
        }
    }
    
    async getAIResponse(message) {
        // Determine which endpoint to use based on search mode
        let endpoint = '/api/chat';
        let requestBody = {
            message: message,
            mode: this.searchMode || 'general',
            timestamp: new Date().toISOString()
        };

        // Add debug info if enabled
        if (this.config.debug) {
            console.log(`[DEBUG] Sending message to ${this.config.apiUrl}${endpoint}:`, requestBody);
        }
        
        // Special handling for different search modes
        if (this.searchMode === 'quran') {
            // Use the dynamic knowledge base for Quran queries
            endpoint = '/api/quran';
            requestBody = {
                verse: message,
                include_translations: true,
                include_tafsir: true
            };
        } else if (this.searchMode === 'hadith') {
            // Use the dynamic knowledge base for Hadith queries
            endpoint = '/api/hadith';
            requestBody = {
                topic: message,
                collection: 'bukhari,muslim',
                include_arabic: true,
                include_english: true
            };
        } else if (this.searchMode === 'scholar') {
            endpoint = '/api/scholar';
            requestBody = {
                message: message,  // Changed from 'query' to 'message' to match backend expectation
                scholar_type: 'auto',  // Let the backend decide the best scholar
                response_format: 'detailed',
                include_sources: true,
                include_arabic: true
            };
        }
        
        // Create a controller for the fetch request to support timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout || 30000);
        
        try {
            if (this.config.debug) {
                console.log(`[DEBUG] Sending request to: ${this.config.apiUrl}${endpoint}`);
                console.log('[DEBUG] Request body:', requestBody);
            }
            
            // Ensure the URL is properly formatted
            const apiUrl = `${this.config.apiUrl}${endpoint}`.replace(/([^:]\/)\/+/g, '$1');
            
            if (this.config.debug) {
                console.log(`[DEBUG] Full API URL: ${apiUrl}`);
                console.log('[DEBUG] Request headers:', {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                });
            }
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                mode: 'cors',
                cache: 'no-cache',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                redirect: 'follow',
                referrerPolicy: 'no-referrer',
                body: JSON.stringify(requestBody),
                signal: controller.signal
            });
            
            if (this.config.debug) {
                console.log('[DEBUG] Response status:', response.status, response.statusText);
                console.log('[DEBUG] Response headers:', [...response.headers.entries()]);
            }
            
            // Clear the timeout since the request completed
            clearTimeout(timeoutId);
            
            if (this.config.debug) {
                console.log(`[DEBUG] Response status: ${response.status} ${response.statusText}`);
            }
            
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                    console.error(`[ERROR] API Error: ${response.status} - ${JSON.stringify(errorData)}`);
                } catch (e) {
                    errorData = { error: response.statusText };
                }
                
                // Return a more specific error message based on the status code
                if (response.status >= 500) {
                    throw new Error('The server encountered an error. Please try again later.');
                } else if (response.status === 404) {
                    throw new Error('The requested resource was not found.');
                } else if (response.status === 401) {
                    throw new Error('Session expired. Please refresh the page and try again.');
                } else if (response.status === 429) {
                    throw new Error('Too many requests. Please wait a moment before trying again.');
                } else {
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
            }
            
            const data = await response.json();
            
            if (this.config.debug) {
                console.log('[DEBUG] Response data:', data);
            }
            
            // Handle different response formats from the backend
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Format the response based on the content type
            let formattedResponse = {
                text: '',
                type: 'response',
                timestamp: new Date().toISOString(),
                source: 'Islamic AI Agent',
                metadata: {},
                references: []
            };
            
            // Handle different response formats from different endpoints
            if (data.response) {
                // Standard response format from /api/chat
                formattedResponse.text = data.response;
                
                // Add metadata if available
                if (data.metadata) {
                    formattedResponse.metadata = data.metadata;
                    
                    // Add source information
                    if (data.metadata.source) {
                        formattedResponse.source = data.metadata.source;
                    }
                    
                    // Add references if available
                    if (data.metadata.references) {
                        formattedResponse.references = Array.isArray(data.metadata.references) 
                            ? data.metadata.references 
                            : [data.metadata.references];
                    }
                    
                    // Add Arabic text if available
                    if (data.metadata.arabic) {
                        formattedResponse.arabic = data.metadata.arabic;
                    }
                }
                
                // Special handling for different content types
                if (data.content_type === 'quran' || this.searchMode === 'quran') {
                    formattedResponse.type = 'quran';
                    formattedResponse.surah = data.surah || data.metadata?.surah || '';
                    formattedResponse.ayah = data.ayah || data.metadata?.ayah || '';
                    
                    // Format Quran verse with Arabic and translation
                    if (data.arabic) {
                        formattedResponse.arabic = data.arabic;
                        formattedResponse.text = `${data.translation || data.response}\n\n(${data.surah}:${data.ayah})`;
                    }
                } 
                else if (data.content_type === 'hadith' || this.searchMode === 'hadith') {
                    formattedResponse.type = 'hadith';
                    formattedResponse.collection = data.collection || data.metadata?.collection || 'Sahih';
                    formattedResponse.grade = data.grade || data.metadata?.grade || 'Sahih';
                    formattedResponse.narrator = data.narrator || data.metadata?.narrator || '';
                    
                    // Format Hadith with Arabic and reference
                    if (data.arabic) {
                        formattedResponse.arabic = data.arabic;
                        formattedResponse.text = `${data.english || data.response}\n\n(${formattedResponse.collection}, ${formattedResponse.grade})`;
                        
                        if (data.reference) {
                            formattedResponse.references.push(data.reference);
                        }
                    }
                }
                else if (data.content_type === 'fiqh' || data.type === 'fiqh') {
                    formattedResponse.type = 'fiqh';
                    formattedResponse.madhab = data.madhab || data.metadata?.madhab || 'General';
                    
                    // Format Fiqh ruling with references
                    if (data.ruling) {
                        formattedResponse.text = data.ruling;
                        if (data.evidence) {
                            formattedResponse.text += `\n\nEvidence: ${data.evidence}`;
                            formattedResponse.references.push(data.evidence);
                        }
                    }
                }
                
                return formattedResponse;
            } 
            // Handle direct text responses
            else if (typeof data === 'string') {
                formattedResponse.text = data;
                return formattedResponse;
            }
            // Handle error responses
            else if (data.error) {
                throw new Error(data.error);
            } 
            // Handle unknown response format
            else {
                console.warn('Unexpected response format:', data);
                formattedResponse.text = 'Received an unexpected response format. Please try again.';
                formattedResponse.type = 'error';
                return formattedResponse;
            }
            
            // Fallback to direct response or message
            return {
                text: data.message || 'No response received',
                type: this.searchMode === 'normal' ? 'response' : this.searchMode,
                raw: data,
                agent: data.agent || 'Islamic AI Assistant',
                timestamp: data.timestamp || new Date().toISOString()
            };
            
        } catch (error) {
            clearTimeout(timeoutId); // Clear timeout in case of other errors
            
            if (error.name === 'AbortError') {
                console.error('[ERROR] Request timed out');
                return {
                    text: this.config.fallbackResponses?.timeout || 'The request timed out. Please try again.',
                    type: 'error'
                };
            } else if (error.message === 'Failed to fetch') {
                console.error('[ERROR] Network error - Failed to connect to the server');
                return {
                    text: this.config.fallbackResponses?.network_error || 'Unable to connect to the server. Please check your internet connection.',
                    type: 'error'
                };
            } else {
                console.error('[ERROR] Unexpected error:', error);
                return {
                    text: this.config.fallbackResponses?.default || 'An unexpected error occurred. Please try again.',
                    type: 'error'
                };
            }
        }
    }
    
    detectIntent(message) {
        const lowerMsg = message.toLowerCase();
        
        if (lowerMsg.includes('prayer') || lowerMsg.includes('salah') || lowerMsg.includes('namaz')) {
            return 'prayer';
        } else if (lowerMsg.includes('quran') || lowerMsg.includes('verse') || lowerMsg.includes('surah')) {
            return 'quran';
        } else if (lowerMsg.includes('hadith') || lowerMsg.includes('prophet') || lowerMsg.includes('sunnah')) {
            return 'hadith';
        } else if (lowerMsg.includes('dua') || lowerMsg.includes('supplication')) {
            return 'dua';
        } else if (lowerMsg.includes('halal') || lowerMsg.includes('haram') || lowerMsg.includes('fiqh')) {
            return 'fiqh';
        }
        
        return 'general';
    }
    
    renderMessage(message) {
        const messagesContainer = document.getElementById('islamic-chat-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `islamic-message ${message.sender} ${message.type || ''}`;
        
        // Format timestamp
        const timestamp = message.timestamp ? new Date(message.timestamp) : new Date();
        const formattedTime = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Badge for message type
        let badge = '';
        if (message.sender === 'agent' && message.type && message.type !== 'response') {
            const badges = {
                quran: '📖 Quran',
                hadith: '⭐ Hadith',
                fiqh: '⚖️ Fiqh Ruling',
                scholar: '👨‍🏫 Scholar',
                error: '⚠️ Error',
                greeting: '👋 Welcome'
            };
            if (badges[message.type]) {
                badge = `<div class="islamic-message-badge ${message.type}">${badges[message.type]}</div>`;
            }
        }
        
        // Determine if this is an error message
        const isErrorMessage = message.type === 'error' || message.isError;
        const messageContentClass = isErrorMessage ? 'islamic-message-content error-message' : 'islamic-message-content';
        
        // Format message content based on type
        let messageContent = message.text;
        
        // Special formatting for Quran verses
        if (message.type === 'quran') {
            const surahAyah = message.surah && message.ayah ? 
                `<div class="quran-reference">Surah ${message.surah}, Ayah ${message.ayah}</div>` : '';
            
            messageContent = `
                <div class="quran-verse">
                    ${message.arabic ? `<div class="arabic-text" dir="rtl">${message.arabic}</div>` : ''}
                    <div class="translation">${message.text}</div>
                    ${surahAyah}
                </div>
            `;
        }
        // Special formatting for Hadith
        else if (message.type === 'hadith') {
            const narrator = message.narrator ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Narrator:</span>
                    <span class="hadith-meta-value">${message.narrator}</span>
                </div>` : '';
                
            const reference = message.reference ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Reference:</span>
                    <span class="hadith-meta-value">${message.reference}</span>
                </div>` : (message.collection ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Reference:</span>
                    <span class="hadith-meta-value">${message.collection}${message.book ? `, Book ${message.book}` : ''}${message.hadithNumber ? `, Hadith ${message.hadithNumber}` : ''}</span>
                </div>` : '');
                
            const chapter = message.chapter ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Chapter:</span>
                    <span class="hadith-meta-value">${message.chapter}</span>
                </div>` : '';
                
            const grade = message.grade ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Grade:</span>
                    <span class="hadith-meta-value">${message.grade}</span>
                </div>` : '';
                
            const topic = message.topic ? `
                <div class="hadith-meta-item">
                    <span class="hadith-meta-label">Topic:</span>
                    <span class="hadith-meta-value">${message.topic}</span>
                </div>` : '';
            
            messageContent = `
                <div class="hadith-card">
                    <div class="hadith-header">
                        <div class="hadith-title">
                            <i class="fas fa-star"></i> Authentic Hadith
                        </div>
                    </div>
                    <div class="hadith-text">
                        ${message.text}
                        ${message.arabic ? `<div class="arabic-text" dir="rtl" style="text-align: right; font-size: 1.2em; margin: 15px 0; color: #1a365d; line-height: 1.8;">${message.arabic}</div>` : ''}
                    </div>
                    <div class="hadith-meta">
                        ${narrator}
                        ${reference}
                        ${chapter}
                        ${grade}
                        ${topic}
                    </div>
                    ${message.authenticity ? `
                    <div class="hadith-authenticity">
                        <i class="fas fa-check-circle"></i> ${message.authenticity}
                    </div>` : ''}
                    ${message.source ? `
                    <div class="hadith-source">
                        <i class="fas fa-book"></i> Source: ${message.source}
                    </div>` : ''}
                </div>
            `;
        }
        // Special formatting for Fiqh rulings
        else if (message.type === 'fiqh') {
            const madhabInfo = message.madhab ? 
                `<div class="fiqh-madhab">Madhab: ${message.madhab}</div>` : '';
            
            messageContent = `
                <div class="fiqh-ruling">
                    <div class="fiqh-text">${message.text}</div>
                    ${madhabInfo}
                </div>
            `;
        }
        
        // Add references if available
        let referencesHtml = '';
        if (message.references && Array.isArray(message.references) && message.references.length > 0) {
            referencesHtml = `
                <div class="islamic-references">
                    <div class="references-title">References:</div>
                    <ul class="references-list">
                        ${message.references.map(ref => `<li>${ref}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Add source information
        const sourceInfo = message.source ? 
            `<div class="message-source">Source: ${message.source}</div>` : '';
            
        // Add timestamp
        const timestampHtml = `
            <div class="message-timestamp">
                ${formattedTime}
            </div>
        `;
        
        // Add agent information if available
        const agentInfo = message.agent ? 
            `<div class="islamic-message-agent">
                <small>${message.agent}</small>
            </div>` : '';
            
        messageElement.innerHTML = `
            <div class="islamic-message-avatar">
                ${message.sender === 'agent' ? '🕌' : '👤'}
            </div>
            <div class="${messageContentClass}">
                ${isErrorMessage ? '⚠️ ' : ''}${badge}
                <div class="message-text">${messageContent}</div>
                ${referencesHtml}
                <div class="message-footer">
                    ${sourceInfo}
                    ${timestampHtml}
                </div>
                ${message.sender === 'agent' ? agentInfo : ''}
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTyping() {
        const messagesContainer = document.getElementById('islamic-chat-messages');
        const typingElement = document.createElement('div');
        typingElement.className = 'islamic-message agent';
        typingElement.id = 'islamic-typing-indicator';
        typingElement.innerHTML = `
            <div class="islamic-message-avatar">🕌</div>
            <div class="islamic-message-content">
                <div class="islamic-typing">
                    <span>Islamic AI is typing</span>
                    <div class="islamic-typing-dots">
                        <div class="islamic-typing-dot"></div>
                        <div class="islamic-typing-dot"></div>
                        <div class="islamic-typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTyping() {
        const typingElement = document.getElementById('islamic-typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
}

// Auto-initialize if config is provided
if (typeof window !== 'undefined' && window.IslamicChatConfig) {
    new IslamicChatWidget(window.IslamicChatConfig);
}

// Export for manual initialization
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IslamicChatWidget;
} else if (typeof window !== 'undefined') {
    window.IslamicChatWidget = IslamicChatWidget;
}
