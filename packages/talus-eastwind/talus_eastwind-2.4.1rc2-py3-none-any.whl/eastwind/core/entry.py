# -*- coding: utf-8 -*-
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import State
from eastwind.__version__ import VERSION
from eastwind.lib.exception import EastwindCriticalError
from eastwind.lib.util import import_module, response, DEBUG_MODE
from eastwind.lib.path import DIR_EASTWIND_STATIC
from .docs import (
    URL_OPENAPI,
    URL_SWAGGER_OAUTH2_REDIRECT,
    APP_TITLE,
)
from .project import (
    PREFIX_STATIC,
    start_project,
    stop_project,
    Project,
    iterate_all_modules
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the project.
    project: Project = start_project()
    # Load all the endpoints from each module referenced in the config file.
    state: State = State(project)
    for module_name, module_prefix in iterate_all_modules(state):
        endpoints_module = import_module(f"{module_prefix}.endpoint")
        if endpoints_module is None:
            continue
        # Check whether load_endpoint() exists in the module.
        if hasattr(endpoints_module, "load_endpoints"):
            await endpoints_module.load_endpoints(state)
        # Add endpoint router to app.
        if hasattr(endpoints_module, 'router') and isinstance(endpoints_module.router, APIRouter):
            app.include_router(endpoints_module.router, prefix=f'/api/{module_name}')
    # Yield with the project state.
    yield project
    # Close the project correctly.
    await stop_project(project)


app = FastAPI(lifespan=lifespan,
              title=APP_TITLE,
              version=VERSION,
              openapi_url=URL_OPENAPI,
              default_response_class=ORJSONResponse,
              docs_url=None, redoc_url=None,
              swagger_ui_oauth2_redirect_url=URL_SWAGGER_OAUTH2_REDIRECT,)
# Mount the library used offline static files.
app.mount(PREFIX_STATIC, StaticFiles(directory=DIR_EASTWIND_STATIC), name="eastwind_static")
# Only loaded docs in DEBUG_MODE.
if DEBUG_MODE:
    from .docs import router as docs_router
    app.include_router(docs_router)


@app.get("/api", response_class=JSONResponse)
async def core_echo_request():
    return response()


@app.exception_handler(EastwindCriticalError)
async def service_critical_error_handler(_: Request, exc: EastwindCriticalError):
    return JSONResponse(
        status_code=200,
        content=exc.to_json(),
    )
