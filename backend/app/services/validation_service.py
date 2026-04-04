"""
Validation service for input validation
"""

import pandas as pd
import io
from typing import List, Dict
from fastapi import UploadFile

from app.utils.logger import logger


class ValidationService:
    """Handle input validation"""
    
    def __init__(self):
        """Initialize validation service"""
        self.max_file_size_mb = 10
        self.allowed_extensions = {'.csv'}
        
    def validate_file_extension(self, filename: str) -> bool:
        """
        Validate file extension
        
        Args:
            filename: File name
            
        Returns:
            True if valid
        """
        return any(filename.lower().endswith(ext) for ext in self.allowed_extensions)
        
    async def validate_csv_file(self, file: UploadFile, 
                               required_columns: List[str]) -> Dict:
        """
        Validate CSV file structure
        
        Args:
            file: Uploaded file
            required_columns: Required column names
            
        Returns:
            Validation result dictionary
        """
        try:
            # Check file extension
            if not self.validate_file_extension(file.filename):
                return {
                    'valid': False,
                    'errors': [f'Invalid file type. Allowed: {self.allowed_extensions}']
                }
                
            # Read CSV
            contents = await file.read()
            
            # Check file size
            file_size_mb = len(contents) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return {
                    'valid': False,
                    'errors': [f'File size ({file_size_mb:.2f}MB) exceeds limit ({self.max_file_size_mb}MB)']
                }
                
            # Parse CSV
            try:
                df = pd.read_csv(io.BytesIO(contents))
            except Exception as e:
                return {
                    'valid': False,
                    'errors': [f'Invalid CSV format: {str(e)}']
                }
                
            # Check required columns
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                return {
                    'valid': False,
                    'errors': [f'Missing required columns: {missing_columns}']
                }
                
            # Check for empty dataframe
            if len(df) == 0:
                return {
                    'valid': False,
                    'errors': ['CSV file is empty']
                }
                
            # Reset file pointer for subsequent reads
            await file.seek(0)
            
            return {
                'valid': True,
                'num_rows': len(df),
                'columns': list(df.columns),
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Error validating CSV: {e}")
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}']
            }


# Global service instance
validation_service = ValidationService()

# Made with Bob
