import logging
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Lead:
    """Lead data structure"""
    id: str
    name: str
    status: str
    email: Optional[str] = None
    phone: Optional[str] = None
    course_interest: Optional[str] = None
    last_contact: Optional[str] = None
    assigned_counselor: Optional[str] = None
    created_at: Optional[str] = None
    notes: Optional[str] = None

class CAMClient:
    """
    CRM/CAM Client for managing leads and student data
    Currently using mock data, but structured for easy migration to real CRM
    """
    
    def __init__(self):
        self.mock_leads = self._initialize_mock_data()
        logger.info("CAM Client initialized with mock data")
    
    def _initialize_mock_data(self) -> Dict[str, Lead]:
        """Initialize mock lead data"""
        return {
            "123": Lead(
                id="123",
                name="John Doe",
                status="Interested",
                email="john.doe@email.com",
                phone="+91-9876543210",
                course_interest="B.Tech Computer Science",
                last_contact="2024-01-15",
                assigned_counselor="Ms. Priya Sharma",
                created_at="2024-01-10",
                notes="Interested in AI/ML specialization"
            ),
            "456": Lead(
                id="456",
                name="Jane Smith",
                status="Not Responding",
                email="jane.smith@email.com",
                phone="+91-9876543211",
                course_interest="MBA",
                last_contact="2024-01-12",
                assigned_counselor="Mr. Raj Kumar",
                created_at="2024-01-08",
                notes="Called multiple times, no response"
            ),
            "789": Lead(
                id="789",
                name="Rahul Gupta",
                status="Application Submitted",
                email="rahul.gupta@email.com",
                phone="+91-9876543212",
                course_interest="B.Com",
                last_contact="2024-01-20",
                assigned_counselor="Ms. Priya Sharma",
                created_at="2024-01-05",
                notes="Documents verified, awaiting admission decision"
            ),
            "101": Lead(
                id="101",
                name="Priya Patel",
                status="Enrolled",
                email="priya.patel@email.com",
                phone="+91-9876543213",
                course_interest="BCA",
                last_contact="2024-01-22",
                assigned_counselor="Mr. Raj Kumar",
                created_at="2024-01-01",
                notes="Successfully enrolled for 2024 batch"
            )
        }
    
    def get_lead_status(self, lead_id: str) -> Dict[str, Any]:
        """
        Get lead status by ID
        
        Args:
            lead_id (str): The lead ID to look up
            
        Returns:
            Dict containing lead information or error message
        """
        try:
            lead = self.mock_leads.get(lead_id)
            
            if not lead:
                logger.warning(f"Lead ID {lead_id} not found")
                return {
                    "status": "Unknown Lead ID",
                    "error": True,
                    "message": f"No lead found with ID: {lead_id}"
                }
            
            logger.info(f"Retrieved lead data for ID: {lead_id}")
            return {
                "id": lead.id,
                "name": lead.name,
                "status": lead.status,
                "email": lead.email,
                "phone": lead.phone,
                "course_interest": lead.course_interest,
                "last_contact": lead.last_contact,
                "assigned_counselor": lead.assigned_counselor,
                "created_at": lead.created_at,
                "notes": lead.notes,
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Error retrieving lead {lead_id}: {e}")
            return {
                "status": "Error",
                "error": True,
                "message": "An error occurred while retrieving lead information"
            }
    
    def search_leads_by_name(self, name: str) -> list[Dict[str, Any]]:
        """
        Search leads by name (partial match)
        
        Args:
            name (str): Name to search for
            
        Returns:
            List of matching leads
        """
        try:
            name_lower = name.lower()
            matching_leads = []
            
            for lead in self.mock_leads.values():
                if name_lower in lead.name.lower():
                    matching_leads.append({
                        "id": lead.id,
                        "name": lead.name,
                        "status": lead.status,
                        "course_interest": lead.course_interest
                    })
            
            logger.info(f"Found {len(matching_leads)} leads matching name: {name}")
            return matching_leads
            
        except Exception as e:
            logger.error(f"Error searching leads by name {name}: {e}")
            return []
    
    def get_leads_by_status(self, status: str) -> list[Dict[str, Any]]:
        """
        Get all leads with a specific status
        
        Args:
            status (str): Status to filter by
            
        Returns:
            List of leads with the specified status
        """
        try:
            filtered_leads = []
            
            for lead in self.mock_leads.values():
                if lead.status.lower() == status.lower():
                    filtered_leads.append({
                        "id": lead.id,
                        "name": lead.name,
                        "status": lead.status,
                        "last_contact": lead.last_contact,
                        "assigned_counselor": lead.assigned_counselor
                    })
            
            logger.info(f"Found {len(filtered_leads)} leads with status: {status}")
            return filtered_leads
            
        except Exception as e:
            logger.error(f"Error filtering leads by status {status}: {e}")
            return []
    
    def update_lead_status(self, lead_id: str, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update lead status
        
        Args:
            lead_id (str): Lead ID to update
            new_status (str): New status
            notes (str, optional): Additional notes
            
        Returns:
            Dict with update result
        """
        try:
            if lead_id not in self.mock_leads:
                return {
                    "success": False,
                    "message": f"Lead ID {lead_id} not found"
                }
            
            lead = self.mock_leads[lead_id]
            old_status = lead.status
            lead.status = new_status
            lead.last_contact = datetime.now().strftime("%Y-%m-%d")
            
            if notes:
                lead.notes = f"{lead.notes}; {notes}" if lead.notes else notes
            
            logger.info(f"Updated lead {lead_id} status from {old_status} to {new_status}")
            
            return {
                "success": True,
                "message": f"Lead status updated successfully",
                "old_status": old_status,
                "new_status": new_status
            }
            
        except Exception as e:
            logger.error(f"Error updating lead {lead_id}: {e}")
            return {
                "success": False,
                "message": "An error occurred while updating lead status"
            }
    
    def get_counselor_leads(self, counselor_name: str) -> list[Dict[str, Any]]:
        """
        Get all leads assigned to a specific counselor
        
        Args:
            counselor_name (str): Counselor name
            
        Returns:
            List of leads assigned to the counselor
        """
        try:
            counselor_leads = []
            
            for lead in self.mock_leads.values():
                if lead.assigned_counselor and counselor_name.lower() in lead.assigned_counselor.lower():
                    counselor_leads.append({
                        "id": lead.id,
                        "name": lead.name,
                        "status": lead.status,
                        "course_interest": lead.course_interest,
                        "last_contact": lead.last_contact
                    })
            
            logger.info(f"Found {len(counselor_leads)} leads for counselor: {counselor_name}")
            return counselor_leads
            
        except Exception as e:
            logger.error(f"Error getting leads for counselor {counselor_name}: {e}")
            return []

# Initialize the client
cam_client = CAMClient()

# Convenience functions for backward compatibility
def get_lead_status(lead_id: str) -> Dict[str, Any]:
    """Backward compatible function"""
    return cam_client.get_lead_status(lead_id)

# Health check for the CAM system
def health_check() -> bool:
    """Check if CAM client is working"""
    try:
        # Test with a known lead ID
        result = cam_client.get_lead_status("123")
        return not result.get("error", True)
    except Exception as e:
        logger.error(f"CAM health check failed: {e}")
        return False
