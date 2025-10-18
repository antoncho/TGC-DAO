"""
Legal Kernel

Specialized processor for legal documents and references. Handles:
- Legal citation extraction and validation
- Jurisdiction detection
- Legal concept extraction
- Compliance checking
- Legal document structure analysis
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LegalKernel')

# Kernel metadata
KERNEL_NAME = 'legal'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['legal_document', 'contract', 'regulation', 'statute', 'case_law']

# Common legal patterns
CITATION_PATTERNS = {
    'us_case': r'\b(\d+)\s+U\.?\s*S\.?\s+(\d+)\b',  # 123 U.S. 456
    'us_code': r'\b(\d+)\s+U\.?\s*S\.?\s*C\.?\s+§?\s*(\d+)(?:\(([a-z0-9]+)\))?',  # 5 U.S.C. § 552(a)
    'cfr': r'\b(\d+)\s+C\.?\s*F\.?\s*R\.?\s+(§+)\s*(\d+(?:\.\d+)*)\b',  # 42 C.F.R. § 482.15
    'fr': r'\b(\d+)\s+Fed\.?\s*Reg\.?\s+(\d+)(?:,\s*(\d+))?',  # 84 Fed. Reg. 12345
    'public_law': r'Pub\.?\s*L\.?\s*(?:No\.?\s*)?(\d+)-(\d+)',  # Pub. L. No. 107-296
    'stat': r'\b(\d+)\s+Stat\.?\s+(\d+)\b',  # 122 Stat. 2461
    'european_union': r'(?i)(?:Regulation|Directive|Decision)\s+(?:No\s+)?(\d+/\d+)(?:/\w+)?',  # Regulation (EU) No 2016/679
    'uk_legislation': r'\b(\d{4}\s+[a-zA-Z]+\s+\d+)\b',  # Human Rights Act 1998
}

JURISDICTION_KEYWORDS = {
    'federal': ['united states', 'federal', 'u.s.', 'us', 'u.s.c.', 'cfr', 'congress'],
    'california': ['california', 'ca', 'cal. code', 'cal. civ. code', 'cal. pen. code'],
    'new_york': ['new york', 'n.y.', 'ny', 'n.y. cplr', 'n.y. rpc'],
    'european_union': ['european union', 'eu', 'e.u.', 'regulation eu', 'directive'],
    'uk': ['united kingdom', 'uk', 'u.k.', 'england', 'wales', 'scotland', 'northern ireland', 'act of parliament'],
    'international': ['united nations', 'un', 'wto', 'who', 'icao', 'imo', 'wipo', 'wco']
}

LEGAL_TERMS = {
    'contract': ['party', 'agreement', 'term', 'condition', 'obligation', 'indemnification', 'warranty', 'breach'],
    'intellectual_property': ['copyright', 'trademark', 'patent', 'trade secret', 'license', 'infringement'],
    'privacy': ['gdpr', 'ccpa', 'hipaa', 'pii', 'personal data', 'data protection', 'consent'],
    'corporate': ['board', 'shareholder', 'merger', 'acquisition', 'fiduciary', 'compliance', 'governance'],
    'litigation': ['plaintiff', 'defendant', 'motion', 'discovery', 'deposition', 'subpoena', 'settlement'],
    'regulatory': ['sec', 'fda', 'ftc', 'epa', 'cfpb', 'enforcement', 'investigation', 'subpoena']
}

class LegalCitation:
    """Represents a legal citation."""
    
    def __init__(self, citation_type: str, match: tuple, text: str, start: int, end: int):
        self.type = citation_type
        self.match = match
        self.text = text
        self.start = start
        self.end = end
        self.jurisdiction = self._infer_jurisdiction()
        self.normalized = self._normalize()
    
    def _infer_jurisdiction(self) -> str:
        """Infer the jurisdiction based on citation type and content."""
        if self.type in ['us_case', 'us_code', 'cfr', 'fr', 'public_law', 'stat']:
            return 'federal'
        elif 'european' in self.type:
            return 'european_union'
        elif 'uk_' in self.type:
            return 'uk'
        return 'unknown'
    
    def _normalize(self) -> str:
        """Normalize the citation to a standard format."""
        if self.type == 'us_case':
            vol, page = self.match
            return f"{vol} U.S. {page}"
        elif self.type == 'us_code':
            title, section, subsection = self.match + (None,) * (3 - len(self.match))
            return f"{title} U.S.C. § {section}" + (f"({subsection})" if subsection else "")
        elif self.type == 'cfr':
            title, symbol, section = self.match
            return f"{title} C.F.R. {symbol} {section}"
        return self.text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the citation to a dictionary."""
        return {
            'type': self.type,
            'text': self.text,
            'normalized': self.normalized,
            'jurisdiction': self.jurisdiction,
            'position': {'start': self.start, 'end': self.end}
        }

class LegalProcessor(GenericProcessor):
    """Processor for legal documents and references."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.citations: List[LegalCitation] = []
        self.jurisdictions: Set[str] = set()
        self.legal_terms: Dict[str, List[Dict[str, Any]]] = {}
        self.document_type = 'legal_document'
    
    def extract_citations(self) -> List[Dict[str, Any]]:
        """Extract legal citations from the document."""
        if not self.content:
            return []
        
        for citation_type, pattern in CITATION_PATTERNS.items():
            for match in re.finditer(pattern, self.content, re.IGNORECASE):
                citation = LegalCitation(
                    citation_type=citation_type,
                    match=match.groups(),
                    text=match.group(0),
                    start=match.start(),
                    end=match.end()
                )
                self.citations.append(citation)
                self.jurisdictions.add(citation.jurisdiction)
        
        # Sort citations by position in document
        self.citations.sort(key=lambda x: x.start)
        
        return [c.to_dict() for c in self.citations]
    
    def detect_jurisdictions(self) -> List[str]:
        """Detect jurisdictions mentioned in the document."""
        if not self.content:
            return []
        
        content_lower = self.content.lower()
        
        # Check for jurisdiction keywords
        for jurisdiction, keywords in JURISDICTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    self.jurisdictions.add(jurisdiction)
        
        return list(self.jurisdictions)
    
    def extract_legal_terms(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract and categorize legal terms from the document."""
        if not self.content:
            return {}
        
        content_lower = self.content.lower()
        self.legal_terms = {}
        
        for category, terms in LEGAL_TERMS.items():
            self.legal_terms[category] = []
            for term in terms:
                # Find all occurrences of the term (case insensitive)
                for match in re.finditer(r'\b' + re.escape(term) + r'\b', content_lower, re.IGNORECASE):
                    self.legal_terms[category].append({
                        'term': term,
                        'text': match.group(0),
                        'start': match.start(),
                        'end': match.end(),
                        'context': self._get_context(match.start(), match.end())
                    })
        
        return self.legal_terms
    
    def _get_context(self, start: int, end: int, chars: int = 50) -> str:
        """Get context around a position in the text."""
        if not self.content:
            return ""
        
        context_start = max(0, start - chars)
        context_end = min(len(self.content), end + chars)
        
        # Ensure we don't cut words in the middle
        while context_start > 0 and not self.content[context_start].isspace():
            context_start -= 1
        
        while context_end < len(self.content) and not self.content[context_end].isspace():
            context_end += 1
        
        prefix = "..." if context_start > 0 else ""
        suffix = "..." if context_end < len(self.content) else ""
        
        return f"{prefix}{self.content[context_start:context_end].strip()}{suffix}"
    
    def analyze_document_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the legal document."""
        if not self.content:
            return {}
        
        # Common legal document sections
        section_patterns = {
            'preamble': r'^(?:WHEREAS|PREAMBLE|INTRODUCTION)',
            'definitions': r'\bDEFINITIONS?\b',
            'obligations': r'\bOBLIGATIONS?\b',
            'representations': r'\bREPRESENTATIONS? AND WARRANTIES?\b',
            'indemnification': r'\bINDEMNIFICATION\b',
            'confidentiality': r'\bCONFIDENTIAL(?:ITY)?\b',
            'termination': r'\bTERMINATION\b',
            'governing_law': r'\bGOVERNING LAW\b',
            'jurisdiction': r'\bJURISDICTION\b',
            'miscellaneous': r'\bMISCELLANEOUS\b',
            'signatures': r'\b(?:SIGNATURES?|IN WITNESS WHEREOF|EXECUTED)\b'
        }
        
        sections = {}
        for name, pattern in section_patterns.items():
            match = re.search(pattern, self.content, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[name] = {
                    'position': match.start(),
                    'title': match.group(0).strip()
                }
        
        # Sort sections by position
        sorted_sections = {k: v for k, v in sorted(sections.items(), key=lambda x: x[1]['position'])}
        
        return {
            'sections': sorted_sections,
            'section_count': len(sorted_sections)
        }
    
    def detect_document_type(self) -> str:
        """Detect the type of legal document."""
        if not self.content:
            return 'unknown'
        
        content_lower = self.content.lower()
        
        # Check for common document types
        if any(term in content_lower for term in ['agreement', 'contract', 'license']):
            return 'contract'
        elif any(term in content_lower for term in ['act', 'statute', 'law', 'regulation']):
            return 'statute'
        elif any(term in content_lower for term in ['v.', 'plaintiff', 'defendant', 'court case']):
            return 'case_law'
        elif any(term in content_lower for term in ['policy', 'compliance', 'guideline']):
            return 'policy'
        
        return 'legal_document'
    
    def process(self) -> Dict[str, Any]:
        """Process the legal document and return results."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Detect document type
        self.document_type = self.detect_document_type()
        
        # Extract legal information
        citations = self.extract_citations()
        jurisdictions = self.detect_jurisdictions()
        legal_terms = self.extract_legal_terms()
        structure = self.analyze_document_structure()
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': {
                'document_type': self.document_type,
                'jurisdictions': jurisdictions,
                'citation_count': len(citations),
                'legal_term_categories': list(legal_terms.keys()),
                'section_count': structure.get('section_count', 0),
                'kernel': KERNEL_NAME,
                'kernel_version': KERNEL_VERSION
            },
            'citations': citations,
            'legal_terms': legal_terms,
            'structure': structure,
            'stats': {
                'processing_time': time.time() - start_time,
                'content_length': len(self.content) if self.content else 0,
                'citation_count': len(citations),
                'jurisdiction_count': len(jurisdictions),
                'legal_term_count': sum(len(terms) for terms in legal_terms.values())
            }
        }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'document_type': self.document_type,
                'jurisdictions': jurisdictions,
                'citation_count': len(citations),
                'legal_term_categories': list(legal_terms.keys())
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the legal kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = LegalProcessor(doc_path, context=context)
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
