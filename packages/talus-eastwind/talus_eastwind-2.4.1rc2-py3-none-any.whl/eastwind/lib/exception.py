# -*- coding: utf-8 -*-
from typing import TypeAlias, Callable, Any
from fastapi import Request
from .util import err

ExceptionHandler: TypeAlias = Callable[[Request, Exception], Any]


class EastwindCriticalError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code: int = code
        self.message: str = message

    def to_json(self):
        return err(self.code, self.message)


class CliCommandError(Exception):
    def __init__(self, message: str):
        self.error_info: str = message


class ModuleNotExist(Exception):
    def __init__(self, module_prefix: str):
        self.module_prefix = module_prefix

    def __str__(self):
        return f'Module "{self.module_prefix}" does not exist'


class ModuleDependencyError(Exception):
    def __init__(self, failed_to_load: list[str]) -> None:
        self.failed_to_load = failed_to_load

    def __str__(self) -> str:
        return 'The following package cannot be loaded: \n' + '\n'.join(f" - {key}" for key in self.failed_to_load)
