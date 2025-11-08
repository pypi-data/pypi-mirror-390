from __future__ import annotations

import importlib
import json
import pkgutil
import re

APP_ROUTES = []


def route(path_pattern: str, method: str, cache_ttl: int | None = None):
    """
    Route decorator with optional edge caching support.

    Args:
        path_pattern: URL path pattern with optional {params}
        method: HTTP method (GET, POST, etc.)
        cache_ttl: Cache TTL in seconds (adds Cache-Control header)
                   Only applies to safe methods (GET, HEAD, OPTIONS)

    Example:
        @route("/quotes/", "GET", cache_ttl=300)  # 5 minute cache

    Note:
        cache_ttl is ignored for unsafe methods (POST, PUT, PATCH, DELETE)
        to prevent caching of mutations.
    """
    method = method.upper()
    normalized_pattern = path_pattern.strip("/")

    # Only cache safe/idempotent methods
    CACHEABLE_METHODS = {'GET', 'HEAD', 'OPTIONS'}

    def wrapper(func):
        regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", normalized_pattern)

        # Wrap the handler to add cache headers if specified
        def cached_handler(*args, **kwargs):
            response = func(*args, **kwargs)

            # Add Cache-Control header only for safe methods
            if cache_ttl is not None and method in CACHEABLE_METHODS and isinstance(response, dict):
                if 'headers' not in response:
                    response['headers'] = {}
                response['headers']['Cache-Control'] = f'public, max-age={cache_ttl}'

            return response

        APP_ROUTES.append((method, re.compile(f"^{regex}$"), cached_handler))
        return func

    return wrapper


def match_route(path: str, method: str):
    normalized = path.strip("/")
    for route_method, route_pattern, handler in APP_ROUTES:
        if method == route_method:
            m = route_pattern.match(normalized)
            if m:
                return handler, m.groupdict()
    return None, {}


def http_not_found(event, context):
    return {"statusCode": 404, "body": json.dumps({"error": "Route not found"})}


def load_routes(package):
    """
    Dynamically import all submodules of the given package
    so that any @route() decorators in them get registered.

    Usage:
        load_routes(routes)
    """
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_name = f"{package.__name__}.{module_name}"
        importlib.import_module(full_name)
