"""
Data freshness tests for ensuring data is up-to-date and timely.
Tests include timestamp validation, partition freshness, and data age checks.
"""

import pandas as pd
import inspect, os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from ..main.testkit import TestKit


class FreshnessTests:
    """Data freshness tests for ensuring data is up-to-date and timely."""
    
    def __init__(self, testkit: TestKit, caller_script: Optional[str] = None):
        """
        Initialize FreshnessTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration
        """
        self.testkit = testkit
    
        # Set caller script for easier identification in logs
        self.caller_script = caller_script if caller_script else os.path.basename(inspect.getfile(inspect.currentframe()))

    def check_data_freshness(self, df: pd.DataFrame, timestamp_column: str, 
                           max_age_hours: int = None, test_name: str = "check_data_freshness") -> bool:
        """
        Check that data is fresh based on timestamp column.
        
        Args:
            df: DataFrame to validate
            timestamp_column: Name of the column containing timestamps
            max_age_hours: Maximum age in hours (uses config if not provided)
            test_name: Name of the test for logging
            
        Returns:
            True if data is fresh, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_freshness_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Freshness checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            if timestamp_column not in df.columns:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Timestamp column '{timestamp_column}' not found")
                return False
            
            # Get max age from config if not provided
            if max_age_hours is None:
                max_age_hours = self.testkit.get_threshold('data_freshness', 'max_age_hours', 24)
            
            # Convert timestamp column to datetime
            try:
                timestamps = pd.to_datetime(df[timestamp_column], errors='coerce')
            except Exception as e:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error converting timestamps: {str(e)}")
                return False
            
            # Check for invalid timestamps
            invalid_timestamps = timestamps.isnull().sum()
            if invalid_timestamps > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {invalid_timestamps} invalid timestamps in column '{timestamp_column}'",
                    metrics = {"invalid_timestamps": invalid_timestamps, "timestamp_column": timestamp_column}
                )
                return False
            
            # Check data age
            now = datetime.now(timezone.utc)
            max_age = timedelta(hours=max_age_hours)
            
            # Find the most recent timestamp
            latest_timestamp = timestamps.max()
            if latest_timestamp.tzinfo is None:
                latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
            
            data_age = now - latest_timestamp
            
            if data_age > max_age:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Data is {data_age} old (max allowed: {max_age})",
                    metrics = {
                        "data_age_hours": data_age.total_seconds() / 3600,
                        "max_age_hours": max_age_hours,
                        "latest_timestamp": latest_timestamp.isoformat(),
                        "timestamp_column": timestamp_column
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Data is fresh (age: {data_age}, max allowed: {max_age})",
                    metrics = {
                        "data_age_hours": data_age.total_seconds() / 3600,
                        "max_age_hours": max_age_hours,
                        "latest_timestamp": latest_timestamp.isoformat(),
                        "timestamp_column": timestamp_column
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking data freshness: {str(e)}")
            return False
    
    def check_timestamp_progression(self, df: pd.DataFrame, timestamp_column: str, 
                                  test_name: str = "check_timestamp_progression") -> bool:
        """
        Check that timestamps are progressing forward (no future timestamps).
        
        Args:
            df: DataFrame to validate
            timestamp_column: Name of the column containing timestamps
            test_name: Name of the test for logging
            
        Returns:
            True if timestamps are progressing correctly, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_freshness_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Freshness checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            if timestamp_column not in df.columns:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Timestamp column '{timestamp_column}' not found")
                return False
            
            # Convert timestamp column to datetime
            try:
                timestamps = pd.to_datetime(df[timestamp_column], errors='coerce')
            except Exception as e:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error converting timestamps: {str(e)}")
                return False
            
            # Check for invalid timestamps
            invalid_timestamps = timestamps.isnull().sum()
            if invalid_timestamps > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {invalid_timestamps} invalid timestamps",
                    metrics = {"invalid_timestamps": invalid_timestamps, "timestamp_column": timestamp_column}
                )
                return False
            
            # Check for future timestamps
            now = datetime.now(timezone.utc)
            future_timestamps = timestamps[timestamps > now]
            
            if len(future_timestamps) > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {len(future_timestamps)} future timestamps",
                    metrics = {
                        "future_timestamps": len(future_timestamps),
                        "timestamp_column": timestamp_column,
                        "max_future_timestamp": future_timestamps.max().isoformat()
                    }
                )
                return False
            else:
                self.testkit.log_pass(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"No future timestamps found in column '{timestamp_column}'",
                    metrics = {
                        "total_timestamps": len(timestamps),
                        "timestamp_column": timestamp_column,
                        "latest_timestamp": timestamps.max().isoformat()
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking timestamp progression: {str(e)}")
            return False
    
    def check_data_consistency(self, df: pd.DataFrame, timestamp_column: str, 
                             expected_frequency: str = None, test_name: str = "check_data_consistency") -> bool:
        """
        Check that data is consistent in terms of frequency and gaps.
        
        Args:
            df: DataFrame to validate
            timestamp_column: Name of the column containing timestamps
            expected_frequency: Expected frequency (e.g., 'D' for daily, 'H' for hourly)
            test_name: Name of the test for logging
            
        Returns:
            True if data is consistent, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_freshness_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Freshness checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            if timestamp_column not in df.columns:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Timestamp column '{timestamp_column}' not found")
                return False
            
            # Convert timestamp column to datetime
            try:
                timestamps = pd.to_datetime(df[timestamp_column], errors='coerce')
            except Exception as e:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error converting timestamps: {str(e)}")
                return False
            
            # Check for invalid timestamps
            invalid_timestamps = timestamps.isnull().sum()
            if invalid_timestamps > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {invalid_timestamps} invalid timestamps",
                    metrics = {"invalid_timestamps": invalid_timestamps, "timestamp_column": timestamp_column}
                )
                return False
            
            # Sort timestamps
            timestamps_sorted = timestamps.sort_values()
            
            # Check for duplicate timestamps
            duplicate_timestamps = timestamps_sorted.duplicated().sum()
            if duplicate_timestamps > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {duplicate_timestamps} duplicate timestamps",
                    metrics = {"duplicate_timestamps": duplicate_timestamps, "timestamp_column": timestamp_column}
                )
                return False
            
            # Check frequency if specified
            if expected_frequency:
                # Create expected date range
                start_date = timestamps_sorted.min()
                end_date = timestamps_sorted.max()
                expected_range = pd.date_range(start=start_date, end=end_date, freq=expected_frequency)
                
                # Find missing timestamps
                missing_timestamps = set(expected_range) - set(timestamps_sorted)
                
                if len(missing_timestamps) > 0:
                    self.testkit.log_warn(
                        test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                        message = f"Found {len(missing_timestamps)} missing timestamps for frequency '{expected_frequency}'",
                        metrics = {
                            "missing_timestamps": len(missing_timestamps),
                            "expected_frequency": expected_frequency,
                            "timestamp_column": timestamp_column,
                            "date_range": f"{start_date} to {end_date}"
                        }
                    )
                else:
                    self.testkit.log_pass(
                        test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                        message = f"All expected timestamps present for frequency '{expected_frequency}'",
                        metrics = {
                            "expected_frequency": expected_frequency,
                            "timestamp_column": timestamp_column,
                            "total_timestamps": len(timestamps_sorted),
                            "date_range": f"{start_date} to {end_date}"
                        }
                    )
            else:
                self.testkit.log_pass(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Timestamp consistency checked (no frequency specified)",
                    metrics = {
                        "timestamp_column": timestamp_column,
                        "total_timestamps": len(timestamps_sorted),
                        "date_range": f"{timestamps_sorted.min()} to {timestamps_sorted.max()}"
                    }
                )
            
            return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking data consistency: {str(e)}")
            return False
    
    def check_partition_freshness(self, project_id: str, dataset_id: str, table_id: str, 
                                partition_column: str = None, test_name: str = "check_partition_freshness") -> bool:
        """
        Check that BigQuery table partitions are fresh.
        
        Args:
            project_id: BigQuery project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            partition_column: Partition column name (optional)
            test_name: Name of the test for logging
            
        Returns:
            True if partitions are fresh, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_freshness_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Freshness checks disabled - validation skipped")
                return True
            
            # This would require BigQuery client integration
            # For now, we'll log a warning that this feature needs implementation
            self.testkit.log_warn(
                test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                message = "Partition freshness check not yet implemented - requires BigQuery client integration",
                metrics = {
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "table_id": table_id,
                    "partition_column": partition_column
                }
            )
            return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking partition freshness: {str(e)}")
            return False
    
    def check_data_age_distribution(self, df: pd.DataFrame, timestamp_column: str, 
                                  test_name: str = "check_data_age_distribution") -> bool:
        """
        Check the distribution of data ages to identify potential issues.
        
        Args:
            df: DataFrame to validate
            timestamp_column: Name of the column containing timestamps
            test_name: Name of the test for logging
            
        Returns:
            True if data age distribution is acceptable, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_freshness_checks'):
                self.testkit.log_warn(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "Freshness checks disabled - validation skipped")
                return True
            
            if df is None or df.empty:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = "DataFrame is None or empty")
                return False
            
            if timestamp_column not in df.columns:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Timestamp column '{timestamp_column}' not found")
                return False
            
            # Convert timestamp column to datetime
            try:
                timestamps = pd.to_datetime(df[timestamp_column], errors='coerce')
            except Exception as e:
                self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error converting timestamps: {str(e)}")
                return False
            
            # Check for invalid timestamps
            invalid_timestamps = timestamps.isnull().sum()
            if invalid_timestamps > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {invalid_timestamps} invalid timestamps",
                    metrics = {"invalid_timestamps": invalid_timestamps, "timestamp_column": timestamp_column}
                )
                return False
            
            # Calculate data ages
            now = datetime.now(timezone.utc)
            data_ages = now - timestamps
            
            # Convert to hours for analysis
            ages_hours = data_ages.dt.total_seconds() / 3600
            
            # Calculate statistics
            min_age = ages_hours.min()
            max_age = ages_hours.max()
            mean_age = ages_hours.mean()
            median_age = ages_hours.median()
            
            # Check for very old data
            warn_age_hours = self.testkit.get_threshold('data_freshness', 'warn_age_hours', 12)
            max_age_hours = self.testkit.get_threshold('data_freshness', 'max_age_hours', 24)
            
            old_data_count = (ages_hours > max_age_hours).sum()
            warn_data_count = (ages_hours > warn_age_hours).sum()
            
            if old_data_count > 0:
                self.testkit.log_fail(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {old_data_count} records older than {max_age_hours} hours",
                    metrics = {
                        "old_data_count": old_data_count,
                        "max_age_hours": max_age_hours,
                        "min_age_hours": min_age,
                        "max_age_hours_actual": max_age,
                        "mean_age_hours": mean_age,
                        "median_age_hours": median_age
                    }
                )
                return False
            elif warn_data_count > 0:
                self.testkit.log_warn(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Found {warn_data_count} records older than {warn_age_hours} hours",
                    metrics = {
                        "warn_data_count": warn_data_count,
                        "warn_age_hours": warn_age_hours,
                        "min_age_hours": min_age,
                        "max_age_hours": max_age,
                        "mean_age_hours": mean_age,
                        "median_age_hours": median_age
                    }
                )
            else:
                self.testkit.log_pass(
                    test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}",
                    message = f"Data age distribution is acceptable",
                    metrics = {
                        "min_age_hours": min_age,
                        "max_age_hours": max_age,
                        "mean_age_hours": mean_age,
                        "median_age_hours": median_age,
                        "total_records": len(ages_hours)
                    }
                )
            
            return True
                
        except Exception as e:
            self.testkit.log_fail(test_name = test_name, issue_identifier = f"{self.caller_script}-{inspect.currentframe().f_code.co_name}", message = f"Error checking data age distribution: {str(e)}")
            return False

