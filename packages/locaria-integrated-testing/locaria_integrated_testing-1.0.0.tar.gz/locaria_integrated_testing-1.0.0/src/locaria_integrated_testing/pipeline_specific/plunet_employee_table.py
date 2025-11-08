"""
Business logic tests for the plunet_employee_table pipeline.
These tests validate business rules specific to this pipeline's data and operations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from modules.integrated_tests import create_testkit

class PlunetEmployeeTableBusinessTests:
    """Business logic tests for plunet employee table pipeline."""
    
    def __init__(self, testkit=None):
        """
        Initialize PlunetEmployeeTableBusinessTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration. If None, creates a new one.
        """
        if testkit is None:
            self.testkit = create_testkit("adaptria_pulls", "plunet_employee_table")
        else:
            self.testkit = testkit
    
    def check_duplicate_employee_records(self, employee_df: pd.DataFrame, 
                                       test_name: str = "check_duplicate_employee_records") -> bool:
        """
        Check if there are duplicate employee records based on email address.
        
        This business rule validates that each employee email should have only one record
        in the Plunet employee table. Duplicates indicate data quality issues that need
        manual resolution in the source system.
        
        Args:
            employee_df: DataFrame with employee data from Plunet
            test_name: Name of the test for logging
            
        Returns:
            True if no duplicates found or if duplicates are acknowledged, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name, f"{test_name}_disabled", "Business logic checks disabled - validation skipped")
                return True
            
            if employee_df is None or employee_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_data", "No employee data to validate - check data pipeline")
                return True
            
            # Check if PlunetEmail column exists
            if 'PlunetEmail' not in employee_df.columns:
                self.testkit.log_fail(test_name, f"{test_name}_missing_column", "PlunetEmail column not found in employee data")
                return False
            
            # Check for duplicates based on email
            total_rows = len(employee_df)
            unique_emails = employee_df['PlunetEmail'].nunique()
            
            if total_rows != unique_emails:
                duplicates = total_rows - unique_emails
                
                # Get detailed information about duplicates
                duplicate_emails = employee_df[employee_df.duplicated(subset=['PlunetEmail'], keep=False)]
                duplicate_email_list = duplicate_emails['PlunetEmail'].unique().tolist()
                
                # Create detailed breakdown of duplicates (for metrics only, not individual logging)
                duplicate_details = []
                for email in duplicate_email_list:
                    email_records = employee_df[employee_df['PlunetEmail'] == email]
                    record_count = len(email_records)
                    
                    # Get status variations for this email
                    statuses = email_records['PlunetEmployeeStatus'].unique().tolist() if 'PlunetEmployeeStatus' in email_records.columns else ['N/A']
                    employment_types = email_records['PlunetEmploymentType'].unique().tolist() if 'PlunetEmploymentType' in email_records.columns else ['N/A']
                    
                    duplicate_details.append({
                        'email': email,
                        'record_count': record_count,
                        'statuses': statuses,
                        'employment_types': employment_types,
                        'employee_ids': email_records['PlunetEmployeeID'].tolist() if 'PlunetEmployeeID' in email_records.columns else []
                    })
                
                # Create summary message with detailed breakdown for email display
                sample_emails = [d['email'] for d in duplicate_details[:5]]  # Show first 5 as examples
                if len(duplicate_email_list) > 5:
                    sample_text = f"Sample duplicates: {', '.join(sample_emails)} ... and {len(duplicate_email_list) - 5} more"
                else:
                    sample_text = f"Duplicate emails: {', '.join(sample_emails)}"
                
                # Build detailed message with all duplicate information for email
                detailed_message_parts = [f"Found {duplicates} duplicate records across {len(duplicate_email_list)} email addresses ({sample_text})"]
                detailed_message_parts.append("")  # Empty line for spacing in email
                detailed_message_parts.append("<b>Detailed Duplicate Information:</b>")
                for detail in duplicate_details:
                    email = detail['email']
                    record_count = detail['record_count']
                    statuses = ', '.join(detail['statuses'])
                    employee_ids = ', '.join(map(str, detail['employee_ids']))
                    detailed_message_parts.append(f"  • {email}: {record_count} records (Statuses: {statuses}, IDs: {employee_ids})")
                
                # Format message with HTML tags for email display
                # Note: HTML tags will show literally in console, but that's acceptable since it's one log entry instead of 40
                formatted_message = "<br/>".join(detailed_message_parts)
                
                self.testkit.log_warn(
                    test_name,
                    "duplicate_employee_records_summary",  # issue_identifier
                    formatted_message,  # Full details formatted for email
                    {
                        "issue_identifier": "duplicate_employee_records_summary",
                        "issue_name": "Duplicate Employee Records Summary",
                        "issue_type": "duplicate_employee_records",
                        "issue_key": "duplicate_employee_records_summary",
                        "total_duplicates": duplicates,
                        "total_duplicate_emails": len(duplicate_email_list),
                        "total_records": total_rows,
                        "unique_emails": unique_emails,
                        "duplicate_details": duplicate_details  # Keep details in metrics for reference
                    }
                )
                
                return True  # Warning, not failure - allows pipeline to continue
            
            else:
                self.testkit.log_pass(
                    test_name,
                    f"No duplicate employee records found - {total_rows} records for {unique_emails} unique emails",
                    {
                        "total_records": total_rows,
                        "unique_emails": unique_emails
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name, f"{test_name}_error", f"Error checking duplicate employee records: {str(e)}")
            return False

    def check_employee_data_quality(self, employee_df: pd.DataFrame, 
                                  test_name: str = "check_employee_data_quality") -> bool:
        """
        Check data quality issues in employee records.
        
        This business rule validates that employee records have required fields
        and reasonable data values.
        
        Args:
            employee_df: DataFrame with employee data from Plunet
            test_name: Name of the test for logging
            
        Returns:
            True if data quality is acceptable, False otherwise
        """
        try:
            if not self.testkit.is_test_enabled('enable_business_logic_checks'):
                self.testkit.log_warn(test_name, f"{test_name}_disabled", "Business logic checks disabled - validation skipped")
                return True
            
            if employee_df is None or employee_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_data", "No employee data to validate - check data pipeline")
                return True
            
            issues = []
            
            # Check for missing emails
            if 'PlunetEmail' in employee_df.columns:
                missing_emails = employee_df['PlunetEmail'].isna().sum()
                if missing_emails > 0:
                    issues.append(f"{missing_emails} records with missing email addresses")
            
            # Check for missing employee IDs
            if 'PlunetEmployeeID' in employee_df.columns:
                missing_ids = employee_df['PlunetEmployeeID'].isna().sum()
                if missing_ids > 0:
                    issues.append(f"{missing_ids} records with missing employee IDs")
            
            # Check for missing employee names
            if 'PlunetEmployeeName' in employee_df.columns:
                missing_names = employee_df['PlunetEmployeeName'].isna().sum()
                if missing_names > 0:
                    issues.append(f"{missing_names} records with missing employee names")
            
            # Check for invalid email formats (basic ̈¨check)
            if 'PlunetEmail' in employee_df.columns:
                invalid_emails = employee_df[
                    (employee_df['PlunetEmail'].notna()) & 
                    (~employee_df['PlunetEmail'].str.contains('@', na=False))
                ]
                if len(invalid_emails) > 0:
                    issues.append(f"{len(invalid_emails)} records with invalid email format")
            
            if issues:
                # Log warning for data quality issues
                self.testkit.log_warn(
                    test_name,
                    "employee_data_quality",  # issue_identifier
                    f"Data quality issues found: {'; '.join(issues)}",
                    {
                        "issue_identifier": "employee_data_quality",
                        "issue_type": "data_quality",
                        "issue_key": "employee_data_quality",
                        "issues": issues,
                        "total_records": len(employee_df)
                    }
                )
                return True  # Warning, not failure
            
            else:
                self.testkit.log_pass(
                    test_name,
                    f"Employee data quality is good - {len(employee_df)} records validated",
                    {
                        "total_records": len(employee_df)
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name, f"{test_name}_error", f"Error checking employee data quality: {str(e)}")
            return False

    def run_all_business_checks(self, employee_df: pd.DataFrame, stop_pipeline: bool = False) -> Dict[str, bool]:
        """
        Run all business logic checks for the plunet employee table pipeline.
        
        Args:
            employee_df: DataFrame with employee data from Plunet
            stop_pipeline: If True, stop pipeline on failure. If False, continue.
            
        Returns:
            Dict[str, bool]: Results of all business checks
        """
        results = {}
        
        # Run duplicate employee records check
        results['duplicate_employee_records'] = self.check_duplicate_employee_records(employee_df)
        
        # Run data quality check
        results['employee_data_quality'] = self.check_employee_data_quality(employee_df)
        
        return results
