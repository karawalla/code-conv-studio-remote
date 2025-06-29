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
        'createJob': 'Create Job',
        'settings': 'Settings',
        'agents': 'Agents'
    };
    
    // Commented out - redundant page titles removed
    // document.getElementById('pageTitle').textContent = titles[pageName] || 'Dashboard';
    // document.querySelector('.breadcrumb').textContent = titles[pageName] || 'Home';
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
        case 'agents':
            await loadAgents();
            break;
        case 'jobs':
            await loadJobs();
            break;
        case 'createJob':
            await loadCreateJobPage();
            break;
        case 'settings':
            // Load credentials by default when opening settings
            await loadCredentials();
            break;
    }
}

// Load Sources
async function loadSources() {
    try {
        const response = await fetch('/api/sources');
        const sources = await response.json();
        
        const tbody = document.getElementById('sourcesTableBody');
        const emptyState = document.getElementById('noSourcesMessage');
        const table = document.querySelector('.sources-table');
        
        tbody.innerHTML = '';
        
        if (sources.length === 0) {
            table.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            table.style.display = 'table';
            emptyState.style.display = 'none';
            
            sources.forEach(source => {
                const row = document.createElement('tr');
                const createdDate = new Date(source.created_at).toLocaleDateString();
                const fileCount = source.info?.total_files || 0;
                
                row.innerHTML = `
                    <td>
                        <div class="source-name">
                            ${source.icon} ${source.name}
                        </div>
                    </td>
                    <td>
                        <span class="source-type-badge ${source.type} liquid-glass">
                            ${source.type === 'github' ? '🐙' : '📁'} ${source.type}
                        </span>
                    </td>
                    <td>
                        ${source.type === 'github' ? 
                            `<a href="${source.url}" target="_blank" class="text-link">${source.url}</a>` : 
                            'Local Folder'}
                    </td>
                    <td>${fileCount} files</td>
                    <td>${createdDate}</td>
                    <td>
                        <div class="source-actions">
                            <button class="btn btn-sm btn-secondary liquid-glass" onclick="viewSourceTree('${source.id}', '${source.name}')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                                </svg>
                                View Tree
                            </button>
                            ${source.type === 'github' ? `
                                <button class="btn btn-sm btn-secondary liquid-glass" onclick="updateSource('${source.id}')">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                                    </svg>
                                    Update
                                </button>
                            ` : ''}
                            <button class="btn btn-sm btn-danger" onclick="deleteSource('${source.id}', '${source.name}')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                </svg>
                                Delete
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading sources:', error);
        showNotification('Error loading sources', 'error');
    }
}

// Load Targets
async function loadTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        const container = document.getElementById('targetsGrid');
        const emptyState = document.getElementById('noTargetsMessage');
        
        container.innerHTML = '';
        
        if (targets.length === 0) {
            container.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            container.style.display = 'grid';
            emptyState.style.display = 'none';
            
            targets.forEach(target => {
                const card = document.createElement('div');
                card.className = 'target-card liquid-glass';
                card.innerHTML = `
                    <div class="target-header">
                        <div class="target-info">
                            <div class="target-icon">${getTargetIcon(target.name)}</div>
                            <h4 class="target-name">${target.name}</h4>
                            <p class="target-description">${target.description}</p>
                        </div>
                        <div class="target-actions">
                            <button class="btn btn-sm btn-secondary liquid-glass" onclick="editTarget('${target.id}')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                                </svg>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteTarget('${target.id}', '${target.name}')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="target-prompts-info">
                        <div class="prompts-count">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            6 conversion prompts configured
                        </div>
                    </div>
                `;
                card.onclick = (e) => {
                    if (!e.target.closest('button')) {
                        editTarget(target.id);
                    }
                };
                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading targets:', error);
        showNotification('Error loading targets', 'error');
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
function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
    document.body.classList.add('modal-open');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
    document.body.classList.remove('modal-open');
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

// Add Source Functions
function showAddSourceModal() {
    document.getElementById('addSourceModal').classList.add('show');
}

function toggleSourceTypeFields() {
    const sourceType = document.querySelector('input[name="sourceType"]:checked').value;
    const githubFields = document.getElementById('githubFields');
    const localFields = document.getElementById('localFields');
    
    if (sourceType === 'github') {
        githubFields.style.display = 'block';
        localFields.style.display = 'none';
    } else {
        githubFields.style.display = 'none';
        localFields.style.display = 'block';
    }
}

async function addSource() {
    const sourceType = document.querySelector('input[name="sourceType"]:checked').value;
    const sourceName = document.getElementById('sourceName').value.trim();
    const btnText = document.getElementById('addSourceBtnText');
    const spinner = document.getElementById('addSourceSpinner');
    
    let data = {
        type: sourceType,
        name: sourceName
    };
    
    if (sourceType === 'github') {
        const repoUrl = document.getElementById('repoUrl').value.trim();
        if (!repoUrl) {
            showNotification('Please enter a repository URL', 'error');
            return;
        }
        data.url = repoUrl;
    } else {
        const folderPath = document.getElementById('folderPath').value.trim();
        if (!folderPath) {
            showNotification('Please enter a folder path', 'error');
            return;
        }
        data.path = folderPath;
    }
    
    // Show loading state
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch('/api/sources', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Source added successfully', 'success');
            closeModal('addSourceModal');
            loadSources(); // Reload the sources list
            
            // Clear form
            document.getElementById('sourceName').value = '';
            document.getElementById('repoUrl').value = '';
            document.getElementById('folderPath').value = '';
        } else {
            showNotification(result.error || 'Failed to add source', 'error');
        }
    } catch (error) {
        console.error('Error adding source:', error);
        showNotification('Failed to add source', 'error');
    } finally {
        // Hide loading state
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

async function deleteSource(sourceId, sourceName) {
    if (!confirm(`Are you sure you want to delete "${sourceName}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sources/${sourceId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Source deleted successfully', 'success');
            loadSources(); // Reload the sources list
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to delete source', 'error');
        }
    } catch (error) {
        console.error('Error deleting source:', error);
        showNotification('Failed to delete source', 'error');
    }
}

async function updateSource(sourceId) {
    try {
        const response = await fetch(`/api/sources/${sourceId}/update`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Source updated successfully', 'success');
            loadSources(); // Reload the sources list
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to update source', 'error');
        }
    } catch (error) {
        console.error('Error updating source:', error);
        showNotification('Failed to update source', 'error');
    }
}

// Tree view state
let treeState = {
    sourceId: null,
    sourceName: null,
    currentPath: [],
    fullTree: null
};

async function viewSourceTree(sourceId, sourceName) {
    const modal = document.getElementById('sourceTreeModal');
    const title = document.getElementById('sourceTreeTitle');
    const content = document.getElementById('sourceTreeContent');
    
    // Reset state
    treeState = {
        sourceId: sourceId,
        sourceName: sourceName,
        currentPath: [],
        fullTree: null
    };
    
    title.textContent = `Source Tree - ${sourceName}`;
    content.innerHTML = '<div class="spinner"></div> Loading...';
    
    modal.classList.add('show');
    
    try {
        const response = await fetch(`/api/sources/${sourceId}/tree`);
        const tree = await response.json();
        
        treeState.fullTree = tree;
        navigateToPath([]);
    } catch (error) {
        console.error('Error loading source tree:', error);
        content.innerHTML = '<p>Failed to load source tree</p>';
    }
}

function navigateToPath(path) {
    treeState.currentPath = path;
    
    // Update navigation breadcrumb
    updateTreeNavigation();
    
    // Get items at current path
    let currentItems = treeState.fullTree;
    for (const segment of path) {
        const folder = currentItems.find(item => item.name === segment && item.type === 'folder');
        if (folder && folder.children) {
            currentItems = folder.children;
        }
    }
    
    // Render current level
    renderTreeLevel(currentItems);
}

function updateTreeNavigation() {
    const nav = document.getElementById('treeNavigation');
    nav.innerHTML = '';
    
    // Root item
    const rootItem = document.createElement('div');
    rootItem.className = 'tree-nav-item liquid-glass';
    rootItem.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        ${treeState.sourceName}
    `;
    rootItem.onclick = () => navigateToPath([]);
    nav.appendChild(rootItem);
    
    // Path segments
    treeState.currentPath.forEach((segment, index) => {
        // Separator
        const separator = document.createElement('span');
        separator.className = 'tree-nav-separator';
        separator.textContent = '›';
        nav.appendChild(separator);
        
        // Path item
        const pathItem = document.createElement('div');
        pathItem.className = 'tree-nav-item liquid-glass';
        pathItem.textContent = segment;
        pathItem.onclick = () => navigateToPath(treeState.currentPath.slice(0, index + 1));
        nav.appendChild(pathItem);
    });
}

function renderTreeLevel(items) {
    const content = document.getElementById('sourceTreeContent');
    content.innerHTML = '';
    
    // Sort items: folders first, then files
    const sortedItems = [...items].sort((a, b) => {
        if (a.type === b.type) return a.name.localeCompare(b.name);
        return a.type === 'folder' ? -1 : 1;
    });
    
    sortedItems.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = `tree-item tree-${item.type}`;
        
        if (item.type === 'file') {
            const ext = item.name.split('.').pop().toLowerCase();
            itemElement.classList.add(`file-${ext}`);
        }
        
        const icon = document.createElement('span');
        icon.className = 'tree-icon';
        icon.innerHTML = item.type === 'folder' ? 
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>' :
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>';
        
        const label = document.createElement('span');
        label.className = 'tree-label';
        label.textContent = item.name;
        
        if (item.type === 'file' && item.size) {
            const info = document.createElement('span');
            info.className = 'tree-info';
            info.textContent = formatFileSize(item.size);
            label.appendChild(info);
        }
        
        itemElement.appendChild(icon);
        itemElement.appendChild(label);
        
        if (item.type === 'folder') {
            itemElement.onclick = () => {
                const newPath = [...treeState.currentPath, item.name];
                navigateToPath(newPath);
            };
        } else {
            // File click handler
            itemElement.onclick = () => {
                selectFile(item.name);
            };
        }
        
        content.appendChild(itemElement);
    });
    
    // If empty folder
    if (items.length === 0) {
        content.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--gray-500);">Empty folder</div>';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Simple notification (you can enhance this with a proper notification system)
    console.log(`${type}: ${message}`);
    // TODO: Implement visual notification
}

// Add CSS classes
const style = document.createElement('style');
style.textContent = `
    .text-link {
        color: var(--primary);
        text-decoration: none;
    }
    .text-link:hover {
        text-decoration: underline;
    }
    .btn-danger {
        background: var(--danger);
        color: var(--white);
    }
    .btn-danger:hover {
        background: #dc2626;
    }
`;
document.head.appendChild(style);

// Export functions for global use
window.navigateToPage = navigateToPage;
window.closeModal = closeModal;
window.viewJob = viewJob;
window.showAddSourceModal = showAddSourceModal;
window.toggleSourceTypeFields = toggleSourceTypeFields;
window.addSource = addSource;
window.deleteSource = deleteSource;
window.updateSource = updateSource;
window.viewSourceTree = viewSourceTree;
window.showAddTargetModal = showAddTargetModal;
window.addTarget = addTarget;
window.editTarget = editTarget;
window.deleteTarget = deleteTarget;
window.switchTab = switchTab;
window.switchAddTargetTab = switchAddTargetTab;
window.switchMainTab = switchMainTab;
window.switchKnowledgeTab = switchKnowledgeTab;
window.saveTarget = saveTarget;
window.triggerFileUpload = triggerFileUpload;
window.handleFileUpload = handleFileUpload;
window.addSearchTopic = addSearchTopic;
window.addGithubSample = addGithubSample;
window.addDocumentationUrl = addDocumentationUrl;
window.removeKnowledgeItem = removeKnowledgeItem;
window.removeTopicTag = removeTopicTag;

// File selection and content display
let selectedFile = null;

async function selectFile(filename) {
    // Update selected state
    document.querySelectorAll('.tree-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Find and select the clicked item
    const items = document.querySelectorAll('.tree-item');
    items.forEach(item => {
        if (item.querySelector('.tree-label').textContent.includes(filename)) {
            item.classList.add('selected');
        }
    });
    
    // Build full path
    const fullPath = [...treeState.currentPath, filename].join('/');
    selectedFile = fullPath;
    
    // Update content header
    document.getElementById('contentHeader').querySelector('.content-filename').textContent = fullPath || filename;
    
    // Show loading state
    const contentBody = document.getElementById('contentBody');
    contentBody.innerHTML = '<div class="spinner" style="margin: 2rem auto; display: block;"></div> Loading file content...';
    
    try {
        // Fetch file content
        const response = await fetch(`/api/sources/${treeState.sourceId}/file?path=${encodeURIComponent(fullPath)}`);
        
        if (response.ok) {
            const data = await response.json();
            displayFileContent(data.content, filename);
        } else {
            contentBody.innerHTML = `
                <div class="content-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p>Unable to load file content</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading file:', error);
        contentBody.innerHTML = `
            <div class="content-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p>Error loading file content</p>
            </div>
        `;
    }
}

function displayFileContent(content, filename) {
    const contentBody = document.getElementById('contentBody');
    const fileContent = document.getElementById('fileContent');
    
    // Hide placeholder, show content
    contentBody.innerHTML = '';
    const pre = document.createElement('pre');
    pre.id = 'fileContent';
    pre.className = 'file-content';
    
    // Check if it's a binary file or image
    const imageExtensions = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'bmp', 'webp'];
    const ext = filename.split('.').pop().toLowerCase();
    
    if (imageExtensions.includes(ext)) {
        // Display image
        pre.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <img src="data:image/${ext};base64,${content}" style="max-width: 100%; max-height: 600px; border: 1px solid var(--gray-200); border-radius: var(--radius);" />
            </div>
        `;
    } else if (content === null || content === undefined) {
        pre.textContent = '// Binary file - content preview not available';
    } else {
        // Display text content with syntax highlighting (basic)
        pre.textContent = content || '// Empty file';
    }
    
    contentBody.appendChild(pre);
}

// Selected styles are now handled in dashboard.css

// Target Functions
function getTargetIcon(targetName) {
    const icons = {
        'Python': '🐍',
        'Java': '☕',
        'JavaScript': '🟨',
        'C#/.NET': '🔷',
        'Ruby': '💎',
        'PHP': '🐘',
        'Go': '🐹',
        'Rust': '🦀'
    };
    
    // Check if the target name contains any of the keys
    for (const [key, icon] of Object.entries(icons)) {
        if (targetName.toLowerCase().includes(key.toLowerCase())) {
            return icon;
        }
    }
    
    return '🎯'; // Default icon
}

async function showAddTargetModal() {
    document.getElementById('addTargetModal').classList.add('show');
    
    // Load default targets
    try {
        const response = await fetch('/api/targets/defaults');
        const defaults = await response.json();
        
        const container = document.getElementById('defaultTargetsList');
        container.innerHTML = '';
        
        defaults.forEach(target => {
            const item = document.createElement('div');
            item.className = 'default-target-item';
            item.innerHTML = `
                <div class="default-target-icon">${target.icon}</div>
                <div class="default-target-name">${target.name}</div>
            `;
            item.onclick = () => {
                document.getElementById('targetName').value = target.name;
                document.getElementById('targetDescription').value = target.description;
            };
            container.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading default targets:', error);
    }
}

function switchAddTargetTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('#addTargetModal .tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab panels
    document.querySelectorAll('#addTargetModal .tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(tabName + '-panel').classList.add('active');
}

async function addTarget() {
    const name = document.getElementById('targetName').value.trim();
    const description = document.getElementById('targetDescription').value.trim();
    const btnText = document.getElementById('addTargetBtnText');
    const spinner = document.getElementById('addTargetSpinner');
    
    if (!name) {
        showNotification('Please enter a target name', 'error');
        return;
    }
    
    // Collect prompts
    const prompts = {
        analyze: document.getElementById('addPromptAnalyze').value.trim(),
        plan: document.getElementById('addPromptPlan').value.trim(),
        migrate: document.getElementById('addPromptMigrate').value.trim(),
        validate: document.getElementById('addPromptValidate').value.trim(),
        fix: document.getElementById('addPromptFix').value.trim(),
        discuss: document.getElementById('addPromptDiscuss').value.trim()
    };
    
    // Show loading state
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch('/api/targets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description,
                prompts: prompts
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Target created successfully', 'success');
            closeModal('addTargetModal');
            loadTargets(); // Reload the targets list
            
            // Clear form
            document.getElementById('targetName').value = '';
            document.getElementById('targetDescription').value = '';
            document.getElementById('addPromptAnalyze').value = '';
            document.getElementById('addPromptPlan').value = '';
            document.getElementById('addPromptMigrate').value = '';
            document.getElementById('addPromptValidate').value = '';
            document.getElementById('addPromptFix').value = '';
            document.getElementById('addPromptDiscuss').value = '';
            
            // Reset to first tab
            switchAddTargetTab('add-analyze');
        } else {
            showNotification(result.error || 'Failed to create target', 'error');
        }
    } catch (error) {
        console.error('Error creating target:', error);
        showNotification('Failed to create target', 'error');
    } finally {
        // Hide loading state
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

let currentEditingTarget = null;

async function editTarget(targetId) {
    try {
        const response = await fetch(`/api/targets/${targetId}`);
        const target = await response.json();
        
        if (response.ok) {
            currentEditingTarget = target;
            
            // Update modal title
            document.getElementById('editTargetTitle').textContent = `Edit Target - ${target.name}`;
            
            // Fill in target info
            document.getElementById('editTargetName').value = target.name;
            document.getElementById('editTargetDescription').value = target.description;
            
            // Fill in prompts
            document.getElementById('promptAnalyze').value = target.prompts.analyze || '';
            document.getElementById('promptPlan').value = target.prompts.plan || '';
            document.getElementById('promptMigrate').value = target.prompts.migrate || '';
            document.getElementById('promptValidate').value = target.prompts.validate || '';
            document.getElementById('promptFix').value = target.prompts.fix || '';
            document.getElementById('promptDiscuss').value = target.prompts.discuss || '';
            
            // TODO: Load knowledge store items
            
            // Show modal
            document.getElementById('editTargetModal').classList.add('show');
            
            // Reset to first tab
            switchTab('analyze');
        } else {
            showNotification('Target not found', 'error');
        }
    } catch (error) {
        console.error('Error loading target:', error);
        showNotification('Failed to load target', 'error');
    }
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        if (panel.getAttribute('data-panel') === tabName) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });
}

function switchMainTab(tabName) {
    // Update main tab buttons
    document.querySelectorAll('.main-tab-button').forEach(btn => {
        if (btn.getAttribute('data-main-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update main tab panels
    document.querySelectorAll('.main-tab-panel').forEach(panel => {
        if (panel.id === tabName + '-panel') {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });
}

function switchKnowledgeTab(tabName) {
    // Update knowledge tab buttons
    document.querySelectorAll('.knowledge-tab-button').forEach(btn => {
        if (btn.getAttribute('data-knowledge-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update knowledge tab panels
    document.querySelectorAll('.knowledge-tab-panel').forEach(panel => {
        if (panel.getAttribute('data-knowledge-panel') === tabName) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });
}

async function saveTarget() {
    if (!currentEditingTarget) return;
    
    const btnText = document.getElementById('saveTargetBtnText');
    const spinner = document.getElementById('saveTargetSpinner');
    
    // Collect data
    const updates = {
        name: document.getElementById('editTargetName').value.trim(),
        description: document.getElementById('editTargetDescription').value.trim(),
        prompts: {
            analyze: document.getElementById('promptAnalyze').value.trim(),
            plan: document.getElementById('promptPlan').value.trim(),
            migrate: document.getElementById('promptMigrate').value.trim(),
            validate: document.getElementById('promptValidate').value.trim(),
            fix: document.getElementById('promptFix').value.trim(),
            discuss: document.getElementById('promptDiscuss').value.trim()
        }
    };
    
    // Show loading state
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch(`/api/targets/${currentEditingTarget.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });
        
        if (response.ok) {
            showNotification('Target updated successfully', 'success');
            closeModal('editTargetModal');
            loadTargets(); // Reload the targets list
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to update target', 'error');
        }
    } catch (error) {
        console.error('Error updating target:', error);
        showNotification('Failed to update target', 'error');
    } finally {
        // Hide loading state
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

async function deleteTarget(targetId, targetName) {
    if (!confirm(`Are you sure you want to delete "${targetName}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/targets/${targetId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Target deleted successfully', 'success');
            loadTargets(); // Reload the targets list
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to delete target', 'error');
        }
    } catch (error) {
        console.error('Error deleting target:', error);
        showNotification('Failed to delete target', 'error');
    }
}

// Knowledge Store Functions
function triggerFileUpload() {
    document.getElementById('knowledgeFileInput').click();
}

function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length === 0) return;
    
    // For now, just show the files in the list
    // In a real implementation, you would upload these to the server
    const knowledgeList = document.getElementById('knowledgeStoreList');
    
    for (let file of files) {
        const item = createKnowledgeItem({
            type: 'file',
            name: file.name,
            size: formatFileSize(file.size),
            id: Date.now() + Math.random() // Temporary ID
        });
        knowledgeList.appendChild(item);
    }
    
    // Show the knowledge list if it was hidden
    knowledgeList.style.display = 'flex';
    
    showNotification(`Added ${files.length} file(s) to knowledge store`, 'success');
    event.target.value = ''; // Reset input
}

function addSearchTopic() {
    const topicInput = document.getElementById('searchTopicInput');
    const topic = topicInput.value.trim();
    
    if (!topic) {
        showNotification('Please enter a search topic', 'error');
        return;
    }
    
    // Get or create the topics container
    let topicsContainer = document.getElementById('searchTopicsContainer');
    if (!topicsContainer) {
        topicsContainer = document.createElement('div');
        topicsContainer.id = 'searchTopicsContainer';
        topicsContainer.className = 'topics-container';
        const panel = document.querySelector('[data-knowledge-panel="search"]');
        if (panel) {
            panel.appendChild(topicsContainer);
        }
    }
    
    // Create a tag instead of a full item
    const tag = createTopicTag({
        name: topic,
        id: Date.now() + Math.random()
    });
    
    topicsContainer.appendChild(tag);
    topicInput.value = '';
    showNotification('Search topic added', 'success');
}

function addGithubSample() {
    const githubInput = document.getElementById('githubUrlInput');
    const url = githubInput.value.trim();
    
    if (!url) {
        showNotification('Please enter a GitHub URL', 'error');
        return;
    }
    
    // Validate GitHub URL
    try {
        const urlObj = new URL(url);
        if (!urlObj.hostname.includes('github.com')) {
            showNotification('Please enter a valid GitHub URL', 'error');
            return;
        }
    } catch (e) {
        showNotification('Please enter a valid URL', 'error');
        return;
    }
    
    const knowledgeList = document.getElementById('knowledgeStoreList');
    const item = createKnowledgeItem({
        type: 'github',
        name: getGithubRepoName(url),
        url: url,
        id: Date.now() + Math.random()
    });
    
    knowledgeList.appendChild(item);
    knowledgeList.style.display = 'flex';
    githubInput.value = '';
    showNotification('GitHub sample added', 'success');
}

function addDocumentationUrl() {
    const docInput = document.getElementById('docUrlInput');
    const url = docInput.value.trim();
    
    if (!url) {
        showNotification('Please enter a documentation URL', 'error');
        return;
    }
    
    // Basic URL validation
    try {
        new URL(url);
    } catch (e) {
        showNotification('Please enter a valid URL', 'error');
        return;
    }
    
    const knowledgeList = document.getElementById('knowledgeStoreList');
    const item = createKnowledgeItem({
        type: 'doc',
        name: getDomainFromUrl(url),
        url: url,
        id: Date.now() + Math.random()
    });
    
    knowledgeList.appendChild(item);
    knowledgeList.style.display = 'flex';
    docInput.value = '';
    showNotification('Documentation link added', 'success');
}

function createKnowledgeItem(data) {
    const item = document.createElement('div');
    item.className = 'knowledge-item';
    item.dataset.id = data.id;
    
    const icons = {
        search: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>',
        github: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>',
        doc: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>',
        file: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>'
    };
    
    const tagLabels = {
        search: 'Search',
        github: 'GitHub',
        doc: 'Doc',
        file: 'File'
    };
    
    const icon = icons[data.type] || icons.file;
    const tagLabel = tagLabels[data.type] || 'File';
    
    item.innerHTML = `
        <div class="knowledge-item-info">
            <div class="knowledge-item-icon">
                ${icon}
            </div>
            <div>
                <div>
                    <span class="knowledge-item-name">${data.name}</span>
                    <span class="knowledge-item-tag ${data.type}">${tagLabel}</span>
                </div>
                ${data.size ? `<div class="knowledge-item-size">${data.size}</div>` : ''}
                ${data.url ? `<div class="knowledge-item-size">${data.url}</div>` : ''}
            </div>
        </div>
        <div class="knowledge-item-actions">
            <button class="btn btn-sm btn-danger" onclick="removeKnowledgeItem('${data.id}')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
            </button>
        </div>
    `;
    
    return item;
}

function removeKnowledgeItem(id) {
    const item = document.querySelector(`.knowledge-item[data-id="${id}"]`);
    if (item) {
        item.remove();
        showNotification('Item removed from knowledge store', 'info');
        
        // Hide the list if it's now empty
        const knowledgeList = document.getElementById('knowledgeStoreList');
        if (knowledgeList && knowledgeList.children.length === 0) {
            knowledgeList.style.display = 'none';
        }
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getDomainFromUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.replace('www.', '');
    } catch (e) {
        return url;
    }
}

function getGithubRepoName(url) {
    try {
        const urlObj = new URL(url);
        const parts = urlObj.pathname.split('/').filter(p => p);
        if (parts.length >= 2) {
            return `${parts[0]}/${parts[1]}`;
        }
        return urlObj.pathname;
    } catch (e) {
        return url;
    }
}

function createTopicTag(data) {
    const tag = document.createElement('div');
    tag.className = 'topic-tag';
    tag.dataset.id = data.id;
    
    // Generate random color for border
    const colors = [
        '#ef4444', // red
        '#f59e0b', // amber
        '#10b981', // emerald
        '#3b82f6', // blue
        '#8b5cf6', // violet
        '#ec4899', // pink
        '#14b8a6', // teal
        '#6366f1', // indigo
        '#f97316', // orange
        '#06b6d4'  // cyan
    ];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    tag.style.borderColor = randomColor;
    tag.style.color = randomColor;
    
    tag.innerHTML = `
        <span class="topic-text">${data.name}</span>
        <button class="topic-delete" onclick="removeTopicTag('${data.id}')" style="color: ${randomColor}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    `;
    
    return tag;
}

function removeTopicTag(id) {
    const tag = document.querySelector(`.topic-tag[data-id="${id}"]`);
    if (tag) {
        tag.remove();
        showNotification('Topic removed', 'info');
        
        // Check if container is empty and hide if needed
        const container = document.getElementById('searchTopicsContainer');
        if (container && container.children.length === 0) {
            container.remove();
        }
    }
}

// ============= Agents Management =============
let currentAgents = [];
let capabilitiesCatalog = {};
let currentEditingAgent = null;

// Load agents when switching to agents page
function loadAgents() {
    fetch('/api/agents')
        .then(response => response.json())
        .then(agents => {
            currentAgents = agents;
            renderAgents(agents);
        })
        .catch(error => {
            console.error('Error loading agents:', error);
            showNotification('Failed to load agents', 'error');
        });
}

// Render agents in the container
function renderAgents(agents) {
    const container = document.getElementById('agentsContainer');
    
    if (!agents || agents.length === 0) {
        container.innerHTML = `
            <div class="agents-empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
                <h4>No agents configured</h4>
                <p>AI agents will help automate your conversion workflows</p>
                <button class="btn btn-primary" onclick="showAddAgentModal()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 20px; height: 20px;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                    </svg>
                    Add Your First Agent
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = agents.map(agent => `
        <div class="agent-card ${agent.status === 'inactive' ? 'inactive' : ''}" onclick="showEditAgentModal('${agent.id}')">
            <div class="agent-status ${agent.status === 'inactive' ? 'inactive' : ''}"></div>
            <div class="agent-header">
                <div class="agent-avatar">${agent.avatar || '🤖'}</div>
                <div class="agent-info">
                    <h4 class="agent-name">${agent.name}</h4>
                    <div class="agent-role">${agent.role.replace('_', ' ')}</div>
                </div>
            </div>
            <p class="agent-description">${agent.description || 'No description provided'}</p>
            <div class="agent-capabilities">
                <div class="capabilities-label">Capabilities</div>
                <div class="capabilities-list">
                    ${agent.capabilities.slice(0, 3).map(cap => `
                        <div class="capability-badge">
                            <span class="capability-icon">${cap.icon}</span>
                            <span>${cap.name}</span>
                        </div>
                    `).join('')}
                    ${agent.capabilities.length > 3 ? `
                        <div class="capability-badge">+${agent.capabilities.length - 3} more</div>
                    ` : ''}
                </div>
            </div>
            <div class="agent-actions">
                <button class="btn btn-primary" onclick="event.stopPropagation(); showEditAgentModal('${agent.id}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Configure
                </button>
            </div>
        </div>
    `).join('');
}

// Show add agent modal
function showAddAgentModal() {
    // Load capabilities catalog first
    fetch('/api/agents/capabilities/catalog')
        .then(response => response.json())
        .then(catalog => {
            capabilitiesCatalog = catalog;
            updateCapabilitiesSuggestions();
            showModal('addAgentModal');
        });
}

// Show edit agent modal
function showEditAgentModal(agentId) {
    const agent = currentAgents.find(a => a.id === agentId);
    if (!agent) return;
    
    currentEditingAgent = agent;
    
    // Populate form fields
    document.getElementById('editAgentId').value = agent.id;
    document.getElementById('editAgentName').value = agent.name;
    document.getElementById('editAgentDescription').value = agent.description || '';
    document.getElementById('editAgentAvatar').value = agent.avatar || '🤖';
    document.getElementById('editAgentStatus').value = agent.status || 'active';
    
    // Load capabilities catalog and render
    fetch('/api/agents/capabilities/catalog')
        .then(response => response.json())
        .then(catalog => {
            capabilitiesCatalog = catalog;
            renderEditCapabilities(agent);
            showModal('editAgentModal');
        });
}

// Update capabilities suggestions based on role
function updateCapabilitiesSuggestions() {
    const role = document.getElementById('newAgentRole').value;
    const container = document.getElementById('capabilitiesSection');
    
    // Always show common capabilities
    let html = `
        <div class="capability-group">
            <div class="capability-group-title">Common Capabilities</div>
            ${renderCapabilityGroup(capabilitiesCatalog.common || [])}
        </div>
    `;
    
    // Show role-specific capabilities if not custom
    if (role !== 'custom' && capabilitiesCatalog[role]) {
        html += `
            <div class="capability-group">
                <div class="capability-group-title">${role.replace('_', ' ')} Capabilities</div>
                ${renderCapabilityGroup(capabilitiesCatalog[role])}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Render capability group
function renderCapabilityGroup(capabilities) {
    return capabilities.map(cap => `
        <div class="capability-checkbox">
            <input type="checkbox" id="cap_${cap.id}" value="${cap.id}" ${cap.id === 'file_read' || cap.id === 'search' ? 'checked' : ''}>
            <label for="cap_${cap.id}">
                <span class="capability-icon">${cap.icon}</span>
                <span class="capability-name">${cap.name}</span>
                <span class="capability-desc">${cap.description}</span>
            </label>
        </div>
    `).join('');
}

// Render capabilities for editing
function renderEditCapabilities(agent) {
    const container = document.getElementById('editCapabilitiesSection');
    const agentCapIds = agent.capabilities.map(c => c.id);
    
    let html = '<div class="capability-group"><div class="capability-group-title">Common Capabilities</div>';
    
    (capabilitiesCatalog.common || []).forEach(cap => {
        const isChecked = agentCapIds.includes(cap.id);
        html += `
            <div class="capability-checkbox">
                <input type="checkbox" id="edit_cap_${cap.id}" value="${cap.id}" ${isChecked ? 'checked' : ''}>
                <label for="edit_cap_${cap.id}">
                    <span class="capability-icon">${cap.icon}</span>
                    <span class="capability-name">${cap.name}</span>
                    <span class="capability-desc">${cap.description}</span>
                </label>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Add role-specific capabilities
    if (agent.role !== 'custom' && capabilitiesCatalog[agent.role]) {
        html += `<div class="capability-group"><div class="capability-group-title">${agent.role.replace('_', ' ')} Capabilities</div>`;
        
        capabilitiesCatalog[agent.role].forEach(cap => {
            const isChecked = agentCapIds.includes(cap.id);
            html += `
                <div class="capability-checkbox">
                    <input type="checkbox" id="edit_cap_${cap.id}" value="${cap.id}" ${isChecked ? 'checked' : ''}>
                    <label for="edit_cap_${cap.id}">
                        <span class="capability-icon">${cap.icon}</span>
                        <span class="capability-name">${cap.name}</span>
                        <span class="capability-desc">${cap.description}</span>
                    </label>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    container.innerHTML = html;
}

// Create new agent
function createAgent() {
    const name = document.getElementById('newAgentName').value.trim();
    const role = document.getElementById('newAgentRole').value;
    const description = document.getElementById('newAgentDescription').value.trim();
    const avatar = document.getElementById('newAgentAvatar').value.trim() || '🤖';
    
    if (!name) {
        showNotification('Please enter an agent name', 'error');
        return;
    }
    
    // Get selected capabilities
    const selectedCaps = [];
    const checkboxes = document.querySelectorAll('#capabilitiesSection input[type="checkbox"]:checked');
    
    checkboxes.forEach(cb => {
        const capId = cb.value;
        // Find capability in catalog
        let capability = null;
        
        Object.values(capabilitiesCatalog).forEach(group => {
            const found = group.find(c => c.id === capId);
            if (found) capability = found;
        });
        
        if (capability) {
            selectedCaps.push(capability);
        }
    });
    
    const agentData = {
        name,
        role,
        description,
        avatar,
        capabilities: selectedCaps
    };
    
    fetch('/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showNotification(result.error, 'error');
        } else {
            showNotification('Agent created successfully', 'success');
            closeModal('addAgentModal');
            loadAgents();
            
            // Clear form
            document.getElementById('newAgentName').value = '';
            document.getElementById('newAgentRole').value = 'custom';
            document.getElementById('newAgentDescription').value = '';
            document.getElementById('newAgentAvatar').value = '';
        }
    })
    .catch(error => {
        console.error('Error creating agent:', error);
        showNotification('Failed to create agent', 'error');
    });
}

// Update existing agent
function updateAgent() {
    const agentId = document.getElementById('editAgentId').value;
    const name = document.getElementById('editAgentName').value.trim();
    const description = document.getElementById('editAgentDescription').value.trim();
    const avatar = document.getElementById('editAgentAvatar').value.trim() || '🤖';
    const status = document.getElementById('editAgentStatus').value;
    
    if (!name) {
        showNotification('Please enter an agent name', 'error');
        return;
    }
    
    // Get selected capabilities
    const selectedCaps = [];
    const checkboxes = document.querySelectorAll('#editCapabilitiesSection input[type="checkbox"]:checked');
    
    checkboxes.forEach(cb => {
        const capId = cb.value;
        // Find capability in catalog
        let capability = null;
        
        Object.values(capabilitiesCatalog).forEach(group => {
            const found = group.find(c => c.id === capId);
            if (found) capability = found;
        });
        
        if (capability) {
            selectedCaps.push(capability);
        }
    });
    
    const updates = {
        name,
        description,
        avatar,
        status,
        capabilities: selectedCaps
    };
    
    fetch(`/api/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            showNotification(result.error, 'error');
        } else {
            showNotification('Agent updated successfully', 'success');
            closeModal('editAgentModal');
            loadAgents();
        }
    })
    .catch(error => {
        console.error('Error updating agent:', error);
        showNotification('Failed to update agent', 'error');
    });
}

// Delete agent
function deleteAgent() {
    const agentId = document.getElementById('editAgentId').value;
    const agentName = document.getElementById('editAgentName').value;
    
    if (confirm(`Are you sure you want to delete the agent "${agentName}"? This action cannot be undone.`)) {
        fetch(`/api/agents/${agentId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                showNotification(result.error, 'error');
            } else {
                showNotification('Agent deleted successfully', 'success');
                closeModal('editAgentModal');
                loadAgents();
            }
        })
        .catch(error => {
            console.error('Error deleting agent:', error);
            showNotification('Failed to delete agent', 'error');
        });
    }
}

// ===== JOBS FUNCTIONS =====

// Load Jobs
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs');
        const jobs = await response.json();
        
        const tbody = document.getElementById('jobsTableBody');
        tbody.innerHTML = '';
        
        if (jobs.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="jobs-empty-state">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                        <h4>No Migration Jobs Yet</h4>
                        <p>Start by creating your first migration job</p>
                        <button class="btn btn-primary" onclick="showNewJobModal()">Create First Job</button>
                    </td>
                </tr>
            `;
        } else {
            jobs.forEach(job => {
                const row = document.createElement('tr');
                row.onclick = () => showInlineJobDetail(job.id);
                
                const createdDate = new Date(job.created_at).toLocaleDateString();
                const statusClass = job.status.toLowerCase();
                
                row.innerHTML = `
                    <td>
                        <div class="job-name">
                            <strong>${job.name}</strong>
                            ${job.description ? `<br><small>${job.description}</small>` : ''}
                        </div>
                    </td>
                    <td>${job.source_name || 'N/A'}</td>
                    <td>${job.target_name || 'N/A'}</td>
                    <td>
                        <span class="status-badge ${statusClass}">${job.status}</span>
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${job.progress}%"></div>
                            </div>
                            <span>${job.progress}%</span>
                        </div>
                    </td>
                    <td>${createdDate}</td>
                    <td>
                        <div class="job-actions">
                            <button class="job-action-btn" onclick="event.stopPropagation(); showInlineJobDetail('${job.id}')" title="View Details">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                </svg>
                            </button>
                            <button class="job-action-btn" onclick="event.stopPropagation(); deleteJob('${job.id}', '${job.name}')" title="Delete Job">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                </svg>
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
        showNotification('Error loading jobs', 'error');
    }
}

// Show Inline Job Form
async function showNewJobModal() {
    try {
        // Hide jobs table and show inline form
        document.getElementById('jobsTableContainer').style.display = 'none';
        document.getElementById('inlineCreateJob').style.display = 'block';
        
        // Load sources and targets
        await Promise.all([loadInlineJobSources(), loadInlineJobTargets()]);
        
        // Initialize @ mention system
        initializeMentionSystem();
    } catch (error) {
        console.error('Error showing inline job form:', error);
        showNotification('Failed to load job creation form', 'error');
    }
}

// @ Mention System
let selectedCredentials = [];
let mentionSuggestions = [];
let currentMentionIndex = 0;

function initializeMentionSystem() {
    const input = document.getElementById('credentialMentions');
    const suggestionsDiv = document.getElementById('mentionSuggestions');
    selectedCredentials = [];
    updateSelectedCredentialsDisplay();
    
    input.addEventListener('input', handleMentionInput);
    input.addEventListener('keydown', handleMentionKeydown);
    
    // Click outside to close suggestions
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.mention-input-wrapper')) {
            suggestionsDiv.style.display = 'none';
        }
    });
}

async function handleMentionInput(e) {
    const input = e.target;
    const value = input.value;
    const cursorPosition = input.selectionStart;
    
    // Find @ symbol before cursor
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');
    
    if (lastAtIndex !== -1 && lastAtIndex === textBeforeCursor.length - 1 || 
        (lastAtIndex !== -1 && !value.substring(lastAtIndex + 1, cursorPosition).includes(' '))) {
        // Show suggestions
        const query = value.substring(lastAtIndex + 1, cursorPosition);
        await showMentionSuggestions(query);
    } else {
        // Hide suggestions
        document.getElementById('mentionSuggestions').style.display = 'none';
    }
}

async function showMentionSuggestions(query) {
    try {
        const response = await fetch(`/api/credentials/search?q=${query}`);
        const credentials = await response.json();
        
        // Filter out already selected credentials
        mentionSuggestions = credentials.filter(cred => 
            !selectedCredentials.find(selected => selected.id === cred.id)
        );
        
        const suggestionsDiv = document.getElementById('mentionSuggestions');
        
        if (mentionSuggestions.length > 0) {
            currentMentionIndex = 0;
            suggestionsDiv.innerHTML = mentionSuggestions.map((cred, index) => `
                <div class="mention-suggestion ${index === 0 ? 'active' : ''}" 
                     data-index="${index}"
                     onclick="selectMention(${index})">
                    <span class="mention-icon">${cred.icon}</span>
                    <div class="mention-info">
                        <div class="mention-name">@${cred.name}</div>
                        <div class="mention-type">${cred.type}</div>
                    </div>
                </div>
            `).join('');
            suggestionsDiv.style.display = 'block';
        } else {
            suggestionsDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading mention suggestions:', error);
    }
}

function handleMentionKeydown(e) {
    const suggestionsDiv = document.getElementById('mentionSuggestions');
    if (suggestionsDiv.style.display === 'none') return;
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            currentMentionIndex = Math.min(currentMentionIndex + 1, mentionSuggestions.length - 1);
            updateMentionHighlight();
            break;
        case 'ArrowUp':
            e.preventDefault();
            currentMentionIndex = Math.max(currentMentionIndex - 1, 0);
            updateMentionHighlight();
            break;
        case 'Enter':
            e.preventDefault();
            if (mentionSuggestions.length > 0) {
                selectMention(currentMentionIndex);
            }
            break;
        case 'Escape':
            suggestionsDiv.style.display = 'none';
            break;
    }
}

function updateMentionHighlight() {
    document.querySelectorAll('.mention-suggestion').forEach((elem, index) => {
        elem.classList.toggle('active', index === currentMentionIndex);
    });
}

function selectMention(index) {
    const credential = mentionSuggestions[index];
    const input = document.getElementById('credentialMentions');
    const value = input.value;
    const cursorPosition = input.selectionStart;
    
    // Find @ symbol before cursor
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');
    
    // Replace the @ mention with empty string
    input.value = value.substring(0, lastAtIndex) + value.substring(cursorPosition);
    
    // Add to selected credentials
    selectedCredentials.push(credential);
    updateSelectedCredentialsDisplay();
    
    // Hide suggestions
    document.getElementById('mentionSuggestions').style.display = 'none';
    
    // Focus back on input
    input.focus();
}

function updateSelectedCredentialsDisplay() {
    const container = document.getElementById('selectedCredentials');
    container.innerHTML = selectedCredentials.map(cred => `
        <div class="credential-chip">
            <span class="credential-chip-icon">${cred.icon}</span>
            <span>@${cred.name}</span>
            <button class="credential-chip-remove" onclick="removeCredential('${cred.id}')">&times;</button>
        </div>
    `).join('');
}

function removeCredential(credentialId) {
    selectedCredentials = selectedCredentials.filter(cred => cred.id !== credentialId);
    updateSelectedCredentialsDisplay();
}

// Load Sources for Inline Job Form
async function loadInlineJobSources() {
    try {
        const response = await fetch('/api/sources');
        const sources = await response.json();
        
        const select = document.getElementById('inlineSourceSelect');
        select.innerHTML = '<option value="">Choose source...</option>';
        
        sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source.id;
            option.textContent = `${source.name} (${source.type})`;
            option.dataset.name = source.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading sources for inline job form:', error);
    }
}

// Load Targets for Inline Job Form
async function loadInlineJobTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        const select = document.getElementById('inlineTargetSelect');
        select.innerHTML = '<option value="">Choose target...</option>';
        
        targets.forEach(target => {
            const option = document.createElement('option');
            option.value = target.id;
            option.textContent = target.name;
            option.dataset.name = target.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading targets for inline job form:', error);
    }
}

// Cancel Inline Job Form
function cancelInlineJob() {
    // Show jobs table and hide inline form
    document.getElementById('jobsTableContainer').style.display = 'block';
    document.getElementById('inlineCreateJob').style.display = 'none';
    
    // Reset form
    document.getElementById('inlineJobName').value = '';
    document.getElementById('inlineSourceSelect').value = '';
    document.getElementById('inlineTargetSelect').value = '';
    
    // Clear selected credentials
    selectedCredentials = [];
    document.getElementById('selectedCredentials').innerHTML = '';
    document.getElementById('credentialMentions').value = '';
}

// Save Inline Job
async function saveInlineJob() {
    const nameInput = document.getElementById('inlineJobName');
    const sourceSelect = document.getElementById('inlineSourceSelect');
    const targetSelect = document.getElementById('inlineTargetSelect');
    
    // Validate required fields
    if (!nameInput.value.trim()) {
        showNotification('Job name is required', 'error');
        nameInput.focus();
        return;
    }
    
    if (!sourceSelect.value) {
        showNotification('Please select a source repository', 'error');
        sourceSelect.focus();
        return;
    }
    
    if (!targetSelect.value) {
        showNotification('Please select a target platform', 'error');
        targetSelect.focus();
        return;
    }
    
    // Show loading state
    const btn = document.getElementById('inlineSaveJobBtnText');
    const spinner = document.getElementById('inlineSaveJobSpinner');
    btn.style.display = 'none';
    spinner.style.display = 'block';
    
    try {
        const jobData = {
            name: nameInput.value.trim(),
            description: `${sourceSelect.options[sourceSelect.selectedIndex].dataset.name} to ${targetSelect.options[targetSelect.selectedIndex].dataset.name} migration`,
            source_id: sourceSelect.value,
            source_name: sourceSelect.options[sourceSelect.selectedIndex].dataset.name,
            target_id: targetSelect.value,
            target_name: targetSelect.options[targetSelect.selectedIndex].dataset.name,
            config: {
                priority: 'medium',
                credentials: selectedCredentials.map(cred => ({
                    id: cred.id,
                    name: cred.name,
                    type: cred.type
                }))
            },
            created_by: 'system'
        };
        
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Migration job created successfully!', 'success');
            
            // Reset form and show jobs table
            cancelInlineJob();
            
            // Reload jobs
            await loadJobs();
            
            // Show job detail modal after a brief delay
            setTimeout(() => showJobDetail(result.id), 500);
        } else {
            showNotification(result.error || 'Failed to create job', 'error');
        }
    } catch (error) {
        console.error('Error creating job:', error);
        showNotification('Failed to create job', 'error');
    } finally {
        // Reset button state
        btn.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Load Create Job Page
async function loadCreateJobPage() {
    try {
        // Load sources and targets for the create job page
        await Promise.all([loadCreateJobSources(), loadCreateJobTargets()]);
    } catch (error) {
        console.error('Error loading create job page:', error);
        showNotification('Failed to load job creation page', 'error');
    }
}

// Load Sources for Create Job Page
async function loadCreateJobSources() {
    try {
        const response = await fetch('/api/sources');
        const sources = await response.json();
        
        const select = document.getElementById('createSourceSelect');
        select.innerHTML = '<option value="">Choose source repository...</option>';
        
        sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source.id;
            option.textContent = `${source.name} (${source.type})`;
            option.dataset.name = source.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading sources for create job page:', error);
    }
}

// Load Targets for Create Job Page
async function loadCreateJobTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        const select = document.getElementById('createTargetSelect');
        select.innerHTML = '<option value="">Choose target platform...</option>';
        
        targets.forEach(target => {
            const option = document.createElement('option');
            option.value = target.id;
            option.textContent = target.name;
            option.dataset.name = target.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading targets for create job page:', error);
    }
}

// Save Job from Create Job Page
async function saveJob() {
    const nameInput = document.getElementById('createJobName');
    const descriptionInput = document.getElementById('createJobDescription');
    const sourceSelect = document.getElementById('createSourceSelect');
    const targetSelect = document.getElementById('createTargetSelect');
    
    // Validate required fields
    if (!nameInput.value.trim()) {
        showNotification('Job name is required', 'error');
        nameInput.focus();
        return;
    }
    
    if (!sourceSelect.value) {
        showNotification('Please select a source repository', 'error');
        sourceSelect.focus();
        return;
    }
    
    if (!targetSelect.value) {
        showNotification('Please select a target platform', 'error');
        targetSelect.focus();
        return;
    }
    
    // Show loading state
    const btn = document.getElementById('saveJobBtnText');
    const spinner = document.getElementById('saveJobSpinner');
    btn.style.display = 'none';
    spinner.style.display = 'block';
    
    try {
        const jobData = {
            name: nameInput.value.trim(),
            description: descriptionInput.value.trim(),
            source_id: sourceSelect.value,
            source_name: sourceSelect.options[sourceSelect.selectedIndex].dataset.name,
            target_id: targetSelect.value,
            target_name: targetSelect.options[targetSelect.selectedIndex].dataset.name,
            config: {
                priority: 'medium'
            },
            created_by: 'system'
        };
        
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Migration job created successfully!', 'success');
            
            // Reset form
            nameInput.value = '';
            descriptionInput.value = '';
            sourceSelect.value = '';
            targetSelect.value = '';
            
            // Navigate back to jobs page
            navigateToPage('jobs');
            
            // Show job detail modal after a brief delay
            setTimeout(() => showJobDetail(result.id), 500);
        } else {
            showNotification(result.error || 'Failed to create job', 'error');
        }
    } catch (error) {
        console.error('Error creating job:', error);
        showNotification('Failed to create job', 'error');
    } finally {
        // Reset button state
        btn.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Legacy functions for modal (keeping for compatibility)
// Load Sources for Job Creation
async function loadJobSources() {
    try {
        const response = await fetch('/api/sources');
        const sources = await response.json();
        
        const select = document.getElementById('sourceSelect');
        if (select) {
            select.innerHTML = '<option value="">Select source...</option>';
            
            sources.forEach(source => {
                const option = document.createElement('option');
                option.value = source.id;
                option.textContent = `${source.name} (${source.type})`;
                option.dataset.name = source.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading sources for job:', error);
    }
}

// Load Targets for Job Creation
async function loadJobTargets() {
    try {
        const response = await fetch('/api/targets');
        const targets = await response.json();
        
        const select = document.getElementById('targetSelect');
        if (select) {
            select.innerHTML = '<option value="">Select target...</option>';
            
            targets.forEach(target => {
                const option = document.createElement('option');
                option.value = target.id;
                option.textContent = target.name;
                option.dataset.name = target.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading targets for job:', error);
    }
}

// Create Job
async function createJob() {
    const nameInput = document.getElementById('jobName');
    const descriptionInput = document.getElementById('jobDescription');
    const sourceSelect = document.getElementById('sourceSelect');
    const targetSelect = document.getElementById('targetSelect');
    
    // Validate required fields
    if (!nameInput.value.trim()) {
        showNotification('Job name is required', 'error');
        nameInput.focus();
        return;
    }
    
    if (!sourceSelect.value) {
        showNotification('Please select a source repository', 'error');
        sourceSelect.focus();
        return;
    }
    
    if (!targetSelect.value) {
        showNotification('Please select a target platform', 'error');
        targetSelect.focus();
        return;
    }
    
    // Show loading state
    const btn = document.getElementById('createJobBtnText');
    const spinner = document.getElementById('createJobSpinner');
    btn.style.display = 'none';
    spinner.style.display = 'block';
    
    try {
        const jobData = {
            name: nameInput.value.trim(),
            description: descriptionInput.value.trim(),
            source_id: sourceSelect.value,
            source_name: sourceSelect.options[sourceSelect.selectedIndex].dataset.name,
            target_id: targetSelect.value,
            target_name: targetSelect.options[targetSelect.selectedIndex].dataset.name,
            config: {
                priority: 'medium'
            },
            created_by: 'system'
        };
        
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Migration job created successfully!', 'success');
            closeModal('newJobModal');
            
            // Reset form
            nameInput.value = '';
            descriptionInput.value = '';
            sourceSelect.value = '';
            targetSelect.value = '';
            
            // Reload jobs
            await loadJobs();
        } else {
            showNotification(result.error || 'Failed to create job', 'error');
        }
    } catch (error) {
        console.error('Error creating job:', error);
        showNotification('Failed to create job', 'error');
    } finally {
        // Reset button state
        btn.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Show Inline Job Detail
async function showInlineJobDetail(jobId) {
    try {
        const response = await fetch(`/api/jobs/${jobId}`);
        const job = await response.json();
        
        if (!response.ok) {
            showNotification(job.error || 'Job not found', 'error');
            return;
        }
        
        // Hide tables and forms, show job detail
        document.getElementById('jobsTableContainer').style.display = 'none';
        document.getElementById('inlineCreateJob').style.display = 'none';
        document.getElementById('inlineJobDetail').style.display = 'block';
        
        // Populate timeline details
        document.getElementById('inlineJobDetailName').textContent = job.name;
        document.getElementById('inlineJobDetailDescription').textContent = job.description || 'Track your migration progress step by step';
        document.getElementById('inlineJobDetailSource').textContent = job.source_name || 'N/A';
        document.getElementById('inlineJobDetailTarget').textContent = job.target_name || 'N/A';
        document.getElementById('inlineJobDetailCreated').textContent = new Date(job.created_at).toLocaleDateString();
        
        // Show linked credentials if any
        const credentialsContainer = document.getElementById('inlineJobDetailCredentials');
        if (credentialsContainer && job.config && job.config.credentials && job.config.credentials.length > 0) {
            credentialsContainer.innerHTML = `
                <div class="linked-credentials">
                    <h4>Linked Credentials</h4>
                    <div class="credential-chips">
                        ${job.config.credentials.map(cred => `
                            <div class="credential-chip">
                                <span>${getCredentialIcon(cred.type)}</span>
                                <span>${cred.name}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            credentialsContainer.style.display = 'block';
        } else if (credentialsContainer) {
            credentialsContainer.style.display = 'none';
        }
        
        // Render beautiful timeline
        renderInlineJobStages(job.stages, job.current_stage);
        
        // Store job ID for refresh
        document.getElementById('inlineJobDetail').dataset.jobId = jobId;
    } catch (error) {
        console.error('Error loading job details:', error);
        showNotification('Failed to load job details', 'error');
    }
}

// Close Inline Job Detail
function closeInlineJobDetail() {
    document.getElementById('inlineJobDetail').style.display = 'none';
    document.getElementById('jobsTableContainer').style.display = 'block';
}

// Show Job Detail Modal (keeping for backward compatibility)
async function showJobDetail(jobId) {
    // Redirect to inline view
    await showInlineJobDetail(jobId);
}

// Render Job Stages (Beautiful Timeline)
function renderJobStages(stages, currentStage) {
    const container = document.getElementById('jobStagesContainer');
    container.innerHTML = '';
    
    if (!stages || stages.length === 0) {
        container.innerHTML = `
            <div class="timeline-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>No migration stages yet</p>
            </div>
        `;
        return;
    }
    
    stages.forEach((stage, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = `timeline-item ${stage.status.replace('_', '-')}`;
        
        timelineItem.innerHTML = `
            <div class="timeline-card">
                <div class="timeline-card-header">
                    <h3 class="timeline-stage-title">${stage.name}</h3>
                    <span class="timeline-status ${stage.status.replace('_', '-')}">${stage.status.replace('_', ' ')}</span>
                </div>
                
                <p class="timeline-description">${stage.description}</p>
                
                <div class="timeline-agents">
                    ${stage.agents.map(agent => `
                        <div class="timeline-agent">
                            <span>👤</span>
                            <span>${agent}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="timeline-tasks">
                    ${stage.tasks.map(task => `
                        <div class="timeline-task">
                            <div class="task-status-dot ${task.status.replace('_', '-')}"></div>
                            <span class="task-name">${task.name}</span>
                            <span class="task-agent">${task.agent}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.appendChild(timelineItem);
    });
}

// Render Inline Job Stages
function renderInlineJobStages(stages, currentStage) {
    const container = document.getElementById('inlineJobStagesContainer');
    container.innerHTML = '';
    
    if (!stages || stages.length === 0) {
        container.innerHTML = `
            <div class="timeline-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>No migration stages yet</p>
            </div>
        `;
        return;
    }
    
    stages.forEach((stage, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = `timeline-item ${stage.status.replace('_', '-')}`;
        
        timelineItem.innerHTML = `
            <div class="timeline-card">
                <div class="timeline-card-header">
                    <h3 class="timeline-stage-title">${stage.name}</h3>
                    <span class="timeline-status ${stage.status.replace('_', '-')}">${stage.status.replace('_', ' ')}</span>
                </div>
                
                <p class="timeline-description">${stage.description}</p>
                
                <div class="timeline-agents">
                    ${stage.agents.map(agent => `
                        <div class="timeline-agent">
                            <span>👤</span>
                            <span>${agent}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="timeline-tasks">
                    ${stage.tasks.map(task => `
                        <div class="timeline-task">
                            <div class="task-status-dot ${task.status.replace('_', '-')}"></div>
                            <span class="task-name">${task.name}</span>
                            <span class="task-agent">${task.agent}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.appendChild(timelineItem);
    });
}

// Render Job Logs
function renderJobLogs(logs) {
    const container = document.getElementById('jobLogsContainer');
    container.innerHTML = '';
    
    if (logs.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 48px; height: 48px; margin-bottom: 1rem; opacity: 0.5;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>No activity logs yet</p>
            </div>
        `;
        return;
    }
    
    // Sort logs by timestamp (newest first)
    const sortedLogs = logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    sortedLogs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const timestamp = new Date(log.timestamp).toLocaleTimeString();
        
        logEntry.innerHTML = `
            <div class="log-timestamp">${timestamp}</div>
            <div class="log-agent">${log.agent}</div>
            <div class="log-message">${log.message}</div>
        `;
        
        container.appendChild(logEntry);
    });
}

// Refresh Job Detail
async function refreshJobDetail() {
    const modal = document.getElementById('jobDetailModal');
    const jobId = modal.dataset.jobId;
    
    if (jobId) {
        await showJobDetail(jobId);
    }
}

// ===== CONFIGURATION FUNCTIONS =====

// Switch job detail tabs
function switchJobDetailTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.job-detail-tabs .tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show/hide content
    if (tabName === 'timeline') {
        document.getElementById('timelineTabContent').style.display = 'block';
        document.getElementById('configurationTabContent').style.display = 'none';
    } else {
        document.getElementById('timelineTabContent').style.display = 'none';
        document.getElementById('configurationTabContent').style.display = 'block';
        // Load configuration when switching to config tab
        loadJobConfiguration();
    }
}

// Load job configuration
async function loadJobConfiguration() {
    const jobId = document.getElementById('inlineJobDetail').dataset.jobId;
    if (!jobId) return;
    
    try {
        const response = await fetch(`/api/jobs/${jobId}/config`);
        const config = await response.json();
        
        // Populate global integrations
        if (config.global_config && config.global_config.integrations) {
            const integrations = config.global_config.integrations;
            
            // Jira
            if (integrations.jira) {
                document.getElementById('jiraEnabled').checked = integrations.jira.enabled || false;
                document.getElementById('jiraUrl').value = integrations.jira.url || '';
                document.getElementById('jiraProjectKey').value = integrations.jira.project_key || '';
                document.getElementById('jiraAuth').value = integrations.jira.auth || '';
                toggleIntegration('jira');
            }
            
            // Slack
            if (integrations.slack) {
                document.getElementById('slackEnabled').checked = integrations.slack.enabled || false;
                document.getElementById('slackWebhook').value = integrations.slack.webhook_url || '';
                document.getElementById('slackChannel').value = integrations.slack.channels?.notifications || '#general';
                document.getElementById('slackAlertChannel').value = integrations.slack.channels?.alerts || '#alerts';
                toggleIntegration('slack');
            }
            
            // Email
            if (integrations.email) {
                document.getElementById('emailEnabled').checked = integrations.email.enabled || false;
                document.getElementById('emailHost').value = integrations.email.smtp_config?.host || '';
                document.getElementById('emailPort').value = integrations.email.smtp_config?.port || '587';
                document.getElementById('emailFrom').value = integrations.email.from_address || '';
                toggleIntegration('email');
            }
        }
        
        // Load stage configurations
        await loadStageConfigurations(config.stage_configs || {});
        
    } catch (error) {
        console.error('Error loading job configuration:', error);
        showNotification('Failed to load configuration', 'error');
    }
}

// Load stage configurations
async function loadStageConfigurations(stageConfigs) {
    const container = document.getElementById('stageConfigList');
    container.innerHTML = '';
    
    // Get job stages
    const jobId = document.getElementById('inlineJobDetail').dataset.jobId;
    const response = await fetch(`/api/jobs/${jobId}`);
    const job = await response.json();
    
    if (job.stages) {
        job.stages.forEach(stage => {
            const config = stageConfigs[stage.id] || { enabled: true };
            const item = document.createElement('div');
            item.className = 'stage-config-item';
            item.innerHTML = `
                <div class="stage-config-icon">🔧</div>
                <div class="stage-config-info">
                    <div class="stage-config-name">${stage.name}</div>
                    <div class="stage-config-status">
                        ${config.enabled ? 'Configured' : 'Not configured'}
                    </div>
                </div>
                <button class="stage-config-action" onclick="editStageConfig('${stage.id}', '${stage.name}')">
                    ${config.enabled ? 'Edit' : 'Configure'}
                </button>
            `;
            container.appendChild(item);
        });
    }
}

// Toggle integration visibility
function toggleIntegration(integration) {
    const enabled = document.getElementById(`${integration}Enabled`).checked;
    const configDiv = document.getElementById(`${integration}Config`);
    configDiv.style.display = enabled ? 'block' : 'none';
}

// Test integration connection
async function testIntegration(integration) {
    const config = {};
    
    // Gather configuration based on integration type
    switch (integration) {
        case 'jira':
            config.enabled = document.getElementById('jiraEnabled').checked;
            config.url = document.getElementById('jiraUrl').value;
            config.project_key = document.getElementById('jiraProjectKey').value;
            config.auth = document.getElementById('jiraAuth').value;
            break;
        case 'slack':
            config.enabled = document.getElementById('slackEnabled').checked;
            config.webhook_url = document.getElementById('slackWebhook').value;
            config.channels = {
                notifications: document.getElementById('slackChannel').value,
                alerts: document.getElementById('slackAlertChannel').value
            };
            break;
        case 'email':
            config.enabled = document.getElementById('emailEnabled').checked;
            config.smtp_config = {
                host: document.getElementById('emailHost').value,
                port: parseInt(document.getElementById('emailPort').value) || 587
            };
            config.from_address = document.getElementById('emailFrom').value;
            break;
    }
    
    try {
        const response = await fetch('/api/integrations/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: integration, config })
        });
        
        const result = await response.json();
        
        // Show test result
        const card = document.querySelector(`.integration-card[data-integration="${integration}"]`);
        const existingResult = card.querySelector('.test-result');
        if (existingResult) existingResult.remove();
        
        const resultDiv = document.createElement('div');
        resultDiv.className = `test-result ${result.success ? 'success' : 'error'}`;
        resultDiv.innerHTML = `
            <span class="test-result-icon">${result.success ? '✅' : '❌'}</span>
            ${result.details?.message || result.error || 'Test completed'}
        `;
        
        card.querySelector('.integration-content').appendChild(resultDiv);
        
        // Remove result after 5 seconds
        setTimeout(() => resultDiv.remove(), 5000);
        
    } catch (error) {
        console.error('Error testing integration:', error);
        showNotification('Failed to test integration', 'error');
    }
}

// Save job configuration
async function saveJobConfiguration() {
    const jobId = document.getElementById('inlineJobDetail').dataset.jobId;
    if (!jobId) return;
    
    // Show loading state
    const btnText = document.getElementById('saveConfigBtnText');
    const spinner = document.getElementById('saveConfigSpinner');
    btnText.style.display = 'none';
    spinner.style.display = 'block';
    
    try {
        // Gather configuration
        const config = {
            job_id: jobId,
            global_config: {
                integrations: {
                    jira: {
                        enabled: document.getElementById('jiraEnabled').checked,
                        url: document.getElementById('jiraUrl').value,
                        project_key: document.getElementById('jiraProjectKey').value,
                        auth: document.getElementById('jiraAuth').value
                    },
                    slack: {
                        enabled: document.getElementById('slackEnabled').checked,
                        webhook_url: document.getElementById('slackWebhook').value,
                        channels: {
                            notifications: document.getElementById('slackChannel').value,
                            alerts: document.getElementById('slackAlertChannel').value
                        }
                    },
                    email: {
                        enabled: document.getElementById('emailEnabled').checked,
                        from_address: document.getElementById('emailFrom').value,
                        smtp_config: {
                            host: document.getElementById('emailHost').value,
                            port: parseInt(document.getElementById('emailPort').value) || 587
                        }
                    }
                },
                defaults: {
                    timeout_minutes: 30,
                    retry_attempts: 3,
                    notification_level: 'all'
                }
            },
            stage_configs: {}  // Will be populated when implementing stage config
        };
        
        const response = await fetch(`/api/jobs/${jobId}/config`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Configuration saved successfully', 'success');
        } else {
            showNotification(result.error || 'Failed to save configuration', 'error');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showNotification('Failed to save configuration', 'error');
    } finally {
        // Hide loading state
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Edit stage configuration
function editStageConfig(stageId, stageName) {
    // This would open a modal or inline editor for stage-specific config
    showNotification(`Stage configuration for ${stageName} - Coming soon!`, 'info');
}

// Load configuration template
async function loadConfigurationTemplate() {
    try {
        const response = await fetch('/api/config/templates?type=global');
        const templates = await response.json();
        
        // For now, just show available templates
        if (templates.length > 0) {
            showNotification(`${templates.length} templates available`, 'info');
        } else {
            showNotification('No templates available', 'info');
        }
    } catch (error) {
        console.error('Error loading templates:', error);
        showNotification('Failed to load templates', 'error');
    }
}

// ===== CREDENTIALS FUNCTIONS =====

// Switch settings tab
function switchSettingsTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.settings-tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.settings-tab-button').classList.add('active');
    
    // Show/hide content
    document.querySelectorAll('.settings-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Load data for the tab
    if (tabName === 'credentials') {
        loadCredentials();
    } else if (tabName === 'connections') {
        loadConnections();
    }
}

// Load credentials
// Component: Render Credential Card
function renderCredentialCard(credential) {
    const statusText = {
        'active': 'Connected',
        'error': 'Error',
        'unchecked': 'Not tested'
    };
    
    const escapedName = credential.name.replace(/'/g, "\\'");
    const icon = getEnhancedCredentialIcon(credential.type);
    const formattedType = credential.type.replace('_', ' ').toLowerCase();
    
    return `
        <div class="credential-card" data-id="${credential.id}" data-type="${credential.type}">
            <div class="credential-card-header">
                <div class="credential-info">
                    <div class="credential-name">${credential.name}</div>
                    <div class="credential-type">
                        <span class="credential-icon">${icon}</span>
                        ${formattedType}
                    </div>
                </div>
            </div>
            <div class="credential-status ${credential.status || 'unchecked'}">
                ${statusText[credential.status] || statusText['unchecked']}
            </div>
            <div class="credential-card-footer">
                <button class="credential-action" onclick="testCredential('${credential.id}')">Test</button>
                <button class="credential-action" onclick="editCredential('${credential.id}')">Edit</button>
                <button class="credential-action" onclick="deleteCredential('${credential.id}', '${escapedName}')">Delete</button>
            </div>
        </div>
    `;
}

// Load and Display Credentials
async function loadCredentials() {
    console.log('loadCredentials() called');
    try {
        const response = await fetch('/api/credentials');
        console.log('Credentials API response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const credentials = await response.json();
        console.log('Credentials loaded:', credentials);
        
        const grid = document.getElementById('credentialsGrid');
        const emptyState = document.getElementById('credentialsEmpty');
        
        if (!grid) {
            console.error('credentialsGrid element not found!');
            return;
        }
        
        if (!emptyState) {
            console.error('credentialsEmpty element not found!');
            return;
        }
        
        if (credentials.length === 0) {
            console.log('No credentials found, showing empty state');
            grid.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            console.log(`Displaying ${credentials.length} credentials`);
            grid.style.display = 'grid';
            emptyState.style.display = 'none';
            
            // Use component function to render each credential
            grid.innerHTML = credentials.map(renderCredentialCard).join('');
        }
    } catch (error) {
        console.error('Error loading credentials:', error);
        showNotification('Failed to load credentials', 'error');
    }
}

// Show add credential modal
async function showAddCredentialModal() {
    document.getElementById('addCredentialModal').classList.add('show');
    // Reset form
    document.getElementById('credentialName').value = '';
    document.getElementById('credentialForm').style.display = 'none';
    document.getElementById('credentialFields').innerHTML = '';
    document.getElementById('saveCredentialBtn').disabled = true;
    document.getElementById('credentialTypeSearch').value = '';
    
    // Load credential types
    await loadCredentialTypes();
}

// Load credential types organized by category
async function loadCredentialTypes() {
    try {
        const response = await fetch('/api/credentials/types');
        const types = await response.json();
        
        // Organize types by category
        const categories = {
            'project_management': { name: 'Project Management', types: [] },
            'version_control': { name: 'Version Control', types: [] },
            'communication': { name: 'Communication', types: [] },
            'database': { name: 'Databases', types: [] },
            'cloud': { name: 'Cloud Services', types: [] },
            'api': { name: 'APIs & Authentication', types: [] },
            'other': { name: 'Other Services', types: [] },
            'custom': { name: 'Custom', types: [] }
        };
        
        // Group types by category
        Object.entries(types).forEach(([key, config]) => {
            const category = config.category || 'other';
            if (categories[category]) {
                categories[category].types.push({ key, ...config });
            }
        });
        
        // Render categories
        const container = document.getElementById('credentialTypesContainer');
        container.innerHTML = '';
        
        Object.entries(categories).forEach(([categoryKey, category]) => {
            if (category.types.length === 0) return;
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'credential-category';
            categoryDiv.innerHTML = `
                <div class="credential-category-title">${category.name}</div>
                <div class="credential-types-grid">
                    ${category.types.map(type => `
                        <div class="credential-type-card" onclick="selectCredentialType('${type.key}')" data-type="${type.key}">
                            <span class="type-icon">${type.icon}</span>
                            <span class="type-name">${type.name}</span>
                        </div>
                    `).join('')}
                </div>
            `;
            container.appendChild(categoryDiv);
        });
    } catch (error) {
        console.error('Error loading credential types:', error);
        document.getElementById('credentialTypesContainer').innerHTML = 
            '<div class="error-message">Failed to load credential types</div>';
    }
}

// Filter credential types
function filterCredentialTypes() {
    const searchTerm = document.getElementById('credentialTypeSearch').value.toLowerCase();
    const cards = document.querySelectorAll('.credential-type-card');
    const categories = document.querySelectorAll('.credential-category');
    
    cards.forEach(card => {
        const typeName = card.querySelector('.type-name').textContent.toLowerCase();
        const shouldShow = typeName.includes(searchTerm);
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // Hide empty categories
    categories.forEach(category => {
        const visibleCards = category.querySelectorAll('.credential-type-card:not([style*="display: none"])');
        category.style.display = visibleCards.length > 0 ? '' : 'none';
    });
}

// Select credential type
let selectedCredentialType = null;

async function selectCredentialType(type) {
    selectedCredentialType = type;
    
    // Update UI
    document.querySelectorAll('.credential-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.credential-type-card[data-type="${type}"]`).classList.add('selected');
    
    // Show form
    document.getElementById('credentialForm').style.display = 'block';
    document.getElementById('saveCredentialBtn').disabled = false;
    
    // Load fields for this type
    try {
        const response = await fetch('/api/credentials/types');
        const types = await response.json();
        const typeConfig = types[type];
        
        if (typeConfig && typeConfig.fields) {
            const fieldsContainer = document.getElementById('credentialFields');
            fieldsContainer.innerHTML = typeConfig.fields.map(field => `
                <div class="form-group">
                    <label>${field.label}</label>
                    <input 
                        type="${field.type}" 
                        id="field_${field.key}" 
                        placeholder="${field.placeholder}" 
                        class="form-input"
                        ${field.type === 'number' ? 'min="1" max="65535"' : ''}
                    >
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading credential fields:', error);
    }
}

// Save credential
async function saveCredential() {
    const name = document.getElementById('credentialName').value.trim();
    if (!name) {
        showNotification('Please enter a credential name', 'error');
        return;
    }
    
    if (!selectedCredentialType) {
        showNotification('Please select a credential type', 'error');
        return;
    }
    
    // Gather field values
    const data = {};
    const inputs = document.querySelectorAll('#credentialFields input');
    inputs.forEach(input => {
        const key = input.id.replace('field_', '');
        data[key] = input.value;
    });
    
    // Show loading state
    const btnText = document.getElementById('saveCredentialBtnText');
    const spinner = document.getElementById('saveCredentialSpinner');
    btnText.style.display = 'none';
    spinner.style.display = 'block';
    
    try {
        const response = await fetch('/api/credentials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                type: selectedCredentialType,
                data: data
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Credential saved successfully', 'success');
            closeModal('addCredentialModal');
            loadCredentials();
        } else {
            showNotification(result.error || 'Failed to save credential', 'error');
        }
    } catch (error) {
        console.error('Error saving credential:', error);
        showNotification('Failed to save credential', 'error');
    } finally {
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Test credential
async function testCredential(credentialId) {
    try {
        const response = await fetch(`/api/credentials/${credentialId}/test`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message || 'Connection successful', 'success');
            // Reload to update status
            loadCredentials();
        } else {
            showNotification(result.message || 'Connection failed', 'error');
        }
    } catch (error) {
        console.error('Error testing credential:', error);
        showNotification('Failed to test credential', 'error');
    }
}

// Edit credential
function editCredential(credentialId) {
    showNotification('Edit credential - Coming soon!', 'info');
}

// Delete credential
async function deleteCredential(credentialId, credentialName) {
    if (confirm(`Are you sure you want to delete the credential "${credentialName}"? This action cannot be undone.`)) {
        try {
            const response = await fetch(`/api/credentials/${credentialId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showNotification('Credential deleted successfully', 'success');
                loadCredentials();
            } else {
                showNotification('Failed to delete credential', 'error');
            }
        } catch (error) {
            console.error('Error deleting credential:', error);
            showNotification('Failed to delete credential', 'error');
        }
    }
}

// Component: Render Connection Item
function renderConnectionItem(credential) {
    const icon = getEnhancedCredentialIcon(credential.type);
    return `
        <div class="connection-item" data-type="${credential.type}">
            <div class="connection-icon">${icon}</div>
            <div class="connection-info">
                <div class="connection-name">${credential.name}</div>
                <div class="connection-details">${credential.type.replace('_', ' ').toUpperCase()}</div>
            </div>
            <div class="connection-status">
                <div class="status-indicator ${getConnectionStatus(credential.status)}">
                    <span class="status-dot"></span>
                    <span>${getConnectionStatusText(credential.status)}</span>
                </div>
                <button class="connection-test-btn" onclick="testCredential('${credential.id}')">
                    Test Connection
                </button>
            </div>
        </div>
    `;
}

// Component: Render Empty Connections State
function renderEmptyConnectionsState() {
    return `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <h5>No Connections</h5>
            <p>Add credentials first to see connection status</p>
        </div>
    `;
}

// Load and Display Connections
async function loadConnections() {
    try {
        const response = await fetch('/api/credentials');
        const credentials = await response.json();
        
        const container = document.getElementById('connectionsList');
        
        if (credentials.length === 0) {
            container.innerHTML = renderEmptyConnectionsState();
        } else {
            // Use component function to render each connection
            container.innerHTML = credentials.map(renderConnectionItem).join('');
        }
    } catch (error) {
        console.error('Error loading connections:', error);
        showNotification('Failed to load connections', 'error');
    }
}

// Helper functions
function getConnectionStatus(status) {
    switch (status) {
        case 'active': return 'connected';
        case 'error': return 'disconnected';
        default: return 'checking';
    }
}

function getCredentialIcon(type) {
    const icons = {
        'jira': '🎫',
        'slack': '💬',
        'email': '📧',
        'github': '🐙',
        'teams': '👥',
        'postgresql': '🐘'
    };
    return icons[type] || '🔑';
}

// Enhanced icons for connections
function getEnhancedCredentialIcon(type) {
    const icons = {
        // Project Management - Gold/Yellow theme
        'jira': '<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><path d="M3 3h18l-3 9 3 9H3l3-9z"/></svg>',
        'jira_local': '<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M3 7l9-4 9 4M12 3v4"/></svg>',
        
        // Version Control - Purple theme
        'github': '<svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>',
        'gitlab': '<svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><path d="M22.65 14.39L12 22.13 1.35 14.39a.84.84 0 0 1-.3-.94l1.22-3.78 2.44-7.51A.42.42 0 0 1 4.82 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.49h8.1l2.44-7.51A.42.42 0 0 1 18.6 2a.43.43 0 0 1 .58 0 .42.42 0 0 1 .11.18l2.44 7.51L23 13.45a.84.84 0 0 1-.35.94z"/></svg>',
        'bitbucket': '<svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><path d="M3.6 3a.83.83 0 0 0-.8.9l2.5 15.3a1 1 0 0 0 1 .8h11.4a.83.83 0 0 0 .8-.7l2.5-15.4a.83.83 0 0 0-.8-.9H3.6zM9 14l3-6 3 6H9z"/></svg>',
        
        // Communication - Blue theme
        'slack': '<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M14.5 10c-.83 0-1.5-.67-1.5-1.5v-5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5z"/><path d="M20.5 10H19V8.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/><path d="M9.5 14c.83 0 1.5.67 1.5 1.5v5c0 .83-.67 1.5-1.5 1.5S8 21.33 8 20.5v-5c0-.83.67-1.5 1.5-1.5z"/><path d="M3.5 14H5v1.5c0 .83-.67 1.5-1.5 1.5S2 16.33 2 15.5 2.67 14 3.5 14z"/><path d="M14 14.5c0-.83.67-1.5 1.5-1.5h5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-5c-.83 0-1.5-.67-1.5-1.5z"/><path d="M15.5 19H14v1.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5-.67-1.5-1.5-1.5z"/><path d="M10 9.5C10 8.67 9.33 8 8.5 8h-5C2.67 8 2 8.67 2 9.5S2.67 11 3.5 11h5c.83 0 1.5-.67 1.5-1.5z"/><path d="M8.5 5H10V3.5C10 2.67 9.33 2 8.5 2S7 2.67 7 3.5 7.67 5 8.5 5z"/></svg>',
        'teams': '<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"/></svg>',
        'email': '<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 5L2 7"/></svg>',
        
        // Databases - Teal theme
        'postgresql': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        'mysql': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M12 12v7"/></svg>',
        'mongodb': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
        'redis': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 9h6v6H9z"/></svg>',
        'oracle': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/></svg>',
        'sqlserver': '<svg viewBox="0 0 24 24" fill="none" stroke="#14b8a6" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
        
        // Cloud Services - Pink theme
        'aws': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><path d="M2 18h20l-2-6 2-6H2l2 6z"/><path d="M6 12h12"/></svg>',
        's3': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="7.5 4.21 12 6.81 16.5 4.21"/><polyline points="7.5 19.79 7.5 14.6 3 12"/><polyline points="21 12 16.5 14.6 16.5 19.79"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
        'azure': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><path d="M6 2L3 8l7.5 13h7.5L6 2z"/><path d="M13 2l5 7-5 12H5.5L13 2z"/></svg>',
        'azure_storage': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><rect x="7" y="7" width="10" height="10" rx="1"/></svg>',
        'gcp': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
        'gcs': '<svg viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2v20"/><path d="M2 12h20"/><ellipse cx="12" cy="12" rx="10" ry="4"/></svg>',
        
        // APIs - Amber theme
        'rest_api': '<svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M21 12h-8l-3.5-3.5"/><path d="M9.5 5.5L3 12l6.5 6.5"/><path d="M21 12v7a2 2 0 0 1-2 2H5"/></svg>',
        'graphql': '<svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><polygon points="12 2 2 7 2 17 12 22 22 17 22 7 12 2"/><line x1="2" y1="7" x2="12" y2="12"/><line x1="12" y1="12" x2="22" y2="7"/><line x1="12" y1="12" x2="12" y2="22"/><line x1="12" y1="12" x2="2" y2="17"/><line x1="12" y1="12" x2="22" y2="17"/><circle cx="12" cy="12" r="3"/></svg>',
        'oauth2': '<svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><line x1="22" y1="11" x2="18" y2="11"/><line x1="20" y1="9" x2="20" y2="13"/></svg>',
        
        // Other Services - Violet theme
        'docker': '<svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><path d="M10 14h4V9h-4z"/><path d="M16 14h4V9h-4z"/><path d="M4 14h4V9H4z"/><path d="M10 8h4V3h-4z"/><path d="M21 14h.01"/><path d="M3 18c1.5 2 4 3 7 3 5.5 0 10-2.2 10-7.1 0 0 1 0 2-1"/></svg>',
        'kubernetes': '<svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><path d="M12 2l-3.5 6h7L12 2z"/><path d="M12 8v8"/><path d="M8 14l-6 3.5L8 21l4-3 4 3 6-3.5L16 14"/><path d="M8 14v4l4 3"/><path d="M16 14v4l-4 3"/><path d="M8 14l4-2 4 2"/></svg>',
        'jenkins': '<svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2"><path d="M16 22h3a2 2 0 0 0 2-2V7.5L14.5 1H6a2 2 0 0 0-2 2v3"/><polyline points="14 1 14 8 21 8"/><path d="M3 15h6"/><path d="M3 18h6"/><path d="M3 21h6"/><circle cx="3" cy="15" r="0.5"/><circle cx="3" cy="18" r="0.5"/><circle cx="3" cy="21" r="0.5"/></svg>',
        
        // Custom - Gray theme
        'custom': '<svg viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>'
    };
    return icons[type] || '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="7" y="2" width="10" height="20" rx="2"/><circle cx="12" cy="18" r="1"/></svg>';
}

function getConnectionStatusText(status) {
    switch (status) {
        case 'active': return 'Connected';
        case 'error': return 'Disconnected';
        default: return 'Not tested';
    }
}

// Test all connections
async function testAllConnections() {
    showNotification('Testing all connections...', 'info');
    
    try {
        const response = await fetch('/api/credentials');
        const credentials = await response.json();
        
        for (const cred of credentials) {
            await testCredential(cred.id);
        }
        
        // Reload connections view
        loadConnections();
    } catch (error) {
        console.error('Error testing connections:', error);
        showNotification('Failed to test connections', 'error');
    }
}

// Delete Job
function deleteJob(jobId, jobName) {
    if (confirm(`Are you sure you want to delete the job "${jobName}"? This action cannot be undone.`)) {
        fetch(`/api/jobs/${jobId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                showNotification(result.error, 'error');
            } else {
                showNotification('Job deleted successfully', 'success');
                loadJobs();
            }
        })
        .catch(error => {
            console.error('Error deleting job:', error);
            showNotification('Failed to delete job', 'error');
        });
    }
}

