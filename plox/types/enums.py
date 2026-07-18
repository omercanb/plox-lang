from enum import Enum, auto


class FunctionType(Enum):
    none = auto()
    function = auto()
    lmbda = auto()
    method = auto()
    initializer = auto()


class ClassType(Enum):
    none = auto()
    cls = auto()
    subclass = auto()
