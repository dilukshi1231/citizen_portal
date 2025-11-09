// Citizen Services Portal - Main Script
let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;

// ============================================
// INITIALIZATION
// ============================================
window.onload = async () => {
    console.log("🚀 Initializing Citizen Services Portal...");
    await loadCategories();
    await loadServices();
    await loadAds();
    console.log("✅ Portal ready!");
};

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
        // Fallback: filter by category
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
    
    // Show profile modal after 3rd interaction (non-intrusive)
    const interactionCount = parseInt(localStorage.getItem('interaction_count') || '0') + 1;
    localStorage.setItem('interaction_count', interactionCount);
    
    if (interactionCount === 3 && !localStorage.getItem('profile_completed')) {
        setTimeout(() => showProfileModal(), 2000);
    }
}

// ============================================
// AI SEARCH
// ============================================
async function handleSearch() {
    const query = document.getElementById("search-input").value.trim();
    if (!query) return;
    
    const resultsDiv = document.getElementById("ai-results");
    const answerDiv = document.getElementById("ai-answer");
    
    resultsDiv.style.display = "block";
    answerDiv.innerHTML = '<div style="text-align:center; color:#666;">🔍 Searching...</div>';
    
    try {
        const res = await fetch('/api/ai/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, language: lang })
        });
        
        const data = await res.json();
        
        if (data.error) {
            answerDiv.innerHTML = `<div style="color:#dc3545;">❌ ${data.error}</div>`;
            return;
        }
        
        if (!data.results || data.results.length === 0) {
            answerDiv.innerHTML = `
                <div style="color:#666;">
                    No results found. Try:
                    <ul style="margin:10px 0;">
                        <li>Different keywords</li>
                        <li>Simpler language</li>
                        <li>Browse categories on the left</li>
                    </ul>
                </div>`;
            return;
        }
        
        // Display results
        let html = `<p><b>${data.results.length} relevant results found:</b></p>`;
        
        data.results.slice(0, 3).forEach((result, i) => {
            html += `
                <div style="background:white; padding:12px; margin:10px 0; border-left:4px solid #0b3b8c; border-radius:4px;">
                    <h4 style="margin:0 0 8px 0; color:#0b3b8c;">
                        ${i + 1}. ${result.service_name}
                    </h4>
                    <p style="margin:5px 0;"><b>Q:</b> ${result.question_text}</p>
                    <p style="margin:5px 0; color:#555;"><b>A:</b> ${result.answer_text}</p>
                    ${result.metadata?.downloads?.length ? 
                        `<p style="margin:5px 0; font-size:0.9em;">📄 Forms available</p>` : ''}
                </div>
            `;
        });
        
        answerDiv.innerHTML = html;
        
        // Log search
        logEngagement(query, 'AI Search');
        
    } catch (error) {
        console.error('Search error:', error);
        answerDiv.innerHTML = `<div style="color:#dc3545;">❌ Search failed. Please try again.</div>`;
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
        notifications: document.getElementById("p_notify").checked
    };
    
    try {
        // Save step 1
        let res = await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: data2.email, step: "basic", data: data1 })
        });
        let json = await res.json();
        profile_id = json.profile_id;
        
        // Save step 2
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "contact", data: data2 })
        });
        
        // Save step 3
        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id, step: "employment", data: data3 })
        });
        
        localStorage.setItem('profile_completed', 'true');
        closeProfileModal();
        
        // Thank you message
        alert("Thank you! Your preferences have been saved to help us serve you better.");
        
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
    loadCategories();
    loadServices();
    loadAds();
    
    // Clear current selections
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================
document.getElementById("search-input")?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        handleSearch();
    }
});

console.log("✅ Citizen Services Portal script loaded successfully!");