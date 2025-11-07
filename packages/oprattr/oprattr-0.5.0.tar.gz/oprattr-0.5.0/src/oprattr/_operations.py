from numerical import operators

from .abstract import (
    Quantity,
    Object,
)


class MetadataError(TypeError):
    """A metadata-related TypeError occurred."""

    def __init__(
        self,
        f: operators.Operator,
        *args,
        error: str | None = None,
        key: str | None = None,
    ) -> None:
        super().__init__(*args)
        self._f = f
        self._error = error
        self._key = key

    def __str__(self):
        """Called when handling the exception."""
        types = [type(arg) for arg in self.args]
        return _build_error_message(
            self._f,
            *types,
            error=self._error,
            key=self._key,
        )


def _build_error_message(
    f: operators.Operator,
    *types: type,
    error: str | None = None,
    key: str | None = None,
) -> str:
    """Helper for `_raise_metadata_exception`.
    
    This function should avoid raising an exception if at all possible, and
    instead return the default error message, since it is already being called
    as the result of an error elsewhere.
    """
    errmsg = f"Cannot compute {f}"
    errstr = error.lower() if isinstance(error, str) else ''
    if errstr == 'unequal':
        return f"{errmsg} between objects with unequal metadata"
    if errstr in {'non-empty', 'nonempty'}:
        if len(types) == 2:
            a, b = types
            endstr = "because {} has metadata"
            if issubclass(a, Object):
                return f"{errmsg} between {a} and {b} {endstr.format(str(a))}"
            if issubclass(b, Object):
                return f"{errmsg} between {a} and {b} {endstr.format(str(b))}"
    if errstr == 'type':
        if key is None:
            keystr = "a metadata attribute"
        else:
            keystr = f"metadata attribute {key!r}"
        midstr = f"because {keystr}"
        endstr = "does not support this operation"
        if len(types) == 1:
            return f"{errmsg} of {types[0]} {midstr} {endstr}"
        if len(types) == 2:
            a, b = types
            return f"{errmsg} between {a} and {b} {midstr} {endstr}"
    return errmsg


def unary(f: operators.Operator, a):
    """Compute the unary operation f(a)."""
    if isinstance(a, Quantity):
        meta = {}
        for key, value in a._meta.items():
            try:
                v = f(value)
            except TypeError as exc:
                raise MetadataError(f, a, error='type', key=key) from exc
            else:
                meta[key] = v
        return type(a)(f(a._data), **meta)
    return f(a)


def equality(f: operators.Operator, a, b):
    """Compute the equality operation f(a, b)."""
    x = a._data if isinstance(a, Quantity) else a
    y = b._data if isinstance(b, Quantity) else b
    fxy = f(x, y)
    try:
        iter(fxy)
    except TypeError:
        r = bool(fxy)
    else:
        r = all(fxy)
    isne = f(1, 2)
    if isinstance(a, Quantity) and isinstance(b, Quantity):
        if a._meta != b._meta:
            return isne
        return r
    if isinstance(a, Quantity):
        if not a._meta:
            return r
        return isne
    if isinstance(b, Quantity):
        if not b._meta:
            return r
        return isne
    return r


def ordering(f: operators.Operator, a, b):
    """Compute the ordering operation f(a, b)."""
    if isinstance(a, Quantity) and isinstance(b, Quantity):
        if a._meta == b._meta:
            return f(a._data, b._data)
        raise MetadataError(f, a, b, error='unequal') from None
    if isinstance(a, Quantity):
        if not a._meta:
            return f(a._data, b)
        raise MetadataError(f, a, b, error='non-empty') from None
    if isinstance(b, Quantity):
        if not b._meta:
            return f(a, b._data)
        raise MetadataError(f, a, b, error='non-empty') from None
    return f(a, b)


def additive(f: operators.Operator, a, b):
    """Compute the additive operation f(a, b)."""
    if isinstance(a, Quantity) and isinstance(b, Quantity):
        if a._meta == b._meta:
            return type(a)(f(a._data, b._data), **a._meta)
        raise MetadataError(f, a, b, error='unequal') from None
    if isinstance(a, Quantity):
        if not a._meta:
            return type(a)(f(a._data, b))
        raise MetadataError(f, a, b, error='non-empty') from None
    if isinstance(b, Quantity):
        if not b._meta:
            return type(b)(f(a, b._data))
        raise MetadataError(f, a, b, error='non-empty') from None
    return f(a, b)


def multiplicative(f: operators.Operator, a, b):
    """Compute the multiplicative operation f(a, b)."""
    if isinstance(a, Quantity) and isinstance(b, Quantity):
        keys = set(a._meta) & set(b._meta)
        meta = {}
        for key in keys:
            try:
                v = f(a._meta[key], b._meta[key])
            except TypeError as exc:
                raise MetadataError(f, a, b, error='type', key=key) from exc
            else:
                meta[key] = v
        for key, value in a._meta.items():
            if key not in keys:
                meta[key] = value
        for key, value in b._meta.items():
            if key not in keys:
                meta[key] = value
        return type(a)(f(a._data, b._data), **meta)
    if isinstance(a, Quantity):
        meta = {}
        for key, value in a._meta.items():
            try:
                v = f(value, b)
            except TypeError as exc:
                raise MetadataError(f, a, b, error='type', key=key) from exc
            else:
                meta[key] = v
        return type(a)(f(a._data, b), **meta)
    if isinstance(b, Quantity):
        meta = {}
        for key, value in b._meta.items():
            try:
                v = f(a, value)
            except TypeError as exc:
                raise MetadataError(f, a, b, error='type', key=key) from exc
            else:
                meta[key] = v
        return type(b)(f(a, b._data), **meta)
    return f(a, b)


