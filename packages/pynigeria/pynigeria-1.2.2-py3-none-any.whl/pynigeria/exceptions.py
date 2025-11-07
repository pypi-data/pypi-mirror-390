# Custom exceptions for pynigeria.

from __future__ import annotations


class PyNigeriaError(Exception):
    """
    Base exception for all pynigeria errors.
    """


class DataLoadError(PyNigeriaError):
    """
    Raised when data files cannot be loaded or parsed.
    """


class DataIntegrityError(PyNigeriaError):
    """
    Raised when data validation fails.
    """


class NotFoundError(PyNigeriaError):
    """
    Raised when a requested resource is not found.
    """
