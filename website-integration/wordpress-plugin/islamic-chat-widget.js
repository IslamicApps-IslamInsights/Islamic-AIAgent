/**
 * Islamic AI Agent Chat Widget for theislaminsights.com
 * Embeddable chat interface that connects to your Islamic AI backend
 */

class IslamicChatWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:5002',
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
        this.addWelcomeMessage();
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
            
            .islamic-message.user .islamic-message-avatar {
                background: #e0e0e0;
                color: #666;
            }
            
            .islamic-message-content {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.4;
                white-space: pre-wrap;
            }
            
            .islamic-message.agent .islamic-message-content {
                background: white;
                color: #333;
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
                background: #fff3cd;
                color: #856404;
            }
            
            .islamic-message-badge.scholar {
                background: #f8d7da;
                color: #721c24;
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
            
            @media (max-width: 480px) {
                .islamic-chat-container {
                    width: calc(100vw - 40px);
                    height: calc(100vh - 100px);
                    bottom: 80px;
                    right: 20px;
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
                    <h3 class="islamic-chat-title">
                        🕌 ${this.config.title}
                    </h3>
                    <p class="islamic-chat-subtitle">${this.config.subtitle}</p>
                </div>
                
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
        `;
        
        document.body.appendChild(widget);
        this.widget = widget;
    }
    
    attachEventListeners() {
        const toggle = document.getElementById('islamic-chat-toggle');
        const close = document.getElementById('islamic-chat-close');
        const input = document.getElementById('islamic-chat-input');
        const send = document.getElementById('islamic-chat-send');
        const searchModes = document.querySelectorAll('.islamic-search-mode');
        
        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.closeChat());
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
        this.showTyping();
        
        try {
            // Get AI response
            const response = await this.getAIResponse(message);
            
            // Add AI response
            const aiMessage = {
                id: Date.now() + 1,
                text: response.text,
                sender: 'agent',
                timestamp: new Date(),
                type: response.type || 'response'
            };
            
            this.messages.push(aiMessage);
            this.renderMessage(aiMessage);
            
        } catch (error) {
            console.error('Error getting AI response:', error);
            
            const errorMessage = {
                id: Date.now() + 2,
                text: "I apologize, but I'm having trouble processing your request right now. Please try again or ask a different question.",
                sender: 'agent',
                timestamp: new Date(),
                type: 'error'
            };
            
            this.messages.push(errorMessage);
            this.renderMessage(errorMessage);
        }
        
        // Hide typing indicator and re-enable send button
        this.hideTyping();
        send.disabled = false;
        input.focus();
    }
    
    async getAIResponse(message) {
        let endpoint = '/api/chat';
        let body = {
            message: message,
            intent: this.detectIntent(message),
            user_preferences: {}
        };
        
        // Route based on search mode
        if (this.searchMode === 'quran') {
            body.message = `[QURAN SEARCH] ${message}`;
            body.intent = 'quran';
        } else if (this.searchMode === 'hadith') {
            body.message = `[HADITH SEARCH] ${message}`;
            body.intent = 'hadith';
        } else if (this.searchMode === 'scholar') {
            endpoint = '/api/scholar';
            body = {
                message: message,
                scholar_type: null,
                consultation_type: 'single'
            };
        }
        
        const response = await fetch(`${this.config.apiUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        return {
            text: data.response || data.message || 'No response received',
            type: this.searchMode === 'normal' ? 'response' : this.searchMode
        };
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
        messageElement.className = `islamic-message ${message.sender}`;
        
        let badge = '';
        if (message.sender === 'agent' && message.type && message.type !== 'greeting' && message.type !== 'response') {
            const badges = {
                quran: '📖 Quran Search',
                hadith: '⭐ Hadith Search',
                scholar: '👨‍🏫 Scholar Consultation'
            };
            if (badges[message.type]) {
                badge = `<div class="islamic-message-badge ${message.type}">${badges[message.type]}</div>`;
            }
        }
        
        messageElement.innerHTML = `
            <div class="islamic-message-avatar">
                ${message.sender === 'agent' ? '🕌' : '👤'}
            </div>
            <div class="islamic-message-content">
                ${badge}
                ${message.text}
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
