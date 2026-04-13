// Islamic AI Agent - Frontend JavaScript

class IslamicAIApp {
    constructor() {
        this.currentAgent = 'single';
        this.userGender = localStorage.getItem('userGender') || 'not_specified';
        this.userLocation = null;
        this.isVoiceInputActive = false;
        this.init();
    }

    init() {
        // Initial load
        this.loadHijriDate();
        this.setInitialGender();
        this.setupEventListeners();
        this.checkAgentStatus();
        this.setupKnowledgeBaseListeners();

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

    setInitialGender() {
        const genderSelect = document.getElementById('genderSelect');
        if (genderSelect) {
            genderSelect.value = this.userGender;
        }
    }

    updateGender(gender) {
        this.userGender = gender;
        localStorage.setItem('userGender', gender);
        this.addMessage(`👤 Language & guidance preference updated to ${gender === 'female' ? 'Sister' : gender === 'male' ? 'Brother' : 'General'} mode.`, 'agent');
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
                    body: JSON.stringify({
                        message,
                        user_gender: this.userGender
                    })
                });
            } else {
                response = await fetch('/api/multi-chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message,
                        specialist: this.currentAgent,
                        user_gender: this.userGender
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

    addMessage(text, sender, isHtml = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatarIcon = sender === 'agent' ? 'fa-mosque' : 'fa-user';
        const senderName = sender === 'agent' ? document.getElementById('currentAgentName').textContent : 'You';
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageContent = isHtml ? text : this.formatMarkdown(text);

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${avatarIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${senderName}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-text">${messageContent}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMarkdown(content) {
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
            function (match) {
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
            'hadith': 'Sheikha Aisha',
            'fiqh': 'Sheikh Omar',
            'spiritual': 'Sheikha Fatima'
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

    async performZakatCalculation() {
        const cash = document.getElementById('cashInput').value || 0;
        const gold_grams = document.getElementById('goldInput').value || 0;
        const silver_grams = document.getElementById('silverInput').value || 0;
        const investments = document.getElementById('investmentInput').value || 0;
        const business_assets = document.getElementById('businessInput').value || 0;
        const debts = document.getElementById('debtInput').value || 0;

        this.closeModal('zakatModal');
        this.showLoading();

        try {
            const response = await fetch('/api/zakat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cash, gold_grams, silver_grams, investments, business_assets, debts
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.addMessage(data.zakat_result, 'agent');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error calculating Zakat: ${error.message}`, 'agent');
        }

        // Reset fields
        const fields = ['cashInput', 'goldInput', 'silverInput', 'investmentInput', 'businessInput', 'debtInput'];
        fields.forEach(f => document.getElementById(f).value = '');
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
                // Add text response
                this.addMessage(data.qibla_direction, 'agent');

                // Add visual compass if bearing is available
                if (data.bearing !== undefined) {
                    this.addVisualCompass(data.bearing, data.direction);
                }
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.hideLoading();
            this.addMessage(`❌ Error fetching Qibla direction: ${error.message}`, 'agent');
        }
    }

    addVisualCompass(bearing, direction) {
        const compassId = `compass-${Date.now()}`;
        const compassHtml = `
            <div class="qibla-container">
                <div class="compass-wrapper">
                    <!-- Compass Disk -->
                    <svg class="compass-base" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="48" fill="#F8F9FA" stroke="#2E8B57" stroke-width="2"/>
                        <circle cx="50" cy="50" r="42" fill="none" stroke="#e9ecef" stroke-width="1" stroke-dasharray="2,2"/>
                        <text x="50" y="15" text-anchor="middle" font-size="8" font-weight="bold" fill="#2E8B57">N</text>
                        <text x="85" y="53" text-anchor="middle" font-size="8" font-weight="bold" fill="#2C3E50">E</text>
                        <text x="50" y="90" text-anchor="middle" font-size="8" font-weight="bold" fill="#2C3E50">S</text>
                        <text x="15" y="53" text-anchor="middle" font-size="8" font-weight="bold" fill="#2C3E50">W</text>
                        <!-- Degree Marks -->
                        <path d="M50 5 L50 10 M50 90 L50 95 M5 50 L10 50 M90 50 L95 50" stroke="#ADB5BD" stroke-width="1"/>
                    </svg>
                    <!-- Rotating Needle -->
                    <div id="${compassId}" class="compass-needle">
                        <svg viewBox="0 0 100 100" width="100%" height="100%">
                            <!-- Needle -->
                            <path d="M50 10 L58 50 L50 90 L42 50 Z" fill="#DAA520" stroke="#B8860B" stroke-width="1"/>
                            <path d="M50 10 L50 90" stroke="white" stroke-width="0.5" stroke-dasharray="2,2"/>
                            <!-- Indicator -->
                            <circle cx="50" cy="18" r="6" fill="#1F5F3F"/>
                            <text x="50" y="21" text-anchor="middle" font-size="8" fill="white">🕌</text>
                        </svg>
                    </div>
                </div>
                <div class="qibla-info">
                    <div class="qibla-degree">${bearing.toFixed(1)}° ${direction}</div>
                    <small>Pointed toward the Kaaba</small>
                </div>
            </div>
        `;

        this.addMessage(compassHtml, 'agent', true);

        // Final rotation with timing
        setTimeout(() => {
            const needle = document.getElementById(compassId);
            if (needle) {
                needle.style.transform = `translate(-50%, -50%) rotate(${bearing}deg)`;
            }
        }, 100);
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

    // Knowledge Base Management
    setupKnowledgeBaseListeners() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        if (!dropZone || !fileInput) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFileUpload(files);
        }, false);

        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files);
        }, false);
    }

    showKnowledgeModal() {
        document.getElementById('knowledgeModal').style.display = 'block';
        this.loadIngestedFiles();
    }

    switchKnowledgeTab(tab) {
        const uploadTab = document.getElementById('uploadTab');
        const manageTab = document.getElementById('manageTab');
        const tabs = document.querySelectorAll('.tab-btn');

        if (tab === 'upload') {
            uploadTab.style.display = 'block';
            manageTab.style.display = 'none';
            tabs[0].classList.add('active');
            tabs[1].classList.remove('active');
        } else {
            uploadTab.style.display = 'none';
            manageTab.style.display = 'block';
            tabs[0].classList.remove('active');
            tabs[1].classList.add('active');
            this.loadIngestedFiles();
        }
    }

    async handleFileUpload(files) {
        const fileList = document.getElementById('fileList');
        const ingestBtn = document.getElementById('ingestBtn');

        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/knowledge/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.innerHTML = `
                        <span><i class="fas fa-file-alt"></i> ${file.name}</span>
                        <span class="status text-success">Uploaded</span>
                    `;
                    fileList.appendChild(item);
                    ingestBtn.disabled = false;
                } else {
                    alert(`Error uploading ${file.name}: ${data.error}`);
                }
            } catch (error) {
                console.error('Upload error:', error);
            }
        }
    }

    async startIngestion() {
        const ingestBtn = document.getElementById('ingestBtn');
        ingestBtn.disabled = true;
        ingestBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ingesting...';

        try {
            const response = await fetch('/api/knowledge/ingest', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.addMessage('📦 Knowledge ingestion started in the background. Your AI will be updated shortly.', 'agent');
                setTimeout(() => {
                    ingestBtn.innerHTML = '<i class="fas fa-check"></i> Success';
                    this.loadIngestedFiles();
                }, 2000);
            }
        } catch (error) {
            alert('Error starting ingestion: ' + error.message);
            ingestBtn.disabled = false;
            ingestBtn.innerHTML = '<i class="fas fa-cogs"></i> Start Ingestion';
        }
    }

    async loadIngestedFiles() {
        const list = document.getElementById('ingestedFileList');
        try {
            const response = await fetch('/api/knowledge/list');
            if (!response.ok) return;
            const data = await response.json();

            if (data.files && data.files.length > 0) {
                list.innerHTML = data.files.map(f => `
                    <li><i class="fas fa-check-circle"></i> ${f}</li>
                `).join('');
            } else {
                list.innerHTML = '<li>No documents ingested yet.</li>';
            }
        } catch (error) {
            list.innerHTML = '<li>Error loading documents.</li>';
        }
    }

    async getAdhkar(category) {
        const resultArea = document.getElementById('adhkarResult');
        resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching Adhkar...';
        try {
            const response = await fetch('/api/adhkar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category })
            });
            const data = await response.json();
            resultArea.innerHTML = this.formatIslamicText(data.response);
        } catch (error) {
            resultArea.innerHTML = 'Error fetching Adhkar: ' + error.message;
        }
    }

    async getNameOfAllah() {
        const query = document.getElementById('nameQueryInput').value;
        const resultArea = document.getElementById('namesResult');
        if (!query) return alert('Please enter a name or number');

        resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
        try {
            const response = await fetch('/api/names-of-allah', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            resultArea.innerHTML = this.formatIslamicText(data.response);
        } catch (error) {
            resultArea.innerHTML = 'Error: ' + error.message;
        }
    }

    async getHajjGuidance(ritual) {
        const resultArea = document.getElementById('hajjResult');
        resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading guide...';
        try {
            const response = await fetch('/api/hajj-umrah', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ritual })
            });
            const data = await response.json();
            resultArea.innerHTML = this.formatIslamicText(data.response);
        } catch (error) {
            resultArea.innerHTML = 'Error: ' + error.message;
        }
    }

    async checkHalal() {
        const item = document.getElementById('halalItemInput').value;
        const resultArea = document.getElementById('halalResult');
        if (!item) return alert('Please enter an ingredient or E-number');

        resultArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
        try {
            const response = await fetch('/api/halal-check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item })
            });
            const data = await response.json();
            resultArea.innerHTML = this.formatIslamicText(data.response);
        } catch (error) {
            resultArea.innerHTML = 'Error: ' + error.message;
        }
    }

    async loadCalendarEvents() {
        const eventsList = document.getElementById('calendarEventsList');
        const hijriDisplay = document.getElementById('currentHijriDisplay');
        const gregorianDisplay = document.getElementById('currentGregorianDisplay');

        eventsList.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Calculating events...</div>';

        try {
            const response = await fetch('/api/calendar');
            const data = await response.json();

            hijriDisplay.textContent = data.current_hijri || "N/A";
            gregorianDisplay.textContent = new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

            if (data.events && data.events.length > 0) {
                eventsList.innerHTML = data.events.map(event => `
                    <div class="event-item">
                        <div class="event-info">
                            <span class="event-name">${event.name}</span>
                            <span class="event-date">Month ${event.month}, Day ${event.day}</span>
                        </div>
                        <p class="event-desc">${event.desc}</p>
                    </div>
                `).join('');
            } else {
                eventsList.innerHTML = '<p>No upcoming events found.</p>';
            }
        } catch (error) {
            eventsList.innerHTML = '<p class="error-text">Error loading calendar: ' + error.message + '</p>';
        }
    }
    async loadTrendingTopics() {
        const list = document.getElementById('trendingList');
        if (!list) return;

        list.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';

        try {
            const response = await fetch('/api/trending');
            const data = await response.json();

            if (data.trending && data.trending.length > 0) {
                list.innerHTML = data.trending.map(t => `
                    <div class="trending-item">
                        <span class="trending-topic">${t.topic}</span>
                        <div class="trending-meta">
                            <span class="count">${t.count} queries</span>
                            <span class="trend-badge trend-${t.trend}">${t.trend.toUpperCase()}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                list.innerHTML = '<p>No trending data available yet.</p>';
            }
        } catch (error) {
            list.innerHTML = '<p>Error loading trending insights.</p>';
        }
    }

    formatIslamicText(text) {
        if (!text) return '';
        // Convert **bold** to <strong> and newlines to <br>
        return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/<div class="arabic-text"/g, '<div class="arabic-text"');
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
function showZakatModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('zakatModal');
    else console.warn('App not ready for showZakatModal');
}
function performZakatCalculation() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.performZakatCalculation) appInstance.performZakatCalculation();
    else console.warn('App not ready for performZakatCalculation');
}
function changeAgent() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.changeAgent) appInstance.changeAgent();
    else console.warn('App not ready for changeAgent');
}
function showKnowledgeModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showKnowledgeModal) appInstance.showKnowledgeModal();
    else console.warn('App not ready for showKnowledgeModal');
}
function switchKnowledgeTab(tab) {
    if (app && app.switchKnowledgeTab) app.switchKnowledgeTab(tab);
    else console.warn('App not ready for switchKnowledgeTab');
}
function startIngestion() {
    if (app && app.startIngestion) app.startIngestion();
    else console.warn('App not ready for startIngestion');
}
function getLocation() {
    if (app && app.getLocation) app.getLocation();
    else console.warn('App not ready for getLocation');
}
function toggleVoiceInput() {
    if (app && app.toggleVoiceInput) app.toggleVoiceInput();
    else console.warn('App not ready for toggleVoiceInput');
}
function updateGender() {
    const gender = document.getElementById('genderSelect').value;
    if (app && app.updateGender) app.updateGender(gender);
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
function showAdhkarModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('adhkarModal');
}
function showNamesModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('namesModal');
}
function showHajjModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('hajjModal');
}
function showHalalModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) appInstance.showModal('halalModal');
}
function showCalendarModal() {
    const modal = document.getElementById('calendarModal');
    modal.style.display = 'block';
    ensureAppReady().then(app => app.loadCalendarEvents());
}

function showStatsModal() {
    const appInstance = ensureAppReady();
    if (appInstance && appInstance.showModal) {
        appInstance.showModal('statsModal');
        appInstance.loadTrendingTopics();
    }
}
function getAdhkar(cat) {
    if (app && app.getAdhkar) app.getAdhkar(cat);
}
function getNameOfAllah() {
    if (app && app.getNameOfAllah) app.getNameOfAllah();
}
function getHajjGuidance(ritual) {
    if (app && app.getHajjGuidance) app.getHajjGuidance(ritual);
}
function checkHalal() {
    if (app && app.checkHalal) app.checkHalal();
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
