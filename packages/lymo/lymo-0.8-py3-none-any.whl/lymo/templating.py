import base64
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape


def filter_base64encode(s):
    if isinstance(s, str):
        s = s.encode("utf-8")
    return base64.b64encode(s).decode("utf-8")


def filter_urlencode(s):
    return quote(s)


def load_template_environment(
    template_dir: str,
    template_globals: dict | None = None,
    extensions: list[str] | None = None,
):
    template_env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template_globals = template_globals or {}
    template_env.globals.update(template_globals)
    template_env.filters["urlencode"] = filter_urlencode
    template_env.filters["base64"] = filter_base64encode
    if extensions:
        for extension in extensions:
            template_env.add_extension(extension)
    return template_env
