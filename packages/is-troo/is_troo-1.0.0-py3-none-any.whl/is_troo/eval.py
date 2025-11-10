"""
Public interface layer for the revolutionary Python truth evaluation framework. And such.
"""

from .analyzers import TroothAnalyzer, TroothinessAnalyzer
from .exceptions import TrooEvalError, TroothyEvalError


def is_troo(value) -> bool:
    """
    Determines whether the value is *equal* to True.

    Parameters
    ----------
    value : any
        The object to test for troo-ness.

    Returns
    -------
    bool
        True if troo, False if not troo.
    """
    try:
        return TroothAnalyzer.analyze(value)
    except Exception as e:
        raise TrooEvalError(f"Trooth error popped up when straight troothing it: {e}")


def is_troothy(value) -> bool:
    """
    Determines whether the value *evaluates* to True (is truthy).

    Parameters
    ----------
    value : any
        The object to test for thoothiness.

    Returns
    -------
    bool
        True if truthy, False if not truthy (so ig falsy).
    """
    try:
        return TroothinessAnalyzer.analyze(value)
    except Exception as e:
        raise TroothyEvalError(f"Troothiness error from getting too troothy with it: {e}") from e