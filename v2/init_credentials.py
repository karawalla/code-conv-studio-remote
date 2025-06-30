#!/usr/bin/env python3
"""Initialize default credentials for the Code Conversion Studio"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import CredentialsService

def init_credentials():
    """Create default credentials"""
    credentials_service = CredentialsService('data')
    
    # Check if credentials already exist
    existing = credentials_service.get_all_credentials()
    if existing:
        print(f"Found {len(existing)} existing credentials. Skipping initialization.")
        return
    
    print("Creating default credentials...")
    
    # Jira Cloud credential
    jira_cloud_data = {
        'name': 'Jira Cloud - Demo Instance',
        'type': 'jira',
        'data': {
            'url': 'https://demo-company.atlassian.net',
            'project_key': 'MIGRATE',
            'email': 'demo@company.com',
            'api_token': 'demo_api_token_replace_with_real'
        }
    }
    
    try:
        jira_cloud = credentials_service.create_credential(jira_cloud_data)
        if jira_cloud:
            print("✓ Created Jira Cloud credential")
    except Exception as e:
        print(f"✗ Failed to create Jira Cloud credential: {e}")
    
    # Jira Local (On-Premise) credential
    jira_local_data = {
        'name': 'Jira Server - Internal',
        'type': 'jira_local',
        'data': {
            'url': 'https://jira.internal.company.com',
            'project_key': 'DEV',
            'username': 'jira_admin',
            'password': 'demo_password_replace_with_real'
        }
    }
    
    try:
        jira_local = credentials_service.create_credential(jira_local_data)
        if jira_local:
            print("✓ Created Jira Local credential")
    except Exception as e:
        print(f"✗ Failed to create Jira Local credential: {e}")
    
    # GitHub Personal Access Token
    github_data = {
        'name': 'GitHub - Personal Account',
        'type': 'github',
        'data': {
            'token': 'ghp_demo_token_replace_with_real',
            'username': 'demo_user'
        }
    }
    
    try:
        github = credentials_service.create_credential(github_data)
        if github:
            print("✓ Created GitHub credential")
    except Exception as e:
        print(f"✗ Failed to create GitHub credential: {e}")
    
    # PostgreSQL Database
    postgres_data = {
        'name': 'PostgreSQL - Development DB',
        'type': 'postgresql',
        'data': {
            'host': 'localhost',
            'port': '5432',
            'database': 'code_migration_dev',
            'username': 'postgres',
            'password': 'demo_password_replace_with_real',
            'ssl_mode': 'prefer'
        }
    }
    
    try:
        postgres = credentials_service.create_credential(postgres_data)
        if postgres:
            print("✓ Created PostgreSQL credential")
    except Exception as e:
        print(f"✗ Failed to create PostgreSQL credential: {e}")
    
    # Email SMTP credential
    email_data = {
        'name': 'Email - Company SMTP',
        'type': 'email',
        'data': {
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': '587',
            'username': 'noreply@company.com',
            'password': 'demo_password_replace_with_real',
            'from_address': 'noreply@company.com'
        }
    }
    
    try:
        email = credentials_service.create_credential(email_data)
        if email:
            print("✓ Created Email credential")
    except Exception as e:
        print(f"✗ Failed to create Email credential: {e}")
    
    # Slack webhook
    slack_data = {
        'name': 'Slack - Development Team',
        'type': 'slack',
        'data': {
            'webhook_url': 'https://hooks.slack.com/services/DEMO/WEBHOOK/URL',
            'default_channel': '#code-migration'
        }
    }
    
    try:
        slack = credentials_service.create_credential(slack_data)
        if slack:
            print("✓ Created Slack credential")
    except Exception as e:
        print(f"✗ Failed to create Slack credential: {e}")
    
    # Microsoft Teams webhook
    teams_data = {
        'name': 'Teams - Engineering Channel',
        'type': 'teams',
        'data': {
            'webhook_url': 'https://outlook.office.com/webhook/DEMO-WEBHOOK-URL'
        }
    }
    
    try:
        teams = credentials_service.create_credential(teams_data)
        if teams:
            print("✓ Created Microsoft Teams credential")
    except Exception as e:
        print(f"✗ Failed to create Teams credential: {e}")
    
    print("\nInitialization complete!")
    print("\nIMPORTANT: Please update the demo credentials with real values before using them.")
    print("The sensitive fields (passwords, tokens, etc.) are encrypted and stored securely.")

if __name__ == '__main__':
    init_credentials()