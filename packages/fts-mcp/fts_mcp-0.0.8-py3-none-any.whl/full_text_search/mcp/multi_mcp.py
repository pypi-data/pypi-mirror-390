# ---------------------------------------------------------------------------
# multi_mcp.py – helper to load N configs and return a ready-to-run FastAPI app
# ---------------------------------------------------------------------------
import argparse
import sys

import uvicorn
from fastapi import FastAPI
from starlette.routing import Mount

from .mcp import FullTextSearchMCP, load_config_from_yaml


def build_multi_mcp_app(
    config_paths: list[str],
    host: str = "0.0.0.0",
    port: int = 8000,
) -> FastAPI:
    """
    Build a FastAPI app that mounts one FastMCP server per YAML.
    """
    routes = []
    lifespans = []

    seen_paths = set()
    for cfg_path in config_paths:
        srv_name, srv_desc, idx_cfgs, srv_cfg = load_config_from_yaml(cfg_path)
        mount_path = srv_cfg.get("mount", "/mcp").rstrip("/") or "/mcp"

        if mount_path in seen_paths:
            raise ValueError(f"Duplicate mount path '{mount_path}' across configs")
        seen_paths.add(mount_path)

        search_srv = FullTextSearchMCP(srv_name, srv_desc, idx_cfgs)
        mcp = search_srv.create_mcp_server()

        # Build ASGI sub-app at /mcp/ inside each mount
        sub_app = mcp.http_app(path="/")  # default path="/mcp/" ➜ /books/mcp/
        lifespans.append(sub_app.lifespan)
        routes.append(Mount(mount_path, sub_app))

    # FastAPI accepts only one lifespan handler – use the first one.
    # This is sufficient because every sub-app registers its own session
    # manager inside its own lifespan context.  See FastMCP docs.
    # https://gofastmcp.com/deployment/asgi#fastapi-integration :contentReference[oaicite:0]{index=0}
    app = FastAPI(routes=routes, lifespan=lifespans[0])

    # Convenience runner so you can still do `python multi_mcp.py …`
    def _run() -> None:  # pragma: no cover
        uvicorn.run(app, host=host, port=port)

    app.run = _run  # type: ignore[attr-defined]
    return app


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        action="append",
        required=True,
        help="May be given multiple times – one YAML per index group",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    try:
        app = build_multi_mcp_app(args.config, host=args.host, port=args.port)
        app.run()  # type: ignore # uvicorn wrapper attached in helper
    except Exception as exc:
        print(f"Error starting server: {exc}", file=sys.stderr)
        return 1
    return 0
