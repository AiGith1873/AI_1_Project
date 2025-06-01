"""
GDPR and EU AI compliance configuration.
This module contains settings and checks to ensure compliance with GDPR and EU AI regulations.
"""

import os
import logging
from typing import Dict, List
from datetime import datetime, timedelta

class GDPRConfig:
    """
    Configuration class for GDPR and EU AI compliance.
    Manages data retention, processing, and privacy settings.
    """
    
    def __init__(self):
        """Initialize GDPR configuration with default settings."""
        self.logger = logging.getLogger(__name__)
        
        # Data retention settings (in days)
        self.retention_periods = {
            "user_queries": 30,  # Store queries for 30 days
            "document_embeddings": 365,  # Keep embeddings for 1 year
            "processing_logs": 90,  # Keep logs for 90 days
        }
        
        # Data processing settings
        self.processing_settings = {
            "data_minimization": True,  # Only process necessary data
            "purpose_limitation": True,  # Process only for specified purposes
            "storage_limitation": True,  # Enforce retention periods
            "local_processing": True,  # Process data locally only
        }
        
        # Privacy settings
        self.privacy_settings = {
            "anonymize_queries": True,  # Remove personal identifiers from queries
            "log_minimal_data": True,  # Log only necessary information
            "secure_storage": True,  # Ensure secure storage of data
        }
        
        # EU AI Act compliance
        self.ai_compliance = {
            "transparency": True,  # Provide clear information about AI usage
            "human_oversight": True,  # Enable human review of AI decisions
            "risk_assessment": True,  # Regular risk assessments
            "documentation": True,  # Maintain documentation of AI system
        }
    
    def validate_processing(self, data_type: str, purpose: str) -> bool:
        """
        Validate if data processing is compliant.
        
        Args:
            data_type (str): Type of data being processed
            purpose (str): Purpose of processing
            
        Returns:
            bool: True if processing is compliant
        """
        # Check if processing is necessary
        if not self.processing_settings["data_minimization"]:
            self.logger.warning("Data minimization not enforced")
            return False
            
        # Check if processing is local
        if not self.processing_settings["local_processing"]:
            self.logger.warning("Non-local processing detected")
            return False
            
        return True
    
    def get_retention_date(self, data_type: str) -> datetime:
        """
        Get the retention end date for a data type.
        
        Args:
            data_type (str): Type of data
            
        Returns:
            datetime: Date when data should be deleted
        """
        retention_days = self.retention_periods.get(data_type, 30)
        return datetime.now() + timedelta(days=retention_days)
    
    def should_anonymize(self, data: str) -> bool:
        """
        Check if data should be anonymized.
        
        Args:
            data (str): Data to check
            
        Returns:
            bool: True if data should be anonymized
        """
        return self.privacy_settings["anonymize_queries"]
    
    def log_processing(self, 
                      data_type: str, 
                      purpose: str, 
                      metadata: Dict = None) -> None:
        """
        Log data processing activity.
        
        Args:
            data_type (str): Type of data processed
            purpose (str): Purpose of processing
            metadata (Dict, optional): Additional metadata
        """
        if not self.privacy_settings["log_minimal_data"]:
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
            "purpose": purpose,
            "metadata": metadata or {}
        }
        
        self.logger.info(f"Data processing: {log_entry}")
    
    def get_compliance_report(self) -> Dict:
        """
        Generate a compliance report.
        
        Returns:
            Dict: Compliance status and settings
        """
        return {
            "gdpr_compliance": {
                "data_minimization": self.processing_settings["data_minimization"],
                "purpose_limitation": self.processing_settings["purpose_limitation"],
                "storage_limitation": self.processing_settings["storage_limitation"],
                "local_processing": self.processing_settings["local_processing"]
            },
            "privacy_settings": self.privacy_settings,
            "ai_compliance": self.ai_compliance,
            "retention_periods": self.retention_periods
        } 