// Authentication Functions

// Switch between login and signup forms
function switchToSignup() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupForm').style.display = 'block';
    document.getElementById('authTitle').textContent = 'Create Account';
    document.getElementById('authSubtitle').textContent = 'Join our mental wellness community';
}

function switchToLogin() {
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('authTitle').textContent = 'Welcome to Zenith';
    document.getElementById('authSubtitle').textContent = 'Your AI-powered mental wellness companion';
}

// Continue as guest
function continueAsGuest() {
    STATE.isGuest = true;
    STATE.user = {
        display_name: 'User',
        email: 'guest@zenith.com'
    };
    
    document.getElementById('authModal').style.display = 'none';
    document.getElementById('mainApp').style.display = 'flex';
    document.getElementById('userName').textContent = 'User';
    
    showToast('You are browsing as a guest. Some features are limited.', 'info');
    initializeApp();
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        showLoadingScreen();
        const response = await AuthAPI.login(email, password);
        
        document.getElementById('authModal').style.display = 'none';
        document.getElementById('mainApp').style.display = 'flex';
        document.getElementById('userName').textContent = response.user.display_name || 'User';
        
        showToast('Welcome back!', 'success');
        initializeApp();
        
    } catch (error) {
        showToast(error.message || 'Login failed. Please try again.', 'error');
    } finally {
        hideLoadingScreen();
    }
}

// Handle signup
async function handleSignup(event) {
    event.preventDefault();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const language = document.getElementById('signupLanguage').value;
    
    try {
        showLoadingScreen();
        const response = await AuthAPI.signup(email, password, name, language);
        
        STATE.language = language;
        saveState();
        
        document.getElementById('authModal').style.display = 'none';
        document.getElementById('mainApp').style.display = 'flex';
        document.getElementById('userName').textContent = response.user.display_name || 'User';
        
        showToast('Welcome to Zenith!', 'success');
        initializeApp();
        
    } catch (error) {
        showToast(error.message || 'Signup failed. Please try again.', 'error');
    } finally {
        hideLoadingScreen();
    }
}

// Handle logout
async function logout() {
    if (confirm('Are you sure you want to logout?')) {
        try {
            await AuthAPI.logout();
            clearState();
            
            document.getElementById('mainApp').style.display = 'none';
            document.getElementById('authModal').style.display = 'flex';
            
            // Reset forms
            document.getElementById('loginForm').reset();
            document.getElementById('signupForm').reset();
            
            showToast('Logged out successfully', 'info');
            
        } catch (error) {
            console.error('Logout error:', error);
            // Force logout even if API call fails
            clearState();
            location.reload();
        }
    }
}

// Check authentication status on page load
async function checkAuth() {
    if (STATE.token) {
        try {
            const profile = await AuthAPI.getProfile();
            STATE.user = profile;
            saveState();
            
            document.getElementById('authModal').style.display = 'none';
            document.getElementById('mainApp').style.display = 'flex';
            document.getElementById('userName').textContent = profile.display_name || 'User';
            
            initializeApp();
            
        } catch (error) {
            console.error('Auth check failed:', error);
            clearState();
            document.getElementById('authModal').style.display = 'flex';
            document.getElementById('mainApp').style.display = 'none';
        }
    } else {
        document.getElementById('authModal').style.display = 'flex';
        document.getElementById('mainApp').style.display = 'none';
    }
}

// Initialize auth event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Signup form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Initialize state
    initializeState();
    
    // Hide loading screen
    setTimeout(() => {
        hideLoadingScreen();
        checkAuth();
    }, 1000);
});