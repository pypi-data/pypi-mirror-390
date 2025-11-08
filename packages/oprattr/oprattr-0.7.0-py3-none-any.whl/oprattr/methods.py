import numbers

from numerical import operators

from ._operations import (
    unary,
    equality,
    ordering,
    additive,
    multiplicative,
)


def __abs__(a):
    """Called for abs(a)."""
    return unary(operators.abs, a)

def __pos__(a):
    """Called for +a."""
    return unary(operators.pos, a)

def __neg__(a):
    """Called for -a."""
    return unary(operators.neg, a)

def __eq__(a, b):
    """Called for a == b."""
    return equality(operators.eq, a, b)

def __ne__(a, b):
    """Called for a != b."""
    return equality(operators.ne, a, b)

def __lt__(a, b):
    """Called for a < b."""
    return ordering(operators.lt, a, b)

def __le__(a, b):
    """Called for a <= b."""
    return ordering(operators.le, a, b)

def __gt__(a, b):
    """Called for a > b."""
    return ordering(operators.gt, a, b)

def __ge__(a, b):
    """Called for a >= b."""
    return ordering(operators.ge, a, b)

def __add__(a, b):
    """Called for a + b."""
    return additive(operators.add, a, b)

def __radd__(a, b):
    """Called for b + a."""
    return additive(operators.add, b, a)

def __sub__(a, b):
    """Called for a - b."""
    return additive(operators.sub, a, b)

def __rsub__(a, b):
    """Called for b - a."""
    return additive(operators.sub, b, a)

def __mul__(a, b):
    """Called for a * b."""
    return multiplicative(operators.mul, a, b)

def __rmul__(a, b):
    """Called for b * a."""
    return multiplicative(operators.mul, b, a)

def __truediv__(a, b):
    """Called for a / b."""
    return multiplicative(operators.truediv, a, b)

def __rtruediv__(a, b):
    """Called for b / a."""
    return multiplicative(operators.truediv, b, a)

def __floordiv__(a, b):
    """Called for a // b."""
    return multiplicative(operators.floordiv, a, b)

def __rfloordiv__(a, b):
    """Called for b // a."""
    return multiplicative(operators.floordiv, b, a)

def __mod__(a, b):
    """Called for a % b."""
    return multiplicative(operators.mod, a, b)

def __rmod__(a, b):
    """Called for b % a."""
    return multiplicative(operators.mod, b, a)

def __pow__(a, b):
    """Called for a ** b."""
    if isinstance(b, numbers.Real):
        return multiplicative(operators.pow, a, b)
    return NotImplemented

def __rpow__(a, b):
    """Called for b ** a."""
    return NotImplemented

