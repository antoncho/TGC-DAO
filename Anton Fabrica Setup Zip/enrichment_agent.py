"""
Enrichment Agent - Uses AI to classify and enhance document metadata.
"""

import json
import os
from typing import Dict, Any, Optional, List

# Configure logging
import logging
logger = logging.getLogger('EnrichmentAgent')

# Try to import OpenAI, but make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available. GPT-based enrichment will be disabled.")

class EnrichmentAgent:
    """Handles document enrichment using AI models."""
    
    def __init__(self, api_key_path: Optional[str] = None, model: str = "gpt-4"):
        """Initialize the enrichment agent.
        
        Args:
            api_key_path: Path to the OpenAI API key file
            model: Name of the model to use for enrichment
        """
        self.model = model
        self._api_key_loaded = False
        
        # Try to load API key
        if api_key_path:
            self.load_api_key(api_key_path)
        elif os.path.exists(".windsurf/openai_key.txt"):
            self.load_api_key(".windsurf/openai_key.txt")
        elif os.environ.get("OPENAI_API_KEY"):
            openai.api_key = os.environ["OPENAI_API_KEY"]
            self._api_key_loaded = True
    
    def load_api_key(self, key_path: str) -> bool:
        """Load OpenAI API key from file.
        
        Args:
            key_path: Path to the API key file
            
        Returns:
            bool: True if key was loaded successfully
        """
        try:
            with open(key_path, 'r') as f:
                openai.api_key = f.read().strip()
            self._api_key_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load API key from {key_path}: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if the enrichment agent is available."""
        return OPENAI_AVAILABLE and self._api_key_loaded
    
    def _call_gpt(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make a call to the GPT model."""
        if not self.is_available():
            raise RuntimeError("OpenAI API is not available")
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document enrichment assistant for the GILC Tesseract system. "
                                             "You analyze documents and extract structured information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error calling GPT model: {e}")
            raise
    
    def enrich_document(self, document_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """Enrich a document with metadata and classifications.
        
        Args:
            document_path: Path to the document
            content: Optional document content (if already loaded)
            
        Returns:
            Dict containing enrichment data
        """
        if content is None:
            try:
                with open(document_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read document for enrichment: {e}")
                content = ""
        
        # Truncate content if too long (to avoid excessive token usage)
        max_content_length = 32000  # ~8K tokens
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n[Document truncated for processing]"
        
        # Prepare the enrichment prompt
        prompt = f"""Analyze the following document and extract structured information.

Document Path: {document_path}

Document Content:
```
{content}
```

Please provide the following information in JSON format:
1. type: Document type (e.g., research, note, legal, ontology, code, spec, proposal)
2. domains: List of relevant domains (e.g., ["math", "quantum", "governance"])
3. summary: A concise summary (1-3 sentences)
4. tags: List of relevant tags
5. suggested_braid_links: List of document paths or IDs that this document references
6. confidence: Your confidence in this analysis (0.0 to 1.0)

Return ONLY valid JSON, no other text."""
        
        try:
            # Get enrichment from GPT
            if self.is_available():
                result_json = self._call_gpt(prompt)
                
                # Parse the JSON response
                try:
                    result = json.loads(result_json)
                    
                    # Ensure required fields
                    if not isinstance(result, dict):
                        raise ValueError("Expected a JSON object")
                    
                    # Set default values for required fields
                    result.setdefault('type', 'document')
                    result.setdefault('domains', [])
                    result.setdefault('summary', '')
                    result.setdefault('tags', [])
                    result.setdefault('suggested_braid_links', [])
                    result.setdefault('confidence', 0.0)
                    
                    # Add enrichment metadata
                    result['_enrichment'] = {
                        'model': self.model,
                        'timestamp': str(datetime.utcnow())
                    }
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GPT response: {e}")
                    logger.debug(f"GPT Response: {result_json}")
                    return self._create_default_enrichment("Failed to parse GPT response")
            else:
                return self._create_default_enrichment("OpenAI API not available")
                
        except Exception as e:
            logger.error(f"Error during document enrichment: {e}")
            return self._create_default_enrichment(str(e))
    
    def _create_default_enrichment(self, error: str) -> Dict[str, Any]:
        """Create a default enrichment result with error information."""
        return {
            'type': 'document',
            'domains': [],
            'summary': '',
            'tags': ['enrichment_failed'],
            'suggested_braid_links': [],
            'confidence': 0.0,
            '_enrichment': {
                'error': error,
                'timestamp': str(datetime.utcnow())
            }
        }

# Global instance for convenience
_default_agent = None

def get_enrichment_agent() -> EnrichmentAgent:
    """Get the default enrichment agent instance."""
    global _default_agent
    if _default_agent is None:
        _default_agent = EnrichmentAgent()
    return _default_agent

def enrich_document(document_path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """Enrich a document using the default enrichment agent.
    
    Args:
        document_path: Path to the document
        content: Optional document content (if already loaded)
        
    Returns:
        Dict containing enrichment data
    """
    return get_enrichment_agent().enrich_document(document_path, content)
