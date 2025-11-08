from __future__ import annotations

import dataclasses
from typing import Any, TYPE_CHECKING


from lymo.router import load_routes
from lymo.templating import load_template_environment

if TYPE_CHECKING:
    from jinja2 import Environment
    from logging import Logger


@dataclasses.dataclass(kw_only=True)
class App:
    routes: Any
    template_dir: str | None = None
    template_globals: dict | None = None
    resources: dict[str, Any] | None = None
    template_env: Environment | None = None
    template_extensions: list[str] | None = None
    logger: Logger | None = None

    def __post_init__(self):
        load_routes(self.routes)
        if self.template_env is None:
            if self.template_dir:
                template_extensions = self.template_extensions or []
                self.template_env = load_template_environment(
                    self.template_dir,
                    template_globals=self.template_globals,
                    extensions=template_extensions,
                )
        else:
            self.template_env.globals.update(self.template_globals)
