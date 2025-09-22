// User display utility functions

function updateUserDisplay(userData) {
    // Determine the display name
    let displayName = 'User';
    
    if (userData) {
        if (userData.display_name) {
            displayName = userData.display_name;
        } else if (userData.name) {
            displayName = userData.name;
        } else if (userData.email) {
            displayName = userData.email.split('@')[0];
        }
    }
    
    // Update all user name elements
    const userNameElements = [
        document.getElementById('userName'),
        document.getElementById('userNameSidebar')
    ];
    
    userNameElements.forEach(element => {
        if (element) {
            element.textContent = displayName;
        }
    });
    
    // Update user email if available
    const emailElement = document.getElementById('userEmail');
    if (emailElement && userData && userData.email) {
        emailElement.textContent = userData.email;
    }
    
    // Update user status
    const statusElements = document.querySelectorAll('.user-status');
    statusElements.forEach(element => {
        if (element) {
            element.textContent = userData ? 'Active' : 'Guest Mode';
        }
    });
    
    return displayName;
}