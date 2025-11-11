# 🪙 bip322-py

**Python ↔ Rust bridge for [BIP-322](https://github.com/bitcoin/bips/blob/master/bip-0322.mediawiki) message verification**, powered by [rust-bitcoin/bip322](https://github.com/rust-bitcoin/bip322) and [PyO3](https://pyo3.rs).

This package provides a single, high-performance function for verifying BIP-322 (Bitcoin) signed messages directly from Python.

---

## ⚙️ Features

- Lightweight wrapper around the Rust `bip322` crate  
- Validates Bitcoin message signatures in **BIP-322 simple mode**  
- Fully typed and pip-installable wheel (`.whl`)

---

## 🧩 Installation


### 🧑‍💻 For end users (from PyPI)

Simply install with pip:

```bash
pip install bip322
```


### From source (development)
```bash
# Create and activate venv (Python 3.8+)
python -m venv .venv
source .venv/bin/activate

# Install maturin and build
pip install maturin
maturin develop
