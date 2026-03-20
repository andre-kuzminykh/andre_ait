"""
Кастомные исключения.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)
