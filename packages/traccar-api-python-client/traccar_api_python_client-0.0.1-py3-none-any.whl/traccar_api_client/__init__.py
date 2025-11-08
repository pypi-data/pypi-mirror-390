"""A Python API client for the Traccar GPS tracking system"""

__version__ = "0.0.1"

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
