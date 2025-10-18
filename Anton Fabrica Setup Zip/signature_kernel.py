"""
Signature Kernel

Specialized processor for handling document signatures and integrity verification.
Handles:
- Quantum-sealed signature verification
- Document integrity checks
- Signature chain validation
- Timestamp verification
"""

import re
import json
import base64
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timezone

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SignatureKernel')

# Kernel metadata
KERNEL_NAME = 'signature'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['signed_document', 'quantum_seal', 'signature_block']

# Signature patterns
SIGNATURE_BLOCK_PATTERN = r'<!-- SIGNATURE BLOCK\n([\s\S]*?)\n-->'
SEAL_PATTERN = r'<!-- SEAL:([a-f0-9]+) -->'
TIMESTAMP_PATTERN = r'<!-- TIMESTAMP:(\d+) -->'
SIGNER_PATTERN = r'<!-- SIGNER:([^\n]+) -->'
SIGNATURE_PATTERN = r'<!-- SIGNATURE:([a-f0-9]+) -->'

class SignatureVerificationError(Exception):
    """Exception raised for signature verification errors."""
    pass

class DocumentIntegrityError(Exception):
    """Exception raised for document integrity errors."""
    pass

class QuantumSealVerifier:
    """Verifies quantum-sealed signatures."""
    
    def __init__(self, public_key: Optional[str] = None):
        """Initialize with an optional public key for verification."""
        self.public_key = public_key
    
    def verify_seal(self, content: str, seal: str) -> bool:
        """
        Verify a quantum seal against document content.
        
        Args:
            content: The content that was sealed
            seal: The seal to verify
            
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        try:
            # In a real implementation, this would verify a quantum-resistant signature
            # For now, we'll use a simple hash-based verification
            expected_seal = self._generate_seal(content)
            return seal == expected_seal
        except Exception as e:
            logger.error(f"Error verifying seal: {e}")
            return False
    
    def _generate_seal(self, content: str) -> str:
        """Generate a seal for the given content."""
        # In a real implementation, this would use a quantum-resistant hash function
        # and potentially include additional metadata
        h = hashlib.sha3_256()
        h.update(content.encode('utf-8'))
        return h.hexdigest()
    
    def verify_signature(self, content: str, signature: str, public_key: Optional[str] = None) -> bool:
        """
        Verify a signature against content using the provided or instance public key.
        
        Args:
            content: The content that was signed
            signature: The signature to verify
            public_key: Optional public key to use (overrides instance key)
            
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        pub_key = public_key or self.public_key
        if not pub_key:
            raise ValueError("No public key provided for verification")
        
        try:
            # In a real implementation, this would verify a quantum-resistant signature
            # For now, we'll use a simple check that the signature is a valid hex string
            return all(c in '0123456789abcdef' for c in signature.lower())
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

class SignatureProcessor(GenericProcessor):
    """Processor for document signatures and integrity verification."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.signature_blocks = []
        self.seals = []
        self.timestamps = []
        self.signers = []
        self.signatures = []
        self.verifier = QuantumSealVerifier()
        self.original_content = ""
        self.signed_content = ""
    
    def extract_signature_blocks(self) -> List[Dict[str, Any]]:
        """Extract signature blocks from the document."""
        if not self.content:
            return []
        
        # Find all signature blocks
        for match in re.finditer(SIGNATURE_BLOCK_PATTERN, self.content):
            block = match.group(1)
            block_data = {
                'full_match': match.group(0),
                'content': block,
                'start': match.start(),
                'end': match.end(),
                'seal': None,
                'timestamp': None,
                'signer': None,
                'signature': None
            }
            
            # Extract seal if present
            seal_match = re.search(SEAL_PATTERN, block)
            if seal_match:
                block_data['seal'] = seal_match.group(1)
                self.seals.append(block_data['seal'])
            
            # Extract timestamp if present
            ts_match = re.search(TIMESTAMP_PATTERN, block)
            if ts_match:
                timestamp = int(ts_match.group(1))
                block_data['timestamp'] = timestamp
                block_data['timestamp_iso'] = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
                self.timestamps.append(timestamp)
            
            # Extract signer if present
            signer_match = re.search(SIGNER_PATTERN, block)
            if signer_match:
                block_data['signer'] = signer_match.group(1)
                self.signers.append(block_data['signer'])
            
            # Extract signature if present
            sig_match = re.search(SIGNATURE_PATTERN, block)
            if sig_match:
                block_data['signature'] = sig_match.group(1)
                self.signatures.append(block_data['signature'])
            
            self.signature_blocks.append(block_data)
        
        return self.signature_blocks
    
    def separate_content_from_signatures(self) -> Tuple[str, str]:
        """
        Separate the original content from signature blocks.
        
        Returns:
            Tuple of (original_content, signature_blocks)
        """
        if not self.content:
            return "", ""
        
        if not self.signature_blocks:
            return self.content, ""
        
        # Sort signature blocks by start position
        sorted_blocks = sorted(self.signature_blocks, key=lambda x: x['start'])
        
        # The original content is everything before the first signature block
        first_block_start = sorted_blocks[0]['start']
        original_content = self.content[:first_block_start].rstrip()
        
        # The signature blocks are everything from the first signature block to the end
        signature_blocks = self.content[first_block_start:].strip()
        
        self.original_content = original_content
        self.signed_content = signature_blocks
        
        return original_content, signature_blocks
    
    def verify_document_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the document and its signatures."""
        if not self.signature_blocks:
            return {
                'verified': False,
                'error': 'No signature blocks found',
                'details': []
            }
        
        results = []
        all_verified = True
        
        # Separate content from signatures if not already done
        if not self.original_content:
            self.separate_content_from_signatures()
        
        for block in self.signature_blocks:
            block_result = {
                'position': f"{block['start']}-{block['end']}",
                'seal_verified': None,
                'signature_verified': None,
                'timestamp': block.get('timestamp_iso'),
                'signer': block.get('signer'),
                'errors': []
            }
            
            # Verify seal if present
            if block['seal']:
                try:
                    block_result['seal_verified'] = self.verifier.verify_seal(
                        self.original_content, 
                        block['seal']
                    )
                    if not block_result['seal_verified']:
                        block_result['errors'].append('Seal verification failed')
                except Exception as e:
                    block_result['errors'].append(f'Seal verification error: {str(e)}')
            
            # Verify signature if present
            if block['signature'] and block['signer']:
                try:
                    # In a real implementation, we would use the signer's public key
                    # For now, we'll just check the signature format
                    block_result['signature_verified'] = self.verifier.verify_signature(
                        self.original_content,
                        block['signature'],
                        public_key=f"public_key_for_{block['signer']}"
                    )
                    if not block_result['signature_verified']:
                        block_result['errors'].append('Signature verification failed')
                except Exception as e:
                    block_result['errors'].append(f'Signature verification error: {str(e)}')
            
            # Check timestamp if present
            if block.get('timestamp'):
                # Verify the timestamp is not in the future
                current_time = datetime.now(timezone.utc).timestamp()
                if block['timestamp'] > current_time:
                    block_result['errors'].append('Timestamp is in the future')
            
            # Update overall verification status
            block_result['verified'] = not block_result['errors']
            if not block_result['verified']:
                all_verified = False
            
            results.append(block_result)
        
        return {
            'verified': all_verified,
            'signature_blocks': len(self.signature_blocks),
            'verified_blocks': sum(1 for r in results if r.get('verified', False)),
            'details': results
        }
    
    def check_timestamp_chain(self) -> Dict[str, Any]:
        """Check the temporal consistency of timestamps in signature blocks."""
        if not self.timestamps:
            return {
                'verified': False,
                'error': 'No timestamps found',
                'details': []
            }
        
        # Sort timestamps
        sorted_timestamps = sorted(self.timestamps)
        
        # Check if timestamps are in chronological order
        is_chronological = all(
            sorted_timestamps[i] <= sorted_timestamps[i+1] 
            for i in range(len(sorted_timestamps)-1)
        )
        
        # Check for duplicate timestamps
        has_duplicates = len(sorted_timestamps) != len(set(sorted_timestamps))
        
        return {
            'verified': is_chronological and not has_duplicates,
            'is_chronological': is_chronological,
            'has_duplicates': has_duplicates,
            'timestamp_count': len(sorted_timestamps),
            'earliest': datetime.fromtimestamp(min(self.timestamps), tz=timezone.utc).isoformat() if self.timestamps else None,
            'latest': datetime.fromtimestamp(max(self.timestamps), tz=timezone.utc).isoformat() if self.timestamps else None
        }
    
    def process(self) -> Dict[str, Any]:
        """Process the document for signatures and integrity verification."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Extract signature blocks and separate content
        signature_blocks = self.extract_signature_blocks()
        original_content, signed_content = self.separate_content_from_signatures()
        
        # Perform verifications
        integrity_check = self.verify_document_integrity()
        timestamp_check = self.check_timestamp_chain()
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': {
                'document_type': 'signed_document',
                'content_length': len(original_content),
                'signature_block_count': len(signature_blocks),
                'unique_signers': list(set(self.signers)) if self.signers else [],
                'kernel': KERNEL_NAME,
                'kernel_version': KERNEL_VERSION
            },
            'integrity_check': integrity_check,
            'timestamp_check': timestamp_check,
            'stats': {
                'processing_time': time.time() - start_time,
                'content_size': len(original_content),
                'signature_blocks': len(signature_blocks),
                'seals_found': len(self.seals),
                'signatures_found': len(self.signatures),
                'signers_found': len(self.signers),
                'timestamps_found': len(self.timestamps)
            },
            'signature_blocks': signature_blocks
        }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'verified': integrity_check.get('verified', False) and timestamp_check.get('verified', False),
                'signature_blocks': len(signature_blocks),
                'signers': list(set(self.signers)) if self.signers else [],
                'timestamps': self.timestamps
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the signature kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = SignatureProcessor(doc_path, context=context)
    return processor.process()

# Register this kernel
register_kernel(KERNEL_NAME, sys.modules[__name__])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
        print(f"Processing document with {KERNEL_NAME} kernel: {doc_path}")
        result = process(doc_path)
        print("Processing complete. Results:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Usage: python -m kernels.{KERNEL_NAME}_kernel <document_path>")
        sys.exit(1)
