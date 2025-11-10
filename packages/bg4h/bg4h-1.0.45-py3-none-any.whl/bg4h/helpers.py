
import warnings


class DeprecatedAttr:
    def __init__(self, value, name, replacement=None):
        self.value = value
        self.name = name
        self.replacement = replacement

    def __get__(self, instance, owner):
        msg = f"{owner.__name__}.{self.name} is deprecated"
        if self.replacement:
            msg += f"; use {owner.__name__}.{self.replacement} instead"
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        return self.value