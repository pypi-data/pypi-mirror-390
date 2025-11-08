from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lymo.serializer import dumps

if TYPE_CHECKING:
    from lymo.http_requests import HttpRequest


class BaseResponse(dict):
    default_headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-cache",
    }

    def __init__(
        self,
        *,
        body: str,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        merged = dict(self.default_headers)
        if headers:
            merged.update(headers)

        super().__init__(
            statusCode=status_code,
            headers=merged,
            body=body,
        )


class HttpResponse(BaseResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        body: str,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            body=body,
            status_code=status_code,
            headers=headers,
        )


class JsonResponse(HttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        data: dict | list[dict],
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        headers = headers or {}
        headers["Content-Type"] = "application/json; charset=utf-8"
        super().__init__(
            request=request,
            body=dumps(data),
            status_code=status_code,
            headers=headers,
        )


class TemplateResponse(HttpResponse):
    def __init__(
        self,
        *,
        request: HttpRequest,
        template: str,
        context: dict[str, Any] | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        template = request.template_env.get_template(template)
        if context is None:
            context = {}
        context.update({"request": request})
        body = template.render(**context)
        super().__init__(
            request=request,
            body=body,
            status_code=status_code,
            headers=headers,
        )
