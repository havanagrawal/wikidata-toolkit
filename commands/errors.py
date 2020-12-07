"""Errors raised by the commands module"""

class CommandError(Exception):
    """Base exception for all command errors"""
    def __init__(self, message):
        super().__init__()
        self.message = message


class SuspiciousTitlesError(CommandError):
    ...
