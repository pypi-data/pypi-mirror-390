"""Experiment complete job logics."""

from __future__ import annotations

import logging
import shutil
import time
from itertools import chain
from typing import TYPE_CHECKING, Self

import rich.progress as rich_prog

import slurmbench.samples.items as smp
import slurmbench.samples.slurm.status as smp_slurm_status
import slurmbench.samples.status as smp_status
import slurmbench.slurm.bash as slurm_bash
from slurmbench import root_logging

from . import errors as exp_errors
from . import file_system as exp_fs
from . import history, monitors
from . import managers as exp_managers
from .bash import items as exp_bash_items
from .slurm import checks as exp_slurm_checks
from .slurm import status as exp_slurm_status

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from slurmbench.slurm import sacct

_LOGGER = logging.getLogger(__name__)


def resolve_running_samples(
    exp_manager: exp_managers.OnlyOptions | exp_managers.WithArguments,
    unresolved_samples: list[smp.RowNumbered],
    array_job_id: str,
) -> None:
    """Complete experiment."""
    _finished_job_deamon(exp_manager.fs_managers(), unresolved_samples, array_job_id)
    conclude_experiment(exp_manager)


def _finished_job_deamon(
    exp_fs_manager: exp_fs.Managers,
    unresolved_samples: list[smp.RowNumbered],
    array_job_id: str,
) -> None:
    """Run finished job deamon."""
    in_running_job_ids = _running_job_ids(array_job_id, unresolved_samples)

    with rich_prog.Progress(console=root_logging.CONSOLE) as progress:
        slurm_running_task = progress.add_task(
            "Slurm running",
            total=len(in_running_job_ids),
        )

        while in_running_job_ids:
            time.sleep(10)

            _tmp_in_running_job_ids, resolved_samples = _get_resolved_samples(
                exp_fs_manager,
                in_running_job_ids,
            )

            _manage_resolved_samples(resolved_samples, exp_fs_manager)

            progress.update(
                slurm_running_task,
                advance=(len(in_running_job_ids) - len(_tmp_in_running_job_ids)),
            )
            in_running_job_ids = _tmp_in_running_job_ids


def _get_resolved_samples(
    exp_fs_managers: exp_fs.Managers,
    running_samples: list[RunningSample],
) -> tuple[list[RunningSample], ResolvedSamples]:
    """Get resolved samples."""
    _tmp_in_running_job_ids: list[RunningSample] = []
    resolved_samples = ResolvedSamples.new()

    for running_sample in running_samples:
        job_status = JobStatus.from_job_id(
            exp_fs_managers.work(),
            running_sample,
        )
        match job_status.sample_status():
            case smp_status.Success.OK:
                resolved_samples.ok_samples().append(
                    ResolvedSample(
                        running_sample,
                        job_status,
                    ),
                )
            case smp_status.Error.ERROR:
                resolved_samples.error_samples().append(
                    ResolvedSample(
                        running_sample,
                        job_status,
                    ),
                )
            case smp_status.Error.NOT_RUN:
                _tmp_in_running_job_ids.append(running_sample)

    return _tmp_in_running_job_ids, resolved_samples


class RunningSample:
    """Running sample."""

    @classmethod
    def from_array_job_id(
        cls,
        array_job_id: str,
        row_numbered_item: smp.RowNumbered,
    ) -> Self:
        """Get running job ID from array job ID and row numbered item."""
        return cls(
            slurm_bash.array_task_job_id(
                array_job_id,
                str(row_numbered_item.to_base_one()),
            ),
            row_numbered_item,
        )

    def __init__(self, job_id: str, row_numbered_item: smp.RowNumbered) -> None:
        self.__job_id = job_id
        self.__row_numbered_item = row_numbered_item

    def job_id(self) -> str:
        """Get job id."""
        return self.__job_id

    def row_numbered_item(self) -> smp.RowNumbered:
        """Get row numbered item."""
        return self.__row_numbered_item


def _running_job_ids(
    array_job_id: str,
    unresolved_samples: list[smp.RowNumbered],
) -> list[RunningSample]:
    """Get the list of running job IDs."""
    return [
        RunningSample.from_array_job_id(array_job_id, running_sample)
        for running_sample in unresolved_samples
    ]


class ResolvedSample:
    """Resolved sample."""

    def __init__(
        self,
        running_sample: RunningSample,
        job_status: JobStatus,
    ) -> None:
        self.__running_job_id = running_sample
        self.__job_status = job_status

    def running_sample(self) -> RunningSample:
        """Get running job ID."""
        return self.__running_job_id

    def job_status(self) -> JobStatus:
        """Get job status."""
        return self.__job_status


class JobStatus:
    """Job status."""

    @classmethod
    def from_job_id(
        cls,
        work_exp_fs_manager: exp_fs.WorkManager,
        running_sample: RunningSample,
    ) -> Self:
        """Get sample experiment status from job id."""
        sacct_state = slurm_bash.get_state(running_sample.job_id())

        if sacct_state is not None:
            return cls(smp_status.from_sacct_state(sacct_state), sacct_state)
        #
        # Unknown sacct state
        #
        # The command job terminated with a success
        if (
            work_exp_fs_manager.slurm_log_fs_manager()
            .script_step_status_file(
                running_sample.job_id(),
                exp_bash_items.Steps.COMMAND,
                exp_slurm_status.ScriptSteps.OK,
            )
            .exists()
        ):
            # REFACTOR move to a work check function
            return cls(smp_status.Success.OK, None)
        # The job did not terminate or with an error
        return cls(smp_status.Error.ERROR, None)

    def __init__(
        self,
        status: smp_status.Status,
        sacct_state: sacct.State | None,
    ) -> None:
        self.__status = status
        self.__sacct_state = sacct_state

    def sample_status(self) -> smp_status.Status:
        """Get status."""
        return self.__status

    def sacct_state(self) -> sacct.State | None:
        """Get sacct state."""
        return self.__sacct_state


class ResolvedSamples:
    """Resolved samples."""

    @classmethod
    def new(cls) -> Self:
        """Get new resolved samples."""
        return cls([], [])

    def __init__(
        self,
        ok_samples: Iterable[ResolvedSample],
        error_samples: Iterable[ResolvedSample],
    ) -> None:
        self.__ok_samples = list(ok_samples)
        self.__error_samples = list(error_samples)

    def ok_samples(self) -> list[ResolvedSample]:
        """Get ok samples."""
        return self.__ok_samples

    def error_samples(self) -> list[ResolvedSample]:
        """Get error samples."""
        return self.__error_samples

    def __iter__(self) -> Iterator[ResolvedSample]:
        """Get iterator."""
        return chain(self.__ok_samples, self.__error_samples)


def _manage_resolved_samples(
    resolved_samples: ResolvedSamples,
    exp_fs_managers: exp_fs.Managers,
) -> None:
    _manage_finished_ok_samples(resolved_samples, exp_fs_managers.work())
    _manage_finished_error_jobs(resolved_samples, exp_fs_managers)

    for resolved_job in resolved_samples:
        _move_slurm_logs_to_work_sample_dir(resolved_job, exp_fs_managers.work())
        _move_work_sample_dir_to_data_dir(resolved_job, exp_fs_managers)

    monitors.update_samples_resolution_status(
        exp_fs_managers.work(),
        (
            (
                resolved_sample.running_sample().row_numbered_item(),
                resolved_sample.job_status().sample_status(),
            )
            for resolved_sample in resolved_samples
        ),
    )


def _manage_finished_ok_samples(
    resolved_samples: ResolvedSamples,
    work_exp_fs_manager: exp_fs.WorkManager,
) -> None:
    for resolved_job_id in resolved_samples.ok_samples():
        slurm_stdout = work_exp_fs_manager.slurm_log_fs_manager().stdout(
            resolved_job_id.running_sample().job_id(),
        )
        sample_fs_manager = work_exp_fs_manager.sample_fs_manager(
            resolved_job_id.running_sample().row_numbered_item(),
        )
        sample_fs_manager.sample_dir().mkdir(parents=True, exist_ok=True)
        shutil.copy(slurm_stdout, sample_fs_manager.done_log())


def _manage_finished_error_jobs(
    resolved_samples: ResolvedSamples,
    exp_fs_managers: exp_fs.Managers,
) -> None:
    for failed_sample in resolved_samples.error_samples():
        slurm_stderr = (
            exp_fs_managers.work()
            .slurm_log_fs_manager()
            .stderr(failed_sample.running_sample().job_id())
        )
        sample_fs_manager = exp_fs_managers.work().sample_fs_manager(
            failed_sample.running_sample().row_numbered_item(),
        )
        sample_fs_manager.sample_dir().mkdir(parents=True, exist_ok=True)
        shutil.copy(slurm_stderr, sample_fs_manager.errors_log())

    if resolved_samples.error_samples():
        exp_errors.write_errors(
            exp_fs_managers.data(),
            (
                error_job_id.running_sample().row_numbered_item()
                for error_job_id in resolved_samples.error_samples()
            ),
        )


def _move_slurm_logs_to_work_sample_dir(
    resolved_sample: ResolvedSample,
    work_exp_fs_manager: exp_fs.WorkManager,
) -> None:
    sample_fs_manager = work_exp_fs_manager.sample_fs_manager(
        resolved_sample.running_sample().row_numbered_item(),
    )
    smp_slurm_fs_manager = sample_fs_manager.slurm_fs_manager()

    smp_slurm_fs_manager.slurm_dir().mkdir(parents=True, exist_ok=True)

    sacct_state = resolved_sample.job_status().sacct_state()
    if sacct_state is not None:
        smp_slurm_fs_manager.job_state_file_builder().path(sacct_state).touch()

    slurm_bash.write_slurm_stats(
        resolved_sample.running_sample().job_id(),
        smp_slurm_fs_manager.stats_psv(),
    )

    slurm_stdout = work_exp_fs_manager.slurm_log_fs_manager().stdout(
        resolved_sample.running_sample().job_id(),
    )
    shutil.copy(slurm_stdout, smp_slurm_fs_manager.stdout_log())

    slurm_stderr = work_exp_fs_manager.slurm_log_fs_manager().stderr(
        resolved_sample.running_sample().job_id(),
    )
    shutil.copy(slurm_stderr, smp_slurm_fs_manager.stderr_log())

    _command_steps_process_from_slurm_logs(
        work_exp_fs_manager,
        resolved_sample,
    ).to_yaml(
        smp_slurm_fs_manager.command_steps_status_file_manager().path(),
    )


def _command_steps_process_from_slurm_logs(
    work_exp_fs_manager: exp_fs.WorkManager,
    resolved_sample: ResolvedSample,
) -> smp_slurm_status.CommandStepsProcess:
    return smp_slurm_status.CommandStepsProcess(
        exp_slurm_checks.script_step_status(
            work_exp_fs_manager,
            resolved_sample.running_sample().job_id(),
            exp_bash_items.Steps.INIT_ENV,
        ),
        exp_slurm_checks.script_step_status(
            work_exp_fs_manager,
            resolved_sample.running_sample().job_id(),
            exp_bash_items.Steps.COMMAND,
        ),
        exp_slurm_checks.script_step_status(
            work_exp_fs_manager,
            resolved_sample.running_sample().job_id(),
            exp_bash_items.Steps.CLOSE_ENV,
        ),
    )


def _move_work_sample_dir_to_data_dir(
    resolved_sample: ResolvedSample,
    exp_fs_managers: exp_fs.Managers,
) -> None:
    work_sample_fs_manager = exp_fs_managers.work().sample_fs_manager(
        resolved_sample.running_sample().row_numbered_item(),
    )
    data_sample_fs_manager = exp_fs_managers.data().sample_fs_manager(
        resolved_sample.running_sample().row_numbered_item(),
    )
    shutil.rmtree(data_sample_fs_manager.sample_dir(), ignore_errors=True)
    shutil.copytree(
        work_sample_fs_manager.sample_dir(),
        data_sample_fs_manager.sample_dir(),
    )
    shutil.rmtree(work_sample_fs_manager.sample_dir(), ignore_errors=True)


def conclude_experiment(
    exp_manager: exp_managers.OnlyOptions | exp_managers.WithArguments,
) -> None:
    """Conclude the experiment."""
    event = history.update_history(exp_manager.fs_managers())
    _LOGGER.info("Experiment `%s` finished", exp_manager.exp_name())
    _LOGGER.info(
        (
            "Experiment stats:\n"
            "* Total number of samples: %d\n"
            "* Number of successful samples: %d\n"
            "* Number of samples with missing inputs: %d\n"
            "* Number of failed samples: %d\n"
            "* Number of not run samples: %d\n"
        ),
        event.stats().total_number_of_samples(),
        event.stats().number_of_successful_samples(),
        event.stats().number_of_samples_with_missing_inputs(),
        event.stats().number_of_failed_samples(),
        event.stats().number_of_not_run_samples(),
    )
    exp_manager.fs_managers().data().in_progress_yaml().unlink()
    _clean_work_directory(exp_manager.fs_managers().work())


def _clean_work_directory(work_exp_fs_manager: exp_fs.WorkManager) -> None:
    """Move work to data."""
    _LOGGER.info("Cleaning work directory")
    shutil.rmtree(work_exp_fs_manager.exp_dir(), ignore_errors=True)
    #
    # Try to remove empty parent directories
    #
    tree_to_remove = [
        work_exp_fs_manager.root_dir(),
        work_exp_fs_manager.topic_dir(),
        work_exp_fs_manager.tool_dir(),
    ]
    last_empty = True
    while tree_to_remove and last_empty:
        dir_to_remove = tree_to_remove.pop()
        if not any(dir_to_remove.iterdir()):
            dir_to_remove.rmdir()
        else:
            last_empty = False
