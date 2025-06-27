// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Load initial data
    loadDashboardData();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update date/time
    updateDateTime();
    setInterval(updateDateTime, 60000); // Update every minute
});

// Initialize Dashboard
function initializeDashboard() {
    // Set active page
    const hash = window.location.hash.substring(1) || 'home';
    navigateToPage(hash);
}

// Setup Event Listeners
function setupEventListeners() {
    // Navigation clicks
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            navigateToPage(page);
        });
    });
    
    // Modal close on backdrop click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
}

// Navigation
function navigateToPage(pageName) {
    // Update URL hash
    window.location.hash = pageName;
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-page') === pageName) {
            item.classList.add('active');
        }
    });
    
    // Show corresponding page
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const pageElement = document.getElementById(pageName + 'Page');
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    // Update page title and breadcrumb
    updatePageHeader(pageName);
    
    // Load page-specific data
    loadPageData(pageName);
}

// Update Page Header
function updatePageHeader(pageName) {
    const titles = {
        'home': 'Dashboard',
        'sources': 'Sources',
        'targets': 'Targets',
        'jobs': 'Jobs',
        'settings': 'Settings'
    };
    
    document.getElementById('pageTitle').textContent = titles[pageName] || 'Dashboard';
    document.querySelector('.breadcrumb').textContent = titles[pageName] || 'Home';
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load stats
        const response = await fetch('/api/dashboard/stats');
        const stats = await response.json();
        
        // Update stats cards
        updateStatsCards(stats);
        
        // Load recent jobs
        loadRecentJobs(stats.jobs.recent);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update Stats Cards
function updateStatsCards(stats) {
    // Update conversion count
    const conversionCard = document.querySelector('.stat-card:nth-child(1) .stat-value');
    if (conversionCard) {
        conversionCard.textContent = stats.conversions.month.toLocaleString();
    }
    
    // Update active jobs
    const activeJobsCard = document.querySelector('.stat-card:nth-child(2) .stat-value');
    if (activeJobsCard) {
        activeJobsCard.textContent = stats.jobs.running;
    }
    
    // Update success rate
    const successRateCard = document.querySelector('.stat-card:nth-child(3) .stat-value');
    if (successRateCard) {
        successRateCard.textContent = stats.conversions.success_rate + '%';
    }
    
    // Update sources count
    const sourcesCard = document.querySelector('.stat-card:nth-child(4) .stat-value');
    if (sourcesCard) {
        sourcesCard.textContent = stats.sources.total;
    }
}

// Load Recent Jobs
function loadRecentJobs(jobs) {
    const container = document.getElementById('recentJobsList');
    container.innerHTML = '';
    
    jobs.forEach(job => {
        const item = document.createElement('div');
        item.className = 'activity-item';
        item.innerHTML = `
            <div class="activity-status ${job.status}"></div>
            <div class="activity-details">
                <div class="activity-name">${job.name}</div>
                <div class="activity-info">${job.status === 'running' ? 'In Progress' : job.status}</div>
            </div>
            <div class="activity-progress">${job.progress}%</div>
        `;
        container.appendChild(item);
    });
}

// Load Page Data
async function loadPageData(pageName) {
    switch(pageName) {
        case 'sources':
            await loadSources();
            break;
        case 'targets':
            await loadTargets();
            break;
        case 'jobs':
            await loadJobs();
            break;
    }
}

// Load Sources
async function loadSources() {
    try {
        const response = await fetch('/api/sources');
        const sources = await response.json();
        
        const container = document.getElementById('sourcesGrid');
        container.innerHTML = '';
        
        sources.forEach(source => {
            const card = document.createElement('div');
            card.className = 'source-card';
            card.innerHTML = `
                <div class="card-icon">${source.icon}</div>
                <h4 class="card-title">${source.name}</h4>
                <p class="card-description">${source.description}</p>
                <div class="card-tags">
                    ${source.frameworks.map(f => `<span class="tag">${f}</span>`).join('')}
                </div>
                <div class="card-status">
                    <span class="status-indicator ${source.active ? 'active' : 'inactive'}"></span>
                    <span>${source.active ? 'Active' : 'Inactive'}</span>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading sources:', error);
    }
}

// Load Targets
async function loadTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        const container = document.getElementById('targetsGrid');
        container.innerHTML = '';
        
        targets.forEach(target => {
            const card = document.createElement('div');
            card.className = 'target-card';
            card.innerHTML = `
                <div class="card-icon">${target.icon}</div>
                <h4 class="card-title">${target.name}</h4>
                <p class="card-description">${target.description}</p>
                <div class="card-tags">
                    ${target.features.map(f => `<span class="tag">${f}</span>`).join('')}
                </div>
                <div class="card-status">
                    <span class="status-indicator ${target.active ? 'active' : 'inactive'}"></span>
                    <span>${target.active ? 'Active' : 'Inactive'}</span>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading targets:', error);
    }
}

// Load Jobs
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const jobs = await response.json();
        
        const tbody = document.getElementById('jobsTableBody');
        tbody.innerHTML = '';
        
        jobs.forEach(job => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${job.name}</td>
                <td>${getSourceName(job.source)}</td>
                <td>${getTargetName(job.target)}</td>
                <td><span class="status-badge ${job.status}">${job.status}</span></td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${job.progress}%"></div>
                    </div>
                </td>
                <td>${formatDate(job.created)}</td>
                <td>
                    <button class="btn btn-sm btn-icon" onclick="viewJob(${job.id})">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                        </svg>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

// Helper Functions
function getSourceName(sourceId) {
    const sources = {
        'java-spring': 'Java Spring Boot',
        'python-django': 'Python Django',
        'nodejs-express': 'Node.js Express'
    };
    return sources[sourceId] || sourceId;
}

function getTargetName(targetId) {
    const targets = {
        'sage-it': 'Sage IT',
        'aws-lambda': 'AWS Lambda',
        'kubernetes': 'Kubernetes'
    };
    return targets[targetId] || targetId;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Modal Functions
function showNewJobModal() {
    document.getElementById('newJobModal').classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// Update Date/Time
function updateDateTime() {
    const now = new Date();
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    document.getElementById('currentDateTime').textContent = now.toLocaleDateString('en-US', options);
}

// View Job Details
function viewJob(jobId) {
    console.log('View job:', jobId);
    // TODO: Implement job details view
}

// Export functions for global use
window.navigateToPage = navigateToPage;
window.showNewJobModal = showNewJobModal;
window.closeModal = closeModal;
window.viewJob = viewJob;