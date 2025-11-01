// Hospital Dashboard Utility Functions

// Show toast notification
function showToast(message, type = 'success', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// Confirm action with custom message
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading state management
function setLoading(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = '<span class="loading"></span> Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.getAttribute('data-original-text') || 'Submit';
    }
}

// API request helper
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Auto-refresh functionality
function setupAutoRefresh(interval = 30000) {
    if (window.location.pathname.includes('dashboard')) {
        setInterval(async () => {
            try {
                const data = await apiRequest('/api/dashboard_stats');
                updateDashboardStats(data);
            } catch (error) {
                console.log('Auto-refresh failed:', error);
            }
        }, interval);
    }
}

// Update dashboard statistics
function updateDashboardStats(data) {
    const elements = {
        'total-beds': data.total_beds,
        'occupied-beds': data.occupied_beds,
        'available-beds': data.available_beds
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Setup auto-refresh
    setupAutoRefresh();
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.setAttribute('data-original-text', submitBtn.innerHTML);
                setLoading(submitBtn, true);
            }
        });
    });
});

// Export functions for global use
window.HospitalUtils = {
    showToast,
    formatDate,
    confirmAction,
    setLoading,
    apiRequest,
    setupAutoRefresh,
    updateDashboardStats
};
