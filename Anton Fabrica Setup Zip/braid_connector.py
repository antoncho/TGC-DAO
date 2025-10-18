"""
Semantic Braid Connector for GILC Tesseract

Manages relationships between documents based on semantic and contextual analysis.
"""

import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict

logger = logging.getLogger('BraidConnector')

class DocumentNode:
    """Represents a document in the semantic braid network."""
    
    def __init__(self, doc_id: str, doc_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Initialize a document node.
        
        Args:
            doc_id: Unique identifier for the document
            doc_path: Path to the document
            metadata: Optional document metadata
        """
        self.id = doc_id
        self.path = str(doc_path)
        self.metadata = metadata or {}
        self.links: List[DocumentLink] = []
        self.embeddings: Dict[str, List[float]] = {}
        self.tags: Set[str] = set()
        
        # Extract basic metadata
        self.title = self.metadata.get('title', Path(doc_path).stem)
        self.doc_type = self.metadata.get('type', 'document')
        
        # Generate a stable ID if not provided
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a stable ID for the document."""
        content = f"{self.path}:{self.title}:{self.doc_type}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def add_link(self, target: 'DocumentNode', link_type: str, weight: float = 1.0, 
                metadata: Optional[Dict[str, Any]] = None) -> 'DocumentLink':
        """Add a link to another document.
        
        Args:
            target: Target document node
            link_type: Type of relationship (e.g., 'references', 'similar_to')
            weight: Strength of the relationship (0.0 to 1.0)
            metadata: Additional metadata about the relationship
            
        Returns:
            The created DocumentLink
        """
        link = DocumentLink(source=self, target=target, link_type=link_type, 
                          weight=weight, metadata=metadata or {})
        self.links.append(link)
        return link
    
    def get_links(self, link_type: Optional[str] = None) -> List['DocumentLink']:
        """Get all links, optionally filtered by type.
        
        Args:
            link_type: Optional link type filter
            
        Returns:
            List of matching DocumentLinks
        """
        if link_type is None:
            return list(self.links)
        return [link for link in self.links if link.link_type == link_type]
    
    def add_embedding(self, model_name: str, embedding: List[float]) -> None:
        """Add a vector embedding for this document.
        
        Args:
            model_name: Name of the embedding model
            embedding: Vector embedding
        """
        self.embeddings[model_name] = embedding
    
    def get_embedding(self, model_name: str) -> Optional[List[float]]:
        """Get a stored embedding by model name.
        
        Args:
            model_name: Name of the embedding model
            
        Returns:
            The embedding vector, or None if not found
        """
        return self.embeddings.get(model_name)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this document."""
        self.tags.add(tag.lower())
    
    def has_tag(self, tag: str) -> bool:
        """Check if this document has a specific tag."""
        return tag.lower() in self.tags


class DocumentLink:
    """Represents a relationship between two documents."""
    
    def __init__(self, source: DocumentNode, target: DocumentNode, link_type: str, 
                 weight: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        """Initialize a document link.
        
        Args:
            source: Source document node
            target: Target document node
            link_type: Type of relationship
            weight: Strength of the relationship (0.0 to 1.0)
            metadata: Additional metadata about the relationship
        """
        self.source = source
        self.target = target
        self.link_type = link_type
        self.weight = max(0.0, min(1.0, weight))  # Clamp to [0.0, 1.0]
        self.metadata = metadata or {}
        
        # Add reverse link for bidirectional relationships
        if self.link_type in ['similar_to', 'related_to']:
            reverse_link = DocumentLink(
                source=target,
                target=source,
                link_type=link_type,
                weight=weight,
                metadata=metadata
            )
            target.links.append(reverse_link)


class SemanticBraid:
    """Manages a network of interconnected documents with semantic relationships."""
    
    def __init__(self):
        """Initialize an empty semantic braid."""
        self.nodes: Dict[str, DocumentNode] = {}
        self.link_types: Set[str] = set()
        self.tag_index: Dict[str, Set[DocumentNode]] = defaultdict(set)
    
    def add_document(self, doc_id: str, doc_path: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> DocumentNode:
        """Add a document to the braid.
        
        Args:
            doc_id: Unique identifier for the document
            doc_path: Path to the document
            metadata: Optional document metadata
            
        Returns:
            The created DocumentNode
        """
        if doc_id in self.nodes:
            logger.warning(f"Document with ID {doc_id} already exists, updating")
            
        node = DocumentNode(doc_id, doc_path, metadata)
        self.nodes[doc_id] = node
        
        # Update tag index
        for tag in node.tags:
            self.tag_index[tag].add(node)
            
        return node
    
    def get_document(self, doc_id: str) -> Optional[DocumentNode]:
        """Get a document by ID."""
        return self.nodes.get(doc_id)
    
    def find_documents_by_tag(self, tag: str) -> List[DocumentNode]:
        """Find documents with a specific tag."""
        return list(self.tag_index.get(tag.lower(), set()))
    
    def link_documents(self, source_id: str, target_id: str, link_type: str, 
                      weight: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> Optional[DocumentLink]:
        """Create a link between two documents.
        
        Args:
            source_id: Source document ID
            target_id: Target document ID
            link_type: Type of relationship
            weight: Strength of the relationship (0.0 to 1.0)
            metadata: Additional metadata about the relationship
            
        Returns:
            The created DocumentLink, or None if either document doesn't exist
        """
        source = self.get_document(source_id)
        target = self.get_document(target_id)
        
        if not source or not target:
            logger.warning(f"Could not create link: source or target document not found")
            return None
            
        self.link_types.add(link_type)
        return source.add_link(target, link_type, weight, metadata)
    
    def find_related_documents(self, doc_id: str, link_type: Optional[str] = None, 
                             min_weight: float = 0.0) -> List[Tuple[DocumentNode, float]]:
        """Find documents related to a given document.
        
        Args:
            doc_id: Source document ID
            link_type: Optional link type filter
            min_weight: Minimum relationship weight (inclusive)
            
        Returns:
            List of (document, weight) tuples, sorted by weight descending
        """
        node = self.get_document(doc_id)
        if not node:
            return []
            
        related = []
        for link in node.links:
            if (link_type is None or link.link_type == link_type) and link.weight >= min_weight:
                related.append((link.target, link.weight))
        
        # Sort by weight descending
        return sorted(related, key=lambda x: x[1], reverse=True)
    
    def get_shortest_path(self, source_id: str, target_id: str, 
                         max_hops: int = 5) -> Optional[List[DocumentNode]]:
        """Find the shortest path between two documents.
        
        Uses breadth-first search.
        
        Args:
            source_id: Starting document ID
            target_id: Target document ID
            max_hops: Maximum number of hops to search
            
        Returns:
            List of documents in the path, or None if no path found
        """
        source = self.get_document(source_id)
        target = self.get_document(target_id)
        
        if not source or not target:
            return None
            
        if source == target:
            return [source]
            
        # BFS setup
        from collections import deque
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue and max_hops >= 0:
            current, path = queue.popleft()
            
            for link in current.links:
                if link.target not in visited:
                    if link.target == target:
                        return path + [target]
                        
                    visited.add(link.target)
                    queue.append((link.target, path + [link.target]))
            
            max_hops -= 1
            
        return None


def create_semantic_braid() -> SemanticBraid:
    """Create a new SemanticBraid instance."""
    return SemanticBraid()


# Global instance for convenience
default_braid = create_semantic_braid()
