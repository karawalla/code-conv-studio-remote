#!/usr/bin/env python3
"""
Script to create a test job without JIRA tasks - focused on code migration only
"""
import requests
import json
import sys
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def create_code_only_job():
    """Create a test job with only code-related stages (no JIRA/PM tasks)"""
    
    print("Creating code-only test job...")
    
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
    
    # Job creation payload - only code-related stages
    job_data = {
        "name": f"Code Migration Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Test job for code migration without project management tasks",
        "source_id": source['id'],
        "source_name": source['name'],
        "source_type": source['type'],
        "target_id": "rust",
        "target_name": "Rust",
        "target_type": "rust",
        "stages": [
            {
                "id": "stage_1",
                "name": "Analysis",
                "order": 1,
                "tasks": [
                    {
                        "name": "Analyze",
                        "agent": "Code Architect",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "analysis_depth": "comprehensive",
                            "include_dependencies": True,
                            "generate_reports": True
                        }
                    }
                ]
            },
            {
                "id": "stage_2",
                "name": "Planning",
                "order": 2,
                "tasks": [
                    {
                        "name": "Plan",
                        "agent": "Code Architect", 
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "strategy": "incremental",
                            "risk_assessment": True,
                            "estimate_effort": True
                        }
                    }
                ]
            },
            {
                "id": "stage_3",
                "name": "Implementation",
                "order": 3,
                "tasks": [
                    {
                        "name": "Migrate",
                        "agent": "Code Engineer",
                        "status": "pending", 
                        "enabled": True,
                        "config": {
                            "preserve_structure": True,
                            "optimize_performance": True,
                            "maintain_compatibility": False
                        }
                    },
                    {
                        "name": "Refactor",
                        "agent": "Code Engineer",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "code_style": "idiomatic",
                            "apply_best_practices": True,
                            "modernize_patterns": True
                        }
                    }
                ]
            },
            {
                "id": "stage_4",
                "name": "Quality Assurance",
                "order": 4,
                "tasks": [
                    {
                        "name": "Test",
                        "agent": "QA Engineer",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "test_coverage": "comprehensive",
                            "include_integration_tests": True,
                            "performance_benchmarks": True
                        }
                    },
                    {
                        "name": "Validate",
                        "agent": "QA Engineer",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "validate_functionality": True,
                            "check_edge_cases": True,
                            "verify_requirements": True
                        }
                    }
                ]
            },
            {
                "id": "stage_5",
                "name": "Documentation",
                "order": 5,
                "tasks": [
                    {
                        "name": "Document",
                        "agent": "Tech Writer",
                        "status": "pending",
                        "enabled": True,
                        "config": {
                            "api_documentation": True,
                            "migration_guide": True,
                            "code_examples": True
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
            print(f"  - {stage['name']} ({len(stage['tasks'])} tasks)")
            for task in stage['tasks']:
                print(f"    • {task['name']} ({task['agent']})")
        
        print(f"\n🔗 View job at: http://localhost:5000/")
        print(f"\nNOTE: This job contains only code-related tasks.")
        print(f"All project management and JIRA tasks have been excluded.")
        print(f"\nYou can now:")
        print("1. Click on the job to view details")
        print("2. Use the Edit button to modify stages/tasks")
        print("3. Execute tasks individually")
        print("4. View outputs after execution")
        
        return job
    else:
        print(f"Failed to create job: {create_response.text}")
        return None


def main():
    """Main function"""
    print("=" * 60)
    print("Code Conversion Studio - Code-Only Test Job Creator")
    print("=" * 60)
    
    job = create_code_only_job()
    
    if job:
        print("\n" + "=" * 60)
        print("Success! Your code-only job is ready.")
        print("=" * 60)


if __name__ == "__main__":
    main()