import copy
import json
import logging
import ssl
import time
import urllib.request
from typing import Dict, Optional, Type
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request

from .resources import User, UserSearch
from .response import SCIMResponse


class SCIMClientMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        attr_meta = attrs.pop("Meta", None)
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        meta = attr_meta or getattr(new_class, "Meta", None)

        setattr(new_class, "UserCls", getattr(meta, "UserCls", User))
        setattr(new_class, "UserSearchCls", getattr(meta, "UserSearchCls", UserSearch))
        return new_class


class SCIMClient(metaclass=SCIMClientMeta):
    """
    Client to interact with the SCIM v2 API.
    """

    base_url: str
    token: str
    timeout: int
    default_headers: Dict[str, str]
    logger: logging.Logger
    UserCls: Type[User]
    UserSearchCls: Type[UserSearch]
    verify_ssl: bool

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = 30,
        max_retries: int = 3,
        default_headers: Optional[Dict[str, str]] = None,
        logger: Optional[logging.Logger] = None,
        verify_ssl: bool = True,
    ):
        self.token = token
        self.timeout = timeout
        self.base_url = base_url
        self.default_headers = default_headers if default_headers else {}
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl

    def search_users(self, q: str, count: int = 20, start_index: int = 0) -> UserSearch:
        """Search or filter users by query."""
        query_params = {
            key: value
            for key, value in (("filter", q), ("count", count), ("startIndex", start_index))
            if value not in [None, ""]
        }

        scim_response = self._make_request(
            method="GET",
            resource="Users",
            query_params=query_params,
        )
        return self.UserSearchCls(**scim_response.snake_cased_body)

    def create_user(self, user: User) -> User:
        """Creates a new user and returns `User` object."""

        scim_response = self._make_request(
            method="POST", resource="Users", data=user.to_dict()
        )
        return self.UserCls(**scim_response.snake_cased_body)

    def delete_user(self, user_id: Optional[str] = None, user: Optional[User] = None):
        """Deletes a user for given `user_id` or from `User` object."""

        assert (user_id is not None) or (
            user is not None
        ), "Must provide either user_id or user"
        scim_response = None
        if user_id is not None:
            scim_response = self._make_request(
                method="DELETE", resource="Users/%s" % user_id
            )
        elif user is not None:
            scim_response = self._make_request(
                method="DELETE", resource="Users/%s" % user.id
            )
        return scim_response

    def read_user(self, user_id: str) -> User:
        """Get user resource data for given `user_id`"""

        scim_response = self._make_request(method="GET", resource="Users/%s" % user_id)
        return self.UserCls(**scim_response.snake_cased_body)

    def update_user(self, user: User) -> User:
        scim_response = self._make_request(
            method="PUT", resource="Users/%s" % user.id, data=user.to_dict()
        )
        return self.UserCls(**scim_response.snake_cased_body)

    def _make_request(
        self,
        method: str,
        resource: str,
        data: Optional[Dict] = None,
        query_params: Optional[Dict] = None,
    ) -> SCIMResponse:
        url = "%s/%s" % (self.base_url, resource)
        headers = copy.deepcopy(self.default_headers)
        headers.update(
            {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": "Bearer %s" % self.token,
            }
        )
        if query_params is not None:
            url = url + "?" + urlencode(query_params)

        request_kwargs = {
            "url": url,
            "headers": headers,
        }

        if data is not None:
            request_kwargs["data"] = json.dumps(data).encode("utf-8")

        retries_left = self.max_retries
        http_error = None

        # disable certificate verification if `verify_ssl` is set to `False`
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = self.verify_ssl
        ssl_context.verify_mode = (
            ssl.CERT_REQUIRED if self.verify_ssl else ssl.CERT_NONE
        )

        while retries_left > 0:
            try:
                request = Request(**request_kwargs, method=method)
                with urllib.request.urlopen(request, context=ssl_context) as resp:
                    if 500 <= resp.status < 600:
                        raise HTTPError(
                            url=url,
                            code=resp.status,
                            msg=f"{resp.status} Server Error",
                            fp=resp,
                            hdrs=resp.getheaders(),
                        )
                    elif resp.status == 429:
                        raise HTTPError(
                            url=url,
                            code=resp.status,
                            msg=f"{resp.status} Too many requests",
                            fp=resp,
                            hdrs=resp.getheaders(),
                        )
                    return SCIMResponse(
                        url=url,
                        status_code=resp.status,
                        raw_body=resp.read().decode("utf-8"),
                        headers=resp.headers,
                    )
            except HTTPError as he:
                http_error = he
                if he.code >= 500 or he.code == 429:
                    self.logger.warning(
                        "HTTP error url={} code={} reason={} headers={}".format(
                            he.url, he.code, he.reason, he.headers
                        )
                    )
                    time.sleep(self.max_retries - retries_left + 1)
                    retries_left -= 1
                else:
                    raise he

        if http_error is not None:
            raise http_error
