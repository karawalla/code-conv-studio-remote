// Application State
class AppState {
    constructor() {
        this.eventSource = null;
        this.fileEventSource = null;
        this.openTabs = new Map();
        this.activeTab = null;
        this.fileTree = [];
        this.theme = 'dark';
        this.isCustomQueryMode = false;
    }
}

// Task Mapping System
const TASK_MAPPING = {
    'task1': {
        name: 'Analyze',
        description: 'Generate Developer Notes',
        file: 'task1.md',
        query: 'Use task1.md from the prompts folder and perform the task',
        icon: '📝',
        color: '#3b82f6'
    },
    'task2': {
        name: 'Plan', 
        description: 'Generate Migration Plan',
        file: 'task2.md',
        query: 'Use task2.md from the prompts folder and perform the task',
        icon: '📋',
        color: '#059669'
    },
    'task3': {
        name: 'Migrate',
        description: 'Generate Ship JSON',
        file: 'task3.md', 
        query: 'Use task3.md from the prompts folder and perform the task',
        icon: '🚀',
        color: '#dc2626'
    },
    'task4': {
        name: 'Fix',
        description: 'Apply Fix Issues',
        file: 'task4.md',
        query: 'Use task4.md from the prompts folder and perform the task',
        icon: '🔧',
        color: '#d97706'
    }
};

const app = new AppState();

// Theme Management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.applyTheme();
        this.updateThemeIcon();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (this.theme === 'system') {
                this.applyTheme();
            }
        });
    }

    applyTheme() {
        const root = document.documentElement;

        if (this.theme === 'dark' ||
            (this.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    }

    setTheme(theme) {
        this.theme = theme;
        localStorage.setItem('theme', theme);
        this.applyTheme();
        this.updateThemeIcon();
    }

    toggleTheme() {
        const themes = ['light', 'dark', 'system'];
        const currentIndex = themes.indexOf(this.theme);
        const nextIndex = (currentIndex + 1) % themes.length;
        this.setTheme(themes[nextIndex]);
    }

    updateThemeIcon() {
        const sunIcon = document.getElementById('sunIcon');
        const moonIcon = document.getElementById('moonIcon');

        if (!sunIcon || !moonIcon) return;

        const isDark = this.theme === 'dark' ||
            (this.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

        if (isDark) {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
    }
}

const themeManager = new ThemeManager();

// Utility Functions
function updateGlobalStatus(text, type = '') {
    console.log('Updating global status:', text, type);
    const status = document.getElementById('globalStatus');

    // Add status dot for visual feedback
    const dot = type ? `<span class="status-dot ${type}"></span>` : '';
    status.innerHTML = dot + text;
    status.className = 'global-status' + (type ? ' ' + type : '');
}

function addLogEntry(content, type = 'message') {
    console.log('Adding log entry:', content, type);
    const container = document.getElementById('logsContainer');

    // Clear empty state if present
    const emptyState = container.querySelector('.empty-logs');
    if (emptyState) {
        emptyState.remove();
    }

    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = content;
    container.appendChild(entry);

    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function clearLogs() {
    const container = document.getElementById('logsContainer');
    container.innerHTML = `
        <div class="empty-logs">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <p>Enter a query and click Process to start</p>
        </div>
    `;
}

// File Explorer Functions
class FileExplorerManager {
    constructor() {
        this.currentPath = '';
        this.pathHistory = [''];
        this.fileTree = null;
    }

    renderBreadcrumbs() {
        const breadcrumbContainer = document.getElementById('breadcrumbTabs');
        const pathParts = this.currentPath ? this.currentPath.split('/').filter(p => p) : [];

        let html = `
            <button class="breadcrumb-tab ${this.currentPath === '' ? 'active' : ''}" data-path="">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>
                Root
            </button>
        `;

        let currentPath = '';
        pathParts.forEach((part) => {
            currentPath += (currentPath ? '/' : '') + part;
            const isActive = currentPath === this.currentPath;
            html += `
                <button class="breadcrumb-tab ${isActive ? 'active' : ''}" data-path="${currentPath}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                    </svg>
                    ${part}
                </button>
            `;
        });

        breadcrumbContainer.innerHTML = html;

        // Add click handlers
        breadcrumbContainer.querySelectorAll('.breadcrumb-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.navigateToPath(tab.dataset.path);
            });
        });
    }

    getCurrentFolderContents() {
        if (!this.fileTree) return [];

        if (this.currentPath === '') {
            return this.fileTree;
        }

        const pathParts = this.currentPath.split('/').filter(p => p);
        let current = this.fileTree;

        for (const part of pathParts) {
            const folder = current.find(item => item.type === 'folder' && item.name === part);
            if (!folder || !folder.children) {
                return [];
            }
            current = folder.children;
        }

        return current;
    }

    renderCurrentFolder() {
        const container = document.getElementById('currentFolderView');
        const contents = this.getCurrentFolderContents();

        if (!contents || contents.length === 0) {
            container.innerHTML = `
                <div class="empty-folder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                    </svg>
                    <p>This folder is empty</p>
                </div>
            `;
            return;
        }

        let html = '';
        contents.forEach(item => {
            const isFolder = item.type === 'folder';
            const iconSvg = isFolder ?
                `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>` :
                `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>`;

            const itemClass = isFolder ? 'folder-item' : 'file-item';
            const extension = isFolder ? '' : item.name.split('.').pop();

            // Add delete button for output folder items
            const deleteButton = currentExplorerTab === 'output' ? `
                <button class="delete-btn" onclick="deleteItem('${item.path}', '${item.type}')" title="Delete ${item.type}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </button>
            ` : '';

            html += `
                <div class="${itemClass}" data-path="${item.path}" data-extension="${extension}" data-type="${item.type}">
                    <div class="icon">${iconSvg}</div>
                    <div class="name">${item.name}</div>
                    ${deleteButton}
                </div>
            `;
        });

        container.innerHTML = html;

        // Add click handlers
        container.querySelectorAll('.folder-item').forEach(folder => {
            folder.addEventListener('click', (e) => {
                // Don't navigate if clicking on delete button
                if (e.target.closest('.delete-btn')) return;
                this.navigateToPath(folder.dataset.path);
            });
        });

        container.querySelectorAll('.file-item').forEach(file => {
            file.addEventListener('click', (e) => {
                // Don't select if clicking on delete button
                if (e.target.closest('.delete-btn')) return;
                this.selectFile(file.dataset.path);
            });
        });
    }

    navigateToPath(path) {
        this.currentPath = path;
        this.renderBreadcrumbs();
        this.renderCurrentFolder();
        this.updateGoUpButton();
    }

    selectFile(filePath) {
        // Remove previous selection
        document.querySelectorAll('.file-item.selected').forEach(item => {
            item.classList.remove('selected');
        });

        // Add selection to current file
        const fileElement = document.querySelector(`[data-path="${filePath}"]`);
        if (fileElement) {
            fileElement.classList.add('selected');
        }

        // Open file in tab
        openFile(filePath, filePath.split('/').pop());
    }

    updateGoUpButton() {
        const goUpButton = document.getElementById('goUpFolder');
        goUpButton.disabled = this.currentPath === '';
    }

    goUp() {
        if (this.currentPath === '') return;

        const pathParts = this.currentPath.split('/').filter(p => p);
        pathParts.pop();
        const newPath = pathParts.join('/');
        this.navigateToPath(newPath);
    }

    refresh(fileTree) {
        this.fileTree = fileTree;
        this.renderBreadcrumbs();
        this.renderCurrentFolder();
        this.updateGoUpButton();
    }
}

const fileExplorerManager = new FileExplorerManager();

function renderFileTree(files) {
    // Legacy function for compatibility - now uses file explorer
    fileExplorerManager.refresh(files);
}

// Old FileTreeManager code - to be removed
class OldFileTreeManager {
    constructor() {
        this.expandedFolders = new Set();
    }

    renderFileTree(files, container, level = 0) {
        if (level === 0) {
            container.innerHTML = '';
        }

        if (!files || files.length === 0) {
            if (level === 0) {
                container.innerHTML = `
                    <div class="empty-tree">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                        </svg>
                        <p>No files generated yet</p>
                    </div>
                `;
            }
            return;
        }

        files.forEach(file => {
            const itemContainer = document.createElement('div');
            const item = document.createElement('div');
            item.className = `file-tree-item ${file.type}-item`;
            item.style.paddingLeft = `${level * 16 + 8}px`;
            item.tabIndex = 0;
            item.setAttribute('role', file.type === 'folder' ? 'button' : 'treeitem');
            item.setAttribute('aria-label', `${file.type}: ${file.name}`);

            let expandIcon = '';
            if (file.type === 'folder' && file.children && file.children.length > 0) {
                const isExpanded = this.expandedFolders.has(file.path);
                expandIcon = `
                    <div class="expand-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 18l6-6-6-6"/>
                        </svg>
                    </div>
                `;
                item.classList.toggle('expanded', isExpanded);
                item.setAttribute('aria-expanded', isExpanded.toString());
            }

            const icon = file.type === 'folder' ?
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>' :
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>';

            item.innerHTML = `
                ${expandIcon}
                <div class="icon">${icon}</div>
                <div class="name">${file.name}</div>
            `;

            // Add event listeners
            if (file.type === 'file') {
                const clickHandler = () => this.selectFile(item, file);
                item.addEventListener('click', clickHandler);
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        clickHandler();
                    }
                });
            } else if (file.type === 'folder') {
                const toggleHandler = () => this.toggleFolder(item, file);
                item.addEventListener('click', toggleHandler);
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleHandler();
                    }
                });
            }

            itemContainer.appendChild(item);

            // Add children container for folders
            if (file.type === 'folder' && file.children) {
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'file-tree-children';
                const isExpanded = this.expandedFolders.has(file.path);
                childrenContainer.classList.toggle('expanded', isExpanded);
                childrenContainer.classList.toggle('collapsed', !isExpanded);

                if (isExpanded) {
                    this.renderFileTree(file.children, childrenContainer, level + 1);
                }

                itemContainer.appendChild(childrenContainer);
            }

            container.appendChild(itemContainer);
        });
    }

    selectFile(item, file) {
        // Remove previous selection
        document.querySelectorAll('.file-tree-item.selected').forEach(el => {
            el.classList.remove('selected');
        });
        // Add selection to current item
        item.classList.add('selected');
        openFile(file.path, file.name);
    }

    toggleFolder(item, folder) {
        const isExpanded = this.expandedFolders.has(folder.path);
        const childrenContainer = item.parentElement.querySelector('.file-tree-children');

        if (isExpanded) {
            this.expandedFolders.delete(folder.path);
            item.classList.remove('expanded');
            item.setAttribute('aria-expanded', 'false');
            if (childrenContainer) {
                childrenContainer.classList.remove('expanded');
                childrenContainer.classList.add('collapsed');
            }
        } else {
            this.expandedFolders.add(folder.path);
            item.classList.add('expanded');
            item.setAttribute('aria-expanded', 'true');
            if (childrenContainer) {
                childrenContainer.classList.remove('collapsed');
                childrenContainer.classList.add('expanded');
                // Render children if not already rendered
                if (childrenContainer.children.length === 0) {
                    this.renderFileTree(folder.children, childrenContainer,
                        (item.style.paddingLeft.replace('px', '') / 16) + 1);
                }
            }
        }
    }
}

// File explorer is now handled by fileExplorerManager

// Loading State Management
class LoadingManager {
    static showFileTreeSkeleton() {
        const container = document.getElementById('currentFolderView');
        container.innerHTML = `
            <div class="file-tree-skeleton">
                ${Array.from({ length: 5 }, (_, i) => `
                    <div class="file-tree-skeleton-item">
                        <div class="skeleton skeleton-avatar file-tree-skeleton-icon"></div>
                        <div class="skeleton skeleton-text file-tree-skeleton-name ${i % 3 === 0 ? 'short' : i % 3 === 1 ? 'medium' : 'long'}"></div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    static showTabContentSkeleton(pane) {
        pane.innerHTML = `
            <div class="tab-content-skeleton">
                <div class="tab-content-skeleton-header">
                    <div class="skeleton skeleton-text tab-content-skeleton-title"></div>
                    <div class="skeleton skeleton-button tab-content-skeleton-badge"></div>
                </div>
                ${Array.from({ length: 15 }, (_, i) => `
                    <div class="skeleton skeleton-text tab-content-skeleton-line ${i % 4 === 0 ? 'short' : i % 4 === 1 ? 'medium' : 'long'}"></div>
                `).join('')}
            </div>
        `;
    }

    static showLoadingOverlay(container, message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay with-message';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-message">${message}</div>
        `;
        container.appendChild(overlay);
        return overlay;
    }

    static removeLoadingOverlay(container) {
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

function refreshFileTree() {
    const container = document.getElementById('currentFolderView');

    // Show skeleton loading
    LoadingManager.showFileTreeSkeleton();

    // Get files for the current explorer tab
    const url = `/api/files?type=${currentExplorerTab}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            app.fileTree = data.files;
            app.currentFolderType = data.folder_type;
            app.currentFolderPath = data.folder_path;

            // Small delay to show the skeleton effect
            setTimeout(() => {
                fileExplorerManager.refresh(data.files);
                
                // Update info bar if input tab is active
                if (currentExplorerTab === 'input') {
                    updateInputFolderInfo();
                }
            }, 300);
        })
        .catch(error => {
            console.error('Error fetching file tree:', error);
            container.innerHTML = `
                <div class="empty-folder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                    </svg>
                    <p>Error loading files: ${error.message}</p>
                    <button class="btn btn-primary btn-sm" onclick="refreshFileTree()" style="margin-top: 12px;">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                        </svg>
                        Retry
                    </button>
                </div>
            `;
        });
}

// Modern Tab Management System
class TabManager {
    constructor() {
        this.tabs = new Map();
        this.activeTabId = null;
        this.tabOrder = [];
    }

    createTab(filePath, fileName) {
        const tabId = `tab-${Date.now()}`;
        const tab = document.createElement('button');
        tab.className = 'tab';
        tab.dataset.tabId = tabId;
        tab.dataset.filePath = filePath;
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', 'false');
        tab.setAttribute('aria-controls', `panel-${tabId}`);
        tab.setAttribute('id', `tab-${tabId}`);
        tab.tabIndex = -1; // Will be managed by roving tabindex

        tab.innerHTML = `
            <span>${fileName}</span>
            <button class="close-btn" aria-label="Close ${fileName}" tabindex="-1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        `;

        // Add event listeners
        tab.addEventListener('click', (e) => {
            if (!e.target.closest('.close-btn')) {
                this.activateTab(tabId);
            }
        });

        tab.addEventListener('keydown', (e) => this.handleTabKeydown(e, tabId));

        const closeBtn = tab.querySelector('.close-btn');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeTab(tabId);
        });

        // Store tab info
        this.tabs.set(tabId, { filePath, fileName, element: tab });
        this.tabOrder.push(tabId);

        return { tab, tabId };
    }

    handleTabKeydown(e, tabId) {
        const currentIndex = this.tabOrder.indexOf(tabId);
        let targetIndex;

        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                targetIndex = currentIndex > 0 ? currentIndex - 1 : this.tabOrder.length - 1;
                this.focusTab(this.tabOrder[targetIndex]);
                break;
            case 'ArrowRight':
                e.preventDefault();
                targetIndex = currentIndex < this.tabOrder.length - 1 ? currentIndex + 1 : 0;
                this.focusTab(this.tabOrder[targetIndex]);
                break;
            case 'Home':
                e.preventDefault();
                this.focusTab(this.tabOrder[0]);
                break;
            case 'End':
                e.preventDefault();
                this.focusTab(this.tabOrder[this.tabOrder.length - 1]);
                break;
            case 'Enter':
            case ' ':
                e.preventDefault();
                this.activateTab(tabId);
                break;
            case 'Delete':
            case 'Backspace':
                e.preventDefault();
                this.closeTab(tabId);
                break;
        }
    }

    focusTab(tabId) {
        // Update roving tabindex
        this.tabOrder.forEach(id => {
            const tab = this.tabs.get(id)?.element;
            if (tab) {
                tab.tabIndex = id === tabId ? 0 : -1;
            }
        });

        const tab = this.tabs.get(tabId)?.element;
        if (tab) {
            tab.focus();
        }
    }

    activateTab(tabId) {
        // Update tab appearance and ARIA attributes
        this.tabOrder.forEach(id => {
            const tab = this.tabs.get(id)?.element;
            if (tab) {
                const isActive = id === tabId;
                tab.classList.toggle('active', isActive);
                tab.setAttribute('aria-selected', isActive.toString());
                tab.tabIndex = isActive ? 0 : -1;
            }
        });

        // Update content panels
        document.querySelectorAll('.tab-pane').forEach(pane => {
            const isActive = pane.dataset.tabId === tabId;
            pane.classList.toggle('active', isActive);
            pane.setAttribute('aria-hidden', (!isActive).toString());
        });

        this.activeTabId = tabId;

        // Ensure the active tab is focusable
        const activeTab = this.tabs.get(tabId)?.element;
        if (activeTab) {
            activeTab.tabIndex = 0;
        }
    }

    closeTab(tabId) {
        const tab = this.tabs.get(tabId)?.element;
        const pane = document.querySelector(`.tab-pane[data-tab-id="${tabId}"]`);

        if (tab) tab.remove();
        if (pane) pane.remove();

        this.tabs.delete(tabId);
        const orderIndex = this.tabOrder.indexOf(tabId);
        if (orderIndex > -1) {
            this.tabOrder.splice(orderIndex, 1);
        }

        // If this was the active tab, activate another one
        if (this.activeTabId === tabId) {
            if (this.tabOrder.length > 0) {
                // Activate the next tab, or the previous one if we closed the last tab
                const nextIndex = orderIndex < this.tabOrder.length ? orderIndex : orderIndex - 1;
                const nextTabId = this.tabOrder[Math.max(0, nextIndex)];
                this.activateTab(nextTabId);
            } else {
                this.activeTabId = null;
                this.showEmptyViewer();
                // Hide file viewer when no tabs are open
                hideFileViewer();
            }
        }
    }

    closeAllTabs() {
        this.tabOrder.forEach(tabId => {
            const tab = this.tabs.get(tabId)?.element;
            const pane = document.querySelector(`.tab-pane[data-tab-id="${tabId}"]`);
            if (tab) tab.remove();
            if (pane) pane.remove();
        });

        this.tabs.clear();
        this.tabOrder = [];
        this.activeTabId = null;
        this.showEmptyViewer();
        // Hide file viewer when all tabs are closed
        hideFileViewer();
    }

    showEmptyViewer() {
        const content = document.getElementById('tabsContent');
        content.innerHTML = `
            <div class="empty-viewer">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p>Select a file from the tree to view its content</p>
            </div>
        `;
    }
}

const tabManager = new TabManager();

// Legacy functions for compatibility
function createTab(filePath, fileName) {
    return tabManager.createTab(filePath, fileName);
}

function activateTab(tabId) {
    tabManager.activateTab(tabId);
}

function closeTab(tabId, event) {
    if (event) {
        event.stopPropagation();
    }
    tabManager.closeTab(tabId);
}

function closeAllTabs() {
    tabManager.closeAllTabs();
}

function showEmptyViewer() {
    tabManager.showEmptyViewer();
}

// File Operations
function openFile(filePath, fileName) {
    // Show the file viewer panel
    showFileViewer();

    // Check if tab already exists
    const existingTab = document.querySelector(`[data-file-path="${filePath}"]`);
    if (existingTab) {
        activateTab(existingTab.dataset.tabId);
        return;
    }

    // Create new tab
    const { tab, tabId } = createTab(filePath, fileName);

    // Add tab to header with animation
    const tabsHeader = document.getElementById('tabsHeader');
    tab.style.opacity = '0';
    tab.style.transform = 'translateY(-10px)';
    tabsHeader.appendChild(tab);

    // Animate tab in
    requestAnimationFrame(() => {
        tab.style.transition = 'all 0.3s ease';
        tab.style.opacity = '1';
        tab.style.transform = 'translateY(0)';
    });

    // Create content pane with loading state
    const pane = document.createElement('div');
    pane.className = 'tab-pane';
    pane.dataset.tabId = tabId;
    pane.setAttribute('role', 'tabpanel');
    pane.setAttribute('aria-labelledby', `tab-${tabId}`);
    pane.setAttribute('id', `panel-${tabId}`);
    pane.setAttribute('aria-hidden', 'true');
    // Show skeleton loading
    LoadingManager.showTabContentSkeleton(pane);

    document.getElementById('tabsContent').appendChild(pane);

    // Store tab info
    app.openTabs.set(tabId, { filePath, fileName });

    // Activate the new tab
    activateTab(tabId);

    // Load file content with better error handling
    const url = `/api/files/${filePath}?type=${currentExplorerTab}`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Determine file type for better syntax highlighting
            const fileExtension = fileName.split('.').pop().toLowerCase();
            const languageMap = {
                'js': 'javascript',
                'ts': 'typescript',
                'py': 'python',
                'java': 'java',
                'xml': 'xml',
                'json': 'json',
                'html': 'html',
                'css': 'css',
                'md': 'markdown',
                'yml': 'yaml',
                'yaml': 'yaml'
            };
            const language = languageMap[fileExtension] || 'text';

            pane.innerHTML = `
                <div class="file-content">
                    <pre><code class="language-${language}">${escapeHtml(data.content)}</code></pre>
                </div>
            `;

            // Apply syntax highlighting
            if (window.Prism) {
                Prism.highlightAllUnder(pane);
            }
        })
        .catch(error => {
            console.error('Error loading file:', error);
            pane.innerHTML = `
                <div class="empty-viewer">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                    </svg>
                    <p>Error loading file: ${error.message}</p>
                    <button class="btn btn-primary btn-sm" onclick="openFile('${filePath}', '${fileName}')" style="margin-top: 12px;">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                        </svg>
                        Retry
                    </button>
                </div>
            `;
        });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// File Viewer Panel Management
function showFileViewer() {
    const appMain = document.querySelector('.app-main');
    appMain.classList.add('file-viewer-visible');
}

function hideFileViewer() {
    const appMain = document.querySelector('.app-main');
    appMain.classList.remove('file-viewer-visible');
}

// Explorer Tab Management
let currentExplorerTab = 'input';

function switchExplorerTab(tabType) {
    currentExplorerTab = tabType;

    // Update tab visual state
    document.querySelectorAll('.explorer-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabType + 'Tab').classList.add('active');

    // Show/hide input folder info
    const infoBar = document.getElementById('inputFolderInfo');
    if (tabType === 'input' && infoBar) {
        infoBar.style.display = 'block';
        updateInputFolderInfo();
    } else if (infoBar) {
        infoBar.style.display = 'none';
    }

    // Refresh file tree for the selected tab
    refreshFileTree();
}

// Update input folder info display
function updateInputFolderInfo() {
    const folderPath = document.getElementById('inputFolderPath');
    const fileCount = document.getElementById('inputFileCount');
    
    if (!folderPath || !fileCount) return;
    
    // Get current input folder from backend
    fetch('/api/input')
        .then(response => response.json())
        .then(data => {
            if (data.exists && data.path) {
                // Extract just the folder name from the full path
                const pathParts = data.path.split('/');
                const folderName = pathParts[pathParts.length - 1];
                
                folderPath.textContent = folderName;
                folderPath.title = data.path; // Show full path on hover
                
                // Use the total_files count from the API response
                const count = data.total_files || 0;
                fileCount.textContent = count + (count === 1 ? ' file' : ' files');
            } else {
                folderPath.textContent = 'No folder selected';
                fileCount.textContent = '0 files';
            }
        })
        .catch(error => {
            console.error('Error fetching input folder info:', error);
        });
}

// Helper function to count files in tree
function countFilesInTree(tree) {
    let count = 0;
    
    function traverse(items) {
        for (const item of items) {
            if (item.type === 'file') {
                count++;
            } else if (item.type === 'folder' && item.children) {
                traverse(item.children);
            }
        }
    }
    
    traverse(tree);
    return count;
}

// Process Management
function startProcess() {
    console.log('startProcess called');
    const query = document.getElementById('query').value.trim();
    console.log('Query:', query);

    if (!query) {
        alert('Please select a task or enter a custom query');
        return;
    }

    // Check if a task is selected
    const selectedTask = document.querySelector('.task-btn.selected');
    if (selectedTask) {
        const taskId = selectedTask.dataset.task;
        const task = TASK_MAPPING[taskId];
        console.log(`Processing ${task.name} task:`, task.description);
        
        // Add log entry showing which task is being processed
        addLogEntry(`Starting ${task.name} task: ${task.description}`, 'init');
    } else if (app.isCustomQueryMode) {
        console.log('Processing custom query:', query);
        addLogEntry(`Starting custom query: ${query}`, 'init');
    }

    const button = document.getElementById('processBtn');
    button.disabled = true;
    button.classList.add('pulse');
    // Remove the highlight effect once processing starts
    button.style.boxShadow = '';
    button.innerHTML = `
        <div class="spinner"></div>
        Processing...
    `;

    // Clear previous output
    clearLogs();
    updateGlobalStatus('Starting...', 'active');

    console.log('Sending request to /process');

    // Start the process
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'started') {
            // Start listening to the event stream
            console.log('Starting EventSource');
            app.eventSource = new EventSource('/stream');

            app.eventSource.onmessage = function(event) {
                console.log('EventSource message:', event.data);
                const data = JSON.parse(event.data);

                if (data.type === 'complete') {
                    app.eventSource.close();
                    button.disabled = false;
                    button.classList.remove('pulse');
                    button.innerHTML = `
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        Process
                    `;
                    updateGlobalStatus('Completed', 'success');
                } else if (data.type === 'keepalive') {
                    // Ignore keepalive messages
                } else {
                    if (data.type === 'init') {
                        updateGlobalStatus('Processing...', 'active');
                    }
                    addLogEntry(data.content, data.type);
                }
            };

            app.eventSource.onerror = function(error) {
                console.error('EventSource error:', error);
                app.eventSource.close();
                button.disabled = false;
                button.classList.remove('pulse');
                button.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Process
                `;
                updateGlobalStatus('Error', 'error');
                addLogEntry('Connection error occurred', 'error');
            };
        } else if (data.error) {
            throw new Error(data.error);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        button.disabled = false;
        button.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            Process
        `;
        updateGlobalStatus('Error', 'error');
        addLogEntry(`Error: ${error.message}`, 'error');
    });
}

// File Monitoring
function startFileMonitoring() {
    if (app.fileEventSource) {
        return;
    }

    app.fileEventSource = new EventSource('/api/files/stream');

    app.fileEventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'file_tree_update') {
            // Only update if it's for the currently selected tab
            if (data.folder_type === currentExplorerTab) {
                app.fileTree = data.data;
                fileExplorerManager.refresh(data.data);
            }
        }
    };

    app.fileEventSource.onerror = function(error) {
        console.error('File monitoring error:', error);
        // Reconnect after a delay
        setTimeout(() => {
            if (app.fileEventSource) {
                app.fileEventSource.close();
                app.fileEventSource = null;
                startFileMonitoring();
            }
        }, 5000);
    };
}

// Panel Resizer functionality
class PanelResizer {
    constructor() {
        this.isResizing = false;
        this.currentResizer = null;
        this.startX = 0;
        this.startLeftWidth = 0;
        this.startCenterWidth = 0;
        this.init();
    }

    init() {
        const resizers = document.querySelectorAll('.panel-resizer');
        resizers.forEach(resizer => {
            resizer.addEventListener('mousedown', this.startResize.bind(this));
        });

        document.addEventListener('mousemove', this.resize.bind(this));
        document.addEventListener('mouseup', this.stopResize.bind(this));

        // Prevent text selection during resize
        document.addEventListener('selectstart', (e) => {
            if (this.isResizing) {
                e.preventDefault();
            }
        });
    }

    startResize(e) {
        this.isResizing = true;
        this.currentResizer = e.target.closest('.panel-resizer');
        this.startX = e.clientX;

        const leftPanel = document.querySelector('.left-panel');
        const centerPanel = document.querySelector('.center-panel');

        this.startLeftWidth = leftPanel.offsetWidth;
        this.startCenterWidth = centerPanel.offsetWidth;

        this.currentResizer.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';

        e.preventDefault();
    }

    resize(e) {
        if (!this.isResizing || !this.currentResizer) return;

        const deltaX = e.clientX - this.startX;
        const resizeType = this.currentResizer.dataset.resize;

        const leftPanel = document.querySelector('.left-panel');
        const centerPanel = document.querySelector('.center-panel');

        if (resizeType === 'left-center') {
            // Resizing between left and center panels
            const newLeftWidth = this.startLeftWidth + deltaX;
            const newCenterWidth = this.startCenterWidth - deltaX;

            // Apply constraints
            const minLeftWidth = parseInt(getComputedStyle(leftPanel).minWidth);
            const maxLeftWidth = parseInt(getComputedStyle(leftPanel).maxWidth);
            const minCenterWidth = parseInt(getComputedStyle(centerPanel).minWidth);
            const maxCenterWidth = parseInt(getComputedStyle(centerPanel).maxWidth);

            if (newLeftWidth >= minLeftWidth && newLeftWidth <= maxLeftWidth &&
                newCenterWidth >= minCenterWidth && newCenterWidth <= maxCenterWidth) {
                leftPanel.style.width = newLeftWidth + 'px';
                centerPanel.style.width = newCenterWidth + 'px';
            }
        } else if (resizeType === 'center-right') {
            // Resizing between center and right panels
            const newCenterWidth = this.startCenterWidth + deltaX;

            // Apply constraints
            const minCenterWidth = parseInt(getComputedStyle(centerPanel).minWidth);
            const maxCenterWidth = parseInt(getComputedStyle(centerPanel).maxWidth);

            if (newCenterWidth >= minCenterWidth && newCenterWidth <= maxCenterWidth) {
                centerPanel.style.width = newCenterWidth + 'px';
                // Right panel automatically adjusts due to flex: 1
            }
        }
    }

    stopResize() {
        if (!this.isResizing) return;

        this.isResizing = false;
        if (this.currentResizer) {
            this.currentResizer.classList.remove('resizing');
        }
        this.currentResizer = null;

        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    }
}

// Management Actions functionality
class ManagementActions {
    constructor() {
        this.init();
    }

    init() {
        // Bind event listeners
        const cleanupBtn = document.getElementById('cleanupBtn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', this.cleanupOutput.bind(this));
        }
    }

    // checkInput method removed - button no longer exists

    async cleanupOutput() {
        const button = document.getElementById('cleanupBtn');

        // Confirm action
        if (!confirm('Are you sure you want to delete all files in the output folder? This action cannot be undone.')) {
            return;
        }

        // Update UI to loading state
        button.disabled = true;

        try {
            const response = await fetch('/api/cleanup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                console.log('Cleanup completed:', data);
                
                // Show success message in logs
                addLog(`Cleanup completed: ${data.items_removed} items removed`, 'success');

                // Always refresh file tree after cleanup to ensure UI is updated
                // Add a small delay to ensure backend has completed cleanup
                setTimeout(() => {
                    refreshFileTree();
                }, 500);
            } else {
                throw new Error(data.message || data.error || 'Cleanup failed');
            }
        } catch (error) {
            console.error('Error during cleanup:', error);
            addLog(`Cleanup error: ${error.message}`, 'error');
        } finally {
            button.disabled = false;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// Task Management Functions
function executeTask4() {
    const task = TASK_MAPPING['task4'];
    if (!task) return;

    // Clear any existing task selection
    document.querySelectorAll('.task-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Select the task4 button
    const task4Button = document.querySelector('[data-task="task4"]');
    if (task4Button) {
        task4Button.classList.add('selected');
    }

    // Set the query value
    const queryInput = document.getElementById('query');
    queryInput.value = task.query;
    queryInput.classList.remove('custom-mode');
    queryInput.readOnly = true;
    queryInput.placeholder = `${task.name}: ${task.description}`;
    
    // Update global status
    updateGlobalStatus(`Starting ${task.name} task...`, 'active');
    
    // Clear custom query mode
    app.isCustomQueryMode = false;
    
    // Auto-execute the task
    setTimeout(() => {
        startProcess();
        // Scroll to processing logs section
        scrollToProcessingLogs();
    }, 500); // Small delay for visual feedback
}

function selectTask(taskId) {
    const task = TASK_MAPPING[taskId];
    if (!task) return;

    // Update button visual state
    document.querySelectorAll('.task-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    document.querySelector(`[data-task="${taskId}"]`).classList.add('selected');

    // Set the query value
    const queryInput = document.getElementById('query');
    queryInput.value = task.query;
    queryInput.classList.remove('custom-mode');
    queryInput.readOnly = true;
    queryInput.placeholder = `${task.name}: ${task.description}`;
    
    // Update global status
    updateGlobalStatus(`Starting ${task.name} task...`, 'active');
    
    // Clear custom query mode
    app.isCustomQueryMode = false;
    
    // Auto-execute the task
    setTimeout(() => {
        startProcess();
        // Scroll to processing logs section
        scrollToProcessingLogs();
    }, 500); // Small delay for visual feedback
}

function scrollToProcessingLogs() {
    const logsSection = document.querySelector('.logs-section');
    if (logsSection) {
        logsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

function enterCustomQueryMode() {
    // Clear task selection
    document.querySelectorAll('.task-btn').forEach(btn => {
        btn.classList.remove('selected');
    });

    // Enable custom query input
    const queryInput = document.getElementById('query');
    queryInput.readOnly = false;
    queryInput.classList.add('custom-mode');
    queryInput.placeholder = 'Enter your custom conversion query...';
    queryInput.value = '';
    queryInput.focus();
    
    // Update global status and highlight Process button for custom queries
    updateGlobalStatus('Custom query mode - Enter query and click Process', 'active');
    
    const processBtn = document.getElementById('processBtn');
    processBtn.classList.add('pulse');
    processBtn.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.5)';
    
    // Set custom query mode
    app.isCustomQueryMode = true;
}

function exitCustomQueryMode() {
    const queryInput = document.getElementById('query');
    if (app.isCustomQueryMode && !queryInput.value.trim()) {
        // If no custom query was entered, reset to readonly state
        queryInput.readOnly = true;
        queryInput.classList.remove('custom-mode');
        queryInput.placeholder = 'Double-click to enter custom query...';
        queryInput.value = '';
        updateGlobalStatus('Ready', '');
        app.isCustomQueryMode = false;
    }
}

// Event Listeners and Initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app');

    // Initialize panel resizer
    new PanelResizer();

    // Initialize management actions
    new ManagementActions();

    // Task selection event listeners
    document.querySelectorAll('.task-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.dataset.task;
            selectTask(taskId);
        });
    });

    // Query input event listeners
    const queryInput = document.getElementById('query');
    
    // Double-click to enter custom query mode
    queryInput.addEventListener('dblclick', function() {
        if (!app.isCustomQueryMode) {
            enterCustomQueryMode();
        }
    });

    // Blur to exit custom query mode if empty
    queryInput.addEventListener('blur', function() {
        setTimeout(exitCustomQueryMode, 150); // Small delay to handle focus changes
    });

    // Enter key to process
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !document.getElementById('processBtn').disabled) {
            if (this.value.trim()) {
                startProcess();
            }
        }
    });

    // Escape key to exit custom query mode
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && app.isCustomQueryMode) {
            exitCustomQueryMode();
        }
    });

    // Global keyboard shortcuts for task selection
    document.addEventListener('keydown', function(e) {
        // Only handle shortcuts if not in input fields and not in custom query mode
        if (e.target.tagName !== 'INPUT' && !app.isCustomQueryMode) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    selectTask('task1');
                    break;
                case '2':
                    e.preventDefault();
                    selectTask('task2');
                    break;
                case '3':
                    e.preventDefault();
                    selectTask('task3');
                    break;
                case ' ':
                    e.preventDefault();
                    if (queryInput.value.trim() && !document.getElementById('processBtn').disabled) {
                        startProcess();
                    }
                    break;
            }
        }
    });

    // Refresh files button
    document.getElementById('refreshFiles').addEventListener('click', refreshFileTree);

    // Go up folder button
    document.getElementById('goUpFolder').addEventListener('click', () => {
        fileExplorerManager.goUp();
    });

    // Clear logs button
    document.getElementById('clearLogs').addEventListener('click', clearLogs);

    // Close all tabs button
    document.getElementById('closeAllTabs').addEventListener('click', closeAllTabs);

    // Theme toggle button
    document.getElementById('themeToggle').addEventListener('click', () => {
        themeManager.toggleTheme();
    });

    // Explorer tab buttons
    const inputTab = document.getElementById('inputTab');
    const outputTab = document.getElementById('outputTab');
    
    if (inputTab) {
        inputTab.addEventListener('click', () => {
            switchExplorerTab('input');
        });
    }

    if (outputTab) {
        outputTab.addEventListener('click', () => {
            switchExplorerTab('output');
        });
    }

    // Initialize file tree
    refreshFileTree();
    
    // Show input folder info if input tab is active (default)
    if (currentExplorerTab === 'input') {
        const infoBar = document.getElementById('inputFolderInfo');
        if (infoBar) {
            infoBar.style.display = 'block';
            updateInputFolderInfo();
        }
    }

    // Start file monitoring
    startFileMonitoring();

    // Initialize empty viewer
    showEmptyViewer();

    // Hide file viewer initially
    hideFileViewer();
});

// Folder Browser Functionality
let currentBrowserPath = null;
let selectedFolderPath = null;

function openFolderBrowser() {
    const modal = document.getElementById('folderBrowserModal');
    modal.style.display = 'flex';

    // Start browsing from current working directory
    browseFolders();
}

function closeFolderBrowser() {
    const modal = document.getElementById('folderBrowserModal');
    modal.style.display = 'none';
    currentBrowserPath = null;
    selectedFolderPath = null;
}

function browseFolders(path = null) {
    const folderList = document.getElementById('folderList');
    const currentPathElement = document.getElementById('currentPath');

    // Show loading state
    folderList.innerHTML = `
        <div class="loading-folders">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <p>Loading folders...</p>
        </div>
    `;

    const url = path ? `/api/browse?path=${encodeURIComponent(path)}` : '/api/browse';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentBrowserPath = data.path;
                currentPathElement.textContent = data.path;
                renderFolderList(data.items);
            } else {
                folderList.innerHTML = `
                    <div class="loading-folders">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.232 15.5c-.77.833.192 2.5 1.732 2.5z"/>
                        </svg>
                        <p>Error: ${data.message}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error browsing folders:', error);
            folderList.innerHTML = `
                <div class="loading-folders">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.232 15.5c-.77.833.192 2.5 1.732 2.5z"/>
                    </svg>
                    <p>Error loading folders</p>
                </div>
            `;
        });
}

function renderFolderList(items) {
    const folderList = document.getElementById('folderList');

    if (!items || items.length === 0) {
        folderList.innerHTML = `
            <div class="loading-folders">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>
                <p>No folders found</p>
            </div>
        `;
        return;
    }

    let html = '';
    items.forEach(item => {
        const icon = item.type === 'parent' ?
            `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>` :
            `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>`;

        html += `
            <div class="folder-item-browser" data-path="${item.path}" data-type="${item.type}">
                <div class="icon">${icon}</div>
                <div class="name">${item.display_name}</div>
            </div>
        `;
    });

    folderList.innerHTML = html;

    // Add click handlers
    folderList.querySelectorAll('.folder-item-browser').forEach(item => {
        item.addEventListener('click', () => {
            const path = item.dataset.path;
            const type = item.dataset.type;

            if (type === 'parent' || type === 'folder') {
                // Navigate to folder
                browseFolders(path);
            }
        });

        // Add double-click handler for immediate folder selection and copy
        item.addEventListener('dblclick', () => {
            const path = item.dataset.path;
            const type = item.dataset.type;

            if (type === 'folder') {
                // Double-click immediately selects and copies the folder
                selectedFolderPath = path;
                document.getElementById('selectedFolder').textContent = path;
                selectFolderForInput(path);
            }
        });

        // Add single click selection for folders
        item.addEventListener('click', () => {
            const type = item.dataset.type;
            if (type === 'folder') {
                // Remove previous selection
                folderList.querySelectorAll('.folder-item-browser.selected').forEach(el => {
                    el.classList.remove('selected');
                });

                // Select current folder
                item.classList.add('selected');
                selectedFolderPath = item.dataset.path;

                // Update selected folder display
                const selectedFolderElement = document.getElementById('selectedFolder');
                selectedFolderElement.textContent = selectedFolderPath;

                // Enable confirm button
                const confirmBtn = document.getElementById('confirmFolderBtn');
                confirmBtn.disabled = false;
            }
        });
    });
}

function confirmFolderSelection() {
    if (selectedFolderPath) {
        selectFolderForInput(selectedFolderPath);
    }
}

// updateInputStatus function removed - status indicators no longer exist

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function selectFolderForInput(folderPath) {
    // Show progress in modal and disable confirm button
    const confirmBtn = document.getElementById('confirmFolderBtn');
    const selectedFolderElement = document.getElementById('selectedFolder');
    
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = `
        <div class="spinner"></div>
        Copying...
    `;
    selectedFolderElement.textContent = 'Copying files...';
    
    // Add log entry about starting the copy process
    addLogEntry(`Starting folder copy from: ${folderPath}`, 'init');
    updateGlobalStatus('Copying folder contents...', 'active');

    fetch('/api/input/select', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ path: folderPath })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the query input to reflect the new path (use service's input folder)
            const queryInput = document.getElementById('query');
            const currentQuery = queryInput.value;
            const newQuery = currentQuery.replace(/in\s+[^\s]+/, `in ./input`);
            queryInput.value = newQuery;

            // Update input folder info in the left panel
            if (currentExplorerTab === 'input') {
                updateInputFolderInfo();
            }

            // Refresh file tree to show files from new input folder
            // Add a small delay to ensure backend has updated
            setTimeout(() => {
                refreshFileTree();
            }, 500);

            // Close the modal
            closeFolderBrowser();

            // Show detailed success message
            const message = `Input folder updated! Copied ${data.files_copied} files (${formatFileSize(data.total_size)}) from ${data.source_path}`;
            addLogEntry(message, 'success');
            updateGlobalStatus('Input folder updated', 'success');
        } else {
            addLogEntry(`Error setting input folder: ${data.message}`, 'error');
            updateGlobalStatus('Error copying folder', 'error');
            
            // Reset modal state
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = 'Select Folder';
            selectedFolderElement.textContent = folderPath;
        }
    })
    .catch(error => {
        console.error('Error selecting input folder:', error);
        addLogEntry('Error selecting input folder', 'error');
        updateGlobalStatus('Error', 'error');
        
        // Reset modal state
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = 'Select Folder';
        selectedFolderElement.textContent = folderPath;
    });
}

// Rules, Issues, and Core Prompt Functions
async function viewRules() {
    const modal = document.getElementById('rulesModal');
    const content = document.getElementById('rulesContent');
    
    modal.style.display = 'flex';
    content.innerHTML = '<div class="loading-content"><div class="spinner"></div><p>Loading rules...</p></div>';
    
    try {
        const response = await fetch('/api/rules');
        const data = await response.json();
        
        if (data.success) {
            content.innerHTML = formatRules(data.content);
        } else {
            content.innerHTML = `<div class="error-message">Failed to load rules: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Error loading rules:', error);
        content.innerHTML = '<div class="error-message">Error loading rules</div>';
    }
}

async function viewIssues() {
    const modal = document.getElementById('issuesModal');
    const content = document.getElementById('issuesContent');
    
    modal.style.display = 'flex';
    content.innerHTML = '<div class="loading-content"><div class="spinner"></div><p>Loading issues...</p></div>';
    
    try {
        const response = await fetch('/api/issues');
        const data = await response.json();
        
        if (data.success) {
            content.innerHTML = formatIssues(data.content);
        } else {
            content.innerHTML = `<div class="error-message">Failed to load issues: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Error loading issues:', error);
        content.innerHTML = '<div class="error-message">Error loading issues</div>';
    }
}

async function viewCorePrompt() {
    const modal = document.getElementById('corePromptModal');
    const editor = document.getElementById('corePromptEditor');
    const status = document.getElementById('editorStatus');
    
    modal.style.display = 'flex';
    editor.value = 'Loading core prompt...';
    editor.disabled = true;
    status.textContent = 'Loading...';
    
    try {
        const response = await fetch('/api/core-prompt');
        const data = await response.json();
        
        if (data.success) {
            editor.value = data.content;
            editor.disabled = false;
            status.textContent = 'Ready';
        } else {
            editor.value = `Failed to load core prompt: ${data.error}`;
            status.textContent = 'Error';
        }
    } catch (error) {
        console.error('Error loading core prompt:', error);
        editor.value = 'Error loading core prompt';
        status.textContent = 'Error';
    }
}

async function saveCorePrompt() {
    const editor = document.getElementById('corePromptEditor');
    const status = document.getElementById('editorStatus');
    const saveBtn = document.getElementById('saveCorePromptBtn');
    const backupInfo = document.getElementById('lastBackup');
    
    if (!confirm('Are you sure you want to save changes to ship.md? A backup will be created.')) {
        return;
    }
    
    saveBtn.disabled = true;
    status.textContent = 'Saving...';
    
    try {
        const response = await fetch('/api/core-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: editor.value })
        });
        
        const data = await response.json();
        
        if (data.success) {
            status.textContent = 'Saved successfully';
            if (data.backup) {
                backupInfo.textContent = `Backup: ${data.backup}`;
            }
            setTimeout(() => {
                status.textContent = 'Ready';
            }, 3000);
        } else {
            status.textContent = 'Save failed';
            alert(`Failed to save: ${data.error}`);
        }
    } catch (error) {
        console.error('Error saving core prompt:', error);
        status.textContent = 'Save error';
        alert('Error saving core prompt');
    } finally {
        saveBtn.disabled = false;
    }
}

function formatRules(content) {
    const sections = content.split('\n\n');
    let html = '<div class="rules-container">';
    let currentSection = null;
    
    sections.forEach(section => {
        const lines = section.trim().split('\n');
        if (!lines[0]) return;
        
        // Check if it's a section header (ends with Rules or similar)
        if (lines[0].includes('Rules') || lines[0].includes('Checklist')) {
            if (currentSection) {
                html += '</ul></div>';
            }
            html += `<div class="rule-section">`;
            html += `<h3 class="rule-section-title">${lines[0].replace(/-/g, '').trim()}</h3>`;
            html += '<ul class="rule-list">';
            currentSection = lines[0];
        } else {
            // Process rule items
            lines.forEach(line => {
                if (line.startsWith('•')) {
                    const ruleText = line.substring(1).trim();
                    let ruleClass = 'rule-item';
                    
                    // Color code based on keywords
                    if (ruleText.toLowerCase().includes('must') || ruleText.toLowerCase().includes('critical')) {
                        ruleClass += ' rule-critical';
                    } else if (ruleText.toLowerCase().includes('should') || ruleText.toLowerCase().includes('important')) {
                        ruleClass += ' rule-important';
                    } else {
                        ruleClass += ' rule-info';
                    }
                    
                    html += `<li class="${ruleClass}">${escapeHtml(ruleText)}</li>`;
                }
            });
        }
    });
    
    if (currentSection) {
        html += '</ul></div>';
    }
    
    html += '</div>';
    return html;
}

function formatIssues(content) {
    const lines = content.split('\n');
    let html = '<div class="issues-container">';
    let inBlocker = false;
    let inIssue = false;
    let currentIssue = null;
    
    lines.forEach(line => {
        if (line.includes('BLOCKER ISSUES')) {
            html += '<div class="issue-section">';
            html += '<div class="issue-blocker-header">';
            html += '<span class="issue-blocker-badge">BLOCKER</span>';
            html += '<h3>Critical Issues That Must Be Fixed</h3>';
            html += '</div>';
            inBlocker = true;
        } else if (line.includes('ALL ISSUES')) {
            if (inBlocker) {
                html += '</div>';
            }
            html += '<div class="issue-section">';
            html += '<h3 class="rule-section-title">All Migration Issues</h3>';
            inBlocker = false;
        } else if (line.match(/^\d+\./)) {
            // Start of a new issue
            if (currentIssue) {
                html += formatSingleIssue(currentIssue, inBlocker);
            }
            currentIssue = {
                title: line,
                description: '',
                resolution: '',
                inResolution: false
            };
        } else if (currentIssue) {
            if (line.includes('Resolution:') || line.includes('Impact:')) {
                currentIssue.inResolution = true;
            }
            
            if (currentIssue.inResolution) {
                currentIssue.resolution += line + '\n';
            } else {
                currentIssue.description += line + '\n';
            }
        }
    });
    
    if (currentIssue) {
        html += formatSingleIssue(currentIssue, inBlocker);
    }
    
    html += '</div></div>';
    return html;
}

function formatSingleIssue(issue, isBlocker) {
    let html = `<div class="issue-item ${isBlocker ? 'issue-blocker' : ''}">`;
    html += `<div class="issue-title">${escapeHtml(issue.title)}</div>`;
    
    if (issue.description.trim()) {
        html += `<div class="issue-description">${escapeHtml(issue.description.trim())}</div>`;
    }
    
    if (issue.resolution.trim()) {
        html += '<div class="issue-resolution">';
        html += '<div class="issue-resolution-label">Resolution</div>';
        html += `<div>${escapeHtml(issue.resolution.trim())}</div>`;
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function closeRulesModal() {
    document.getElementById('rulesModal').style.display = 'none';
}

function closeIssuesModal() {
    document.getElementById('issuesModal').style.display = 'none';
}

function closeCorePromptModal() {
    document.getElementById('corePromptModal').style.display = 'none';
}

// Additional Context Functions
async function viewContext() {
    const modal = document.getElementById('contextModal');
    const editor = document.getElementById('contextEditor');
    const status = document.getElementById('contextStatus');
    
    modal.style.display = 'flex';
    editor.value = 'Loading additional context...';
    editor.disabled = true;
    status.textContent = 'Loading...';
    
    try {
        const response = await fetch('/api/context');
        const data = await response.json();
        
        if (data.success) {
            editor.value = data.content || '';
            editor.disabled = false;
            status.textContent = 'Ready';
            
            // Show placeholder if empty
            if (!data.content) {
                editor.placeholder = `Enter additional context rules here...

Example:
- Always use specific naming convention: camelCase for Java, snake_case for Python
- Include detailed logging for all database operations
- Custom error codes must follow pattern: APP-XXXX
- Ignore files with .tmp extension during migration`;
            }
        } else {
            editor.value = `Failed to load context: ${data.error}`;
            status.textContent = 'Error';
        }
    } catch (error) {
        console.error('Error loading context:', error);
        editor.value = 'Error loading additional context';
        status.textContent = 'Error';
    }
}

async function saveContext() {
    const editor = document.getElementById('contextEditor');
    const status = document.getElementById('contextStatus');
    const saveBtn = document.getElementById('saveContextBtn');
    
    saveBtn.disabled = true;
    status.textContent = 'Saving...';
    
    try {
        const response = await fetch('/api/context', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: editor.value })
        });
        
        const data = await response.json();
        
        if (data.success) {
            status.textContent = 'Saved successfully';
            setTimeout(() => {
                status.textContent = 'Ready';
            }, 3000);
        } else {
            status.textContent = 'Save failed';
            alert(`Failed to save: ${data.error}`);
        }
    } catch (error) {
        console.error('Error saving context:', error);
        status.textContent = 'Save error';
        alert('Error saving additional context');
    } finally {
        saveBtn.disabled = false;
    }
}

function closeContextModal() {
    document.getElementById('contextModal').style.display = 'none';
}

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
    }
});

// Delete item function
async function deleteItem(itemPath, itemType) {
    const itemName = itemPath.split('/').pop();
    const confirmMessage = itemType === 'folder' 
        ? `Are you sure you want to delete the folder "${itemName}" and all its contents? This action cannot be undone.`
        : `Are you sure you want to delete the file "${itemName}"? This action cannot be undone.`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                path: itemPath,
                type: itemType
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            addLog(`Deleted ${itemType}: ${itemName}`, 'success');
            
            // Refresh file tree after deletion
            setTimeout(() => {
                refreshFileTree();
            }, 300);
        } else {
            addLog(`Failed to delete ${itemType}: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error(`Error deleting ${itemType}:`, error);
        addLog(`Error deleting ${itemType}: ${error.message}`, 'error');
    }
}

// Global functions
window.startProcess = startProcess;
window.closeTab = closeTab;
window.openFolderBrowser = openFolderBrowser;
window.viewRules = viewRules;
window.viewIssues = viewIssues;
window.viewCorePrompt = viewCorePrompt;
window.saveCorePrompt = saveCorePrompt;
window.closeRulesModal = closeRulesModal;
window.closeIssuesModal = closeIssuesModal;
window.closeCorePromptModal = closeCorePromptModal;
window.viewContext = viewContext;
window.saveContext = saveContext;
window.closeContextModal = closeContextModal;
window.deleteItem = deleteItem;
window.closeFolderBrowser = closeFolderBrowser;
window.confirmFolderSelection = confirmFolderSelection;

// Authentication Status Function
async function checkAuthStatus() {
    const btn = document.getElementById('authStatusBtn');
    const originalIcon = btn.innerHTML;
    
    // Show loading state
    btn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="loading-spin">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
    `;
    
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        // Create status message
        let statusMsg = `Claude Authentication Status\n\n`;
        statusMsg += `✅ Authenticated: ${data.authenticated ? 'Yes' : 'No'}\n`;
        
        if (data.claude_version) {
            statusMsg += `📦 Claude Version: ${data.claude_version}\n`;
        }
        
        statusMsg += `🔐 Auth Method: ${data.auth_method}\n`;
        statusMsg += `🛠️ Manager Active: ${data.manager_active ? 'Yes' : 'No'}\n`;
        
        if (data.last_refresh) {
            const refreshTime = new Date(data.last_refresh).toLocaleString();
            statusMsg += `🔄 Last Refresh: ${refreshTime}\n`;
        }
        
        if (data.refresh_interval) {
            statusMsg += `⏱️ Refresh Interval: ${data.refresh_interval}s\n`;
        }
        
        // Show status based on authentication state
        if (data.authenticated) {
            alert(statusMsg + '\n🟢 System is ready for processing');
        } else {
            alert(statusMsg + '\n🔴 Claude CLI authentication required');
        }
        
    } catch (error) {
        console.error('Error checking auth status:', error);
        alert('❌ Failed to check authentication status\n\nError: ' + error.message);
    } finally {
        // Restore original icon
        btn.innerHTML = originalIcon;
    }
}

window.checkAuthStatus = checkAuthStatus;

// Fix Modal Functions
let fixIssues = [];
let issueCounter = 0;

function openFixModal() {
    const modal = document.getElementById('fixModal');
    modal.style.display = 'flex';
    
    // Reset issues if needed
    if (fixIssues.length === 0) {
        fixIssues = [];
        issueCounter = 0;
        renderIssuesList();
    }
}

function closeFixModal() {
    const modal = document.getElementById('fixModal');
    modal.style.display = 'none';
}

function addNewIssue() {
    issueCounter++;
    const issue = {
        id: `issue-${issueCounter}`,
        number: issueCounter,
        text: ''
    };
    
    fixIssues.push(issue);
    renderIssuesList();
    
    // Focus on the new issue textarea
    setTimeout(() => {
        const textarea = document.querySelector(`#${issue.id} textarea`);
        if (textarea) {
            textarea.focus();
        }
    }, 100);
}

function removeIssue(issueId) {
    fixIssues = fixIssues.filter(issue => issue.id !== issueId);
    renderIssuesList();
}

function updateIssueText(issueId, text) {
    const issue = fixIssues.find(issue => issue.id === issueId);
    if (issue) {
        issue.text = text;
    }
}

function renderIssuesList() {
    const container = document.getElementById('issuesList');
    container.innerHTML = '';
    
    fixIssues.forEach(issue => {
        const issueElement = document.createElement('div');
        issueElement.className = 'issue-item';
        issueElement.id = issue.id;
        
        issueElement.innerHTML = `
            <div class="issue-header">
                <span class="issue-number">Issue #${issue.number}</span>
                <button class="remove-issue-btn" onclick="removeIssue('${issue.id}')" title="Remove issue">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </button>
            </div>
            <textarea 
                class="issue-textarea" 
                placeholder="Describe the issue that needs to be fixed..."
                onchange="updateIssueText('${issue.id}', this.value)"
                onkeyup="updateIssueText('${issue.id}', this.value)"
            >${issue.text}</textarea>
        `;
        
        container.appendChild(issueElement);
    });
}

async function saveFixIssues() {
    // Filter out empty issues
    const validIssues = fixIssues.filter(issue => issue.text.trim() !== '');
    
    if (validIssues.length === 0) {
        alert('Please add at least one issue before saving.');
        return;
    }
    
    // Show loading state
    const saveBtn = document.querySelector('#fixModal .modal-header-actions .btn-primary');
    const originalContent = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = `
        <div class="spinner"></div>
        Saving...
    `;
    
    try {
        const response = await fetch('/api/fix', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                issues: validIssues.map(issue => issue.text)
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            addLogEntry(`Fix issues saved to ${data.file_path}`, 'success');
            updateGlobalStatus('Fix issues saved, starting task 4...', 'success');
            closeFixModal();
            
            // Reset issues for next time
            fixIssues = [];
            issueCounter = 0;
            renderIssuesList();
            
            // Set up task4 directly as custom query mode
            const task = TASK_MAPPING['task4'];
            const queryInput = document.getElementById('query');
            queryInput.value = task.query;
            queryInput.classList.add('custom-mode');
            queryInput.readOnly = false;
            queryInput.placeholder = `${task.name}: ${task.description}`;
            app.isCustomQueryMode = true;
            updateGlobalStatus(`Starting ${task.name} task...`, 'active');
            
            setTimeout(() => {
                startProcess();
            }, 500);
        } else {
            alert(`Failed to save issues: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error saving fix issues:', error);
        alert('Error saving fix issues: ' + error.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalContent;
    }
}

// Add keyboard shortcut for Fix button
document.addEventListener('keydown', function(e) {
    // Only handle shortcuts if not in input fields and not in custom query mode
    if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && !app.isCustomQueryMode) {
        if (e.key.toLowerCase() === 'f' && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            openFixModal();
        }
    }
});

// Export functions to window
window.openFixModal = openFixModal;
window.closeFixModal = closeFixModal;
window.addNewIssue = addNewIssue;
window.removeIssue = removeIssue;
window.updateIssueText = updateIssueText;
window.saveFixIssues = saveFixIssues;