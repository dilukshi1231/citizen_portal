// ============================================
// NOTIFICATION SYSTEM - FRONTEND
// Add this to your static/script.js or create static/notifications.js
// ============================================

class NotificationSystem {
    constructor() {
        this.unreadCount = 0;
        this.notifications = [];
        this.userId = null;
        this.userRole = null;
        this.lang = localStorage.getItem('language') || 'en';
        this.pollInterval = null;
        this.isInitialized = false;
    }

    // ============================================
    // INITIALIZATION
    // ============================================
    async initialize(userId, userRole) {
        if (this.isInitialized) return;
        
        this.userId = userId;
        this.userRole = userRole;
        
        console.log('🔔 Initializing Notification System for:', userRole);
        
        // Load notifications
        await this.loadNotifications();
        
        // Create notification UI
        this.createNotificationUI();
        
        // Start polling for new notifications (every 30 seconds)
        this.startPolling();
        
        this.isInitialized = true;
        console.log('✅ Notification System initialized');
    }

    // ============================================
    // UI CREATION
    // ============================================
    createNotificationUI() {
        // Check if notification bell already exists
        if (document.getElementById('notification-bell')) return;
        
        const navbar = document.querySelector('nav') || document.querySelector('header');
        if (!navbar) {
            console.warn('No navbar found for notification bell');
            return;
        }
        
        // Create notification bell HTML
        const bellHTML = `
            <div class="notification-container" style="position: relative; display: inline-block; margin-left: 20px;">
                <button id="notification-bell" class="notification-bell" style="
                    position: relative;
                    background: none;
                    border: none;
                    cursor: pointer;
                    font-size: 24px;
                    color: #333;
                    padding: 8px;
                    border-radius: 50%;
                    transition: all 0.3s;
                ">
                    🔔
                    <span id="notification-badge" class="notification-badge" style="
                        position: absolute;
                        top: 0;
                        right: 0;
                        background: #ef4444;
                        color: white;
                        border-radius: 10px;
                        padding: 2px 6px;
                        font-size: 11px;
                        font-weight: bold;
                        display: none;
                    ">0</span>
                </button>
                
                <div id="notification-dropdown" class="notification-dropdown" style="
                    position: absolute;
                    top: 50px;
                    right: 0;
                    width: 400px;
                    max-height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    display: none;
                    z-index: 1000;
                    overflow: hidden;
                ">
                    <div class="notification-header" style="
                        padding: 16px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <h3 style="margin: 0; font-size: 18px; font-weight: 600;">Notifications</h3>
                        <button id="mark-all-read" style="
                            background: rgba(255,255,255,0.2);
                            border: 1px solid rgba(255,255,255,0.3);
                            color: white;
                            padding: 6px 12px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 12px;
                            transition: all 0.3s;
                        ">Mark All Read</button>
                    </div>
                    
                    <div class="notification-filters" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border-bottom: 1px solid #e9ecef;
                        display: flex;
                        gap: 8px;
                    ">
                        <button class="filter-btn active" data-filter="all" style="
                            padding: 6px 12px;
                            border-radius: 6px;
                            border: 1px solid #dee2e6;
                            background: white;
                            cursor: pointer;
                            font-size: 12px;
                            transition: all 0.3s;
                        ">All</button>
                        <button class="filter-btn" data-filter="unread" style="
                            padding: 6px 12px;
                            border-radius: 6px;
                            border: 1px solid #dee2e6;
                            background: white;
                            cursor: pointer;
                            font-size: 12px;
                            transition: all 0.3s;
                        ">Unread</button>
                    </div>
                    
                    <div id="notification-list" class="notification-list" style="
                        max-height: 400px;
                        overflow-y: auto;
                    ">
                        <div class="loading" style="padding: 20px; text-align: center; color: #6c757d;">
                            Loading notifications...
                        </div>
                    </div>
                    
                    <div class="notification-footer" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border-top: 1px solid #e9ecef;
                        text-align: center;
                    ">
                        <button id="view-all-notifications" style="
                            color: #667eea;
                            background: none;
                            border: none;
                            cursor: pointer;
                            font-size: 14px;
                            font-weight: 500;
                        ">View All Notifications</button>
                    </div>
                </div>
            </div>
        `;
        
        // Insert bell into navbar
        navbar.insertAdjacentHTML('beforeend', bellHTML);
        
        // Add event listeners
        this.attachEventListeners();
        
        // Add CSS for animations
        this.addStyles();
    }

    attachEventListeners() {
        const bell = document.getElementById('notification-bell');
        const dropdown = document.getElementById('notification-dropdown');
        const markAllRead = document.getElementById('mark-all-read');
        const viewAll = document.getElementById('view-all-notifications');
        
        // Toggle dropdown
        bell?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown?.contains(e.target) && e.target !== bell) {
                this.closeDropdown();
            }
        });
        
        // Mark all as read
        markAllRead?.addEventListener('click', () => {
            this.markAllAsRead();
        });
        
        // View all notifications (navigate to notifications page)
        viewAll?.addEventListener('click', () => {
            window.location.href = '/notifications';
        });
        
        // Filter buttons
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                this.filterNotifications(filter);
            });
        });
    }

    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .notification-bell:hover {
                background: #f3f4f6;
                transform: scale(1.1);
            }
            
            .notification-bell.has-unread {
                animation: ring 2s ease-in-out infinite;
            }
            
            @keyframes ring {
                0%, 100% { transform: rotate(0deg); }
                10%, 30% { transform: rotate(-10deg); }
                20%, 40% { transform: rotate(10deg); }
            }
            
            .notification-item {
                padding: 16px;
                border-bottom: 1px solid #e9ecef;
                cursor: pointer;
                transition: all 0.3s;
                position: relative;
            }
            
            .notification-item:hover {
                background: #f8f9fa;
            }
            
            .notification-item.unread {
                background: #eff6ff;
                border-left: 4px solid #3b82f6;
            }
            
            .notification-item.unread::before {
                content: '';
                position: absolute;
                left: 8px;
                top: 50%;
                transform: translateY(-50%);
                width: 8px;
                height: 8px;
                background: #3b82f6;
                border-radius: 50%;
            }
            
            .notification-priority-urgent {
                border-left-color: #ef4444 !important;
            }
            
            .notification-priority-high {
                border-left-color: #f59e0b !important;
            }
            
            .filter-btn.active {
                background: #667eea !important;
                color: white !important;
                border-color: #667eea !important;
            }
            
            #mark-all-read:hover {
                background: rgba(255,255,255,0.3);
            }
            
            .notification-list::-webkit-scrollbar {
                width: 6px;
            }
            
            .notification-list::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            
            .notification-list::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 3px;
            }
            
            .notification-list::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        `;
        document.head.appendChild(style);
    }

    // ============================================
    // NOTIFICATION LOADING
    // ============================================
    async loadNotifications(unreadOnly = false) {
        try {
            const response = await fetch(
                `/api/notifications?user_id=${this.userId}&role=${this.userRole}&lang=${this.lang}&unread_only=${unreadOnly}`
            );
            
            if (!response.ok) throw new Error('Failed to load notifications');
            
            const data = await response.json();
            this.notifications = data.notifications || [];
            this.unreadCount = data.unread_count || 0;
            
            this.updateBadge();
            
            return this.notifications;
        } catch (error) {
            console.error('Error loading notifications:', error);
            return [];
        }
    }

    async filterNotifications(filter) {
        const unreadOnly = filter === 'unread';
        await this.loadNotifications(unreadOnly);
        this.renderNotifications();
    }

    // ============================================
    // UI UPDATES
    // ============================================
    updateBadge() {
        const badge = document.getElementById('notification-badge');
        const bell = document.getElementById('notification-bell');
        
        if (!badge || !bell) return;
        
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'block';
            bell.classList.add('has-unread');
        } else {
            badge.style.display = 'none';
            bell.classList.remove('has-unread');
        }
    }

    renderNotifications() {
        const listEl = document.getElementById('notification-list');
        if (!listEl) return;
        
        if (this.notifications.length === 0) {
            listEl.innerHTML = `
                <div style="padding: 40px 20px; text-align: center; color: #6c757d;">
                    <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
                    <p style="margin: 0;">No notifications</p>
                </div>
            `;
            return;
        }
        
        listEl.innerHTML = this.notifications.map(notif => {
            const priorityClass = notif.priority === 'urgent' || notif.priority === 'high' 
                ? `notification-priority-${notif.priority}` 
                : '';
            
            const icon = this.getNotificationIcon(notif.type);
            const timeAgo = this.getTimeAgo(notif.created_at);
            
            return `
                <div class="notification-item ${notif.is_read ? '' : 'unread'} ${priorityClass}" 
                     data-id="${notif.id}"
                     onclick="notificationSystem.handleNotificationClick('${notif.id}', '${notif.action_url || ''}')">
                    <div style="display: flex; gap: 12px;">
                        <div style="font-size: 24px; flex-shrink: 0;">${icon}</div>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-weight: 600; color: #1f2937; margin-bottom: 4px; font-size: 14px;">
                                ${notif.title}
                            </div>
                            <div style="color: #6b7280; font-size: 13px; margin-bottom: 6px; 
                                        overflow: hidden; text-overflow: ellipsis; display: -webkit-box; 
                                        -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                                ${notif.message}
                            </div>
                            <div style="color: #9ca3af; font-size: 11px;">
                                ${timeAgo}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getNotificationIcon(type) {
        const icons = {
            'announcement': '📢',
            'service_update': '🔄',
            'payment_reminder': '💰',
            'document_ready': '📄',
            'appointment': '📅',
            'system_alert': '⚠️',
            'training': '🎓',
            'feedback': '💬'
        };
        return icons[type] || '🔔';
    }

    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    }

    toggleDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (!dropdown) return;
        
        const isVisible = dropdown.style.display === 'block';
        
        if (isVisible) {
            this.closeDropdown();
        } else {
            dropdown.style.display = 'block';
            this.renderNotifications();
        }
    }

    closeDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    }

    // ============================================
    // NOTIFICATION ACTIONS
    // ============================================
    async handleNotificationClick(notificationId, actionUrl) {
        // Mark as read
        await this.markAsRead(notificationId);
        
        // Navigate if action URL exists
        if (actionUrl && actionUrl !== 'null' && actionUrl !== '') {
            window.location.href = actionUrl;
        }
        
        this.closeDropdown();
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });
            
            if (!response.ok) throw new Error('Failed to mark as read');
            
            const data = await response.json();
            
            // Update unread count
            this.unreadCount = data.unread_count;
            this.updateBadge();
            
            // Update local notification state
            const notif = this.notifications.find(n => n.id === notificationId);
            if (notif) {
                notif.is_read = true;
            }
            
            this.renderNotifications();
            
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/read-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    role: this.userRole
                })
            });
            
            if (!response.ok) throw new Error('Failed to mark all as read');
            
            // Update all notifications
            this.notifications.forEach(n => n.is_read = true);
            this.unreadCount = 0;
            
            this.updateBadge();
            this.renderNotifications();
            
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }

    // ============================================
    // POLLING
    // ============================================
    startPolling() {
        // Poll every 30 seconds for new notifications
        this.pollInterval = setInterval(async () => {
            await this.checkForNewNotifications();
        }, 30000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async checkForNewNotifications() {
        try {
            const response = await fetch(
                `/api/notifications/unread-count?user_id=${this.userId}&role=${this.userRole}`
            );
            
            if (!response.ok) return;
            
            const data = await response.json();
            const newCount = data.unread_count;
            
            // If count increased, show notification and reload
            if (newCount > this.unreadCount) {
                this.showNewNotificationToast();
                await this.loadNotifications();
                this.renderNotifications();
            }
            
            this.unreadCount = newCount;
            this.updateBadge();
            
        } catch (error) {
            console.error('Error checking for new notifications:', error);
        }
    }

    showNewNotificationToast() {
        // Create toast notification
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
            cursor: pointer;
        `;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 24px;">🔔</div>
                <div>
                    <div style="font-weight: 600; margin-bottom: 4px;">New Notification</div>
                    <div style="font-size: 12px; opacity: 0.9;">You have new notifications</div>
                </div>
            </div>
        `;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Click to view
        toast.addEventListener('click', () => {
            this.toggleDropdown();
            toast.remove();
        });
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => toast.remove(), 5000);
    }

    // ============================================
    // CLEANUP
    // ============================================
    destroy() {
        this.stopPolling();
        this.isInitialized = false;
    }
}

// ============================================
// GLOBAL INSTANCE
// ============================================
const notificationSystem = new NotificationSystem();

// Initialize on page load (example - adjust based on your auth system)
window.addEventListener('load', () => {
    // Get user info from your session/auth system
    const userId = sessionStorage.getItem('user_id') || localStorage.getItem('user_id');
    const userRole = sessionStorage.getItem('user_role') || localStorage.getItem('user_role') || 'citizen';
    
    if (userId) {
        notificationSystem.initialize(userId, userRole);
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    notificationSystem.destroy();
});