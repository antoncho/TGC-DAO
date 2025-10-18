#!/bin/bash
# TYPE: Kernel Runtime Boot
# MODE: Windsurf Cascade – ΣΩΩ.3.2
# OPERATOR: ψ11411

echo "🚦 Launching Kernel Execution Runtime..."

# Set path vars
EPOCH_DIR="bundles/ΣΩΩ.current"
VAULT="$EPOCH_DIR/vault"
REGISTRY="$VAULT/execution_registry.json"
HOOK="kernels/auto_kernel_hook.py"
CONNECTOR="kernels/braid_connector.py"
ROUTER="kernels/processor_router.py"

# Create necessary directories
echo "📂 Setting up directory structure..."
mkdir -p "$VAULT/documents"
mkdir -p "$VAULT/braids"

# 1. Start document watch with hook
echo "📡 Activating quantum ingestion observer..."
python3 quantum_ingestor.py &

# 2. Trigger braid connector scan
echo "🔗 Running semantic braid analysis..."
python3 $CONNECTOR --scan "$VAULT/documents" --output "$VAULT/semantic_links.json"

# 3. Initialize registry if not present
if [ ! -f "$REGISTRY" ]; then
  echo "🧭 Creating execution registry..."
  python3 -c "
import json, os
os.makedirs('$VAULT', exist_ok=True)
with open('$REGISTRY', 'w') as f:
    json.dump({'executions': [], 'epoch': 'ΣΩΩ.3.2'}, f, indent=2)
"
else
  echo "📜 Registry already present: $REGISTRY"
fi

# 4. Initialize braidmap if not present
BRAIDMAP="$VAULT/braidmap.json"
if [ ! -f "$BRAIDMAP" ]; then
  echo "🌐 Initializing braidmap..."
  python3 -c "
import json, os
braidmap = {
    'version': '1.0',
    'epoch': 'ΣΩΩ.3.2',
    'kernel_registry': {
        'logic_kernel': [],
        'ethics_kernel': [],
        'semantic_kernel': [],
        'quantum_kernel': []
    },
    'semantic_links': {}
}
with open('$BRAIDMAP', 'w') as f:
    json.dump({'braidmap': braidmap}, f, indent=2)
"
fi

# 5. Sync braidmap with semantic links
echo "🌐 Linking braidmap to semantic connector..."
python3 -c "
import json, os
bm_path = '$BRAIDMAP'
sl_path = '$VAULT/semantic_links.json'

if os.path.exists(bm_path) and os.path.exists(sl_path):
    bm = json.load(open(bm_path))
    sl = json.load(open(sl_path))
    bm['braidmap']['semantic_links'] = sl
    json.dump(bm, open(bm_path, 'w'), indent=2)
    print('✅ Braidmap updated with semantic links')
"

echo "✅ Kernel Runtime initialized and active."
echo ""
echo "🧪 Recommended next steps:"
echo "1. Add documents to: $VAULT/documents/"
echo "2. Monitor execution: watch -n 5 \"jq '.executions | last' $REGISTRY\""
echo "3. View braidmap: jq . $BRAIDMAP"
echo ""
echo "🔄 Development aliases have been added to your shell."
echo "   Run 'source ~/.bashrc' to reload your shell configuration."

# Add aliases to .bashrc if they don't exist
alias_file="$HOME/.bashrc"
if [ -f "$alias_file" ]; then
    if ! grep -q "alias seed_kernel=" "$alias_file"; then
        echo "" >> "$alias_file"
        echo "# GILC Tesseract Kernel Aliases" >> "$alias_file"
        echo "alias seed_kernel='bash $(pwd)/initialize_kernel_runtime.sh'" >> "$alias_file"
        echo "alias view_registry='cat $(pwd)/$REGISTRY | jq'" >> "$alias_file"
        echo "alias braid_map='cat $(pwd)/$BRAIDMAP | jq'" >> "$alias_file"
        echo "alias watch_braid='watch -n 5 \"jq . $(pwd)/$BRAIDMAP | head -30\"'" >> "$alias_file"
        echo ""
        echo "🔧 Added development aliases to $alias_file"
        echo "   Run 'source $alias_file' to use them in this session."
    fi
fi

echo ""
echo "🌊 Windsurf Cascade Kernel Runtime Ready - ΣΩΩ.3.2 🌊"
