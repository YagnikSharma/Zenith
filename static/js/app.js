// Main Application JavaScript

// Initialize the application
function initializeApp() {
    console.log('Initializing Zenith Mental Wellness Platform...');
    
    // Initialize chat
    initializeChat();
    
    // Load initial content based on section
    navigateTo('chat');
    
    // Load stats if user is logged in
    if (!STATE.isGuest) {
        loadMeditationStats();
    }
}

// Navigate between sections
function navigateTo(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(`${section}Section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent.toLowerCase().includes(section) || 
            (section === 'chat' && item.textContent.includes('AI Companion'))) {
            item.classList.add('active');
        }
    });
    
    // Update state
    STATE.currentSection = section;
    
    // Load section-specific content
    switch(section) {
        case 'chat':
            // Chat is already initialized
            break;
        case 'community':
            loadPosts('all');
            break;
        case 'spiritual':
            loadSpiritualContent();
            break;
        case 'meditation':
            loadMeditationStats();
            break;
        case 'crisis':
            // Crisis resources are static
            break;
    }
}

// Show loading screen
function showLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        loadingScreen.style.display = 'flex';
        loadingScreen.classList.remove('hidden');
    }
}

// Hide loading screen
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
    }[type] || 'info';
    
    toast.innerHTML = `
        <span class="material-icons">${icon}</span>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search/chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.focus();
        }
    }
    
    // Escape: Close modals
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.active');
        if (modal) {
            modal.remove();
        }
    }
});

// Handle window resize
window.addEventListener('resize', function() {
    // Mobile responsive adjustments
    if (window.innerWidth < 768) {
        document.querySelector('.sidebar')?.classList.remove('open');
    }
});

// Toggle mobile sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Handle network status
window.addEventListener('online', function() {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showToast('You are offline. Some features may be limited.', 'warning');
});

// Handle visibility change (tab switching)
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause any active timers/animations
        if (meditationTimer) {
            // Don't stop meditation, just note the time
            console.log('Tab hidden during meditation');
        }
    } else {
        // Resume if needed
        console.log('Tab visible again');
    }
});

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e);
    
    // Don't show toast for every error in development
    if (STATE.APP_ENV === 'production') {
        showToast('Something went wrong. Please try again.', 'error');
    }
});

// Unhandled promise rejection
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e);
    
    if (e.reason && e.reason.message) {
        if (e.reason.message.includes('401') || e.reason.message.includes('Unauthorized')) {
            showToast('Session expired. Please login again.', 'warning');
            logout();
        }
    }
});

// Service Worker Registration (for PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment when service worker is implemented
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('Service Worker registered'))
        //     .catch(err => console.log('Service Worker registration failed'));
    });
}

// Initialize tooltips
function initTooltips() {
    // Basic tooltip implementation
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            // Could implement custom tooltip here
        });
    });
}

// Auto-save functionality
let autoSaveTimer = null;

function autoSave(key, value) {
    clearTimeout(autoSaveTimer);
    
    autoSaveTimer = setTimeout(() => {
        localStorage.setItem(`zenith_draft_${key}`, JSON.stringify({
            value,
            timestamp: Date.now()
        }));
    }, 1000);
}

function loadDraft(key) {
    const draft = localStorage.getItem(`zenith_draft_${key}`);
    
    if (draft) {
        try {
            const parsed = JSON.parse(draft);
            // Check if draft is less than 24 hours old
            if (Date.now() - parsed.timestamp < 86400000) {
                return parsed.value;
            }
        } catch (e) {
            console.error('Failed to load draft:', e);
        }
    }
    
    return null;
}

// Clear old drafts
function clearOldDrafts() {
    for (let key in localStorage) {
        if (key.startsWith('zenith_draft_')) {
            try {
                const draft = JSON.parse(localStorage.getItem(key));
                if (Date.now() - draft.timestamp > 86400000) {
                    localStorage.removeItem(key);
                }
            } catch (e) {
                localStorage.removeItem(key);
            }
        }
    }
}

// Clean up on load
clearOldDrafts();

// Export functions for use in other modules
window.ZenithApp = {
    navigateTo,
    showToast,
    showLoadingScreen,
    hideLoadingScreen,
    autoSave,
    loadDraft
};

console.log('Zenith Mental Wellness Platform v1.0.0 loaded successfully');