from __future__ import annotations

import hashlib
import hmac

import httpx

from inaptas.infrastructure.integrations.models import IntegrationResult


class WhatsAppClient:
    def __init__(
        self,
        *,
        access_token: str = "",
        phone_number_id: str = "",
        app_secret: str = "",
        base_url: str = "https://graph.facebook.com",
        timeout_seconds: float = 10.0,
    ) -> None:
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def validar_assinatura(self, corpo: bytes, assinatura: str | None) -> bool:
        if not self.app_secret or not assinatura or not assinatura.startswith("sha256="):
            return False
        esperado = hmac.new(self.app_secret.encode(), corpo, hashlib.sha256).hexdigest()
        recebido = assinatura.removeprefix("sha256=")
        return hmac.compare_digest(recebido, esperado)

    async def enviar_texto(self, destinatario: str, texto: str) -> IntegrationResult:
        if not self.access_token or not self.phone_number_id:
            return IntegrationResult("unavailable", "integration_not_configured")

        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                follow_redirects=False,
            ) as cliente:
                resposta = await cliente.post(
                    f"/{self.phone_number_id}/messages",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={
                        "messaging_product": "whatsapp",
                        "to": destinatario,
                        "type": "text",
                        "text": {"body": texto},
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
