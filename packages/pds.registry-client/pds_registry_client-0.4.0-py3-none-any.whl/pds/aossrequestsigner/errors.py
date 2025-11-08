from http import HTTPStatus
from typing import Optional


class Non200HttpStatusError(RuntimeError):
    def __init__(self, status_code: int, description: Optional[str] = None):
        if status_code == HTTPStatus.OK:
            raise ValueError('Cannot init Non200HttpStatusError with status_code=200')

        msg = f'Response returned HTTP{status_code} {HTTPStatus(status_code).phrase}'
        if description is not None:
            msg += f': {description}'

        super().__init__(msg)
