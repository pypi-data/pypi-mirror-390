# -*- coding: utf-8 -*-
import os
import sys
import base64
import string
import asyncio
import importlib
import traceback
import subprocess
from types import ModuleType
from typing import TypeVar, Generic, Optional
from sqlalchemy import Select
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, CipherContext
from eastwind.lib.path import DIR_ROOT, DIR_EASTWIND

BUILTIN_PREFIX: str = 'eastwind.modules.'
PROJECT_PREFIX: str = 'modules.'
# Check whether is in debugging mode.
DEBUG_MODE: bool = os.environ.get("EASTWIND_DEBUG") == "1"


def response(code: int = 200, **results) -> dict:
    """
    Generate a standard dictionary response with "code" and "results" keys.
    :param code: The code to be returned, generally it have the same means of the standard HTTP response code.
    :param results: Any results to be packed within the dictionary.
    :return: Packed JSON dictionary response.
    """
    if len(results) == 0:
        return { 'code': code }
    return { 'code': code, 'result': results }


def err(code: int, msg: str) -> dict:
    return { 'code': code, 'error': msg }


T = TypeVar('T')


class Result(Generic[T]):
    def __init__(self, value: Optional[T] = None, error: Optional[dict] = None):
        # Treat has error.
        if error is not None and value is not None:
            raise ValueError("result and error are mutually exclusive")
        # Save the result and error result.
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return not self.is_error()

    def is_error(self) -> bool:
        return isinstance(self.error, dict)


def is_hex_str(data: str) -> bool:
    return all(c in string.hexdigits for c in data)


def is_n_long_hex_str(data: str, length: int) -> bool:
    return len(data) == length and is_hex_str(data)


def is_32_bytes_hash(data: str) -> bool:
    return is_n_long_hex_str(data, 64)


def str_to_base64(raw: str) -> str:
    return base64.urlsafe_b64encode(raw.encode('utf-8')).decode('utf-8')


def base64_to_str(encoded: str) -> str:
    return base64.urlsafe_b64decode(encoded.encode('utf-8')).decode('utf-8')


def sm3_hash_text(text: str) -> bytes:
    digest: hashes.Hash = hashes.Hash(hashes.SM3())
    digest.update(text.encode('utf-8'))
    return digest.finalize()


def sm4_encrypt_gcm(plain_text: str, key: bytes, iv: bytes) -> str:
    # Prepare the raw data with padding.
    padder = padding.PKCS7(128).padder()
    padded_plain: bytes = padder.update(plain_text.encode('utf-8')) + padder.finalize()
    # Encrypt the data.
    cipher: Cipher = Cipher(algorithms.SM4(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext: bytes = encryptor.update(padded_plain) + encryptor.finalize()
    # Get the authentication tag
    tag: bytes = encryptor.tag
    # Combine the ciphertext and tag
    return (ciphertext + tag).hex()


def sm4_decrypt_gcm(cipher_hex: str, key: bytes, iv: bytes) -> str:
    # Decrypt the data first.
    if not is_hex_str(cipher_hex):
        raise ValueError("cipher string must be hex string")
    # Convert the hex string to bytes
    cipher_bytes: bytes = bytes.fromhex(cipher_hex)
    # Extract the ciphertext and the authentication tag
    tag: bytes = cipher_bytes[-16:]  # Last 16 bytes are the tag
    ciphertext: bytes = cipher_bytes[:-16]  # The rest is the ciphertext
    # Create the cipher object in GCM mode
    cipher = Cipher(algorithms.SM4(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    # Decrypt the ciphertext
    decrypted_data: bytes = decryptor.update(ciphertext) + decryptor.finalize()
    # Un-pad the data.
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(decrypted_data) + unpadder.finalize()).decode('utf-8')


def import_module(module_name: str) -> ModuleType | None:
    # Load the modules to the running process.
    try:
        return importlib.import_module(module_name)
    # When fail to load the modules, return a None instead.
    except ModuleNotFoundError:
        return None
    except (ImportError, Exception):
        print(f"Error occurs during import of module '{module_name}': \n{traceback.format_exc()}")
        return None


def config_python_environ(env: dict) -> None:
    # Set encoding to UTF-8.
    env['PYTHONIOENCODING'] = 'UTF-8'
    # Add project directory to PATH.
    python_paths: list[str] = list({DIR_ROOT, os.path.dirname(DIR_EASTWIND)})
    env['PYTHONPATH'] = os.pathsep.join(python_paths)


def run_python_sync(*args, stdout=None, stderr=None) -> subprocess.Popen:
    # Configure the Python running environment.
    script_env = os.environ.copy()
    config_python_environ(script_env)
    # Launch the normal subprocess Popen method.
    proc = subprocess.Popen(
        [sys.executable, *args],
        cwd=os.getcwd(),
        env=script_env,
        stdout=stdout,
        stderr=stderr)
    proc.communicate()
    return proc


async def launch_python(*args, stdout=None, stderr=None) -> asyncio.subprocess.Process:
    # Configure the Python running environment.
    script_env = os.environ.copy()
    config_python_environ(script_env)
    # Launch the asyncio subprocess exec method.
    return await asyncio.create_subprocess_exec(
        sys.executable, *args,
        cwd=os.getcwd(),
        env=script_env,
        stdout=stdout,
        stderr=stderr,
    )


async def run_python(*args, stdout=None, stderr=None) -> asyncio.subprocess.Process:
    # Launch the asyncio subprocess exec method.
    proc = await launch_python(*args,
        stdout=stdout,
        stderr=stderr,
    )
    await proc.wait()
    return proc


def set_offset_and_limit(expression: Select, offset: int = -1, limit: int = -1) -> Select:
    """
    Set offset and limit to a select expression, if any of these value is -1, then this option will be ignored.
    :param expression: The SQL expression to execute.
    :param offset: The offset of the SQL query result.
    :param limit: The limit of the SQL query result.
    :return: The new select expression with offset and limit.
    """
    # Prepare a new expression.
    query_sql = expression
    # Add offset and limit if they are provided.
    if offset != -1:
        query_sql = query_sql.offset(offset)
    if limit != -1:
        query_sql = query_sql.limit(limit)
    return query_sql


def page_to_limit_offset(page: int, page_size: int) -> tuple[int, int]:
    """
    Convert the page and page size value from the endpoint request into SQL offset and limit.
    :param page: The requested page number.
    :param page_size: The requested page size.
    :return: A two integer value tuple, contains the offset and limit used in SQL expression.
    """
    return max(page - 1, 0) * page_size, page_size
