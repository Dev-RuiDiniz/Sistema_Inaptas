from fastapi import FastAPI

from inaptas.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    configuracao = settings or get_settings()
    app = FastAPI(
        title="Fiscal Gateway — Inaptas",
        version=configuracao.app_version,
        docs_url="/docs" if configuracao.openapi_enabled else None,
        redoc_url="/redoc" if configuracao.openapi_enabled else None,
        openapi_url="/openapi.json" if configuracao.openapi_enabled else None,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": configuracao.app_version}

    return app


app = create_app()
