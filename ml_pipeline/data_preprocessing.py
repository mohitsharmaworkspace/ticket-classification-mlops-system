"""
Data preprocessing pipeline for ticket classification
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional
from pathlib import Path

from ml_pipeline.config import config
from ml_pipeline.utils import (
    clean_text, 
    validate_csv_schema, 
    validate_text_length,
    merge_ground_truth_with_raw
)

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Data preprocessing pipeline"""
    
    def __init__(self):
        """Initialize data preprocessor"""
        self.config = config
        self.required_columns = ['Ticket ID', 'Ticket Description', 'Ticket Type']
        
    def load_raw_data(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load raw ticket data
        
        Args:
            filepath: Path to CSV file (optional, uses config if not provided)
            
        Returns:
            DataFrame with raw data
        """
        if filepath is None:
            filepath = self.config.raw_data_path
            
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} records from {filepath}")
            return df
        except FileNotFoundError:
            logger.error(f"Data file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
            
    def load_categories(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load category definitions
        
        Args:
            filepath: Path to categories CSV (optional, uses config if not provided)
            
        Returns:
            DataFrame with categories
        """
        if filepath is None:
            filepath = self.config.default_categories_path
            
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} categories from {filepath}")
            return df
        except FileNotFoundError:
            logger.error(f"Categories file not found: {filepath}")
            raise
            
    def load_ground_truth(self) -> pd.DataFrame:
        """
        Load ground truth corrections
        
        Returns:
            DataFrame with ground truth data
        """
        filepath = self.config.ground_truth_path
        
        try:
            if Path(filepath).exists():
                df = pd.read_csv(filepath)
                logger.info(f"Loaded {len(df)} ground truth corrections")
                return df
            else:
                logger.info("No ground truth file found, returning empty DataFrame")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading ground truth: {e}")
            return pd.DataFrame()
            
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data schema and content
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required columns
        if not validate_csv_schema(df, self.required_columns):
            return False
            
        # Check for missing values in critical columns
        missing_counts = df[self.required_columns].isnull().sum()
        if missing_counts.any():
            logger.warning(f"Missing values detected:\n{missing_counts}")
            
        # Check data types
        if 'Ticket ID' in df.columns and not pd.api.types.is_numeric_dtype(df['Ticket ID']):
            logger.warning("Ticket ID should be numeric")
            
        return True
        
    def clean_ticket_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean ticket descriptions
        
        Args:
            df: DataFrame with ticket data
            
        Returns:
            DataFrame with cleaned text
        """
        df = df.copy()
        
        # Get preprocessing parameters
        lowercase = self.config.get('data.preprocessing.lowercase', True)
        remove_special = self.config.get('data.preprocessing.remove_special_chars', True)
        remove_spaces = self.config.get('data.preprocessing.remove_extra_spaces', True)
        
        # Clean ticket descriptions
        if 'Ticket Description' in df.columns:
            df['Ticket Description'] = df['Ticket Description'].apply(
                lambda x: clean_text(
                    str(x), 
                    lowercase=lowercase,
                    remove_special_chars=remove_special,
                    remove_extra_spaces=remove_spaces
                )
            )
            
        # Clean ticket subjects if available
        if 'Ticket Subject' in df.columns:
            df['Ticket Subject'] = df['Ticket Subject'].apply(
                lambda x: clean_text(
                    str(x),
                    lowercase=lowercase,
                    remove_special_chars=remove_special,
                    remove_extra_spaces=remove_spaces
                )
            )
            
        logger.info("Text cleaning completed")
        return df
        
    def filter_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out invalid records
        
        Args:
            df: DataFrame to filter
            
        Returns:
            Filtered DataFrame
        """
        df = df.copy()
        initial_count = len(df)
        
        # Get length constraints
        min_length = self.config.get('data.preprocessing.min_text_length', 10)
        max_length = self.config.get('data.preprocessing.max_text_length', 1000)
        
        # Filter by text length
        if 'Ticket Description' in df.columns:
            df = df[df['Ticket Description'].apply(
                lambda x: validate_text_length(str(x), min_length, max_length)
            )]
            
        # Remove duplicates
        if 'Ticket ID' in df.columns:
            df = df.drop_duplicates(subset=['Ticket ID'])
            
        # Remove rows with missing critical data
        df = df.dropna(subset=['Ticket Description'])
        
        removed_count = initial_count - len(df)
        logger.info(f"Filtered out {removed_count} invalid records")
        
        return df
        
    def create_combined_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create combined text field from subject and description
        
        Args:
            df: DataFrame with ticket data
            
        Returns:
            DataFrame with combined text field
        """
        df = df.copy()
        
        if 'Ticket Subject' in df.columns and 'Ticket Description' in df.columns:
            df['combined_text'] = df['Ticket Subject'] + ' ' + df['Ticket Description']
        else:
            df['combined_text'] = df['Ticket Description']
            
        logger.info("Combined text field created")
        return df
        
    def preprocess(self, df: pd.DataFrame, 
                   include_ground_truth: bool = True) -> pd.DataFrame:
        """
        Complete preprocessing pipeline
        
        Args:
            df: Raw DataFrame
            include_ground_truth: Whether to merge ground truth corrections
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting preprocessing pipeline")
        
        # Validate data
        if not self.validate_data(df):
            raise ValueError("Data validation failed")
            
        # Merge ground truth if requested
        if include_ground_truth:
            ground_truth_df = self.load_ground_truth()
            if not ground_truth_df.empty:
                df = merge_ground_truth_with_raw(df, ground_truth_df)
                
        # Clean text
        df = self.clean_ticket_text(df)
        
        # Filter invalid records
        df = self.filter_invalid_records(df)
        
        # Create combined text
        df = self.create_combined_text(df)
        
        logger.info(f"Preprocessing completed. Final dataset size: {len(df)}")
        return df
        
    def save_processed_data(self, df: pd.DataFrame, 
                           filepath: Optional[str] = None):
        """
        Save preprocessed data
        
        Args:
            df: Preprocessed DataFrame
            filepath: Output path (optional, uses config if not provided)
        """
        if filepath is None:
            filepath = self.config.processed_data_path
            
        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        logger.info(f"Processed data saved to {filepath}")
        
    def run_pipeline(self, input_path: Optional[str] = None,
                    output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete preprocessing pipeline
        
        Args:
            input_path: Input CSV path (optional)
            output_path: Output CSV path (optional)
            
        Returns:
            Preprocessed DataFrame
        """
        # Load data
        df = self.load_raw_data(input_path)
        
        # Preprocess
        df = self.preprocess(df)
        
        # Save
        self.save_processed_data(df, output_path)
        
        return df


if __name__ == "__main__":
    # Run preprocessing pipeline
    preprocessor = DataPreprocessor()
    df = preprocessor.run_pipeline()
    print(f"Preprocessing complete. Processed {len(df)} records.")

# Made with Bob
