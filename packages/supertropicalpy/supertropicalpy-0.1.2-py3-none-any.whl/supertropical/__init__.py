"""
SupertropicalPy
================

A Python package (SupertropicalPy) for working with supertropical algebra, featuring:
- Tangible and ghost elements
- Matrix operations over supertropical semiring
- Linear system solving using Cramer's rule

Basic usage (recommended):
    >>> import supertropical as suptrop
    >>> a = suptrop.Element(5)  # tangible
    >>> b = suptrop.Element(5, is_ghost=True)  # ghost (5ν)
    >>> print(a + b)  # supertropical addition
    5.0ν
    
    >>> A = suptrop.Matrix([[2, 1], [1, 3]])
    >>> b = suptrop.Matrix([[5], [4]])
    >>> x = A.solve(b)  # Solve linear system

Alternative usage:
    >>> from supertropical import Element, Matrix
    >>> a = Element(5)
    >>> A = Matrix([[1, 2], [3, 4]])
"""

from .element import SupertropicalElement
from .matrix import SupertropicalMatrix

# Shorter aliases for easier import
Element = SupertropicalElement
Matrix = SupertropicalMatrix

__version__ = "0.1.2"
__all__ = [
    "SupertropicalElement", 
    "SupertropicalMatrix",
    "Element",  # Alias
    "Matrix",   # Alias
]
