from __future__ import annotations

from time import perf_counter
from typing import Any

import httpx

from inaptas.domain.models import CadastroProviderResult, ProviderStatus


class ReceitaWsProvider:
    nome = "RECEITAWS"

    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        inicio = perf_counter()
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds,
                follow_redirects=False,
            ) as cliente:
                resposta = await cliente.get(f"/v1/cnpj/{cnpj}")
        except httpx.TimeoutException:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.UNAVAILABLE,
                source_data={},
                error_code="provider_timeout",
                latency_ms=_latencia(inicio),
            )
        except httpx.RequestError:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.UNAVAILABLE,
                source_data={},
                error_code="provider_connection_error",
                latency_ms=_latencia(inicio),
            )

        if resposta.status_code == 429 or resposta.status_code >= 500:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.UNAVAILABLE,
                source_data={},
                error_code="provider_unavailable",
                latency_ms=_latencia(inicio),
            )
        if resposta.status_code in {401, 403}:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.ERROR,
                source_data={},
                error_code="provider_unauthorized",
                latency_ms=_latencia(inicio),
            )
        if resposta.status_code != 200:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.ERROR,
                source_data={},
                error_code="provider_http_error",
                latency_ms=_latencia(inicio),
            )

        try:
            payload = resposta.json()
        except ValueError:
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.ERROR,
                source_data={},
                error_code="provider_invalid_json",
                latency_ms=_latencia(inicio),
            )

        if payload.get("status") != "OK":
            return CadastroProviderResult(
                provider=self.nome,
                status=ProviderStatus.INVALID,
                source_data={},
                error_code="provider_rejected_cnpj",
                latency_ms=_latencia(inicio),
            )

        return CadastroProviderResult(
            provider=self.nome,
            status=ProviderStatus.OK,
            source_data=_mapear_payload(payload),
            latency_ms=_latencia(inicio),
        )


def _latencia(inicio: float) -> int:
    return round((perf_counter() - inicio) * 1000)


def _mapear_payload(payload: dict[str, Any]) -> dict[str, Any]:
    simples = payload.get("simples") or {}
    simei = payload.get("simei") or {}
    return {
        "legal_name": payload.get("nome"),
        "opening_date": payload.get("abertura"),
        "registration_status": payload.get("situacao"),
        "registration_status_date": payload.get("data_situacao"),
        "registration_status_reason": payload.get("motivo_situacao"),
        "simple_national": simples.get("optante"),
        "simei": simei.get("optante"),
    }
