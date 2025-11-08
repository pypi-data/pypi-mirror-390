"""
Business logic tests for the capacity_tracker_linguists_days_off pipeline.
These tests validate business rules specific to this pipeline's data and operations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any
import sys
from pathlib import Path
import inspect
import os

# Add the project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

from modules.integrated_tests import create_testkit


class CapacityTrackerBusinessTests:
    """Business logic tests for capacity tracker pipeline."""
    
    def __init__(self, testkit=None):
        """
        Initialize CapacityTrackerBusinessTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration. If None, creates a new one.
        """
        if testkit is None:
            self.testkit = create_testkit("adaptria_pulls", "capacity_tracker_linguists_days_off")
        else:
            self.testkit = testkit
    
    def check_consistent_daily_hours_per_person(self, timesheet_df: pd.DataFrame, 
                                              linguists_days_off_df: pd.DataFrame,
                                              test_name: str = "check_consistent_daily_hours_per_person") -> bool:
        """
        Check if submitted hours per week match expected weekly hours for each person.
        
        This business rule validates that each person submits hours that match their
        expected weekly hours from the whoisouttable, checking only the past 8 complete weeks.
        
        The test excludes the current incomplete week and current month entirely since 
        people typically submit timesheets on Fridays. This prevents daily submissions 
        from the current week from skewing the results when working with monthly aggregated data.
        
        For the current month, it only counts business days up to today to provide
        fair expectations. For past months, it uses the full month's business days.
        
        Args:
            timesheet_df: DataFrame with timesheet submission data
            linguists_days_off_df: DataFrame with weekly hours data from whoisouttable
            test_name: Name of the test for logging
            
        Returns:
            True if all people have consistent weekly hours, False otherwise
        """
        try:
            if timesheet_df is None or timesheet_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_timesheet_data", "No timesheet data to validate - check data pipeline")
                return True
            
            if linguists_days_off_df is None or linguists_days_off_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_weekly_hours_data", "No weekly hours data available for comparison - check data pipeline")
                return True
            
            # Get past 8 complete weeks of data (excluding current incomplete week)
            from datetime import datetime, timedelta
            import pandas as pd
            
            # Get the start of the current week (Monday)
            current_date = datetime.now()
            days_since_monday = current_date.weekday()  # Monday = 0, Sunday = 6
            current_week_start = current_date - timedelta(days=days_since_monday)
            current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Go back 8 complete weeks from the start of current week
            eight_weeks_ago_start = current_week_start - timedelta(weeks=8)
            
            # Convert to string format for comparison (YYYY-MM-DD)
            eight_weeks_ago_str = eight_weeks_ago_start.strftime("%Y-%m-%d")
            current_week_start_str = current_week_start.strftime("%Y-%m-%d")
            
            # Filter timesheet data to past 8 complete weeks (exclude current week)
            # Note: We need to convert Submission_Month to actual dates for proper filtering
            recent_timesheet_df = timesheet_df.copy()
            
            # Convert Submission_Month to the first day of the month for comparison
            recent_timesheet_df['Month_Start'] = pd.to_datetime(recent_timesheet_df['Submission_Month'], format='%Y-%m')
            
            # Filter to include only months that fall within our 8-week window
            # We'll include any month that has at least some overlap with our 8-week period
            recent_timesheet_df = recent_timesheet_df[
                (recent_timesheet_df['Month_Start'] >= eight_weeks_ago_str) &
                (recent_timesheet_df['Month_Start'] < current_week_start_str)
            ].copy()
            
            # Always exclude current month data to avoid incomplete week issues
            # Since people typically submit timesheets on Fridays, and we're working with monthly
            # aggregated data, we need to be conservative about the current month to avoid
            # including daily submissions from the current incomplete week
            ## NOTE the language lead dashboards will have an alert view that flags incomplete DAILY submissions anyways, 
            ## so this should be sufficient.
            current_month = current_date.strftime('%Y-%m')
            recent_timesheet_df = recent_timesheet_df[recent_timesheet_df['Submission_Month'] != current_month]
            
            if recent_timesheet_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_recent_data", "No recent timesheet data (past 8 complete weeks) to validate - check data pipeline")
                return True
            
            # Create a mapping of email to expected weekly hours from whoisouttable
            weekly_hours_map = {}
            for _, row in linguists_days_off_df.iterrows():
                email = row.get('Email')
                weekly_hours = row.get('WeeklyHours')
                if email and weekly_hours:
                    weekly_hours_map[email] = weekly_hours
            
            # Group by person and calculate weekly hours consistency
            inconsistent_people = []
            
            for email, person_df in recent_timesheet_df.groupby('email'):
                # Calculate total hours per month for this person
                monthly_hours = person_df.groupby('Submission_Month')['Time_spent'].sum()
                
                # Get expected weekly hours for this person
                expected_weekly_hours = weekly_hours_map.get(email)
                if not expected_weekly_hours:
                    continue  # Skip if no expected hours data
                
                # Check if monthly hours match expected weekly hours (within tolerance)
                person_name = person_df['Resource'].iloc[0] if 'Resource' in person_df.columns else email
                issues = []
                
                for month, actual_hours in monthly_hours.items():
                    # Calculate expected monthly hours based on actual business days in that month
                    month_start = pd.to_datetime(month, format='%Y-%m')
                    month_end = month_start + pd.offsets.MonthEnd(0)
                    
                    # Check if this is the current month (incomplete)
                    current_date = datetime.now()
                    current_month = current_date.strftime('%Y-%m')
                    is_current_month = month == current_month
                    
                    if is_current_month:
                        # For current month: only count business days up to today
                        business_days_to_check = len(pd.date_range(start=month_start, end=current_date, freq='B'))
                        business_days_in_month = len(pd.date_range(start=month_start, end=month_end, freq='B'))
                    else:
                        # For past months: use full month business days
                        business_days_to_check = len(pd.date_range(start=month_start, end=month_end, freq='B'))
                        business_days_in_month = business_days_to_check
                    
                    # Calculate expected monthly hours based on business days to check
                    # Daily hours = Weekly hours / 5 (assuming 5-day work week)
                    daily_hours = expected_weekly_hours / 5
                    expected_monthly_hours = daily_hours * business_days_to_check
                    
                    difference = abs(actual_hours - expected_monthly_hours)
                    
                    # They usually submit every single day for the exact hours they work (7 for almost all of them). Any deviation should be flagged.
                    if difference > 0.01:
                        if is_current_month:
                            issues.append(f"{month}: {actual_hours:.1f}h (expected {expected_monthly_hours:.1f}h, {business_days_to_check}/{business_days_in_month} business days)")
                        else:
                            issues.append(f"{month}: {actual_hours:.1f}h (expected {expected_monthly_hours:.1f}h, {business_days_in_month} business days)")
                
                if issues:
                    inconsistent_people.append({
                        'email': email,
                        'name': person_name,
                        'expected_weekly_hours': expected_weekly_hours,
                        'issues': issues
                    })
            
            if inconsistent_people:
                # Build detailed message with all person information for email display
                sample_people = inconsistent_people[:5]  # Show first 5 as examples
                sample_names = [f"{p['name']} ({p['email']})" for p in sample_people]
                
                if len(inconsistent_people) > 5:
                    sample_text = f"Sample: {', '.join(sample_names)} ... and {len(inconsistent_people) - 5} more"
                else:
                    sample_text = f"People: {', '.join(sample_names)}"
                
                # Create summary message for console/sheet
                summary_message_parts = [f"Found {len(inconsistent_people)} people with inconsistent weekly hours ({sample_text})"]
                
                # Build detailed message with all person information for email display
                detailed_message_parts = [f"Found {len(inconsistent_people)} people with inconsistent weekly hours ({sample_text})"]
                detailed_message_parts.append("")  # Empty line for spacing in email
                detailed_message_parts.append("<b>Detailed Hours Inconsistency Information:</b>")
                for person in inconsistent_people:
                    issues_text = ", ".join(person['issues'])
                    detailed_message_parts.append(
                        f"  • {person['name']} ({person['email']}): Expected {person['expected_weekly_hours']}h/week - Issues: {issues_text}"
                    )
                
                # Format message with HTML tags for email display
                # Note: HTML tags will show literally in console, but that's acceptable since it's one log entry instead of many
                formatted_message = "<br/>".join(detailed_message_parts)
                
                # Log single summary warning instead of individual warnings for each person
                self.testkit.log_warn(
                    test_name,
                    f"{os.path.basename(inspect.getfile(inspect.currentframe()))}-{inspect.currentframe().f_code.co_name}",  # issue_identifier
                    formatted_message,  # Full details formatted for email
                    {
                        "issue_identifier": "hours_inconsistency_summary",
                        "issue_details": formatted_message,
                        "issue_type": "hours_inconsistency",
                        "total_people_with_issues": len(inconsistent_people),
                        "total_people_checked": len(recent_timesheet_df['email'].unique()),
                        "analysis_period": f"{eight_weeks_ago_start.strftime('%Y-%m-%d')} to {current_week_start.strftime('%Y-%m-%d')} (excluding current week)",
                        "people_details": inconsistent_people  # Keep all details in metrics for reference
                    }
                )
                return True  # Warning, not failure
            else:
                self.testkit.log_pass(
                    test_name,
                    f"All {len(recent_timesheet_df['email'].unique())} people have consistent weekly hours (past 8 complete weeks, excluding current month)",
                    {
                        "total_people_checked": len(recent_timesheet_df['email'].unique()),
                        "total_recent_records": len(recent_timesheet_df),
                        "analysis_period": f"{eight_weeks_ago_start.strftime('%Y-%m-%d')} to {current_week_start.strftime('%Y-%m-%d')} (excluding current week and month)"
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name, f"{test_name}_error", f"Error checking weekly hours consistency: {str(e)}")
            return False

    def check_absent_time_thresholds(self, timesheet_df: pd.DataFrame, 
                                   payroll_team_doc: Dict[str, dict] = None,
                                   test_name: str = "check_absent_time_thresholds") -> bool:
        """
        Check if absent times per person YTD do not exceed business thresholds.
        
        Business Rules:
        - Warning if absent time exceeds 20% of total time
        - Only checks active employees (status: "Active")
        
        Args:
            timesheet_df: DataFrame with timesheet submission data
            payroll_team_doc: Dictionary with payroll team data including status
            test_name: Name of the test for logging
            
        Returns:
            True if all people are within acceptable absent time limits, False otherwise
        """
        try:
            if timesheet_df is None or timesheet_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_timesheet_data", "No timesheet data to validate - check data pipeline")
                return True
            
            # Create a mapping of email to status from payroll team data
            active_emails = set()
            if payroll_team_doc:
                for name, info in payroll_team_doc.items():
                    email = info.get('email')
                    status = info.get('status')
                    if email and status == 'Active':
                        active_emails.add(email)
            
            # Filter timesheet data to only include active employees
            if active_emails:
                active_timesheet_df = timesheet_df[timesheet_df['email'].isin(active_emails)].copy()
            else:
                # If no payroll team data provided, check all people (fallback)
                active_timesheet_df = timesheet_df.copy()
            
            if active_timesheet_df.empty:
                self.testkit.log_warn(test_name, f"{test_name}_no_active_data", "No timesheet data for active employees to validate - check data pipeline")
                return True
            
            # Calculate absent time percentages per person (only active employees)
            people_with_warnings = []
            
            for email, person_df in active_timesheet_df.groupby('email'):
                # Separate absent and work time
                absent_df = person_df[person_df['Activity'] == 'Absent']
                work_df = person_df[person_df['Activity'] != 'Absent']
                
                total_absent_hours = absent_df['Time_spent'].sum()
                total_work_hours = work_df['Time_spent'].sum()
                total_hours = total_absent_hours + total_work_hours
                
                if total_hours > 0:  # Only check if person has any time recorded
                    absent_percentage = (total_absent_hours / total_hours) * 100
                    
                    person_name = person_df['Resource'].iloc[0] if 'Resource' in person_df.columns else email
                    
                    # Get threshold from config
                    warn_threshold = self.testkit.get_threshold(
                        f"{test_name}.warn_threshold_percentage", 20
                    )
                    
                    if absent_percentage > warn_threshold:  # Warning threshold only
                        people_with_warnings.append({
                            'email': email,
                            'name': person_name,
                            'absent_percentage': round(absent_percentage, 1),
                            'absent_hours': round(total_absent_hours, 1),
                            'total_hours': round(total_hours, 1)
                        })
            
            if people_with_warnings:
                # Build summary message for console/sheet
                sample_people = people_with_warnings[:5]  # Show first 5 as examples
                sample_names = [f"{p['name']} ({p['email']})" for p in sample_people]
                
                if len(people_with_warnings) > 5:
                    sample_text = f"Sample: {', '.join(sample_names)} ... and {len(people_with_warnings) - 5} more"
                else:
                    sample_text = f"People: {', '.join(sample_names)}"
                
                # Build detailed message with all person information for email display
                detailed_message_parts = [f"Found {len(people_with_warnings)} people exceeding absent time threshold ({sample_text})"]
                detailed_message_parts.append("")  # Empty line for spacing in email
                detailed_message_parts.append("<b>Detailed Absent Time Threshold Information:</b>")
                for person in people_with_warnings:
                    detailed_message_parts.append(
                        f"  • {person['name']} ({person['email']}): {person['absent_percentage']}% absent ({person['absent_hours']}h/{person['total_hours']}h) - exceeds {warn_threshold}% threshold"
                    )
                
                # Format message with HTML tags for email display
                # Note: HTML tags will show literally in console, but that's acceptable since it's one log entry instead of many
                formatted_message = "<br/>".join(detailed_message_parts)
                
                # Log single summary warning instead of individual warnings for each person
                self.testkit.log_warn(
                    test_name,
                    f"{os.path.basename(inspect.getfile(inspect.currentframe()))}-{inspect.currentframe().f_code.co_name}",  # issue_identifier
                    formatted_message,  # Full details formatted for email
                    {
                        "issue_details": formatted_message,
                        "issue_name": "Absent Time Threshold Summary",
                        "issue_type": "absent_threshold",
                        "threshold_percentage": warn_threshold,
                        "threshold_source": "pipeline_config" if warn_threshold != 20 else "default",
                        "total_people_with_warnings": len(people_with_warnings),
                        "total_active_people_checked": len(active_timesheet_df['email'].unique()),
                        "total_people_in_data": len(timesheet_df['email'].unique()),
                        "people_details": people_with_warnings  # Keep all details in metrics for reference
                    }
                )
                return True
            
            else:
                self.testkit.log_pass(
                    test_name,
                    f"All {len(active_timesheet_df['email'].unique())} active people are within acceptable absent time limits (≤{warn_threshold}%)",
                    {
                        "total_active_people_checked": len(active_timesheet_df['email'].unique()),
                        "total_people_in_data": len(timesheet_df['email'].unique()),
                        "total_records": len(active_timesheet_df),
                        "threshold_percentage": warn_threshold,
                        "threshold_source": "pipeline_config" if warn_threshold != 20 else "default"
                    }
                )
                return True
                
        except Exception as e:
            self.testkit.log_fail(test_name, f"{test_name}_error", f"Error checking absent time thresholds: {str(e)}")
            return False

    def run_all_business_checks(self, timesheet_df: pd.DataFrame, linguists_days_off_df: pd.DataFrame) -> Dict[str, bool]:
        """
        Run all business logic checks for the capacity tracker pipeline.
        
        Args:
            timesheet_df: DataFrame with timesheet submission data
            linguists_days_off_df: DataFrame with weekly hours data from whoisouttable
            
        Returns:
            Dict[str, bool]: Results of all business checks
        """
        results = {}
        
        # Run daily hours consistency check
        results['daily_hours_consistent'] = self.check_consistent_daily_hours_per_person(timesheet_df, linguists_days_off_df)
        
        # Run absent time threshold check
        results['absent_time_acceptable'] = self.check_absent_time_thresholds(timesheet_df)
        
        return results


