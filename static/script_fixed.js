// FIXED: Citizen Services Portal - Main Script with Working Search

let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;
let searchCache = {}; // Cache search results

// ============================================
// INITIALIZATION
// ============================================
window.onload = async () => {
    console.log("🚀 Initializing Citizen Services Portal...");
    await loadCategories();
    await loadServices();
    await loadAds();
    
    // Setup search listeners
    setupSearchBar();
    
    console.log("✅ Portal ready!");
};

// ============================================
// SEARCH BAR SETUP (FIXED)
// ============================================
function setupSearchBar() {
    const searchInput = document.getElementById("search-input");
    const searchBtn = document.querySelector(".search-row button");
    
    if (!searchInput || !searchBtn) {
        console.error("Search elements not found");
        return;
    }
    
    // Enter key
    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            handleSearch();
        }
    });
    
    // Click button
    searchBtn.onclick = handleSearch;
    
    console.log("✅ Search bar configured");
}

// ============================================
// AI SEARCH (FIXED)
// ============================================
async function handleSearch() {
    const query = document.getElementById("search-input").value.trim();
    
    if (!query) {
        alert("Please enter a search query");
        return;
    }
    
    if (query.length < 3) {
        alert("Please enter at least 3 characters");
        return;
    }
    
    const resultsDiv = document.getElementById("ai-results");
    const answerDiv = document.getElementById("ai-answer");
    
    // Show loading
    resultsDiv.style.display = "block";
    answerDiv.innerHTML = `
        <div style="text-align:center; padding:20px;">
            <div class="spinner"></div>
            <p style="color:#666; margin-top:10px;">🔍 Searching through government services...</p>
        </div>
    `;
    
    // Check cache first
    if (searchCache[query]) {
        console.log("Using cached result for:", query);
        displaySearchResults(searchCache[query]);
        return;
    }
    
    try {
        const response = await fetch('/api/ai/search', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ 
                query: query,
                top_k: 5,
                language: lang 
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache result
        searchCache[query] = data;
        
        displaySearchResults(data);
        
        // Log engagement
        logEngagement(query, 'AI Search');
        
    } catch (error) {
        console.error('Search error:', error);
        
        answerDiv.innerHTML = `
            <div style="background:#fee; padding:20px; border-radius:8px; border-left:4px solid #dc3545;">
                <h4 style="color:#dc3545; margin:0 0 10px 0;">❌ Search Failed</h4>
                <p style="margin:5px 0;"><strong>Error:</strong> ${error.message}</p>
                <p style="margin:10px 0 5px 0;"><strong>Possible causes:</strong></p>
                <ul style="margin:5px 0; padding-left:20px;">
                    <li>Search index not built yet</li>
                    <li>Server connection issue</li>
                    <li>Invalid search query</li>
                </ul>
                <p style="margin:10px 0 0 0;">
                    <strong>Quick fix:</strong> Run <code style="background:#333; color:#0f0; padding:2px 6px; border-radius:3px;">python build_ai_index_fixed.py</code>
                </p>
            </div>
        `;
    }
}

function displaySearchResults(data) {
    const answerDiv = document.getElementById("ai-answer");
    
    if (data.error) {
        answerDiv.innerHTML = `
            <div style="background:#fff3cd; padding:15px; border-radius:8px; border-left:4px solid #ffc107;">
                <h4 style="color:#856404; margin:0 0 10px 0;">⚠️ ${data.error}</h4>
                <p style="margin:0;">Please try:</p>
                <ul style="margin:10px 0; padding-left:20px;">
                    <li>Different keywords</li>
                    <li>Simpler language</li>
                    <li>Browse categories on the left</li>
                </ul>
            </div>
        `;
        return;
    }
    
    if (!data.results || data.results.length === 0) {
        answerDiv.innerHTML = `
            <div style="background:#e7f3ff; padding:20px; border-radius:8px; border-left:4px solid#3b82f6;">
                <h4 style="color:#1e40af; margin:0 0 10px 0;">🔍 No Results Found</h4>
                <p style="margin:5px 0;"><strong>Query:</strong> "${data.query}"</p>
                <p style="margin:10px 0 5px 0;"><strong>Try:</strong></p>
                <ul style="margin:5px 0; padding-left:20px;">
                    <li>Different keywords (e.g., "passport" instead of "travel document")</li>
                    <li>Simpler terms (e.g., "renew passport" instead of "passport renewal procedure")</li>
                    <li>Browse categories ← on the left sidebar</li>
                </ul>
            </div>
        `;
        return;
    }
    
    // Display results
    let html = `
        <div style="background:#f0f9ff; padding:15px; border-radius:8px; border-left:4px solid #0b3b8c; margin-bottom:15px;">
            <h4 style="color:#0b3b8c; margin:0 0 8px 0;">🎯 Found ${data.results.length} relevant results</h4>
            <p style="margin:0; font-size:14px; color:#666;">
                <strong>Query:</strong> "${data.query}" | 
                <strong>Method:</strong> ${data.method || 'vector search'} |
                <strong>Language:</strong> ${data.language || 'en'}
            </p>
        </div>
    `;
    
    data.results.forEach((result, i) => {
        const score = result.score || 0;
        const scorePercent = Math.round(score * 100);
        const scoreColor = score > 0.8 ? '#28a745' : score > 0.5 ? '#ffc107' : '#6c757d';
        
        html += `
            <div style="background:white; padding:15px; margin:12px 0; border-left:4px solid ${scoreColor}; border-radius:6px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:10px;">
                    <h4 style="margin:0; color:#0b3b8c; font-size:16px;">
                        ${i + 1}. ${result.service_name || 'Unknown Service'}
                    </h4>
                    <span style="background:${scoreColor}; color:white; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:bold;">
                        ${scorePercent}% match
                    </span>
                </div>
                
                <p style="margin:8px 0; font-size:14px;">
                    <strong style="color:#495057;">Q:</strong> 
                    <span style="color:#212529;">${result.question_text || result.question?.en || 'N/A'}</span>
                </p>
                
                <p style="margin:8px 0; font-size:14px; color:#6c757d;">
                    <strong style="color:#495057;">A:</strong> 
                    ${result.answer_text || result.answer?.en || 'N/A'}
                </p>
                
                ${result.metadata?.downloads?.length ? `
                    <p style="margin:8px 0; font-size:13px;">
                        📄 <strong>Forms:</strong> 
                        ${result.metadata.downloads.map(d => 
                            `<a href="${d}" target="_blank" style="color:#0b61d4; text-decoration:none;">${d.split('/').pop()}</a>`
                        ).join(', ')}
                    </p>
                ` : ''}
                
                ${result.metadata?.location ? `
                    <p style="margin:8px 0; font-size:13px;">
                        📍 <a href="${result.metadata.location}" target="_blank" style="color:#0b61d4; text-decoration:none;">View Location</a>
                    </p>
                ` : ''}
                
                ${result.metadata?.instructions ? `
                    <p style="margin:8px 0; font-size:13px; background:#f8f9fa; padding:8px; border-radius:4px;">
                        ℹ️ <strong>Instructions:</strong> ${result.metadata.instructions}
                    </p>
                ` : ''}
            </div>
        `;
    });
    
    answerDiv.innerHTML = html;
}

// ============================================
// LOAD DATA
// ============================================
async function loadCategories() {
    try {
        const res = await fetch("/api/categories");
        categories = await res.json();
        const el = document.getElementById("category-list");
        el.innerHTML = "";
        
        categories.forEach(c => {
            const btn = document.createElement("div");
            btn.className = "cat-item";
            btn.textContent = c.name?.[lang] || c.name?.en || c.id;
            btn.onclick = () => loadMinistriesInCategory(c);
            el.appendChild(btn);
        });
    } catch (error) {
        console.error("Error loading categories:", error);
    }
}

async function loadServices() {
    try {
        const res = await fetch("/api/services");
        services = await res.json();
        console.log(`✅ Loaded ${services.length} services`);
        
        const list = document.getElementById("service-list");
        if (!list) return;
        
        list.innerHTML = "";
        
        if (services.length === 0) {
            list.innerHTML = "<li style='background:#ef4444; padding:10px;'>No services found. Run seed_data.py</li>";
            return;
        }
        
        services.forEach(s => {
            let li = document.createElement("li");
            li.textContent = s.name?.[lang] || s.name?.en;
            li.onclick = () => loadSubservices(s);
            list.appendChild(li);
        });
    } catch (error) {
        console.error("Error loading services:", error);
    }
}

async function loadAds() {
    try {
        const res = await fetch("/api/ads");
        const ads = await res.json();
        const el = document.getElementById("ads-area");
        
        if (ads.length === 0) {
            el.style.display = 'none';
            return;
        }
        
        el.style.display = 'block';
        el.innerHTML = '<h4>📢 Announcements</h4>';
        
        ads.forEach(a => {
            const card = document.createElement("div");
            card.className = "ad-card";
            card.innerHTML = `
                <a href="${a.link || '#'}" target="_blank">
                    <h4>${a.title?.[lang] || a.title?.en}</h4>
                    <p>${(a.body?.[lang] || a.body?.en || '').substring(0, 80)}...</p>
                </a>
            `;
            el.appendChild(card);
        });
    } catch (error) {
        console.error("Error loading ads:", error);
    }
}

// ============================================
// CATEGORY NAVIGATION
// ============================================
async function loadMinistriesInCategory(cat) {
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;
    
    if (cat.ministry_ids && cat.ministry_ids.length) {
        for (let id of cat.ministry_ids) {
            const s = services.find(svc => svc.id === id);
            if (s && s.subservices) {
                s.subservices.forEach(sub => {
                    let li = document.createElement("li");
                    li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                    li.onclick = () => loadQuestions(s, sub);
                    document.getElementById("sub-list").appendChild(li);
                });
            }
        }
    } else {
        services.filter(s => s.category === cat.id).forEach(s => {
            s.subservices?.forEach(sub => {
                let li = document.createElement("li");
                li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                li.onclick = () => loadQuestions(s, sub);
                document.getElementById("sub-list").appendChild(li);
            });
        });
    }
}

// ============================================
// SERVICE NAVIGATION
// ============================================
function loadSubservices(service) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    const subList = document.getElementById("sub-list");
    subList.innerHTML = "";
    document.getElementById("sub-title").innerText = currentServiceName;
    
    (service.subservices || []).forEach(sub => {
        let li = document.createElement("li");
        li.textContent = sub.name?.[lang] || sub.name?.en;
        li.onclick = () => loadQuestions(service, sub);
        subList.appendChild(li);
    });
}

function loadQuestions(service, sub) {
    currentServiceName = service.name?.[lang] || service.name?.en;
    currentSub = sub;
    
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";
    document.getElementById("q-title").innerText = sub.name?.[lang] || sub.name?.en || sub.id;
    
    (sub.questions || []).forEach(q => {
        let li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en;
        li.onclick = () => showAnswer(service, sub, q);
        qList.appendChild(li);
    });
}

function showAnswer(service, sub, q) {
    let html = `<h3>${q.q?.[lang] || q.q?.en}</h3>`;
    html += `<p>${q.answer?.[lang] || q.answer?.en}</p>`;
    
    if (q.downloads && q.downloads.length) {
        html += `<p><b>📄 Downloads:</b> `;
        q.downloads.forEach(d => {
            html += `<a href="${d}" target="_blank">${d.split("/").pop()}</a> `;
        });
        html += `</p>`;
    }
    
    if (q.location) {
        html += `<p><b>📍 Location:</b> <a href="${q.location}" target="_blank">View on Map</a></p>`;
    }
    
    if (q.instructions) {
        html += `<p><b>ℹ️ Instructions:</b> ${q.instructions}</p>`;
    }
    
    document.getElementById("answer-box").innerHTML = html;
    
    // Log engagement
    logEngagement(q.q?.[lang] || q.q?.en, currentServiceName);
    
    // Show profile modal after 3rd interaction
    const interactionCount = parseInt(localStorage.getItem('interaction_count') || '0') + 1;
    localStorage.setItem('interaction_count', interactionCount);
    
    if (interactionCount === 3 && !localStorage.getItem('profile_completed')) {
        setTimeout(() => showProfileModal(), 2000);
    }
}

// ============================================
// PROGRESSIVE PROFILE
// ============================================
function showProfileModal() {
    document.getElementById("profile-modal").style.display = "flex";
}

function closeProfileModal() {
    document.getElementById("profile-modal").style.display = "none";
}

function profileNext(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step + 1}`).style.display = "block";
}

function profileBack(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step - 1}`).style.display = "block";
}

async function profileSubmit() {
    const data1 = {
        name: document.getElementById("p_name").value,
        age: document.getElementById("p_age").value
    };
    const data2 = {
        email: document.getElementById("p_email").value,
        phone: document.getElementById("p_phone").value
    };
    const data3 = {
        job: document.getElementById("p_job").value,
        notifications: document.getElementById("p_notify")?.checked || false
    };
    
    try {
        let res = await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: data2.email, step: "basic", data: data1 })
        });
        let json = await res.json();
        profile_id = json.profile_id;
        
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "contact", data: data2 })
        });
        
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "employment", data: data3 })
        });
        
        localStorage.setItem('profile_completed', 'true');
        closeProfileModal();
        
        alert("Thank you! Your preferences have been saved.");
        
    } catch (error) {
        console.error("Profile save error:", error);
        alert("Profile save failed. You can continue using the portal.");
        closeProfileModal();
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
                service: service
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
    searchCache = {}; // Clear cache on language change
    loadCategories();
    loadServices();
    loadAds();
    
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
    document.getElementById("ai-results").style.display = "none";
}

// Add CSS for spinner
const style = document.createElement('style');
style.textContent = `
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #0b3b8c;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log("✅ Fixed script loaded successfully!");