"""
is_troo: The only package you'll ever need for finally figuring out what that expression evals to!

Exports two functions:
- 'is_troo(value)'     -> True if the value is True
- 'is_troothy(value)'  -> True if the value evaluates to True (is truthy)
"""

from .eval import is_troo, is_troothy

__all__ = ["is_troo", "is_troothy"]
__version__ = "1.0.1"