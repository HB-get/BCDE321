from dataclasses import dataclass

from zimp.domain.common.error_code import ErrorCode


@dataclass(frozen=True)
class Result[T]:
    """Result used to return ErrorCode or data from method calls."""

    __error_code: ErrorCode | None
    __data: T

    @staticmethod
    def success(data: T) -> Result[T]:
        """Creates a success Result.
        Args:
            data (T): Data to create a success Result.
        Returns:
            Result: A success Result.
        """
        return Result(None, data)

    @staticmethod
    def fail(error: ErrorCode) -> Result[T]:
        """Creates a fail Result.
        Args:
            error (ErrorCode): Error code to create a fail Result.
        Returns:
            Result: A fail Result.
        """
        return Result(error, None)

    def get_data(self) -> T:
        """Gets data from the Result.
        Returns:
            T: The data from the Result.
        """
        return self.__data

    def get_error_code(self) -> ErrorCode | None:
        """Gets error code from the Result.
        Returns:
            ErrorCode: The error code from a fail Result. | None: From a success Result.
        """
        return self.__error_code

    def is_fail(self) -> bool:
        """Checks if the Result is a fail.
        Returns:
            bool: True if the Result is a fail, False if the Result is a success.
        """
        return self.__error_code is not None
