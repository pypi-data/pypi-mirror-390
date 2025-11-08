"""
Row count tracking tests for monitoring data volume changes over time.
Handles both append and truncate operations with Firestore history tracking.
"""

import pandas as pd
import inspect, os
from typing import Dict, List, Any, Optional
from ..main.testkit import TestKit


class RowCountTests:
    """Row count tracking tests for monitoring data volume changes."""
    
    def __init__(self, testkit: TestKit, caller_script: Optional[str] = None):
        """
        Initialize RowCountTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration
        """
        self.testkit = testkit
    
        # Set caller script for easier identification in logs
        self.caller_script = caller_script if caller_script else os.path.basename(inspect.getfile(inspect.currentframe()))

    def check_row_count_change(self, df: pd.DataFrame, table_name: str, 
                              operation_type: str = "append", test_name: str = "check_row_count_change") -> bool:
        """
        Check row count changes against historical data and configurable thresholds.
        Handles both append and truncate operations with Firestore history tracking.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table being processed
            operation_type: "append" or "truncate" - how data is being loaded
            test_name: Name of the test for logging
            
        Returns:
            True if row count change is acceptable, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_row_count_validation'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Row count validation disabled - validation skipped")
                return True
            
            if df is None:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None")
                return False
            
            current_count = len(df)
            current_date = self.testkit.start_time.date().isoformat()
            
            # Get thresholds from config using universal API
            warn_percentage = self.testkit.get_threshold('global.row_count_change.warn_percentage', 20)
            fail_percentage = self.testkit.get_threshold('global.row_count_change.fail_percentage', 50)
            
            # Get historical data from Firestore
            historical_data = self._get_row_count_history(table_name)
            
            # Store current execution
            self._store_row_count_execution(table_name, current_count, current_date, operation_type)
            
            # Determine comparison logic based on operation type
            if operation_type == "append":
                # For append: compare current total vs previous total
                comparison_result = self._compare_append_operation(
                    current_count, historical_data, warn_percentage, fail_percentage
                )
            elif operation_type == "truncate":
                # For truncate: compare current count vs previous day's count
                comparison_result = self._compare_truncate_operation(
                    current_count, historical_data, warn_percentage, fail_percentage
                )
            else:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Invalid operation_type: {operation_type}. Must be 'append' or 'truncate'")
                return False
            
            # Log result based on comparison
            if comparison_result['status'] == 'pass':
                self.testkit.log_pass(
                    test_name = test_name, 
                    message = f"Row count change acceptable: {comparison_result['message']}",
                    metrics=comparison_result['metrics']
                )
                return True
            elif comparison_result['status'] == 'warn':
                self.testkit.log_warn(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", 
                    message = f"Row count change warning: {comparison_result['message']}",
                    metrics=comparison_result['metrics']
                )
                return True
            else:  # fail
                self.testkit.log_fail(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", 
                    message = f"Row count change failure: {comparison_result['message']}",
                    metrics=comparison_result['metrics']
                )
                return False
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking row count change: {str(e)}")
            return False

    def _get_row_count_history(self, table_name: str) -> List[Dict[str, Any]]:
        """Get row count history for a table from Firestore."""
        try:
            if not self.testkit.firestore_client:
                return []
            
            # Get history from Firestore
            history_ref = self.testkit.firestore_client.collection('row_count_history').document(table_name)
            history_doc = history_ref.get()
            
            if history_doc.exists:
                data = history_doc.to_dict()
                return data.get('executions', [])
            else:
                return []
                
        except Exception as e:
            print(f"Warning: Could not retrieve row count history: {e}")
            return []

    def _store_row_count_execution(self, table_name: str, row_count: int, date: str, operation_type: str):
        """Store current execution in Firestore history."""
        try:
            if not self.testkit.firestore_client:
                return
            
            # Get existing history
            history_ref = self.testkit.firestore_client.collection('row_count_history').document(table_name)
            history_doc = history_ref.get()
            
            executions = []
            if history_doc.exists:
                data = history_doc.to_dict()
                executions = data.get('executions', [])
            
            # Add current execution
            current_execution = {
                'date': date,
                'row_count': row_count,
                'operation_type': operation_type,
                'run_id': self.testkit.run_id,
                'timestamp': self.testkit.start_time.isoformat()
            }
            
            # Add to beginning of list (most recent first)
            executions.insert(0, current_execution)
            
            # Keep only last 7 executions
            executions = executions[:7]
            
            # Store back to Firestore
            history_ref.set({
                'table_name': table_name,
                'executions': executions,
                'last_updated': self.testkit.start_time.isoformat()
            })
            
        except Exception as e:
            print(f"Warning: Could not store row count execution: {e}")

    def _compare_append_operation(self, current_count: int, historical_data: List[Dict], 
                                 warn_percentage: float, fail_percentage: float) -> Dict[str, Any]:
        """Compare append operation against historical data."""
        if not historical_data:
            return {
                'status': 'pass',
                'message': f"No historical data available. Current count: {current_count}",
                'metrics': {'current_count': current_count, 'change_percentage': 0}
            }
        
        # For append, compare total current count vs previous total count
        previous_execution = historical_data[0]  # Most recent
        previous_count = previous_execution['row_count']
        
        if previous_count == 0:
            change_percentage = 100 if current_count > 0 else 0
        else:
            change_percentage = ((current_count - previous_count) / previous_count) * 100
        
        metrics = {
            'current_count': current_count,
            'previous_count': previous_count,
            'change_percentage': round(change_percentage, 2),
            'operation_type': 'append'
        }
        
        if abs(change_percentage) <= warn_percentage:
            return {
                'status': 'pass',
                'message': f"Append operation: {current_count} rows (change: {change_percentage:+.1f}%)",
                'metrics': metrics
            }
        elif abs(change_percentage) <= fail_percentage:
            return {
                'status': 'warn',
                'message': f"Append operation: {current_count} rows (change: {change_percentage:+.1f}% - exceeds warning threshold {warn_percentage}%)",
                'metrics': metrics
            }
        else:
            return {
                'status': 'fail',
                'message': f"Append operation: {current_count} rows (change: {change_percentage:+.1f}% - exceeds failure threshold {fail_percentage}%)",
                'metrics': metrics
            }

    def _compare_truncate_operation(self, current_count: int, historical_data: List[Dict], 
                                   warn_percentage: float, fail_percentage: float) -> Dict[str, Any]:
        """Compare truncate operation against historical data."""
        if not historical_data:
            return {
                'status': 'pass',
                'message': f"No historical data available. Current count: {current_count}",
                'metrics': {'current_count': current_count, 'change_percentage': 0}
            }
        
        # For truncate, find the most recent execution from a different day
        current_date = self.testkit.start_time.date().isoformat()
        previous_day_execution = None
        
        for execution in historical_data:
            if execution['date'] != current_date:
                previous_day_execution = execution
                break
        
        if not previous_day_execution:
            return {
                'status': 'pass',
                'message': f"No previous day data available. Current count: {current_count}",
                'metrics': {'current_count': current_count, 'change_percentage': 0}
            }
        
        previous_count = previous_day_execution['row_count']
        
        if previous_count == 0:
            change_percentage = 100 if current_count > 0 else 0
        else:
            change_percentage = ((current_count - previous_count) / previous_count) * 100
        
        metrics = {
            'current_count': current_count,
            'previous_count': previous_count,
            'change_percentage': round(change_percentage, 2),
            'operation_type': 'truncate',
            'previous_date': previous_day_execution['date']
        }
        
        if abs(change_percentage) <= warn_percentage:
            return {
                'status': 'pass',
                'message': f"Truncate operation: {current_count} rows (change: {change_percentage:+.1f}% vs {previous_day_execution['date']})",
                'metrics': metrics
            }
        elif abs(change_percentage) <= fail_percentage:
            return {
                'status': 'warn',
                'message': f"Truncate operation: {current_count} rows (change: {change_percentage:+.1f}% vs {previous_day_execution['date']} - exceeds warning threshold {warn_percentage}%)",
                'metrics': metrics
            }
        else:
            return {
                'status': 'fail',
                'message': f"Truncate operation: {current_count} rows (change: {change_percentage:+.1f}% vs {previous_day_execution['date']} - exceeds failure threshold {fail_percentage}%)",
                'metrics': metrics
            }
