import sys


def _error_message_detail(error: Exception | str) -> str:
    _, _, exc_tb = sys.exc_info()
    if exc_tb is None:
        return str(error)

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    return (
        f"Error occurred in python script [{file_name}] "
        f"line number [{line_number}] error message [{error}]"
    )


class NetworkSecurityException(Exception):
    def __init__(self, error_message: Exception | str) -> None:
        self.error_message = _error_message_detail(error_message)
        super().__init__(self.error_message)

    def __str__(self) -> str:
        return self.error_message
