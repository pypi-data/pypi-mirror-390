# 🧬 BioLM JupyterLab Extension — Product Design Document

## 1. Overview
The **BioLM JupyterLab Extension** enhances productivity for users working with the [BioLM API](https://api.biolm.ai/) and SDK inside notebooks.  
It provides a **graphical interface** to browse available models, insert SDK code snippets, and manage authentication — all from within JupyterLab’s sidebar.  

**Goal:** streamline discovery, copying, and usage of BioLM’s models and SDK actions without leaving the notebook environment.

---

## 2. Core Features

### **A. Model Browser (Primary Tab)**
**Purpose:** Quickly explore available BioLM models and their capabilities.

**Key Functions:**
- Displays a **searchable, filterable list** of all BioLM models.
- Each model entry shows:
  - **Model Name / ID**
  - **Tags** (e.g. `predict`, `generate`, `encode`, `embed`, `classify`)
  - **Description / brief metadata**
- **Actions** for selected model:
  - **Copy model ID** to clipboard.
  - **Copy SDK function snippet** for chosen model + action.
  - **Insert SDK snippet** directly into the current notebook cell.

**User Flow:**
1. Open the “Models” tab.
2. Search or filter by tag.
3. Select model → choose an action → copy or insert code.

---

### **B. Operations Shortcuts (Docs Integrations Tab)**
**Purpose:** Provide quick access to common SDK examples and API operations from the [BioLM Docs](https://docs.biolm.ai/latest/index.html).

**Key Functions:**
- Organized list of **common operations** (e.g. “Generate text,” “Embed sequence,” “Fine-tune model,” etc.).
- Each operation displays:
  - Description
  - Required parameters (if any)
  - Associated code snippet (Python SDK)
- **Insert into notebook cell** with one click.

**User Flow:**
1. Open the “Operations” tab.
2. Browse or search for desired task.
3. Click to insert the relevant SDK example into the active cell.

---

### **C. Settings (Configuration Tab)**
**Purpose:** Handle BioLM authentication and basic configuration.

**Key Functions:**
- UI for entering or updating **API key** (from [Authentication Guide](https://docs.biolm.ai/latest/python-client/authentication.html)).
- Option to **test connection** to verify the key.
- Display current SDK version and linked account info (if available).
- Option to set:
  - Default model
  - Default action (e.g. `predict`)
  - Toggle telemetry or analytics (if implemented later)

**User Flow:**
1. Open “Settings” tab.
2. Enter API key.
3. Click “Validate” to confirm authentication.
4. Adjust default model/action preferences.

---

## 3. UX Structure (JupyterLab Sidebar)

| Tab | Name | Purpose |
|-----|------|----------|
| 🧠 **Models** | Browse models & insert snippets | Core entry point for code generation |
| ⚙️ **Operations** | Common SDK operations | Quick examples from docs |
| 🔑 **Settings** | Authentication & preferences | Manage BioLM API credentials |

Each tab is self-contained but unified in look and feel — leveraging consistent component styles (search bar, list view, copy/insert buttons).

---

## 4. Data & Integrations
- **Data Source:** `https://api.biolm.ai/models` (or equivalent endpoint) for real-time model metadata.
- **Docs Source:** Static or fetched index of SDK operation examples from `https://docs.biolm.ai/latest/`.
- **Storage:** JupyterLab’s user settings system (for storing API key and preferences securely).

---

## 5. Non-Goals / Out of Scope (v1)
- No model execution or live inference inside the extension.
- No fine-tuning UI (beyond inserting SDK examples).
- No dependency on the running kernel for UI rendering (pure client-side).

---

## 6. Future Enhancements (v2+)
- Offline cache of model metadata.
- Context-aware snippet generation (auto-detects kernel language).
- Integration with the BioLM dashboard for usage metrics.
- Optional telemetry / “recently used models” history.


## 7. Clarifying Questions

### Technical Stack & Compatibility
**Q1:** What minimum version of JupyterLab should this extension target? (e.g., JupyterLab 3.x, 4.x, or both?)

- I don't care

**Q2:** What frontend framework/library should be used? (React, Vue, vanilla TypeScript/JavaScript, or JupyterLab's built-in components?)

- I don't care

**Q3:** Should the extension be written in TypeScript or JavaScript?

- I don't care

**Q4:** Are there any specific browser compatibility requirements? (e.g., Chrome, Firefox, Safari versions)

- I don't care

### API & Data Integration
**Q5:** What is the exact endpoint URL and authentication method for `https://api.biolm.ai/models`? Does it require an API key in headers, or is it publicly accessible?

- https://api.biolm.ai/ is a postman site

**Q6:** What is the structure of the models API response? (JSON schema with fields like `id`, `name`, `tags`, `description`, etc.?)

- you can determine this yourself from https://api.biolm.ai/

**Q7:** Should the extension handle API rate limiting or errors gracefully? What should be displayed if the models endpoint is unavailable?

- use your best judgement

**Q8:** How often should model metadata be refreshed? (On extension load, on tab open, manual refresh button, or cached with TTL?)

- use your best judgement

**Q9:** For the Operations tab, should code snippets be:
   - Static examples bundled with the extension?
   - Fetched dynamically from the docs site?
   - A curated list maintained separately?

- static examples bundled with the extension I guess

### SDK Integration
**Q10:** What version(s) of the BioLM Python SDK should code snippets target? (Latest stable, specific version, or version-agnostic?)

- I don't care

**Q11:** When inserting SDK snippets, should they:
   - Include placeholder values (e.g., `model="<model-id>"`, `sequence="<your-sequence>"`)?
   - Include the actual selected model ID pre-filled?
   - Include import statements (e.g., `from biolm import Client`)?

- Include the actual selected model info pre-filled
- No import statements, that can come from the example snippets tab

**Q12:** Should snippets be editable before insertion, or always insert as-is?

- use your best judgement

**Q13:** When a user selects a model and action (e.g., "predict"), what should the generated snippet look like? (Full function call, minimal example, or configurable complexity?)

- use your judgement

### Authentication & Settings
**Q14:** How should the API key be stored securely? (JupyterLab's settings system with encryption, environment variable support, or both?)

- environemnt variable

**Q15:** Should the extension support multiple API keys/profiles, or just a single key?

- support for selecting from profiles (with optional profile names) would be cool

**Q16:** What does "test connection" validation entail? (Simple API endpoint ping, authenticated request to a specific endpoint, or account info retrieval?)

- use your judgement

**Q17:** Should the extension respect existing API key configuration (e.g., environment variables like `BIOLM_API_KEY`) and allow the UI to override, or should it manage keys independently?

- yes, respect existing API key configurations

**Q18:** What account info should be displayed in Settings? (Email, organization, usage limits, etc.?)

- use your judgement

### UI/UX Details
**Q19:** Should the extension match JupyterLab's default theme (light/dark mode support), or have a custom design?

- use your judgement, but our primary accent color is #558BF7

**Q20:** For the Model Browser, should:
   - Model descriptions be truncated with "show more" expandability?
   - Tags be clickable to filter by that tag?
   - Models be grouped by category (if categories exist)?

- sure, 'show more' could be good
- I would probably make tags act as the buttons for actions like code insertion.. that way you select an 'action' tag for a model and you have both those pieces of information to inject
- sort would be good

**Q21:** When inserting code into a notebook cell, should it:
   - Replace the current cell content?
   - Append to the current cell?
   - Insert into a new cell below?

- append, but use your judgement

**Q22:** Should there be visual feedback when code is copied/inserted? (Toast notifications, checkmarks, etc.?)

- use your judgement

**Q23:** What should happen if no notebook is open when the user tries to insert code? (Show error, open new notebook, or disable insert button?)

- use your judgement

### Search & Filtering
**Q24:** Should search be:
   - Full-text across model name, description, and tags?
   - Case-sensitive or case-insensitive?
   - Real-time as-you-type or on Enter/button click?

- use your judgement

**Q25:** Should tag filtering support multiple selected tags (AND/OR logic)?

- I don't care

### Installation & Distribution
**Q26:** How should this extension be distributed? (npm package, pip package, conda package, or all of the above?)

- yes, use your judgement

**Q27:** Are there any dependencies that must be pre-installed? (e.g., specific JupyterLab extensions, Node.js version requirements)

- I don't know, but use your judgement

**Q28:** Should the extension be available on PyPI, npm, or both?

- Yes but I don't know which.. I guess PyPI?

### Error Handling & Edge Cases
**Q29:** What should happen if:
   - The models API returns an empty list?
   - A model has no tags or description?
   - The user's API key is invalid/expired?
   - Network requests fail (offline mode)?

- Use your best judgement on these

**Q30:** Should the extension work in offline mode with cached data, or require an active internet connection?

- I don't know

### Model Metadata
**Q31:** Are there additional model metadata fields that should be displayed but aren't mentioned? (e.g., model size, training date, performance metrics, supported input formats)

- Not sure

**Q32:** Should the extension show model versioning information if models have multiple versions?

- sure if such a thing exists