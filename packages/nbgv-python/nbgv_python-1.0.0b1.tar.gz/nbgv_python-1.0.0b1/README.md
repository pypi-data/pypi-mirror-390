---
post_title: nbgv-python Package Overview
author1: Shuai Zhang
post_slug: nbgv-python
microsoft_alias: shuzhang
featured_image: "https://devblogs.microsoft.com/azuremigrate/wp-content/uploads/sites/113/2023/01/microsoft-logo.png"
categories:
  - Architecture
tags:
  - nbgv
  - hatch
  - versioning
ai_note: This document was prepared with AI assistance.
summary: Guidance for using the nbgv-python package to integrate Nerdbank.GitVersioning with hatchling projects.
post_date: 2025-11-08
---

<!-- markdownlint-disable-next-line MD041 -->
## Overview

- `nbgv-python` wraps the Nerdbank.GitVersioning CLI so Python projects can reuse the same versioning semantics.
- The package discovers the CLI via `NBGV_PYTHON_COMMAND`, a direct `nbgv` executable, or `dotnet tool run nbgv` as a fallback.
- A Hatch version source plugin is provided, allowing projects to declare `dynamic = ["version"]` and resolve their version at build time.

## Installation

- Install the package into your monorepo environment using `uv add --package nbgv-python nbgv-python`.
- Ensure the `nbgv` CLI is available either as a global .NET tool (`dotnet tool install -g nbgv`) or via a local tool manifest.
- Optionally set `NBGV_PYTHON_COMMAND` when the executable lives outside of `PATH` or requires additional arguments.

## Hatch Integration

Add the plugin to your project configuration:

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
source = "nbgv"

[tool.hatch.version.nbgv]
version-field = "simple_version"
```

During builds Hatch invokes `nbgv get-version --format json` in the project root and uses the selected field for the package version.
Additional configuration keys include `command` (override CLI invocation) and `working-directory` (relative path for the repository root).
The plugin normalizes the chosen value to a PEP 440 compliant version, so SemVer pre-release tags such as `-beta.1` are mapped to `b1` automatically.

## Python API

Retrieve version metadata directly from Python code:

```python
from nbgv_python import get_version

version = get_version()
print(version["simple_version"])  # -> 1.2.3
```

Forward arbitrary commands to the CLI:

```python
from nbgv_python import forward

forward(["cloud", "--ci"])
```

All helpers raise `NbgvNotFoundError` when the CLI cannot be resolved and `NbgvCommandError` for non-zero exit codes.

## Command-Line Usage

The console script `nbgv-python` proxies all arguments to the real CLI:

```bash
nbgv-python get-version --format json
```

The wrapper surfaces the same exit codes as the underlying tool and prints diagnostic guidance when the command cannot be located.
