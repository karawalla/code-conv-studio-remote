# Input/Output Icons Implementation

## Overview
Added two clean icons to each task row - one for viewing input files and one for viewing output files. Both icons open the same tree view UI but focus on the respective folder type.

## Changes Made

### 1. **Task Row UI Update**
- Replaced single "View Output" button with two distinct icons:
  - **Input Icon** (Blue) - Shows input folder contents
  - **Output Icon** (Green) - Shows output folder contents
- Icons are always visible, regardless of task execution status
- Icons use glass-morphism styling consistent with the rest of the UI

### 2. **Icon Styling**
```css
/* Input button - Blue theme */
.task-file-btn.input {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.3);
}

/* Output button - Green theme */
.task-file-btn.output {
    background: rgba(34, 197, 94, 0.1);
    border-color: rgba(34, 197, 94, 0.3);
}
```

### 3. **Functionality**
- `viewTaskFiles(stageId, taskIndex, type)` - New function that handles both input and output views
- Modal title shows which type is being viewed (Input/Output) with color coding
- File tree automatically highlights and can auto-expand the selected folder type
- Empty folders show "(empty)" indicator

### 4. **Visual Features**
- Glass-morphism effect with backdrop blur
- Smooth hover animations with subtle lift effect
- Shimmer effect on hover (using CSS pseudo-elements)
- Consistent spacing and alignment with existing UI elements

## User Experience

1. **Before Execution**: 
   - Input folder will be empty (shows "input (empty)")
   - Output folder will be empty (shows "output (empty)")
   - Data folder may be empty or contain configuration

2. **After Execution**:
   - Input folder contains the copied source files
   - Output folder contains execution results
   - Files can be clicked to view contents

## Benefits

1. **Clear Separation**: Users can easily distinguish between input and output files
2. **Always Available**: Icons are visible at all times, providing consistent UI
3. **Visual Consistency**: Maintains the beautiful glass-morphism theme
4. **Intuitive Colors**: Blue for input (data going in), Green for output (results coming out)
5. **Space Efficient**: Compact icons don't clutter the task row

## Technical Implementation

The icons use the same file/folder infrastructure as before but with:
- Enhanced `viewTaskFiles()` function that accepts a type parameter
- Modified `loadTaskFileTree()` to highlight the focused folder
- Updated modal title to show Input/Output with appropriate coloring
- CSS animations for smooth interactions