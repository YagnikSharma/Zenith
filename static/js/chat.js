// Chat Functionality

let isTyping = false;

// Send a message
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check if guest trying to use chat
    if (STATE.isGuest) {
        showToast('Please login to use the chat feature', 'warning');
        return;
    }
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to API
        const response = await ChatAPI.sendMessage(message, STATE.language);
        
        // Remove typing indicator
        hideTypingIndicator();
        
        // Add AI response to chat
        addMessageToChat(response.response, 'ai', response.sentiment);
        
        // Check for crisis keywords locally
        if (containsCrisisKeywords(message)) {
            const crisisResponse = await ChatAPI.checkCrisis(message);
            if (crisisResponse && crisisResponse.is_crisis) {
                showCrisisAlert(crisisResponse);
            }
        }
        
    } catch (error) {
        hideTypingIndicator();
        showToast('Failed to send message. Please try again.', 'error');
        console.error('Chat error:', error);
    }
}

// Add message to chat display
function addMessageToChat(content, sender, sentiment = null) {
    const chatMessages = document.getElementById('chatMessages');
    
    // Remove welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.chat-welcome');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = `<span class="material-icons">${sender === 'user' ? 'person' : 'psychology'}</span>`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const messageText = document.createElement('p');
    messageText.textContent = content;
    contentDiv.appendChild(messageText);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();
    contentDiv.appendChild(timeDiv);
    
    if (sentiment && sender === 'user') {
        const sentimentDiv = document.createElement('div');
        sentimentDiv.className = `message-sentiment ${sentiment.sentiment}`;
        sentimentDiv.textContent = `Mood: ${sentiment.sentiment}`;
        contentDiv.appendChild(sentimentDiv);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const chatMessages = document.getElementById('chatMessages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <span class="material-icons">psychology</span>
        </div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    const typingMessage = document.querySelector('.typing-message');
    if (typingMessage) {
        typingMessage.remove();
    }
}

// Check for crisis keywords
function containsCrisisKeywords(message) {
    const lowerMessage = message.toLowerCase();
    return CONFIG.CRISIS_KEYWORDS.some(keyword => lowerMessage.includes(keyword));
}

// Show crisis alert
function showCrisisAlert(crisisData) {
    const alertDiv = document.getElementById('crisisAlert');
    alertDiv.style.display = 'block';
    
    // Scroll to alert
    alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-hide after 30 seconds
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 30000);
}

// Start crisis chat
async function startCrisisChat() {
    navigateTo('chat');
    
    const message = "I need immediate support. Can you help me with some coping strategies?";
    document.getElementById('chatInput').value = message;
    await sendMessage();
}

// Load chat history
async function loadChatHistory() {
    if (STATE.isGuest) return;
    
    try {
        const history = await ChatAPI.getHistory(20);
        
        if (history.messages && history.messages.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            
            // Remove welcome message
            const welcomeMsg = chatMessages.querySelector('.chat-welcome');
            if (welcomeMsg) {
                welcomeMsg.remove();
            }
            
            // Add history messages
            history.messages.reverse().forEach(msg => {
                addMessageToChat(msg.user_message, 'user');
                addMessageToChat(msg.ai_response, 'ai');
            });
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

// Initialize chat
function initializeChat() {
    // Set up enter key to send message
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Load chat history if logged in
    if (!STATE.isGuest) {
        loadChatHistory();
    }
    
    // Set language selector
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.value = STATE.language;
        languageSelect.addEventListener('change', function(e) {
            STATE.language = e.target.value;
            saveState();
            showToast(`Language changed to ${CONFIG.LANGUAGES[STATE.language]}`, 'info');
        });
    }
}