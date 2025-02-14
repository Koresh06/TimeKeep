from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from jinja2 import pass_context


@pass_context
def urlx_for(context: dict, name: str, **path_params: Any) -> str:
    request: Request = context["request"]
    http_url = request.url_for(name, **path_params)
    scheme = request.headers.get("x-forwarded-proto", "http") 
    return http_url._url.replace("http://", f"{scheme}://")  


templates = Jinja2Templates(directory="src/templates")
templates.env.globals["urlx_for"] = urlx_for


def configure_static(app):
    app.mount("/static", StaticFiles(directory="src/static"), name="static")