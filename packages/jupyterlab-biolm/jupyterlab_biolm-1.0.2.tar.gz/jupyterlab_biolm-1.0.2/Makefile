.PHONY: help build clean install rebuild-jupyterlab clean-jupyterlab start deploy verify check-server full-rebuild test-endpoint dev restart check-deployed check-server-status

# Default target
help:
	@echo "BioLM JupyterLab Extension - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make build              - Build TypeScript and labextension"
	@echo "  make clean              - Clean all build artifacts"
	@echo "  make install            - Install extension (pip install -e .)"
	@echo "  make rebuild-jupyterlab - Rebuild JupyterLab with extension"
	@echo "  make clean-jupyterlab  - Clean JupyterLab build cache"
	@echo "  make deploy             - Copy built files to extension directory"
	@echo "  make verify             - Verify endpoints in built files"
	@echo "  make check-server       - Check if server extension is loaded"
	@echo "  make test-endpoint      - Test server proxy endpoint"
	@echo "  make full-rebuild       - Clean, build, install, and rebuild JupyterLab"
	@echo "  make dev                - Quick dev cycle: build and deploy"
	@echo "  make start              - Start JupyterLab on port 8889"
	@echo "  make restart            - Kill existing server and start fresh"
	@echo "  make check-deployed     - Check what files are deployed"
	@echo "  make check-server-status - Check server extension in running JupyterLab"
	@echo ""

# Build TypeScript and labextension
build:
	npm run build:lib
	@JUPYTERLAB_CORE=$$(python3 -c "import jupyterlab; import os; print(os.path.join(os.path.dirname(jupyterlab.__file__), 'staging'))") && \
	npm run clean:labextension && \
	node node_modules/@jupyterlab/builder/lib/build-labextension.js . --core-path "$$JUPYTERLAB_CORE" --development
	@echo "✅ Build complete"

# Clean all build artifacts
clean:
	npm run clean:all
	@echo "✅ Clean complete"

# Install extension
install:
	pip3 install -e . --force-reinstall
	@echo "✅ Installation complete"

# Rebuild JupyterLab
rebuild-jupyterlab:
	python3 -m jupyterlab build
	@echo "✅ JupyterLab rebuild complete"

# Clean JupyterLab build cache
clean-jupyterlab:
	python3 -m jupyterlab clean --all
	@echo "✅ JupyterLab clean complete"

# Deploy built files to extension directory
deploy:
	@mkdir -p /Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm/static
	cp jupyterlab_biolm/labextension/static/* /Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm/static/
	@echo "✅ Files deployed"

# Verify endpoints in built files
verify:
	@echo "Checking endpoints in built files..."
	@grep -o "/biolm/api/models\|/biolm/api/test-connection\|biolm.ai/api/ui/community-api-models" /Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm/static/lib_index_js.*.js 2>/dev/null | sort | uniq -c || echo "No files found or no matches"
	@echo ""
	@echo "Checking source files..."
	@grep -o "/biolm/api/models\|/biolm/api/test-connection\|biolm.ai/api/ui/community-api-models" lib/api/client.js 2>/dev/null | sort | uniq || echo "Source not built yet"

# Check if server extension is loaded
check-server:
	@echo "Checking server extension..."
	@python3 -c "import jupyterlab_biolm.serverextension; print('✅ Server extension module can be imported')" 2>&1 || echo "❌ Server extension not found"
	@python3 -c "from jupyterlab_biolm import _jupyter_server_extension_points; print('✅ Extension points:', _jupyter_server_extension_points())" 2>&1 || echo "❌ Extension points not found"
	@echo ""
	@echo "Checking config file..."
	@test -f ~/.jupyter/jupyter_server_config.py && echo "✅ Config file exists" || echo "⚠️  Config file not found"
	@grep -q "jupyterlab_biolm" ~/.jupyter/jupyter_server_config.py 2>/dev/null && echo "✅ BioLM extension enabled in config" || echo "⚠️  BioLM not in config"

# Test server proxy endpoint
test-endpoint:
	@python3 scripts/test_endpoint.py || echo "⚠️  Test script not found or failed"

# Full rebuild: clean, build, install, rebuild JupyterLab
full-rebuild: clean build install deploy rebuild-jupyterlab
	@echo ""
	@echo "✅✅✅ Full rebuild complete!"
	@echo "   - TypeScript compiled"
	@echo "   - Labextension built"
	@echo "   - Extension installed"
	@echo "   - Files deployed"
	@echo "   - JupyterLab rebuilt"

# Start JupyterLab
start:
	@echo "Starting JupyterLab on port 8889..."
	@python3 -m jupyterlab --no-browser --port 8889 2>&1 &
	@python3 scripts/wait_for_server.py || echo "⚠️  Wait script not found"

# Restart JupyterLab (kill existing and start fresh)
restart:
	@echo "Killing existing JupyterLab servers on port 8889..."
	@ps aux | grep "[j]upyterlab.*8889" | awk '{print $$2}' | xargs kill 2>/dev/null || true
	@sleep 2
	@$(MAKE) start

# Check what's actually being served
check-deployed:
	@echo "Checking deployed extension files..."
	@ls -lh /Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm/static/lib_index_js.*.js 2>/dev/null | tail -3 || echo "No files found"
	@echo ""
	@echo "Endpoint check:"
	@$(MAKE) verify

# Quick development cycle: build and deploy
dev: build deploy
	@echo "✅ Development build and deploy complete"

# Check server extension status in running JupyterLab
check-server-status:
	@python3 scripts/check_server_status.py || echo "⚠️  Check script not found"
