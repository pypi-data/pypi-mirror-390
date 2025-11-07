# CLI Installation Guide

## Installation Options

### Option 1: Install from parent directory (Recommended)

From the project root directory (`simultaneous/`), run:

```bash
pip install -e ./cli
```

This will properly install the CLI package with the correct module structure.

### Option 2: Install from CLI directory

If you're in the `cli/` directory, you need to install from the parent:

```bash
cd ..
pip install -e ./cli
```

### Option 3: Run directly without installation

You can run the CLI directly without installing:

```bash
# From project root
python -m cli.main

# Or from CLI directory  
cd cli
python -m cli.main
```

However, if you run from the CLI directory, you need to set PYTHONPATH:

```bash
# Windows
set PYTHONPATH=..
python main.py

# Linux/Mac
PYTHONPATH=.. python main.py
```

## After Installation

Once installed, you can use the CLI from anywhere:

```bash
sim --help
sim auth signin
sim projects list
```



