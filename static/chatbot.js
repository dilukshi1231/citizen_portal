// AI Citizen Services Chatbot - Enhanced with Dropdown Ministry Selection

class CitizenChatbot {
    constructor() {
        this.services = [];
        this.filteredServices = [];
        this.selectedMinistry = null;
        this.selectedLanguage = 'en';
        this.messages = [];
        this.loading = false;
        this.showChat = false;
        this.searchQuery = '';
        
        this.languages = {
            en: 'English',
            si: 'සිංහල',
            ta: 'தமிழ்'
        };
        
        // Multilingual UI text
        this.translations = {
            en: {
                portalTitle: 'Citizen Services Portal',
                portalSubtitle: 'Select your language and ministry to get AI-powered assistance',
                searchPlaceholder: 'Search ministries...',
                servicesAvailable: 'services available',
                askAI: 'Ask AI Assistant',
                back: '← Back',
                placeholder: 'Ask a question...',
                aiAssistant: 'AI Assistant',
                noResults: 'No ministries found',
                clearSearch: 'Clear search',
                allMinistries: 'Select Ministry',
                popularServices: 'Popular Services',
                selectMinistry: '-- Select a Ministry --',
                welcomeMessage: (ministryName) => `Welcome to ${ministryName}! I'm here to help you with information about our services. How can I assist you today?`
            },
            si: {
                portalTitle: 'පුරවැසි සේවා ද්වාරය',
                portalSubtitle: 'AI ශක්තිමත් සහාය ලබා ගැනීමට ඔබේ භාෂාව සහ අමාත්‍යාංශය තෝරන්න',
                searchPlaceholder: 'අමාත්‍යාංශ සොයන්න...',
                servicesAvailable: 'සේවා ලබා ගත හැක',
                askAI: 'AI සහායක ඇසීම',
                back: '← ආපසු',
                placeholder: 'ප්‍රශ්නයක් අසන්න...',
                aiAssistant: 'AI සහායක',
                noResults: 'අමාත්‍යාංශ හමු නොවිණි',
                clearSearch: 'සෙවුම මකන්න',
                allMinistries: 'අමාත්‍යාංශය තෝරන්න',
                popularServices: 'ජනප්‍රිය සේවා',
                selectMinistry: '-- අමාත්‍යාංශයක් තෝරන්න --',
                welcomeMessage: (ministryName) => `${ministryName} වෙත සාදරයෙන් පිළිගනිමු! අපගේ සේවා පිළිබඳ තොරතුරු සමඟ ඔබට උදව් කිරීමට මම මෙහි සිටිමි. අද මට ඔබට කෙසේ සහාය විය හැකිද?`
            },
            ta: {
                portalTitle: 'குடிமக்கள் சேவைகள் நுழைவாயில்',
                portalSubtitle: 'AI இயக்கப்பட்ட உதவியைப் பெற உங்கள் மொழி மற்றும் அமைச்சகத்தைத் தேர்ந்தெடுக்கவும்',
                searchPlaceholder: 'அமைச்சகங்களை தேடுங்கள்...',
                servicesAvailable: 'சேவைகள் கிடைக்கின்றன',
                askAI: 'AI உதவியாளரிடம் கேளுங்கள்',
                back: '← பின்னால்',
                placeholder: 'கேள்வி கேளுங்கள்...',
                aiAssistant: 'AI உதவியாளர்',
                noResults: 'அமைச்சகங்கள் காணப்படவில்லை',
                clearSearch: 'தேடலை அழிக்கவும்',
                allMinistries: 'அமைச்சகத்தைத் தேர்ந்தெடுக்கவும்',
                popularServices: 'பிரபலமான சேவைகள்',
                selectMinistry: '-- அமைச்சகத்தைத் தேர்ந்தெடுக்கவும் --',
                welcomeMessage: (ministryName) => `${ministryName} க்கு வரவேற்கிறோம்! எங்கள் சேவைகள் பற்றிய தகவல்களுடன் உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?`
            }
        };
        
        // Category icons
        this.categoryIcons = {
            'cat_it': '💻',
            'cat_education': '📚',
            'cat_health': '🏥',
            'cat_transport': '🚗',
            'cat_immigration': '🛂',
            'cat_public': '🏛️'
        };
        
        this.init();
    }
    
    async init() {
        await this.loadServices();
        this.filteredServices = this.services;
        this.render();
    }
    
    async loadServices() {
        try {
            const response = await fetch('/api/services');
            this.services = await response.json();
            console.log('Loaded services:', this.services.length);
        } catch (error) {
            console.error('Error loading services:', error);
            this.services = [];
        }
    }
    
    filterServices(query) {
        // Kept for compatibility but not actively used
        this.searchQuery = '';
        this.filteredServices = this.services;
    }
    
    clearSearch() {
        // Kept for compatibility but not actively used
        this.searchQuery = '';
        this.filteredServices = this.services;
        this.render();
    }
    
    handleDropdownChange(ministryId) {
        if (ministryId) {
            this.startChat(ministryId);
        }
    }
    
    startChat(ministryId) {
        this.selectedMinistry = this.services.find(s => s.id === ministryId);
        if (!this.selectedMinistry) {
            console.error('Ministry not found:', ministryId);
            return;
        }
        
        this.showChat = true;
        const ministryName = this.selectedMinistry.name[this.selectedLanguage] || this.selectedMinistry.name.en;
        
        this.messages = [{
            role: 'assistant',
            content: this.translations[this.selectedLanguage].welcomeMessage(ministryName),
            timestamp: new Date()
        }];
        this.render();
    }
    
    resetChat() {
        this.showChat = false;
        this.selectedMinistry = null;
        this.messages = [];
        this.searchQuery = '';
        this.filteredServices = this.services;
        this.render();
    }
    
    setLanguage(lang) {
        this.selectedLanguage = lang;
        
        if (this.showChat && this.selectedMinistry && this.messages.length > 0) {
            const ministryName = this.selectedMinistry.name[lang] || this.selectedMinistry.name.en;
            this.messages[0] = {
                role: 'assistant',
                content: this.translations[lang].welcomeMessage(ministryName),
                timestamp: this.messages[0].timestamp
            };
        }
        
        this.render();
    }
    
    async sendMessage(message) {
        if (!message.trim() || !this.selectedMinistry) return;
        
        this.messages.push({
            role: 'user',
            content: message,
            timestamp: new Date()
        });
        
        this.loading = true;
        this.render();
        
        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: message,
                    ministry_id: this.selectedMinistry.id,
                    language: this.selectedLanguage
                })
            });
            
            const data = await response.json();
            
            this.messages.push({
                role: 'assistant',
                content: data.answer || this.getErrorMessage(),
                timestamp: new Date()
            });
        } catch (error) {
            console.error('Error:', error);
            this.messages.push({
                role: 'assistant',
                content: this.getErrorMessage(),
                timestamp: new Date()
            });
        } finally {
            this.loading = false;
            this.render();
            this.scrollToBottom();
        }
    }
    
    getErrorMessage() {
        const errorMessages = {
            en: 'I apologize, but I encountered an error. Please try again.',
            si: 'මට කණගාටුයි, නමුත් මට දෝෂයක් ඇති විය. කරුණාකර නැවත උත්සාහ කරන්න.',
            ta: 'மன்னிக்கவும், ஆனால் எனக்கு ஒரு பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.'
        };
        return errorMessages[this.selectedLanguage] || errorMessages.en;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            const messagesContainer = document.getElementById('messages-container');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }, 100);
    }
    
    render() {
        const app = document.getElementById('app');
        
        if (!this.showChat) {
            app.innerHTML = this.renderMinistrySelection();
            this.attachMinistryEvents();
        } else {
            app.innerHTML = this.renderChatInterface();
            this.attachChatEvents();
            this.scrollToBottom();
        }
    }
    
    renderMinistrySelection() {
        const t = this.translations[this.selectedLanguage];
        
        const languageButtons = Object.entries(this.languages).map(([code, name]) => `
            <button 
                onclick="chatbot.setLanguage('${code}')" 
                class="px-6 py-2 rounded-lg font-medium transition-all ${
                    this.selectedLanguage === code
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                }"
            >
                🌐 ${name}
            </button>
        `).join('');
        
        // Ministry Dropdown
        const ministryOptions = this.services.map(service => {
            const serviceName = service.name[this.selectedLanguage] || service.name.en || 'Unknown';
            const categoryIcon = this.categoryIcons[service.category] || '🏢';
            return `<option value="${service.id}">${categoryIcon} ${serviceName}</option>`;
        }).join('');
        
        const dropdownBar = `
            <div class="max-w-2xl mx-auto mb-8">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    ${t.allMinistries}
                </label>
                <div class="relative">
                    <select 
                        id="ministry-dropdown"
                        onchange="chatbot.handleDropdownChange(this.value)"
                        class="w-full px-5 py-4 pr-12 text-lg border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm appearance-none bg-white cursor-pointer"
                    >
                        <option value="">${t.selectMinistry}</option>
                        ${ministryOptions}
                    </select>
                    <svg class="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </div>
            </div>
        `;
        
        return `
            <div class="min-h-screen p-6 flex items-center justify-center">
                <div class="max-w-3xl w-full">
                    <!-- Header -->
                    <div class="text-center mb-12">
                        <h1 class="text-5xl font-bold text-gray-900 mb-4">
                            ${t.portalTitle}
                        </h1>
                        <p class="text-xl text-gray-600">
                            ${t.portalSubtitle}
                        </p>
                    </div>
                    
                    <!-- Language Selector -->
                    <div class="flex justify-center gap-3 mb-12">
                        ${languageButtons}
                    </div>
                    
                    <!-- Ministry Dropdown -->
                    ${dropdownBar}
                    
                    <!-- Footer Info -->
                    <div class="mt-12 text-center text-sm text-gray-500">
                        <p>💡 ${t.portalSubtitle}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderChatInterface() {
        if (!this.selectedMinistry) {
            return '<div class="p-6">Error: No ministry selected</div>';
        }
        
        const t = this.translations[this.selectedLanguage];
        
        const languageButtons = Object.entries(this.languages).map(([code, name]) => `
            <button 
                onclick="chatbot.setLanguage('${code}')" 
                class="px-3 py-1 rounded text-sm ${
                    this.selectedLanguage === code
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }"
            >
                ${name}
            </button>
        `).join('');
        
        const messagesHtml = this.messages.map((message, index) => {
            const isUser = message.role === 'user';
            return `
                <div class="flex gap-3 mb-4 message-enter ${isUser ? 'flex-row-reverse' : ''}">
                    <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-purple-500 to-pink-500'
                    }">
                        ${isUser ? '👤' : '🤖'}
                    </div>
                    <div class="flex-1 max-w-2xl ${isUser ? 'text-right' : ''}">
                        <div class="inline-block px-4 py-3 rounded-2xl ${
                            isUser
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-900 shadow-md'
                        }">
                            <p class="whitespace-pre-line">${this.escapeHtml(message.content)}</p>
                        </div>
                        <p class="text-xs text-gray-500 mt-1 px-2">
                            ${message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                        </p>
                    </div>
                </div>
            `;
        }).join('');
        
        const loadingHtml = this.loading ? `
            <div class="flex gap-3 mb-4">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    🤖
                </div>
                <div class="bg-white px-4 py-3 rounded-2xl shadow-md">
                    <div class="flex gap-2">
                        <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                        <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        <div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                    </div>
                </div>
            </div>
        ` : '';
        
        return `
            <div class="h-screen flex flex-col">
                <!-- Header -->
                <div class="bg-white shadow-md p-4 border-b">
                    <div class="max-w-4xl mx-auto flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <button onclick="chatbot.resetChat()" class="text-gray-600 hover:text-gray-900 font-medium">
                                ${t.back}
                            </button>
                            <div class="h-8 w-px bg-gray-300"></div>
                            <div class="bg-gradient-to-br from-blue-500 to-blue-600 p-2 rounded-lg text-white text-xl">
                                ${this.categoryIcons[this.selectedMinistry.category] || '🏢'}
                            </div>
                            <div>
                                <h2 class="font-semibold text-gray-900">
                                    ${this.selectedMinistry.name[this.selectedLanguage] || this.selectedMinistry.name.en}
                                </h2>
                                <p class="text-xs text-gray-500">${t.aiAssistant}</p>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            ${languageButtons}
                        </div>
                    </div>
                </div>
                
                <!-- Messages -->
                <div id="messages-container" class="flex-1 overflow-y-auto p-4 bg-gradient-to-br from-blue-50 to-indigo-100">
                    <div class="max-w-4xl mx-auto">
                        ${messagesHtml}
                        ${loadingHtml}
                    </div>
                </div>
                
                <!-- Input -->
                <div class="bg-white border-t p-4">
                    <div class="max-w-4xl mx-auto flex gap-3">
                        <input 
                            type="text" 
                            id="message-input"
                            placeholder="${t.placeholder}"
                            ${this.loading ? 'disabled' : ''}
                            class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button 
                            onclick="chatbot.handleSendClick()"
                            ${this.loading ? 'disabled' : ''}
                            class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachMinistryEvents() {
        // Focus dropdown when page loads
        const dropdown = document.getElementById('ministry-dropdown');
        if (dropdown) {
            dropdown.focus();
        }
    }
    
    attachChatEvents() {
        const input = document.getElementById('message-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.loading) {
                    this.handleSendClick();
                }
            });
            input.focus();
        }
    }
    
    handleSendClick() {
        const input = document.getElementById('message-input');
        if (input && input.value.trim()) {
            this.sendMessage(input.value);
            input.value = '';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is ready
let chatbot;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatbot = new CitizenChatbot();
    });
} else {
    chatbot = new CitizenChatbot();
}