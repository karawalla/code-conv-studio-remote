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
                        <span class="source-type-badge ${source.type}">
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
                            <button class="btn btn-sm btn-secondary" onclick="viewSourceTree('${source.id}', '${source.name}')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="14" height="14">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                                </svg>
                                View Tree
                            </button>
                            ${source.type === 'github' ? `
                                <button class="btn btn-sm btn-secondary" onclick="updateSource('${source.id}')">
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
    rootItem.className = 'tree-nav-item';
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
        pathItem.className = 'tree-nav-item';
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