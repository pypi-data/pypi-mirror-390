# SupertropicalPy

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TetewHeroez/supertropicalpy/blob/main/docs/source/examples/tutorial.ipynb)

A comprehensive Python package for **supertropical algebra**, featuring tangible and ghost elements, matrix operations, and linear system solving using Cramer's rule.

> **🚀 Try it now!** Click the "Open in Colab" badge above to run the interactive tutorial instantly in your browser - fast and free! No installation needed.

## ✨ Features

- **🎯 Tangible & Ghost Elements**: Full support for both element types with automatic conversion

- **🧮 Supertropical Operations**: Addition $\oplus$ defined by $a\oplus b=\max\{a,b\}$ (with ghost rules), and multiplication $\odot$ defined by $a\odot b=a+b$.

- **📐 Matrix Operations**: Matrix multiplication, permanent (supertropical determinant), adjoint.

- **🔧 Linear System Solver**: Cramer's rule implementation for solving $Ax = b$

- **🚀 NumPy Integration**: Efficient computations using NumPy arrays

- **📚 Comprehensive Documentation**: Full API reference, theory guide, and interactive tutorials

- **✅ Type Safety**: Automatic type coercion and validation

## 📦 Installation

```bash
pip install supertropicalpy
```

Or install from source:

```bash

git clone https://github.com/TetewHeroez/supertropicalpy.git

cd supertropicalpy

pip install -e .

```

## 📖 Documentation

- Full documentation is available at: **[GitHub Pages](https://tetewhereoez.github.io/supertropicalpy)**

- **[Theory Guide](https://tetewhereoez.github.io/supertropicalpy/theory.html)**: Mathematical background on supertropical algebra

- **[Interactive Tutorial](https://tetewhereoez.github.io/supertropicalpy/examples/tutorial.html)**: Jupyter notebook with executable examples

- **[API Reference](https://tetewhereoez.github.io/supertropicalpy/api/index.html)**: Complete API documentation

## 🧪 Running Tests

```bash

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

```

## Run with coverage

```bash
pytest --cov=supertropical

```

## 📚 Building Documentation Locally

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build HTML docs
cd docs
sphinx-build -b html source build
pytest --cov=supertropical

```

## 📚 Building Documentation Locally

```bash
# Install docs dependencies

pip install -e ".[docs]"

# Build HTML docs

cd docs

sphinx-build -b html source build
```

```python
# Or use make (on Unix/Mac/Windows with make installed)
cd docs

make html
```

## 🎓 Mathematical Background

Supertropical algebra extends tropical algebra with ghost elements:

**Operations**:

- **Addition**: $a \oplus b = \max(a, b)$ with special ghost rules

- **Multiplication**: $a \odot b = a + b$ (classical addition)

**Elements**:

- **Tangible**: Regular elements (e.g., $5.0$)

- **Ghost**: Elements marked with $\nu$ (e.g., $5.0\nu$)

- **Zero**: $-\infty$ (additive identity)

- **One**: $0$ (multiplicative identity)

**Key Properties**:

- Matrix permanent replaces determinant

- Cramer's rule works for nonsingular matrices (permanent is tangible)

- Applications in optimization, algebraic geometry, and phylogenetics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.```

## 👥 Authors

- **Supertropical Team**

## 🙏 Acknowledgments

- Based on research by Izhakian, Z., & Rowen, L. on supertropical algebra

## 📞 Contact

- **GitHub**: [https://github.com/TetewHeroez/supertropicalpy](https://github.com/TetewHeroez/supertropicalpy)

- **Issues**: [https://github.com/TetewHeroez/supertropicalpy/issues](https://github.com/TetewHeroez/supertropicalpy/issues)

- **Documentation**: [https://tetewhereoez.github.io/supertropicalpy](https://tetewhereoez.github.io/supertropicalpy)
