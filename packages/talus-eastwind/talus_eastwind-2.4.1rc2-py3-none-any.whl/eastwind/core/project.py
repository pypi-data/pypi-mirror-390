# -*- coding: utf-8 -*-
import os
from datetime import datetime, timezone
from typing import Type, TypedDict, Generator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from starlette.datastructures import State
from eastwind.lib.path import PATH_CONFIG_FILE
from eastwind.lib.database import Database
from eastwind.lib.module import sort_config_module_by_dependencies, iterate_modules
from .config import Config

# Prepare the static prefix.
PREFIX_STATIC: str = "/api/eastwind/static"

class Project(TypedDict):
    config: Config
    main_db: Database
    Session: Type[AsyncSession]
    module_dependency_order: list[tuple[str, str]]


def start_project() -> Project:
    # Prepare a global config instance.
    config = Config()
    path_config_file: str = PATH_CONFIG_FILE
    if "EASTWIND_CONFIG" in os.environ and os.path.isfile(os.environ["EASTWIND_CONFIG"]):
        path_config_file = os.environ["EASTWIND_CONFIG"]
    if os.path.isfile(path_config_file):
        config.load_from_yaml(path_config_file)
    # Load the database from the config.
    try:
        main_db: Database = Database(config.db_type, config.db_url)
    except Exception as e:
        raise RuntimeError(f"Error happened when loading database: {str(e)}")
    # Calculate the modules dependency order.
    module_dependency_order = sort_config_module_by_dependencies(config.module_builtin, config.module_project)
    # Prepare the project state.
    return Project(
        config=config,
        main_db=main_db,
        Session=main_db.Session,
        module_dependency_order=module_dependency_order,
    )


async def stop_project(state: Project):
    # Stop the database connection.
    await state["main_db"].close()


# Loop using the dependency order.
def iterate_all_modules(state: State) -> Generator[tuple[str, str], None, None]:
    yield from iterate_modules(state.module_dependency_order)


# Convert the datetime to config local time.
def to_local_timezone(state: State, db_datetime: datetime | Mapped[datetime]) -> datetime:
    # Correctly construct the UTC datetime.
    return db_datetime.replace(tzinfo=timezone.utc).astimezone(state.config.timezone)
