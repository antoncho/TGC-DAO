"""
Note Kernel

Specialized processor for note documents. Handles:
- Tag extraction and enrichment
- Research link analysis
- Note linking and backlinking
- Metadata extraction
"""

import re
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NoteKernel')

# Kernel metadata
KERNEL_NAME = 'note'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['note', 'research_note', 'meeting_note', 'personal_note']

# Common patterns for note metadata
TAG_PATTERN = r'#([a-zA-Z0-9_\-\/]+)'
LINK_PATTERN = r'\[\[([^\]]+)\]\]|\[([^\]]+)\]\(([^)]+)\)'
DATE_PATTERN = r'\b(\d{4}-\d{2}-\d{2})\b|\b(\d{1,2}/\d{1,2}/\d{2,4})\b'
TITLE_PATTERN = r'^#\s+(.+)$'
TODO_PATTERN = r'- \[ \]\s*(.+)'
DONE_PATTERN = r'- \[x\]\s*(.+)'

class NoteProcessor(GenericProcessor):
    """Processor for note documents."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.tags = set()
        self.links = []
        self.backlinks = []
        self.todos = []
        self.dones = []
        self.dates = set()
        self.title = ""
        self.frontmatter = {}
    
    def extract_frontmatter(self) -> Dict[str, Any]:
        """Extract YAML frontmatter from the note."""
        import yaml
        
        if not self.content:
            return {}
        
        lines = self.content.splitlines()
        if not lines or not lines[0].startswith('---'):
            return {}
        
        yaml_lines = []
        in_yaml = False
        
        for line in lines[1:]:
            if line.startswith('---'):
                in_yaml = not in_yaml
                if not in_yaml:
                    break
            elif in_yaml:
                yaml_lines.append(line)
        
        if not yaml_lines:
            return {}
        
        try:
            frontmatter = yaml.safe_load('\n'.join(yaml_lines))
            if not isinstance(frontmatter, dict):
                return {}
            self.frontmatter = frontmatter
            return frontmatter
        except Exception as e:
            logger.warning(f"Error parsing YAML frontmatter: {e}")
            return {}
    
    def extract_title(self) -> str:
        """Extract the title from the note."""
        # First try frontmatter
        if self.frontmatter and 'title' in self.frontmatter:
            self.title = str(self.frontmatter['title'])
            return self.title
        
        # Then look for first heading
        if not self.content:
            return ""
        
        for line in self.content.splitlines():
            match = re.match(TITLE_PATTERN, line)
            if match:
                self.title = match.group(1).strip()
                return self.title
        
        # Fall back to filename
        self.title = self.doc_path.stem.replace('_', ' ').title()
        return self.title
    
    def extract_tags(self) -> Set[str]:
        """Extract tags from the note content."""
        if not self.content:
            return set()
        
        # Get tags from frontmatter if present
        if self.frontmatter and 'tags' in self.frontmatter:
            tags = self.frontmatter['tags']
            if isinstance(tags, list):
                self.tags.update(t.strip('#').lower() for t in tags if t)
            elif isinstance(tags, str):
                self.tags.update(t.strip('#').lower() for t in tags.split() if t)
        
        # Get tags from content
        content_tags = set(re.findall(TAG_PATTERN, self.content))
        self.tags.update(t.lower() for t in content_tags)
        
        return self.tags
    
    def extract_links(self) -> List[Dict[str, str]]:
        """Extract wikilinks and markdown links from the note."""
        if not self.content:
            return []
        
        # Find all link patterns
        matches = re.finditer(LINK_PATTERN, self.content)
        
        for match in matches:
            # Handle wikilinks [[...]]
            if match.group(1):
                link_text = match.group(1)
                link_parts = link_text.split('|')
                if len(link_parts) > 1:
                    display_text = link_parts[1]
                    link_target = link_parts[0]
                else:
                    display_text = link_text
                    link_target = link_text
                
                self.links.append({
                    'type': 'wikilink',
                    'target': link_target,
                    'text': display_text,
                    'raw': match.group(0)
                })
            # Handle markdown links [text](url)
            elif match.group(2) and match.group(3):
                self.links.append({
                    'type': 'markdown',
                    'target': match.group(3),
                    'text': match.group(2),
                    'raw': match.group(0)
                })
        
        return self.links
    
    def extract_todos(self) -> List[Dict[str, Any]]:
        """Extract TODO and DONE items from the note."""
        if not self.content:
            return []
        
        for i, line in enumerate(self.content.splitlines()):
            # Check for TODO items
            todo_match = re.match(TODO_PATTERN, line)
            if todo_match:
                self.todos.append({
                    'text': todo_match.group(1).strip(),
                    'line': i + 1,
                    'raw': line.strip()
                })
            
            # Check for DONE items
            done_match = re.match(DONE_PATTERN, line)
            if done_match:
                self.dones.append({
                    'text': done_match.group(1).strip(),
                    'line': i + 1,
                    'raw': line.strip()
                })
        
        return {
            'todos': self.todos,
            'dones': self.dones,
            'total_todos': len(self.todos),
            'total_dones': len(self.dones)
        }
    
    def extract_dates(self) -> Set[str]:
        """Extract dates mentioned in the note."""
        if not self.content:
            return set()
        
        # Find all date patterns
        matches = re.finditer(DATE_PATTERN, self.content)
        
        for match in matches:
            # First group matches YYYY-MM-DD
            if match.group(1):
                self.dates.add(match.group(1))
            # Second group matches MM/DD/YYYY or MM/DD/YY
            elif match.group(2):
                self.dates.add(match.group(2))
        
        return self.dates
    
    def analyze_note_structure(self) -> Dict[str, Any]:
        """Analyze the structure of the note."""
        if not self.content:
            return {}
        
        lines = self.content.splitlines()
        
        # Count different types of elements
        stats = {
            'total_lines': len(lines),
            'non_empty_lines': sum(1 for line in lines if line.strip()),
            'heading_lines': sum(1 for line in lines if re.match(r'^#+\s', line)),
            'code_blocks': len(re.findall(r'```[^`]*```', self.content, re.DOTALL)),
            'images': len(re.findall(r'!\[.*?\]\(.*?\)', self.content)),
            'tables': len(re.findall(r'\|.*\|', self.content)) > 0,  # Simple check
            'word_count': len(re.findall(r'\b\w+\b', self.content)),
            'char_count': len(self.content),
            'link_count': len(self.links),
            'tag_count': len(self.tags)
        }
        
        return stats
    
    def process(self) -> Dict[str, Any]:
        """Process the note document and return results."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Extract metadata and content
        frontmatter = self.extract_frontmatter()
        title = self.extract_title()
        tags = self.extract_tags()
        links = self.extract_links()
        todos = self.extract_todos()
        dates = self.extract_dates()
        stats = self.analyze_note_structure()
        
        # Prepare metadata
        metadata = {
            'title': title,
            'path': str(self.doc_path),
            'filename': self.doc_path.name,
            'directory': str(self.doc_path.parent),
            'created': self.doc_path.stat().st_ctime,
            'modified': self.doc_path.stat().st_mtime,
            'file_size': self.doc_path.stat().st_size,
            'kernel': KERNEL_NAME,
            'kernel_version': KERNEL_VERSION,
            'frontmatter': frontmatter,
            'tags': sorted(list(tags)),
            'dates': sorted(list(dates)),
            'link_count': len(links),
            'tag_count': len(tags),
            'has_todos': len(todos['todos']) > 0,
            'todo_count': len(todos['todos']),
            'done_count': len(todos['dones'])
        }
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': metadata,
            'stats': stats,
            'todos': todos,
            'links': links,
            'tags': sorted(list(tags)),
            'processing_time': time.time() - start_time
        }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'metadata': metadata,
                'stats': stats,
                'todos': todos,
                'link_count': len(links),
                'tag_count': len(tags)
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the note kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = NoteProcessor(doc_path, context=context)
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
