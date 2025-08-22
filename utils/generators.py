import random
import string
from enum import Enum


class CodeType(str, Enum):
    NUMERIC = 'numeric'
    ALPHABETIC = 'alphabetic'
    ALPHANUMERIC = 'alphanumeric'
    NON_STANDARD = 'non_standard'


class CacheType(str, Enum):
    FORGOT_PASSWORD = 'forgot-password'
    CONFIRMED_FORGOT_PASSWORD = 'confirmed-forgot-password'
    COMPANY_UPDATE_PASSWORD = 'company-update-password'


def generate_code(length: int, code_type: CodeType) -> str:
    if length <= 0:
        raise ValueError("Length must be greater than 0")

    if code_type == CodeType.NUMERIC:
        chars = string.digits
    elif code_type == CodeType.ALPHABETIC:
        chars = string.ascii_letters
    elif code_type == CodeType.ALPHANUMERIC:
        chars = string.ascii_letters + string.digits
    elif code_type == CodeType.NON_STANDARD:
        unsafe = ": \t\n\r"
        raw = string.punctuation + string.whitespace
        chars = raw.translate(str.maketrans('', '', unsafe))
    else:
        raise ValueError(f"Unsupported code type: {code_type}")

    return ''.join(random.choices(chars, k=length))


def generate_cache_key(cache_type: CacheType, *parts) -> str:
    key_parts = [str(cache_type)] + list(map(str, parts))
    return ":".join(key_parts)


__all__ = [
    'generate_code',
    'generate_cache_key',
    'CacheType',
    'CodeType',
]
