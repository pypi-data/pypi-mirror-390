# jupyterlab_makefile_file_type_extension

[![GitHub Actions](https://github.com/stellarshenson/jupyterlab_makefile_file_type_extension/actions/workflows/build.yml/badge.svg)](https://github.com/stellarshenson/jupyterlab_makefile_file_type_extension/actions/workflows/build.yml)
[![npm version](https://img.shields.io/npm/v/jupyterlab_makefile_file_type_extension.svg)](https://www.npmjs.com/package/jupyterlab_makefile_file_type_extension)
[![PyPI version](https://img.shields.io/pypi/v/jupyterlab-makefile-file-type-extension.svg)](https://pypi.org/project/jupyterlab-makefile-file-type-extension/)
[![Total PyPI downloads](https://static.pepy.tech/badge/jupyterlab-makefile-file-type-extension)](https://pepy.tech/project/jupyterlab-makefile-file-type-extension)
[![JupyterLab 4](https://img.shields.io/badge/JupyterLab-4-orange.svg)](https://jupyterlab.readthedocs.io/en/stable/)

A JupyterLab extension providing comprehensive Makefile support with syntax highlighting and custom file type recognition.

![Makefile Extension Screenshot](.resources/screenshot.png)

## Features

This extension enhances the Makefile editing experience in JupyterLab with intelligent syntax highlighting and visual aids:

- **Custom syntax highlighter** - Purpose-built CodeMirror language mode for accurate Makefile token recognition
- **Target highlighting** - Build targets (`build:`, `install:`, etc.) displayed in bold with distinct keyword styling
- **Variable recognition** - Make-style `$(VAR)` and shell-style `${VAR}` variables colored differently for clarity
- **Automatic variables** - Special variables like `$@`, `$<`, `$^` highlighted distinctly
- **Function support** - Make functions (`$(shell ...)`, `$(wildcard ...)`, etc.) recognized as keywords
- **Line continuations** - Backslash line breaks (`\`) at end of lines highlighted prominently
- **String parsing** - Quoted strings in single and double quotes properly recognized throughout
- **Recipe detection** - Tab-indented command lines distinguished from regular Makefile content
- **Custom icon** - VS Code-style bold red "M" icon for easy Makefile identification in file browser
- **Pattern matching** - Recognizes `Makefile`, `makefile`, `GNUmakefile`, and `*.mk` files

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install jupyterlab_makefile_file_type_extension
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyterlab_makefile_file_type_extension
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the jupyterlab_makefile_file_type_extension directory

# Set up a virtual environment and install package in development mode
python -m venv .venv
source .venv/bin/activate
pip install --editable "."

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Rebuild extension Typescript source after making changes
# IMPORTANT: Unlike the steps above which are performed only once, do this step
# every time you make a change.
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall jupyterlab_makefile_file_type_extension
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jupyterlab_makefile_file_type_extension` within that folder.

### Testing the extension

#### Frontend tests

This extension is using [Jest](https://jestjs.io/) for JavaScript code testing.

To execute them, execute:

```sh
jlpm
jlpm test
```

#### Integration tests

This extension uses [Playwright](https://playwright.dev/docs/intro) for the integration tests (aka user level tests).
More precisely, the JupyterLab helper [Galata](https://github.com/jupyterlab/jupyterlab/tree/master/galata) is used to handle testing the extension in JupyterLab.

More information are provided within the [ui-tests](./ui-tests/README.md) README.

### Packaging the extension

See [RELEASE](RELEASE.md)
