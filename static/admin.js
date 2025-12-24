

document.getElementById("login-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const res = await fetch('/admin/login', { method:'POST', body: form });
  if (res.redirected) window.location = res.url;
  else {
    loadDashboard();
  }
});

async function loadDashboard() {
  const dashEl = document.getElementById("dashboard");
  try {
    const r = await fetch('/api/admin/insights');
    if (r.status === 401) {
      document.getElementById("login-box").style.display = "block";
      dashEl.style.display = "none";
      return;
    }
    const data = await r.json();
    document.getElementById("login-box").style.display = "none";
    dashEl.style.display = "block";

    // Check index status
    checkIndexStatus();

    // Age Chart
    new Chart(document.getElementById("ageChart"), {
      type:'bar',
      data: {
        labels: Object.keys(data.age_groups),
        datasets: [{
          label: "Users by Age Group",
          data: Object.values(data.age_groups),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: 'Age Distribution' }
        }
      }
    });

    // Jobs Chart
    new Chart(document.getElementById("jobChart"), {
      type:'pie',
      data: {
        labels: Object.keys(data.jobs).slice(0, 8),
        datasets: [{
          label: "Jobs",
          data: Object.values(data.jobs).slice(0, 8),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(199, 199, 199, 0.6)',
            'rgba(83, 102, 255, 0.6)'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: 'Job Distribution' }
        }
      }
    });

    // Services Chart
    new Chart(document.getElementById("serviceChart"), {
      type:'doughnut',
      data: {
        labels: Object.keys(data.services).slice(0, 10),
        datasets: [{
          label: "Services",
          data: Object.values(data.services).slice(0, 10),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(199, 199, 199, 0.6)',
            'rgba(83, 102, 255, 0.6)',
            'rgba(255, 99, 255, 0.6)',
            'rgba(99, 255, 132, 0.6)',
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: 'Top 10 Services' }
        }
      }
    });

    // Questions Chart
    new Chart(document.getElementById("questionChart"), {
      type:'bar',
      data: {
        labels: Object.keys(data.questions).slice(0, 10).map(q => q.substring(0, 30) + '...'),
        datasets: [{
          label: "Top Questions",
          data: Object.values(data.questions).slice(0, 10),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        indexAxis: 'y',
        plugins: {
          title: { display: true, text: 'Top 10 Questions' }
        }
      }
    });

    // Premium list
    const pl = document.getElementById("premiumList");
    if (data.premium_suggestions.length) {
      pl.innerHTML = data.premium_suggestions
        .map(p => `
          <div style="background:#fff3cd;padding:12px;margin:8px 0;border-left:4px solid #ffc107;border-radius:4px;">
            <strong>User:</strong> ${p.user || 'Anonymous'} | 
            <strong>Question:</strong> ${p.question} | 
            <strong>Asked ${p.count} times</strong>
            <span style="float:right;background:#dc3545;color:white;padding:4px 8px;border-radius:12px;font-size:11px;">HIGH PRIORITY</span>
          </div>
        `).join("");
    } else {
      pl.innerHTML = "<div style='color:#999;padding:20px;text-align:center;'>No premium help suggestions yet</div>";
    }

    // Engagements list
    const res = await fetch('/api/admin/engagements');
    const items = await res.json();
    const tbody = document.querySelector("#engTable tbody");
    tbody.innerHTML = "";
    
    items.slice(0, 100).forEach(it => {
      const chatType = it.chat_type === 'ai_enhanced' ? '<span style="background:#28a745;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">AI Enhanced</span>' : '';
      const row = `<tr>
        <td>${it.age || 'N/A'}</td>
        <td>${it.job || 'N/A'}</td>
        <td>${(it.desires || []).join(", ") || 'N/A'}</td>
        <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;">${it.question_clicked || 'N/A'} ${chatType}</td>
        <td>${it.service || 'N/A'}</td>
        <td style="font-size:11px;color:#666;">${it.timestamp || 'N/A'}</td>
      </tr>`;
      tbody.insertAdjacentHTML('beforeend', row);
    });
  } catch (err) {
    console.error(err);
    alert('Error loading dashboard: ' + err.message);
  }
}

// ============================================
// AI INDEX MANAGEMENT
// ============================================
async function checkIndexStatus() {
  try {
    const res = await fetch('/api/ai/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'test', top_k: 1 })
    });
    
    const statusEl = document.getElementById('indexStatus');
    
    if (res.ok) {
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        statusEl.textContent = '✅ Index Ready';
        statusEl.style.background = 'rgba(40, 167, 69, 0.3)';
      } else {
        statusEl.textContent = '⚠️ Index Empty';
        statusEl.style.background = 'rgba(255, 193, 7, 0.3)';
      }
    } else {
      statusEl.textContent = '❌ Not Built';
      statusEl.style.background = 'rgba(220, 53, 69, 0.3)';
    }
  } catch (err) {
    console.error('Index check failed:', err);
    document.getElementById('indexStatus').textContent = '❓ Unknown';
  }
}

async function rebuildIndex() {
  if (!confirm('Rebuild the AI search index?\n\nThis will:\n- Re-generate embeddings for all Q&A pairs\n- Update the FAISS vector database\n- Take 30-60 seconds\n\nContinue?')) {
    return;
  }

  const btn = document.getElementById('rebuildIndexBtn');
  const status = document.getElementById('rebuildStatus');
  const originalText = btn.innerHTML;

  btn.disabled = true;
  btn.innerHTML = '⏳ Building index, please wait...';
  status.innerHTML = '<div class="alert alert-info">🔄 Building AI search index... This may take up to 60 seconds.</div>';

  try {
    const startTime = Date.now();
    const res = await fetch('/api/admin/rebuild-index', {
      method: 'POST'
    });

    const data = await res.json();
    const duration = ((Date.now() - startTime) / 1000).toFixed(1);

    if (data.status === 'success') {
      status.innerHTML = `
        <div class="alert alert-success">
          ✅ ${data.message}
          <br><small>Completed in ${duration} seconds</small>
          ${data.details ? `<br><small>${data.details}</small>` : ''}
        </div>
      `;
      
      setTimeout(checkIndexStatus, 1000);
    } else {
      status.innerHTML = `
        <div class="alert alert-danger">
          ❌ Error: ${data.error}
          <br><small>Check console for details</small>
        </div>
      `;
      console.error('Index build error:', data);
    }
  } catch (error) {
    status.innerHTML = `
      <div class="alert alert-danger">
        ❌ Network error: ${error.message}
        <br><small>Make sure the server is running and build_ai_index.py exists</small>
      </div>
    `;
    console.error('Network error:', error);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
}
// Update active button state
function setActiveAgeButton(ageGroup) {
    document.querySelectorAll('.btn-age-group').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = Array.from(document.querySelectorAll('.btn-age-group'))
        .find(btn => btn.textContent.includes(ageGroup) || btn.onclick.toString().includes(`'${ageGroup}'`));
    
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}
// Age Group Question Analytics
async function showAgeGroupQuestions(ageGroup) {
    setActiveAgeButton(ageGroup);
    const resultsDiv = document.getElementById('age-group-results');
    const chartCanvas = document.getElementById('age-lang-chart');
    
    resultsDiv.innerHTML = '<div style="text-align:center;padding:20px;">📊 Loading data...</div>';
    
    try {
        const res = await fetch('/api/admin/questions-by-age', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ age_group: ageGroup })
        });
        
        const data = await res.json();
        
        if (data.error) {
            resultsDiv.innerHTML = `<div class="alert alert-danger">❌ ${data.error}</div>`;
            return;
        }
        
        // Render results
        let html = `
            <div style="background:#f8f9fa;padding:15px;border-radius:8px;margin-bottom:20px;">
                <h4 style="margin:0 0 10px 0;">📊 Age Group: ${data.age_group}</h4>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px;">
                    <div style="background:white;padding:12px;border-radius:6px;text-align:center;">
                        <div style="font-size:24px;font-weight:bold;color:#0b3b8c;">${data.total_engagements}</div>
                        <div style="font-size:12px;color:#666;">Total Engagements</div>
                    </div>
                    <div style="background:white;padding:12px;border-radius:6px;text-align:center;">
                        <div style="font-size:24px;font-weight:bold;color:#28a745;">${data.questions.length}</div>
                        <div style="font-size:12px;color:#666;">Unique Questions</div>
                    </div>
                    <div style="background:white;padding:12px;border-radius:6px;text-align:center;">
                        <div style="font-size:24px;font-weight:bold;color:#ffc107;">${data.age_range.min}-${data.age_range.max}</div>
                        <div style="font-size:12px;color:#666;">Age Range</div>
                    </div>
                </div>
            </div>
        `;
        
        // Language Breakdown
        html += `
            <div style="background:#e7f3ff;padding:15px;border-radius:8px;margin-bottom:20px;">
                <h5 style="margin:0 0 10px 0;">🌐 Language Distribution</h5>
                <div style="display:flex;gap:15px;justify-content:space-around;">
        `;
        
        const langNames = { en: 'English', si: 'Sinhala', ta: 'Tamil' };
        const langColors = { en: '#0b3b8c', si: '#28a745', ta: '#dc3545' };
        
        for (const [lang, count] of Object.entries(data.language_breakdown)) {
            const percentage = ((count / data.total_engagements) * 100).toFixed(1);
            const color = langColors[lang] || '#666';
            html += `
                <div style="text-align:center;">
                    <div style="font-size:28px;font-weight:bold;color:${color};">${count}</div>
                    <div style="font-size:12px;color:#666;">${langNames[lang] || lang}</div>
                    <div style="font-size:11px;color:#999;">${percentage}%</div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        // Top 10 Questions
        html += `
            <h5 style="margin:20px 0 10px 0;">🔥 Top 10 Questions Asked</h5>
            <div style="background:white;border-radius:8px;overflow:hidden;border:1px solid #e5e7eb;">
        `;
        
        data.questions.forEach((q, index) => {
            const langBadges = q.languages.map(l => {
                const color = langColors[l] || '#666';
                return `<span style="background:${color};color:white;padding:2px 6px;border-radius:3px;font-size:10px;margin-left:5px;">${langNames[l] || l}</span>`;
            }).join('');
            
            const serviceBadges = q.services.slice(0, 2).map(s => 
                `<span style="background:#f3f4f6;padding:2px 6px;border-radius:3px;font-size:10px;margin-left:5px;">${s}</span>`
            ).join('');
            
            html += `
                <div style="padding:15px;border-bottom:1px solid #f3f4f6;${index === 0 ? 'background:#fffbeb;' : ''}">
                    <div style="display:flex;justify-content:space-between;align-items:start;">
                        <div style="flex:1;">
                            <div style="font-weight:${index < 3 ? 'bold' : 'normal'};margin-bottom:5px;">
                                <span style="background:#0b3b8c;color:white;padding:2px 8px;border-radius:50%;margin-right:8px;font-size:12px;">${index + 1}</span>
                                ${q.question}
                            </div>
                            <div style="font-size:12px;color:#666;margin-top:5px;">
                                ${langBadges}
                                ${serviceBadges}
                                ${q.services.length > 2 ? `<span style="color:#999;font-size:10px;margin-left:5px;">+${q.services.length - 2} more</span>` : ''}
                            </div>
                        </div>
                        <div style="text-align:right;margin-left:15px;">
                            <div style="font-size:24px;font-weight:bold;color:#0b3b8c;">${q.count}</div>
                            <div style="font-size:11px;color:#666;">times</div>
                            <div style="font-size:10px;color:#999;margin-top:2px;">Avg: ${q.avg_age}y</div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
        
        resultsDiv.innerHTML = html;
        
        // Render language chart
        renderLanguageChart(data.language_breakdown, langNames, langColors);
        
    } catch (error) {
        console.error('Error loading age group questions:', error);
        resultsDiv.innerHTML = `<div class="alert alert-danger">❌ Failed to load data: ${error.message}</div>`;
    }
}

function renderLanguageChart(langData, langNames, langColors) {
    const canvas = document.getElementById('age-lang-chart');
    if (!canvas) return;
    
    // Destroy existing chart
    if (window.ageLangChart) {
        window.ageLangChart.destroy();
    }
    
    const labels = Object.keys(langData).map(l => langNames[l] || l);
    const data = Object.values(langData);
    const colors = Object.keys(langData).map(l => langColors[l] || '#666');
    
    window.ageLangChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Language Usage by Age Group'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Default to 18-25 age group if section exists
    const ageSection = document.getElementById('age-group-section');
    if (ageSection) {
        showAgeGroupQuestions('18-25');
    }
});
// ============================================
// ML INSIGHTS MODAL (ENHANCED)
// ============================================
async function showMLInsights() {
  const modal = document.getElementById('mlInsightsModal');
  const content = document.getElementById('mlInsightsContent');
  
  modal.style.display = 'block';
  content.innerHTML = '<p style="text-align:center;padding:40px;">🧠 Loading ML insights...</p>';
  
  try {
    const res = await fetch('/api/admin/ml-insights');
    const data = await res.json();
    
    if (data.error) {
      content.innerHTML = `
        <div class="alert alert-danger">
          ⚠️ ML Engine not available
          <br><small>${data.error}</small>
          ${data.message ? `<br><small>${data.message}</small>` : ''}
        </div>
      `;
      return;
    }
    
    let html = '<div style="max-height:70vh;overflow-y:auto;">';
    
    // Analytics Overview
    html += '<h3>📊 AI Analytics Overview</h3>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:20px;">';
    
    const analytics = data.analytics || {};
    const stats = [
      { label: 'AI Chat Queries', value: analytics.ai_chat_queries || 0, icon: '🤖', color: '#667eea' },
      { label: 'Vector Searches', value: analytics.vector_searches || 0, icon: '🔍', color: '#f093fb' },
      { label: 'Success Rate', value: `${analytics.success_rate || 0}%`, icon: '✅', color: '#4facfe' },
      { label: 'Total Engagements', value: analytics.total_engagements || 0, icon: '📈', color: '#43e97b' }
    ];
    
    stats.forEach(stat => {
      html += `
        <div style="background:linear-gradient(135deg,${stat.color}20,${stat.color}10);padding:15px;border-radius:8px;text-align:center;border:1px solid ${stat.color}40;">
          <div style="font-size:32px;margin-bottom:5px;">${stat.icon}</div>
          <div style="font-size:24px;font-weight:bold;color:${stat.color};">${stat.value}</div>
          <div style="font-size:12px;color:#666;margin-top:5px;">${stat.label}</div>
        </div>
      `;
    });
    
    html += '</div>';
    
    // Language Distribution
    if (analytics.language_distribution) {
      html += '<h3>🌐 Language Distribution</h3>';
      html += '<div style="background:#f8f9fa;padding:15px;border-radius:6px;margin-bottom:20px;">';
      const langs = { en: 'English', si: 'Sinhala', ta: 'Tamil' };
      const total = Object.values(analytics.language_distribution).reduce((a, b) => a + b, 0);
      
      Object.entries(analytics.language_distribution).forEach(([lang, count]) => {
        const percent = total > 0 ? (count / total * 100).toFixed(1) : 0;
        html += `
          <div style="margin:8px 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
              <span><strong>${langs[lang] || lang}:</strong> ${count} queries</span>
              <span>${percent}%</span>
            </div>
            <div style="background:#e9ecef;height:8px;border-radius:4px;overflow:hidden;">
              <div style="background:#667eea;height:100%;width:${percent}%;transition:width 0.3s;"></div>
            </div>
          </div>
        `;
      });
      
      html += '</div>';
    }
    
    // Engagement Patterns
    if (data.patterns) {
      html += '<h3>📈 Engagement Patterns</h3>';
      html += `<div style="background:#f0f9ff;padding:15px;border-radius:6px;margin-bottom:20px;">`;
      html += `<p><strong>Total Engagements:</strong> ${data.patterns.total_engagements || 0}</p>`;
      html += `<p><strong>Unique Users:</strong> ${data.patterns.unique_users || 0}</p>`;
      html += `<p><strong>Average Age:</strong> ${data.patterns.average_age || 'N/A'}</p>`;
      html += `</div>`;
    }
    
    // User Segments
    if (data.user_segments && Object.keys(data.user_segments).length > 0) {
      html += '<h3>👥 User Segments (ML Clustering)</h3>';
      html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-bottom:20px;">';
      
      for (const [segment, info] of Object.entries(data.user_segments)) {
        const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];
        const color = colors[parseInt(segment.split('_')[1]) % colors.length];
        
        html += `
          <div style="background:${color}15;padding:12px;border-radius:6px;border-left:4px solid ${color};">
            <div style="font-weight:bold;color:${color};margin-bottom:8px;">${info.label || segment}</div>
            <div style="font-size:13px;color:#555;">
              <div>👤 ${info.size} users</div>
              <div>📊 Avg ${info.avg_engagements} engagements</div>
              <div>🎂 Avg age ${info.avg_age}</div>
            </div>
          </div>
        `;
      }
      
      html += '</div>';
    }
    
    // Premium Candidates
    html += '<h3>💎 Premium Help Candidates</h3>';
    if (data.premium_candidates && data.premium_candidates.length > 0) {
      html += '<div style="max-height:300px;overflow-y:auto;">';
      data.premium_candidates.slice(0, 10).forEach(c => {
        const priorityColor = c.priority === 'high' ? '#dc3545' : '#ffc107';
        html += `
          <div style="background:#fff3cd;padding:12px;margin:8px 0;border-left:4px solid ${priorityColor};border-radius:4px;">
            <div style="display:flex;justify-content:between;align-items:start;">
              <div style="flex:1;">
                <strong>User:</strong> ${c.user_id || 'Anonymous'}<br>
                <strong>Question:</strong> ${c.question}<br>
                <strong>Repeat Count:</strong> ${c.repeat_count} times<br>
                <strong>Action:</strong> ${c.suggested_action}
              </div>
              <span style="background:${priorityColor};color:white;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:bold;">
                ${c.priority.toUpperCase()}
              </span>
            </div>
          </div>
        `;
      });
      html += '</div>';
    } else {
      html += '<p style="color:#999;padding:20px;text-align:center;background:#f8f9fa;border-radius:6px;">No premium candidates detected yet.</p>';
    }
    
    // Recommended Services
    if (data.recommended_services && data.recommended_services.length > 0) {
      html += '<h3 style="margin-top:20px;">🎯 AI-Recommended Services</h3>';
      html += '<div style="display:flex;flex-wrap:wrap;gap:8px;">';
      data.recommended_services.forEach(svc => {
        html += `
          <div style="background:#e7f3ff;padding:8px 12px;border-radius:16px;font-size:13px;border:1px solid #3b82f6;">
            ${svc.name}
          </div>
        `;
      });
      html += '</div>';
    }
    
    // Export Button
    html += `
      <div style="margin-top:30px;padding-top:20px;border-top:2px solid #e9ecef;text-align:center;">
        <button onclick="exportMLReport()" class="btn-ml-insights" style="background:#28a745;">
          📥 Export Full ML Report (CSV)
        </button>
        <button onclick="trainRecommendations()" class="btn-ml-insights" style="background:#17a2b8;margin-left:10px;">
          🔄 Retrain ML Models
        </button>
      </div>
    `;
    
    html += '</div>';
    content.innerHTML = html;
    
  } catch (error) {
    content.innerHTML = `
      <div class="alert alert-danger">
        ❌ Failed to load ML insights: ${error.message}
        <br><small>Check that ml_recommendations.py is properly installed</small>
      </div>
    `;
    console.error('ML insights error:', error);
  }
}

async function exportMLReport() {
  try {
    window.location.href = '/api/admin/export-ml-report';
  } catch (error) {
    alert('Export failed: ' + error.message);
  }
}
// Add to admin.js:

async function loadServiceRatings() {
    const res = await fetch('/api/admin/service-ratings');
    const data = await res.json();
    
    // Create ratings chart
    new Chart(document.getElementById("ratingsChart"), {
        type: 'bar',
        data: {
            labels: data.services.map(s => s.name),
            datasets: [{
                label: 'Average Rating',
                data: data.services.map(s => s.avg_rating),
                backgroundColor: 'rgba(255, 206, 86, 0.6)'
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5
                }
            }
        }
    });
}

async function sendBulkNotification() {
    const message = prompt("Enter notification message:");
    if (!message) return;
    
    const res = await fetch('/api/admin/send-notification', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: message,
            target: 'all'  // or specific user segment
        })
    });
    
    if (res.ok) {
        alert('Notification sent successfully!');
    }
}
async function trainRecommendations() {
  if (!confirm('Retrain ML recommendation models?\n\nThis will:\n- Rebuild user clusters\n- Update recommendation engine\n- Take 10-30 seconds\n\nContinue?')) {
    return;
  }
  
  try {
    const res = await fetch('/api/admin/train-recommendations', { method: 'POST' });
    const data = await res.json();
    
    if (data.status === 'success') {
      alert('✅ ML models retrained successfully!\n\n' + JSON.stringify(data.training_data, null, 2));
      showMLInsights(); // Refresh insights
    } else {
      alert('❌ Training failed: ' + data.error);
    }
  } catch (error) {
    alert('❌ Network error: ' + error.message);
  }
}

function closeMLModal() {
  document.getElementById('mlInsightsModal').style.display = 'none';
}

window.onclick = function(event) {
  const modal = document.getElementById('mlInsightsModal');
  if (event.target === modal) {
    modal.style.display = 'none';
  }
}

// ============================================
// EXISTING FUNCTIONS
// ============================================
document.getElementById("logoutBtn")?.addEventListener('click', async () => {
  await fetch('/api/admin/logout', {method:'POST'});
  window.location = "/admin";
});

document.getElementById("exportCsv")?.addEventListener('click', () => {
  window.location = '/api/admin/export_csv';
});

window.onload = loadDashboard;

console.log('✅ Complete admin dashboard loaded');