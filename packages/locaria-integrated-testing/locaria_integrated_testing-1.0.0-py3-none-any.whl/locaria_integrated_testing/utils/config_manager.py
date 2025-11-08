"""
Configuration management utility for the integrated testing framework.
Provides tools to manage repository-specific configurations in Firestore.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from google.cloud import firestore
from pathlib import Path

# Add the parent directory to the path so we can import the config store
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from config.config_store import ConfigStore
from config.bigquery_config_store import BigQueryConfigStore

class ConfigManager:
    """Manages repository-specific testing configurations in Firestore."""
    
    def __init__(self, project_id: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            project_id: GCP project ID for Firestore (if None, will try to get from config store)
        """
        # Try to get project ID from existing config store if not provided
        if project_id is None:
            try:                
                # Initialize config store to get the project ID
                bq_config = BigQueryConfigStore()
                config_store = ConfigStore(bigquery_config_store=bq_config)
                project_id = config_store.GCP_CONFIG_STORE_PROJECT
                print(f"Using project ID from config store: {project_id}")
                
            except Exception as config_error:
                print(f"Warning: Could not load config store, using fallback: {config_error}")
                # Fallback to hardcoded project ID
                project_id = "locaria-dev-config-store"
                print(f"Using fallback project ID: {project_id}")
        
        self.project_id = project_id
        self.firestore_client = firestore.Client(project=self.project_id)
        self.collection_name = 'integrated_testing_config'
    
    def create_repository_config(self, repository_name: str, config: Dict[str, Any]) -> bool:
        """
        Create a new repository configuration.
        
        Args:
            repository_name: Name of the repository
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            config['created_at'] = datetime.now(timezone.utc)
            config['created_by'] = os.getenv('USER', 'unknown')
            config['last_updated'] = datetime.now(timezone.utc)
            config['updated_by'] = os.getenv('USER', 'unknown')
            
            # Create the document
            doc_ref = self.firestore_client.collection(self.collection_name).document(repository_name)
            doc_ref.set(config)
            
            print(f"Created configuration for repository: {repository_name}")
            return True
            
        except Exception as e:
            print(f"Error creating configuration for {repository_name}: {e}")
            return False
    
    def update_repository_config(self, repository_name: str, config_updates: Dict[str, Any]) -> bool:
        """
        Update an existing repository configuration.
        
        Args:
            repository_name: Name of the repository
            config_updates: Dictionary of configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            config_updates['last_updated'] = datetime.now(timezone.utc)
            config_updates['updated_by'] = os.getenv('USER', 'unknown')
            
            # Update the document
            doc_ref = self.firestore_client.collection(self.collection_name).document(repository_name)
            doc_ref.set(config_updates, merge=True)
            
            print(f"Updated configuration for repository: {repository_name}")
            return True
            
        except Exception as e:
            print(f"Error updating configuration for {repository_name}: {e}")
            return False
    
    def get_repository_config(self, repository_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific repository.
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            doc_ref = self.firestore_client.collection(self.collection_name).document(repository_name)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"No configuration found for repository: {repository_name}")
                return None
                
        except Exception as e:
            print(f"Error getting configuration for {repository_name}: {e}")
            return None
    
    def get_all_repository_configs(self) -> Dict[str, Any]:
        """
        Get all repository configurations.
        
        Returns:
            Dictionary mapping repository names to their configurations
        """
        try:
            configs = {}
            docs = self.firestore_client.collection(self.collection_name).stream()
            
            for doc in docs:
                configs[doc.id] = doc.to_dict()
            
            print(f"Retrieved configurations for {len(configs)} repositories")
            return configs
            
        except Exception as e:
            print(f"Error getting all repository configurations: {e}")
            return {}
    
    def delete_repository_config(self, repository_name: str) -> bool:
        """
        Delete configuration for a specific repository.
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.firestore_client.collection(self.collection_name).document(repository_name)
            doc_ref.delete()
            
            print(f"Deleted configuration for repository: {repository_name}")
            return True
            
        except Exception as e:
            print(f"Error deleting configuration for {repository_name}: {e}")
            return False
    
    def update_thresholds(self, repository_name: str, category: str, thresholds: Dict[str, Any]) -> bool:
        """
        Update thresholds for a specific category.
        
        Args:
            repository_name: Name of the repository
            category: Threshold category (e.g., 'row_count_change')
            thresholds: Dictionary of threshold updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current configuration
            current_config = self.get_repository_config(repository_name)
            if not current_config:
                print(f"No configuration found for repository: {repository_name}")
                return False
            
            # Update thresholds
            if 'thresholds' not in current_config:
                current_config['thresholds'] = {}
            
            if category not in current_config['thresholds']:
                current_config['thresholds'][category] = {}
            
            current_config['thresholds'][category].update(thresholds)
            
            # Save updated configuration
            return self.update_repository_config(repository_name, current_config)
            
        except Exception as e:
            print(f"Error updating thresholds for {repository_name}: {e}")
            return False
    
    def update_test_switches(self, repository_name: str, switches: Dict[str, bool]) -> bool:
        """
        Update test switches for a repository.
        
        Args:
            repository_name: Name of the repository
            switches: Dictionary of test switch updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current configuration
            current_config = self.get_repository_config(repository_name)
            if not current_config:
                print(f"No configuration found for repository: {repository_name}")
                return False
            
            # Update test switches
            if 'test_switches' not in current_config:
                current_config['test_switches'] = {}
            
            current_config['test_switches'].update(switches)
            
            # Save updated configuration
            return self.update_repository_config(repository_name, current_config)
            
        except Exception as e:
            print(f"Error updating test switches for {repository_name}: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration template.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'api_config': {
                'email_api_url': 'https://locaria-dev-finance-reports.ew.r.appspot.com/api/tools/send_email_direct',
                'email_template_failure': 'Test Failure Alert',
                'email_template_warning': 'Test Warning Digest',
                'sheet_logger_spreadsheet_id': '1mXwqEiG2LKngwFaIb6AepGNUbUSmYngjYnh1nzl3iLU',
                'sheet_logger_tab_name': 'TestLogs'
            },
            'thresholds': {
                'row_count_change': {
                    'warn_percentage': 20,
                    'fail_percentage': 50
                },
                'out_of_office_percentage': {
                    'warn_threshold': 25,
                    'fail_threshold': 35
                },
                'time_split_tolerance': {
                    'precision': 0.01
                },
                'data_freshness': {
                    'max_age_hours': 48,  # 2 days
                    'warn_age_hours': 24  # 1 day
                },
                'financial_data': {
                    'variance_threshold': 0.15,
                    'min_amount_threshold': 0.01
                },
                'api_response': {
                    'max_response_time_seconds': 30,
                    'min_success_rate': 0.95
                },
                'data_quality': {
                    'min_completeness_percentage': 95.0,
                    'max_null_percentage': 5.0,
                    'max_duplicate_percentage': 1.0
                },
                'numeric_ranges': {
                    'default_tolerance': 0.01
                }
            },
            'test_switches': {
                'enable_schema_validation': True,
                'enable_business_logic_checks': True,
                'enable_freshness_checks': True,
                'enable_row_count_validation': True,
                'enable_api_health_checks': True,
                'enable_data_quality_checks': True,
                'enable_numeric_range_checks': True
            },
            'pipeline_overrides': {},
            'email_alerts': {
                'failure_recipients': ['data_team@locaria.com'],
                'warning_recipients': ['data_team@locaria.com'],
                'digest_frequency': 'daily',
                'send_immediate_failure_alerts': True,
                'send_warning_digests': True
            },
            'logging': {
                'log_level': 'INFO',
                'max_log_entries': 1000,
                'log_retention_days': 30,
                'enable_console_logging': True,
                'enable_sheet_logging': True
            },
            'default_behavior': {
                'fail_on_error': False,  # Default to continue on failures
                'stop_pipeline_on_failure': False  # Default to continue on failures
            }
        }
    
    def create_default_config_for_repository(self, repository_name: str) -> bool:
        """
        Create a default configuration for a repository.
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            True if successful, False otherwise
        """
        default_config = self.get_default_config()
        return self.create_repository_config(repository_name, default_config)
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level keys
        required_keys = ['thresholds', 'test_switches', 'email_alerts', 'logging']
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # Validate thresholds structure
        if 'thresholds' in config:
            thresholds = config['thresholds']
            if not isinstance(thresholds, dict):
                errors.append("Thresholds must be a dictionary")
            else:
                # Check for required global threshold categories
                global_thresholds = thresholds.get('global', {})
                required_categories = ['row_count_change', 'data_freshness']
                for category in required_categories:
                    if category not in global_thresholds:
                        errors.append(f"Missing required global threshold category: {category}")
        
        # Validate test switches
        if 'test_switches' in config:
            switches = config['test_switches']
            if not isinstance(switches, dict):
                errors.append("Test switches must be a dictionary")
            else:
                # Check for required switches
                required_switches = ['enable_schema_validation', 'enable_business_logic_checks']
                for switch in required_switches:
                    if switch not in switches:
                        errors.append(f"Missing required test switch: {switch}")
                    elif not isinstance(switches[switch], bool):
                        errors.append(f"Test switch {switch} must be a boolean")
        
        return errors
    
    def get_threshold(self, repository_name: str, path: str, default_value: Any = None) -> Any:
        """
        Get a threshold value using dot notation path.
        
        Args:
            repository_name: Name of the repository
            path: Dot notation path to threshold (e.g., 'plunet_employee_table.check_employee_data_completeness.completeness_threshold')
            default_value: Default value if threshold not found
            
        Returns:
            Threshold value or default_value if not found
        """
        try:
            config = self.get_repository_config(repository_name)
            if not config:
                return default_value
            
            # Navigate using dot notation path
            current = config
            for key in path.split('.'):
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default_value
            
            return current
            
        except Exception as e:
            print(f"Error getting threshold for {repository_name}.{path}: {e}")
            return default_value
    
    def set_threshold(self, repository_name: str, path: str, value: Any) -> bool:
        """
        Set a threshold value using dot notation path.
        
        Args:
            repository_name: Name of the repository
            path: Dot notation path to threshold (e.g., 'thresholds.plunet_employee_table.check_employee_data_completeness.completeness_threshold')
            value: New threshold value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current configuration
            current_config = self.get_repository_config(repository_name)
            if not current_config:
                print(f"No configuration found for repository: {repository_name}")
                return False
            
            # Navigate to the parent of the target key and set the value
            keys = path.split('.')
            current = current_config
            
            # Navigate to the parent container
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            current[keys[-1]] = value
            
            # Save updated configuration
            return self.update_repository_config(repository_name, current_config)
            
        except Exception as e:
            print(f"Error setting threshold for {repository_name}.{path}: {e}")
            return False
    
    def get_pipeline_config(self, repository_name: str, pipeline_name: str) -> Dict[str, Any]:
        """
        Get all configuration for a specific pipeline.
        
        Args:
            repository_name: Name of the repository
            pipeline_name: Name of the pipeline
            
        Returns:
            Dictionary of pipeline configuration
        """
        try:
            config = self.get_repository_config(repository_name)
            if not config:
                return {}
            
            # Get pipeline-specific thresholds
            thresholds = config.get('thresholds', {})
            pipeline_thresholds = thresholds.get(pipeline_name, {})
            
            return {
                'thresholds': pipeline_thresholds,
                'global_thresholds': thresholds.get('global_thresholds', {}),
                'test_switches': config.get('test_switches', {}),
                'email_alerts': config.get('email_alerts', {}),
                'logging': config.get('logging', {})
            }
            
        except Exception as e:
            print(f"Error getting pipeline config for {repository_name}.{pipeline_name}: {e}")
            return {}