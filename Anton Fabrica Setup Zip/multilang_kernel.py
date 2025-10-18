"""
Multilingual Kernel

Specialized processor for handling multilingual content. Handles:
- Language detection
- Translation alignment
- Script conversion
- Multilingual term consistency
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set

# Import the kernel registry
from . import register_kernel
from .generic_kernel import GenericProcessor

# Try to import language detection libraries
try:
    import langdetect
    from langdetect import detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect not available. Install with 'pip install langdetect' for language detection.")

try:
    import langid
    LANGID_AVAILABLE = True
except ImportError:
    LANGID_AVAILABLE = False
    logger.warning("langid not available. Install with 'pip install langid' for language detection.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MultilangKernel')

# Kernel metadata
KERNEL_NAME = 'multilang'
KERNEL_VERSION = '1.0.0'
SUPPORTED_TYPES = ['multilingual', 'translation', 'localization']

# Common language codes and names
LANGUAGE_CODES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'or': 'Odia',
    'ml': 'Malayalam',
    'sa': 'Sanskrit',
    'el': 'Greek',
    'he': 'Hebrew',
    'la': 'Latin'
}

# Script detection patterns
SCRIPT_PATTERNS = {
    'latin': r'[a-zA-Z]',
    'cyrillic': r'[\u0400-\u04FF]',
    'arabic': r'[\u0600-\u06FF]',
    'devanagari': r'[\u0900-\u097F]',
    'bengali': r'[\u0980-\u09FF]',
    'tamil': r'[\u0B80-\u0BFF]',
    'telugu': r'[\u0C00-\u0C7F]',
    'gujarati': r'[\u0A80-\u0AFF]',
    'gurmukhi': r'[\u0A00-\u0A7F]',
    'kannada': r'[\u0C80-\u0CFF]',
    'malayalam': r'[\u0D00-\u0D7F]',
    'thai': r'[\u0E00-\u0E7F]',
    'chinese': r'[\u4E00-\u9FFF]',
    'japanese': r'[\u3040-\u30FF]',
    'korean': r'[\uAC00-\uD7AF]',
    'greek': r'[\u0370-\u03FF]',
    'hebrew': r'[\u0590-\u05FF]',
    'latin_extended': r'[\u0100-\u017F]'
}

class LanguageDetectionResult:
    """Represents the result of language detection."""
    
    def __init__(self, language: str, confidence: float, method: str):
        self.language = language
        self.confidence = confidence
        self.method = method
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'language': self.language,
            'language_name': LANGUAGE_CODES.get(self.language, 'Unknown'),
            'confidence': self.confidence,
            'method': self.method
        }

class ScriptDetectionResult:
    """Represents the result of script detection."""
    
    def __init__(self, script: str, confidence: float):
        self.script = script
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'script': self.script,
            'confidence': self.confidence
        }

class MultilingualProcessor(GenericProcessor):
    """Processor for multilingual content."""
    
    def __init__(self, doc_path: str, context: Optional[Dict] = None):
        """Initialize the processor with a document path and optional context."""
        super().__init__(doc_path, context)
        self.languages = []
        self.scripts = []
        self.translation_units = []
        self.detected_language = None
        self.detection_confidence = 0.0
    
    def detect_language(self) -> List[Dict[str, Any]]:
        """Detect the language of the document content."""
        if not self.content:
            return []
        
        results = []
        
        # Use langdetect if available
        if LANGDETECT_AVAILABLE:
            try:
                detections = detect_langs(self.content)
                for detection in detections:
                    results.append(LanguageDetectionResult(
                        language=detection.lang,
                        confidence=detection.prob,
                        method='langdetect'
                    ).to_dict())
            except Exception as e:
                logger.warning(f"Error in langdetect: {e}")
        
        # Use langid if available
        if LANGID_AVAILABLE and not results:
            try:
                lang, confidence = langid.classify(self.content)
                results.append(LanguageDetectionResult(
                    language=lang,
                    confidence=confidence,
                    method='langid'
                ).to_dict())
            except Exception as e:
                logger.warning(f"Error in langid: {e}")
        
        # Fallback to simple character-based detection
        if not results:
            # Count characters from different scripts
            script_counts = {}
            total = 0
            
            for script, pattern in SCRIPT_PATTERNS.items():
                count = len(re.findall(pattern, self.content))
                if count > 0:
                    script_counts[script] = count
                    total += count
            
            # If we found any scripts, use the most common one to guess language
            if script_counts:
                most_common = max(script_counts.items(), key=lambda x: x[1])
                script, count = most_common
                confidence = count / total if total > 0 else 0.0
                
                # Map script to likely language
                script_to_lang = {
                    'latin': 'en',
                    'cyrillic': 'ru',
                    'arabic': 'ar',
                    'devanagari': 'hi',
                    'bengali': 'bn',
                    'tamil': 'ta',
                    'telugu': 'te',
                    'gujarati': 'gu',
                    'gurmukhi': 'pa',
                    'kannada': 'kn',
                    'malayalam': 'ml',
                    'thai': 'th',
                    'chinese': 'zh',
                    'japanese': 'ja',
                    'korean': 'ko',
                    'greek': 'el',
                    'hebrew': 'he'
                }
                
                lang = script_to_lang.get(script, 'en')
                results.append(LanguageDetectionResult(
                    language=lang,
                    confidence=confidence,
                    method='script_analysis'
                ).to_dict())
        
        # Store the primary detection result
        if results:
            self.detected_language = results[0]['language']
            self.detection_confidence = results[0]['confidence']
        
        self.languages = results
        return results
    
    def detect_scripts(self) -> List[Dict[str, Any]]:
        """Detect scripts used in the document."""
        if not self.content:
            return []
        
        script_counts = {}
        total = 0
        
        # Count characters from different scripts
        for script, pattern in SCRIPT_PATTERNS.items():
            count = len(re.findall(pattern, self.content))
            if count > 0:
                script_counts[script] = count
                total += count
        
        # Calculate confidence for each script
        results = []
        for script, count in script_counts.items():
            confidence = count / total if total > 0 else 0.0
            results.append(ScriptDetectionResult(
                script=script,
                confidence=confidence
            ).to_dict())
        
        # Sort by confidence (descending)
        results.sort(key=lambda x: x['confidence'], reverse=True)
        self.scripts = results
        return results
    
    def extract_translation_units(self) -> List[Dict[str, Any]]:
        """Extract translation units from the document."""
        if not self.content:
            return []
        
        # Simple implementation - look for translation pairs
        # This could be enhanced to handle specific formats like XLIFF, TMX, etc.
        translation_units = []
        
        # Look for patterns like:
        # en: Hello
        # es: Hola
        # 
        # or [en] Hello
        # [es] Hola
        
        # Pattern 1: Language code followed by colon
        pattern1 = r'^([a-z]{2,3}):\s*(.+?)(?:\n|$)'
        
        # Pattern 2: Language code in brackets
        pattern2 = r'^\[([a-z]{2,3})\]\s*(.+?)(?:\n|$)'
        
        # Process the content line by line
        current_lang = None
        current_text = ""
        
        for line in self.content.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Try pattern 1
            match1 = re.match(pattern1, line, re.IGNORECASE)
            if match1:
                lang, text = match1.groups()
                if current_lang and current_text:
                    translation_units.append({
                        'language': current_lang,
                        'text': current_text.strip()
                    })
                current_lang = lang.lower()
                current_text = text
                continue
                
            # Try pattern 2
            match2 = re.match(pattern2, line, re.IGNORECASE)
            if match2:
                lang, text = match2.groups()
                if current_lang and current_text:
                    translation_units.append({
                        'language': current_lang,
                        'text': current_text.strip()
                    })
                current_lang = lang.lower()
                current_text = text
                continue
                
            # If we're in a translation unit, append to current text
            if current_lang:
                current_text += "\n" + line
        
        # Add the last translation unit
        if current_lang and current_text:
            translation_units.append({
                'language': current_lang,
                'text': current_text.strip()
            })
        
        self.translation_units = translation_units
        return translation_units
    
    def check_term_consistency(self) -> Dict[str, Any]:
        """Check consistency of terms across translations."""
        if not self.translation_units:
            return {}
        
        # Group translations by language
        lang_groups = {}
        for unit in self.translation_units:
            lang = unit['language']
            if lang not in lang_groups:
                lang_groups[lang] = []
            lang_groups[lang].append(unit['text'])
        
        # For now, just return the language groups
        # In a real implementation, we would analyze term consistency
        return {
            'languages_found': list(lang_groups.keys()),
            'translation_unit_count': len(self.translation_units),
            'language_groups': {k: len(v) for k, v in lang_groups.items()}
        }
    
    def process(self) -> Dict[str, Any]:
        """Process the document for multilingual analysis."""
        import time
        start_time = time.time()
        
        if not self.load_document():
            return {'success': False, 'error': 'Failed to load document'}
        
        # Perform multilingual analysis
        languages = self.detect_language()
        scripts = self.detect_scripts()
        translation_units = self.extract_translation_units()
        term_consistency = self.check_term_consistency()
        
        # Prepare result
        result = {
            'success': True,
            'kernel': KERNEL_NAME,
            'metadata': {
                'detected_language': self.detected_language,
                'detection_confidence': self.detection_confidence,
                'language_name': LANGUAGE_CODES.get(self.detected_language, 'Unknown') if self.detected_language else 'Unknown',
                'script_count': len(scripts),
                'translation_unit_count': len(translation_units),
                'kernel': KERNEL_NAME,
                'kernel_version': KERNEL_VERSION
            },
            'languages': languages,
            'scripts': scripts,
            'translation_units': translation_units,
            'term_consistency': term_consistency,
            'stats': {
                'processing_time': time.time() - start_time,
                'content_length': len(self.content) if self.content else 0,
                'language_count': len(languages),
                'script_count': len(scripts),
                'translation_unit_count': len(translation_units)
            }
        }
        
        # Update context if provided
        if self.context is not None:
            if 'processing' not in self.context:
                self.context['processing'] = {}
            self.context['processing'][KERNEL_NAME] = {
                'detected_language': self.detected_language,
                'detection_confidence': self.detection_confidence,
                'scripts': [s['script'] for s in scripts[:3]],  # Top 3 scripts
                'translation_unit_count': len(translation_units)
            }
        
        return result

def process(doc_path: str, context: Optional[Dict] = None) -> Dict:
    """
    Process a document using the multilingual kernel.
    
    Args:
        doc_path: Path to the document to process
        context: Optional context dictionary to pass between kernels
        
    Returns:
        Dictionary with processing results
    """
    processor = MultilingualProcessor(doc_path, context=context)
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
