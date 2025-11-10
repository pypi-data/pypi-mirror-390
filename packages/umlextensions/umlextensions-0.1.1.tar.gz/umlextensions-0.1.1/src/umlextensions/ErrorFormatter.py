
from sys import exc_info

from traceback import format_exception

MAX_STACK: int = 5


class ErrorFormatter:
    """
    A static class with class methods to simplify error reporting
    """
    def __init__(self):
        pass

    @classmethod
    def getErrorMessage(cls):
        error, eMessage, eTraceback = exc_info()
        return str(eMessage)

    @classmethod
    def getErrorStack(cls, e, limit: int = MAX_STACK) -> str:
        """
        Returns the bottom half of the error stack
        Args:
            e:
            limit:

        Returns:

        """

        errorList = format_exception(e)
        errorList.reverse()

        fs:         str = ''
        stackLimit: int = 0

        for e in errorList:
            fs = f'{fs}{e}'
            stackLimit += 1
            if stackLimit == limit:
                break

        return fs
