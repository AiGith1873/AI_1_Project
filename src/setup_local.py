"""
Local environment setup script with GDPR compliance checks.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Dict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LocalSetup:
    """
    Handles local environment setup with GDPR compliance.
    """
    
    def __init__(self):
        """Initialize the setup process."""
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        self.config_dir = self.base_dir / "src" / "config"
        
    def setup_directories(self) -> None:
        """Create necessary directories with proper permissions."""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.config_dir,
            self.data_dir / "sample_documents",
            self.data_dir / "processed",
            self.data_dir / "embeddings"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions (read/write for owner only)
            os.chmod(directory, 0o700)
            logger.info(f"Created directory: {directory}")
    
    def check_ollama(self) -> bool:
        """
        Check if Ollama is installed and running.
        
        Returns:
            bool: True if Ollama is available
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Ollama: {str(e)}")
            return False
    
    def setup_virtual_environment(self) -> None:
        """Create and configure virtual environment."""
        venv_dir = self.base_dir / "venv"
        
        if not venv_dir.exists():
            logger.info("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        
        # Activate virtual environment and install requirements
        if os.name == 'nt':  # Windows
            activate_script = venv_dir / "Scripts" / "activate"
            pip_path = venv_dir / "Scripts" / "pip"
        else:  # Unix/Linux
            activate_script = venv_dir / "bin" / "activate"
            pip_path = venv_dir / "bin" / "pip"
        
        # Install requirements
        subprocess.run([
            str(pip_path),
            "install",
            "-r",
            str(self.base_dir / "requirements.txt")
        ])
    
    def setup_gdpr_config(self) -> None:
        """Create GDPR configuration file."""
        config = {
            "data_retention": {
                "user_queries": 30,
                "document_embeddings": 365,
                "processing_logs": 90
            },
            "privacy": {
                "anonymize_queries": True,
                "log_minimal_data": True,
                "secure_storage": True
            },
            "processing": {
                "local_only": True,
                "data_minimization": True,
                "purpose_limitation": True
            }
        }
        
        config_file = self.config_dir / "gdpr_settings.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        os.chmod(config_file, 0o600)  # Restrictive permissions
    
    def verify_setup(self) -> Dict[str, bool]:
        """
        Verify the setup is complete and compliant.
        
        Returns:
            Dict[str, bool]: Status of each setup component
        """
        return {
            "directories_created": all(
                d.exists() for d in [
                    self.data_dir,
                    self.logs_dir,
                    self.config_dir
                ]
            ),
            "ollama_available": self.check_ollama(),
            "virtual_environment": (self.base_dir / "venv").exists(),
            "gdpr_config": (self.config_dir / "gdpr_settings.json").exists()
        }
    
    def run(self) -> None:
        """Run the complete setup process."""
        logger.info("Starting local setup...")
        
        try:
            self.setup_directories()
            self.setup_virtual_environment()
            self.setup_gdpr_config()
            
            # Verify setup
            status = self.verify_setup()
            if all(status.values()):
                logger.info("Setup completed successfully!")
                logger.info("Status:")
                for key, value in status.items():
                    logger.info(f"- {key}: {'✓' if value else '✗'}")
            else:
                logger.error("Setup incomplete. Please check the logs.")
                
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    setup = LocalSetup()
    setup.run() 