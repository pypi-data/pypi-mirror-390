import collections.abc
import functools
import numbers

from numerical import operators
import numpy

from . import abstract
from . import mixins
from . import typeface
from ._operations import (
    unary,
    equality,
    ordering,
    additive,
    multiplicative,
)


T = typeface.TypeVar('T')


class Operand(abstract.Object[T], mixins.Numpy):
    """A concrete implementation of a real-valued object."""

    def __abs__(self):
        """Called for abs(self)."""
        return unary(operators.abs, self)

    def __pos__(self):
        """Called for +self."""
        return unary(operators.pos, self)

    def __neg__(self):
        """Called for -self."""
        return unary(operators.neg, self)

    def __eq__(self, other):
        """Called for self == other."""
        return equality(operators.eq, self, other)

    def __ne__(self, other):
        """Called for self != other."""
        return equality(operators.ne, self, other)

    def __lt__(self, other):
        """Called for self < other."""
        return ordering(operators.lt, self, other)

    def __le__(self, other):
        """Called for self <= other."""
        return ordering(operators.le, self, other)

    def __gt__(self, other):
        """Called for self > other."""
        return ordering(operators.gt, self, other)

    def __ge__(self, other):
        """Called for self >= other."""
        return ordering(operators.ge, self, other)

    def __add__(self, other):
        """Called for self + other."""
        return additive(operators.add, self, other)

    def __radd__(self, other):
        """Called for other + self."""
        return additive(operators.add, other, self)

    def __sub__(self, other):
        """Called for self - other."""
        return additive(operators.sub, self, other)

    def __rsub__(self, other):
        """Called for other - self."""
        return additive(operators.sub, other, self)

    def __mul__(self, other):
        """Called for self * other."""
        return multiplicative(operators.mul, self, other)

    def __rmul__(self, other):
        """Called for other * self."""
        return multiplicative(operators.mul, other, self)

    def __truediv__(self, other):
        """Called for self / other."""
        return multiplicative(operators.truediv, self, other)

    def __rtruediv__(self, other):
        """Called for other / self."""
        return multiplicative(operators.truediv, other, self)

    def __floordiv__(self, other):
        """Called for self // other."""
        return multiplicative(operators.floordiv, self, other)

    def __rfloordiv__(self, other):
        """Called for other // self."""
        return multiplicative(operators.floordiv, other, self)

    def __mod__(self, other):
        """Called for self % other."""
        return multiplicative(operators.mod, self, other)

    def __rmod__(self, other):
        """Called for other % self."""
        return multiplicative(operators.mod, other, self)

    def __pow__(self, other):
        """Called for self ** other."""
        if isinstance(other, numbers.Real):
            return multiplicative(operators.pow, self, other)
        return NotImplemented

    def __rpow__(self, other):
        """Called for other ** self."""
        return NotImplemented

    def __array__(self, *args, **kwargs):
        """Called for numpy.array(self)."""
        return numpy.array(self._data, *args, **kwargs)

    def _apply_ufunc(self, ufunc, method, *args, **kwargs):
        if ufunc in (numpy.equal, numpy.not_equal):
            # NOTE: We are probably here because the left operand is a
            # `numpy.ndarray`, which would otherwise take control and return the
            # pure `numpy` result.
            f = getattr(ufunc, method)
            return equality(f, *args)
        return super()._apply_ufunc(ufunc, method, *args, **kwargs)


@Operand.implementation(numpy.array_equal)
def array_equal(
    x: numpy.typing.ArrayLike,
    y: numpy.typing.ArrayLike,
    **kwargs
) -> bool:
    """Called for numpy.array_equal(x, y)"""
    return numpy.array_equal(numpy.array(x), numpy.array(y), **kwargs)


@Operand.implementation(numpy.gradient)
def gradient(x: Operand[T], *args, **kwargs):
    """Called for numpy.gradient(x)."""
    data = numpy.gradient(x._data, *args, **kwargs)
    meta = {}
    for key, value in x._meta.items():
        try:
            v = numpy.gradient(value, **kwargs)
        except TypeError as exc:
            raise TypeError(
                "Cannot compute numpy.gradient(x)"
                f" because metadata attribute {key!r}"
                " does not support this operation"
            ) from exc
        else:
            meta[key] = v
    if isinstance(data, (list, tuple)):
        r = [type(x)(array, **meta) for array in data]
        if isinstance(data, tuple):
            return tuple(r)
        return r
    return type(x)(data, **meta)


def wrapnumpy(f: collections.abc.Callable):
    """Implement a numpy function for objects with metadata."""
    @functools.wraps(f)
    def method(x: Operand[T], **kwargs):
        """Apply a numpy function to x."""
        data = f(x._data, **kwargs)
        meta = {}
        for key, value in x._meta.items():
            try:
                v = f(value, **kwargs)
            except TypeError as exc:
                raise TypeError(
                    f"Cannot compute numpy.{f.__qualname__}(x)"
                    f" because metadata attribute {key!r}"
                    " does not support this operation"
                ) from exc
            else:
                meta[key] = v
        return type(x)(data, **meta)
    return method


_OPERAND_UFUNCS = (
    numpy.sqrt,
    numpy.sin,
    numpy.cos,
    numpy.tan,
    numpy.log,
    numpy.log2,
    numpy.log10,
)


_OPERAND_FUNCTIONS = (
    numpy.squeeze,
    numpy.mean,
    numpy.sum,
    numpy.cumsum,
    numpy.transpose,
    numpy.trapezoid,
)


for f in _OPERAND_UFUNCS + _OPERAND_FUNCTIONS:
    Operand.implement(f, wrapnumpy(f))


