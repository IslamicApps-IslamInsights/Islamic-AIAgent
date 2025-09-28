// Islamic AI Agent - Frontend JavaScript

class IslamicAIApp {
    constructor() {
        this.currentAgent = 'single';
        this.userLocation = null;
        this.isVoiceInputActive = false;
        this.init();
    }

    init() {
        this.loadHijriDate();
        this.setupEventListeners();
        this.checkAgentStatus();
        
        // Load user location if available
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    console.log('Location loaded:', this.userLocation);
                },
                (error) => {
                    console.log('Location access denied or unavailable');
                }
            );
        }
    }

    setupEventListeners() {
        // Enter key for message input
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.agent_initialized) {
                this.addMessage('🌟 Islamic AI Agent is ready to help you!', 'agent');
            } else {
                this.addMessage('⚠️ AI Agent is initializing... Attempting to initialize now.', 'agent');
                await this.initializeAgents();
            }
        } catch (error) {
            this.addMessage('❌ Unable to connect to the AI service. Please refresh the page.', 'agent');
        }
    }

    updateAgentStatus(status) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = statusIndicator.querySelector('span');
        
        switch (status) {
            case 'online':
                statusIndicator.className = 'status-indicator online';
                statusText.textContent = 'Online';
                break;
            case 'initializing':
                statusIndicator.className = 'status-indicator initializing';
                statusText.textContent = 'Initializing...';
                break;
            case 'offline':
                statusIndicator.className = 'status-indicator offline';
                statusText.textContent = 'Offline';
                break;
        }
    }

    async initializeAgents() {
        try {
            this.showLoading();
            const response = await fetch('/api/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            this.hideLoading();
            
            if (data.agent_initialized) {
                this.addMessage('✅ AI Agents initialized successfully! You can now chat with the Islamic AI.', 'agent');
            } else {
                this.addMessage('❌ Failed to initialize AI agents. Please refresh the page and try again.', 'agent');
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error initializing agents: ${error.message}`, 'agent');
        }
    }

    async loadHijriDate() {
        try {
            const response = await fetch('/api/hijri-date');
            const data = await response.json();
            
            // Extract just the date part from the response
            const hijriText = data.hijri_date;
            const dateMatch = hijriText.match(/🌙 \*\*(.+?)\*\*/);
            if (dateMatch) {
                document.getElementById('hijriDate').textContent = dateMatch[1];
            } else {
                document.getElementById('hijriDate').textContent = 'Loading...';
            }
        } catch (error) {
            document.getElementById('hijriDate').textContent = 'Error loading date';
        }
    }

    async checkAgentStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.status === 'healthy' && data.agents_ready) {
                console.log('✅ Agents are ready');
            } else {
                console.log('⚠️ Agents may not be fully ready');
            }
        } catch (error) {
            console.log('❌ Error checking agent status:', error.message);
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input and show user message
        messageInput.value = '';
        this.addMessage(message, 'user');
        this.showTypingIndicator();

        try {
            let response;
            
            if (this.currentAgent === 'single') {
                response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });
            } else {
                response = await fetch('/api/multi-chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        message,
                        specialist: this.currentAgent 
                    })
                });
            }

            const data = await response.json();
            
            if (response.ok) {
                this.hideTypingIndicator();
                
                // Update agent name if using multi-agent
                if (data.specialist) {
                    this.updateCurrentAgent(data.specialist);
                }
                
                this.addMessage(data.response, 'agent');
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage(`❌ Error: ${error.message}`, 'agent');
        }
    }

    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const avatarIcon = sender === 'user' ? 'fa-user' : 'fa-mosque';
        const senderName = sender === 'user' ? 'You' : this.getCurrentAgentName();

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${senderName}</span>
                    <span class="message-time">${currentTime}</span>
                </div>
                <div class="message-text">
                    ${this.formatMessage(content)}
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMessage(content) {
        // Format headers and bold text
        content = content.replace(/\*\*Arabic:\*\*/g, '<div class="content-header"><strong>🕌 Arabic:</strong></div>');
        content = content.replace(/\*\*Translation.*?:\*\*/g, '<div class="content-header"><strong>📖 Translation:</strong></div>');
        content = content.replace(/\*\*Reference:\*\*/g, '<div class="content-header"><strong>📚 Reference:</strong></div>');
        content = content.replace(/\*\*Surah.*?:\*\*/g, '<div class="surah-header"><strong>$&</strong></div>');
        content = content.replace(/\*\*Verse.*?:\*\*/g, '<div class="verse-header"><strong>$&</strong></div>');
        content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Format line breaks
        content = content.replace(/\n\n/g, '</p><p>');
        content = content.replace(/\n/g, '<br>');
        content = '<p>' + content + '</p>';
        
        // Enhanced Arabic text formatting
        content = content.replace(/([\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s]+)/g, 
            function(match) {
                // Only apply Arabic styling to substantial Arabic text (more than 3 characters)
                if (match.trim().length > 3) {
                    return '<div class="arabic-text">' + match.trim() + '</div>';
                }
                return match;
            });
        
        // Format Quran verses specially
        if (content.includes('📖') && content.includes('Arabic:')) {
            content = '<div class="quran-verse">' + content + '</div>';
        }
        
        // Format Hadith specially
        if (content.includes('⭐') && content.includes('Hadith')) {
            content = '<div class="hadith-text">' + content + '</div>';
        }
        
        // Format Prayer times specially
        if (content.includes('🕐') && content.includes('Prayer Times')) {
            content = '<div class="prayer-times">' + content + '</div>';
        }
        
        // Format Next Prayer specially
        if (content.includes('⏰') && content.includes('Next Prayer:')) {
            content = content.replace(/(⏰ \*\*Next Prayer:\*\* .+?)(<br>|$)/g, 
                '<div class="next-prayer">$1</div>$2');
        }
        
        // Format Hijri Date specially
        if (content.includes('📅') && content.includes('Islamic Date:')) {
            content = content.replace(/(📅 \*\*Islamic Date:\*\* .+?)(<br>|$)/g, 
                '<div class="hijri-date">$1</div>$2');
        }
        
        return content;
    }

    getCurrentAgentName() {
        const agentNames = {
            'single': 'Noor',
            'auto': 'Islamic AI Team',
            'quran': 'Sheikh Abdullah',
            'hadith': 'Sheikh Aisha', 
            'fiqh': 'Sheikh Omar',
            'spiritual': 'Sheikh Fatima'
        };
        return agentNames[this.currentAgent] || 'Noor';
    }

    updateCurrentAgent(specialistName) {
        document.getElementById('currentAgentName').textContent = specialistName;
        document.getElementById('currentAgentRole').textContent = 'Islamic Specialist';
    }

    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'flex';
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }

    // Tool Functions
    async getQuranVerse() {
        const verseInput = document.getElementById('verseInput').value.trim();
        if (!verseInput) {
            alert('Please enter a verse reference');
            return;
        }

        this.closeModal('quranModal');
        this.showLoading();

        try {
            const response = await fetch('/api/quran', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ verse: verseInput })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.verse, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching verse: ${error.message}`, 'agent');
        }

        document.getElementById('verseInput').value = '';
    }

    async getHadithByTopic() {
        const topic = document.getElementById('hadithTopicInput').value.trim();
        
        this.closeModal('hadithModal');
        this.showLoading();

        try {
            const response = await fetch('/api/hadith', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic: topic || null })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.hadith, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching hadith: ${error.message}`, 'agent');
        }

        document.getElementById('hadithTopicInput').value = '';
    }

    async getRandomHadith() {
        this.showLoading();

        try {
            const response = await fetch('/api/hadith', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic: null })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.hadith, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching hadith: ${error.message}`, 'agent');
        }
    }

    async getPrayerTimes() {
        if (!this.userLocation) {
            this.addMessage('📍 Please share your location first by clicking the location button or allowing location access.', 'agent');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/prayer-times', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.userLocation)
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.prayer_times, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching prayer times: ${error.message}`, 'agent');
        }
    }

    async getQiblaDirection() {
        if (!this.userLocation) {
            this.addMessage('📍 Please share your location first by clicking the location button or allowing location access.', 'agent');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/qibla', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.userLocation)
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.qibla_direction, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching Qibla direction: ${error.message}`, 'agent');
        }
    }

    async getDuaByOccasion() {
        const occasion = document.getElementById('duaOccasionSelect').value;
        
        this.closeModal('duaModal');
        this.showLoading();

        try {
            const response = await fetch('/api/dua', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ occasion })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.dua, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching dua: ${error.message}`, 'agent');
        }
    }

    async getDailyContent() {
        this.showLoading();

        try {
            const response = await fetch('/api/daily-content');
            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.daily_content, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching daily content: ${error.message}`, 'agent');
        }
    }

    async getGuidanceByTopic() {
        const topic = document.getElementById('guidanceTopicInput').value.trim();
        if (!topic) {
            alert('Please enter a topic');
            return;
        }

        this.closeModal('guidanceModal');
        this.showLoading();

        try {
            const response = await fetch('/api/guidance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.guidance, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching guidance: ${error.message}`, 'agent');
        }

        document.getElementById('guidanceTopicInput').value = '';
    }

    async performSearch() {
        const query = document.getElementById('searchQueryInput').value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }

        this.closeModal('searchModal');
        this.showLoading();

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.search_results, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error searching: ${error.message}`, 'agent');
        }

        document.getElementById('searchQueryInput').value = '';
    }

    // UI Helper Functions
    showModal(modalId) {
        document.getElementById(modalId).style.display = 'block';
    }

    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    changeAgent() {
        const select = document.getElementById('agentSelect');
        this.currentAgent = select.value;
        
        const agentNames = {
            'single': 'Noor',
            'auto': 'Islamic AI Team',
            'quran': 'Sheikh Abdullah',
            'hadith': 'Sheikh Aisha',
            'fiqh': 'Sheikh Omar',
            'spiritual': 'Sheikh Fatima'
        };

        const agentRoles = {
            'single': 'Islamic AI Assistant',
            'auto': 'Auto-Routing Specialists',
            'quran': 'Quran & Tafsir Specialist',
            'hadith': 'Hadith & Sunnah Expert',
            'fiqh': 'Fiqh & Islamic Law Scholar',
            'spiritual': 'Spiritual Guidance & Duas'
        };

        document.getElementById('currentAgentName').textContent = agentNames[this.currentAgent];
        document.getElementById('currentAgentRole').textContent = agentRoles[this.currentAgent];
    }

    getLocation() {
        if (!navigator.geolocation) {
            this.addMessage('❌ Geolocation is not supported by this browser.', 'agent');
            return;
        }

        this.showLoading();
        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                this.hideLoading();
                this.addMessage(`📍 Location updated! You can now get prayer times and Qibla direction.`, 'agent');
            },
            (error) => {
                this.hideLoading();
                this.addMessage(`❌ Error getting location: ${error.message}`, 'agent');
            }
        );
    }

    toggleVoiceInput() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.addMessage('❌ Speech recognition is not supported in this browser.', 'agent');
            return;
        }

        if (this.isVoiceInputActive) {
            this.stopVoiceInput();
        } else {
            this.startVoiceInput();
        }
    }

    startVoiceInput() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            this.isVoiceInputActive = true;
            this.addMessage('🎤 Listening... Speak your question.', 'agent');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('messageInput').value = transcript;
            this.isVoiceInputActive = false;
        };

        recognition.onerror = (event) => {
            this.isVoiceInputActive = false;
            this.addMessage(`❌ Speech recognition error: ${event.error}`, 'agent');
        };

        recognition.onend = () => {
            this.isVoiceInputActive = false;
        };

        recognition.start();
    }

    stopVoiceInput() {
        this.isVoiceInputActive = false;
    }

    sendSuggestion(suggestion) {
        document.getElementById('messageInput').value = suggestion;
        this.sendMessage();
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        // Keep only the welcome message
        const welcomeMessage = chatMessages.querySelector('.message');
        chatMessages.innerHTML = '';
        chatMessages.appendChild(welcomeMessage);
    }

    exportChat() {
        const messages = document.querySelectorAll('.message');
        let chatText = 'Islamic AI Agent Chat Export\n';
        chatText += '================================\n\n';

        messages.forEach(message => {
            const sender = message.querySelector('.sender-name').textContent;
            const time = message.querySelector('.message-time').textContent;
            const content = message.querySelector('.message-text').textContent;
            
            chatText += `${sender} (${time}):\n${content}\n\n`;
        });

        const blob = new Blob([chatText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `islamic-ai-chat-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async getRandomHadith() {
        this.showLoading();
        try {
            const response = await fetch('/api/hadith/random', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.hadith, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching random hadith: ${error.message}`, 'agent');
        }
    }

    async getPrayerTimes() {
        if (!this.userLocation) {
            this.addMessage('📍 Please share your location first to get prayer times.', 'agent');
            return;
        }

        this.showLoading();
        try {
            const response = await fetch('/api/prayer-times', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: this.userLocation.latitude,
                    longitude: this.userLocation.longitude
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.prayer_times, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching prayer times: ${error.message}`, 'agent');
        }
    }

    async getQiblaDirection() {
        if (!this.userLocation) {
            this.addMessage('📍 Please share your location first to get Qibla direction.', 'agent');
            return;
        }

        this.showLoading();
        try {
            const response = await fetch('/api/qibla', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: this.userLocation.latitude,
                    longitude: this.userLocation.longitude
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.qibla_direction, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching Qibla direction: ${error.message}`, 'agent');
        }
    }

    async getDailyContent() {
        this.showLoading();
        try {
            const response = await fetch('/api/daily-content');
            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.daily_content, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching daily content: ${error.message}`, 'agent');
        }
    }

    searchContent(type) {
        const query = prompt(`Enter your search query for ${type}:`);
        if (query) {
            this.sendMessage(`Search ${type}: ${query}`);
        }
    }
}

// Global functions for HTML onclick events with enhanced safety checks
function showQuranModal() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('quranModal'); 
    else console.warn('App not ready for showQuranModal'); 
}
function showHadithModal() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('hadithModal'); 
    else console.warn('App not ready for showHadithModal'); 
}
function showDuaModal() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('duaModal'); 
    else console.warn('App not ready for showDuaModal'); 
}
function showGuidanceModal() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('guidanceModal'); 
    else console.warn('App not ready for showGuidanceModal'); 
}
function showSearchModal() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('searchModal'); 
    else console.warn('App not ready for showSearchModal'); 
}
function closeModal(modalId) { 
    if (app && app.closeModal) app.closeModal(modalId); 
    else console.warn('App not ready for closeModal'); 
}
function getQuranVerse() { 
    if (app && app.getQuranVerse) app.getQuranVerse(); 
    else console.warn('App not ready for getQuranVerse'); 
}
function getHadithByTopic() { 
    if (app && app.getHadithByTopic) app.getHadithByTopic(); 
    else console.warn('App not ready for getHadithByTopic'); 
}
function getRandomHadith() { 
    if (app && app.getRandomHadith) app.getRandomHadith(); 
    else console.warn('App not ready for getRandomHadith'); 
}
function getPrayerTimes() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.getPrayerTimes) appInstance.getPrayerTimes(); 
    else console.warn('App not ready for getPrayerTimes'); 
}
function getQiblaDirection() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.getQiblaDirection) appInstance.getQiblaDirection(); 
    else console.warn('App not ready for getQiblaDirection'); 
}
function getDuaByOccasion() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.getDuaByOccasion) appInstance.getDuaByOccasion(); 
    else console.warn('App not ready for getDuaByOccasion'); 
}
function getDailyContent() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.getDailyContent) appInstance.getDailyContent(); 
    else console.warn('App not ready for getDailyContent'); 
}
function getGuidanceByTopic() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.getGuidanceByTopic) appInstance.getGuidanceByTopic(); 
    else console.warn('App not ready for getGuidanceByTopic'); 
}
function performSearch() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.performSearch) appInstance.performSearch(); 
    else console.warn('App not ready for performSearch'); 
}
function changeAgent() { 
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.changeAgent) appInstance.changeAgent(); 
    else console.warn('App not ready for changeAgent'); 
}
function getLocation() { 
    if (app && app.getLocation) app.getLocation(); 
    else console.warn('App not ready for getLocation'); 
}
function toggleVoiceInput() { 
    if (app && app.toggleVoiceInput) app.toggleVoiceInput(); 
    else console.warn('App not ready for toggleVoiceInput'); 
}
function sendSuggestion(suggestion) { 
    if (app && app.sendSuggestion) app.sendSuggestion(suggestion); 
    else console.warn('App not ready for sendSuggestion'); 
}
function clearChat() { 
    if (app && app.clearChat) app.clearChat(); 
    else console.warn('App not ready for clearChat'); 
}
function exportChat() { 
    if (app && app.exportChat) app.exportChat(); 
    else console.warn('App not ready for exportChat'); 
}
function sendMessage() { 
    if (app && app.sendMessage) app.sendMessage(); 
    else console.warn('App not ready for sendMessage'); 
}
function searchContent(type) { 
    if (app && app.searchContent) app.searchContent(type); 
    else console.warn('App not ready for searchContent'); 
}
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (app) app.sendMessage();
    }
}

// Initialize the app when DOM is loaded
let app = null;

// Backup initialization function
function initializeApp() {
    if (app) return app; // Already initialized
    
    try {
        console.log('🚀 Initializing Islamic AI App...');
        app = new IslamicAIApp();
        console.log('✅ Islamic AI App initialized successfully');
        
        // Make app globally accessible for debugging
        window.islamicApp = app;
        return app;
    } catch (error) {
        console.error('❌ Error initializing Islamic AI App:', error);
        
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;border-radius:5px;z-index:9999;';
        errorDiv.textContent = 'Error initializing app. Please refresh the page.';
        document.body.appendChild(errorDiv);
        return null;
    }
}

// Primary initialization on DOM ready
document.addEventListener('DOMContentLoaded', initializeApp);

// Backup initialization after window load
window.addEventListener('load', () => {
    if (!app) {
        console.log('🔄 Backup initialization triggered...');
        initializeApp();
    }
});

// Emergency initialization function for buttons
function ensureAppReady() {
    if (!app) {
        console.log('⚡ Emergency initialization triggered...');
        return initializeApp();
    }
    return app;
}
