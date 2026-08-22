from __future__ import annotations

import asyncio

import httpx

from inaptas.infrastructure.integrations.models import IntegrationResult


class N8nClient:
    """Entrega eventos validados ao webhook interno do n8n."""

    def __init__(
        self,
        webhook_url: str,
        token: str,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
    ) -> None:
        self.webhook_url = webhook_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)

    async def enviar_evento(
        self,
        payload: dict[str, object],
        correlation_id: str | None = None,
    ) -> IntegrationResult:
        if not self.webhook_url or not self.token:
            return IntegrationResult("unavailable", "integration_not_configured")

        headers = {"Authorization": f"Bearer {self.token}"}
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id

        for tentativa in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout_seconds, follow_redirects=False
                ) as cliente:
                    resposta = await cliente.post(self.webhook_url, headers=headers, json=payload)
            except httpx.TimeoutException:
                if tentativa < self.max_retries:
                    await asyncio.sleep(0)
                    continue
                return IntegrationResult("unavailable", "integration_timeout")
            except httpx.RequestError:
                if tentativa < self.max_retries:
                    await asyncio.sleep(0)
                    continue
                return IntegrationResult("unavailable", "integration_connection_error")

            if resposta.status_code == 429 or resposta.status_code >= 500:
                if tentativa < self.max_retries:
                    await asyncio.sleep(0)
                    continue
                return IntegrationResult("unavailable", "integration_unavailable")
            if 200 <= resposta.status_code < 300:
                return IntegrationResult("accepted")
            return IntegrationResult("error", "integration_http_error")

        return IntegrationResult("unavailable", "integration_unavailable")
