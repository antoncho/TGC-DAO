"""
Quantum Kernel Cascade - Total Harmonic Execution Suite

This module provides the main entry point for the enhanced kernel processing system,
integrating document processing, quantum sealing, and ScrollChain synchronization.
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

# Configure logging
logger = logging.getLogger('QuantumCascade')

# Import core components
from .processor_router import process_document, route_document, execute_processor
from .codexscroll_router import link_to_scroll, verify_scroll_link, generate_quantum_anchor
from .enrichment_agent import enrich_document, EnrichmentAgent
from .netsync_scrollchain import sync_registry, verify_sync, get_latest_sync
from .graph_indexer import visualize_graph, get_connected_components

class QuantumKernelCascade:
    """Main class for managing the Quantum Kernel Cascade execution suite."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Quantum Kernel Cascade.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.enrichment_agent = EnrichmentAgent()
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the cascade system.
        
        Returns:
            bool: True if initialization was successful
        """
        if self._initialized:
            return True
            
        try:
            # Initialize enrichment agent
            if not self.enrichment_agent.is_available():
                logger.warning("Enrichment agent is not fully available")
            
            # Verify ScrollChain sync
            if not verify_sync():
                logger.warning("Initial ScrollChain verification failed")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize QuantumKernelCascade: {e}", exc_info=True)
            return False
    
    def process_document(
        self,
        document_path: str,
        context: Optional[Dict] = None,
        enable_enrichment: bool = True,
        enable_scrollchain: bool = True
    ) -> Dict[str, Any]:
        """Process a document through the quantum kernel cascade.
        
        Args:
            document_path: Path to the document to process
            context: Optional context dictionary
            enable_enrichment: Whether to enable AI document enrichment
            enable_scrollchain: Whether to enable ScrollChain integration
            
        Returns:
            Dictionary with processing results
        """
        if not self._initialized:
            self.initialize()
        
        # Prepare context
        if context is None:
            context = {}
            
        # Add cascade-specific context
        context.update({
            'quantum_cascade': True,
            'enable_enrichment': enable_enrichment,
            'enable_scrollchain': enable_scrollchain,
            'processing_start': datetime.utcnow().isoformat(),
            'processing_id': f"cascade_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        })
        
        # Generate quantum seal if not provided
        if 'quantum_seal' not in context:
            context['quantum_seal'] = generate_quantum_anchor(document_path)
        
        try:
            # Process the document
            result = process_document(
                document_path=document_path,
                context=context
            )
            
            # Add cascade metadata
            result.update({
                'quantum_seal': context['quantum_seal'],
                'processing_id': context['processing_id'],
                'cascade_version': '1.0.0',
                'completed_at': datetime.utcnow().isoformat()
            })
            
            # Sync with ScrollChain if enabled
            if enable_scrollchain:
                try:
                    sync_success, sync_msg = sync_registry()
                    result['scrollchain_sync'] = {
                        'success': sync_success,
                        'message': sync_msg,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    logger.error(f"ScrollChain sync failed: {e}", exc_info=True)
            
            return result
            
        except Exception as e:
            error_msg = f"Error in QuantumKernelCascade: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                'success': False,
                'error': error_msg,
                'document': document_path,
                'quantum_seal': context.get('quantum_seal', ''),
                'processing_id': context.get('processing_id', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def visualize_document_graph(
        self,
        output_path: Optional[str] = None,
        show: bool = True
    ) -> Optional[Any]:
        """Generate a visualization of the document graph.
        
        Args:
            output_path: Optional path to save the visualization
            show: Whether to display the visualization
            
        Returns:
            The visualization object if show=False, else None
        """
        try:
            return visualize_graph(output_path=output_path, show=show)
        except Exception as e:
            logger.error(f"Failed to generate document graph: {e}", exc_info=True)
            return None
    
    def get_connected_components(self) -> List[List[str]]:
        """Get connected components in the document graph.
        
        Returns:
            List of connected components, where each component is a list of document IDs
        """
        try:
            return get_connected_components()
        except Exception as e:
            logger.error(f"Failed to get connected components: {e}", exc_info=True)
            return []
    
    def get_processing_status(self, processing_id: str) -> Dict[str, Any]:
        """Get the status of a processing operation.
        
        Args:
            processing_id: The processing ID to look up
            
        Returns:
            Dictionary with status information
        """
        # This would typically query a database or execution registry
        # For now, return a simple response
        return {
            'processing_id': processing_id,
            'status': 'completed',  # or 'in_progress', 'failed', etc.
            'timestamp': datetime.utcnow().isoformat()
        }

# Global instance for convenience
_global_cascade = None

def get_quantum_cascade(config: Optional[Dict] = None) -> 'QuantumKernelCascade':
    """Get the global QuantumKernelCascade instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        The global QuantumKernelCascade instance
    """
    global _global_cascade
    if _global_cascade is None:
        _global_cascade = QuantumKernelCascade(config)
    return _global_cascade

def process_with_cascade(
    document_path: str,
    context: Optional[Dict] = None,
    enable_enrichment: bool = True,
    enable_scrollchain: bool = True
) -> Dict[str, Any]:
    """Process a document using the global QuantumKernelCascade instance.
    
    Args:
        document_path: Path to the document to process
        context: Optional context dictionary
        enable_enrichment: Whether to enable AI document enrichment
        enable_scrollchain: Whether to enable ScrollChain integration
        
    Returns:
        Dictionary with processing results
    """
    cascade = get_quantum_cascade()
    return cascade.process_document(
        document_path=document_path,
        context=context,
        enable_enrichment=enable_enrichment,
        enable_scrollchain=enable_scrollchain
    )

def visualize_cascade_graph(
    output_path: Optional[str] = None,
    show: bool = True
) -> Optional[Any]:
    """Visualize the document graph using the global QuantumKernelCascade instance."""
    return get_quantum_cascade().visualize_document_graph(
        output_path=output_path,
        show=show
    )
