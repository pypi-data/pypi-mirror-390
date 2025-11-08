// Common utilities and shared variables for GRI Resolver Web Interface

// API base URL
const API_BASE = '/api';

// Utility function to escape HTML
function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Function to escape JavaScript string for use in HTML attributes
function escapeForJs(str) {
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
}

