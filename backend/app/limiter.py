"""Shared rate limiter (slowapi).

Kept in its own module so both main.py (registers state/handler) and the auth
route (applies @limiter.limit) can import it without a circular import.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])
