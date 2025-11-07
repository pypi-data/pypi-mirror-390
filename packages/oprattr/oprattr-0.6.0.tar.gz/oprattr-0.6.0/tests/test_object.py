import itertools
import numbers

import numpy
import pytest

import oprattr


class Symbol(oprattr.mixins.Numpy):
    """A symbolic test attribute."""

    def __init__(self, __x: str):
        self._x = __x

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self})"

    def __str__(self):
        return self._x

    def __abs__(self):
        return f"abs({self._x})"

    def __pos__(self):
        return f"+{self._x}"

    def __neg__(self):
        return f"-{self._x}"

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self._x == other._x
        if isinstance(other, str):
            return self._x == other
        return False

    def __ne__(self, other):
        return not (self == other)

    def __le__(self, other):
        return symbolic_binary(self, '<=', other)

    def __lt__(self, other):
        return symbolic_binary(self, '<', other)

    def __ge__(self, other):
        return symbolic_binary(self, '>=', other)

    def __gt__(self, other):
        return symbolic_binary(self, '>', other)

    def __add__(self, other):
        return symbolic_binary(self, '+', other)

    def __radd__(self, other):
        return symbolic_binary(other, '+', self)

    def __sub__(self, other):
        return symbolic_binary(self, '-', other)

    def __rsub__(self, other):
        return symbolic_binary(other, '-', self)

    def __mul__(self, other):
        return symbolic_binary(self, '*', other)

    def __rmul__(self, other):
        return symbolic_binary(other, '-', self)

    def __truediv__(self, other):
        return symbolic_binary(self, '/', other)

    def __rtruediv__(self, other):
        return symbolic_binary(other, '/', self)

    def __floordiv__(self, other):
        return symbolic_binary(self, '//', other)

    def __rfloordiv__(self, other):
        return symbolic_binary(other, '//', self)

    def __mod__(self, other):
        return symbolic_binary(self, '%', other)

    def __rmod__(self, other):
        return symbolic_binary(other, '%', self)

    def __pow__(self, other):
        if isinstance(other, numbers.Real):
            return f"{self} ** {other}"
        return NotImplemented


@Symbol.implementation(numpy.sqrt)
def symbol_sqrt(x: Symbol):
    return f"numpy.sqrt({x})"


@Symbol.implementation(numpy.sin)
def symbol_sin(x: Symbol):
    return f"numpy.sin({x})"


@Symbol.implementation(numpy.cos)
def symbol_cos(x: Symbol):
    return f"numpy.cos({x})"


@Symbol.implementation(numpy.tan)
def symbol_tan(x: Symbol):
    return f"numpy.tan({x})"


@Symbol.implementation(numpy.log)
def symbol_log(x: Symbol):
    return f"numpy.log({x})"


@Symbol.implementation(numpy.log2)
def symbol_log2(x: Symbol):
    return f"numpy.log2({x})"


@Symbol.implementation(numpy.log10)
def symbol_log10(x: Symbol):
    return f"numpy.log10({x})"


@Symbol.implementation(numpy.squeeze)
def symbol_squeeze(x: Symbol, **kwargs):
    return f"numpy.squeeze({x})"


@Symbol.implementation(numpy.mean)
def symbol_mean(x: Symbol, **kwargs):
    return f"numpy.mean({x})"


@Symbol.implementation(numpy.sum)
def symbol_sum(x: Symbol, **kwargs):
    return f"numpy.sum({x})"


@Symbol.implementation(numpy.cumsum)
def symbol_cumsum(x: Symbol, **kwargs):
    return f"numpy.cumsum({x})"


@Symbol.implementation(numpy.transpose)
def symbol_transpose(x: Symbol, **kwargs):
    return f"numpy.transpose({x})"


@Symbol.implementation(numpy.gradient)
def symbol_gradient(x: Symbol, **kwargs):
    return f"numpy.gradient({x})"


@Symbol.implementation(numpy.trapezoid)
def symbol_trapezoid(x: Symbol, **kwargs):
    return f"numpy.trapezoid({x})"


def symbolic_binary(a, op, b):
    if isinstance(a, (Symbol, str)) and isinstance(b, (Symbol, str)):
        return f"{a} {op} {b}"
    return NotImplemented


def test_initialize():
    """Test rules for initializing defined types."""
    assert isinstance(oprattr.Operand(+1), oprattr.Operand)
    assert isinstance(oprattr.Operand(+1.0), oprattr.Operand)
    assert isinstance(oprattr.Operand(-1), oprattr.Operand)
    assert isinstance(oprattr.Operand(-1.0), oprattr.Operand)
    assert isinstance(oprattr.Operand(numpy.array([1, 2])), oprattr.Operand)
    with pytest.raises(TypeError):
        oprattr.Operand([1, 2])
    with pytest.raises(TypeError):
        oprattr.Operand((1, 2))
    with pytest.raises(TypeError):
        oprattr.Operand({1, 2})
    with pytest.raises(TypeError):
        oprattr.Operand("+1")


def x(data, **metadata):
    """Convenience factory function."""
    return oprattr.Operand(data, **metadata)


def test_equality():
    """Test the == and != operations."""
    assert x(1) == x(1)
    assert x(1) != x(-1)
    assert x(1) == 1
    assert x(1) != -1
    sA = Symbol('A')
    sB = Symbol('B')
    assert x(1, name=sA) == x(1, name=sA)
    assert x(1, name=sA) != x(1, name=sB)
    assert x(1, name=sA) != 1
    assert 1 != x(1, name=sA)
    array = numpy.array([-1, +1])
    assert x(array) == x(array)
    assert x(array, name=sA) == x(array, name=sA)
    assert x(array, name=sA) != x(array, name=sB)
    assert x(array, name=sA) != array
    assert x(array) == array
    assert array == x(array)
    assert array != x(array, name=sA)


def test_ordering():
    """Test the >, <, >=, and <= operations."""
    assert x(1) < x(2)
    assert x(1) <= x(2)
    assert x(1) <= x(1)
    assert x(1) > x(0)
    assert x(1) >= x(0)
    assert x(1) >= x(1)
    nA = Symbol('A')
    nB = Symbol('B')
    assert x(1, name=nA) < x(2, name=nA)
    assert x(1, name=nA) <= x(2, name=nA)
    assert x(1, name=nA) <= x(1, name=nA)
    assert x(1, name=nA) > x(0, name=nA)
    assert x(1, name=nA) >= x(0, name=nA)
    assert x(1, name=nA) >= x(1, name=nA)
    with pytest.raises(ValueError):
         x(1, name=nA) < x(2, name=nB)
    with pytest.raises(ValueError):
         x(1, name=nA) <= x(2, name=nB)
    with pytest.raises(ValueError):
         x(1, name=nA) <= x(1, name=nB)
    with pytest.raises(ValueError):
         x(1, name=nA) > x(0, name=nB)
    with pytest.raises(ValueError):
         x(1, name=nA) >= x(0, name=nB)
    with pytest.raises(ValueError):
         x(1, name=nA) >= x(1, name=nB)
    assert x(1) < +2
    assert x(1) <= +2
    assert x(1) <= +1
    assert x(1) > 0
    assert x(1) >= 0
    assert x(1) >= +1
    with pytest.raises(TypeError):
         x(1, name=nA) < +2
    with pytest.raises(TypeError):
         x(1, name=nA) <= +2
    with pytest.raises(TypeError):
         x(1, name=nA) <= +1
    with pytest.raises(TypeError):
         x(1, name=nA) > 0
    with pytest.raises(TypeError):
         x(1, name=nA) >= 0
    with pytest.raises(TypeError):
         x(1, name=nA) >= +1


def test_unary():
    """Test the all unary operations."""
    assert abs(x(-1)) == x(1)
    assert +x(-1) == x(-1)
    assert -x(1) == x(-1)
    nA = Symbol('A')
    assert abs(x(-1, name=nA)) == x(1, name=Symbol('abs(A)'))
    assert +x(1, name=nA) == x(+1, name=Symbol('+A'))
    assert -x(1, name=nA) == x(-1, name=Symbol('-A'))
    with pytest.raises(TypeError):
        abs(x(-1, name='A'))
    with pytest.raises(TypeError):
        +x(1, name='A')
    with pytest.raises(TypeError):
        -x(1, name='A')


def test_additive():
    """Test the + and - operations."""
    assert x(1) + x(2) == x(3)
    nA = Symbol('A')
    nB = Symbol('B')
    assert x(1, name=nA) + x(2, name=nA) == x(3, name=nA)
    with pytest.raises(ValueError):
        x(1, name=nA) + x(2, name=nB)
    assert x(1) - x(2) == x(-1)
    assert x(1, name=nA) - x(2, name=nA) == x(-1, name=nA)
    with pytest.raises(ValueError):
        x(1, name=nA) - x(2, name=nB)
    assert x(1) + 2 == x(3)
    with pytest.raises(TypeError):
        x(1, name=nA) + 2
    assert x(1) - 2 == x(-1)
    with pytest.raises(TypeError):
        x(1, name=nA) - 2
    assert 2 + x(1) == x(3)
    with pytest.raises(TypeError):
        2 + x(1, name=nA)
    assert 2 - x(1) == x(1)
    with pytest.raises(TypeError):
        2 - x(1, name=nA)


def test_multiplicative():
    """Test the *, /, //, and % operations."""
    nA = Symbol('A')
    nB = Symbol('B')
    assert x(3, name=nA) * x(2, name=nB) == x(6, name=Symbol('A * B'))
    assert x(3, name=nA) / x(2, name=nB) == x(1.5, name=Symbol('A / B'))
    assert x(3, name=nA) // x(2, name=nB) == x(1, name=Symbol('A // B'))
    assert x(6, name=nA) % x(2, name=nB) == x(0, name=Symbol('A % B'))
    assert x(3, name=nA) * x(2) == x(6, name=nA)
    assert x(3, name=nA) / x(2) == x(1.5, name=nA)
    assert x(3, name=nA) // x(2) == x(1, name=nA)
    assert x(6, name=nA) % x(2) == x(0, name=nA)
    assert x(3) * x(2, name=nB) == x(6, name=nB)
    assert x(3) / x(2, name=nB) == x(1.5, name=nB)
    assert x(3) // x(2, name=nB) == x(1, name=nB)
    assert x(6) % x(2, name=nB) == x(0, name=nB)
    assert x(3) * 2 == x(6)
    assert x(3) / 2 == x(1.5)
    assert x(3) // 2 == x(1)
    assert x(6) % 2 == x(0)
    with pytest.raises(TypeError):
         x(3, name=nA) * 2
    with pytest.raises(TypeError):
         x(3, name=nA) / 2
    with pytest.raises(TypeError):
         x(3, name=nA) // 2
    with pytest.raises(TypeError):
         x(6, name=nA) % 2
    assert 3 * x(2) == x(6)
    assert 3 / x(2) == x(1.5)
    assert 3 // x(2) == x(1)
    assert 6 % x(2) == x(0)
    with pytest.raises(TypeError):
         3 * x(2, name=nA)
    with pytest.raises(TypeError):
         3 / x(2, name=nA)
    with pytest.raises(TypeError):
         3 // x(2, name=nA)
    with pytest.raises(TypeError):
         6 % x(2, name=nA)


def test_exponential():
    """Test the ** operation."""
    assert x(3) ** 2 == x(9)
    with pytest.raises(TypeError):
        x(3) ** x(2)
    with pytest.raises(TypeError):
        3 ** x(2)
    nA = Symbol('A')
    assert x(3, name=nA) ** 2 == x(9, name=Symbol('A ** 2'))
    with pytest.raises(TypeError):
        x(3, name=nA) ** x(2, name='B')
    with pytest.raises(TypeError):
        x(3, name='A') ** 2
    with pytest.raises(TypeError):
        x(3, name='A') ** x(2, name='A')
    with pytest.raises(TypeError):
        x(3, name=nA) ** x(2)
    with pytest.raises(TypeError):
        3 ** x(2, name=nA)
    with pytest.raises(TypeError):
        x(3) ** x(2, name=nA)


def test_trig():
    """Test `numpy` trigonometric ufuncs."""
    nA = Symbol('A')
    v = numpy.pi / 3
    this = x(v, name=nA)
    that = numpy.sin(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.sin(v), name=Symbol('numpy.sin(A)'))
    that = numpy.cos(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.cos(v), name=Symbol('numpy.cos(A)'))
    that = numpy.tan(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.tan(v), name=Symbol('numpy.tan(A)'))


def test_sqrt():
    """Test `numpy.sqrt`."""
    this = x(4, name=Symbol('A'))
    that = numpy.sqrt(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(2, name=Symbol('numpy.sqrt(A)'))


def test_logs():
    """Test `numpy` logarithmic ufuncs."""
    nA = Symbol('A')
    v = 10.0
    this = x(v, name=nA)
    that = numpy.log(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.log(v), name=Symbol('numpy.log(A)'))
    that = numpy.log2(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.log2(v), name=Symbol('numpy.log2(A)'))
    that = numpy.log10(this)
    assert isinstance(that, oprattr.Operand)
    assert that == x(numpy.log10(v), name=Symbol('numpy.log10(A)'))


def test_squeeze():
    """Test `numpy.squeeze`."""
    nA = Symbol('A')
    nR = Symbol('numpy.squeeze(A)')
    v = numpy.array([[[1], [2], [3]]])
    this = x(v, name=nA)
    that = numpy.squeeze(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.squeeze(v), name=nR))
    that = numpy.squeeze(this, axis=0)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.squeeze(v, axis=0), name=nR))
    that = numpy.squeeze(this, axis=-1)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.squeeze(v, axis=-1), name=nR))


def test_mean():
    """Test `numpy.mean`."""
    nA = Symbol('A')
    nR = Symbol('numpy.mean(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.mean(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.mean(v), name=nR))
    that = numpy.mean(this, axis=0)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.mean(v, axis=0), name=nR))
    that = numpy.mean(this, axis=-1)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.mean(v, axis=-1), name=nR))


def test_sum():
    """Test `numpy.sum`."""
    nA = Symbol('A')
    nR = Symbol('numpy.sum(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.sum(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.sum(v), name=nR))
    that = numpy.sum(this, axis=0)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.sum(v, axis=0), name=nR))
    that = numpy.sum(this, axis=-1)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.sum(v, axis=-1), name=nR))


def test_cumsum():
    """Test `numpy.cumsum`."""
    nA = Symbol('A')
    nR = Symbol('numpy.cumsum(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.cumsum(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.cumsum(v), name=nR))
    that = numpy.cumsum(this, axis=0)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.cumsum(v, axis=0), name=nR))
    that = numpy.cumsum(this, axis=-1)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.cumsum(v, axis=-1), name=nR))


def test_transpose():
    """Test `numpy.transpose`."""
    nA = Symbol('A')
    nR = Symbol('numpy.transpose(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.transpose(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.transpose(v), name=nR))
    for axes in itertools.permutations(range(v.ndim)):
        that = numpy.transpose(this, axes=axes)
        assert isinstance(that, oprattr.Operand)
        expected = x(numpy.transpose(v, axes=axes), name=nR)
        assert numpy.array_equal(that, expected)


def test_gradient():
    """Test `numpy.gradient`."""
    nA = Symbol('A')
    nR = Symbol('numpy.gradient(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.gradient(this)
    grad = numpy.gradient(v)
    for t, g in zip(that, grad):
        assert isinstance(t, oprattr.Operand)
        assert numpy.array_equal(t, x(g, name=nR))
    for axis in range(v.ndim):
        that = numpy.gradient(this, axis=axis)
        assert isinstance(that, oprattr.Operand)
        grad = numpy.gradient(v, axis=axis)
        assert numpy.array_equal(that, x(grad, name=nR))


def test_trapezoid():
    """Test `numpy.trapezoid`."""
    nA = Symbol('A')
    nR = Symbol('numpy.trapezoid(A)')
    v = numpy.arange(3*4*5).reshape(3, 4, 5)
    this = x(v, name=nA)
    that = numpy.trapezoid(this)
    assert isinstance(that, oprattr.Operand)
    assert numpy.array_equal(that, x(numpy.trapezoid(v), name=nR))
    for axis in range(v.ndim):
        that = numpy.trapezoid(this, axis=axis)
        assert isinstance(that, oprattr.Operand)
        trap = numpy.trapezoid(v, axis=axis)
        assert numpy.array_equal(that, x(trap, name=nR))

