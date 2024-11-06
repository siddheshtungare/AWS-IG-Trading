import sys
import fractions
import decimal
from typing import Any

import numpy as np
import numpy.typing as npt

if sys.version_info >= (3, 11):
    from typing import assert_type
else:
    from typing_extensions import assert_type

c16 = np.complex128()
f8 = np.float64()
i8 = np.int64()
u8 = np.uint64()

c8 = np.complex64()
f4 = np.float32()
i4 = np.int32()
u4 = np.uint32()

dt = np.datetime64(0, "D")
td = np.timedelta64(0, "D")

b_ = np.bool()

b = bool()
c = complex()
f = float()
i = int()

AR = np.array([0], dtype=np.int64)
AR.setflags(write=False)

SEQ = (0, 1, 2, 3, 4)

# object-like comparisons

assert_type(i8 > fractions.Fraction(1, 5), Any)
assert_type(i8 > [fractions.Fraction(1, 5)], Any)
assert_type(i8 > decimal.Decimal("1.5"), Any)
assert_type(i8 > [decimal.Decimal("1.5")], Any)

# Time structures

assert_type(dt > dt, np.bool)

assert_type(td > td, np.bool)
assert_type(td > i, np.bool)
assert_type(td > i4, np.bool)
assert_type(td > i8, np.bool)

assert_type(td > AR, npt.NDArray[np.bool])
assert_type(td > SEQ, npt.NDArray[np.bool])
assert_type(AR > SEQ, npt.NDArray[np.bool])
assert_type(AR > td, npt.NDArray[np.bool])
assert_type(SEQ > td, npt.NDArray[np.bool])
assert_type(SEQ > AR, npt.NDArray[np.bool])

# boolean

assert_type(b_ > b, np.bool)
assert_type(b_ > b_, np.bool)
assert_type(b_ > i, np.bool)
assert_type(b_ > i8, np.bool)
assert_type(b_ > i4, np.bool)
assert_type(b_ > u8, np.bool)
assert_type(b_ > u4, np.bool)
assert_type(b_ > f, np.bool)
assert_type(b_ > f8, np.bool)
assert_type(b_ > f4, np.bool)
assert_type(b_ > c, np.bool)
assert_type(b_ > c16, np.bool)
assert_type(b_ > c8, np.bool)
assert_type(b_ > AR, npt.NDArray[np.bool])
assert_type(b_ > SEQ, npt.NDArray[np.bool])

# Complex

assert_type(c16 > c16, np.bool)
assert_type(c16 > f8, np.bool)
assert_type(c16 > i8, np.bool)
assert_type(c16 > c8, np.bool)
assert_type(c16 > f4, np.bool)
assert_type(c16 > i4, np.bool)
assert_type(c16 > b_, np.bool)
assert_type(c16 > b, np.bool)
assert_type(c16 > c, np.bool)
assert_type(c16 > f, np.bool)
assert_type(c16 > i, np.bool)
assert_type(c16 > AR, npt.NDArray[np.bool])
assert_type(c16 > SEQ, npt.NDArray[np.bool])

assert_type(c16 > c16, np.bool)
assert_type(f8 > c16, np.bool)
assert_type(i8 > c16, np.bool)
assert_type(c8 > c16, np.bool)
assert_type(f4 > c16, np.bool)
assert_type(i4 > c16, np.bool)
assert_type(b_ > c16, np.bool)
assert_type(b > c16, np.bool)
assert_type(c > c16, np.bool)
assert_type(f > c16, np.bool)
assert_type(i > c16, np.bool)
assert_type(AR > c16, npt.NDArray[np.bool])
assert_type(SEQ > c16, npt.NDArray[np.bool])

assert_type(c8 > c16, np.bool)
assert_type(c8 > f8, np.bool)
assert_type(c8 > i8, np.bool)
assert_type(c8 > c8, np.bool)
assert_type(c8 > f4, np.bool)
assert_type(c8 > i4, np.bool)
assert_type(c8 > b_, np.bool)
assert_type(c8 > b, np.bool)
assert_type(c8 > c, np.bool)
assert_type(c8 > f, np.bool)
assert_type(c8 > i, np.bool)
assert_type(c8 > AR, npt.NDArray[np.bool])
assert_type(c8 > SEQ, npt.NDArray[np.bool])

assert_type(c16 > c8, np.bool)
assert_type(f8 > c8, np.bool)
assert_type(i8 > c8, np.bool)
assert_type(c8 > c8, np.bool)
assert_type(f4 > c8, np.bool)
assert_type(i4 > c8, np.bool)
assert_type(b_ > c8, np.bool)
assert_type(b > c8, np.bool)
assert_type(c > c8, np.bool)
assert_type(f > c8, np.bool)
assert_type(i > c8, np.bool)
assert_type(AR > c8, npt.NDArray[np.bool])
assert_type(SEQ > c8, npt.NDArray[np.bool])

# Float

assert_type(f8 > f8, np.bool)
assert_type(f8 > i8, np.bool)
assert_type(f8 > f4, np.bool)
assert_type(f8 > i4, np.bool)
assert_type(f8 > b_, np.bool)
assert_type(f8 > b, np.bool)
assert_type(f8 > c, np.bool)
assert_type(f8 > f, np.bool)
assert_type(f8 > i, np.bool)
assert_type(f8 > AR, npt.NDArray[np.bool])
assert_type(f8 > SEQ, npt.NDArray[np.bool])

assert_type(f8 > f8, np.bool)
assert_type(i8 > f8, np.bool)
assert_type(f4 > f8, np.bool)
assert_type(i4 > f8, np.bool)
assert_type(b_ > f8, np.bool)
assert_type(b > f8, np.bool)
assert_type(c > f8, np.bool)
assert_type(f > f8, np.bool)
assert_type(i > f8, np.bool)
assert_type(AR > f8, npt.NDArray[np.bool])
assert_type(SEQ > f8, npt.NDArray[np.bool])

assert_type(f4 > f8, np.bool)
assert_type(f4 > i8, np.bool)
assert_type(f4 > f4, np.bool)
assert_type(f4 > i4, np.bool)
assert_type(f4 > b_, np.bool)
assert_type(f4 > b, np.bool)
assert_type(f4 > c, np.bool)
assert_type(f4 > f, np.bool)
assert_type(f4 > i, np.bool)
assert_type(f4 > AR, npt.NDArray[np.bool])
assert_type(f4 > SEQ, npt.NDArray[np.bool])

assert_type(f8 > f4, np.bool)
assert_type(i8 > f4, np.bool)
assert_type(f4 > f4, np.bool)
assert_type(i4 > f4, np.bool)
assert_type(b_ > f4, np.bool)
assert_type(b > f4, np.bool)
assert_type(c > f4, np.bool)
assert_type(f > f4, np.bool)
assert_type(i > f4, np.bool)
assert_type(AR > f4, npt.NDArray[np.bool])
assert_type(SEQ > f4, npt.NDArray[np.bool])

# Int

assert_type(i8 > i8, np.bool)
assert_type(i8 > u8, np.bool)
assert_type(i8 > i4, np.bool)
assert_type(i8 > u4, np.bool)
assert_type(i8 > b_, np.bool)
assert_type(i8 > b, np.bool)
assert_type(i8 > c, np.bool)
assert_type(i8 > f, np.bool)
assert_type(i8 > i, np.bool)
assert_type(i8 > AR, npt.NDArray[np.bool])
assert_type(i8 > SEQ, npt.NDArray[np.bool])

assert_type(u8 > u8, np.bool)
assert_type(u8 > i4, np.bool)
assert_type(u8 > u4, np.bool)
assert_type(u8 > b_, np.bool)
assert_type(u8 > b, np.bool)
assert_type(u8 > c, np.bool)
assert_type(u8 > f, np.bool)
assert_type(u8 > i, np.bool)
assert_type(u8 > AR, npt.NDArray[np.bool])
assert_type(u8 > SEQ, npt.NDArray[np.bool])

assert_type(i8 > i8, np.bool)
assert_type(u8 > i8, np.bool)
assert_type(i4 > i8, np.bool)
assert_type(u4 > i8, np.bool)
assert_type(b_ > i8, np.bool)
assert_type(b > i8, np.bool)
assert_type(c > i8, np.bool)
assert_type(f > i8, np.bool)
assert_type(i > i8, np.bool)
assert_type(AR > i8, npt.NDArray[np.bool])
assert_type(SEQ > i8, npt.NDArray[np.bool])

assert_type(u8 > u8, np.bool)
assert_type(i4 > u8, np.bool)
assert_type(u4 > u8, np.bool)
assert_type(b_ > u8, np.bool)
assert_type(b > u8, np.bool)
assert_type(c > u8, np.bool)
assert_type(f > u8, np.bool)
assert_type(i > u8, np.bool)
assert_type(AR > u8, npt.NDArray[np.bool])
assert_type(SEQ > u8, npt.NDArray[np.bool])

assert_type(i4 > i8, np.bool)
assert_type(i4 > i4, np.bool)
assert_type(i4 > i, np.bool)
assert_type(i4 > b_, np.bool)
assert_type(i4 > b, np.bool)
assert_type(i4 > AR, npt.NDArray[np.bool])
assert_type(i4 > SEQ, npt.NDArray[np.bool])

assert_type(u4 > i8, np.bool)
assert_type(u4 > i4, np.bool)
assert_type(u4 > u8, np.bool)
assert_type(u4 > u4, np.bool)
assert_type(u4 > i, np.bool)
assert_type(u4 > b_, np.bool)
assert_type(u4 > b, np.bool)
assert_type(u4 > AR, npt.NDArray[np.bool])
assert_type(u4 > SEQ, npt.NDArray[np.bool])

assert_type(i8 > i4, np.bool)
assert_type(i4 > i4, np.bool)
assert_type(i > i4, np.bool)
assert_type(b_ > i4, np.bool)
assert_type(b > i4, np.bool)
assert_type(AR > i4, npt.NDArray[np.bool])
assert_type(SEQ > i4, npt.NDArray[np.bool])

assert_type(i8 > u4, np.bool)
assert_type(i4 > u4, np.bool)
assert_type(u8 > u4, np.bool)
assert_type(u4 > u4, np.bool)
assert_type(b_ > u4, np.bool)
assert_type(b > u4, np.bool)
assert_type(i > u4, np.bool)
assert_type(AR > u4, npt.NDArray[np.bool])
assert_type(SEQ > u4, npt.NDArray[np.bool])
