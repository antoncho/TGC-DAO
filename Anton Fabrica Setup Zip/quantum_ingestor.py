#!/usr/bin/env python3
"""
Quantum Ingestor for GILC Tesseract

Monitors a directory for new files and processes them using the auto kernel hook.
"""

import os
import time
import json
import logging
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, Any, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_ingestor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QuantumIngestor')

# Track processed files to avoid reprocessing
processed_files: Set[str] = set()

class DocumentHandler(FileSystemEventHandler):
    """Handle file system events for document processing."""
    
    def __init__(self, watch_dir: str, auto_hook):
        self.watch_dir = Path(watch_dir).resolve()
        self.auto_hook = auto_hook
        super().__init__()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
            
        try:
            file_path = Path(event.src_path).resolve()
            
            # Skip hidden files and temporary files
            if file_path.name.startswith('.') or file_path.name.endswith('~'):
                return
                
            # Skip already processed files
            if str(file_path) in processed_files:
                return
                
            # Wait a bit to ensure the file is fully written
            time.sleep(0.5)
            
            # Process the file
            self.process_file(file_path)
            
        except Exception as e:
            logger.error(f"Error processing created file {event.src_path}: {e}", exc_info=True)
    
    def process_file(self, file_path: Path):
        """Process a single file using the auto kernel hook."""
        try:
            logger.info(f"Processing new file: {file_path}")
            
            # Mark as processed
            processed_files.add(str(file_path))
            
            # Load basic metadata
            metadata = {
                'filename': file_path.name,
                'extension': file_path.suffix.lower(),
                'size': file_path.stat().st_size,
                'created': file_path.stat().st_ctime,
                'modified': file_path.stat().st_mtime,
            }
            
            # Process the file using the auto kernel hook
            result = self.auto_hook.on_document_ingested(str(file_path), metadata)
            
            logger.info(f"Processed {file_path} with result: {result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}", exc_info=True)
            raise

def load_processed_files(cache_file: str = '.processed_files') -> Set[str]:
    """Load set of previously processed files from disk."""
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return set(json.load(f))
    except Exception as e:
        logger.warning(f"Could not load processed files cache: {e}")
    return set()

def save_processed_files(files: Set[str], cache_file: str = '.processed_files') -> None:
    """Save set of processed files to disk."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(list(files), f)
    except Exception as e:
        logger.error(f"Could not save processed files cache: {e}")

def process_existing_files(directory: str, auto_hook) -> None:
    """Process any existing files in the directory."""
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Directory does not exist: {directory}")
        return
    
    logger.info(f"Processing existing files in {directory}")
    
    # Process files in the directory
    for file_path in directory.glob('**/*'):
        if file_path.is_file() and not file_path.name.startswith('.'):
            handler = DocumentHandler(str(directory), auto_hook)
            handler.process_file(file_path)

def main():
    """Main entry point for the quantum ingestor."""
    parser = argparse.ArgumentParser(description='Quantum Ingestor for GILC Tesseract')
    parser.add_argument('--watch-dir', default='bundles/ΣΩΩ.current/vault/documents',
                       help='Directory to watch for new files')
    parser.add_argument('--process-existing', action='store_true',
                       help='Process existing files in the watch directory')
    parser.add_argument('--cache-file', default='.processed_files',
                       help='File to store processed file cache')
    args = parser.parse_args()
    
    # Initialize auto kernel hook
    try:
        from kernels.auto_kernel_hook import create_auto_kernel_hook
        auto_hook = create_auto_kernel_hook()
    except ImportError as e:
        logger.error(f"Failed to import auto kernel hook: {e}")
        return 1
    
    # Load previously processed files
    global processed_files
    processed_files = load_processed_files(args.cache_file)
    logger.info(f"Loaded {len(processed_files)} previously processed files")
    
    # Process existing files if requested
    if args.process_existing:
        process_existing_files(args.watch_dir, auto_hook)
    
    # Set up file system observer
    event_handler = DocumentHandler(args.watch_dir, auto_hook)
    observer = Observer()
    observer.schedule(event_handler, args.watch_dir, recursive=True)
    
    logger.info(f"Starting to watch directory: {args.watch_dir}")
    observer.start()
    
    try:
        while True:
            # Periodically save the processed files cache
            save_processed_files(processed_files, args.cache_file)
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping quantum ingestor...")
    
    observer.join()
    
    # Save processed files one last time
    save_processed_files(processed_files, args.cache_file)
    
    return 0

if __name__ == "__main__":
    exit(main())
