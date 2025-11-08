"""
Duplicate detection tests for identifying duplicate records in datasets.
Supports single or multiple column combinations for unique identification.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import inspect, os
from ..main.testkit import TestKit


class DuplicateTests:
    """Duplicate detection tests for data validation."""
    
    def __init__(self, testkit: TestKit, caller_script: Optional[str] = None):
        """
        Initialize DuplicateTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration
        """
        self.testkit = testkit
    
        # Set caller script for easier identification in logs
        self.caller_script = caller_script if caller_script else os.path.basename(inspect.getfile(inspect.currentframe()))

    def check_duplicate_records(self, df: pd.DataFrame, key_columns: List[str], 
                               test_name: str = "check_duplicate_records") -> bool:
        """
        Check for duplicate records based on specified key columns.
        
        Args:
            df: DataFrame to validate
            key_columns: List of column names that should uniquely identify records
                       Can be single column: ["employee_id"] 
                       Or multiple columns: ["employee_id", "date", "project_code"]
            test_name: Name of the test for logging
            
        Returns:
            True if no duplicates found, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            # Check if all key columns exist
            missing_columns = [col for col in key_columns if col not in df.columns]
            if missing_columns:
                self.testkit.log_fail(
                    test_name = test_name,
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Missing key columns: {missing_columns}",
                    metrics = {"missing_columns": missing_columns}
                )
                return False
            
            # Check for duplicates
            total_rows = len(df)
            unique_rows = df[key_columns].drop_duplicates()
            unique_count = len(unique_rows)
            
            if total_rows != unique_count:
                duplicates = total_rows - unique_count
                self.testkit.log_fail(
                    test_name = test_name,
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {duplicates} duplicate records based on key columns {key_columns}",
                    metrics = {
                        "total_rows": total_rows,
                        "unique_rows": unique_count,
                        "duplicates": duplicates,
                        "key_columns": key_columns
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name,
                    f"No duplicate records found based on key columns {key_columns}",
                    {
                        "total_rows": total_rows,
                        "unique_rows": unique_count,
                        "key_columns": key_columns
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking duplicate records: {str(e)}")
            return False

    def check_duplicate_records_with_details(self, df: pd.DataFrame, key_columns: List[str], 
                                           test_name: str = "check_duplicate_records_with_details") -> bool:
        """
        Check for duplicate records and provide detailed information about duplicates.
        
        Args:
            df: DataFrame to validate
            key_columns: List of column names that should uniquely identify records
            test_name: Name of the test for logging
            
        Returns:
            True if no duplicates found, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            # Check if all key columns exist
            missing_columns = [col for col in key_columns if col not in df.columns]
            if missing_columns:
                self.testkit.log_fail(
                    test_name = test_name,
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Missing key columns: {missing_columns}",
                    metrics = {"missing_columns": missing_columns}
                )
                return False
            
            # Find duplicates with detailed information
            total_rows = len(df)
            duplicate_mask = df.duplicated(subset=key_columns, keep=False)
            duplicate_count = duplicate_mask.sum()
            
            if duplicate_count > 0:
                # Get duplicate records for detailed reporting
                duplicate_records = df[duplicate_mask].sort_values(key_columns)
                duplicate_groups = duplicate_records.groupby(key_columns).size()
                
                # Create summary of duplicate groups
                duplicate_summary = []
                for key_values, count in duplicate_groups.items():
                    if isinstance(key_values, tuple):
                        key_str = " | ".join([f"{col}={val}" for col, val in zip(key_columns, key_values)])
                    else:
                        key_str = f"{key_columns[0]}={key_values}"
                    duplicate_summary.append(f"{key_str} (appears {count} times)")
                
                self.testkit.log_fail(
                    test_name = test_name,
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {duplicate_count} duplicate records in {len(duplicate_groups)} groups based on key columns {key_columns}",
                    metrics = {
                        "total_rows": total_rows,
                        "duplicate_count": duplicate_count,
                        "duplicate_groups": len(duplicate_groups),
                        "key_columns": key_columns,
                        "duplicate_summary": duplicate_summary[:10]  # Limit to first 10 for brevity
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name,
                    f"No duplicate records found based on key columns {key_columns}",
                    {
                        "total_rows": total_rows,
                        "key_columns": key_columns
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking duplicate records with details: {str(e)}")
            return False
