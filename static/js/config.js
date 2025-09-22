// Configuration and Constants
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    APP_NAME: 'Zenith Mental Wellness Platform',
    VERSION: '1.0.0',
    
    // Storage Keys
    STORAGE_KEYS: {
        AUTH_TOKEN: 'zenith_auth_token',
        USER_DATA: 'zenith_user_data',
        LANGUAGE: 'zenith_language',
        THEME: 'zenith_theme'
    },
    
    // API Endpoints
    ENDPOINTS: {
        // Auth
        LOGIN: '/auth/login',
        SIGNUP: '/auth/signup',
        LOGOUT: '/auth/logout',
        ME: '/auth/me',
        
        // Chat
        CHAT_MESSAGE: '/chat/message',
        CHAT_HISTORY: '/chat/history',
        
        // Crisis
        CRISIS_CHECK: '/crisis/check',
        CRISIS_RESOURCES: '/crisis/resources',
        CRISIS_REPORT: '/crisis/report',
        
        // Community
        POSTS: '/community/posts',
        
        // Spiritual
        SPIRITUAL_QUOTE: '/spiritual/quote',
        SPIRITUAL_GUIDANCE: '/spiritual/guidance',
        SPIRITUAL_PRACTICES: '/spiritual/practices',
        SPIRITUAL_AFFIRMATIONS: '/spiritual/affirmations',
        
        // Meditation
        MEDITATION_SCRIPT: '/meditation/script',
        MEDITATION_BREATHING: '/meditation/breathing',
        MEDITATION_GUIDED: '/meditation/guided',
        MEDITATION_LOG: '/meditation/log',
        MEDITATION_STATS: '/meditation/stats'
    },
    
    // Language Codes
    LANGUAGES: {
        'en': 'English',
        'hi': 'हिन्दी',
        'bn': 'বাংলা',
        'te': 'తెలుగు',
        'mr': 'मराठी',
        'ta': 'தமிழ்',
        'ur': 'اردو',
        'gu': 'ગુજરાતી',
        'kn': 'ಕನ್ನಡ',
        'ml': 'മലയാളം'
    },
    
    // Crisis Keywords for client-side detection
    CRISIS_KEYWORDS: [
        'suicide', 'kill myself', 'end my life', 'want to die',
        'self harm', 'hurt myself', 'no reason to live',
        'better off dead', "can't go on", 'worthless'
    ]
};

// Global State Management
const STATE = {
    user: null,
    token: null,
    language: 'en',
    currentSection: 'chat',
    isGuest: false
};

// Initialize state from localStorage
function initializeState() {
    const token = localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    const userData = localStorage.getItem(CONFIG.STORAGE_KEYS.USER_DATA);
    const language = localStorage.getItem(CONFIG.STORAGE_KEYS.LANGUAGE);
    
    if (token) {
        STATE.token = token;
    }
    
    if (userData) {
        try {
            STATE.user = JSON.parse(userData);
        } catch (e) {
            console.error('Failed to parse user data:', e);
        }
    }
    
    if (language) {
        STATE.language = language;
    }
}

// Save state to localStorage
function saveState() {
    if (STATE.token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN, STATE.token);
    } else {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    }
    
    if (STATE.user) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER_DATA, JSON.stringify(STATE.user));
    } else {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_DATA);
    }
    
    localStorage.setItem(CONFIG.STORAGE_KEYS.LANGUAGE, STATE.language);
}

// Clear state
function clearState() {
    STATE.user = null;
    STATE.token = null;
    STATE.isGuest = false;
    localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_DATA);
}