"""Tool connector module."""

from __future__ import annotations

import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Self, final

import slurmbench.experiment.file_system as exp_fs
import slurmbench.topic.results as topic_res
import slurmbench.topic.visitor as topic_visitor

from . import bash, results
from . import config as cfg
from . import description as desc

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_LOGGER = logging.getLogger(__name__)


class Arg[T: topic_visitor.Tools, R: results.Result](ABC):
    """Tool argument configuration."""

    @classmethod
    def config_type(cls) -> type[cfg.Arg]:
        """Get config type."""
        return cfg.Arg

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get name."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def tools_type(cls) -> type[T]:
        """Get tools type."""
        raise NotImplementedError

    @classmethod
    def valid_tools(cls) -> Iterable[T]:
        """Get valid tools."""
        return (
            tool
            for tool in cls.tools_type()
            if cls.result_visitor().tool_gives_the_result(tool)
        )

    @classmethod
    @abstractmethod
    def result_visitor(cls) -> type[topic_res.Visitor[T, R]]:
        """Get result visitor function."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def sh_lines_builder_type(cls) -> type[bash.Argument[R]]:
        """Get shell lines builder."""
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: cfg.Arg) -> Self | InvalidToolNameError:
        """Convert dict to object."""
        try:
            tool = cls.tools_type()(config.tool_name())
        except ValueError:
            return InvalidToolNameError(
                config.tool_name(),
                (str(tool) for tool in cls.valid_tools()),
            )
        match cls.result_visitor().result_builder_from_tool(tool):
            case topic_res.Error():
                return InvalidToolNameError(
                    config.tool_name(),
                    (str(tool) for tool in cls.valid_tools()),
                )
        return cls(tool, config.exp_name())

    def __init__(self, tool: T, exp_name: str) -> None:
        """Initialize."""
        self._tool = tool
        self._exp_name = exp_name

    def tool(self) -> T:
        """Get tool."""
        return self._tool

    def exp_name(self) -> str:
        """Get experiment name."""
        return self._exp_name

    def result(self, data_exp_fs_manager: exp_fs.DataManager) -> R:
        """Convert argument to input."""
        return self.result_visitor().result_builder()(
            exp_fs.WorkManager(
                data_exp_fs_manager.root_dir(),
                self._tool.to_description(),
                self._exp_name,
            ),
        )

    def sh_lines_builder(self, exp_fs_managers: exp_fs.Managers) -> bash.Argument[R]:
        """Convert input to shell lines builder."""
        return self.sh_lines_builder_type()(
            self.result(exp_fs_managers.data()),
            exp_fs_managers.work(),
        )

    def to_config(self) -> cfg.Arg:
        """Convert to config."""
        return cfg.Arg(str(self._tool), self._exp_name)


class InvalidToolNameError(Exception):
    """Invalid tool name error."""

    def __init__(
        self,
        invalid_tool_name: str,
        expected_tool_names: Iterable[str],
    ) -> None:
        self._invalid_tool_name = invalid_tool_name
        self._expected_tool_names = tuple(expected_tool_names)

    def invalid_tool_name(self) -> str:
        """Get invalid tool name."""
        return self._invalid_tool_name

    def expected_tool_names(self) -> tuple[str, ...]:
        """Get expected tool names."""
        return self._expected_tool_names


class ArgParsingError(Exception):
    """Argument parsing error."""

    def __init__(self, arg_name: str, error: InvalidToolNameError) -> None:
        self._arg_name = arg_name
        self._error = error

    def arg_name(self) -> str:
        """Get argument name."""
        return self._arg_name

    def error(self) -> InvalidToolNameError:
        """Get error."""
        return self._error


class MissingArgumentNameError(Exception):
    """Missing argument name error."""

    def __init__(self, missing_arg_name: str, required_names: Iterable[str]) -> None:
        self._missing_arg_name = missing_arg_name
        self._required_names = tuple(required_names)

    def missing_arg_name(self) -> str:
        """Get missing argument name."""
        return self._missing_arg_name

    def required_names(self) -> tuple[str, ...]:
        """Get list or required names."""
        return self._required_names


class ExtraArgumentNameError(Exception):
    """Extra argument name error."""

    def __init__(
        self,
        extra_arg_names: Iterable[str],
        expected_names: Iterable[str],
    ) -> None:
        self._extra_arg_names = tuple(extra_arg_names)
        self._expected_names = tuple(expected_names)

    def extra_arg_names(self) -> tuple[str, ...]:
        """Get extra argument name."""
        return self._extra_arg_names

    def expected_names(self) -> tuple[str, ...]:
        """Get names type."""
        return self._expected_names


ArgsLoadError = ArgParsingError | MissingArgumentNameError | ExtraArgumentNameError


class NoArgInArgumentsError[A: Arg](Exception):
    """No argument in arguments error."""

    def __init__(
        self,
        query_type: type[A],
        expected_types: Iterable[type[Arg]],
    ) -> None:
        self._query_type = query_type
        self._expected_types = tuple(expected_types)

    def query_type(self) -> type[A]:
        """Get query type."""
        return self._query_type

    def expected_types(self) -> tuple[type[Arg], ...]:
        """Get expected types."""
        return self._expected_types


class NamedResult:
    """Named result."""

    @classmethod
    def from_arg(cls, arg: Arg, data_exp_fs_manager: exp_fs.DataManager) -> Self:
        """Convert argument to named result."""
        return cls(arg.name(), arg.result(data_exp_fs_manager))

    def __init__(self, name: str, result: results.Result) -> None:
        self._name = name
        self._result = result

    def name(self) -> str:
        """Get name."""
        return self._name

    def result(self) -> results.Result:
        """Get result."""
        return self._result


class Arguments(ABC):
    """Tool arguments configuration."""

    @classmethod
    def config_type(cls) -> type[cfg.Arguments]:
        """Get config type."""
        return cfg.Arguments

    @classmethod
    @abstractmethod
    def arg_types(cls) -> list[type[Arg]]:
        """Get argument types."""
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: cfg.Arguments) -> Self | ArgsLoadError:
        """Convert dict to object."""
        name_to_arg: dict[str, Arg] = {}
        for arg_type in cls.arg_types():
            try:
                arg_config = config[arg_type.name()]
            except KeyError:
                return MissingArgumentNameError(
                    arg_type.name(),
                    (at.name() for at in cls.arg_types()),
                )

            match arg_or_err := arg_type.from_config(arg_config):
                case Arg():
                    name_to_arg[arg_type.name()] = arg_or_err
                case InvalidToolNameError():
                    return ArgParsingError(arg_type.name(), arg_or_err)

        if extra_arg := set(config.arguments().keys()) - set(name_to_arg):
            return ExtraArgumentNameError(extra_arg, set(name_to_arg))

        return cls(name_to_arg)

    def __init__(self, arguments: dict[str, Arg]) -> None:
        self.__arguments = arguments

    def __getitem__(self, name: str) -> Arg:
        """Get argument."""
        return self.__arguments[name]

    def __iter__(self) -> Iterator[Arg[topic_visitor.Tools, results.Result]]:
        """Iterate arguments."""
        return iter(self.__arguments.values())

    def get_arg[A: Arg](self, arg_type: type[A]) -> A | NoArgInArgumentsError[A]:
        """Get argument."""
        if arg_type.name() not in self.__arguments:
            return NoArgInArgumentsError(arg_type, self.arg_types())
        a = self.__arguments[arg_type.name()]
        if isinstance(a, arg_type):
            return a
        return NoArgInArgumentsError(arg_type, self.arg_types())

    def named_results(
        self,
        data_exp_fs_manager: exp_fs.DataManager,
    ) -> Iterator[NamedResult]:
        """Iterate over results associated with the arguments."""
        yield from (NamedResult.from_arg(arg, data_exp_fs_manager) for arg in self)

    def sh_lines_builders(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> Iterator[bash.Argument]:
        """Convert to commands."""
        return (
            arg.sh_lines_builder(exp_fs_managers) for arg in self.__arguments.values()
        )

    def to_config(self) -> cfg.Arguments:
        """Convert to config."""
        return cfg.Arguments(
            {str(name): arg.to_config() for name, arg in self.__arguments.items()},
        )


@final
class StringOpts:
    """String options.

    When the options are regular short/long options.
    """

    @classmethod
    def from_config(cls, config: cfg.StringOpts) -> Self:
        """Convert dict to object."""
        return cls(config)

    def __init__(self, options: Iterable[str]) -> None:
        self.__options = list(options)

    def __bool__(self) -> bool:
        """Check if options are not empty."""
        return len(self.__options) > 0

    def __len__(self) -> int:
        """Get options length."""
        return len(self.__options)

    def __iter__(self) -> Iterator[str]:
        """Iterate options."""
        return iter(self.__options)

    def sh_lines_builder(self) -> bash.Options:
        """Get shell lines builder type."""
        return bash.Options(self)

    def to_config(self) -> cfg.StringOpts:
        """Convert to config."""
        return cfg.StringOpts(self.__options)


class WithOptions[C: cfg.WithOptions, E](ABC):
    """Tool config with options."""

    @classmethod
    @abstractmethod
    def description(cls) -> desc.Description:
        """Get tool description."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def config_type(cls) -> type[C]:
        """Get config type."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_config(cls, config: C) -> Self | E:
        """Convert dict to object."""
        raise NotImplementedError

    def __init__(self, options: StringOpts) -> None:
        """Initialize."""
        self._options = options

    def options(self) -> StringOpts:
        """Get options."""
        return self._options

    @abstractmethod
    def to_config(self) -> cfg.WithOptions:
        """Convert to config."""
        raise NotImplementedError

    @abstractmethod
    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.WithOptions:
        """Get sh commands."""
        raise NotImplementedError

    def is_same(self, other: Self) -> bool:
        """Check if configs are the same."""
        return self.to_config().is_same(other.to_config())

    @classmethod
    def parent_dir_where_defined(cls) -> Path:
        """Get the parent directory of the module defining the connector.

        Usefull to retrieve the tool template bash script.
        """
        cls_mod = inspect.getmodule(cls)
        match cls_mod:
            case None:
                _LOGGER.critical("No module for %s", cls)
                raise ValueError
        if cls_mod.__file__ is None:
            _LOGGER.critical("No file for %s", cls)
            raise ValueError
        return Path(cls_mod.__file__).parent


class OnlyOptions(WithOptions[cfg.OnlyOptions, "OnlyOptions"]):
    """Tool config without arguments."""

    @classmethod
    def config_type(cls) -> type[cfg.OnlyOptions]:
        """Get config type."""
        return cfg.OnlyOptions

    @classmethod
    def from_config(cls, config: cfg.OnlyOptions) -> Self:
        """Convert dict to object."""
        return cls(StringOpts.from_config(config.options()))

    @classmethod
    def commands_type(cls) -> type[bash.OnlyOptions]:
        """Get commands type."""
        # DOCU user can change CommandsOnlyOptions
        return bash.OnlyOptions

    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.OnlyOptions:
        """Get sh commands."""
        return self.commands_type()(
            bash.Options(self._options),
            exp_fs_managers,
            self.parent_dir_where_defined(),
        )

    def to_config(self) -> cfg.OnlyOptions:
        """Convert to dict."""
        return cfg.OnlyOptions(self._options.to_config())


class WithArguments[Args: Arguments](WithOptions[cfg.WithArguments, ArgsLoadError]):
    """Tool config with arguments."""

    @classmethod
    @abstractmethod
    def arguments_type(cls) -> type[Args]:
        """Get argument arguments type."""
        raise NotImplementedError

    @classmethod
    def config_type(cls) -> type[cfg.WithArguments]:
        """Get config type."""
        return cfg.WithArguments

    @classmethod
    def from_config(cls, config: cfg.WithArguments) -> Self | ArgsLoadError:
        """Convert dict to object."""
        match args_or_err := cls.arguments_type().from_config(config.arguments()):
            case (
                ArgParsingError()
                | MissingArgumentNameError()
                | ExtraArgumentNameError()
            ):
                return args_or_err
            case _:
                return cls(args_or_err, StringOpts.from_config(config.options()))

    def __init__(self, arguments: Args, options: StringOpts) -> None:
        """Initialize."""
        super().__init__(options)
        self._arguments = arguments

    def arguments(self) -> Arguments:
        """Get arguments."""
        return self._arguments

    def sh_commands(
        self,
        exp_fs_managers: exp_fs.Managers,
    ) -> bash.WithArguments:
        """Get sh commands."""
        return bash.WithArguments(
            self._arguments.sh_lines_builders(exp_fs_managers),
            self.options().sh_lines_builder(),
            exp_fs_managers,
            self.parent_dir_where_defined(),
        )

    def to_config(self) -> cfg.WithArguments:
        """Convert to dict."""
        return cfg.WithArguments(
            self._arguments.to_config(),
            self._options.to_config(),
        )
