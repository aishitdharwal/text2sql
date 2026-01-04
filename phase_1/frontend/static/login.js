// Login page JavaScript
// Get API base URL from environment or use relative path
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8080/api'
    : `http://${window.location.hostname}:8080/api`;

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    
    // Hide previous errors
    errorMessage.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Store session data
            sessionStorage.setItem('sessionId', data.session_id);
            sessionStorage.setItem('team', data.team);
            sessionStorage.setItem('database', data.database);
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Show error message
            errorMessage.textContent = data.detail || 'Login failed';
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMessage.textContent = 'Network error. Please make sure the backend API is running.';
        errorMessage.style.display = 'block';
    }
});
