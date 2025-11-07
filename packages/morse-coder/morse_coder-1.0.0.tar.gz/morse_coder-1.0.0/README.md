# morsepy
[![GitHub Repo](https://img.shields.io/badge/GitHub-morsepy-black?logo=github&style=for-the-badge)](https://github.com/ElisaGenesio/morsepy)
[![PyPI](https://img.shields.io/pypi/v/morsepy?style=for-the-badge&color=blue)](https://pypi.org/project/morsepy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Last Commit](https://img.shields.io/github/last-commit/acrazypie/morsepy)
![Stars](https://img.shields.io/github/stars/acrazypie/morsepy?style=social)

[![Maintained by acrazypie](https://img.shields.io/badge/maintained%20by-acrazypie-9cf?logo=github&style=flat-square)](https://egenesio.com)

A simple and lightweight Python library to encode and decode Morse code.  
Supports letters, numbers, and punctuation symbols — perfect for small projects, learning, or creative experiments.

---

## 🚀 Installation

You can install it directly from PyPI:

```bash
pip install morsepy
```

Or, if you’re developing locally:

```bash
pip install -e .
```

---

## 🧠 Usage

```python
from morsepy import encode, decode

text = "ciao mondo!"
code = encode(text)
print("Morse:", code)

decoded = decode(code)
print("Decoded:", decoded)
```

Output:

```
Morse: _._. .. ._ ___ / __ ___ _. _.. ___ _._.__
Decoded: ciao mondo!
```

---

## 📚 Features

-   🔤 Encode any text into Morse code
-   🔁 Decode Morse code back to text
-   🧩 Supports A–Z, 0–9, and common punctuation
-   ⚡ Lightweight, dependency-free

---

## 📦 Project Structure

```
morsepy/
├── morsepy/
│   ├── __init__.py
│   └── core.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🪪 License

Released under the [MIT License](./LICENSE)  
© 2025 Elisa
