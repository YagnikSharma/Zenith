// API Utilities for making requests to the backend

class API {
    static async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add auth token if available
        if (STATE.token) {
            headers['Authorization'] = `Bearer ${STATE.token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    static async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET'
        });
    }
    
    static async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    static async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    static async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}

// API Service Functions

// Auth API
const AuthAPI = {
    async login(email, password) {
        const response = await API.post(CONFIG.ENDPOINTS.LOGIN, {
            email,
            password
        });
        
        STATE.token = response.access_token;
        STATE.user = response.user;
        STATE.isGuest = false;
        saveState();
        
        return response;
    },
    
    async signup(email, password, displayName, language) {
        const response = await API.post(CONFIG.ENDPOINTS.SIGNUP, {
            email,
            password,
            display_name: displayName,
            preferred_language: language
        });
        
        STATE.token = response.access_token;
        STATE.user = response.user;
        STATE.isGuest = false;
        saveState();
        
        return response;
    },
    
    async logout() {
        try {
            await API.post(CONFIG.ENDPOINTS.LOGOUT);
        } catch (e) {
            console.error('Logout error:', e);
        }
        
        clearState();
    },
    
    async getProfile() {
        return API.get(CONFIG.ENDPOINTS.ME);
    }
};

// Chat API
const ChatAPI = {
    async sendMessage(message, language = STATE.language) {
        const response = await API.post(CONFIG.ENDPOINTS.CHAT_MESSAGE, {
            message,
            language
        });
        
        // Check for crisis
        if (response.sentiment && response.sentiment.sentiment === 'negative') {
            await this.checkCrisis(message);
        }
        
        return response;
    },
    
    async checkCrisis(message) {
        try {
            const response = await API.post(CONFIG.ENDPOINTS.CRISIS_CHECK, {
                message
            });
            
            if (response.is_crisis && response.confidence > 0.7) {
                showCrisisAlert(response);
            }
            
            return response;
        } catch (e) {
            console.error('Crisis check failed:', e);
        }
    },
    
    async getHistory(limit = 50) {
        return API.get(CONFIG.ENDPOINTS.CHAT_HISTORY, { limit });
    },
    
    async clearHistory() {
        return API.delete(CONFIG.ENDPOINTS.CHAT_HISTORY);
    }
};

// Community API
const CommunityAPI = {
    async getPosts(category = null, limit = 20, offset = 0) {
        const params = { limit, offset };
        if (category && category !== 'all') {
            params.category = category;
        }
        
        return API.get(CONFIG.ENDPOINTS.POSTS, params);
    },
    
    async createPost(title, content, category = 'general', anonymous = false) {
        return API.post(CONFIG.ENDPOINTS.POSTS, {
            title,
            content,
            category,
            anonymous
        });
    },
    
    async likePost(postId) {
        return API.post(`${CONFIG.ENDPOINTS.POSTS}/${postId}/like`);
    },
    
    async unlikePost(postId) {
        return API.delete(`${CONFIG.ENDPOINTS.POSTS}/${postId}/like`);
    },
    
    async addComment(postId, content, anonymous = false) {
        return API.post(`${CONFIG.ENDPOINTS.POSTS}/${postId}/comments`, {
            content,
            anonymous
        });
    },
    
    async getComments(postId, limit = 20) {
        return API.get(`${CONFIG.ENDPOINTS.POSTS}/${postId}/comments`, { limit });
    }
};

// Spiritual API
const SpiritualAPI = {
    async getQuote(tradition = 'universal') {
        return API.get(CONFIG.ENDPOINTS.SPIRITUAL_QUOTE, { tradition });
    },
    
    async getGuidance(concern, tradition = 'universal') {
        return API.post(CONFIG.ENDPOINTS.SPIRITUAL_GUIDANCE, {
            concern,
            tradition
        });
    },
    
    async getPractices(goal = 'peace') {
        return API.get(CONFIG.ENDPOINTS.SPIRITUAL_PRACTICES, { goal });
    },
    
    async getAffirmations(count = 5, focus = 'general') {
        return API.get(CONFIG.ENDPOINTS.SPIRITUAL_AFFIRMATIONS, { count, focus });
    }
};

// Meditation API
const MeditationAPI = {
    async getScript(duration = 5, focus = 'general', language = STATE.language) {
        return API.post(CONFIG.ENDPOINTS.MEDITATION_SCRIPT, {
            duration,
            focus,
            language
        });
    },
    
    async getBreathingExercise(type = '4-7-8') {
        return API.get(CONFIG.ENDPOINTS.MEDITATION_BREATHING, { type });
    },
    
    async getGuidedMeditations() {
        return API.get(CONFIG.ENDPOINTS.MEDITATION_GUIDED);
    },
    
    async logSession(duration, type, moodBefore = null, moodAfter = null, notes = null) {
        return API.post(CONFIG.ENDPOINTS.MEDITATION_LOG, {
            duration,
            type,
            mood_before: moodBefore,
            mood_after: moodAfter,
            notes
        });
    },
    
    async getStats() {
        return API.get(CONFIG.ENDPOINTS.MEDITATION_STATS);
    }
};

// Crisis API
const CrisisAPI = {
    async getResources() {
        return API.get(CONFIG.ENDPOINTS.CRISIS_RESOURCES);
    },
    
    async reportCrisis(message) {
        return API.post(CONFIG.ENDPOINTS.CRISIS_REPORT, { message });
    }
};