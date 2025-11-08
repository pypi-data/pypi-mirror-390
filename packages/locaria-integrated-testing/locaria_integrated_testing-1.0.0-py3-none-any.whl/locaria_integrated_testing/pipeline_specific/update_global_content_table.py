"""
Pipeline-specific business logic tests for update_global_content_table.py

This module contains business logic tests specific to the Global Content team's
Firestore resource overview update pipeline. These tests check for data quality
issues that indicate problems in the source systems that need manual fixing.
"""

import pandas as pd
from modules.integrated_tests.main.testkit import TestKit


class GlobalContentTableBusinessTests:
    """
    Business logic tests for the Global Content table update pipeline.
    
    These tests run on RAW data before any filtering or processing to detect
    system-level issues that need manual intervention.
    """
    
    def __init__(self, testkit=None):
        """
        Initialize GlobalContentTableBusinessTests with a TestKit instance.
        
        Args:
            testkit: TestKit instance for logging and configuration. If None, creates a new one.
        """
        if testkit is None:
            from modules.integrated_tests import create_testkit
            self.testkit = create_testkit("adaptria_pulls", "update_global_content_table")
        else:
            self.testkit = testkit
    
    def check_plunet_duplicate_emails(self, df_plunet_raw: pd.DataFrame):
        """
        Check for duplicate PlunetEmail entries in the raw Plunet data.
        
        This test warns about duplicate emails before deduplication, indicating
        potential data quality issues in the source system.
        
        Args:
            df_plunet_raw: Raw DataFrame from Plunet employee table before deduplication
        """
        test_name = "check_plunet_duplicate_emails"
        
        if df_plunet_raw.empty:
            self.testkit.log_warn(test_name, "No Plunet data to check for duplicates")
            return
        
        if 'PlunetEmail' not in df_plunet_raw.columns:
            self.testkit.log_fail(test_name, "PlunetEmail column not found in data")
            return
        
        # Check for duplicates
        duplicates = df_plunet_raw.duplicated(subset=['PlunetEmail'], keep=False)
        duplicate_count = duplicates.sum()
        
        if duplicate_count > 0:
            duplicate_emails = df_plunet_raw[duplicates]['PlunetEmail'].unique()
            
            # Create detailed report of duplicates
            duplicate_details = []
            for email in duplicate_emails:
                email_records = df_plunet_raw[df_plunet_raw['PlunetEmail'] == email]
                record_count = len(email_records)
                
                # Get details for each duplicate record
                records_info = []
                for idx, row in email_records.iterrows():
                    record_info = f"ID='{row.get('PlunetEmployeeID', 'N/A')}', Name='{row.get('PlunetEmployeeName', 'N/A')}'"
                    records_info.append(record_info)
                
                duplicate_details.append(f"Email: {email}\nNumber of records: {record_count}\n  " + 
                                       "\n  ".join([f"Record {idx}: {info}" for idx, info in enumerate(records_info, 1)]))
            
            warning_message = (
                f"Found {duplicate_count} duplicate PlunetEmail entries across {len(duplicate_emails)} unique emails. "
                f"This indicates data quality issues in the source system that need manual fixing.\n\n"
                f"Duplicate details:\n" + "\n".join(duplicate_details)
            )
            
            self.testkit.log_warn(test_name, warning_message)
        else:
            self.testkit.log_pass(test_name, f"No duplicate PlunetEmail entries found in {len(df_plunet_raw)} records")
    
    def check_plunet_data_quality(self, df_plunet_raw: pd.DataFrame):
        """
        Check for data quality issues in the raw Plunet data.
        
        Args:
            df_plunet_raw: Raw DataFrame from Plunet employee table
        """
        test_name = "check_plunet_data_quality"
        
        if df_plunet_raw.empty:
            self.testkit.log_warn(test_name, "No Plunet data to check for quality issues")
            return
        
        issues = []
        
        # Check for missing emails
        if 'PlunetEmail' in df_plunet_raw.columns:
            missing_emails = df_plunet_raw['PlunetEmail'].isna().sum()
            if missing_emails > 0:
                issues.append(f"{missing_emails} records with missing PlunetEmail")
        
        # Check for missing employee IDs
        if 'PlunetEmployeeID' in df_plunet_raw.columns:
            missing_ids = df_plunet_raw['PlunetEmployeeID'].isna().sum()
            if missing_ids > 0:
                issues.append(f"{missing_ids} records with missing PlunetEmployeeID")
        
        # Check for missing employee names
        if 'PlunetEmployeeName' in df_plunet_raw.columns:
            missing_names = df_plunet_raw['PlunetEmployeeName'].isna().sum()
            if missing_names > 0:
                issues.append(f"{missing_names} records with missing PlunetEmployeeName")
        
        
        if issues:
            self.testkit.log_warn(test_name, f"Data quality issues found: {'; '.join(issues)}")
        else:
            self.testkit.log_pass(test_name, f"No data quality issues found in {len(df_plunet_raw)} records")
    
    def check_firestore_update_completeness(self, resource_data: list, updated_resources: list):
        """
        Check completeness of Firestore resource overview updates.
        
        This test verifies that all expected fields are populated in the updated
        resource records and that the update process completed successfully.
        
        Args:
            resource_data: Original resource data from Firestore
            updated_resources: Enriched resource data after processing
        """
        test_name = "check_firestore_update_completeness"
        
        if not resource_data:
            self.testkit.log_warn(test_name, "No original resource data to check")
            return
        
        if not updated_resources:
            self.testkit.log_fail(test_name, "No updated resource data found")
            return
        
        if len(resource_data) != len(updated_resources):
            self.testkit.log_fail(test_name, f"Resource count mismatch: {len(resource_data)} original vs {len(updated_resources)} updated")
            return
        
        # Expected fields that should be added during enrichment
        # Always required fields
        expected_fields = [
            'class', 'billing', 'team', 'email', 'CurrentEmployee', 
            'status', 'full_name', 'entry_date', 'plunet_id'
        ]
        
        # Fields that are conditionally required based on billing type
        # Payroll fields: only required if billing = "Payroll"
        payroll_fields = ['weekly_hours', 'monthly_hours', 'FTEBob']
        
        # Fields that are conditionally required based on CurrentEmployee status
        conditional_fields = {
            'TerminationDate': 'CurrentEmployee'  # Only required if CurrentEmployee is False
        }
        
        issues = []
        enrichment_stats = {
            'total_records': len(updated_resources),
            'records_with_hr_data': 0,
            'records_with_plunet_data': 0,
            'records_with_all_fields': 0
        }
        
        # Track field-level statistics
        field_missing_counts = {field: 0 for field in expected_fields}
        problematic_records = []
        
        for i, record in enumerate(updated_resources):
            email = record.get('email', f'Record_{i}')
            
            # Check if record has HR data (indicated by presence of key HR fields)
            has_hr_data = any(field in record and record[field] is not None 
                            for field in ['direct_reports', 'FTEBob', 'location'])
            if has_hr_data:
                enrichment_stats['records_with_hr_data'] += 1
            
            # Check if record has Plunet data
            has_plunet_data = any(field in record and record[field] is not None 
                                for field in ['full_name', 'plunet_id'])
            if has_plunet_data:
                enrichment_stats['records_with_plunet_data'] += 1
            
            # Check completeness of expected fields
            missing_fields = []
            for field in expected_fields:
                if field not in record or record[field] is None:
                    missing_fields.append(field)
                    field_missing_counts[field] += 1
            
            # Check payroll fields: only required if billing = "Payroll"
            if 'billing' in record and record['billing'] == 'Payroll':
                for field in payroll_fields:
                    if field not in record or record[field] is None:
                        missing_fields.append(field)
                        field_missing_counts[field] += 1
            
            # Check conditional fields based on business logic
            for conditional_field, condition_field in conditional_fields.items():
                if condition_field in record:
                    # For TerminationDate: only required if CurrentEmployee is False
                    if conditional_field == 'TerminationDate' and condition_field == 'CurrentEmployee':
                        if record[condition_field] is False:  # Employee is terminated
                            if conditional_field not in record or record[conditional_field] is None:
                                missing_fields.append(conditional_field)
                                field_missing_counts[conditional_field] += 1
                    # Add more conditional logic here if needed in the future
            
            if not missing_fields:
                enrichment_stats['records_with_all_fields'] += 1
            else:
                # Collect detailed information about problematic records
                problematic_records.append({
                    'email': email,
                    'missing_fields': missing_fields,
                    'missing_count': len(missing_fields)
                })
        
        # Calculate enrichment percentages
        hr_enrichment_pct = (enrichment_stats['records_with_hr_data'] / enrichment_stats['total_records']) * 100
        plunet_enrichment_pct = (enrichment_stats['records_with_plunet_data'] / enrichment_stats['total_records']) * 100
        complete_enrichment_pct = (enrichment_stats['records_with_all_fields'] / enrichment_stats['total_records']) * 100
        
        # Check for concerning enrichment rates
        if hr_enrichment_pct < 80:
            issues.append(f"Low HR data enrichment: {hr_enrichment_pct:.1f}% of records have HR data")
        
        if plunet_enrichment_pct < 80:
            issues.append(f"Low Plunet data enrichment: {plunet_enrichment_pct:.1f}% of records have Plunet data")
        
        if complete_enrichment_pct < 70:
            issues.append(f"Low complete enrichment: {complete_enrichment_pct:.1f}% of records have all expected fields")
        
        # Report results
        if issues:
            # Build detailed field analysis
            field_analysis = []
            for field, missing_count in field_missing_counts.items():
                if missing_count > 0:
                    missing_pct = (missing_count / enrichment_stats['total_records']) * 100
                    field_analysis.append(f"  - {field}: {missing_count} missing ({missing_pct:.1f}%)")
            
            # Build sample of problematic records
            sample_problematic = []
            for record in sorted(problematic_records, key=lambda x: x['missing_count'], reverse=True)[:5]:
                sample_problematic.append(f"  - {record['email']}: missing {record['missing_count']} fields ({', '.join(record['missing_fields'][:3])}{'...' if len(record['missing_fields']) > 3 else ''})")
            
            warning_message = (
                f"Firestore update completeness issues found:\n\n"
                f"OVERALL STATISTICS:\n"
                f"- Total records: {enrichment_stats['total_records']}\n"
                f"- HR data enrichment: {hr_enrichment_pct:.1f}% ({enrichment_stats['records_with_hr_data']} records)\n"
                f"- Plunet data enrichment: {plunet_enrichment_pct:.1f}% ({enrichment_stats['records_with_plunet_data']} records)\n"
                f"- Complete enrichment: {complete_enrichment_pct:.1f}% ({enrichment_stats['records_with_all_fields']} records)\n\n"
                f"FIELD-LEVEL ANALYSIS:\n" + "\n".join(field_analysis) + "\n\n"
                f"SAMPLE PROBLEMATIC RECORDS:\n" + "\n".join(sample_problematic) + "\n\n"
                f"ACTION REQUIRED:\n"
                f"- Review the field-level analysis to identify which fields are most commonly missing\n"
                f"- Check the sample records to understand patterns in missing data\n"
                f"- Verify data sources (HR system, Plunet) for the identified issues"
            )
            self.testkit.log_warn(test_name, warning_message)
        else:
            success_message = (
                f"Firestore update completed successfully:\n"
                f"- Total records: {enrichment_stats['total_records']}\n"
                f"- HR data enrichment: {hr_enrichment_pct:.1f}%\n"
                f"- Plunet data enrichment: {plunet_enrichment_pct:.1f}%\n"
                f"- Complete enrichment: {complete_enrichment_pct:.1f}%"
            )
            self.testkit.log_pass(test_name, success_message)
    
    def run_all_business_checks(self, df_plunet_raw: pd.DataFrame, resource_data: list = None, updated_resources: list = None):
        """
        Run all business logic checks on the raw Plunet data and Firestore updates.
        
        Args:
            df_plunet_raw: Raw DataFrame from Plunet employee table before any processing
            resource_data: Original resource data from Firestore (optional)
            updated_resources: Enriched resource data after processing (optional)
        """
        self.check_plunet_duplicate_emails(df_plunet_raw)
        self.check_plunet_data_quality(df_plunet_raw)
        
        # Run Firestore completeness check if data is provided
        if resource_data is not None and updated_resources is not None:
            self.check_firestore_update_completeness(resource_data, updated_resources)
