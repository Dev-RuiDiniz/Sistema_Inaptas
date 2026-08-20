from __future__ import annotations

from typing import cast

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def tratar_cnpj_invalido(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "invalid_cnpj",
                "message": "O CNPJ informado é inválido.",
                "correlation_id": request.state.correlation_id,
            }
        },
    )


async def tratar_http_exception(request: Request, exc: Exception) -> JSONResponse:
    http_exception = cast(HTTPException, exc)
    code = {
        401: "unauthorized",
        429: "rate_limit_exceeded",
        503: "dependency_unavailable",
    }.get(http_exception.status_code, "http_error")
    message = (
        "Não autorizado."
        if http_exception.status_code == 401
        else "Não foi possível processar a requisição."
    )
    return JSONResponse(
        status_code=http_exception.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "correlation_id": request.state.correlation_id,
            }
        },
    )
