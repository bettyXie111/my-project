"""Development entry point for the API server."""

from __future__ import annotations

from wsgiref.simple_server import make_server

from app.core.config import settings
from app.main import create_application


def main() -> None:
    application = create_application()
    with make_server(settings.host, settings.port, application) as server:
        print(f"Serving {settings.app_name} at http://{settings.host}:{settings.port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
