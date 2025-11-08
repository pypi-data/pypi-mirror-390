"""
Data quality tests for common data validation scenarios.
Tests include row count validation, numeric range checks, and duplicate detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import inspect, os
from ..main.testkit import TestKit

class DataQualityTests:
    """Data quality tests for common validation scenarios."""
    
    def __init__(self, testkit: TestKit, caller_script: Optional[str] = None): 
        """
        Initialize DataQualityTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration
        """
        self.testkit = testkit

        # Set caller script for easier identification in logs
        self.caller_script = caller_script if caller_script else os.path.basename(inspect.getfile(inspect.currentframe()))
    
    #########################################################################################
    def check_numeric_ranges(self, df: pd.DataFrame, column_ranges: Dict[str, Tuple[float, float]] = None, 
                           test_name: str = "check_numeric_ranges") -> bool:
        """
        Check that numeric columns contain values within expected ranges.
        
        Args:
            df: DataFrame to validate
            column_ranges: Dictionary mapping column names to (min, max) tuples (if None, uses config)
            test_name: Name of the test for logging
            
        Returns:
            True if all numeric values are within ranges, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            # Get ranges from config if not provided
            if column_ranges is None:
                config_ranges = self.testkit.get_threshold(f"{test_name}.numeric_ranges", {})
                if not config_ranges:
                    self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "No numeric ranges configured and none provided")
                    return False
                
                # Convert config format to tuple format
                column_ranges = {}
                for column, range_config in config_ranges.items():
                    if 'min' in range_config and 'max' in range_config:
                        column_ranges[column] = (range_config['min'], range_config['max'])
            
            range_violations = []
            detailed_violations = []
            
            for column, (min_val, max_val) in column_ranges.items():
                if column not in df.columns:
                    range_violations.append(f"{column}: column not found")
                    continue
                
                # Check for non-numeric values
                if not pd.api.types.is_numeric_dtype(df[column]):
                    range_violations.append(f"{column}: column is not numeric")
                    continue
                
                # Check range violations
                below_min = df[df[column] < min_val]
                above_max = df[df[column] > max_val]
                
                if len(below_min) > 0:
                    range_violations.append(f"{column}: {len(below_min)} values below {min_val}")
                    # Add detailed information for below_min violations
                    for idx, row in below_min.iterrows():
                        name = row.get('Name', 'Unknown')
                        email = row.get('Email', 'Unknown')
                        month = row.get('ReportingMonth', 'Unknown')
                        value = float(row[column])  # Convert to float for JSON serialization
                        detailed_violations.append(f"{name} ({email}) in {month}: {value} (below {min_val})")
                
                if len(above_max) > 0:
                    range_violations.append(f"{column}: {len(above_max)} values above {max_val}")
                    # Add detailed information for above_max violations
                    for idx, row in above_max.iterrows():
                        name = row.get('Name', 'Unknown')
                        email = row.get('Email', 'Unknown')
                        month = row.get('ReportingMonth', 'Unknown')
                        value = float(row[column])  # Convert to float for JSON serialization
                        detailed_violations.append(f"{name} ({email}) in {month}: {value} (above {max_val})")
            
            if range_violations:
                # Create detailed message with line breaks
                detailed_summary = "<br/>".join(detailed_violations[:10])  # Limit to first 10 for readability
                if len(detailed_violations) > 10:
                    detailed_summary += f"<br/>... and {len(detailed_violations) - 10} more violations"
                
                self.testkit.log_warn(
                    test_name = test_name,
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Numeric range violations detected:<br/>{detailed_summary}",
                    metrics = {
                        "range_violations": range_violations, 
                        "total_checked": int(len(column_ranges)),  # Convert to int
                        "violation_count": int(len(detailed_violations)),  # Convert to int
                        "detailed_violations": detailed_violations[:20],  # Limit for JSON serialization
                        "threshold_source": "pipeline_config" if column_ranges != {} else "provided"
                    }
                )
                return True  # Warning, not failure
            else:
                self.testkit.log_pass(
                    test_name,
                    f"All {len(column_ranges)} numeric columns within expected ranges",
                    {
                        "column_ranges": column_ranges,
                        "threshold_source": "pipeline_config" if column_ranges != {} else "provided"
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking numeric ranges: {str(e)}")
            return False
    
    #########################################################################################
    def check_data_completeness(self, df: pd.DataFrame, completeness_threshold: float = None, 
                               test_name: str = "check_data_completeness") -> bool:
        """
        Check that data completeness is above a threshold.
        
        Args:
            df: DataFrame to validate
            completeness_threshold: Minimum percentage of non-null values required (if None, uses config)
            test_name: Name of the test for logging
            
        Returns:
            True if data completeness is above threshold, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            # Get threshold from config if not provided
            if completeness_threshold is None:
                completeness_threshold = self.testkit.get_threshold(
                    f"{test_name}.completeness_threshold", 0.95
                )
            
            total_cells = df.size
            null_cells = df.isnull().sum().sum()
            completeness = (total_cells - null_cells) / total_cells
            
            if completeness < completeness_threshold:
                self.testkit.log_fail(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Data completeness {completeness:.2%} below threshold {completeness_threshold:.2%}",
                    metrics = {
                        "completeness": float(completeness),
                        "threshold": float(completeness_threshold),
                        "total_cells": int(total_cells),
                        "null_cells": int(null_cells),
                        "threshold_source": "pipeline_config" if completeness_threshold != 0.95 else "default"
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name,
                    f"Data completeness {completeness:.2%} above threshold {completeness_threshold:.2%}",
                    {
                        "completeness": float(completeness),
                        "threshold": float(completeness_threshold),
                        "total_cells": int(total_cells),
                        "null_cells": int(null_cells),
                        "threshold_source": "pipeline_config" if completeness_threshold != 0.95 else "default"
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking data completeness: {str(e)}")
            return False
    
#########################################################################################
    def check_column_completeness(self, df: pd.DataFrame, 
                                columns: Union[str, List[str]], 
                                completeness_threshold: float = None,
                                test_name: str = "check_column_completeness") -> bool:
        """
        Check that data completeness in specified columns is above a threshold.
        
        Args:
            df: DataFrame to validate
            columns: Single column name or list of column names to check
            completeness_threshold: Minimum percentage of non-null values required (if None, uses config)
            test_name: Name of the test for logging
            
        Returns:
            True if data completeness in all specified columns is above threshold, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
                
            # Convert single column to list
            if isinstance(columns, str):
                columns = [columns]
                
            # Validate column existence
            missing_columns = [col for col in columns if col not in df.columns]
            if missing_columns:
                self.testkit.log_fail(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", 
                    message = f"Columns not found in DataFrame: {missing_columns}"
                )
                return False
            
            # Get threshold from config if not provided
            if completeness_threshold is None:
                completeness_threshold = self.testkit.get_threshold(
                    f"{test_name}.completeness_threshold", 0.95
                )
            
            # Calculate completeness for each column
            results = {}
            violations = []
            
            for column in columns:
                total_rows = len(df)
                null_count = df[column].isnull().sum()
                completeness = (total_rows - null_count) / total_rows
                
                results[column] = {
                    "completeness": float(completeness),
                    "total_rows": int(total_rows),
                    "null_count": int(null_count)
                }
                
                if completeness < completeness_threshold:
                    violations.append(f"{column}: {completeness:.2%} complete ({null_count} nulls)")
            
            if violations:
                self.testkit.log_fail(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Column completeness below threshold {completeness_threshold:.2%}: {violations}",
                    metrics = {
                        "results": results,
                        "threshold": float(completeness_threshold),
                        "violations": violations,
                        "threshold_source": "pipeline_config" if completeness_threshold != 0.95 else "default"
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name,
                    f"All specified columns above completeness threshold {completeness_threshold:.2%}",
                    {
                        "results": results,
                        "threshold": float(completeness_threshold),
                        "threshold_source": "pipeline_config" if completeness_threshold != 0.95 else "default"
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking column completeness: {str(e)}")
            return False
    
    #########################################################################################    
    def check_date_ranges(self, df: pd.DataFrame, date_columns: Dict[str, Dict[str, Any]], 
                         test_name: str = "check_date_ranges") -> bool:
        """
        Check that date columns contain values within expected ranges.
        
        Args:
            df: DataFrame to validate
            date_columns: Dictionary mapping column names to date validation rules
                         Rules can include: 'min_date', 'max_date', 'future_allowed'
            test_name: Name of the test for logging
            
        Returns:
            True if all date values are within ranges, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Business logic checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            date_violations = []
            
            for column, rules in date_columns.items():
                if column not in df.columns:
                    date_violations.append(f"{column}: column not found")
                    continue
                
                # Convert to datetime if not already
                try:
                    date_series = pd.to_datetime(df[column], errors='coerce')
                except Exception:
                    date_violations.append(f"{column}: cannot convert to datetime")
                    continue
                
                # Check for invalid dates
                invalid_dates = date_series.isnull().sum()
                if invalid_dates > 0:
                    date_violations.append(f"{column}: {invalid_dates} invalid dates")
                
                # Check minimum date
                if 'min_date' in rules:
                    min_date = pd.to_datetime(rules['min_date'])
                    below_min = date_series[date_series < min_date]
                    if len(below_min) > 0:
                        date_violations.append(f"{column}: {len(below_min)} dates before {min_date}")
                
                # Check maximum date
                if 'max_date' in rules:
                    max_date = pd.to_datetime(rules['max_date'])
                    above_max = date_series[date_series > max_date]
                    if len(above_max) > 0:
                        date_violations.append(f"{column}: {len(above_max)} dates after {max_date}")
                
                # Check future dates
                if not rules.get('future_allowed', True):
                    now = pd.Timestamp.now()
                    future_dates = date_series[date_series > now]
                    if len(future_dates) > 0:
                        date_violations.append(f"{column}: {len(future_dates)} future dates found")
            
            if date_violations:
                self.testkit.log_fail(
                    test_name = test_name, 
                    issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Date range violations: {date_violations}",
                    metrics = {"date_violations": date_violations, "total_checked": len(date_columns)}
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name,
                    f"All {len(date_columns)} date columns within expected ranges",
                    {"date_columns": date_columns}
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking date ranges: {str(e)}")
            return False
    