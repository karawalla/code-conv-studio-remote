# UI Details - Code Conversion Studio v2

## Overview
This document maps out the UI structure, identifying which files are used for each screen and core button handlers.

## File Structure

### Core Files
- **HTML**: `v2/templates/dashboard.html` - Single page containing all screens
- **JavaScript**: `v2/static/js/dashboard.js` - All UI logic and event handlers
- **CSS**: 
  - `v2/static/css/dashboard.css` - Main dashboard styles
  - `v2/static/css/jobs.css` - Job-specific styles
  - `v2/static/css/agents.css` - Agent-specific styles
  - `v2/static/css/credentials.css` - Settings/credentials styles

## Screens and Their Components

### 1. Home Screen
- **HTML Section**: `<div id="homePage" class="page">`
- **Key Functions**:
  - `loadDashboardData()` - Loads dashboard stats
  - `navigateToPage('home')` - Navigation handler

### 2. Sources Screen
- **HTML Section**: `<div id="sourcesPage" class="page">`
- **Key Functions**:
  - `loadSources()` - Loads source repositories
  - `showAddSourceModal()` - Opens add source modal
  - `addSource()` - Creates new source
  - `deleteSource(sourceId)` - Deletes a source
- **Modal**: `<div id="addSourceModal" class="modal">`

### 3. Targets Screen
- **HTML Section**: `<div id="targetsPage" class="page">`
- **Key Functions**:
  - `loadTargets()` - Loads target platforms
  - `showAddTargetModal()` - Opens add target modal
  - `saveTarget()` - Creates new target
  - `deleteTarget(targetId, targetName)` - Deletes a target
  - `switchAddTargetTab(tabName)` - Switches between config tabs
- **Modal**: `<div id="addTargetModal" class="modal">`

### 4. Jobs Screen
- **HTML Section**: `<div id="jobsPage" class="page">`
- **Sub-sections**:
  - `<div id="jobsTableContainer">` - Jobs list
  - `<div id="inlineCreateJob">` - Inline job creation form (now with job type selection)
  - `<div id="inlineJobDetail">` - Job detail view with stages
- **Key Functions**:
  - `loadJobs()` - Loads jobs list (now shows job type badges)
  - `showNewJobModal()` - Shows inline create form
  - `selectJobType(type)` - Handles job type selection (migration/modernization)
  - `saveInlineJob()` - Creates job from inline form (handles both types)
  - `showInlineJobDetail(jobId)` - Shows job detail with stages
  - `editJob(jobId)` - Navigates to edit job (uses create job page)
  - `deleteJob(jobId, jobName)` - Deletes a job
  - `executeJob(jobId)` - Executes a job
  - `refreshJobStatus(jobId)` - Refreshes job status
- **Modernization Functions**:
  - `showModernizationOptions()` - Opens modernization options modal
  - `toggleModernizationOption(option)` - Toggles modernization option selection
  - `confirmModernizationOptions()` - Confirms selected modernization options
- **Modals**:
  - `<div id="modernizationOptionsModal" class="selection-modal">` - Modernization options selector

### 5. Create/Edit Job Screen
- **HTML Section**: `<div id="createJobPage" class="page">`
- **Key Functions**:
  - `loadCreateJobPage()` - Loads page, handles edit mode
  - `saveJob()` - Creates new job
  - `updateJob()` - Updates existing job (when in edit mode)
- **Form Elements**:
  - `#createJobName` - Job name input
  - `#createJobDescription` - Job description textarea
  - `#createSourceSelect` - Source dropdown
  - `#createTargetSelect` - Target dropdown

### 6. Agents Screen
- **HTML Section**: `<div id="agentsPage" class="page">`
- **Key Functions**:
  - `loadAgents()` - Loads agents list
  - `showAddAgentModal()` - Opens add agent modal
  - `createAgent()` - Creates new agent
  - `showEditAgentModal(agentId)` - Opens edit agent modal
  - `updateAgent()` - Updates agent
  - `deleteAgent()` - Deletes agent
- **Modals**:
  - `<div id="addAgentModal" class="modal">`
  - `<div id="editAgentModal" class="modal">`

### 7. Settings Screen
- **HTML Section**: `<div id="settingsPage" class="page">`
- **Tabs**:
  - Credentials: `<div id="credentials-tab">`
  - Connections: `<div id="connections-tab">`
- **Key Functions**:
  - `switchSettingsTab(tabName)` - Switches between tabs
  - `loadCredentials()` - Loads credentials list
  - `showAddCredentialModal()` - Opens add credential modal
  - `saveCredential()` - Creates new credential
  - `deleteCredential(credentialId, credentialName)` - Deletes credential
- **Modal**: `<div id="addCredentialModal" class="modal">`

## Navigation System
- **Function**: `navigateToPage(pageName)`
- **URL Hash**: Updates `window.location.hash`
- **Nav Items**: `<div class="nav-item" data-page="pageName">`

## Modal System
- **Show Modal**: `showModal(modalId)`
- **Close Modal**: `closeModal(modalId)`
- **CSS Class**: `.modal` (hidden by default with `display: none`)
- **Active State**: `.modal.show` class added when visible

## Button Handlers Quick Reference

### Job Operations
```javascript
// Create Job
onclick="showInlineCreateJob()"     // Shows inline form
onclick="saveJob()"                  // Saves new job from create page
onclick="createInlineJob()"          // Creates job from inline form

// Edit Job
onclick="editJob('${job.id}')"      // Opens edit form

// Update Job
onclick="updateJob()"                // Updates existing job

// Delete Job
onclick="deleteJob('${job.id}', '${job.name}')"

// Execute Job
onclick="executeJob('${job.id}')"

// View Job Details
onclick="showInlineJobDetail('${job.id}')"
```

### Source/Target Operations
```javascript
// Sources
onclick="showAddSourceModal()"
onclick="addSource()"
onclick="deleteSource('${source.id}')"

// Targets
onclick="showAddTargetModal()"
onclick="saveTarget()"
onclick="deleteTarget('${target.id}', '${target.name}')"
```

### Agent Operations
```javascript
onclick="showAddAgentModal()"
onclick="createAgent()"
onclick="showEditAgentModal('${agent.id}')"
onclick="updateAgent()"
onclick="deleteAgent()"
```

## Important Notes

1. **Single Page Application**: All screens are in one HTML file, shown/hidden via JavaScript
2. **Modal Management**: Modals should be hidden by default and only shown when explicitly called
3. **Navigation**: Always use `navigateToPage()` for screen transitions
4. **Job Edit Flow**: Edit reuses the create job page with data pre-filled
5. **Inline Forms**: Jobs page has inline creation form that slides down

## Common Issues and Solutions

### Modal Appearing Unexpectedly
- Check modal HTML has proper structure with opening/closing tags
- Ensure `display: none` is set in CSS
- Use `closeModal()` to properly hide modals
- Check for event propagation issues

### Edit Functionality
- Edit job uses the same page as create job (`#createJobPage`)
- Data is passed via `sessionStorage`
- Button text changes from "Create Job" to "Update Job"
- Form submission calls different functions: `saveJob()` vs `updateJob()`

### Adding New Features
1. Add HTML section in `dashboard.html`
2. Add navigation item with `data-page` attribute
3. Create load function in `dashboard.js`
4. Add case in `loadPageData()` function
5. Style in appropriate CSS file

## New Features: Modernization Support

### Job Type Selection
- Jobs now support two types: Migration and Modernization
- Job type selection is required when creating a new job
- Visual job type badges appear in the jobs list

### Modernization Options
When "Modernization" is selected:
- Target selection is replaced with "Modernization Options"
- Multiple options can be selected from categories:
  - Infrastructure & Deployment: CI/CD, Cloud Migration, Containerization, DevOps
  - Architecture & Code: Microservices, API Enablement
  - Operations & Quality: Observability, Security, Data Modernization, Performance

### CSS Classes
- `.job-type-card` - Job type selection cards
- `.job-type-badge` - Type indicators in job list
- `.modernization-option` - Modernization option cards
- `.modernization-category` - Category containers
- `.project-management-toggle` - Project management checkbox container

## Project Management Toggle

### Feature Description
- Jobs can optionally include project management stages (Jira, Sprint Planning, etc.)
- A checkbox in the job creation form controls this option
- When enabled, adds PM-specific stages and tasks to the workflow
- When disabled, creates a streamlined technical-only workflow

### Implementation
- **Frontend**: Checkbox with ID `#projectManagementEnabled` in inline create form
- **Backend**: `project_management_enabled` parameter passed to job creation
- **Stage Generation**: Conditional stages based on the toggle:
  - With PM: Project Setup, Sprint Planning, Sprint Review stages included
  - Without PM: Only core technical stages included
- **Task Differences**: Some tasks are modified based on PM setting
  - With PM: "Update Jira with Findings"
  - Without PM: "Document Findings"