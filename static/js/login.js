// Add this to your template or a separate JS file
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const submitButton = loginForm.querySelector('button[type="submit"]');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Disable submit button and show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm mr-2"></span>Signing in...';

        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            remember_me: formData.get('rememberMe') === 'on'
        };

        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Show success message
                showNotification('success', 'Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = result.redirect_url;
                }, 1000);
            } else {
                // Show error message
                showNotification('error', result.message);
                submitButton.disabled = false;
                submitButton.innerHTML = 'Sign In';
            }
        } catch (error) {
            showNotification('error', 'Login failed. Please try again.');
            submitButton.disabled = false;
            submitButton.innerHTML = 'Sign In';
        }
    });

    // Helper function to show notifications
    function showNotification(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;

        const form = document.querySelector('.login-form');
        form.insertBefore(alertDiv, form.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});