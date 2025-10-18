"""
Network Sync - Manages synchronization between kernel registry and ScrollChain.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger('NetSync')

class ScrollChainSync:
    """Handles synchronization between kernel registry and ScrollChain."""
    
    def __init__(
        self,
        registry_path: Optional[str] = None,
        scrollchain_path: Optional[str] = None
    ):
        """Initialize the ScrollChain synchronizer.
        
        Args:
            registry_path: Path to the kernel registry JSON file
            scrollchain_path: Path to the ScrollChain ledger file
        """
        self.registry_path = registry_path or "bundles/ΣΩΩ.current/vault/kernel_registry.json"
        self.scrollchain_path = scrollchain_path or "scrollchain/ledger_sync.json"
        
        # Ensure parent directories exist
        Path(self.scrollchain_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute the SHA3-256 hash of a file."""
        hasher = hashlib.sha3_256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            return ""
    
    def _compute_registry_hash(self) -> str:
        """Compute a deterministic hash of the registry."""
        try:
            with open(self.registry_path, 'r') as f:
                registry_data = json.load(f)
            
            # Create a deterministic string representation
            registry_str = json.dumps(registry_data, sort_keys=True)
            return hashlib.sha3_256(registry_str.encode()).hexdigest()
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to compute registry hash: {e}")
            return ""
    
    def sync_registry(self, force: bool = False) -> Tuple[bool, str]:
        """Synchronize the kernel registry with ScrollChain.
        
        Args:
            force: If True, force synchronization even if no changes detected
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Compute current registry hash
            registry_hash = self._compute_registry_hash()
            if not registry_hash:
                return False, "Failed to compute registry hash"
            
            # Get current timestamp
            timestamp = datetime.utcnow().isoformat()
            
            # Prepare the sync entry
            sync_entry = {
                'registry_hash': registry_hash,
                'timestamp': timestamp,
                'registry_path': os.path.abspath(self.registry_path)
            }
            
            # Read existing scrollchain or create new
            try:
                with open(self.scrollchain_path, 'r+') as f:
                    try:
                        scrollchain = json.load(f)
                        if not isinstance(scrollchain, dict):
                            scrollchain = {'version': '1.0', 'entries': []}
                    except json.JSONDecodeError:
                        scrollchain = {'version': '1.0', 'entries': []}
                    
                    # Check if this registry hash is already in the scrollchain
                    existing_entry = next(
                        (e for e in scrollchain.get('entries', [])
                         if e.get('registry_hash') == registry_hash),
                        None
                    )
                    
                    if existing_entry and not force:
                        return True, f"Registry already synchronized at {existing_entry['timestamp']}"
                    
                    # Add new entry
                    if 'entries' not in scrollchain:
                        scrollchain['entries'] = []
                    scrollchain['entries'].append(sync_entry)
                    
                    # Write back to file
                    f.seek(0)
                    json.dump(scrollchain, f, indent=2)
                    f.truncate()
                    
            except FileNotFoundError:
                # Create new scrollchain file
                with open(self.scrollchain_path, 'w') as f:
                    scrollchain = {
                        'version': '1.0',
                        'created_at': timestamp,
                        'entries': [sync_entry]
                    }
                    json.dump(scrollchain, f, indent=2)
            
            # Verify the sync was successful
            if self.verify_sync():
                return True, f"Successfully synchronized registry to ScrollChain at {timestamp}"
            else:
                return False, "Synchronization verification failed"
                
        except Exception as e:
            logger.error(f"Error during registry sync: {e}", exc_info=True)
            return False, f"Synchronization failed: {str(e)}"
    
    def verify_sync(self) -> bool:
        """Verify that the registry is properly synchronized with ScrollChain.
        
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        try:
            # Compute current registry hash
            registry_hash = self._compute_registry_hash()
            if not registry_hash:
                return False
            
            # Check if this hash exists in the scrollchain
            try:
                with open(self.scrollchain_path, 'r') as f:
                    scrollchain = json.load(f)
                    
                return any(
                    e.get('registry_hash') == registry_hash
                    for e in scrollchain.get('entries', [])
                )
                
            except (FileNotFoundError, json.JSONDecodeError):
                return False
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def get_latest_sync(self) -> Optional[Dict[str, Any]]:
        """Get the latest synchronization entry.
        
        Returns:
            The latest sync entry or None if not found
        """
        try:
            with open(self.scrollchain_path, 'r') as f:
                scrollchain = json.load(f)
                entries = scrollchain.get('entries', [])
                if entries:
                    # Sort by timestamp (newest first)
                    sorted_entries = sorted(
                        entries,
                        key=lambda x: x.get('timestamp', ''),
                        reverse=True
                    )
                    return sorted_entries[0]
        except (FileNotFoundError, json.JSONDecodeError, IndexError):
            pass
        return None

# Global instance for convenience
_default_sync = None

def get_scrollchain_sync(
    registry_path: Optional[str] = None,
    scrollchain_path: Optional[str] = None
) -> ScrollChainSync:
    """Get the default ScrollChain sync instance."""
    global _default_sync
    if _default_sync is None:
        _default_sync = ScrollChainSync(registry_path, scrollchain_path)
    return _default_sync

def sync_registry(force: bool = False) -> Tuple[bool, str]:
    """Synchronize the kernel registry with ScrollChain using the default instance.
    
    Args:
        force: If True, force synchronization even if no changes detected
        
    Returns:
        Tuple of (success, message)
    """
    return get_scrollchain_sync().sync_registry(force)

def verify_sync() -> bool:
    """Verify the registry is synchronized with ScrollChain."""
    return get_scrollchain_sync().verify_sync()

def get_latest_sync() -> Optional[Dict[str, Any]]:
    """Get the latest synchronization entry."""
    return get_scrollchain_sync().get_latest_sync()
