"""
AcknowledgeManager - Ultra-simple Firestore structure for test acknowledgments.

Uses the simplest possible structure:
- One document per test: {repo}%{pipeline}%{test_name}
- Issues stored as maps within the test document
- No dates, no complex metadata - just the essentials
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from google.cloud import firestore


class AcknowledgeManager:
    """
    Ultra-simple acknowledgment manager with minimal Firestore structure.
    
    Firestore Structure:
    Collection: pipeline_acknowledgments
    └── Document: {repo}%{pipeline}%{test_name}
        └── issues: {
            "issue1": {
                "acknowledged": true/false,
                "muted_until": timestamp,
                "identifier": "user@email.com",
                "details": "xxx hours expected, xx found"
            },
            "issue2": { ... }
        }
    """
    
    def __init__(self, firestore_client: firestore.Client, repository_name: str, pipeline_name: str):
        """
        Initialize the AcknowledgeManager.
        
        Args:
            firestore_client: Firestore client instance
            repository_name: Name of the repository (e.g., 'locate_2_pulls')
            pipeline_name: Name of the pipeline (e.g., 'capacity_tracker_linguists_days_off')
        """
        self.firestore_client = firestore_client
        self.repository_name = repository_name
        self.pipeline_name = pipeline_name
        self.collection = "pipeline_acknowledgments"
        
        # Default configuration
        self.default_mute_days = 7
        self.max_emails_per_day = 1
    
    def _generate_document_id(self, test_name: str) -> str:
        """
        Generate document ID for the ultra-simple structure.
        
        Args:
            test_name: Name of the test
            
        Returns:
            Document ID in format: {repo}%{pipeline}%{test_name}
        """
        return f"{self.repository_name}%{self.pipeline_name}%{test_name}"
    
    
    def check_issue_acknowledged(self, test_name: str, issue_identifier: str) -> bool:
        """
        Check if specific issue is acknowledged and still muted.
        
        Args:
            test_name: Name of the test
            issue_identifier: Primary identifier (email, ID, combination, etc.)
            
        Returns:
            True if issue is acknowledged and still muted, False otherwise
        """
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            doc_ref = self.firestore_client.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            data = doc.to_dict()
            issues = data.get('issues', {})
            
            # Create issue key (simple identifier)
            issue_key_simple = str(issue_identifier).lower().strip()
            
            if issue_key_simple not in issues:
                return False
            
            issue = issues[issue_key_simple]
            
            if not issue.get('acknowledged', False):
                return False
            
            # Check if mute period has expired
            mute_until = issue.get('muted_until')  # Fixed: use 'muted_until' not 'mute_until'
            if not mute_until:
                return False
            
            # Convert Firestore timestamp to datetime if needed
            if hasattr(mute_until, 'timestamp'):
                mute_until = datetime.fromtimestamp(mute_until.timestamp(), tz=timezone.utc)
            elif isinstance(mute_until, str):
                mute_until = datetime.fromisoformat(mute_until.replace('Z', '+00:00'))
            
            current_time = datetime.now(timezone.utc)
            return current_time < mute_until
            
        except Exception as e:
            print(f"Warning: Error checking acknowledgment status: {e}")
            return False
    
    def acknowledge_issue(self, test_name: str, issue_identifier: str, 
                         acknowledged_by: str) -> bool:
        """
        Acknowledge specific issue and mute for configured period.

        Pablo: is it used somewhere?
        
        Args:
            test_name: Name of the test
            issue_identifier: Primary identifier (email, ID, combination, etc.)
            acknowledged_by: Email of person acknowledging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            doc_ref = self.firestore_client.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
            
            data = doc.to_dict()
            issues = data.get('issues', {})
            
            # Create issue key (simple identifier)
            issue_key_simple = str(issue_identifier).lower().strip()
            
            if issue_key_simple not in issues:
                return False
            
            # Update the issue using the simple structure
            current_time = datetime.now(timezone.utc)
            mute_until = current_time + timedelta(days=self.default_mute_days)
            
            issues[issue_key_simple]['acknowledged'] = True
            issues[issue_key_simple]['muted_until'] = mute_until
            issues[issue_key_simple]['identifier'] = acknowledged_by
            
            # Save the document
            doc_ref.set({'issues': issues})
            return True
            
        except Exception as e:
            print(f"❌ Error acknowledging issue: {e}")
            return False
    
    def update_issue_detection(
            self, 
            test_name: str, 
            issue_identifier: str, 
            issue_details: str, 
            additional_metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update detection tracking for an issue (called when issue is detected).
        
        Args:
            test_name: Name of the test
            issue_identifier: Primary identifier (email, ID, combination, etc.).
                It's a good practice to use the `{filename}-{function_name}` format for uniqueness.
            issue_details: Brief details about the issue. The error message or summary.
            additional_metadata: Optional additional metadata to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate document ID for the test
            doc_id = self._generate_document_id(test_name)
            
            # Get document reference
            doc_ref = self.firestore_client.collection(self.collection).document(doc_id)
            
            # Create issue key (simple identifier)
            issue_key_simple = str(issue_identifier).lower().strip()
            
            # Create issue details string
            details = f"{issue_details}"
            if additional_metadata:
                # Add relevant details from metadata
                if 'absent_percentage' in additional_metadata:
                    details += f" - {additional_metadata['absent_percentage']}% absent"
                elif 'expected_weekly_hours' in additional_metadata:
                    details += f" - Expected {additional_metadata['expected_weekly_hours']}h/week"
            
            # Get existing document
            existing_doc = doc_ref.get()
            
            if existing_doc.exists:
                # Update existing document
                existing_data = existing_doc.to_dict()
                issues = existing_data.get('issues', {})
            else:
                # Create new document
                issues = {}
            
            # Update or create the issue, preserving existing acknowledgment status
            existing_issue = issues.get(issue_key_simple, {})
            issues[issue_key_simple] = {
                'acknowledged': existing_issue.get('acknowledged', False),
                'muted_until': existing_issue.get('muted_until'),
                'identifier': issue_identifier,
                'details': details,
                **(additional_metadata or {})
            }
            
            # Save the document
            doc_ref.set({'issues': issues})
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating issue detection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def filter_acknowledged_issues(self, test_results: List[Dict], issue_identifier: str) -> Dict[str, List[Dict]]:
        """
        Filter test results into new vs acknowledged issues.
        OPTIMIZED: Uses batch operations for better performance.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            Dictionary with 'new_issues' and 'acknowledged_issues' lists
        """
        new_issues = []
        acknowledged_issues = []
        
        for result in test_results:
            if not result.get('acknowledgeable', True):
                # Non-acknowledgeable issues are always new
                new_issues.append(result)
                continue
            
            # Extract acknowledgment metadata
            # metrics = result.get('metrics', {})
            # issue_identifier = metrics.get('issue_identifier') or metrics.get('person_email')
            # issue_details = metrics.get('issue_details')
            # issue_key = metrics.get('issue_key')
            test_name = result.get('test_name')
            
            if not all([issue_identifier, test_name]):
                # Missing required metadata, treat as new
                new_issues.append(result)
                continue
            
            # Check if this issue is acknowledged
            is_acknowledged = self.check_issue_acknowledged(
                test_name, issue_identifier
            )
            
            if is_acknowledged:
                acknowledged_issues.append(result)
            else:
                new_issues.append(result)
        
        return {
            'new_issues': new_issues,
            'acknowledged_issues': acknowledged_issues
        }
    


# Convenience functions for easy import
def create_acknowledge_manager(firestore_client: firestore.Client, 
                              repository_name: str, pipeline_name: str) -> AcknowledgeManager:
    """Create a new AcknowledgeManager instance."""
    return AcknowledgeManager(firestore_client, repository_name, pipeline_name)


