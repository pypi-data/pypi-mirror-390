from typing import (
    Any,
    Callable,
    Protocol,
    Self,
    Generic,
    Type,
    TypeVar,
    Union,
    cast,
    runtime_checkable,
)
from dataclasses import dataclass
import copy

type ParameterValue[T] = tuple[ParameterBase[T], T]

T = TypeVar("T")


@runtime_checkable
class Parameter[T](Protocol):
    """Protocol for Parameters"""

    target: str
    help: str

    def parse(self, value: str | None) -> T: ...
    def __eq__(self, value: object, /) -> bool: ...


type TypeCallback[T] = Union[Callable[[str | None], T], Type[T]]


@dataclass(frozen=True, kw_only=True, slots=True, eq=False)
class ParameterBase(Parameter[T]):
    """Base class for a Parameter"""

    type: TypeCallback
    default: T | None = None
    required: bool
    target: str
    help: str

    def copy(self) -> Self:
        return copy.deepcopy(self)

    def parse(self, value: str | None) -> T:
        if value:
            return self.type(value)
        elif self.default is not None:
            return self.default
        else:
            return self.type(None)

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, ParameterBase):
            return self.target == value.target
        else:
            return NotImplemented


@dataclass(frozen=True, kw_only=True, slots=True, eq=False)
class KwParam(ParameterBase[T]):
    """Keyword parameter, usable in many parsers"""

    short: str
    long: str

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, KwParam):
            attrs = ["target", "long", "short"]
            return all([getattr(self, attr) == getattr(value, attr) for attr in attrs])
        else:
            return NotImplemented

    @classmethod
    def new(
        cls,
        *,
        target: str,
        tp: TypeCallback,
        long: str = "",
        short: str = "",
        default: T | None = None,
        required: bool = False,
        help="",
    ) -> Self:
        """
        Simple factory method to create KwParam with optional fields, fills up with base values
        """
        return cls(
            type=tp,
            default=default,
            target=target,
            short=short,
            long=long,
            required=required,
            help=help,
        )

    @classmethod
    def new_simple(
        cls,
        target: str,
        *,
        tp: TypeCallback = str,
        default: T | None = None,
        required: bool = False,
        help: str = "",
    ) -> Self:
        """
        Initialize simple parameter with short = target[0], long = target
        """
        return cls(
            short=target[0],
            long=target,
            type=tp,
            default=default,
            target=target,
            required=required,
            help=help,
        )

    @classmethod
    def new_long(
        cls,
        *,
        target: str,
        short: str = "",
        tp: Callable[[str | None], T] = str,
        long: str = "",
        default: T | None = None,
        required: bool = False,
        help: str = "",
    ) -> Self:
        """
        Initialize a Parameter with long and optional short form, use target as default for long and first char of long as short
        """
        long = long or target
        return cls(
            short=short,
            long=long,
            type=tp,
            default=default,
            target=target,
            required=required,
            help=help,
        )

    @classmethod
    def new_short(
        cls,
        *,
        target: str,
        short: str,
        tp: Callable[[str | None], T] = str,
        default: T | None = None,
        required: bool = False,
        help: str = "",
    ) -> Self:
        """
        Initialize a Parameter with long and optional short form, use target as default for long and first char of long as short
        """
        return cls(
            short=short,
            long="",
            type=tp,
            default=default,
            target=target,
            required=required,
            help=help,
        )


@dataclass(frozen=True, kw_only=True, slots=True, eq=False)
class FlagParam(KwParam[T]):
    """Parameter for boolean values and toggleable flags"""

    @classmethod
    def new(  # type: ignore
        cls,
        *,
        target: str,
        short: str = "",
        long: str = "",
        default: bool = False,
        required: bool = False,
        help: str = "",
    ) -> Self:
        return cls(
            short=short,
            long=long,
            type=bool,
            default=cast(T, default),
            target=target,
            required=required,
            help=help,
        )

    @classmethod
    def new_simple(  # type: ignore
        cls, target: str, help: str = ""
    ) -> Self:
        """
        Initialize a flag parameter that accepts a toggleable boolean flag
        """
        return cls(
            short=target[0],
            long=target,
            type=bool,
            default=cast(T, False),
            target=target,
            required=False,
            help=help,
        )


@dataclass(frozen=True, kw_only=True, slots=True, eq=False)
class PositionalParam(ParameterBase[T]):
    """Cli parameter, may not be used in e.g. file parsers"""

    position: int

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, PositionalParam):
            return (self.position, self.target) == (value.position, value.target)
        else:
            return NotImplemented

    @classmethod
    def new(
        cls,
        pos: int,
        target: str,
        tp: Any = str,
        default: T = None,
        required: bool = False,
        help: str = "",
    ):
        """
        Initialize a new Parameter with position and target, default type is str and no default value
        """
        return cls(
            type=tp,
            position=pos,
            default=default,
            target=target,
            required=required,
            help=help,
        )


class Namespace:
    """Container for read parameters"""

    def __init__(self, **kwargs) -> None:
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{k!r}={v!r}' for k, v in self.__dict__.items()])})"

    def get(self, name: str) -> Any:
        return self.__dict__[name]

    def __or__(self, other: object) -> "Namespace":
        if isinstance(other, Namespace):
            return Namespace(**self.__dict__, **other.__dict__)
        else:
            return NotImplemented

    def __ior__(self, other: object) -> Self:
        if isinstance(other, Namespace):
            self.__dict__.update(other.__dict__)
            return self
        else:
            return NotImplemented
