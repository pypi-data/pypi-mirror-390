from __future__ import annotations
from typing import Any, TYPE_CHECKING, Optional

from dataclasses import dataclass, field

if TYPE_CHECKING:
    from aws_lambda_typing.events import APIGatewayProxyEventV1
    from aws_lambda_typing.context import Context
    from jinja2 import Environment


@dataclass(kw_only=True)
class HttpRequest:
    event: APIGatewayProxyEventV1
    context: Context
    path_params: Optional[dict[str, str]] = None
    template_env: Environment
    method: str = field(init=False)
    path: str = field(init=False)
    headers: dict[str, str] = field(init=False)
    queryparams: dict[str, str] = field(init=False)
    body: Any = field(init=False)
    resources: Optional[dict[str, Any]] = None

    def __post_init__(self):
        self.method = self.event["httpMethod"]
        self.path = self.event["path"]
        self.headers = self.event.get("headers", {})
        self.queryparams = self.event.get("queryStringParameters") or {}
        self.body = self.event.get("body")
        if self.resources is None:
            self.resources = {}
        if self.path_params is None:
            self.path_params = {}
