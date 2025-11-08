import json
from typing import Dict, Any, Optional

from .utils import _to_snake_cased


class Error:
    code: int
    description: str

    def __init__(self, code: int, description: str) -> None:
        self.code = code
        self.description = description

    def to_dict(self) -> dict:
        return {"code": self.code, "description": self.description}


class SCIMResponse:
    url: str
    status_code: int
    headers: Dict[str, Any]
    raw_body: Optional[str]
    body: Optional[Dict[str, Any]]
    error: Optional[Error]

    @property
    def snake_cased_body(self) -> Optional[Dict[str, Any]]:  # type: ignore
        if self._snake_cased_body is None:
            self._snake_cased_body = _to_snake_cased(self.body)
        return self._snake_cased_body

    def __init__(
        self,
        *,
        url: str,
        status_code: int,
        headers: Dict[str, Any],
        raw_body: Optional[str],
    ):
        self.url = url
        self.status_code = status_code
        self.raw_body = raw_body
        self.headers = headers
        self.body = (
            json.loads(raw_body)
            if raw_body is not None and raw_body.startswith("{")
            else None
        )
        self._snake_cased_body = None

    def __repr__(self):
        dict_value = {}
        for key, value in vars(self).items():
            dict_value[key] = value.to_dict() if hasattr(value, "to_dict") else value

        if dict_value:  # skipcq: PYL-R1705
            return f"<scim_client.{self.__class__.__name__}: {dict_value}>"
        else:
            return self.__str__()
