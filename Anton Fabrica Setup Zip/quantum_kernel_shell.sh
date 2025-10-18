#!/bin/bash
#
# Quantum Kernel Shell - Interactive environment for GILC Tesseract Kernel System
#
# TYPE: Interactive Shell Environment
# MODE: Quantum Harmonic Sync
# CONTEXT: Epoch Ω.ΣΩΩ.3.2
# STRUCTURE: Interactive shell with command completion

# Set environment variables
export PYTHONPATH="$PYTHONPATH:$(pwd)"
export EPOCH="ΣΩΩ.3.2"
export VAULT_DIR="$(pwd)/bundles/ΣΩΩ.current/vault"

# Ensure directories exist
mkdir -p "$VAULT_DIR/documents"
mkdir -p "$VAULT_DIR/braids"
mkdir -p "$VAULT_DIR/registry"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Shell functions
quantum_process() {
    # Process a document through the kernel system
    # Usage: quantum_process <document_path> [context_json]
    local doc_path="$1"
    local context="${2:-{}}"
    
    if [ -z "$doc_path" ]; then
        echo "Usage: quantum_process <document_path> [context_json]"
        return 1
    fi
    
    if [ ! -f "$doc_path" ]; then
        echo "Error: Document not found: $doc_path"
        return 1
    fi
    
    echo -e "${GREEN}⚡ Processing document: $doc_path${NC}"
    python3 -c "
import json
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
result = cli.process_document('$doc_path', $context)
print(json.dumps(result, indent=2))
"
}

quantum_kernels() {
    # List all available kernels
    echo -e "${BLUE}Available Kernels:${NC}"
    python3 -c "
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
for kernel in cli.list_kernels():
    print(f'- {kernel}')
"
}

quantum_registry() {
    # View execution registry
    local id="$1"
    python3 -c "
import json
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
result = cli.view_registry('$id' if '$id' else None)
print(json.dumps(result, indent=2) if result else 'No executions found')
"
}

quantum_braid() {
    # View braid map
    local doc_id="$1"
    python3 -c "
import json
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
result = cli.view_braidmap('$doc_id' if '$doc_id' else None)
print(json.dumps(result, indent=2) if result else 'No braid data found')
"
}

quantum_watch() {
    # Watch executions in real-time
    local interval="${1:-5}"
    python3 -c "
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
cli.watch_executions(interval=$interval)
"
}

quantum_export() {
    # Export registry to file
    local output_file="${1:-registry_export.json}"
    python3 -c "
from quantum_kernel_cli import QuantumKernelCLI
cli = QuantumKernelCLI()
success = cli.export_registry('$output_file')
print('Export ' + ('succeeded' if success else 'failed'))
"
}

# Print welcome message
echo -e "${GREEN}┌───────────────────────────────────────────────┐"
echo -e "│  ${YELLOW}⚛️  GILC Tesseract Quantum Kernel Shell  ${GREEN}│"
echo -e "│  ${BLUE}Epoch: $EPOCH | Mode: Quantum Harmonic Sync  ${GREEN}│"
echo -e "└───────────────────────────────────────────────┘${NC}"
echo -e "\n${BLUE}Available Commands:${NC}"
echo -e "  ${GREEN}quantum_process <doc> [context]${NC}  - Process a document"
echo -e "  ${GREEN}quantum_kernels${NC}                - List available kernels"
echo -e "  ${GREEN}quantum_registry [id]${NC}          - View execution registry"
echo -e "  ${GREEN}quantum_braid [doc_id]${NC}         - View braid map"
echo -e "  ${GREEN}quantum_watch [interval]${NC}       - Watch executions"
echo -e "  ${GREEN}quantum_export [file]${NC}          - Export registry"
echo -e "  ${GREEN}exit${NC}                           - Exit the shell"
echo -e "\n${BLUE}Environment:${NC}"
echo -e "  EPOCH: $EPOCH"
echo -e "  VAULT: $VAULT_DIR"
echo -e "  PYTHONPATH: $PYTHONPATH"

# Start interactive shell
while true; do
    read -p "$ " cmd
    case "$cmd" in
        exit) break ;;
        help) 
            echo -e "${BLUE}Available Commands:${NC}"
            echo -e "  ${GREEN}quantum_process <doc> [context]${NC}  - Process a document"
            echo -e "  ${GREEN}quantum_kernels${NC}                - List available kernels"
            echo -e "  ${GREEN}quantum_registry [id]${NC}          - View execution registry"
            echo -e "  ${GREEN}quantum_braid [doc_id]${NC}         - View braid map"
            echo -e "  ${GREEN}quantum_watch [interval]${NC}       - Watch executions"
            echo -e "  ${GREEN}quantum_export [file]${NC}          - Export registry"
            echo -e "  ${GREEN}exit${NC}                           - Exit the shell"
            ;;
        quantum_*) $cmd ;;
        *) echo "Unknown command. Type 'help' for available commands." ;;
    esac
done

echo -e "${GREEN}Exiting Quantum Kernel Shell.${NC}"
