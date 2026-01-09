// Citizen Services Portal - Main Script (FIXED for new index.html)
let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;
let allOfficers = [];

// ============================================
// INITIALIZATION
// ============================================
window.onload = async () => {
    console.log("🚀 Initializing Citizen Services Portal...");
    await loadCategories();
    await loadServices();
    await loadAds();
    await loadOfficers();
    console.log("✅ Portal ready!");
};

// ============================================
// LOAD DATA
// ============================================
async function loadCategories() {
    try {
        const res = await fetch("/api/categories");
        categories = await res.json();
        console.log("✅ Loaded categories:", categories.length);
    } catch (error) {
        console.error("Error loading categories:", error);
    }
}

async function loadServices() {
    try {
        const response = await fetch('/api/services');
        services = await response.json();
        
        const serviceList = document.getElementById('service-list');
        if (!serviceList) return;
        
        serviceList.innerHTML = '';
        
        services.forEach(service => {
            const li = document.createElement('li');
            li.dataset.id = service.id;
            const serviceName = service.name?.[lang] || service.name?.en || service.id;
            li.textContent = serviceName;
            li.onclick = (e) => {
                e.stopPropagation();
                selectService(service.id, serviceName);
            };
            serviceList.appendChild(li);
        });
        
        console.log(`✅ Loaded ${services.length} services`);
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdownContainer = document.querySelector('.dropdown-container');
            if (dropdownContainer && !dropdownContainer.contains(e.target)) {
                closeDropdown();
            }
        });
        
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

async function loadOfficers() {
    try {
        const res = await fetch("/api/officers");
        allOfficers = await res.json();
        console.log(`✅ Loaded ${allOfficers.length} officers`);
    } catch (error) {
        console.error("Error loading officers:", error);
    }
}

async function loadAds() {
    try {
        const res = await fetch("/api/ads");
        const ads = await res.json();
        const el = document.getElementById("ads-area");
        
        if (!el) return;
        
        if (ads.length === 0) {
            el.innerHTML = '<div class="col-span-full text-center text-gray-500 p-8">No announcements at this time</div>';
            return;
        }
        
        el.innerHTML = ads.map(a => `
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg hover:shadow-md transition">
                <a href="${a.link || '#'}" target="_blank" class="block">
                    <h4 class="font-bold text-yellow-900 mb-2">${a.title?.[lang] || a.title?.en || 'Announcement'}</h4>
                    <p class="text-sm text-yellow-800">${(a.body?.[lang] || a.body?.en || '').substring(0, 120)}...</p>
                </a>
            </div>
        `).join('');
        
        console.log("✅ Loaded announcements");
    } catch (error) {
        console.error("Error loading ads:", error);
    }
}

// ============================================
// DROPDOWN FUNCTIONALITY
// ============================================
let dropdownOpen = false;
let selectedService = null;

function toggleDropdown() {
    const dropdownList = document.getElementById('service-list');
    const arrow = document.querySelector('.dropdown-arrow');
    
    dropdownOpen = !dropdownOpen;
    
    if (dropdownOpen) {
        dropdownList.classList.add('show');
        if (arrow) arrow.classList.add('open');
    } else {
        dropdownList.classList.remove('show');
        if (arrow) arrow.classList.remove('open');
    }
}

function closeDropdown() {
    const dropdownList = document.getElementById('service-list');
    const arrow = document.querySelector('.dropdown-arrow');
    
    dropdownOpen = false;
    if (dropdownList) dropdownList.classList.remove('show');
    if (arrow) arrow.classList.remove('open');
}

function selectService(serviceId, serviceName) {
    // Update dropdown button text
    const dropdownText = document.getElementById('dropdown-text');
    if (dropdownText) {
        dropdownText.textContent = serviceName;
    }
    
    // Mark as selected in the list
    const items = document.querySelectorAll('#service-list li');
    items.forEach(item => {
        item.classList.remove('selected');
        if (item.dataset.id === serviceId) {
            item.classList.add('selected');
        }
    });
    
    selectedService = serviceId;
    closeDropdown();
    
    // Find and load the service
    const service = services.find(s => s.id === serviceId);
    if (service) {
        loadSubservices(service);
    } else {
        console.error('Service not found:', serviceId);
    }
}

// ============================================
// SERVICE NAVIGATION (FIXED FOR NEW HTML)
// ============================================
function loadSubservices(service) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    
    // Show sub-panel
    const subPanel = document.getElementById("sub-panel");
    const subList = document.getElementById("sub-list");
    const subTitle = document.getElementById("sub-title");
    
    if (!subPanel || !subList || !subTitle) {
        console.error("Sub-panel elements not found");
        return;
    }
    
    // Clear previous content
    subList.innerHTML = "";
    
    // Update title
    subTitle.textContent = `${currentServiceName} - Select Service`;
    
    // Show panel
    subPanel.style.display = "block";
    
    // Hide question panel
    const questionPanel = document.getElementById("question-panel");
    if (questionPanel) questionPanel.style.display = "none";
    
    // Hide answer box
    const answerBox = document.getElementById("answer-box");
    if (answerBox) answerBox.innerHTML = "";
    
    // Load subservices
    const subservices = service.subservices || [];
    
    if (subservices.length === 0) {
        subList.innerHTML = '<li class="text-gray-500 p-3">No services available</li>';
        return;
    }
    
    subservices.forEach(sub => {
        const li = document.createElement("li");
        li.textContent = sub.name?.[lang] || sub.name?.en;
        li.className = "bg-white p-3 rounded-lg hover:bg-blue-50 hover:border-blue-500 border-2 border-transparent cursor-pointer transition";
        li.onclick = () => loadQuestions(service, sub);
        subList.appendChild(li);
    });
    
    // Scroll to sub-panel
    subPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function loadQuestions(service, sub) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    currentSub = sub;
    
    const questionPanel = document.getElementById("question-panel");
    const qList = document.getElementById("question-list");
    const qTitle = document.getElementById("q-title");
    
    if (!questionPanel || !qList || !qTitle) {
        console.error("Question panel elements not found");
        return;
    }
    
    // Clear previous content
    qList.innerHTML = "";
    
    // Update title
    qTitle.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
    
    // Show panel
    questionPanel.style.display = "block";
    
    // Hide answer box
    const answerBox = document.getElementById("answer-box");
    if (answerBox) answerBox.innerHTML = "";
    
    // Load questions
    const questions = sub.questions || [];
    
    if (questions.length === 0) {
        qList.innerHTML = '<li class="text-gray-500 p-3">No questions available</li>';
        return;
    }
    
    questions.forEach(q => {
        const li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en;
        li.className = "bg-gray-50 p-3 rounded-lg hover:bg-blue-50 hover:border-blue-500 border-2 border-transparent cursor-pointer transition";
        li.onclick = () => showAnswer(service, sub, q);
        qList.appendChild(li);
    });
    
    // Scroll to question panel
    questionPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showAnswer(service, sub, q) {
    const answerBox = document.getElementById("answer-box");
    if (!answerBox) return;
    
    let html = `
        <div class="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-600">
            <h3 class="text-xl font-bold text-gray-900 mb-4">❓ ${q.q?.[lang] || q.q?.en}</h3>
            <div class="prose max-w-none">
                <p class="text-gray-700 mb-4">${q.answer?.[lang] || q.answer?.en}</p>
            </div>
    `;
    
    if (q.downloads && q.downloads.length) {
        html += `
            <div class="mt-4 p-4 bg-blue-50 rounded-lg">
                <p class="font-bold text-blue-900 mb-2">📄 Downloads:</p>
                <div class="space-y-2">
        `;
        q.downloads.forEach(d => {
            html += `<a href="${d}" target="_blank" class="block text-blue-600 hover:text-blue-800 hover:underline">📎 ${d.split("/").pop()}</a>`;
        });
        html += `</div></div>`;
    }
    
    if (q.location) {
        html += `
            <div class="mt-4 p-4 bg-green-50 rounded-lg">
                <p class="font-bold text-green-900 mb-2">📍 Location:</p>
                <a href="${q.location}" target="_blank" class="text-green-600 hover:text-green-800 hover:underline">View on Map</a>
            </div>
        `;
    }
    
    if (q.instructions) {
        html += `
            <div class="mt-4 p-4 bg-yellow-50 rounded-lg">
                <p class="font-bold text-yellow-900 mb-2">ℹ️ Instructions:</p>
                <p class="text-yellow-800">${q.instructions}</p>
            </div>
        `;
    }
    
    html += `</div>`;
    
    answerBox.innerHTML = html;
    answerBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Log engagement
    logEngagement(q.q?.[lang] || q.q?.en, currentServiceName);
}

// ============================================
// AI SEARCH
// ============================================
async function handleSearch() {
    const query = document.getElementById("search-input").value.trim();
    if (!query) return;
    
    const resultsDiv = document.getElementById("ai-results");
    const answerDiv = document.getElementById("ai-answer");
    
    if (!resultsDiv || !answerDiv) return;
    
    resultsDiv.style.display = "block";
    answerDiv.innerHTML = '<div class="text-center text-gray-600">🔍 Searching...</div>';
    
    try {
        const res = await fetch('/api/ai/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, language: lang })
        });
        
        const data = await res.json();
        
        if (data.error) {
            answerDiv.innerHTML = `<div class="text-red-600">❌ ${data.error}</div>`;
            return;
        }
        
        if (!data.results || data.results.length === 0) {
            answerDiv.innerHTML = `
                <div class="text-gray-600">
                    <p class="mb-2">No results found. Try:</p>
                    <ul class="list-disc list-inside space-y-1">
                        <li>Different keywords</li>
                        <li>Simpler language</li>
                        <li>Browse ministries using the dropdown above</li>
                    </ul>
                </div>`;
            return;
        }
        
        // Display results
        let html = `<p class="font-bold mb-3">Found ${data.results.length} relevant results:</p>`;
        
        data.results.slice(0, 3).forEach((result, i) => {
            html += `
                <div class="bg-white p-4 mb-3 rounded-lg border-l-4 border-blue-600 shadow-sm">
                    <h4 class="font-bold text-blue-900 mb-2">
                        ${i + 1}. ${result.service_name}
                    </h4>
                    <p class="text-sm mb-2"><strong>Q:</strong> ${result.question_text}</p>
                    <p class="text-sm text-gray-700"><strong>A:</strong> ${result.answer_text}</p>
                    ${result.metadata?.downloads?.length ? 
                        `<p class="text-xs text-green-600 mt-2">📄 Forms available</p>` : ''}
                </div>
            `;
        });
        
        answerDiv.innerHTML = html;
        
        // Log search
        logEngagement(query, 'AI Search');
        
    } catch (error) {
        console.error('Search error:', error);
        answerDiv.innerHTML = `<div class="text-red-600">❌ Search failed. Please try again.</div>`;
    }
}

// ============================================
// ENGAGEMENT LOGGING
// ============================================
async function logEngagement(question, service) {
    try {
        await fetch("/api/engagement", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: profile_id,
                age: localStorage.getItem('user_age'),
                job: localStorage.getItem('user_job'),
                desires: [],
                question_clicked: question,
                service: service,
                language: lang
            })
        });
    } catch (error) {
        console.error("Engagement logging failed:", error);
    }
}

// ============================================
// LANGUAGE SWITCHING
// ============================================
function setLang(l) {
    lang = l;
    
    // Update nav language selector if exists
    const navLang = document.getElementById("nav-language");
    if (navLang) navLang.value = l;
    
    // Reload data
    loadServices();
    loadAds();
    
    // Clear current selections
    const subPanel = document.getElementById("sub-panel");
    const questionPanel = document.getElementById("question-panel");
    const answerBox = document.getElementById("answer-box");
    
    if (subPanel) subPanel.style.display = "none";
    if (questionPanel) questionPanel.style.display = "none";
    if (answerBox) answerBox.innerHTML = "";
    
    // Reset dropdown
    const dropdownText = document.getElementById("dropdown-text");
    if (dropdownText) dropdownText.textContent = "Select a Ministry / Department";
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                handleSearch();
            }
        });
    }
});

console.log("✅ Citizen Services Portal script loaded successfully!");
