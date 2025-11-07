"""
Demo stages for BoR-Proof SDK quickstart.
Simple, pure functions demonstrating the proof system.
"""

from bor.decorators import step


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C.get("offset", 0)


@step
def square(x, C, V):
    """Square the state."""
    return x * x
