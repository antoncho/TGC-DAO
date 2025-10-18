"""
Ontology Kernel

Specialized processor for ontology-related documents. Handles:
- Ontology term extraction and validation
- Vocabulary alignment
- Term relationship mapping
- Ontology-based reasoning
"""

import re
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OntologyKernel')

# Kernel metadata
KERNEL_NAME = 'ontology'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['ontology', 'vocabulary', 'taxonomy', 'knowledge_graph']

# Common ontology patterns
TERM_PATTERN = r'\b([A-Z][a-zA-Z0-9_]+)\b'
RELATIONSHIP_PATTERN = r'([a-zA-Z0-9_]+)\s*[:=]\s*([a-zA-Z0-9_]+)'
CLASS_DEF_PATTERN = r'Class:\s*([A-Z][a-zA-Z0-9_]*)'
PROPERTY_DEF_PATTERN = r'Property:\s*([a-z][a-zA-Z0-9_]*)'
INSTANCE_DEF_PATTERN = r'Instance:\s*([A-Z][a-zA-Z0-9_]*)'

class OntologyTerm:
    """Represents a term in an ontology."""
    
    def __init__(self, term_id: str, label: str, term_type: str = 'class'):
        self.id = term_id
        self.label = label
        self.type = term_type  # 'class', 'property', 'instance', etc.
        self.definition = ""
        self.synonyms = []
        self.parents = set()
        self.children = set()
        self.properties = {}
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the term to a dictionary."""
        return {
            'id': self.id,
            'label': self.label,
            'type': self.type,
            'definition': self.definition,
            'synonyms': self.synonyms,
            'parents': list(self.parents),
            'children': list(self.children),
            'properties': self.properties,
            'metadata': self.metadata
        }

class OntologyProcessor(GenericProcessor):
    """Processor for ontology documents."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.terms: Dict[str, OntologyTerm] = {}
        self.relationships = []
        self.vocabularies = set()
        self.imports = set()
        self.prefixes = {}
    
    def extract_terms(self) -> Dict[str, OntologyTerm]:
        """Extract ontology terms from the document."""
        if not self.content:
            return {}
        
        # Look for class definitions
        for match in re.finditer(CLASS_DEF_PATTERN, self.content):
            term_id = match.group(1)
            if term_id not in self.terms:
                self.terms[term_id] = OntologyTerm(term_id, term_id, 'class')
        
        # Look for property definitions
        for match in re.finditer(PROPERTY_DEF_PATTERN, self.content):
            term_id = match.group(1)
            if term_id not in self.terms:
                self.terms[term_id] = OntologyTerm(term_id, term_id, 'property')
        
        # Look for instance definitions
        for match in re.finditer(INSTANCE_DEF_PATTERN, self.content):
            term_id = match.group(1)
            if term_id not in self.terms:
                self.terms[term_id] = OntologyTerm(term_id, term_id, 'instance')
        
        # Look for terms in the content
        for match in re.finditer(TERM_PATTERN, self.content):
            term = match.group(1)
            # Skip common words and numbers
            if len(term) < 3 or term.isdigit() or term.lower() in {'the', 'and', 'for', 'with', 'this', 'that'}:
                continue
            
            # Check if term is already in our dictionary
            if term not in self.terms:
                # Check if it's used in a way that suggests it's a class (capitalized)
                if term[0].isupper():
                    self.terms[term] = OntologyTerm(term, term, 'class')
                else:
                    # Otherwise, assume it's a property
                    self.terms[term] = OntologyTerm(term, term, 'property')
        
        return self.terms
    
    def extract_relationships(self) -> List[Dict[str, str]]:
        """Extract relationships between terms."""
        if not self.content:
            return []
        
        # Look for relationship patterns
        for match in re.finditer(RELATIONSHIP_PATTERN, self.content):
            source, target = match.groups()
            rel = {
                'source': source,
                'target': target,
                'type': 'relatedTo',  # Default relationship type
                'line': self._get_line_number(match.start())
            }
            self.relationships.append(rel)
        
        # Look for subclass relationships
        subclass_pattern = r'([A-Z][a-zA-Z0-9_]*)\s+subClassOf\s+([A-Z][a-zA-Z0-9_]*)'
        for match in re.finditer(subclass_pattern, self.content):
            child, parent = match.groups()
            if child in self.terms and parent in self.terms:
                self.terms[child].parents.add(parent)
                self.terms[parent].children.add(child)
                
                rel = {
                    'source': child,
                    'target': parent,
                    'type': 'subClassOf',
                    'line': self._get_line_number(match.start())
                }
                self.relationships.append(rel)
        
        return self.relationships
    
    def extract_vocabularies(self) -> Set[str]:
        """Extract vocabulary references from the document."""
        if not self.content:
            return set()
        
        # Look for vocabulary imports
        import_pattern = r'imports\s*<([^>]+)>'
        for match in re.finditer(import_pattern, self.content):
            self.imports.add(match.group(1))
        
        # Look for vocabulary prefixes
        prefix_pattern = r'prefix\s+([a-zA-Z0-9_]+):\s*<([^>]+)>'
        for match in re.finditer(prefix_pattern, self.content):
            prefix, uri = match.groups()
            self.prefixes[prefix] = uri
            self.vocabularies.add(uri)
        
        return self.vocabularies
    
    def _get_line_number(self, position: int) -> int:
        """Get the line number for a character position in the content."""
        if not self.content:
            return 0
        return self.content.count('\n', 0, position) + 1
    
    def validate_ontology(self) -> Dict[str, Any]:
        """Validate the ontology structure."""
        validation = {
            'term_count': len(self.terms),
            'class_count': sum(1 for t in self.terms.values() if t.type == 'class'),
            'property_count': sum(1 for t in self.terms.values() if t.type == 'property'),
            'instance_count': sum(1 for t in self.terms.values() if t.type == 'instance'),
            'relationship_count': len(self.relationships),
            'vocabulary_count': len(self.vocabularies),
            'import_count': len(self.imports),
            'issues': []
        }
        
        # Check for terms without definitions
        for term in self.terms.values():
            if not term.definition and not term.parents and not term.children:
                validation['issues'].append({
                    'type': 'missing_definition',
                    'term': term.id,
                    'message': f"Term '{term.id}' has no definition or relationships"
                })
        
        # Check for circular inheritance
        for term_id, term in self.terms.items():
            if self._has_circular_inheritance(term_id, set()):
                validation['issues'].append({
                    'type': 'circular_inheritance',
                    'term': term_id,
                    'message': f"Circular inheritance detected for term '{term_id}'"
                })
        
        # Check for undefined terms in relationships
        for rel in self.relationships:
            if rel['source'] not in self.terms:
                validation['issues'].append({
                    'type': 'undefined_term',
                    'term': rel['source'],
                    'relationship': rel,
                    'message': f"Source term '{rel['source']}' is used in a relationship but not defined"
                })
            if rel['target'] not in self.terms:
                validation['issues'].append({
                    'type': 'undefined_term',
                    'term': rel['target'],
                    'relationship': rel,
                    'message': f"Target term '{rel['target']}' is used in a relationship but not defined"
                })
        
        validation['issue_count'] = len(validation['issues'])
        return validation
    
    def _has_circular_inheritance(self, term_id: str, visited: Set[str]) -> bool:
        """Check for circular inheritance starting from the given term."""
        if term_id in visited:
            return True
        
        visited.add(term_id)
        term = self.terms.get(term_id)
        if not term:
            return False
        
        for parent_id in term.parents:
            if self._has_circular_inheritance(parent_id, visited.copy()):
                return True
        
        return False
    
    def to_networkx(self):
        """Convert the ontology to a NetworkX graph."""
        try:
            import networkx as nx
            
            G = nx.DiGraph()
            
            # Add nodes
            for term_id, term in self.terms.items():
                G.add_node(term_id, **{
                    'label': term.label,
                    'type': term.type,
                    'definition': term.definition,
                    'synonyms': term.synonyms,
                    'metadata': term.metadata
                })
            
            # Add edges
            for rel in self.relationships:
                G.add_edge(
                    rel['source'],
                    rel['target'],
                    type=rel.get('type', 'relatedTo'),
                    label=rel.get('type', 'relatedTo')
                )
            
            return G
            
        except ImportError:
            logger.warning("NetworkX not installed. Install with 'pip install networkx' to enable graph export.")
            return None
    
    def process(self) -> Dict[str, Any]:
        """Process the ontology document and return results."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Extract ontology components
        terms = self.extract_terms()
        relationships = self.extract_relationships()
        vocabularies = self.extract_vocabularies()
        validation = self.validate_ontology()
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': {
                'document_type': 'ontology',
                'term_count': len(terms),
                'relationship_count': len(relationships),
                'vocabulary_count': len(vocabularies),
                'vocabularies': list(vocabularies),
                'imports': list(self.imports),
                'prefixes': self.prefixes,
                'kernel': KERNEL_NAME,
                'kernel_version': KERNEL_VERSION
            },
            'validation': validation,
            'stats': {
                'processing_time': time.time() - start_time,
                'term_count': len(terms),
                'class_count': sum(1 for t in terms.values() if t.type == 'class'),
                'property_count': sum(1 for t in terms.values() if t.type == 'property'),
                'instance_count': sum(1 for t in terms.values() if t.type == 'instance'),
                'relationship_count': len(relationships)
            },
            'terms': {k: v.to_dict() for k, v in terms.items()},
            'relationships': relationships
        }
        
        # Add networkx graph if available
        graph = self.to_networkx()
        if graph is not None:
            result['graph'] = {
                'node_count': len(graph.nodes()),
                'edge_count': len(graph.edges())
            }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'metadata': result['metadata'],
                'validation': validation,
                'stats': result['stats']
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the ontology kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = OntologyProcessor(doc_path, context=context)
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
