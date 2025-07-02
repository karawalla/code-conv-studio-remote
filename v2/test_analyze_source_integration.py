#!/usr/bin/env python3
"""
Test script to verify the analyze source integration with Claude Code
"""

import os
import json
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
TEST_REPO_URL = "https://github.com/microsoft/TypeScript-React-Starter"

def test_analyze_source_integration():
    """Test the full flow of creating a source, job, and executing analyze task"""
    
    print("=== Testing Analyze Source Integration ===\n")
    
    # Step 1: Create a GitHub source
    print("1. Creating GitHub source...")
    response = requests.post(f"{BASE_URL}/api/sources", json={
        "type": "github",
        "url": TEST_REPO_URL,
        "name": "TypeScript React Starter"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create source: {response.text}")
        return
    
    source = response.json()
    source_id = source['id']
    print(f"✅ Source created: {source_id}")
    print(f"   Path: {source['path']}")
    
    # Step 2: Create a modernization job
    print("\n2. Creating modernization job...")
    response = requests.post(f"{BASE_URL}/api/jobs", json={
        "name": "Test Analyze Source",
        "description": "Testing analyze source integration",
        "job_type": "modernization",
        "source_id": source_id,
        "source_name": source['name'],
        "modernization_options": ["cloud", "cicd"],
        "project_management_enabled": False
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.text}")
        return
    
    job = response.json()
    job_id = job['id']
    print(f"✅ Job created: {job_id}")
    
    # Check job folder structure
    job_path = Path(f"data/jobs/{job_id}")
    if job_path.exists():
        print(f"✅ Job folder created: {job_path}")
        
        # Check for task folders
        for stage in job['stages']:
            stage_id = stage['id']
            for i, task in enumerate(stage.get('tasks', [])):
                task_name = task['name'].lower().replace(' ', '_')
                task_folder = job_path / stage_id / f"{i}_{task_name}"
                if task_folder.exists():
                    input_folder = task_folder / 'input'
                    output_folder = task_folder / 'output'
                    data_folder = task_folder / 'data'
                    
                    if input_folder.exists() and output_folder.exists() and data_folder.exists():
                        print(f"   ✅ Task folder structure: {task_folder}")
                    else:
                        print(f"   ❌ Incomplete task folder: {task_folder}")
    
    # Step 3: Find the analyze task
    print("\n3. Finding analyze source task...")
    analyze_task = None
    analyze_stage_id = None
    analyze_task_index = None
    
    for stage in job['stages']:
        for i, task in enumerate(stage.get('tasks', [])):
            if 'architect' in task.get('agent', '').lower() and 'analyze' in task['name'].lower():
                analyze_task = task
                analyze_stage_id = stage['id']
                analyze_task_index = i
                break
        if analyze_task:
            break
    
    if not analyze_task:
        print("❌ Could not find analyze task")
        return
    
    print(f"✅ Found analyze task: {analyze_task['name']}")
    print(f"   Stage: {analyze_stage_id}")
    print(f"   Index: {analyze_task_index}")
    
    # Step 4: Execute the analyze task
    print("\n4. Executing analyze source task...")
    response = requests.post(
        f"{BASE_URL}/api/jobs/{job_id}/stages/{analyze_stage_id}/tasks/{analyze_task_index}/execute"
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to execute task: {response.text}")
        return
    
    execution_result = response.json()
    execution_id = execution_result['execution_id']
    print(f"✅ Task execution started: {execution_id}")
    print(f"   Status: {execution_result['status']}")
    
    # Step 5: Check task input folder
    print("\n5. Checking task folders...")
    task_name = analyze_task['name'].lower().replace(' ', '_')
    task_folder = Path(f"data/jobs/{job_id}/{analyze_stage_id}/{analyze_task_index}_{task_name}")
    task_input_folder = task_folder / 'input'
    task_output_folder = task_folder / 'output'
    
    if task_input_folder.exists():
        input_contents = list(task_input_folder.iterdir())
        print(f"✅ Task input folder has {len(input_contents)} items")
        for item in input_contents[:5]:  # Show first 5 items
            print(f"   - {item.name}")
        if len(input_contents) > 5:
            print(f"   ... and {len(input_contents) - 5} more")
    else:
        print(f"❌ Task input folder not found: {task_input_folder}")
    
    # Step 6: Check outputs
    if 'output_paths' in execution_result:
        output_dir = Path(execution_result['output_paths']['directory'])
        if output_dir.exists():
            print(f"\n6. Checking outputs...")
            print(f"✅ Output directory: {output_dir}")
            
            for file_path in execution_result['output_paths']['files']:
                file_name = Path(file_path).name
                print(f"   - {file_name}")
                
            # Read combined output
            combined_output = output_dir / 'combined_output.md'
            if combined_output.exists():
                with open(combined_output, 'r') as f:
                    content = f.read()
                print(f"\n📄 Combined output preview (first 500 chars):")
                print("   " + content[:500].replace('\n', '\n   '))
                if len(content) > 500:
                    print("   ...")
    
    print("\n✅ Test completed successfully!")
    
    # Cleanup (optional)
    cleanup = input("\nDo you want to clean up test data? (y/n): ")
    if cleanup.lower() == 'y':
        # Delete job
        requests.delete(f"{BASE_URL}/api/jobs/{job_id}")
        # Delete source
        requests.delete(f"{BASE_URL}/api/sources/{source_id}")
        print("✅ Test data cleaned up")

if __name__ == "__main__":
    test_analyze_source_integration()