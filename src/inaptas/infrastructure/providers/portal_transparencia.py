from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import perf_counter
from typing import Any, cast

import httpx

from inaptas.domain.models import ComplianceProviderResult, ProviderStatus


@dataclass
class _ResultadoDataset:
    concluido: bool
    registros: list[dict[str, Any]]
    status: ProviderStatus = ProviderStatus.OK
    error_code: str | None = None


class PortalTransparenciaProvider:
    nome = "PORTAL_TRANSPARENCIA"

    def __init__(
        self,
        base_url: str,
        api_token: str,
        timeout_seconds: float = 5.0,
        max_retries: int = 2,
        max_pages: int = 10,
        retry_backoff_seconds: float = 0.1,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.max_pages = max(1, max_pages)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

    async def consultar(self, cnpj: str) -> ComplianceProviderResult:
        inicio = perf_counter()
        if not self.api_token:
            return self._resultado(
                ProviderStatus.ERROR, "provider_token_missing", inicio
            )

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            follow_redirects=False,
            headers={
                "Accept": "application/json",
                "chave-api-dados": self.api_token,
            },
        ) as cliente:
            resultados = await asyncio.gather(
                self._consultar_dataset(
                    cliente, "CEIS", "/ceis", "codigoSancionado", cnpj
                ),
                self._consultar_dataset(
                    cliente, "CNEP", "/cnep", "codigoSancionado", cnpj
                ),
                self._consultar_dataset(
                    cliente, "CEPIM", "/cepim", "cnpjSancionado", cnpj
                ),
            )

        falha = next((resultado for resultado in resultados if not resultado.concluido), None)
        if falha is not None:
            return self._resultado(falha.status, falha.error_code, inicio)

        registros = [
            registro
            for resultado in resultados
            for registro in resultado.registros
        ]
        return self._resultado(
            ProviderStatus.OK,
            None,
            inicio,
            source_data={
                "sanctions_found": bool(registros),
                "records": registros,
                "datasets": ["CEIS", "CNEP", "CEPIM"],
            },
        )

    async def _consultar_dataset(
        self,
        cliente: httpx.AsyncClient,
        dataset: str,
        caminho: str,
        parametro_cnpj: str,
        cnpj: str,
    ) -> _ResultadoDataset:
        registros: list[dict[str, Any]] = []
        for pagina in range(1, self.max_pages + 1):
            resposta = await self._obter_pagina(
                cliente, caminho, parametro_cnpj, cnpj, pagina
            )
            if isinstance(resposta, _ResultadoDataset):
                return resposta
            if not isinstance(resposta, list):
                return _ResultadoDataset(
                    False, [], ProviderStatus.ERROR, "provider_invalid_payload"
                )
            if not resposta:
                return _ResultadoDataset(True, registros)
            for item in resposta:
                if not isinstance(item, dict):
                    return _ResultadoDataset(
                        False, [], ProviderStatus.ERROR, "provider_invalid_payload"
                    )
                registro = self._mapear_registro(dataset, item)
                if registro is None:
                    return _ResultadoDataset(
                        False, [], ProviderStatus.ERROR, "provider_invalid_payload"
                    )
                registros.append(registro)
        return _ResultadoDataset(
            False, [], ProviderStatus.ERROR, "provider_incomplete_response"
        )

    async def _obter_pagina(
        self,
        cliente: httpx.AsyncClient,
        caminho: str,
        parametro_cnpj: str,
        cnpj: str,
        pagina: int,
    ) -> list[Any] | dict[str, Any] | _ResultadoDataset:
        tentativas = 0
        while True:
            try:
                resposta = await cliente.get(
                    caminho,
                    params={parametro_cnpj: cnpj, "pagina": pagina},
                )
            except httpx.TimeoutException:
                if tentativas < self.max_retries:
                    tentativas += 1
                    await self._aguardar_retry(tentativas)
                    continue
                return _ResultadoDataset(
                    False, [], ProviderStatus.UNAVAILABLE, "provider_timeout"
                )
            except httpx.RequestError:
                if tentativas < self.max_retries:
                    tentativas += 1
                    await self._aguardar_retry(tentativas)
                    continue
                return _ResultadoDataset(
                    False, [], ProviderStatus.UNAVAILABLE, "provider_connection_error"
                )

            if resposta.status_code == 200:
                try:
                    return cast(list[Any] | dict[str, Any], resposta.json())
                except ValueError:
                    return _ResultadoDataset(
                        False, [], ProviderStatus.ERROR, "provider_invalid_json"
                    )
            if resposta.status_code in {429, *range(500, 600)}:
                if tentativas < self.max_retries:
                    tentativas += 1
                    await self._aguardar_retry(tentativas)
                    continue
                return _ResultadoDataset(
                    False, [], ProviderStatus.UNAVAILABLE, "provider_unavailable"
                )
            if resposta.status_code in {401, 403}:
                return _ResultadoDataset(
                    False, [], ProviderStatus.ERROR, "provider_unauthorized"
                )
            if resposta.status_code in {400, 422}:
                return _ResultadoDataset(
                    False, [], ProviderStatus.ERROR, "provider_invalid_request"
                )
            return _ResultadoDataset(
                False, [], ProviderStatus.ERROR, "provider_http_error"
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
    ) -> ComplianceProviderResult:
        return ComplianceProviderResult(
            provider=self.nome,
            status=status,
            source_data=source_data or {},
            error_code=error_code,
            latency_ms=int((perf_counter() - inicio) * 1000),
        )

    @staticmethod
    def _mapear_registro(dataset: str, item: dict[str, Any]) -> dict[str, Any] | None:
        identificador = item.get("id")
        if not isinstance(identificador, int) or isinstance(identificador, bool):
            return None
        if dataset == "CEPIM":
            pessoa = item.get("pessoaJuridica")
            orgao = item.get("orgaoSuperior")
            if not isinstance(pessoa, dict) or not isinstance(orgao, dict):
                return None
            return {
                "dataset": dataset,
                "id": identificador,
                "reference_date": item.get("dataReferencia"),
                "sanctioned_name": pessoa.get("nome")
                or pessoa.get("razaoSocialReceita")
                or pessoa.get("nomeFantasiaReceita"),
                "sanctioned_document": pessoa.get("cnpjFormatado"),
                "authority_name": orgao.get("nome"),
                "reason": item.get("motivo"),
            }

        sancao = item.get("tipoSancao")
        sancionado = item.get("sancionado")
        pessoa = item.get("pessoa")
        orgao = item.get("orgaoSancionador")
        if not isinstance(sancao, dict) or not isinstance(orgao, dict):
            return None
        if not isinstance(sancionado, dict) and not isinstance(pessoa, dict):
            return None
        sancionado = sancionado if isinstance(sancionado, dict) else {}
        pessoa = pessoa if isinstance(pessoa, dict) else {}
        return {
            "dataset": dataset,
            "id": identificador,
            "reference_date": item.get("dataReferencia"),
            "start_date": item.get("dataInicioSancao"),
            "end_date": item.get("dataFimSancao"),
            "publication_date": item.get("dataPublicacaoSancao"),
            "sanction_type": sancao.get("descricaoPortal")
            or sancao.get("descricaoResumida"),
            "sanctioned_name": sancionado.get("nome")
            or pessoa.get("nome")
            or pessoa.get("razaoSocialReceita"),
            "sanctioned_document": sancionado.get("codigoFormatado")
            or pessoa.get("cnpjFormatado"),
            "authority_name": orgao.get("nome"),
            "authority_uf": orgao.get("siglaUf"),
            "process_number": item.get("numeroProcesso"),
            "publication_url": item.get("linkPublicacao"),
            "fine_amount": (
                str(item["valorMulta"]) if item.get("valorMulta") is not None else None
            ),
        }
