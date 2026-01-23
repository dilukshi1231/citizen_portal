// Notification Management System - Complete Script

// State Management
let selectedAudiences = new Set();
let notificationData = {
    type: 'announcement',
    priority: 'medium',
    category: '',
    actionUrl: '',
    titleEn: '',
    titleSi: '',
    messageEn: '',
    messageSi: '',
    expiresIn: 30
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updatePreview();
    loadNotifications();
    loadAnalytics();
});

// Event Listeners Setup
function initializeEventListeners() {
    // Audience Selection
    const audienceButtons = document.querySelectorAll('.audience-btn');
    audienceButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleAudience(this.dataset.audience);
        });
    });

    // Notification Type
    const typeButtons = document.querySelectorAll('.type-btn');
    typeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            selectType(this.dataset.type);
        });
    });

    // Priority Level
    const priorityButtons = document.querySelectorAll('.priority-btn');
    priorityButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            selectPriority(this.dataset.priority);
        });
    });

    // Form Inputs
    document.getElementById('category')?.addEventListener('input', updateFromForm);
    document.getElementById('actionUrl')?.addEventListener('input', updateFromForm);
    document.getElementById('titleEn')?.addEventListener('input', updateFromForm);
    document.getElementById('titleSi')?.addEventListener('input', updateFromForm);
    document.getElementById('messageEn')?.addEventListener('input', updateFromForm);
    document.getElementById('messageSi')?.addEventListener('input', updateFromForm);
    document.getElementById('expiresIn')?.addEventListener('input', updateFromForm);

    // Form Actions
    document.getElementById('createBtn')?.addEventListener('click', createNotification);
    document.getElementById('resetBtn')?.addEventListener('click', resetForm);
    document.getElementById('refreshBtn')?.addEventListener('click', loadNotifications);

    // Tab Navigation
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
}

// Audience Management
function toggleAudience(audience) {
    const btn = document.querySelector(`[data-audience="${audience}"]`);
    
    if (selectedAudiences.has(audience)) {
        selectedAudiences.delete(audience);
        btn?.classList.remove('selected');
    } else {
        selectedAudiences.add(audience);
        btn?.classList.add('selected');
    }
    
    updatePreview();
}

// Type Selection
function selectType(type) {
    notificationData.type = type;
    
    const typeButtons = document.querySelectorAll('.type-btn');
    typeButtons.forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.type === type) {
            btn.classList.add('selected');
        }
    });
    
    updatePreview();
}

// Priority Selection
function selectPriority(priority) {
    notificationData.priority = priority;
    
    const priorityButtons = document.querySelectorAll('.priority-btn');
    priorityButtons.forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.priority === priority) {
            btn.classList.add('selected');
        }
    });
    
    updatePreview();
}

// Update from Form Inputs
function updateFromForm() {
    notificationData.category = document.getElementById('category')?.value || '';
    notificationData.actionUrl = document.getElementById('actionUrl')?.value || '';
    notificationData.titleEn = document.getElementById('titleEn')?.value || '';
    notificationData.titleSi = document.getElementById('titleSi')?.value || '';
    notificationData.messageEn = document.getElementById('messageEn')?.value || '';
    notificationData.messageSi = document.getElementById('messageSi')?.value || '';
    notificationData.expiresIn = parseInt(document.getElementById('expiresIn')?.value) || 30;
    
    updatePreview();
}

// Update Preview
function updatePreview() {
    const preview = document.getElementById('notificationPreview');
    if (!preview) return;

    const icon = getTypeIcon(notificationData.type);
    const priorityClass = getPriorityClass(notificationData.priority);
    const title = notificationData.titleEn || 'Notification Title';
    const message = notificationData.messageEn || 'Notification message will appear here...';
    const audienceText = selectedAudiences.size > 0 
        ? Array.from(selectedAudiences).join(', ') 
        : 'No audience selected';

    preview.innerHTML = `
        <div class="preview-notification ${priorityClass}">
            <div class="preview-icon">${icon}</div>
            <div class="preview-content">
                <div class="preview-title">${escapeHtml(title)}</div>
                <div class="preview-message">${escapeHtml(message)}</div>
                <div class="preview-meta">
                    <span class="preview-priority">${notificationData.priority} Priority</span>
                    <span class="preview-audience">${audienceText}</span>
                </div>
            </div>
        </div>
    `;
}

// Create Notification
async function createNotification() {
    // Validation
    if (!notificationData.titleEn.trim()) {
        showAlert('Please enter a title in English', 'error');
        return;
    }

    if (!notificationData.messageEn.trim()) {
        showAlert('Please enter a message in English', 'error');
        return;
    }

    if (selectedAudiences.size === 0) {
        showAlert('Please select at least one target audience', 'error');
        return;
    }

    // Prepare data
    const payload = {
        ...notificationData,
        audiences: Array.from(selectedAudiences),
        createdAt: new Date().toISOString()
    };

    try {
        const response = await fetch('/api/notifications', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            showAlert('Notification created successfully!', 'success');
            resetForm();
            loadNotifications();
            loadAnalytics();
        } else {
            const error = await response.json();
            showAlert(error.message || 'Failed to create notification', 'error');
        }
    } catch (error) {
        console.error('Error creating notification:', error);
        showAlert('An error occurred. Please try again.', 'error');
    }
}

// Load Notifications
async function loadNotifications() {
    const container = document.getElementById('notificationsList');
    if (!container) return;

    container.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const response = await fetch('/api/notifications');
        if (response.ok) {
            const notifications = await response.json();
            displayNotifications(notifications);
        } else {
            container.innerHTML = '<div class="error">Failed to load notifications</div>';
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        container.innerHTML = '<div class="error">Error loading notifications</div>';
    }
}

// Display Notifications
function displayNotifications(notifications) {
    const container = document.getElementById('notificationsList');
    if (!container) return;

    if (notifications.length === 0) {
        container.innerHTML = '<div class="empty-state">No notifications yet</div>';
        return;
    }

    container.innerHTML = notifications.map(notif => `
        <div class="notification-item ${getPriorityClass(notif.priority)}">
            <div class="notification-header">
                <span class="notification-icon">${getTypeIcon(notif.type)}</span>
                <h3>${escapeHtml(notif.titleEn)}</h3>
                <span class="notification-status ${notif.status || 'active'}">${notif.status || 'Active'}</span>
            </div>
            <p class="notification-message">${escapeHtml(notif.messageEn)}</p>
            <div class="notification-meta">
                <span>📊 Sent to: ${notif.audiences.join(', ')}</span>
                <span>📅 ${formatDate(notif.createdAt)}</span>
                <span>👁️ Read: ${notif.readCount || 0}/${notif.sentCount || 0}</span>
            </div>
            <div class="notification-actions">
                <button onclick="viewNotification('${notif.id}')" class="btn-view">View</button>
                <button onclick="editNotification('${notif.id}')" class="btn-edit">Edit</button>
                <button onclick="deleteNotification('${notif.id}')" class="btn-delete">Delete</button>
            </div>
        </div>
    `).join('');
}

// Load Analytics
async function loadAnalytics() {
    try {
        const response = await fetch('/api/notifications/analytics');
        if (response.ok) {
            const analytics = await response.json();
            displayAnalytics(analytics);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Display Analytics
function displayAnalytics(analytics) {
    document.getElementById('totalNotifications').textContent = analytics.total || 0;
    document.getElementById('activeMonth').textContent = analytics.activeMonth || 0;
    document.getElementById('avgReadRate').textContent = (analytics.avgReadRate || 0) + '%';
    
    // Display role chart
    if (analytics.byRole) {
        displayRoleChart(analytics.byRole);
    }
}

// Display Role Chart
function displayRoleChart(roleData) {
    const container = document.getElementById('roleChart');
    if (!container) return;

    const total = Object.values(roleData).reduce((sum, val) => sum + val, 0);
    
    container.innerHTML = Object.entries(roleData).map(([role, count]) => {
        const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : 0;
        return `
            <div class="chart-item">
                <span class="chart-label">${role}</span>
                <div class="chart-bar">
                    <div class="chart-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="chart-value">${count} (${percentage}%)</span>
            </div>
        `;
    }).join('');
}

// Reset Form
function resetForm() {
    // Clear audiences
    selectedAudiences.clear();
    document.querySelectorAll('.audience-btn').forEach(btn => {
        btn.classList.remove('selected');
    });

    // Reset to defaults
    notificationData = {
        type: 'announcement',
        priority: 'medium',
        category: '',
        actionUrl: '',
        titleEn: '',
        titleSi: '',
        messageEn: '',
        messageSi: '',
        expiresIn: 30
    };

    // Clear form inputs
    document.getElementById('category').value = '';
    document.getElementById('actionUrl').value = '';
    document.getElementById('titleEn').value = '';
    document.getElementById('titleSi').value = '';
    document.getElementById('messageEn').value = '';
    document.getElementById('messageSi').value = '';
    document.getElementById('expiresIn').value = '30';

    // Reset selections
    selectType('announcement');
    selectPriority('medium');
    updatePreview();
}

// Tab Switching
function switchTab(tabName) {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        }
    });

    contents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName + 'Tab') {
            content.classList.add('active');
        }
    });

    if (tabName === 'history') {
        loadNotifications();
    } else if (tabName === 'analytics') {
        loadAnalytics();
    }
}

// Notification Actions
function viewNotification(id) {
    console.log('View notification:', id);
    // Implement view details modal
}

function editNotification(id) {
    console.log('Edit notification:', id);
    // Implement edit functionality
}

async function deleteNotification(id) {
    if (!confirm('Are you sure you want to delete this notification?')) {
        return;
    }

    try {
        const response = await fetch(`/api/notifications/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showAlert('Notification deleted successfully', 'success');
            loadNotifications();
            loadAnalytics();
        } else {
            showAlert('Failed to delete notification', 'error');
        }
    } catch (error) {
        console.error('Error deleting notification:', error);
        showAlert('An error occurred', 'error');
    }
}

// Utility Functions
function getTypeIcon(type) {
    const icons = {
        announcement: '📢',
        service_update: '🔄',
        payment_reminder: '💰',
        document_ready: '📄',
        appointment: '📅',
        system_alert: '⚠️',
        training: '🎓',
        feedback_request: '💬'
    };
    return icons[type] || '📢';
}

function getPriorityClass(priority) {
    const classes = {
        low: 'priority-low',
        medium: 'priority-medium',
        high: 'priority-high',
        urgent: 'priority-urgent'
    };
    return classes[priority] || 'priority-medium';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (hours < 48) return 'Yesterday';
    
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}