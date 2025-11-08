# -*- coding: utf-8 -*-
import os
import asyncio
import logging
from starlette.datastructures import State
from eastwind.lib.util import import_module
from eastwind.lib.background import Scheduler
from eastwind.core.project import Project, start_project, stop_project, iterate_all_modules

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-10s: %(message)s",
)
logger = logging.getLogger("surge")


def collect_background_tasks(state: State, scheduler: Scheduler) -> None:
    # Iterate all the modules, gather the background tasks.
    for module_name, module_prefix in iterate_all_modules(state):
        # Collect the background declaration module.
        background_module = import_module(f"{module_prefix}.background")
        if background_module is None:
            continue
        # Add all the task declared in the "TASK" list to scheduler.
        if hasattr(background_module, "TASK") and isinstance(background_module.TASK, list):
            # Loop and fetch the task.
            for workload, trigger in background_module.TASK:
                # Add job to scheduler.
                scheduler.add_task(workload, trigger)


async def launch(scheduler: Scheduler) -> None:
    # Hold and wait for system shutdown.
    try:
        # Run the scheduler
        scheduler.start()
        # Keep and hold for scheduler to run the process.
        while True:
            # Sleep for 30min, and then awaken for the next time.
            await asyncio.sleep(1800)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


def main() -> None:
    # Increase the APScheduler logging level.
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    # Print the background task information.
    logger.info(f"Started background process [{os.getpid()}]")
    project: Project = start_project()
    state: State = State(project)
    # Prepare a scheduler for the local timezone.
    scheduler = Scheduler(state.config.timezone, state)
    # Collect all the background tasks from modules.
    collect_background_tasks(state, scheduler)
    logger.info(f"{scheduler.total_tasks()} tasks collected.")
    # Launch the scheduler.
    asyncio.run(launch(scheduler))
    logger.info("Waiting for project shutting down.")
    asyncio.run(stop_project(project))
    # Background task finished.
    logger.info(f"Finished background process [{os.getpid()}]")


if __name__ == "__main__":
    main()
