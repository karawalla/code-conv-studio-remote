# CLAUDE.md - Project Context and Instructions

## 🚨 CRITICAL: THIS PROJECT RUNS IN DOCKER 🚨

**NEVER run anything locally! ALWAYS use Docker containers!**

## Project Overview
This is the Any-to-Any Code Conversion Studio v2 - a web application for converting code between different frameworks and languages.

## Docker Setup
- The application runs in Docker containers
- **ALWAYS use Docker for running, testing, and developing**
- Main command: `docker-compose up`
- The app runs on http://localhost:5000 (mapped to port 8080 on host)

## UI Theme Guidelines - LIQUID GLASS DESIGN

### Color Palette
- **Primary Color**: `#3b82f6` (Blue)
- **Background**: Dark theme with `rgba(255, 255, 255, 0.02)` glass effect
- **Text Colors**:
  - Primary: `var(--text-primary)` - Main text
  - Secondary: `var(--text-secondary)` - Subtle text
  - Tertiary: `var(--text-tertiary)` - Very subtle text
- **Borders**: `rgba(255, 255, 255, 0.1)` with hover state `rgba(255, 255, 255, 0.2)`

### Design Elements
- **Cards**: Liquid glass effect with `backdrop-filter: blur(10px)`
- **Buttons**: 
  - Primary: Blue background `var(--primary)` with hover effects
  - Secondary: Transparent with border
- **Forms**: Glass-morphism inputs with subtle borders
- **NO GRADIENTS** - Keep it clean and consistent
- **Icons**: Use emojis or consistent icon sets - no mixed styles

### Component Structure
- All cards should have:
  ```css
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  ```
- Consistent padding: `1.5rem`
- Consistent border-radius: `12px` for cards, `8px` for inputs, `6px` for small elements

## Clean Code Rules

### JavaScript Structure
1. **Separation of Concerns**:
   - UI rendering functions separate from data fetching
   - Event handlers in dedicated functions
   - API calls in separate functions

2. **Function Organization**:
   - Group related functions together
   - Use descriptive function names (e.g., `loadCredentials`, `renderCredentialCard`)
   - Keep functions focused on a single task

3. **Component-like Structure** (even in vanilla JS):
   ```javascript
   // Good: Component-like function
   function renderCredentialCard(credential) {
       return `<div class="credential-card">...</div>`;
   }
   
   // Bad: Inline HTML generation in random places
   ```

4. **Consistent Naming**:
   - camelCase for functions and variables
   - Descriptive names (avoid single letters)
   - Prefix event handlers with 'handle' or 'on'

### CSS Organization
1. **Component-based CSS**:
   - Group styles by component
   - Use consistent class naming (BEM-like)
   - Avoid deeply nested selectors

2. **Reusable Classes**:
   - `.liquid-glass` for glass effect
   - `.card` for card containers
   - `.btn` for buttons

3. **No Inline Styles** in JavaScript unless absolutely necessary

### File Organization
- Separate CSS files for major features (credentials.css, jobs.css, etc.)
- Keep related functionality together
- Comment sections clearly

## Important Project Details
1. **Technology Stack**:
   - Backend: Flask (Python)
   - Frontend: Vanilla JavaScript, HTML, CSS
   - Storage: JSON files in data/ directory
   - Container: Docker

2. **Key Features**:
   - Sources management (GitHub repos, local folders)
   - Targets configuration
   - AI Agents for automation
   - Jobs workflow with 8 stages
   - Credentials and Settings management
   - @ mention system for credentials

3. **Recent Work**:
   - Implemented Settings section with Credentials and Connections tabs
   - Created @ mention system for simplified job creation
   - Removed execute buttons from agents
   - Converted all modals to inline forms
   - Fixed job edit functionality and modal issues

4. **UI Guidelines**:
   - NO gradients or "shiny" colors
   - Use consistent styling with var(--primary)
   - Prefer inline forms over modals/popups
   - Keep the interface clean and professional

5. **Git Branch**: v2-stage-3

## 📋 UI STRUCTURE DOCUMENTATION
**IMPORTANT**: Always refer to `/v2/docs/ui-details.md` for:
- Which files to modify for each screen
- Button handler locations
- Modal management
- Navigation system

**MANDATORY**: After ANY UI changes:
1. Update `/v2/docs/ui-details.md` with new components/functions
2. Follow the existing structure and patterns
3. Document any new button handlers or modals

## Development Commands
```bash
# Start the application (ALWAYS USE THIS)
docker-compose up

# Rebuild if needed
docker-compose build

# Stop containers
docker-compose down
```

## Testing
- NEVER test locally
- Always ensure Docker containers are running
- Access the app at http://localhost:5000

## File Structure
- `/v2/` - Main application directory
- `/v2/services/` - Backend services
- `/v2/static/` - Frontend assets (CSS, JS)
- `/v2/templates/` - HTML templates
- `/v2/data/` - JSON data storage (created at runtime)

## Remember
1. **ALWAYS USE DOCKER** - Never run anything locally
2. Keep UI simple - no gradients or fancy colors
3. Use inline forms, not modals
4. Test everything in Docker environment