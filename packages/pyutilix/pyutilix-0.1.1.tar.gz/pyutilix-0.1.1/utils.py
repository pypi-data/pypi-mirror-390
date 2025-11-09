import math


def nearest(x, nums):
    return min(nums, key=lambda n: abs(n-x))


def clamp(value, _min, _max):
    return max(_min, min(value, _max))


class Clamped:
    def __init__(self, value, min_val, max_val, loop=False):
        self._min = min_val
        self._max = max_val
        self.loop = loop
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        if not self.loop:
            self._value = clamp(new,  self._min, self._max)
        else:
            range_size = self._max - self._min + 1
            _value = (new - self._min) % range_size + self._min
            self._value = clamp(_value, self._min, self._max)

    def __iadd__(self, other):
        self.value = self._value + other
        return self

    def __isub__(self, other):
        self.value = self._value - other
        return self

    def __imul__(self, other):
        self.value = self._value * other
        return self

    def __itruediv__(self, other):
        self.value = self._value / other
        return self

    def __imod__(self, other):
        self.value = self._value % other
        return self

    def __ipow__(self, other):
        self.value = self._value ** other
        return self

    def __add__(self, other):
        return Clamped(self._value + other, self._min, self._max, self.loop)

    def __sub__(self, other):
        return Clamped(self._value - other, self._min, self._max, self.loop)

    def __mul__(self, other):
        return Clamped(self._value * other, self._min, self._max, self.loop)

    def __truediv__(self, other):
        return Clamped(self._value / other, self._min, self._max, self.loop)

    def __mod__(self, other):
        return Clamped(self._value % other, self._min, self._max, self.loop)

    def __pow__(self, other):
        return Clamped(self._value ** other, self._min, self._max, self.loop)

    def __neg__(self):
        return Clamped(-self._value, self._min, self._max, self.loop)

    def __pos__(self):
        return Clamped(+self._value, self._min, self._max, self.loop)

    def __abs__(self):
        return Clamped(abs(self._value), self._min, self._max, self.loop)

    def __str__(self):
        return str(self._value)


def to_base(value, first_base, second_base):
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    dec_value = int(str(value), first_base)
    while dec_value > 0:
        result = alphabet[dec_value % second_base] + result
        dec_value //= second_base
    return result


def reverse(obj):
    if isinstance(obj, (int, float)):
        return math.copysign(type(obj)(str(abs(obj))[::-1]), obj)
    else:
        return obj[::-1]


def sign(x):
    return int(math.copysign(1, x)) if x != 0 else 0


# Aliases
closest = nearest
nrst = nearest
