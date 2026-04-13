"""
Offensive Tools Module
"""

from .airstrike import AirStrike
from .netshark import NetShark
from .silent_phish import SilentPhish
from .venom_maker import VenomMaker
from .hashbreaker import HashBreaker

__all__ = [
    'AirStrike',
    'NetShark',
    'SilentPhish',
    'VenomMaker',
    'HashBreaker'
]