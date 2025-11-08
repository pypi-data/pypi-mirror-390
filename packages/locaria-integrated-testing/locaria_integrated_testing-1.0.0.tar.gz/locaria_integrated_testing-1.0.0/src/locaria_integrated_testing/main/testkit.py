"""
Core testing framework that orchestrates test execution, logging, and alerting.
Integrates with Sheet Logger and Email Manager for comprehensive test result tracking.
"""

import json
import requests
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sheet_logger import SheetLogger
from google.cloud import firestore

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from config.config_store import ConfigStore
from config.bigquery_config_store import BigQueryConfigStore
from .acknowledge_manager import AcknowledgeManager

class TestFailureException(Exception):
    """Custom exception raised when a test fails and fail_on_error is True."""
    pass

class TestKit:
    """
    Core testing framework that orchestrates test execution, logging, and alerting.
    
    Features:
    - Sheet Logger integration for persistent test result storage
    - Email Manager integration for real-time failure notifications
    - Firestore configuration management
    - Test result aggregation and reporting
    - Configurable thresholds and test switches
    """
    
    # Class-level cache for shared resources
    _shared_sheet_logger = None
    _shared_firestore_client = None
    _shared_config = None
    
    def __init__(self, repository_name: str, pipeline_name: str = None, fail_on_error: bool = False):
        """
        Initialize the TestKit with repository and pipeline information.
        
        Args:
            repository_name: Name of the repository (e.g., 'locate_2_pulls')
            pipeline_name: Name of the specific pipeline (e.g., 'daily_updates')
            fail_on_error: If True, pipeline will stop on test failures. If False, continues with alerts.
        """
        self.repository_name = repository_name
        self.pipeline_name = pipeline_name or "unknown"
        self.fail_on_error = fail_on_error
        self.run_id = self._generate_run_id()
        self.test_results = []
        self.warnings = []
        self.failures = []
        self.failure_emails_sent = False  # Track if failure email has been sent
        self.start_time = datetime.now(timezone.utc)
        self.collection_integrated_testing_config = "integrated_testing_config"
        
        # Initialize shared resources once
        self._init_shared_resources()
        
        # Initialize sheet logger (use shared config store)
        self.sheet_logger = self._init_sheet_logger()
        
        # Initialize Firestore client for configuration (use shared config store)
        self.firestore_client = self._init_firestore_client()
        
        # Initialize acknowledgment manager
        self.acknowledge_manager = AcknowledgeManager(
            self.firestore_client, self.repository_name, self.pipeline_name
        )
        
        # Load configuration from Firestore (use shared config store)
        self.config = self._load_config_from_firestore()
        
        # Log test run start
        self._log_run_start()
    
    def _init_shared_resources(self):
        """Initialize shared resources (ConfigStore) once per TestKit instance."""
        if not hasattr(self, '_config_store'):
            try:
                # Initialize config store once
                bq_config = BigQueryConfigStore()
                self._config_store = ConfigStore(bigquery_config_store=bq_config)
            except Exception as e:
                print(f"Warning: Could not initialize config store: {e}")
                self._config_store = None
    
    def _generate_run_id(self) -> str:
        """Generate unique run identifier with timestamp and UUID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{self.repository_name}_{self.pipeline_name}_{timestamp}_{unique_id}"
    
    def _init_sheet_logger(self) -> Optional[SheetLogger]:
        """Initialize sheet logger for test result persistence."""
        # Use cached sheet logger if available
        if TestKit._shared_sheet_logger is not None:
            return TestKit._shared_sheet_logger
            
        try:
            # Check if sheet_logger is available
            if not SheetLogger:
                print("Warning: SheetLogger not available. Test results will not be persisted to sheets.")
                return None
            
            # Try to get configuration from shared config store
            try:
                if hasattr(self, '_config_store') and self._config_store:
                    # Use the existing sheet logger from shared config store
                    sheet_logger = self._config_store.sheetlogger
                    print(f"SheetLogger initialized from shared config store for spreadsheet: {self._config_store.logsheet_id}")
                    
                    # Cache the sheet logger for future use
                    TestKit._shared_sheet_logger = sheet_logger
                    return sheet_logger
                    
            except Exception as config_error:
                print(f"Warning: Could not load sheet logger from config store: {config_error}")
                
                # Fallback to environment variables
                spreadsheet_id = os.getenv('TEST_LOGS_SPREADSHEET_ID')
                if not spreadsheet_id:
                    print("Warning: TEST_LOGS_SPREADSHEET_ID not set. Test results will not be persisted to sheets.")
                    return None
                
                # Get credentials path
                credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
                if not credentials_path:
                    print("Warning: GOOGLE_CREDENTIALS_PATH not set. Test results will not be persisted to sheets.")
                    return None
                
                scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                
                # Initialize SheetLogger with environment variables
                sheet_logger = SheetLogger(
                    spreadsheet_id=spreadsheet_id,
                    scopes=scopes,
                    batch_size=10,  # Batch size for efficient API usage
                    token_full_path=credentials_path,
                    timezone='UTC'  # Use UTC for consistency
                )
                
                print(f"SheetLogger initialized from environment for spreadsheet: {spreadsheet_id}")
                return sheet_logger
            
        except Exception as e:
            print(f"Warning: Could not initialize SheetLogger: {e}")
            return None
    
    def _init_firestore_client(self) -> Optional[firestore.Client]:
        """Initialize Firestore client for configuration management."""
        # Use cached Firestore client if available
        if TestKit._shared_firestore_client is not None:
            return TestKit._shared_firestore_client
            
        try:
            # Try to get project ID from shared config store
            try:               
                if hasattr(self, '_config_store') and self._config_store:
                    project_id = self._config_store.GCP_CONFIG_STORE_PROJECT
                    print(f"Using project ID from shared config store: {project_id}")
                else:
                    raise Exception("No shared config store available")
                
            except Exception as config_error:
                print(f"Warning: Could not load config store, using fallback: {config_error}")
                # Fallback to hardcoded project ID
                project_id = "locaria-dev-config-store"
                print(f"Using fallback project ID: {project_id}")
            
            # Initialize Firestore client
            firestore_client = firestore.Client(project=project_id)
            print(f"Firestore client initialized for project: {project_id}")
            
            # Cache the Firestore client for future use
            TestKit._shared_firestore_client = firestore_client
            return firestore_client
            
        except Exception as e:
            print(f"Warning: Could not initialize Firestore client: {e}")
            return None
    
    def _load_config_from_firestore(self) -> Dict[str, Any]:
        """Load test configuration from Firestore using ConfigManager."""
        try:
            # Import ConfigManager here to avoid circular imports
            from modules.integrated_tests.utils.config_manager import ConfigManager
            
            # Initialize ConfigManager
            config_manager = ConfigManager()
            
            # Load repository-specific configuration (all at once)
            config = config_manager.get_repository_config(self.repository_name)
            
            if config:
                print(f"Loaded configuration for repository: {self.repository_name}")
                return config
            else:
                print(f"No configuration found for repository: {self.repository_name}. Using default configuration.")
                return config_manager.get_default_config()
                
        except Exception as e:
            print(f"Warning: Could not load config from Firestore: {e}")
            # Fallback to default config
            try:
                from modules.integrated_tests.utils.config_manager import ConfigManager
                config_manager = ConfigManager()
                return config_manager.get_default_config()
            except:
                return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when Firestore is not available."""
        return {
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
                    'precision': 0.01  # 1% tolerance for time splits
                },
                'data_freshness': {
                    'max_age_hours': 24,
                    'warn_age_hours': 12
                },
                'financial_data': {
                    'variance_threshold': 0.15,
                    'min_amount_threshold': 0.01
                },
                'api_response': {
                    'max_response_time_seconds': 30,
                    'min_success_rate': 0.95
                }
            },
            'test_switches': {
                'enable_schema_validation': True,
                'enable_business_logic_checks': True,
                'enable_freshness_checks': True,
                'enable_row_count_validation': True,
                'enable_api_health_checks': True
            },
            'pipeline_overrides': {},
            'email_alerts': {
                'failure_recipients': ['data_team@locaria.com'],
                'warning_recipients': ['data_team@locaria.com'],
                'digest_frequency': 'daily'
            },
            'logging': {
                'log_level': 'INFO',
                'max_log_entries': 1000,
                'log_retention_days': 30
            }
        }
    
    def _log_run_start(self):
        """Log the start of a test run."""
        start_message = f"Test run started - Repository: {self.repository_name}, Pipeline: {self.pipeline_name}, Run ID: {self.run_id}"
        print(f"🚀 {start_message}")
        
        if self.sheet_logger:
            try:
                self.sheet_logger.write_prints_to_sheet("TestLogs", start_message, flush=True)
            except Exception as e:
                print(f"Warning: Could not log run start to sheet: {e}")
    
    def log_pass(self, test_name: str, message: str = "", metrics: Dict[str, Any] = None):
        """
        Log a passing test result.
        
        Args:
            test_name: Name of the test that passed
            message: Optional message describing the test result
            metrics: Optional dictionary of metrics/measurements
        """
        result = {
            'run_id': self.run_id,
            'repository': self.repository_name,
            'pipeline': self.pipeline_name,
            'test_name': test_name,
            'status': 'PASS',
            'message': message,
            'metrics': metrics or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.test_results.append(result)
        # self._log_to_sheet(result) # logging all the passed tests clutters the logs
        print(f"✅ PASS: {test_name} - {message}")
    
    def log_warn(
        self, 
        test_name: str, 
        issue_identifier: str,
        message: str, 
        metrics: Dict[str, Any] = None, 
        acknowledgeable: bool = True
    ):
        """
        Log a warning test result.
        
        Args:
            test_name: Name of the test that generated a warning
            issue_identifier: Unique identifier for the issue (e.g., email, ID).
                It's a good practice to use the `{filename}-{function_name}` format for uniqueness.
            message: Warning message describing the issue
            metrics:  Dictionary of metrics/measurements. Required to populate the page in the Analytics Hub.
            acknowledgeable: If True, this warning can be acknowledged and muted
        """
        result = {
            'run_id': self.run_id,
            'repository': self.repository_name,
            'pipeline': self.pipeline_name,
            'test_name': test_name,
            'issue_identifier': issue_identifier,
            'status': 'WARN',
            'message': message,
            'metrics': metrics or {},
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'acknowledgeable': acknowledgeable
        }
        
        self.warnings.append(result)
        self.test_results.append(result)
        self._log_to_sheet(result)
        
        # Log the information in Firestore for acknowledgment tracking
        if acknowledgeable and issue_identifier and metrics:
                try:
                    self.acknowledge_manager.update_issue_detection(
                        test_name=test_name,
                        issue_identifier=issue_identifier,
                        issue_details=metrics.get('issue_details', ""),
                        additional_metadata=metrics  # Pass all metrics for future use
                    )
                except Exception as e:
                    print(f"Warning: Could not auto-populate acknowledgment entry: {e}")
        
        print(f"⚠️  WARN: {test_name} - {message}")
    
    def log_fail(
        self, 
        test_name: str, 
        issue_identifier: str,
        message: str, 
        metrics: Dict[str, Any] = None, 
        stop_pipeline: bool = None, 
        acknowledgeable: bool = True
    ):
        """
        Log a failing test result and trigger alerts.
        
        Args:
            test_name: Name of the test that failed.
            issue_identifier: Unique identifier for the issue (e.g., email, ID).
                It's a good practice to use the `{filename}-{function_name}` format for uniqueness.
            message: Failure message describing the issue
            metrics: Dictionary of metrics/measurements. Required to populate the page in the Analytics Hub.
            stop_pipeline: If True, send email and stop pipeline. If False, send email and continue.
                          If None, uses the fail_on_error setting from TestKit initialization.
            acknowledgeable: If True, this failure can be acknowledged and muted
            
        Raises:
            TestFailureException: If stop_pipeline is True, raises exception to stop pipeline
        """
        # Determine if we should stop the pipeline
        should_stop = stop_pipeline if stop_pipeline is not None else self.fail_on_error
        
        result = {
            'run_id': self.run_id,
            'repository': self.repository_name,
            'pipeline': self.pipeline_name,
            'test_name': test_name,
            'issue_identifier': issue_identifier,
            'status': 'FAIL',
            'message': message,
            'metrics': metrics or {},
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'acknowledgeable': acknowledgeable
        }
        
        self.failures.append(result)
        self.test_results.append(result)
        self._log_to_sheet(result)
        
        # Log the information in Firestore for acknowledgment tracking
        if acknowledgeable and issue_identifier and metrics:
            try:
                self.acknowledge_manager.update_issue_detection(
                    test_name=test_name,
                    issue_identifier=issue_identifier,
                    issue_details=metrics.get('issue_details', ""),
                    additional_metadata=metrics  # Pass the rest of the metrics to include them in the document
                )
            except Exception as e:
                print(f"Warning: Could not auto-populate acknowledgment entry: {e}")
        
        print(f"❌ FAIL: {test_name} - {message}")
        
        # If stop_pipeline=True, send summary email with all failures and stop
        if should_stop:
            self._send_failure_summary_email(issue_identifier)
            raise TestFailureException(f"Pipeline stopped due to test failure: {test_name} - {message}")
           
    def _log_to_sheet(self, result: Dict[str, Any]):
        """Log test result to Google Sheets via SheetLogger."""
        if not self.sheet_logger:
            return
            
        try:
            # Format log entry for sheet
            log_entry = f"Test: {result['test_name']} | Status: {result['status']} | Message: {result['message']}"
            if result['metrics']:
                metrics_str = json.dumps(result['metrics'], separators=(',', ':'))
                log_entry += f" | Metrics: {metrics_str}"
            
            # Write to sheet
            self.sheet_logger.write_prints_to_sheet("TestLogs", log_entry)
        except Exception as e:
            print(f"Warning: Could not log to sheet: {e}")
        finally:
            self.sheet_logger.release_remaining_logs()
    
    def _send_failure_summary_email(self, issue_identifier: str):
        """Send summary email with all failures, filtered by acknowledgment status."""
        if not self.failures or self.failure_emails_sent:
            return
        
        # Filter failures into new vs acknowledged issues
        filtered_results = self.acknowledge_manager.filter_acknowledged_issues(self.failures, issue_identifier)
        
        if not filtered_results['new_issues']:
            print("📧 All failure issues are acknowledged and muted - skipping email")
            return
            
        try:
            # Get email API URL from centralized config
            email_api_url = self.config.get('api_config', {}).get('email_api_url')
            
            if not email_api_url:
                # Fallback to environment variable
                email_api_url = os.getenv('EMAIL_API_URL')
                
            if not email_api_url:
                return
                
            # Prepare failure summary with acknowledgment context
            failure_summary = []
            
            # Add new issues
            if filtered_results['new_issues']:
                failure_summary.append("🚨 NEW ISSUES DETECTED:")
                for i, failure in enumerate(filtered_results['new_issues'], 1):
                    failure_summary.append(f"{i}. {failure['test_name']}<br/>   Message: {failure['message']}<br/>   Time: {failure['timestamp']}")
            
            # Add acknowledged issues context
            if filtered_results['acknowledged_issues']:
                if failure_summary:
                    failure_summary.append("")  # Add spacing
                failure_summary.append("✅ PREVIOUSLY ACKNOWLEDGED (muted):")
                for i, failure in enumerate(filtered_results['acknowledged_issues'], 1):
                    metrics = failure.get('metrics', {})
                    # Try multiple field names for backward compatibility
                    person_name = metrics.get('person_name') or metrics.get('issue_name', 'Unknown')
                    person_email = metrics.get('person_email') or metrics.get('issue_identifier', 'Unknown')
                    failure_summary.append(f"{i}. {failure['test_name']} - {person_name} ({person_email}) - Acknowledged and muted")
            
            failure_summary_text = "<br/><br/>".join(failure_summary)
            
            payload = {
                "task_name": self.config.get('api_config', {}).get('email_template_failure', 'Test Failure Alert'),
                "custom_variables": {
                    "repository_name": self.repository_name,
                    "pipeline_name": self.pipeline_name,
                    "run_id": self.run_id,
                    "failure_count": len(filtered_results['new_issues']),
                    "failure_summary": failure_summary_text,
                    "run_duration": self._get_run_duration(),
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            }
            
            response = requests.post(email_api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"📧 Failure summary email sent successfully")
                    self.failure_emails_sent = True
                else:
                    print(f"Warning: Failure summary email failed: {result.get('message')}")
            else:
                print(f"Warning: Failure summary email failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Warning: Could not send failure summary email: {e}")
    
    def send_warning_digest(self, issue_identifier: str):
        """Send digest of all warnings at the end of a run, filtered by acknowledgment status."""
        if not self.warnings:
            return
        
        # Filter warnings into new vs acknowledged issues
        filtered_results = self.acknowledge_manager.filter_acknowledged_issues(self.warnings, issue_identifier)
        
        if not filtered_results['new_issues']:
            print("📧 All warning issues are acknowledged and muted - skipping email")
            return
        
        try:
            # Get email API URL from centralized config
            email_api_url = self.config.get('api_config', {}).get('email_api_url')
            
            if not email_api_url:
                # Fallback to environment variable
                email_api_url = os.getenv('EMAIL_API_URL')
                
            if not email_api_url:
                return
                
            # Prepare warning digest with acknowledgment context
            warning_summary = []
            
            # Add new issues
            if filtered_results['new_issues']:
                warning_summary.append("⚠️ NEW WARNINGS DETECTED:")
                for i, warning in enumerate(filtered_results['new_issues'], 1):
                    warning_summary.append(f"{i}. {warning['test_name']}<br/>   Message: {warning['message']}<br/>   Time: {warning['timestamp']}")
            
            # Add acknowledged issues context
            if filtered_results['acknowledged_issues']:
                if warning_summary:
                    warning_summary.append("")  # Add spacing
                warning_summary.append("✅ PREVIOUSLY ACKNOWLEDGED (muted):")
                for i, warning in enumerate(filtered_results['acknowledged_issues'], 1):
                    metrics = warning.get('metrics', {})
                    # Try multiple field names for backward compatibility
                    person_name = metrics.get('person_name') or metrics.get('issue_name', 'Unknown')
                    person_email = metrics.get('person_email') or metrics.get('issue_identifier', 'Unknown')
                    warning_summary.append(f"{i}. {warning['test_name']} - {person_name} ({person_email}) - Acknowledged and muted")
            
            warning_summary_text = "<br/><br/>".join(warning_summary)
            
            payload = {
                "task_name": self.config.get('api_config', {}).get('email_template_warning', 'Test Warning Digest'),
                "custom_variables": {
                    "repository_name": self.repository_name,
                    "pipeline_name": self.pipeline_name,
                    "run_id": self.run_id,
                    "warning_count": len(filtered_results['new_issues']),
                    "warning_summary": warning_summary_text,
                    "run_duration": self._get_run_duration(),
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            }
            
            response = requests.post(email_api_url, json=payload, timeout=30)
            if response.status_code == 200:
                print(f"Warning digest sent successfully for {len(self.warnings)} warnings")
            else:
                print(f"Warning: Warning digest failed with status {response.status_code}")
                
        except Exception as e:
            print(f"Warning: Could not send warning digest: {e}")
    
    def _get_run_duration(self) -> str:
        """Get the duration of the test run."""
        duration = datetime.now(timezone.utc) - self.start_time
        return str(duration).split('.')[0]  # Remove microseconds
    
    def get_threshold(self, path: str, default_value: Any = None) -> Any:
        """
        Get a threshold value using dot notation path.
        
        Args:
            path: Dot notation path to threshold. Can be:
                  - Pipeline-specific: 'test_name.threshold_name' (e.g., 'check_employee_data_completeness.completeness_threshold')
                  - Global: 'global.category.threshold_name' (e.g., 'global.row_count_change.warn_percentage')
            default_value: Default value if threshold not found
            
        Returns:
            Threshold value or default_value if not found
        """
        try:
            # Handle global thresholds
            if path.startswith('global.'):
                full_path = f"thresholds.{path}"
            else:
                # Pipeline-specific thresholds
                full_path = f"thresholds.{self.pipeline_name}.{path}"
            
            # Navigate using dot notation path
            current = self.config
            for key in full_path.split('.'):
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default_value
            
            return current
            
        except Exception as e:
            print(f"Error getting threshold for {self.pipeline_name}.{path}: {e}")
            return default_value
    
    def set_threshold(self, path: str, value: Any) -> bool:
        """
        Set a threshold value using dot notation path.
        
        Args:
            path: Dot notation path to threshold. Can be:
                  - Pipeline-specific: 'test_name.threshold_name' (e.g., 'check_employee_data_completeness.completeness_threshold')
                  - Global: 'global.category.threshold_name' (e.g., 'global.row_count_change.warn_percentage')
            value: New threshold value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle global thresholds
            if path.startswith('global.'):
                full_path = f"thresholds.{path}"
            else:
                # Pipeline-specific thresholds
                full_path = f"thresholds.{self.pipeline_name}.{path}"
            
            # Navigate to the parent of the target key and set the value
            keys = full_path.split('.')
            current = self.config
            
            # Navigate to the parent container
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Set the final value
            current[keys[-1]] = value
            
            # Update in Firestore if available
            if self.firestore_client:
                from ..utils.config_manager import ConfigManager
                config_manager = ConfigManager()
                return config_manager.set_threshold(self.repository_name, full_path, value)
            
            return True
            
        except Exception as e:
            print(f"Error setting threshold for {self.pipeline_name}.{path}: {e}")
            return False
    
    def is_test_enabled(self, test_category: str) -> bool:
        """
        Check if a test category is enabled.
        
        Args:
            test_category: Test category to check (e.g., 'enable_schema_validation')
            
        Returns:
            True if test is enabled, False otherwise
        """
        try:
            return self.config.get('test_switches', {}).get(test_category, True)
        except Exception:
            return True
    
    def update_config_in_firestore(self, config_updates: Dict[str, Any]) -> bool:
        """Update configuration in Firestore for this repository."""
        if not self.firestore_client:
            print("Warning: Firestore client not available. Cannot update configuration.")
            return False
        
        try:
            repo_doc_ref = self.firestore_client.collection(self.collection_integrated_testing_config).document(self.repository_name)
            
            # Add metadata
            config_updates['last_updated'] = datetime.now(timezone.utc)
            config_updates['updated_by'] = os.getenv('USER', 'unknown')
            
            # Update the document
            repo_doc_ref.set(config_updates, merge=True)
            print(f"Configuration updated for repository: {self.repository_name}")
            
            # Reload configuration
            self.config = self._load_config_from_firestore()
            return True
            
        except Exception as e:
            print(f"Error updating configuration in Firestore: {e}")
            return False
    
    def finalize_run(self, issue_identifier: str):
        """Finalize the test run and send summary."""
        try:
            # Flush remaining logs to sheet
            if self.sheet_logger:
                self.sheet_logger.release_remaining_logs()
            
            # Send failure summary if there were failures (and no email sent yet)
            self._send_failure_summary_email(issue_identifier)
                       
            # Send warning digest if there were warnings
            self.send_warning_digest(issue_identifier)
            
            # Log run summary
            summary = {
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                'warnings': len(self.warnings),
                'failures': len(self.failures),
                'run_duration': self._get_run_duration()
            }
            
            # Log summary to sheet
            if self.sheet_logger:
                summary_message = f"Run Summary - Total: {summary['total_tests']}, Passed: {summary['passed']}, Warnings: {summary['warnings']}, Failures: {summary['failures']}, Duration: {summary['run_duration']}"
                self.sheet_logger.write_prints_to_sheet("TestLogs", summary_message, flush=True)
            
            print(f"🏁 Test run completed: {summary}")
            
            # Return summary for programmatic use
            return summary
            
        except Exception as e:
            print(f"Error finalizing test run: {e}")
            return None


# Convenience functions for easy import
def create_testkit(repository_name: str, pipeline_name: str = None, fail_on_error: bool = False) -> TestKit:
    """Create a new TestKit instance."""
    return TestKit(repository_name, pipeline_name, fail_on_error)


def log_pass(testkit: TestKit, test_name: str, message: str = "", metrics: Dict[str, Any] = None):
    """Log a passing test."""
    testkit.log_pass(test_name, message, metrics)


def log_warn(testkit: TestKit, test_name: str, issue_identifier: str, message: str, metrics: Dict[str, Any] = None, acknowledgeable: bool = True):
    """Log a warning."""
    testkit.log_warn(test_name, issue_identifier, message, metrics, acknowledgeable)


def log_fail(testkit: TestKit, test_name: str, issue_identifier: str, message: str, metrics: Dict[str, Any] = None, stop_pipeline: bool = None, acknowledgeable: bool = True):
    """Log a failure."""
    testkit.log_fail(test_name, issue_identifier, message, metrics, stop_pipeline, acknowledgeable)
