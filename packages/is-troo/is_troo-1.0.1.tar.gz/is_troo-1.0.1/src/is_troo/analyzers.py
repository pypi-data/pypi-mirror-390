"""
The magic behind the mayhem: our proprietary (propriatary? proprietery?) logical framework or whatev
"""

class TroothAnalyzer:

    @staticmethod
    def analyze(value) -> bool:
        """Return True if value is exactly to True"""
        return value is True

class TroothinessAnalyzer:

    @staticmethod
    def analyze(value) -> bool:
        """Return True if value evaluates to True"""
        return bool(value)