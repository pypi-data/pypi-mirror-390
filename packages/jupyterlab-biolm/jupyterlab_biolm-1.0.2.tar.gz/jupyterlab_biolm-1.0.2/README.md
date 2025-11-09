# BioLM JupyterLab Extension

A JupyterLab extension that provides a graphical interface for browsing BioLM models, inserting SDK code snippets, and managing authentication - all from within JupyterLab's sidebar.

## Features

### 🧠 Models Tab
- Browse all available BioLM models
- Search and filter models by name, description, or tags
- Click tags to insert code snippets with model + action pre-filled
- Copy model IDs to clipboard
- Expandable model descriptions

### ⚙️ Operations Tab
- Quick access to common SDK operation examples
- Searchable list of operations (Generate, Predict, Embed, etc.)
- One-click code insertion into notebook cells
- Organized by category

### 🔑 Settings Tab
- Manage multiple API key profiles
- Test API key connections
- Set default model and action preferences
- Respects `BIOLM_API_KEY` environment variable

## Installation

### From PyPI (when available)

```bash
pip install jupyterlab-biolm
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/jupyterlab-biolm.git
cd jupyterlab-biolm

# Install the extension
pip install -e .

# Build the extension
jlpm install
jlpm build

# Rebuild JupyterLab
jupyter lab build
```

## Usage

1. **Open the Extension**: The BioLM sidebar will appear in JupyterLab's left sidebar. If not visible, use the command palette (`Cmd/Ctrl + Shift + C`) and search for "Open BioLM".

2. **Configure API Key**:
   - Go to the Settings tab
   - Add a new profile with your API key
   - Or use the `BIOLM_API_KEY` environment variable

3. **Browse Models**:
   - Switch to the Models tab
   - Search or filter by tags
   - Click a tag button to insert code for that model + action

4. **Use Operations**:
   - Switch to the Operations tab
   - Browse common SDK operations
   - Click "Insert" to add code to your active notebook cell

## Development

### Prerequisites

- Node.js >= 16
- Python >= 3.8
- JupyterLab >= 4.0.0

### Setup

```bash
# Install dependencies
jlpm install

# Build TypeScript
jlpm build:lib

# Build extension in development mode
jlpm build:labextension:dev

# Watch for changes
jlpm watch
```

### Project Structure

```
jupyterlab-biolm/
├── src/                    # TypeScript source
│   ├── index.ts           # Extension entry point
│   ├── widget.tsx         # Main sidebar widget
│   ├── api/               # API client
│   ├── components/        # React components
│   ├── services/          # Business logic
│   └── data/              # Static data
├── style/                  # CSS styles
├── schema/                 # Settings schema
└── jupyterlab_biolm/       # Python package
```

## Configuration

The extension stores settings in JupyterLab's settings system. You can configure:

- **API Key Profiles**: Multiple named profiles with different API keys
- **Active Profile**: Which profile to use (or environment variable)
- **Default Model**: Default model ID for code generation
- **Default Action**: Default action (predict, generate, etc.)

## API Integration

The extension fetches model metadata from `https://api.biolm.ai/models`. Models are cached for 5 minutes to reduce API calls.

## Requirements

- JupyterLab >= 4.0.0
- React >= 18.0.0

## License

BSD-3-Clause

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/yourusername/jupyterlab-biolm).

