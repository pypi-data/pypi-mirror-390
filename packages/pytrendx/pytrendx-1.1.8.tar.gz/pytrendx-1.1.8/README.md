## What is PyTrendx?

[![PyPI version](https://badge.fury.io/py/pytrendx.svg)](https://badge.fury.io/py/pytrendx)
[![Downloads](https://pepy.tech/badge/pytrendx)](https://pepy.tech/project/pytrendx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Support%20Server-7289DA?style=flat&logo=discord)](https://discord.gg/MaWeRFxa)

`PyTrendx` is a **modern CLI tool** that allows you to easily fetch, visualize, analyze, and predict **PyPI package download statistics** directly from your terminal.

It combines **pypistats**, **matplotlib**, **NumPy**, and **scikit-learn** to make data analysis effortless — right from your console.

---

## Features

- Fetch PyPI download stats (`--get`)
- Graph visualization of download trends (`--graph`)
- Statistical analysis using NumPy (`--analyze`)
- Predict future download trends with machine learning (`--predict`)

---

## Installation

```bash
pip install pytrendx
```

## Usage

### Fetch current download stats
```bash
ptx --get pillow
```

### Graph download trends
```bash
ptx --graph numpy
```

### Analyze download statistics
```bash
ptx --analyze flask
```

### Predict future trends
```bash
ptx --predict requests
```