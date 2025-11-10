"""
Codebase hash generator for project identification.

Generates content-based hashes from codebase structure to identify
if two uploads are from the same codebase folder.
"""

import hashlib
import os
from pathlib import Path
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


def generate_codebase_hash(extracted_path: str) -> str:
    """
    Generate a content-based hash from codebase structure.
    
    This hash is deterministic - the same codebase will always produce
    the same hash, allowing us to detect if two uploads are from the
    same folder/project.
    
    Strategy:
    1. Collect file paths (relative to root)
    2. Collect file sizes
    3. Hash a sample of file contents (first 1KB of each file)
    4. Combine into single hash
    
    Args:
        extracted_path: Path to extracted ZIP file
        
    Returns:
        str: SHA256 hash (64 hex characters)
    """
    try:
        root = Path(extracted_path)
        if not root.exists():
            logger.warning(f"Extracted path does not exist: {extracted_path}")
            return ""
        
        # Collect file information
        file_info = []
        ignored_dirs = {'.git', '.rohkun', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env'}
        ignored_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.zip', '.tar', '.gz'}
        
        for file_path in root.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in ignored_dirs):
                continue
            
            # Skip ignored file types
            if file_path.suffix.lower() in ignored_extensions:
                continue
            
            try:
                # Get relative path
                rel_path = file_path.relative_to(root)
                
                # Get file size
                file_size = file_path.stat().st_size
                
                # Read first 1KB for content hash (for speed)
                content_hash = ""
                if file_size > 0:
                    with open(file_path, 'rb') as f:
                        sample = f.read(1024)  # First 1KB
                        content_hash = hashlib.sha256(sample).hexdigest()[:16]  # First 16 chars
                
                file_info.append({
                    'path': str(rel_path),
                    'size': file_size,
                    'hash': content_hash
                })
            except (OSError, PermissionError) as e:
                logger.debug(f"Could not read file {file_path}: {e}")
                continue
        
        # Sort by path for deterministic ordering
        file_info.sort(key=lambda x: x['path'])
        
        # Create hash string from all file info
        hash_string = "\n".join([
            f"{info['path']}:{info['size']}:{info['hash']}"
            for info in file_info
        ])
        
        # Generate final hash
        codebase_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        logger.info(f"Generated codebase hash: {codebase_hash[:16]}... ({len(file_info)} files)")
        return codebase_hash
        
    except Exception as e:
        logger.error(f"Error generating codebase hash: {e}")
        return ""


def generate_project_hash_from_codebase(extracted_path: str) -> str:
    """
    Generate a human-readable project hash from codebase.
    
    Uses codebase hash but formats it as RHKN-XXXXXX for display.
    This ensures the same codebase always gets the same project_hash.
    
    Args:
        extracted_path: Path to extracted ZIP file
        
    Returns:
        str: Project hash in format RHKN-XXXXXX (deterministic from codebase)
    """
    codebase_hash = generate_codebase_hash(extracted_path)
    if not codebase_hash:
        # Fallback to random if hash generation fails (shouldn't happen normally)
        import secrets
        random_hex = secrets.token_hex(3).upper()
        logger.warning(f"Codebase hash generation failed, using random hash")
        return f"RHKN-{random_hex}"
    
    # Use first 6 characters of codebase hash for human-readable format
    # This ensures same codebase = same project_hash
    short_hash = codebase_hash[:6].upper()
    return f"RHKN-{short_hash}"

