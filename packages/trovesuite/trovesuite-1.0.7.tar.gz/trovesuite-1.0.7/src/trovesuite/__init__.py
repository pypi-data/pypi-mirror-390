"""
TroveSuite Package

A comprehensive authentication, authorization, notification, and storage service for ERP systems.
Provides JWT token validation, user authorization, permission checking, notification capabilities,
and Azure Storage blob management.
"""

from .auth import AuthService
from .notification import NotificationService
from .storage import StorageService

__version__ = "1.0.7"
__author__ = "Bright Debrah Owusu"
__email__ = "owusu.debrah@deladetech.com"

__all__ = [
    "AuthService",
    "NotificationService",
    "StorageService"
]
