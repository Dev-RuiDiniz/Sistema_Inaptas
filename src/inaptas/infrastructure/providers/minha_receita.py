from __future__ import annotations

import asyncio
import re
from time import perf_counter
from typing import Any

import httpx

from inaptas.domain.models import CadastroProviderResult, ProviderStatus


class MinhaReceitaProvider:
    """Consulta cadastral no serviço interno Minha Receita."""

    nome = "MINHA_RECEITA"

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 5.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.1,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        inicio = perf_counter()
        for tentativa in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.timeout_seconds,
                    follow_redirects=False,
                ) as cliente:
                    resposta = await cliente.get(f"/{cnpj}")
            except httpx.TimeoutException:
                if tentativa < self.max_retries:
                    await self._aguardar_retry()
                    continue
                return _resultado(
                    self.nome,
                    ProviderStatus.UNAVAILABLE,
                    "provider_timeout",
                    inicio,
                )
            except httpx.RequestError:
                if tentativa < self.max_retries:
                    await self._aguardar_retry()
                    continue
                return _resultado(
                    self.nome,
                    ProviderStatus.UNAVAILABLE,
                    "provider_connection_error",
                    inicio,
                )

            if resposta.status_code == 429 or resposta.status_code >= 500:
                if tentativa < self.max_retries:
                    await self._aguardar_retry()
                    continue
                return _resultado(
                    self.nome,
                    ProviderStatus.UNAVAILABLE,
                    "provider_unavailable",
                    inicio,
                )
            break

        if resposta.status_code == 404:
            return _resultado(
                self.nome,
                ProviderStatus.INVALID,
                "provider_cnpj_not_found",
                inicio,
            )
        if resposta.status_code in {400, 422}:
            return _resultado(
                self.nome,
                ProviderStatus.INVALID,
                "provider_invalid_request",
                inicio,
            )
        if resposta.status_code in {401, 403}:
            return _resultado(
                self.nome,
                ProviderStatus.ERROR,
                "provider_unauthorized",
                inicio,
            )
        if resposta.status_code != 200:
            return _resultado(
                self.nome,
                ProviderStatus.ERROR,
                "provider_http_error",
                inicio,
            )

        try:
            payload = resposta.json()
        except ValueError:
            return _resultado(
                self.nome,
                ProviderStatus.ERROR,
                "provider_invalid_json",
                inicio,
            )

        if not isinstance(payload, dict) or not _payload_compativel(payload, cnpj):
            return _resultado(
                self.nome,
                ProviderStatus.ERROR,
                "provider_invalid_payload",
                inicio,
            )

        return CadastroProviderResult(
            provider=self.nome,
            status=ProviderStatus.OK,
            source_data=_mapear_payload(payload),
            latency_ms=_latencia(inicio),
        )

    async def _aguardar_retry(self) -> None:
        if self.retry_backoff_seconds:
            await asyncio.sleep(self.retry_backoff_seconds)


def _resultado(
    provider: str,
    status: ProviderStatus,
    error_code: str,
    inicio: float,
) -> CadastroProviderResult:
    return CadastroProviderResult(
        provider=provider,
        status=status,
        source_data={},
        error_code=error_code,
        latency_ms=_latencia(inicio),
    )


def _latencia(inicio: float) -> int:
    return round((perf_counter() - inicio) * 1000)


def _payload_compativel(payload: dict[str, Any], cnpj: str) -> bool:
    if not {"razao_social", "descricao_situacao_cadastral"}.issubset(payload):
        return False
    payload_cnpj = payload.get("cnpj")
    if payload_cnpj is None:
        return True
    if not isinstance(payload_cnpj, str):
        return False
    return _normalizar_identificador(payload_cnpj) == _normalizar_identificador(cnpj)


def _normalizar_identificador(valor: str) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", valor).upper()


def _mapear_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "legal_name": payload.get("razao_social"),
        "opening_date": payload.get("data_inicio_atividade"),
        "registration_status": payload.get("descricao_situacao_cadastral"),
        "registration_status_date": payload.get("data_situacao_cadastral"),
        "registration_status_reason": payload.get(
            "descricao_motivo_situacao_cadastral"
        ),
        "simple_national": payload.get("opcao_pelo_simples"),
        "simei": payload.get("opcao_pelo_mei"),
    }
