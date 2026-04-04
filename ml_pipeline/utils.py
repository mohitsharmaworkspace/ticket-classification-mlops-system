"""
Utility functions for ML pipeline
"""

import re
import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_text(text: str, lowercase: bool = True, 
               remove_special_chars: bool = True,
               remove_extra_spaces: bool = True) -> str:
    """
    Clean and preprocess text
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_special_chars: Remove special characters
        remove_extra_spaces: Remove extra whitespace
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
        
    # Convert to lowercase
    if lowercase:
        text = text.lower()
        
    # Remove special characters but keep basic punctuation
    if remove_special_chars:
        text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', ' ', text)
        
    # Remove extra spaces
    if remove_extra_spaces:
        text = re.sub(r'\s+', ' ', text).strip()
        
    return text


def validate_csv_schema(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate CSV schema
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if valid, False otherwise
    """
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
        
    return True


def validate_text_length(text: str, min_length: int = 10, 
                        max_length: int = 1000) -> bool:
    """
    Validate text length
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(text, str):
        return False
        
    text_len = len(text.strip())
    return min_length <= text_len <= max_length


def calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)


def save_json(data: Dict[str, Any], filepath: str):
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: Output file path
    """
    import json
    
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
        
    logger.info(f"Data saved to {filepath}")


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from JSON file
    
    Args:
        filepath: Input file path
        
    Returns:
        Loaded data
    """
    import json
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Data loaded from {filepath}")
        return data
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return {}


def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    Calculate statistical measures for data
    
    Args:
        data: Input data array
        
    Returns:
        Dictionary of statistics
    """
    return {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'median': float(np.median(data)),
        'q25': float(np.percentile(data, 25)),
        'q75': float(np.percentile(data, 75))
    }


def merge_ground_truth_with_raw(raw_df: pd.DataFrame, 
                                ground_truth_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge ground truth corrections with raw data
    
    Args:
        raw_df: Raw data DataFrame
        ground_truth_df: Ground truth DataFrame with corrections
        
    Returns:
        Merged DataFrame
    """
    if ground_truth_df.empty:
        return raw_df
        
    # Update raw data with ground truth labels
    merged_df = raw_df.copy()
    
    for idx, row in ground_truth_df.iterrows():
        ticket_id = row.get('ticket_id')
        corrected_label = row.get('corrected_label')
        
        if ticket_id and corrected_label:
            mask = merged_df['Ticket ID'] == ticket_id
            if mask.any():
                merged_df.loc[mask, 'Ticket Type'] = corrected_label
                
    logger.info(f"Merged {len(ground_truth_df)} ground truth corrections")
    return merged_df


def create_category_embeddings_dict(categories_df: pd.DataFrame, 
                                   embeddings: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Create dictionary mapping category names to embeddings
    
    Args:
        categories_df: DataFrame with category information
        embeddings: Array of category embeddings
        
    Returns:
        Dictionary mapping category names to embeddings
    """
    category_dict = {}
    
    for idx, row in categories_df.iterrows():
        category_name = row['category_name']
        category_dict[category_name] = embeddings[idx]
        
    return category_dict

# Made with Bob
