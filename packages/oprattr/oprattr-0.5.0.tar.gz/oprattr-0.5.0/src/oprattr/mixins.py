import collections.abc
import numbers

import numpy

from . import abstract
from . import typeface


T = typeface.TypeVar('T')


class Real:
    """Mixin for adding basic real-valued operator support."""

    def __abs__(self):
        return self

    def __pos__(self):
        return self

    def __neg__(self):
        return self

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return (self < other) and (self == other)

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def __add__(self, other):
        return self

    def __radd__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __rsub__(self, other):
        return self

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __truediv__(self, other):
        return self

    def __rtruediv__(self, other):
        return self

    def __floordiv__(self, other):
        return self

    def __rfloordiv__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __rmod__(self, other):
        return self

    def __pow__(self, other):
        return self

    def __rpow__(self, other):
        return self


UserFunction = collections.abc.Callable[..., T]


class Numpy:
    """Mixin for adding support for `numpy` functions to numeric objects.
    
    Classes that inherit from this class may implement support for `numpy`
    universal functions ("ufuncs"; e.g., `numpy.sqrt`) by overloading
    `_apply_ufunc`, and may implement support for `numpy` public functions
    (e.g., `numpy.squeeze`) by overloading `_apply_function` and registering
    individual function implementations via `implementation`.

    It is important to note that the use cases of this class extend beyond
    array-like objects. Both single- and multi-valued objects can benefit from
    implementing support for `numpy` universal and public functions. For
    example, it is possible to apply `numpy.sqrt` to both a real number and an
    array

    >>> numpy.sqrt(4)
    2.0
    >>> numpy.sqrt([4, 9])
    array([2., 3.])

    Even the trivial application of `numpy.mean` to a real number is defined:

    >>> numpy.mean(2.5)
    2.5

    Notes
    -----
    - This class does not inherit from `numpy.lib.mixins.NDArrayOperatorsMixin`,
      which implements most of the built-in Python numeric operators via
      `__array_ufunc__`, because it assumes that subclasses independently
      implement those methods.
    """

    def __init_subclass__(cls):
        cls._UFUNC_TYPES |= {cls}
        cls._FUNCTION_TYPES |= {cls}
        cls._FUNCTIONS = {}

    _UFUNC_TYPES = {
        numpy.ndarray,
        numbers.Number,
        list,
        abstract.Quantity,
    }

    def __array_ufunc__(self, ufunc, method, *args, **kwargs):
        """Provide support for `numpy` universal functions.

        See https://numpy.org/doc/stable/reference/arrays.classes.html for more
        information on use of this special method.

        Notes
        -----
        - This method first ensures that the input types (as well as the type of
          `out`, if passed via keyword) are supported types. It then checks for
          a custom implementation of `ufunc`. If there is a custom
          implementation, this method applies it and returns the result. If
          there is no custom implementation, this method passes control to
          `_apply_ufunc`, to allow subclass customization.
        - See `implementation` for additional guidance on custom
          implementations.

        See Also
        --------
        `implementation`
            Class method for registering custom ufunc implementations.

        `_apply_ufunc`
            Instance method that allows custom handling of ufuncs corresponding
            to standard Python numerical operators.
        """
        out = kwargs.get('out', ())
        accepted = tuple(self._UFUNC_TYPES)
        if not all(isinstance(x, accepted) for x in args + out):
            return NotImplemented
        if out:
            kwargs['out'] = tuple(
                x._data if isinstance(x, abstract.Quantity)
                else x for x in out
            )
        if self._implements(ufunc):
            operator = self._FUNCTIONS[ufunc]
            return operator(*args, **kwargs)
        return self._apply_ufunc(ufunc, method, *args, **kwargs)

    def _apply_ufunc(self, ufunc, method, *args, **kwargs):
        """Apply a `numpy` universal function (a.k.a "ufunc") to data.

        Notes
        -----
        - Subclasses that wish to customize support for ufuncs should overload
          this method instead of `__array_ufunc__`.
        - Subclasses should prefer to define custom implementations of specific
          universal functions and register each via `implementation`, rather
          than implementing function-specific logic in this method, since
          `__array_ufunc__` will check for a custom implementation of a given
          function before calling this method.
        - The default implementation of this method applies the given ufunc to
          real-valued data and directly returns the `numpy` result, without
          attempting to create a new instance of the custom subclass.

        See Also
        --------
        `implementation`
            Class method for registering custom ufunc implementations.

        `__array_ufunc__`
            The entry point for `numpy` universal functions.
        """
        operator = getattr(ufunc, method)
        values = self._get_numpy_args(args)
        try:
            data = operator(*values, **kwargs)
        except TypeError as err:
            raise TypeError(
                f"Unable to apply {ufunc} to {args}"
            ) from err
        if method != 'at':
            return data

    _FUNCTION_TYPES = {
        numpy.ndarray,
        abstract.Object,
     } | set(numpy.ScalarType)

    def __array_function__(self, func, types, args, kwargs):
        """Provide support for functions in the `numpy` public API.

        See https://numpy.org/doc/stable/reference/arrays.classes.html for more
        information of use of this special method. The implementation shown here
        is a combination of the example on that page and code from the
        definition of `EncapsulateNDArray.__array_function__` in
        https://github.com/dask/dask/blob/main/dask/array/tests/test_dispatch.py

        Notes
        -----
        - This method first checks that all `types` are in
          `self._FUNCTION_TYPES`, thereby allowing subclasses that don't
          override `__array_function__` to handle objects of this type. It then
          checks for a custom implementation of `func`. If there is a custom
          implementation, this method applies it and returns the result. If
          there is no custom implementation, this method passes control to
          `_apply_function`, to allow subclass customization.
        - See `implementation` for additional guidance on custom
          implementations.

        See Also
        --------
        `implementation`
            Class method for registering custom function implementations.

        `_apply_function`
            Instance method that allows custom handling of `numpy` public
            functions when there is no registered custom implementation.
        """
        accepted = tuple(self._FUNCTION_TYPES)
        if not all(issubclass(ti, accepted) for ti in types):
            return NotImplemented
        if self._implements(func):
            return self._FUNCTIONS[func](*args, **kwargs)
        return self._apply_function(func, types, args, kwargs)

    def _apply_function(self, func, types, args, kwargs):
        """Apply a function in the `numpy` public API.

        Notes
        -----
        - Subclasses that wish to customize support for public functions should
          overload this method instead of `__array_function__`.
        - Subclasses should prefer to define custom implementations of specific
          public functions and register each via `implementation`, rather than
          implementing function-specific logic in this method, since
          `__array_function__` will check for a custom implementation of a given
          function before calling this method.
        - The default implementation calls `_get_numpy_array` for access to
          real-valued data via an instance of `numpy.ndarray`, `_get_numpy_args`
          to convert `args` to appropriate operands, and `_get_numpy_types` to
          extract appropriate operand types. Subclasses may choose to overload
          any of those individual methods instead of overloading this method.

        See Also
        --------
        `implementation`
            Class method for registering custom ufunc implementations.

        `__array_function__`
            The entry point for `numpy` public functions.
        """
        array = self._get_numpy_array()
        if array is None:
            return NotImplemented
        if not isinstance(array, numpy.ndarray):
            raise TypeError(
                f"{self.__class__.__qualname__}._get_numpy_array"
                " did not return a numpy.ndarray"
            ) from None
        args = self._get_numpy_args(args)
        types = self._get_numpy_types(types)
        return array.__array_function__(func, types, args, kwargs)

    def _get_numpy_array(self) -> numpy.typing.NDArray | None:
        """Convert the data interface to an array for `numpy` mixin methods.
        
        Notes
        -----
        - This method allows subclass implementations to control how they
          convert their data interface to a `numpy.ndarray` for use with `numpy`
          public functions.
        - Returning `None` from this method will cause `_apply_function` to
          return `NotImplemented`.
        - The default implementation unconditionally returns `None`.
        """
        return

    def _get_numpy_args(self, args):
        """Convert `args` to operands of a `numpy` function.

        This method will call `~_get_arg_data` on each member of `args` in order
        to build a `tuple` of suitable operands. Subclasses may overload
        `~_get_arg_data` to customize access to their data attribute.
        """
        return tuple(self._get_arg_data(arg) for arg in args)

    def _get_arg_data(self, arg):
        """Convert `arg` to an operand of a `numpy` function.

        See Also
        --------
        `~_get_numpy_args`
            The method that calls this method in a loop.

        Notes
        -----
        - This method allows a subclass to customize how `numpy` functions
          access its data attribute.
        - The default implementation will return the `data` attribute of a of
          `arg` if `arg` is an instance of the base object class; otherwise, it
          will return the unmodified argument.
        """
        if isinstance(arg, abstract.Quantity):
            return arg._data
        return arg

    def _get_numpy_types(self, types):
        """Extract appropriate types for a `numpy` function.
        
        Notes
        -----
        - This method allows subclasses to restrict the object types that they
          pass to `numpy` public functions via `_apply_function`.
        - The default implementation returns a tuple that contains all types
          except for subtypes of `~_types.Quantity`.
        """
        return tuple(
            ti for ti in types
            if not issubclass(ti, abstract.Object)
        )

    @classmethod
    def _implements(cls, operation: collections.abc.Callable):
        """True if this class defines a custom implementation for `operation`.
        
        This is a helper methods that gracefully handles the case in which a
        subclass does not support custom operator implementations.
        """
        try:
            result = operation in cls._FUNCTIONS
        except TypeError:
            return False
        return result

    _FUNCTIONS: dict[str, collections.abc.Callable]=None
    """Internal collection of custom `numpy` function implementations."""

    @classmethod
    def implementation(cls, numpy_function: collections.abc.Callable, /):
        """Register a custom implementation of this `numpy` function.

        Parameters
        ----------
        numpy_function : callable
            The `numpy` universal or public function to implement.

        Notes
        -----
        - Users may register `numpy` universal functions (a.k.a. ufuncs;
          https://numpy.org/doc/stable/reference/ufuncs.html) as well as
          functions in the public `numpy` API (e.g., `numpy.mean`). This may be
          important if, for example, a class needs to implement a custom version
          of `numpy.sqrt`, which is a ufunc.
        - See https://numpy.org/doc/stable/reference/arrays.classes.html for the
          suggestion on which this method is based.

        Examples
        --------
        Overload `numpy.mean` for an existing class called `Array` with a
        version that accepts no keyword arguments:

        ```
            @Array.implementation(numpy.mean)
            def mean(a: Array, **kwargs) -> Array:
                if kwargs:
                    msg = "Cannot pass keywords to numpy.mean with Array" raise
                    TypeError(msg)
                return numpy.sum(a) / len(a)
        ```

        This will compute the mean of the underlying data when called with no
        arguments, but will raise an exception when called with arguments:

            >>> v = Array([[1, 2], [3, 4]])
            >>> numpy.mean(v)
            5.0
            >>> numpy.mean(v, axis=0)
            ...
            TypeError: Cannot pass keywords to numpy.mean with Array

        See Also
        --------
        `~implements`
        """
        if not callable(numpy_function):
            raise TypeError(
                "The target operation of a custom numpy implementation"
                " must be callable"
            ) from None
        def decorator(user_function: UserFunction):
            if cls._FUNCTIONS is None:
                raise NotImplementedError(
                    f"Type {cls} does not support custom implementations"
                    " of numpy functions"
                ) from None
            cls._FUNCTIONS[numpy_function] = user_function
            return user_function
        return decorator

    @classmethod
    def implement(
        cls,
        numpy_function: collections.abc.Callable,
        user_function: UserFunction,
        /,
    ) -> None:
        """Implement a `numpy` function via a given user function.

        This method serves as an alternative to the class method
        `implementation`, which is primarily meant to be used as a decorator.
        This method allows the user to directly associate a custom
        implementation with the target `numpy` function.

        Parameters
        ----------
        numpy_function : callable
            The `numpy` universal or public function to implement.

        user_function: callable
            The custom implementation to associate with `numpy_function`.

        Examples
        --------
        Here is an alternative to the `~implementation` example usage:

        ```
            def mean(a: Array, **kwargs) -> Array:
                if kwargs:
                    msg = "Cannot pass keywords to numpy.mean with Array" raise
                    TypeError(msg)
                return numpy.sum(a) / len(a)

            Array.implement(numpy.mean, mean)
        ```

        However, a more useful application may be to associate multiple `numpy`
        functions with a single custom implementation:

        ```
            def trig(f: numpy.ufunc):
                def method(a: Array):
                    ... # custom implementation
                return method

            for f in {numpy.sin, numpy.cos, numpy.tan}:
                Array.implement(f, trig(f))
        ```

        See Also
        --------
        `~implementation`
        """
        if not callable(numpy_function):
            raise TypeError(
                "The target operation of a custom numpy implementation"
                " must be callable"
            ) from None
        if cls._FUNCTIONS is None:
            raise NotImplementedError(
                f"Type {cls} does not support custom implementations"
                " of numpy functions"
            ) from None
        cls._FUNCTIONS[numpy_function] = user_function

