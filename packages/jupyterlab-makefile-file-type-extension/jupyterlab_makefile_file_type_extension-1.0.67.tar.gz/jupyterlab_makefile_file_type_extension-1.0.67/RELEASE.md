# Release v1.0.5

## Overview

Initial stable release of the JupyterLab Makefile Extension providing comprehensive syntax highlighting and file type support for Makefiles in JupyterLab 4.

## What's New

This release introduces a complete Makefile editing experience in JupyterLab with intelligent syntax highlighting and custom file type recognition.

**Custom Syntax Highlighting**:
- Purpose-built CodeMirror language mode with accurate token recognition for Makefile syntax
- Target definitions (`build:`, `install:`, etc.) highlighted in bold with distinct keyword styling
- Variable references colored differently - Make-style `$(VAR)` vs shell-style `${VAR}`
- Automatic variables (`$@`, `$<`, `$^`, `$*`) highlighted with special styling
- Make functions (`$(shell ...)`, `$(wildcard ...)`, `$(patsubst ...)`, `$(filter ...)`, `$(subst ...)`, `$(foreach ...)`) recognized as keywords
- Line continuation backslashes (`\`) at end of lines highlighted prominently with keyword.control escape styling
- Single and double quoted strings properly recognized throughout Makefile content
- Tab-indented recipe lines (commands) distinguished from regular Makefile directives
- Special targets (`.PHONY`, `.DEFAULT_GOAL`) properly highlighted

**File Type Support**:
- Automatic recognition of `Makefile`, `makefile`, `GNUmakefile`, and `*.mk` files
- VS Code-style bold red "M" icon (#d84a4a) for easy identification in JupyterLab file browser
- Proper MIME type registration (`text/x-makefile`)
- Pattern-based filename matching for standard Makefile naming conventions

**Developer Experience**:
- Improved code readability with semantic syntax highlighting
- Visual aids for complex Makefile constructs like line continuations
- Clear distinction between targets, variables, commands, and strings
- Better understanding of Makefile structure at a glance

## Installation

### From PyPI

```bash
pip install jupyterlab-makefile-file-type-extension
```

### From npm

```bash
npm install jupyterlab_makefile_file_type_extension
```

## Requirements

- JupyterLab >= 4.0.0
- Python >= 3.8
- Node.js >= 20.x (for development)

## Technical Details

**Architecture**:
- Frontend-only extension (no server-side handlers required)
- Custom CodeMirror 6 StreamParser for Makefile syntax
- JupyterLab document registry integration for file type registration
- SVG-based icon with embedded color for consistent rendering

**Dependencies**:
- `@jupyterlab/application` ^4.0.0
- `@jupyterlab/codemirror` ^4.0.0
- `@jupyterlab/docregistry` ^4.0.0
- `@jupyterlab/ui-components` ^4.0.0
- `@codemirror/language` ^6.0.0
- `@codemirror/legacy-modes` ^6.0.0

## Repository

https://github.com/stellarshenson/jupyterlab_makefile_file_type_extension

## Contributors

- Stellars Henson (konrad.jelen@gmail.com)

## License

BSD-3-Clause
