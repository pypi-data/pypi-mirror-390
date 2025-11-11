class PiiAbstractError(Exception):
    def __init__(self, message: str, error: Exception, status_code: int) -> None:
        assert isinstance(message, str), f'message must be str. "{type(message).__name__}" was given'
        assert isinstance(error, Exception), f'error must be Exception. "{type(error).__name__}" was given'
        super(PiiAbstractError, self).__init__(f'{message} :: {str(error)} :: {status_code})')
        self.status_code = status_code
        self.error = error


class PiiRequestError(PiiAbstractError):
    pass


class PiiResponseError(PiiAbstractError):
    pass
