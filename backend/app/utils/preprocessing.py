"""
Text preprocessing utilities
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_text_length(text: str, min_length: int = 10, max_length: int = 1000) -> bool:
    """
    Validate text length
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid
    """
    if not isinstance(text, str):
        return False
    
    text_len = len(text.strip())
    return min_length <= text_len <= max_length


def batch_clean_texts(texts: List[str]) -> List[str]:
    """
    Clean multiple texts
    
    Args:
        texts: List of texts
        
    Returns:
        List of cleaned texts
    """
    return [clean_text(text) for text in texts]

# Made with Bob
