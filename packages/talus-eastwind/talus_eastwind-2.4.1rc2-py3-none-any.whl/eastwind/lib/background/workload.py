# -*- coding: utf-8 -*-
from typing import Callable, Awaitable, Any


class Workload:
    def __init__(self, func: Callable[..., Awaitable[Any]], *args, **kwargs):
        # Save the function with its arguments.
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    async def __call__(self, *args) -> Any:
        # Launch the function with its arguments.
        return await self.__func(*args, *self.__args, **self.__kwargs)
