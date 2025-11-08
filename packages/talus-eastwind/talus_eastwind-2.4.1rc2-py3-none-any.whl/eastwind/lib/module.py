# -*- coding: utf-8 -*-
from typing import Generator
from eastwind.lib.exception import ModuleDependencyError, ModuleNotExist
from eastwind.lib.util import import_module, BUILTIN_PREFIX, PROJECT_PREFIX

BUILTIN_KEY: str = 'eastwind'
PROJECT_KEY: str = 'project'


def sort_by_dependencies(candidates: dict[str, set[str]]) -> list[str]:
    # Topological sort the modules with its dependency.
    # Expect to pass in:
    # {'item': {'set', 'of', 'dependency', ...}), ...}
    result: list[str] = []
    # Pick up all the packages without requirements.
    loaded_set: set[str] = set()
    # Loop and loaded candidates that can be loaded.
    while len(candidates) > 0:
        # Extract the package that can be loaded.
        iterate_loaded_set: set[str] = set()
        # Find out the empty dependency modules.
        for name in candidates:
            if candidates[name].issubset(loaded_set):
                # Add the name to loaded set.
                iterate_loaded_set.add(name)
        # Check whether there is no package can be handled.
        if len(iterate_loaded_set) == 0 and len(candidates) > 0:
            raise ModuleDependencyError(list(candidates.keys()))
        # Append the set to the order list.
        loaded_set = loaded_set.union(iterate_loaded_set)
        result += list(iterate_loaded_set)
        # Remove the result from the package from candidates.
        for package_name in iterate_loaded_set:
            candidates.pop(package_name)
    return result


def iterate_modules(module_info: list[tuple[str, str]]) -> Generator[tuple[str, str], None, None]:
    # Iterate the modules info, and simply yield the modules name and modules prefix.
    for module_name, module_prefix in module_info:
        yield module_name, module_prefix


def load_module_dependency(module_prefix: str) -> set[str]:
    # Try to load 'package' submodule inside the modules.
    try:
        target = import_module(f'{module_prefix}.package')
    except ModuleNotFoundError:
        raise ModuleNotExist(module_prefix)

    # Inside the package.py file, it should define the "EW_MODULE" dict.
    # The 'requirements' contains two keys: 'eastwind' and 'project', which defines the modules
    # requires for the built-in modules and project modules.
    requirements: set[str] = set()
    if hasattr(target, 'EW_MODULE'):
        module_info = target.EW_MODULE
        if isinstance(module_info, dict) and 'requirements' in module_info:
            # Check out the modules settings.
            module_requirements = module_info['requirements']
            # It should be a dict, and contain two dictionaries:
            if isinstance(module_requirements, dict):
                if BUILTIN_KEY in module_requirements and isinstance(module_requirements[BUILTIN_KEY], list):
                    requirements |= set([f'{BUILTIN_PREFIX}{x}' for x in module_requirements[BUILTIN_KEY]])
                if PROJECT_KEY in module_requirements and isinstance(module_requirements[PROJECT_KEY], list):
                    requirements |= set([f'{PROJECT_PREFIX}{x}' for x in module_requirements[PROJECT_KEY]])
    return requirements


def sort_config_module_by_dependencies(builtin_modules: list[str], project_modules: list[str]) -> list[tuple[str, str]]:
    module_name_map: dict[str, str] = {}
    module_dependencies: dict[str, set[str]] = {}
    # Load the built-in modules.
    for module_name in builtin_modules:
        module_prefix: str = f'{BUILTIN_PREFIX}{module_name}'
        module_name_map[module_prefix] = module_name
        module_dependencies[module_prefix] = load_module_dependency(module_prefix)
    # Load the project modules.
    for module_name in project_modules:
        module_prefix: str = f'{PROJECT_PREFIX}{module_name}'
        module_name_map[module_prefix] = module_name
        module_dependencies[module_prefix] = load_module_dependency(module_prefix)
    # Sort the dependencies.
    module_sequences: list[str] = sort_by_dependencies(module_dependencies)
    # Based on the sequence, generate the (module_name, module_prefix) pair.
    return [(module_name_map[module_prefix], module_prefix) for module_prefix in module_sequences]
