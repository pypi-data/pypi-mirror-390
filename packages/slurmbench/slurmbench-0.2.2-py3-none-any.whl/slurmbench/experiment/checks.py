"""Experiment checking module."""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import TYPE_CHECKING, overload

import slurmbench.tool.config as tool_cfg
import slurmbench.tool.connector as tool_connector

from . import file_system as exp_fs
from . import managers as exp_managers

if TYPE_CHECKING:
    from pathlib import Path


_LOGGER = logging.getLogger(__name__)


class RunOK[M: (exp_managers.OnlyOptions, exp_managers.WithArguments)]:
    """OK status."""

    def __init__(self, exp_manager: M) -> None:
        self._exp_manager: M = exp_manager

    def exp_manager(self) -> M:
        """Get experiment manager."""
        return self._exp_manager


class RunErrors(StrEnum):
    """Experiment checks error status before run."""

    NO_PERMISSION = "no_permission"
    READ_CONFIG_FAILED = "read_config_failed"
    MISSING_TOOL_ENV_WRAPPER_SCRIPT = "missing_tool_env_wrapper_script"


@overload
def check_before_start(
    exp_name: str,
    data_dir: Path,
    work_dir: Path,
    tool_connector_type: type[tool_connector.OnlyOptions],
) -> RunOK[exp_managers.OnlyOptions] | RunErrors: ...
@overload
def check_before_start(
    exp_name: str,
    data_dir: Path,
    work_dir: Path,
    tool_connector_type: type[tool_connector.WithArguments],
) -> RunOK[exp_managers.WithArguments] | RunErrors: ...
def check_before_start[
    C: (tool_connector.OnlyOptions, tool_connector.WithArguments),
](
    exp_name: str,
    data_dir: Path,
    work_dir: Path,
    tool_connector_type: type[C],
) -> RunOK[exp_managers.OnlyOptions] | RunOK[exp_managers.WithArguments] | RunErrors:
    """Check experiment."""
    match _check_read_write_access(data_dir, work_dir):
        case PermissionErrors():
            return RunErrors.NO_PERMISSION

    exp_fs_managers = exp_fs.Managers.new(
        data_dir,
        work_dir,
        tool_connector_type.description(),
        exp_name,
    )

    match connector_or_err := instantiate_connector(
        tool_connector_type,
        exp_fs_managers.data().config_yaml(),
    ):
        case RunErrors():
            return connector_or_err
        case tool_connector.OnlyOptions():
            exp_manager = exp_managers.OnlyOptions(
                exp_fs_managers,
                connector_or_err,
            )
        case tool_connector.WithArguments():
            exp_manager = exp_managers.WithArguments(
                exp_fs_managers,
                connector_or_err,
            )

    _LOGGER.debug(
        "Experiment config:\n%s",
        exp_manager.tool_connector().to_config().to_yaml_dump(),
    )

    if _missing_env_wrapper_script(exp_manager.fs_managers().data()):
        return RunErrors.MISSING_TOOL_ENV_WRAPPER_SCRIPT

    return RunOK(exp_manager)


class PermissionOK(StrEnum):
    """Permission OK status."""

    READ_WRITE = "read_write"


class PermissionErrors(StrEnum):
    """Permission status."""

    NO_READ_ACCESS = "no_read_access"
    NO_WRITE_ACCESS = "no_write_access"


type PermissionStatus = PermissionOK | PermissionErrors


def _check_read_write_access(data_dir: Path, work_dir: Path) -> PermissionStatus:
    """Check read and write access."""
    match status := _check_read_write_access_data(data_dir):
        case PermissionErrors():
            return status

    match status := _check_read_write_access_work(work_dir):
        case PermissionErrors():
            return status

    return PermissionOK.READ_WRITE


def _check_read_write_access_data(data_dir: Path) -> PermissionStatus:
    """Check read and write access."""
    if not data_dir.exists():
        _LOGGER.critical("Data directory %s does not exist", data_dir)
        return PermissionErrors.NO_READ_ACCESS

    file_test = data_dir / "test_read_write.txt"
    try:
        file_test.write_text("test")
    except OSError as err:
        _LOGGER.critical("No write access to %s with exception: %s", data_dir, err)
        return PermissionErrors.NO_WRITE_ACCESS

    try:
        file_test.read_text()
    except OSError as err:
        _LOGGER.critical("No read access to %s with exception: %s", data_dir, err)
        file_test.unlink()
        return PermissionErrors.NO_READ_ACCESS

    file_test.unlink()

    return PermissionOK.READ_WRITE


def _check_read_write_access_work(work_dir: Path) -> PermissionStatus:
    """Check read and write access."""
    try:
        work_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        _LOGGER.exception("No write access to %s", work_dir)
        return PermissionErrors.NO_WRITE_ACCESS
    file_test = work_dir / "test_read_write.txt"

    try:
        file_test.write_text("test")
    except OSError:
        _LOGGER.exception("No write access to %s", work_dir)
        file_test.unlink(missing_ok=True)
        if not any(work_dir.iterdir()):
            work_dir.rmdir()
        return PermissionErrors.NO_WRITE_ACCESS

    try:
        file_test.read_text()
    except OSError:
        _LOGGER.exception("No read access to %s", work_dir)
        file_test.unlink()
        if not any(work_dir.iterdir()):
            work_dir.rmdir()
        return PermissionErrors.NO_READ_ACCESS

    file_test.unlink()
    if not any(work_dir.iterdir()):
        work_dir.rmdir()

    return PermissionOK.READ_WRITE


# REFACTOR common function so use common ERROR
def instantiate_connector[
    C: (tool_connector.OnlyOptions, tool_connector.WithArguments),
](
    tool_connector_type: type[C],
    tool_config_yaml: Path,
) -> C | RunErrors:
    """Instantiate connector."""
    if issubclass(tool_connector_type, tool_connector.OnlyOptions):
        return tool_connector_type.from_config(
            tool_cfg.OnlyOptions.from_yaml(tool_config_yaml),
        )
    match connector_or_error := tool_connector_type.from_config(
        tool_cfg.WithArguments.from_yaml(tool_config_yaml),
    ):
        case tool_connector.ArgParsingError():
            _LOGGER.critical(
                "Invalid tool name `%s` for argument name `%s`."
                " Choose among the valid tools in : {%s}",
                connector_or_error.error().invalid_tool_name(),
                connector_or_error.arg_name(),
                ", ".join(connector_or_error.error().expected_tool_names()),
            )
            return RunErrors.READ_CONFIG_FAILED
        case tool_connector.MissingArgumentNameError():
            _LOGGER.critical(
                "Argument name not found: `%s`."
                " All the argument names must be present: {%s}",
                connector_or_error.missing_arg_name(),
                ", ".join(str(name) for name in connector_or_error.required_names()),
            )
            return RunErrors.READ_CONFIG_FAILED
        case tool_connector.ExtraArgumentNameError():
            _LOGGER.critical(
                "Extra argument name: `%s`."
                " Only argument names in the following set must be present: {%s}",
                connector_or_error.extra_arg_names(),
                ", ".join(str(name) for name in connector_or_error.expected_names()),
            )
            return RunErrors.READ_CONFIG_FAILED
    return connector_or_error


def _missing_env_wrapper_script(data_exp_fs_manager: exp_fs.DataManager) -> bool:
    """Check missing env wrapper script."""
    if not data_exp_fs_manager.tool_env_script_sh().exists():
        _LOGGER.critical("Missing tool environment wrapper script")
        _LOGGER.info("You can use `draft-env` command to generate a draft script")
        return True
    return False


class SameExperimentConfigs(StrEnum):
    """Same experiment configs OK status."""

    SAME = "same"


class DifferentExperimentConfigs(StrEnum):
    """Different experiment configs error."""

    DIFFERENT_SYNTAX = "different_syntax"
    NOT_SAME = "not_same"


type ExperimentConfigComparison = SameExperimentConfigs | DifferentExperimentConfigs


def compare_config_vs_config_in_data[
    C: (tool_connector.OnlyOptions, tool_connector.WithArguments),
](
    connector: C,
    config_in_data_yaml: Path,
) -> ExperimentConfigComparison:
    """Compare two experimentation configs."""
    match connector_in_data := connector.from_config(
        connector.config_type().from_yaml(config_in_data_yaml),
    ):
        case (
            tool_connector.ArgParsingError()
            | tool_connector.MissingArgumentNameError()
            | tool_connector.ExtraArgumentNameError()
        ):
            return DifferentExperimentConfigs.DIFFERENT_SYNTAX

    is_same = connector.is_same(connector_in_data)

    if not is_same:
        _LOGGER.critical(
            "Existing and given experiment configurations are not the same",
        )
        return DifferentExperimentConfigs.NOT_SAME

    return SameExperimentConfigs.SAME
