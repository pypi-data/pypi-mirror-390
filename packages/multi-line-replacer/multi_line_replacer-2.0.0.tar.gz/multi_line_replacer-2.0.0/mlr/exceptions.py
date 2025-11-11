#!/usr/bin/env python3


class MLRException(Exception):
    """Base exception class for MLR-related exceptions."""

    pass


class TargetCodeBlockEmpty(MLRException):
    """Exception raised the target text code block is empty."""

    pass


class CodeBlocksMismatched(MLRException):
    """Exception raised when there is an odd number of code blocks."""

    pass
