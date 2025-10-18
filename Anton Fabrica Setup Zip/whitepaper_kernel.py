"""
Whitepaper Kernel

Specialized processor for whitepaper documents. Handles:
- Structure validation
- Abstract extraction
- Braid binding
- Metadata enrichment
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WhitepaperKernel')

# Kernel metadata
KERNEL_NAME = 'whitepaper'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['whitepaper', 'research_paper', 'technical_report']

# Whitepaper section patterns
SECTION_PATTERNS = {
    'title': r'^#\s+(.+)$',
    'authors': r'^##?\s*Authors?\s*##?\s*$',
    'abstract': r'^##?\s*Abstract\s*##?\s*$',
    'introduction': r'^##\s*Introduction\s*$',
    'background': r'^##\s*Background|Related Work\s*$',
    'methodology': r'^##\s*Methodology|Approach\s*$',
    'results': r'^##\s*Results|Findings\s*$',
    'discussion': r'^##\s*Discussion\s*$',
    'conclusion': r'^##\s*Conclusion|Summary\s*$',
    'references': r'^##?\s*References?\s*$',
    'appendix': r'^##\s*Appendix\s*$',
}

class WhitepaperProcessor(GenericProcessor):
    """Processor for whitepaper documents."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.sections = {}
        self.references = []
        self.citations = []
    
    def extract_sections(self) -> Dict[str, str]:
        """Extract sections from the whitepaper content."""
        if not self.content:
            return {}
        
        sections = {}
        current_section = None
        current_content = []
        
        # Split content into lines and process each line
        lines = self.content.splitlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            section_found = False
            for section_name, pattern in SECTION_PATTERNS.items():
                if re.match(pattern, line, re.IGNORECASE):
                    # Save previous section if any
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            # If not a section header, add to current section
            if not section_found and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        self.sections = sections
        return sections
    
    def extract_metadata_from_sections(self) -> Dict[str, Any]:
        """Extract metadata from document sections."""
        metadata = {}
        
        # Extract title
        if 'title' in self.sections:
            metadata['title'] = self.sections['title']
        
        # Extract authors
        if 'authors' in self.sections:
            authors_text = self.sections['authors']
            # Simple author extraction - can be enhanced
            authors = [a.strip() for a in re.split(r'[,\n]', authors_text) if a.strip()]
            metadata['authors'] = authors
        
        # Extract abstract
        if 'abstract' in self.sections:
            metadata['abstract'] = self.sections['abstract']
        
        # Extract keywords if present
        if 'keywords' in self.sections:
            keywords = [k.strip() for k in self.sections['keywords'].split(',') if k.strip()]
            metadata['keywords'] = keywords
        
        # Extract date if present
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})'  # DD Month YYYY
        ]
        
        for section in self.sections.values():
            for pattern in date_patterns:
                match = re.search(pattern, section)
                if match:
                    metadata['date'] = match.group(1)
                    break
            if 'date' in metadata:
                break
        
        return metadata
    
    def extract_references(self) -> List[Dict[str, str]]:
        """Extract references from the references section."""
        if 'references' not in self.sections:
            return []
        
        references = []
        ref_text = self.sections['references']
        
        # Simple reference extraction - can be enhanced with more sophisticated parsing
        ref_entries = re.split(r'\n\s*\d+\.\s*|\n\[\d+\]\s*', ref_text)
        
        for ref in ref_entries:
            ref = ref.strip()
            if not ref:
                continue
                
            # Try to extract DOI, URL, etc.
            doi_match = re.search(r'doi:\s*([^\s\]]+)', ref, re.IGNORECASE)
            url_match = re.search(r'(https?://[^\s\]]+)', ref)
            
            ref_data = {
                'text': ref,
                'doi': doi_match.group(1) if doi_match else None,
                'url': url_match.group(1) if url_match else None
            }
            
            references.append(ref_data)
        
        self.references = references
        return references
    
    def extract_citations(self) -> List[Dict[str, Any]]:
        """Extract citations from the document."""
        # This is a simplified version - would need more sophisticated parsing
        # for different citation styles
        citations = []
        
        # Look for patterns like [1], [2-4], [Smith 2020], etc.
        citation_patterns = [
            r'\[([\d,\s-]+)\]',  # [1], [1,2], [1-3]
            r'\(([A-Za-z]+\s*\d{4}[a-z]?)\)',  # (Smith 2020)
            r'([A-Z][a-z]+\s+et\.?\s*al\.?\s*\d{4})'  # Smith et al. 2020
        ]
        
        for section_name, section_content in self.sections.items():
            for pattern in citation_patterns:
                for match in re.finditer(pattern, section_content):
                    citations.append({
                        'citation': match.group(0),
                        'section': section_name,
                        'position': match.start()
                    })
        
        self.citations = citations
        return citations
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate the structure of the whitepaper."""
        validation = {
            'has_title': 'title' in self.sections,
            'has_authors': 'authors' in self.sections,
            'has_abstract': 'abstract' in self.sections,
            'has_introduction': 'introduction' in self.sections,
            'has_conclusion': 'conclusion' in self.sections,
            'has_references': 'references' in self.sections,
            'sections_found': list(self.sections.keys()),
            'sections_missing': [s for s in ['title', 'abstract', 'introduction', 'conclusion', 'references'] 
                               if s not in self.sections]
        }
        
        # Calculate a simple validation score
        required_sections = ['title', 'abstract', 'introduction', 'conclusion', 'references']
        validation_score = sum(1 for s in required_sections if s in self.sections) / len(required_sections)
        validation['validation_score'] = validation_score
        
        return validation
    
    def process(self) -> Dict[str, Any]:
        """Process the whitepaper document and return results."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Extract sections and metadata
        self.extract_sections()
        metadata = self.extract_metadata_from_sections()
        references = self.extract_references()
        citations = self.extract_citations()
        validation = self.validate_structure()
        
        # Update metadata with additional fields
        metadata.update({
            'document_type': 'whitepaper',
            'reference_count': len(references),
            'citation_count': len(citations),
            'section_count': len(self.sections),
            'sections': list(self.sections.keys())
        })
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': metadata,
            'validation': validation,
            'stats': {
                'sections_found': len(self.sections),
                'references_found': len(references),
                'citations_found': len(citations),
                'processing_time': time.time() - start_time
            },
            'sections': self.sections,
            'references': references,
            'citations': citations
        }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'metadata': metadata,
                'validation': validation,
                'stats': result['stats']
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the whitepaper kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = WhitepaperProcessor(doc_path, context=context)
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
