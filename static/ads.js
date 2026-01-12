// ads.js - Advertisement Display System

class AdManager {
    constructor() {
        this.adContainer = null;
        this.userId = null;
    }
    
    init(userId, containerId = 'ad-container') {
        this.userId = userId;
        this.adContainer = document.getElementById(containerId);
        
        if (!this.adContainer) {
            console.error('Ad container not found');
            return;
        }
    }
    
    async loadAds(pageType = 'home', limit = 3) {
        try {
            const response = await fetch('/api/ads/get_ads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    page_type: pageType,
                    limit: limit
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to load ads');
            }
            
            const data = await response.json();
            this.displayAds(data.ads);
            
        } catch (error) {
            console.error('Error loading ads:', error);
        }
    }
    
    displayAds(ads) {
        if (!ads || ads.length === 0) {
            this.adContainer.innerHTML = '';
            return;
        }
        
        this.adContainer.innerHTML = '';
        
        ads.forEach((ad, index) => {
            const adElement = this.createAdElement(ad, index);
            this.adContainer.appendChild(adElement);
        });
    }
    
    createAdElement(ad, index) {
        const div = document.createElement('div');
        div.className = 'ad-card mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer';
        
        // Add priority badge
        const priorityColors = {
            'high': 'bg-red-500',
            'medium': 'bg-yellow-500',
            'low': 'bg-green-500'
        };
        
        div.innerHTML = `
            <div class="flex items-start space-x-4">
                <!-- Ad Image -->
                <div class="flex-shrink-0">
                    <img src="${ad.image_url}" 
                         alt="${ad.title}" 
                         class="w-24 h-24 object-cover rounded-lg shadow"
                         onerror="this.src='/static/placeholder-ad.png'">
                </div>
                
                <!-- Ad Content -->
                <div class="flex-1">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-bold text-gray-800">
                            ${ad.title}
                        </h3>
                        <span class="px-2 py-1 text-xs text-white rounded-full ${priorityColors[ad.priority]}">
                            ${ad.priority.toUpperCase()}
                        </span>
                    </div>
                    
                    <p class="text-sm text-gray-600 mb-3">
                        ${ad.description}
                    </p>
                    
                    <!-- Targeting Reason -->
                    <p class="text-xs text-gray-500 italic mb-2">
                        <svg class="inline w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                        </svg>
                        ${ad.targeting_reason}
                    </p>
                    
                    <!-- Call to Action -->
                    <button class="mt-2 px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-full hover:bg-blue-700 transition inline-flex items-center">
                        Learn More
                        <svg class="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        // Add click handler
        div.addEventListener('click', () => {
            this.handleAdClick(ad);
        });
        
        return div;
    }
    
    async handleAdClick(ad) {
        // Track the click
        try {
            await fetch(`/api/ads/click/${ad.id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: this.userId })
            });
        } catch (error) {
            console.error('Error tracking ad click:', error);
        }
        
        // Navigate to ad link
        window.location.href = ad.link;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Get user ID from session or global variable
    const userId = getCurrentUserId(); // Replace with your function
    
    if (userId) {
        const adManager = new AdManager();
        adManager.init(userId);
        
        // Determine page type
        const pageType = determinePageType(); // Replace with your logic
        
        // Load ads
        adManager.loadAds(pageType, 3);
    }
});

// Helper function to determine page type
function determinePageType() {
    const path = window.location.pathname;
    if (path.includes('/education')) return 'education';
    if (path.includes('/health')) return 'health';
    if (path.includes('/finance')) return 'finance';
    if (path.includes('/search')) return 'search';
    return 'home';
}