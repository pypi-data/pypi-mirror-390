import numpy.typing

from . import _abstract
from . import mixins
from . import _typeface


T = _typeface.TypeVar('T')

class Operand(_abstract.Object[T], mixins.Numpy):
    """A concrete implementation of a real-valued object."""

    def __abs__(self) -> _typeface.Self:
        """Called for abs(self)."""

    def __pos__(self) -> _typeface.Self:
        """Called for +self."""

    def __neg__(self) -> _typeface.Self:
        """Called for -self."""

    def __eq__(self, other) -> bool:
        """Called for self == other."""

    def __ne__(self, other) -> bool:
        """Called for self != other."""

    def __lt__(self, other) -> bool | numpy.typing.NDArray[numpy.bool]:
        """Called for self < other."""

    def __le__(self, other) -> bool | numpy.typing.NDArray[numpy.bool]:
        """Called for self <= other."""

    def __gt__(self, other) -> bool | numpy.typing.NDArray[numpy.bool]:
        """Called for self > other."""

    def __ge__(self, other) -> bool | numpy.typing.NDArray[numpy.bool]:
        """Called for self >= other."""

    def __add__(self, other) -> _typeface.Self:
        """Called for self + other."""

    def __radd__(self, other) -> _typeface.Self:
        """Called for other + self."""

    def __sub__(self, other) -> _typeface.Self:
        """Called for self - other."""

    def __rsub__(self, other) -> _typeface.Self:
        """Called for other - self."""

    def __mul__(self, other) -> _typeface.Self:
        """Called for self * other."""

    def __rmul__(self, other) -> _typeface.Self:
        """Called for other * self."""

    def __truediv__(self, other) -> _typeface.Self:
        """Called for self / other."""

    def __rtruediv__(self, other) -> _typeface.Self:
        """Called for other / self."""

    def __floordiv__(self, other) -> _typeface.Self:
        """Called for self // other."""

    def __rfloordiv__(self, other) -> _typeface.Self:
        """Called for other // self."""

    def __mod__(self, other) -> _typeface.Self:
        """Called for self % other."""

    def __rmod__(self, other) -> _typeface.Self:
        """Called for other % self."""

    def __pow__(self, other) -> _typeface.Self:
        """Called for self ** other."""

    def __rpow__(self, other):
        """Called for other ** self."""

