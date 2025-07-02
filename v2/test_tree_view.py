#!/usr/bin/env python3
"""
Test script to verify the tree view functionality
"""

import os
import json
import requests
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_tree_view():
    """Test the tree view functionality"""
    
    print("=== Testing Tree View Functionality ===\n")
    
    # Step 1: Get all jobs
    print("1. Getting jobs list...")
    response = requests.get(f"{BASE_URL}/api/jobs")
    
    if response.status_code != 200:
        print(f"❌ Failed to get jobs: {response.text}")
        return
        
    jobs = response.json()
    if not jobs:
        print("❌ No jobs found. Please create a job first.")
        return
        
    # Use the first job
    job = jobs[0]
    job_id = job['id']
    print(f"✅ Using job: {job['name']} ({job_id})")
    
    # Step 2: Find a task with completed status
    print("\n2. Finding completed task...")
    completed_task = None
    stage_id = None
    task_index = None
    
    for stage in job.get('stages', []):
        for i, task in enumerate(stage.get('tasks', [])):
            if task.get('status') == 'completed':
                completed_task = task
                stage_id = stage['id']
                task_index = i
                break
        if completed_task:
            break
    
    if not completed_task:
        print("❌ No completed tasks found. Please execute a task first.")
        return
        
    print(f"✅ Found completed task: {completed_task['name']}")
    print(f"   Stage: {stage_id}, Index: {task_index}")
    
    # Step 3: Get task file structure
    print("\n3. Getting task file structure...")
    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/stages/{stage_id}/tasks/{task_index}/files")
    
    if response.status_code != 200:
        print(f"❌ Failed to get file structure: {response.text}")
        return
        
    file_structure = response.json()
    print(f"✅ Got file structure for task: {file_structure['task_name']}")
    
    # Display folder structure
    print("\n📁 Folder Structure:")
    for folder_name, folder_data in file_structure['folders'].items():
        if folder_data.get('exists') == False:
            print(f"   └─ {folder_name}/ (empty)")
        else:
            print(f"   └─ {folder_name}/")
            display_tree(folder_data, "      ")
    
    # Step 4: Test file content loading
    print("\n4. Testing file content loading...")
    
    # Find a file to load
    test_file = None
    for folder_name, folder_data in file_structure['folders'].items():
        if folder_data.get('children'):
            for child in folder_data['children']:
                if child.get('type') == 'file' and not child['name'].startswith('.'):
                    test_file = child
                    break
            if test_file:
                break
    
    if test_file:
        print(f"   Loading file: {test_file['name']}")
        response = requests.post(
            f"{BASE_URL}/api/jobs/{job_id}/files/content",
            json={'path': test_file['path']}
        )
        
        if response.status_code == 200:
            content_data = response.json()
            print(f"✅ Successfully loaded file: {content_data['name']}")
            print(f"   Size: {content_data['size']} bytes")
            if not content_data.get('binary'):
                preview = content_data['content'][:200]
                if len(content_data['content']) > 200:
                    preview += "..."
                print(f"   Preview: {preview}")
        else:
            print(f"❌ Failed to load file content: {response.text}")
    else:
        print("   No files found to test")
    
    print("\n✅ Tree view test completed!")

def display_tree(node, prefix=""):
    """Display tree structure recursively"""
    if node.get('children'):
        for i, child in enumerate(node['children']):
            is_last = i == len(node['children']) - 1
            connector = "└─" if is_last else "├─"
            
            if child.get('type') == 'folder':
                print(f"{prefix}{connector} {child['name']}/")
                extension = "   " if is_last else "│  "
                display_tree(child, prefix + extension)
            else:
                size = f" ({format_size(child.get('size', 0))})" if child.get('size') else ""
                print(f"{prefix}{connector} {child['name']}{size}")

def format_size(bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

if __name__ == "__main__":
    test_tree_view()