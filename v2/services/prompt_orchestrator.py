"""
Prompt Orchestrator Service
Manages the orchestration of prompts between agents and targets
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PromptOrchestrator:
    """
    Orchestrates the execution of prompts by combining agent capabilities 
    with target-specific prompts in the correct sequence
    """
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.prompt_sequences = self._load_prompt_sequences()
        
    def _load_prompt_sequences(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the prompt sequence mappings that define how agent capabilities
        should integrate with target prompts
        """
        # Define the orchestration patterns for each agent capability
        return {
            "code_architect": {
                "plan": {
                    "description": "Analyze source and create migration plan",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_analyze_project_structure.md", "02_create_migration_plan.md"],
                            "purpose": "Understand source architecture"
                        },
                        {
                            "type": "target",
                            "prompt": "01_analyze.md",
                            "purpose": "Analyze target requirements"
                        },
                        {
                            "type": "target", 
                            "prompt": "02_plan.md",
                            "purpose": "Create target-specific migration plan"
                        },
                        {
                            "type": "agent",
                            "prompts": ["03_design_target_architecture.md"],
                            "purpose": "Design final architecture"
                        }
                    ]
                },
                "analyze": {
                    "description": "Deep analysis of source code",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_analyze_codebase.md", "02_identify_patterns.md"],
                            "purpose": "Analyze source patterns"
                        },
                        {
                            "type": "target",
                            "prompt": "01_analyze.md",
                            "purpose": "Map to target patterns"
                        }
                    ]
                }
            },
            "code_engineer": {
                "migrate": {
                    "description": "Execute code migration",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_setup_target_project.md"],
                            "purpose": "Initialize target project"
                        },
                        {
                            "type": "target",
                            "prompt": "03_migrate.md",
                            "purpose": "Execute target-specific migration"
                        },
                        {
                            "type": "agent",
                            "prompts": ["02_migrate_data_models.md"],
                            "purpose": "Migrate data structures"
                        }
                    ]
                },
                "refactor": {
                    "description": "Refactor migrated code",
                    "sequence": [
                        {
                            "type": "target",
                            "prompt": "04_validate.md",
                            "purpose": "Validate against target standards"
                        },
                        {
                            "type": "target",
                            "prompt": "05_fix.md",
                            "purpose": "Fix target-specific issues"
                        }
                    ]
                }
            },
            "qa_engineer": {
                "test": {
                    "description": "Create and run tests",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_analyze_test_requirements.md"],
                            "purpose": "Understand testing needs"
                        },
                        {
                            "type": "target",
                            "prompt": "04_validate.md",
                            "purpose": "Target-specific validation"
                        },
                        {
                            "type": "agent",
                            "prompts": ["02_create_test_suite.md"],
                            "purpose": "Create comprehensive tests"
                        }
                    ]
                },
                "validate": {
                    "description": "Validate migration quality",
                    "sequence": [
                        {
                            "type": "target",
                            "prompt": "04_validate.md",
                            "purpose": "Target validation rules"
                        },
                        {
                            "type": "agent",
                            "prompts": ["01_run_validation_suite.md"],
                            "purpose": "Execute validation"
                        }
                    ]
                }
            },
            "devops_engineer": {
                "setup_ci_cd": {
                    "description": "Setup CI/CD pipeline",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_analyze_deployment_needs.md"],
                            "purpose": "Understand deployment requirements"
                        },
                        {
                            "type": "target",
                            "prompt": "03_migrate.md",
                            "purpose": "Target deployment patterns"
                        },
                        {
                            "type": "agent",
                            "prompts": ["02_create_pipeline.md"],
                            "purpose": "Create CI/CD pipeline"
                        }
                    ]
                }
            },
            "project_manager": {
                "project_kickoff": {
                    "description": "Initialize project",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_initialize_project.md"],
                            "purpose": "Setup project structure"
                        },
                        {
                            "type": "target",
                            "prompt": "06_discuss.md",
                            "purpose": "Discuss target approach"
                        }
                    ]
                },
                "status_report": {
                    "description": "Generate status reports",
                    "sequence": [
                        {
                            "type": "agent",
                            "prompts": ["01_gather_metrics.md"],
                            "purpose": "Collect project metrics"
                        },
                        {
                            "type": "agent",
                            "prompts": ["02_generate_report.md"],
                            "purpose": "Create status report"
                        }
                    ]
                }
            }
        }
    
    def get_prompt_sequence(self, agent: str, capability: str, target: str) -> List[Dict[str, Any]]:
        """
        Get the orchestrated sequence of prompts for a given agent capability and target
        
        Args:
            agent: The agent name (e.g., 'code_architect')
            capability: The capability name (e.g., 'plan')
            target: The target framework (e.g., 'rust')
            
        Returns:
            List of prompt definitions in execution order
        """
        agent_key = agent.lower().replace(' ', '_')
        capability_key = capability.lower().replace(' ', '_')
        target_key = target.lower().replace(' ', '_').replace('/', '_').replace('.', '_')
        
        # Get the sequence definition
        if agent_key not in self.prompt_sequences:
            logger.warning(f"No prompt sequences defined for agent: {agent}")
            return self._get_fallback_sequence(agent_key, capability_key, target_key)
            
        agent_sequences = self.prompt_sequences[agent_key]
        if capability_key not in agent_sequences:
            logger.warning(f"No sequence defined for {agent}/{capability}")
            return self._get_fallback_sequence(agent_key, capability_key, target_key)
            
        sequence_def = agent_sequences[capability_key]
        
        # Build the actual prompt list
        prompt_list = []
        for step in sequence_def["sequence"]:
            if step["type"] == "agent":
                # Agent-specific prompts
                for prompt_file in step["prompts"]:
                    prompt_path = self.prompts_dir / agent_key / capability_key / prompt_file
                    if prompt_path.exists():
                        prompt_list.append({
                            "type": "agent",
                            "path": prompt_path,
                            "file": prompt_file,
                            "purpose": step["purpose"],
                            "agent": agent,
                            "capability": capability
                        })
                    else:
                        logger.warning(f"Agent prompt not found: {prompt_path}")
                        
            elif step["type"] == "target":
                # Target-specific prompts
                prompt_path = self.prompts_dir / "targets" / target_key / step["prompt"]
                if prompt_path.exists():
                    prompt_list.append({
                        "type": "target",
                        "path": prompt_path,
                        "file": step["prompt"],
                        "purpose": step["purpose"],
                        "target": target
                    })
                else:
                    logger.warning(f"Target prompt not found: {prompt_path}")
        
        return prompt_list
    
    def _get_fallback_sequence(self, agent: str, capability: str, target: str) -> List[Dict[str, Any]]:
        """
        Get a fallback sequence when no specific orchestration is defined
        """
        prompt_list = []
        
        # First, try to get any agent prompts
        agent_dir = self.prompts_dir / agent / capability
        if agent_dir.exists():
            for prompt_file in sorted(agent_dir.glob("*.md")):
                prompt_list.append({
                    "type": "agent",
                    "path": prompt_file,
                    "file": prompt_file.name,
                    "purpose": "Agent-specific task",
                    "agent": agent,
                    "capability": capability
                })
        
        # Then, add relevant target prompts based on capability
        target_mapping = {
            "plan": ["01_analyze.md", "02_plan.md"],
            "analyze": ["01_analyze.md"],
            "migrate": ["03_migrate.md"],
            "validate": ["04_validate.md"],
            "test": ["04_validate.md"],
            "refactor": ["05_fix.md"],
            "discuss": ["06_discuss.md"]
        }
        
        if capability in target_mapping:
            for target_prompt in target_mapping[capability]:
                prompt_path = self.prompts_dir / "targets" / target / target_prompt
                if prompt_path.exists():
                    prompt_list.append({
                        "type": "target",
                        "path": prompt_path,
                        "file": target_prompt,
                        "purpose": "Target-specific implementation",
                        "target": target
                    })
        
        return prompt_list
    
    def get_orchestration_info(self) -> Dict[str, Any]:
        """
        Get information about all available orchestrations
        """
        info = {}
        for agent, capabilities in self.prompt_sequences.items():
            info[agent] = {}
            for capability, config in capabilities.items():
                info[agent][capability] = {
                    "description": config["description"],
                    "steps": len(config["sequence"]),
                    "sequence": [
                        {
                            "type": step["type"],
                            "purpose": step["purpose"],
                            "count": len(step.get("prompts", [step.get("prompt", "")])) 
                        }
                        for step in config["sequence"]
                    ]
                }
        return info
    
    def validate_orchestration(self, agent: str, capability: str, targets: List[str]) -> Dict[str, Any]:
        """
        Validate that all required prompts exist for the orchestration
        """
        results = {
            "agent": agent,
            "capability": capability,
            "valid": True,
            "targets": {}
        }
        
        for target in targets:
            sequence = self.get_prompt_sequence(agent, capability, target)
            target_result = {
                "total_prompts": len(sequence),
                "missing_prompts": [],
                "found_prompts": []
            }
            
            for prompt in sequence:
                if prompt["path"].exists():
                    target_result["found_prompts"].append(str(prompt["path"]))
                else:
                    target_result["missing_prompts"].append(str(prompt["path"]))
                    results["valid"] = False
            
            results["targets"][target] = target_result
        
        return results


# Global instance
prompt_orchestrator = PromptOrchestrator()