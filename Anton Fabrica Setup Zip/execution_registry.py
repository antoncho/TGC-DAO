"""
Execution Registry for GILC Tesseract

Logs kernel execution metadata, output, and quantum_seal.
Maintains historical trace of logic chain progress per epoch.
"""

import logging
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum, auto

logger = logging.getLogger('ExecutionRegistry')

class ExecutionStatus(Enum):
    """Status of a kernel execution."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class ExecutionRecord:
    """Record of a single kernel execution."""
    execution_id: str
    kernel_name: str
    doc_path: str
    start_time: float
    end_time: Optional[float] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    input_metadata: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    quantum_seal: Optional[str] = None
    parent_execution_id: Optional[str] = None
    child_executions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds, or None if not completed."""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        result = asdict(self)
        result['status'] = self.status.name
        result['duration'] = self.duration
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionRecord':
        """Create from a dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ExecutionStatus[data['status']]
        return cls(**data)


class ExecutionRegistry:
    """
    Registry for tracking kernel executions and their metadata.
    
    Maintains a history of all kernel executions with their inputs, outputs,
    and execution context. Supports querying and analysis of execution traces.
    """
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """Initialize the execution registry.
        
        Args:
            storage_path: Optional path for persisting execution records.
                         If None, records are kept only in memory.
        """
        self.records: Dict[str, ExecutionRecord] = {}
        self.storage_path = Path(storage_path) if storage_path else None
        self._next_execution_id = 1
        
        # Load existing records if storage path exists
        if self.storage_path and self.storage_path.exists():
            self._load_records()
    
    def _load_records(self) -> None:
        """Load execution records from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
            
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for record_data in data.get('records', []):
                try:
                    record = ExecutionRecord.from_dict(record_data)
                    self.records[record.execution_id] = record
                    # Update the next execution ID to be higher than any existing
                    try:
                        record_num = int(record.execution_id.split('-')[-1], 16)
                        self._next_execution_id = max(self._next_execution_id, record_num + 1)
                    except (ValueError, IndexError):
                        pass
                except Exception as e:
                    logger.error(f"Error loading execution record: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading execution records: {e}")
    
    def _save_records(self) -> None:
        """Save execution records to storage."""
        if not self.storage_path:
            return
            
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert records to dicts
            records_data = [r.to_dict() for r in self.records.values()]
            
            # Save to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': '1.0',
                    'records': records_data,
                    'last_updated': datetime.utcnow().isoformat()
                }, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving execution records: {e}")
    
    def _generate_execution_id(self) -> str:
        """Generate a unique execution ID."""
        timestamp = int(time.time() * 1000)
        execution_id = f"ex-{timestamp:x}-{self._next_execution_id:x}"
        self._next_execution_id += 1
        return execution_id
    
    def start_execution(self, kernel_name: str, doc_path: str, 
                       input_metadata: Optional[Dict[str, Any]] = None,
                       context: Optional[Dict[str, Any]] = None,
                       parent_execution_id: Optional[str] = None) -> str:
        """Record the start of a kernel execution.
        
        Args:
            kernel_name: Name of the kernel being executed
            doc_path: Path to the document being processed
            input_metadata: Optional input metadata
            context: Optional execution context
            parent_execution_id: Optional parent execution ID
            
        Returns:
            Execution ID for this execution
        """
        execution_id = self._generate_execution_id()
        start_time = time.time()
        
        record = ExecutionRecord(
            execution_id=execution_id,
            kernel_name=kernel_name,
            doc_path=str(doc_path),
            start_time=start_time,
            input_metadata=input_metadata or {},
            context=context or {},
            status=ExecutionStatus.RUNNING,
            parent_execution_id=parent_execution_id
        )
        
        # Update parent's child_executions if this is a child execution
        if parent_execution_id and parent_execution_id in self.records:
            self.records[parent_execution_id].child_executions.append(execution_id)
        
        self.records[execution_id] = record
        self._save_records()
        
        logger.info(f"Started execution {execution_id}: {kernel_name} on {doc_path}")
        return execution_id
    
    def complete_execution(self, execution_id: str, output: Dict[str, Any],
                          metrics: Optional[Dict[str, Any]] = None) -> None:
        """Record the successful completion of a kernel execution.
        
        Args:
            execution_id: The execution ID
            output: Output from the kernel
            metrics: Optional execution metrics
        """
        if execution_id not in self.records:
            logger.warning(f"Cannot complete unknown execution: {execution_id}")
            return
            
        record = self.records[execution_id]
        record.status = ExecutionStatus.COMPLETED
        record.end_time = time.time()
        record.output = output
        record.metrics = metrics or {}
        
        # Generate a quantum seal for this execution
        record.quantum_seal = self._generate_quantum_seal(record)
        
        self._save_records()
        logger.info(f"Completed execution {execution_id} in {record.duration:.2f}s")
    
    def fail_execution(self, execution_id: str, error: Union[str, Exception],
                      metrics: Optional[Dict[str, Any]] = None) -> None:
        """Record a failed kernel execution.
        
        Args:
            execution_id: The execution ID
            error: Error that occurred
            metrics: Optional execution metrics
        """
        if execution_id not in self.records:
            logger.warning(f"Cannot fail unknown execution: {execution_id}")
            return
            
        record = self.records[execution_id]
        record.status = ExecutionStatus.FAILED
        record.end_time = time.time()
        record.error = str(error)
        record.metrics = metrics or {}
        
        self._save_records()
        logger.error(f"Execution {execution_id} failed: {error}")
    
    def cancel_execution(self, execution_id: str) -> None:
        """Cancel a pending or running execution.
        
        Args:
            execution_id: The execution ID to cancel
        """
        if execution_id not in self.records:
            logger.warning(f"Cannot cancel unknown execution: {execution_id}")
            return
            
        record = self.records[execution_id]
        if record.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            record.status = ExecutionStatus.CANCELLED
            record.end_time = time.time()
            self._save_records()
            logger.info(f"Cancelled execution: {execution_id}")
    
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Get an execution record by ID."""
        return self.records.get(execution_id)
    
    def get_execution_trace(self, execution_id: str) -> List[ExecutionRecord]:
        """Get the complete execution trace for an execution.
        
        This includes all ancestor and descendant executions.
        
        Args:
            execution_id: The execution ID
            
        Returns:
            List of execution records in chronological order
        """
        if execution_id not in self.records:
            return []
            
        # Find the root execution
        current = self.records[execution_id]
        while current.parent_execution_id and current.parent_execution_id in self.records:
            current = self.records[current.parent_execution_id]
        
        # Traverse the execution tree in-order
        trace = []
        stack = [(current, False)]
        
        while stack:
            node, processed = stack.pop()
            if processed:
                trace.append(node)
            else:
                # Push children in reverse order to process them in order
                for child_id in reversed(node.child_executions):
                    if child_id in self.records:
                        stack.append((self.records[child_id], False))
                stack.append((node, True))
        
        return trace
    
    def _generate_quantum_seal(self, record: ExecutionRecord) -> str:
        """Generate a quantum seal for an execution record.
        
        This is a cryptographic hash of the execution metadata and output.
        """
        data = {
            'execution_id': record.execution_id,
            'kernel': record.kernel_name,
            'doc_path': record.doc_path,
            'start_time': record.start_time,
            'end_time': record.end_time,
            'input_hash': hashlib.sha256(json.dumps(record.input_metadata, sort_keys=True).encode()).hexdigest(),
            'output_hash': hashlib.sha256(json.dumps(record.output or {}, sort_keys=True).encode()).hexdigest(),
            'parent_id': record.parent_execution_id,
            'timestamp': time.time()
        }
        
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about all executions."""
        if not self.records:
            return {}
        
        completed = [r for r in self.records.values() if r.status == ExecutionStatus.COMPLETED]
        failed = [r for r in self.records.values() if r.status == ExecutionStatus.FAILED]
        running = [r for r in self.records.values() if r.status == ExecutionStatus.RUNNING]
        pending = [r for r in self.records.values() if r.status == ExecutionStatus.PENDING]
        
        durations = [r.duration for r in completed if r.duration is not None]
        
        return {
            'total': len(self.records),
            'completed': len(completed),
            'failed': len(failed),
            'running': len(running),
            'pending': len(pending),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'kernels_used': len({r.kernel_name for r in self.records.values()}),
            'documents_processed': len({r.doc_path for r in self.records.values()})
        }


def create_execution_registry(storage_path: Optional[Union[str, Path]] = None) -> ExecutionRegistry:
    """Create a new ExecutionRegistry instance.
    
    Args:
        storage_path: Optional path for persisting execution records.
                     If None, records are kept only in memory.
    """
    return ExecutionRegistry(storage_path=storage_path)


# Global instance for convenience
default_registry = create_execution_registry()
