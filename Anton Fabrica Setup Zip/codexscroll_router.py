"""
CodexScroll Router - Manages document linking to the ScrollChain for governance and timestamping.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
import logging
logger = logging.getLogger('CodexScroll')

def generate_quantum_anchor(document_path: str, content: Optional[str] = None) -> str:
    """Generate a quantum anchor for document verification.
    
    Args:
        document_path: Path to the document
        content: Optional document content (if already loaded)
        
    Returns:
        str: Quantum anchor string
    """
    # Use provided content or read from file
    if content is None:
        try:
            with open(document_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read document for anchor generation: {e}")
            content = document_path.encode('utf-8')
    
    # Create a deterministic anchor
    doc_hash = hashlib.sha3_256(content).hexdigest()
    timestamp = int(datetime.utcnow().timestamp())
    return f"QS-SCROLL-{doc_hash[:16]}-{timestamp}"

def link_to_scroll(
    document_path: str,
    codexchain_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    operator: str = "system"
) -> Dict[str, Any]:
    """Link a document to the CodexScroll chain.
    
    Args:
        document_path: Path to the document being linked
        codexchain_path: Path to the CodexScroll chain file
        metadata: Additional metadata to include
        operator: ID of the operator performing the link
        
    Returns:
        Dict containing the scroll entry
    """
    if codexchain_path is None:
        codexchain_path = "bundles/ΣΩΩ.current/vault/codexscroll_chain.json"
    
    # Ensure parent directory exists
    Path(codexchain_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Generate quantum anchor
    quantum_anchor = generate_quantum_anchor(document_path)
    
    # Create scroll entry
    entry = {
        "document": str(document_path),
        "linked_at": datetime.utcnow().isoformat(),
        "linked_by": operator,
        "quantum_anchor": quantum_anchor,
        "metadata": metadata or {}
    }
    
    # Read existing data or initialize new
    try:
        with open(codexchain_path, 'r+') as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict) or 'entries' not in data:
                    data = {"version": "1.0", "entries": []}
            except json.JSONDecodeError:
                data = {"version": "1.0", "entries": []}
            
            # Add new entry
            data['entries'].append(entry)
            
            # Write back to file
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except FileNotFoundError:
        # Create new file if it doesn't exist
        with open(codexchain_path, 'w') as f:
            data = {"version": "1.0", "entries": [entry]}
            json.dump(data, f, indent=2)
    
    logger.info(f"Document linked to ScrollChain: {quantum_anchor}")
    return entry

def verify_scroll_link(document_path: str, codexchain_path: Optional[str] = None) -> bool:
    """Verify if a document is properly linked in the ScrollChain.
    
    Args:
        document_path: Path to the document to verify
        codexchain_path: Path to the CodexScroll chain file
        
    Returns:
        bool: True if verification succeeds, False otherwise
    """
    if codexchain_path is None:
        codexchain_path = "bundles/ΣΩΩ.current/vault/codexscroll_chain.json"
    
    try:
        with open(codexchain_path, 'r') as f:
            data = json.load(f)
            
        # Find the document in the scroll chain
        for entry in data.get('entries', []):
            if entry.get('document') == str(document_path):
                # Verify the quantum anchor
                expected_anchor = generate_quantum_anchor(document_path)
                return entry.get('quantum_anchor', '').startswith('QS-SCROLL-') and \
                       entry.get('quantum_anchor').split('-')[-2] == expected_anchor.split('-')[-2]
        
        return False
    except (FileNotFoundError, json.JSONDecodeError):
        return False
