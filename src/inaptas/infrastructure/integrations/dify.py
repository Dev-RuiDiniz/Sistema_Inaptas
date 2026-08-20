from __future__ import annotations

from typing import Any

import httpx

from inaptas.infrastructure.integrations.models import IntegrationResult


class DifyClient:
    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    async def enviar_contexto(self, contexto: dict[str, Any]) -> IntegrationResult:
        if not self.base_url or not self.api_key:
            return IntegrationResult("unavailable", "integration_not_configured")

        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                follow_redirects=False,
            ) as cliente:
                resposta = await cliente.post(
                    "/v1/workflows/run",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "inputs": {"event": contexto},
                        "response_mode": "blocking",
                        "user": "inaptas-gateway",
                    },
                )
        except httpx.TimeoutException:
            return IntegrationResult("unavailable", "integration_timeout")
        except httpx.RequestError:
            return IntegrationResult("unavailable", "integration_connection_error")

        if resposta.status_code == 429 or resposta.status_code >= 500:
            return IntegrationResult("unavailable", "integration_unavailable")
        if resposta.is_success:
            return IntegrationResult("ok")
        return IntegrationResult("error", "integration_http_error")
