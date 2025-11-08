"""
This script generates and echos exceptions related to operations on instances of
the `Operand` class. It is meant as a supplement to rigorous tests.
"""

import oprattr

x = oprattr.Operand(1, name='A')
y = oprattr.Operand(2, name='B')

cases = (
    (oprattr.operators.lt, x, y),
    (oprattr.operators.lt, x, 2),
    (oprattr.operators.lt, 2, x),
    (oprattr.operators.add, x, y),
    (oprattr.operators.add, x, 2),
    (oprattr.operators.add, 2, y),
    (oprattr.operators.abs, x),
    (oprattr.operators.mul, x, 'y'),
    (oprattr.operators.mul, 'x', y),
    (oprattr.operators.pow, x, 2)
)

for f, *args in cases:
    try:
        f(*args)
    except Exception as exc:
        print(f"Caught {type(exc).__qualname__}: {exc}")
    else:
        strargs = ', '.join(str(arg) for arg in args)
        print(f"Calling {f} on {strargs} did not raise an exception")

