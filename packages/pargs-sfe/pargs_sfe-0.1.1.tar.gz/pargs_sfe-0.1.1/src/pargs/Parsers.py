from typing import Protocol, Self, List, Dict, Any, Sequence, runtime_checkable
from abc import abstractmethod
import os
import sys
import json
import tomllib

from .Parameter import FlagParam, KwParam, Parameter, Namespace, PositionalParam
from .Exceptions import PargsMissingArgument, PargsUnkownArgument, PargsException


class BaseParser:
    """Base class for parsers implementing some functionality"""

    def __init__(self):
        self._params: List[Parameter] = list()
        self._values: Dict[str, Any] = dict()

    def __repr__(self) -> str:
        return f"BaseParser{self._params!r}"

    def param_taken(self, param: Parameter) -> bool:
        """test wether the parameter is already present"""
        return any([p == param for p in self._params])

    @abstractmethod
    def parse(self) -> Self:
        """resolve parameters"""
        ...

    def add_param(self, param: Parameter[Any]) -> Self:
        """add single param"""
        if self.param_taken(param):
            raise ValueError(f"Parameter already exists: {param}")
        self._params.append(param)
        return self

    def add_params(self, params: Sequence[Parameter[Any]]) -> Self:
        """add multiple params"""
        for p in params:
            self.add_param(p)
        return self

    def vars(self) -> Namespace:
        """return a namespace generated from the found values"""
        return Namespace(**{k: v for k, v in self._values.items()})

    def clear(self) -> Self:
        """clear the contents of the parser, effectively resetting it"""
        self._values.clear()
        self._params.clear()
        return self

    def help(self, prog: str = "") -> str:
        """
        Build a nicely formatted help/usage string from a list of parameters.
        """
        prog = prog or sys.argv[0]
        lines: list[str] = []
        lines.append("Usage:")
        lines.append(f"  {prog} [OPTIONS] [ARGS]")
        lines.append("\nOptions:")

        positionals: dict[int, str] = dict()
        for p in self._params:
            match p:
                case KwParam(short=short, long=long, help=help_text, default=default):
                    opt = []
                    if short:
                        opt.append(f"-{short}")
                    if long:
                        opt.append(f"--{long}")
                    opts = ", ".join(opt)
                    default_str = (
                        f" (default: {default})" if default is not None else ""
                    )
                    lines.append(f"  {opts} {help_text}{default_str}")

                case FlagParam(short=short, long=long, help=help_text, default=default):
                    opt = []
                    if short:
                        opt.append(f"-{short}")
                    if long:
                        opt.append(f"--{long}")
                    opts = ", ".join(opt)
                    default_str = f" [default: {'on' if default else 'off'}]"
                    lines.append(f"  {opts} {help_text}{default_str}")

                case PositionalParam(
                    target=target, help=help_text, default=default, position=position
                ):
                    default_str = (
                        f" (default: {default})" if default is not None else ""
                    )
                    positionals[position] = f"  {target} {help_text}{default_str}"
                    raise NotImplementedError(
                        "unable to correctly display order of positional params"
                    )

                case _:
                    lines.append(f"  {p.target:<15} {p.help}")

        return "\n".join(lines)


class CliParser(BaseParser):
    """parse cli arguments"""

    def __init__(self):
        super().__init__()
        self.buff: List[str] = sys.argv

    def parse(self) -> Self:
        """resolve parameters"""
        found_long: dict[str, int] = dict()
        found_short: dict[str, int] = dict()
        positional: dict[int, str] = dict()

        def _parse_single(param, idx) -> None:
            value = positional.get(idx + 1, None)
            try:
                self._values[param.target] = param.parse(value)
            except Exception as e:
                raise ValueError(
                    f"Exception occured when converting {param.target!r}; {idx=!r}; {e=!r}"
                )

        for i, item in enumerate(self.buff):
            match item:
                case str(s) if s.startswith("--") and len(s) > 2:
                    found_long[item[2:]] = i
                case str(s) if s.startswith("-") and len(s) == 2 and s[1] != "-":
                    found_short[s] = i
                case _:
                    positional[i] = item
        for param in self._params:
            match param:
                case KwParam(long=long, short=short):
                    if (arg := found_long.get(long, None)) is not None:
                        _parse_single(param, arg)
                    elif (arg := found_short.get(short, None)) is not None:
                        _parse_single(param, arg)
                    elif param.required:
                        raise PargsMissingArgument([param.target])
                case FlagParam(long=long, short=short):
                    if (arg := found_long.get(long, None)) is not None:
                        _parse_single(param, arg)
                    elif (arg := found_short.get(short, None)) is not None:
                        _parse_single(param, arg)
                    elif param.required:
                        raise PargsMissingArgument([param.target])
                case PositionalParam():
                    continue
                case _:
                    raise NotImplementedError(
                        "Other types of parameters are not supported"
                    )

        for param in [p for p in self._params if isinstance(p, PositionalParam)]:
            if param.position is not None:
                value = param.parse(positional.get(param.position))
                self._values[param.target] = value
                positional.pop(param.position)
        if len(positional) != 0:
            raise PargsUnkownArgument(list(positional.values()))
        return self


@runtime_checkable
class ArgParser(Protocol):
    """runtime checkable protocol for argument parsers"""

    def parse(self) -> Self: ...
    def add_param(self, param: Parameter) -> Self: ...
    def vars(self) -> Namespace: ...


class EnvParser(BaseParser):
    """parse environment using optional prefix for all arguments"""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix + "_" if prefix and prefix[-1] != "_" else ""
        super().__init__()

    def parse(self):
        """resolve parameters"""
        for param in self._params:
            env_key = self.prefix + param.target.upper().replace("-", "_")
            self._values[param.target] = param.parse(os.environ.get(env_key, None))
        return self


class FileParser(BaseParser):
    """base parser for file contents, could be extended for e.g. yaml"""

    def __init__(self, path: str):
        self.path: str = path
        super().__init__()


class JsonParser(FileParser):
    """parse a json file"""

    def parse(self, **kwargs) -> Self:
        """
        parse the specified file as json.
        A list at top level is parsed as
        positional arguments
        :kwargs -- forward to `json.load`
        """
        with open(self.path) as f:
            d = json.load(f, **kwargs)
        if isinstance(d, list):
            for p in self._params:
                match p:
                    case PositionalParam(target=target, position=pos):
                        if (pos := p.position) and len(d) > pos:
                            self._values[target] = p.parse(d[pos])
                        elif p.required:
                            raise PargsMissingArgument([p.target])
        elif isinstance(d, dict):
            for p in self._params:
                match p:
                    case PositionalParam(target=target):
                        raise PargsUnkownArgument([target])
                    case (
                        KwParam(target=target, long=long)
                        | FlagParam(target=target, long=long)
                    ):
                        self._values[target] = p.parse(
                            d.get(target, None) or d.get(long, None)
                        )
                    case Parameter(target=target):
                        self._values[target] = p.parse(d.get(target, None))
                    case _:
                        raise PargsUnkownArgument([p.target])

        return self


class TomlParser(FileParser):
    """parses a toml file, positional arguments are not allowed"""

    def add_param(self, param: Parameter) -> Self:
        if isinstance(param, PositionalParam):
            raise PargsUnkownArgument([param.target])
        return super().add_param(param)

    def parse(self, parse_float=float) -> Self:
        """
        parse the spefified file as toml.

        positional arguments
        :parse_float -- forward to `tomllib.load`
        """
        with open(self.path, "rb") as f:
            d = tomllib.load(f, parse_float=parse_float)
        for p in self._params:
            match p:
                case (
                    KwParam(target=target, long=long)
                    | FlagParam(target=target, long=long)
                ):
                    value = d.get(target, None) or d.get(long, None)
                    self._values[p.target] = p.parse(value)
                case Parameter(target=target):
                    self._values[target] = d.get(target, None)
                case _:
                    raise PargsUnkownArgument([p.target])

        return self


class MultiParser(BaseParser):
    """glue to add multiple sources for configuration together"""

    def __init__(self, parsers: Dict[int, ArgParser] = {}):
        super().__init__()
        self.parsers: Dict[int, ArgParser] = parsers
        self.ns: Namespace = Namespace()
        self.max = max(parsers.keys()) if parsers else 0

    def add_parser(self, parser: ArgParser, priority: int = -1) -> Self:
        """add parser as source for config, priority defaults to next available value"""
        if priority < 0:
            self.parsers[self.max] = parser
            self.max += 1
        elif old := self.parsers.get(priority):
            raise PargsException(
                f"Parser with priority {priority} already exists ({old.__class__.__name__})"
            )
        else:
            self.parsers[priority] = parser
            if priority > self.max:
                self.max = priority + 1

        return self

    def parse(self) -> Self:
        for _, parser in sorted(
            self.parsers.items(), key=lambda pp: pp[0], reverse=True
        ):
            for p in self._params:
                parser.add_param(p)
            self.ns |= parser.parse().vars()
        return self

    def vars(self) -> Namespace:
        return self.ns
