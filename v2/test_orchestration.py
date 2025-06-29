#!/usr/bin/env python3
"""
Test script for prompt orchestration
"""
import os
import sys
import json
from pathlib import Path

# Add the v2 directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.prompt_orchestrator import prompt_orchestrator


def test_get_sequence():
    """Test getting prompt sequences"""
    print("Testing prompt sequence retrieval...")
    print("=" * 60)
    
    test_cases = [
        ("code_architect", "plan", "rust"),
        ("code_engineer", "migrate", "python"),
        ("qa_engineer", "test", "java"),
        ("devops_engineer", "setup_ci_cd", "go"),
    ]
    
    for agent, capability, target in test_cases:
        print(f"\n{agent} - {capability} → {target}:")
        sequence = prompt_orchestrator.get_prompt_sequence(agent, capability, target)
        
        for i, prompt in enumerate(sequence, 1):
            exists = "✓" if prompt['path'].exists() else "✗"
            print(f"  {i}. [{exists}] {prompt['type']}: {prompt['file']} - {prompt['purpose']}")


def test_orchestration_info():
    """Test getting orchestration info"""
    print("\n\nOrchestration Information:")
    print("=" * 60)
    
    info = prompt_orchestrator.get_orchestration_info()
    
    for agent, capabilities in info.items():
        print(f"\n{agent}:")
        for capability, details in capabilities.items():
            print(f"  - {capability}: {details['description']} ({details['steps']} steps)")


def test_validation():
    """Test orchestration validation"""
    print("\n\nValidation Test:")
    print("=" * 60)
    
    targets = ["rust", "python", "java", "go", "typescript"]
    result = prompt_orchestrator.validate_orchestration("code_architect", "plan", targets)
    
    print(f"Agent: {result['agent']}")
    print(f"Capability: {result['capability']}")
    print(f"Overall Valid: {result['valid']}")
    
    for target, validation in result['targets'].items():
        missing = len(validation['missing_prompts'])
        found = len(validation['found_prompts'])
        status = "✓" if missing == 0 else f"✗ ({missing} missing)"
        print(f"  {target}: {status} - {found} prompts found")


def test_fallback():
    """Test fallback behavior for undefined orchestrations"""
    print("\n\nFallback Test:")
    print("=" * 60)
    
    # Test with an agent/capability that might not have orchestration defined
    sequence = prompt_orchestrator.get_prompt_sequence("tech_writer", "document", "rust")
    
    if sequence:
        print("Fallback sequence generated:")
        for i, prompt in enumerate(sequence, 1):
            exists = "✓" if prompt['path'].exists() else "✗"
            print(f"  {i}. [{exists}] {prompt['type']}: {prompt['file']}")
    else:
        print("No fallback sequence generated")


def main():
    """Run all tests"""
    print("Prompt Orchestration Tests")
    print("=" * 60)
    
    test_get_sequence()
    test_orchestration_info()
    test_validation()
    test_fallback()
    
    print("\n\nTests completed!")
    print("\nView the orchestration visually at: http://localhost:5000/orchestration")


if __name__ == '__main__':
    main()