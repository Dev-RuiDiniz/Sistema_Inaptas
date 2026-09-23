from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any, cast

import httpx

from inaptas.domain.models import PgfnProviderResult, ProviderStatus

DOCUMENTO_TRIAL = "09781911768"
CAMINHO_TRIAL = f"/consulta-divida-ativa-trial/api/v1/devedor/{DOCUMENTO_TRIAL}"


class SerproDividaAtivaTrialProvider:
    nome = "SERPRO_PGFN_TRIAL"

    def __init__(
        self,
        base_url: str,
        api_token: str,
        timeout_seconds: float = 5.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.1,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

    async def consultar(self, cnpj: str) -> PgfnProviderResult:
        del cnpj  # O ambiente trial aceita temporariamente apenas o CPF fictício fixo.
        inicio = perf_counter()
        if not self.api_token:
            return self._resultado(ProviderStatus.INVALID, "provider_token_missing", inicio)

        tentativas = 0
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            follow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_token}",
            },
        ) as cliente:
            while True:
                try:
                    resposta = await cliente.get(CAMINHO_TRIAL)
                except httpx.TimeoutException:
                    if tentativas < self.max_retries:
                        tentativas += 1
                        await self._aguardar_retry(tentativas)
                        continue
                    return self._resultado(
                        ProviderStatus.UNAVAILABLE, "provider_timeout", inicio
                    )
                except httpx.RequestError:
                    if tentativas < self.max_retries:
                        tentativas += 1
                        await self._aguardar_retry(tentativas)
                        continue
                    return self._resultado(
                        ProviderStatus.UNAVAILABLE, "provider_connection_error", inicio
                    )

                if resposta.status_code == 200:
                    try:
                        payload = cast(Any, resposta.json())
                    except ValueError:
                        return self._resultado(
                            ProviderStatus.ERROR, "provider_invalid_json", inicio
                        )
                    return self._normalizar(payload, inicio)
                if resposta.status_code in {429, *range(500, 600)}:
                    if tentativas < self.max_retries:
                        tentativas += 1
                        await self._aguardar_retry(tentativas)
                        continue
                    return self._resultado(
                        ProviderStatus.UNAVAILABLE, "provider_unavailable", inicio
                    )
                if resposta.status_code in {401, 403}:
                    return self._resultado(
                        ProviderStatus.INVALID, "provider_unauthorized", inicio
                    )
                if resposta.status_code in {400, 404, 422}:
                    return self._resultado(
                        ProviderStatus.ERROR, "provider_invalid_request", inicio
                    )
                return self._resultado(ProviderStatus.ERROR, "provider_http_error", inicio)

    def _normalizar(self, payload: Any, inicio: float) -> PgfnProviderResult:
        if not isinstance(payload, list):
            return self._resultado(ProviderStatus.ERROR, "provider_invalid_payload", inicio)

        dividas: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict) or not isinstance(item.get("numeroInscricao"), str):
                return self._resultado(
                    ProviderStatus.ERROR, "provider_invalid_payload", inicio
                )
            dividas.append(
                {
                    "registration_number": item.get("numeroInscricao"),
                    "process_number": item.get("numeroProcesso"),
                    "status_code": item.get("situacaoInscricao"),
                    "status_description": item.get("situacaoDescricao"),
                    "debtor_name": item.get("nomeDevedor"),
                    "debtor_type": item.get("tipoDevedor"),
                    "consolidated_total": item.get("valorTotalConsolidadoMoeda"),
                    "document": item.get("cpfCnpj"),
                    "sida_code": item.get("codigoSida"),
                    "unit_name": item.get("nomeUnidade"),
                    "comprot_code": item.get("codigoComprot"),
                    "uorg_code": item.get("codigoUorg"),
                }
            )
        return self._resultado(
            ProviderStatus.OK,
            None,
            inicio,
            {"has_active_debt": bool(dividas), "debts": dividas},
        )

    async def _aguardar_retry(self, tentativa: int) -> None:
        if self.retry_backoff_seconds:
            await asyncio.sleep(self.retry_backoff_seconds * tentativa)

    def _resultado(
        self,
        status: ProviderStatus,
        error_code: str | None,
        inicio: float,
        source_data: dict[str, Any] | None = None,
    ) -> PgfnProviderResult:
        return PgfnProviderResult(
            provider=self.nome,
            status=status,
            source_data=source_data or {},
            error_code=error_code,
            latency_ms=int((perf_counter() - inicio) * 1000),
        )
