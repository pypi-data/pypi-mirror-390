import collections.abc
import functools

import numpy

from . import abstract
from . import methods
from . import mixins
from . import typeface
from ._operations import equality


T = typeface.TypeVar('T')


class Operand(abstract.Object[T], mixins.Numpy):
    """A concrete implementation of a real-valued object."""

    __abs__ = methods.__abs__
    __pos__ = methods.__pos__
    __neg__ = methods.__neg__

    __eq__ = methods.__eq__
    __ne__ = methods.__ne__
    __lt__ = methods.__lt__
    __le__ = methods.__le__
    __gt__ = methods.__gt__
    __ge__ = methods.__ge__

    __add__ = methods.__add__
    __radd__ = methods.__radd__
    __sub__ = methods.__sub__
    __rsub__ = methods.__rsub__
    __mul__ = methods.__mul__
    __rmul__ = methods.__rmul__
    __truediv__ = methods.__truediv__
    __rtruediv__ = methods.__rtruediv__
    __floordiv__ = methods.__floordiv__
    __rfloordiv__ = methods.__rfloordiv__
    __mod__ = methods.__mod__
    __rmod__ = methods.__rmod__
    __pow__ = methods.__pow__
    __rpow__ = methods.__rpow__

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


