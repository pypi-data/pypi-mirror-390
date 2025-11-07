<div align="center">

# 🧠 Torcy

**Aesthetic and smart PyTorch environment tester - because checking your setup shouldn't look boring.**

[![PyPI](https://img.shields.io/pypi/v/torcy?color=6ea8fe&label=PyPI)](https://pypi.org/project/torcy)
[![Python](https://img.shields.io/badge/python-%3E%3D3.8-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](#)
[![Torch](https://img.shields.io/badge/PyTorch-supported-EE4C2C.svg)](https://pytorch.org)

</div>

---

> ⚠️ **Note:** This library is not expected to receive frequent updates.  
> It will only be updated when it becomes **incompatible or broken** with newer versions of PyTorch or Python.  
> Torcy is designed to be stable, lightweight, and long-lasting. Once it works - it *just works*.

---

## ✨ Overview

Torcy is a stylish and safe CLI & library tool to test your **PyTorch environment** in seconds.  
It checks whether PyTorch is installed correctly, detects **CPU/GPU**, verifies CUDA support, and even runs a small benchmark - all with an aesthetic terminal output 💻🔥

---

## 🚀 Installation

```bash
pip install torcy
```

Or install from source:
```bash
git clone https://github.com/rillToMe/torcy.git
cd torcy
pip install .
```

---

## 💡 Usage

Run directly in your terminal:
```bash
torcy
```

Example output:
```
🔥 Starting PyTorch Environment Test 🔥
🧩 PyTorch version: 2.4.0+cpu
⚙️  Using CPU: 12th Gen Intel(R) Core(TM) i5-12450HX
💡 You can install the GPU version with: torcy --install-gpu

📊 Random tensor on CPU:
tensor([[0.23, 0.58, 0.71],
        [0.91, 0.64, 0.12],
        [0.55, 0.41, 0.77]])

🧠 Running quick compute benchmark...
🚀 Benchmarking... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:05
⚡ Compute speed: 5.11245s
✅ Test completed successfully - 🧘 Smooth setup!
```

---

## 🧩 GPU Installation Helper

Got an NVIDIA GPU (like RTX 3050)?  
Torcy can install the correct GPU-enabled PyTorch build automatically:

```bash
torcy --install-gpu
```

This uses the official CUDA 12.1 wheel from the PyTorch repository.

---

## 📚 Features

| Feature | Description |
|----------|-------------|
| 🔍 **Smart Detection** | Detects PyTorch version, CUDA status, and hardware info |
| 🧠 **CPU/GPU Info** | Shows exact CPU model or GPU name |
| 💡 **Auto-Suggestion** | Suggests commands to install GPU-enabled PyTorch |
| ⚙️ **Benchmark Test** | Quick compute test using PyTorch matrix multiplication |
| 🎨 **Beautiful CLI** | Animated intro, colorized output with `rich` |
| 🐍 **Dual-Use** | Works as both a CLI tool and Python module |

---

## 🧠 As a Python Module

```python
import torcy

torcy.test()
```

---

## ⚙️ Dependencies

- Python 3.8+
- [PyTorch](https://pytorch.org/)
- [`rich`](https://pypi.org/project/rich/)
- [`py-cpuinfo`](https://pypi.org/project/py-cpuinfo/)

Install manually if missing:
```bash
pip install rich py-cpuinfo
```

---

## 🧩 Developer Mode

For local development (to test without reinstalling the wheel):
```bash
python -m torcy
```

---

---

## 🧾 License

**MIT License © 2025 [DitDev](https://github.com/rillToMe)**  
Feel free to fork, modify, and share!

🌐 **Portfolio:** [ditdev.vercel.app](https://ditdev.vercel.app)

---


## 💬 Fun Fact

Torcy was created just to make `torch.cuda.is_available()` look cooler 😎  
If you love small tools with personality - welcome aboard.

---

<div align="center">
  
**Torcy** - *beautiful, minimal, and brutally honest about your PyTorch setup.*

</div>
