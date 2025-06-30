#!/usr/bin/env python3
"""
Script to create a test job automatically via API
"""
import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def create_test_job():
    """Create a test job with Code Architect and Code Engineer stages"""
    
    print("Creating test job...")
    
    # First, get available sources
    print("\nFetching available sources...")
    sources_response = requests.get(f"{BASE_URL}/sources")
    if sources_response.status_code != 200:
        print(f"Failed to fetch sources: {sources_response.text}")
        return
    
    sources = sources_response.json()
    if not sources:
        print("No sources available. Please add a source first.")
        return
    
    # Use the first available source
    source = sources[0]
    print(f"Using source: {source['name']} ({source['type']})")
    
    # Job creation payload
    job_data = {
        "name": f"Test Migration Job - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Automated test job for Code Architect and Code Engineer testing",
        "source_id": source['id'],
        "source_name": source['name'],
        "source_type": source['type'],
        "target_id": "rust",
        "target_name": "Rust",
        "target_type": "rust",
        "stages": [
            {
                "id": "stage_1",
                "name": "Planning & Analysis",
                "order": 1,
                "tasks": [
                    {
                        "name": "Analyze",
                        "agent": "Code Architect",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "depth": "comprehensive",
                            "include_dependencies": True
                        }
                    },
                    {
                        "name": "Plan",
                        "agent": "Code Architect", 
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "migration_strategy": "incremental",
                            "risk_assessment": True
                        }
                    }
                ]
            },
            {
                "id": "stage_2",
                "name": "Development",
                "order": 2,
                "tasks": [
                    {
                        "name": "Migrate",
                        "agent": "Code Engineer",
                        "status": "pending", 
                        "enabled": True,
                        "config": {
                            "preserve_structure": True,
                            "optimize_performance": True
                        }
                    },
                    {
                        "name": "Refactor",
                        "agent": "Code Engineer",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "code_style": "idiomatic",
                            "apply_best_practices": True
                        }
                    }
                ]
            }
        ]
    }
    
    # Create the job
    print("\nCreating job...")
    create_response = requests.post(
        f"{BASE_URL}/jobs",
        json=job_data,
        headers={"Content-Type": "application/json"}
    )
    
    if create_response.status_code in [200, 201]:
        job = create_response.json()
        print(f"\n✅ Job created successfully!")
        print(f"Job ID: {job['id']}")
        print(f"Job Name: {job['name']}")
        print(f"Source: {job['source_name']} → Target: {job['target_name']}")
        print(f"\nStages:")
        for stage in job['stages']:
            print(f"  - {stage['name']}")
            for task in stage['tasks']:
                print(f"    • {task['name']} ({task['agent']})")
        
        print(f"\n🔗 View job at: http://localhost:5000/")
        print(f"Click on the job to see tasks and execute them individually")
        
        return job
    else:
        print(f"Failed to create job: {create_response.text}")
        return None


def main():
    """Main function"""
    print("=" * 60)
    print("Code Conversion Studio - Test Job Creator")
    print("=" * 60)
    
    job = create_test_job()
    
    if job:
        print("\n" + "=" * 60)
        print("Job created! You can now:")
        print("1. Go to the dashboard")
        print("2. Click on the job")
        print("3. Execute tasks individually")
        print("4. View outputs for each task")
        print("=" * 60)


if __name__ == "__main__":
    main()