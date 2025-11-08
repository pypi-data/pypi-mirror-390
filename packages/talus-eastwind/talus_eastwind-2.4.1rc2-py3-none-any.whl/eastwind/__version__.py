# -*- coding: utf-8 -*-
MAJOR_VERSION = 2
MINOR_VERSION = 4
PATCH_VERSION = 1
SUFFIX_VERSION = "rc2"
POST_VERSION = ""

def get_version():
    post_version = POST_VERSION
    if len(POST_VERSION) != 0:
        post_version = f".{POST_VERSION}"
    return f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}{SUFFIX_VERSION}{post_version}"

VERSION = get_version()
