from .core import ExpireDate, set_expiration, check_expiration
from .prot import ProtectionSystem
from .val import TimeValidator
from .term import SystemTerminator
from .net import NetworkTimeValidator
from .mem import MemoryProtection
from .hook import SystemHooks

__version__ = "1.0.0"
__author__ = "san"
__telegram__ = "@ii00hh"

__all__ = [
    "ExpireDate",
    "set_expiration",
    "check_expiration",
    "ProtectionSystem",
    "TimeValidator",
    "SystemTerminator",
    "NetworkTimeValidator",
    "MemoryProtection",
    "SystemHooks"
]
