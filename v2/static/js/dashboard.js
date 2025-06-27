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
window.showNewJobModal = showNewJobModal;
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
                <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); showExecuteAgentModal('${agent.id}')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" style="width: 16px; height: 16px;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Execute
                </button>
                <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); showEditAgentModal('${agent.id}')">
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

// Show execute agent modal
function showExecuteAgentModal(agentId) {
    const agent = currentAgents.find(a => a.id === agentId);
    if (!agent) return;
    
    // TODO: Implement agent execution modal
    showNotification('Agent execution coming soon!', 'info');
}