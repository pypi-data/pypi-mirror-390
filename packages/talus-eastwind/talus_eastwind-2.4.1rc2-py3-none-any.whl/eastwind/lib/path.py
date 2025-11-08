# -*- coding: utf-8 -*-
import os

# Get the current module directory.
DIR_EASTWIND: str = os.path.dirname(os.path.dirname(__file__))
# Get the library used offline static files.
DIR_EASTWIND_STATIC: str = os.path.join(DIR_EASTWIND, 'static')

# Get the root directory of the user directory.
DIR_ROOT: str = os.path.abspath(os.getcwd())
# Calculate the default project config file path.
PATH_CONFIG_FILE: str = os.path.join(DIR_ROOT, 'config.yaml')
# Calculate the other user directory path.
#  - Module
DIR_MODULE: str = os.path.join(DIR_ROOT, 'modules')
#  - Storage
DIR_STORAGE: str = os.path.join(DIR_ROOT, 'storage')
DIR_STORAGE_DATABASE: str = os.path.join(DIR_STORAGE, 'database')
DIR_STORAGE_TEMP: str = os.path.join(DIR_STORAGE, 'temporary')
#  - 3rd Party
DIR_3RD_PARTY: str = os.path.join(DIR_ROOT, '3rd_party')