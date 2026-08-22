from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import httpx

_AFIRMACOES_REGULARIDADE = re.compile(
    r"\b(regular|sem pend[eê]ncia|sem d[ií]vida|nenhuma pend[eê]ncia|sem irregularidade)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InterpretationResult:
    status: str
    text: str
    error_code: str | None = None


def interpretar_com_fallback(contexto: dict[str, Any]) -> str:
    diagnostico = contexto.get("system_diagnosis") or {}
    registro = diagnostico.get("registration", "UNKNOWN")
    pgfn = diagnostico.get("pgfn", "UNKNOWN_SOURCE_UNAVAILABLE")

    partes: list[str] = []
    if registro == "ACTIVE":
        partes.append("A fonte cadastral retornou situação ativa.")
    elif registro == "INACTIVE":
        partes.append("A fonte cadastral retornou situação diferente de ativa.")
    else:
        partes.append("A situação cadastral não pôde ser confirmada pela fonte disponível.")

    if pgfn == "ACTIVE_DEBT_RETURNED_BY_SOURCE":
        partes.append("A fonte PGFN retornou dívida ativa.")
    elif pgfn == "NO_ACTIVE_DEBT_RETURNED_BY_SOURCE":
        partes.append("A fonte PGFN não retornou dívida ativa na consulta.")
    else:
        partes.append("A situação na PGFN não pôde ser confirmada pela fonte disponível.")

    partes.append(
        "A interpretação automática está indisponível; consulte as evidências "
        "e os status das fontes."
    )
    return " ".join(partes)


def _evidencia_permite_afirmacao_de_regularidade(contexto: dict[str, Any]) -> bool:
    diagnostico = contexto.get("system_diagnosis") or {}
    return diagnostico.get("registration") == "ACTIVE" and diagnostico.get("pgfn") == (
        "NO_ACTIVE_DEBT_RETURNED_BY_SOURCE"
    )


def _resposta_segura(texto: str, contexto: dict[str, Any]) -> str | None:
    if _AFIRMACOES_REGULARIDADE.search(texto) and not _evidencia_permite_afirmacao_de_regularidade(
        contexto
    ):
        return None
    return texto.strip() or None


class OllamaClient:
    """Cliente opcional para interpretação textual baseada no contrato canônico."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def interpretar(self, contexto: dict[str, Any]) -> InterpretationResult:
        fallback = interpretar_com_fallback(contexto)
        if not self.base_url or not self.model:
            return InterpretationResult("fallback", fallback, "integration_not_configured")

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds, follow_redirects=False
            ) as cliente:
                resposta = await cliente.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": self._prompt(contexto),
                        "stream": False,
                    },
                )
        except httpx.TimeoutException:
            return InterpretationResult("fallback", fallback, "integration_timeout")
        except httpx.RequestError:
            return InterpretationResult("fallback", fallback, "integration_connection_error")

        if resposta.status_code >= 500 or resposta.status_code == 429:
            return InterpretationResult("fallback", fallback, "integration_unavailable")
        if not resposta.is_success:
            return InterpretationResult("fallback", fallback, "integration_http_error")

        corpo = resposta.json()
        texto = corpo.get("response") if isinstance(corpo, dict) else None
        if not isinstance(texto, str):
            return InterpretationResult("fallback", fallback, "invalid_response")
        texto_seguro = _resposta_segura(texto, contexto)
        if texto_seguro is None:
            return InterpretationResult("fallback", fallback, "unsafe_interpretation")
        return InterpretationResult("ok", texto_seguro)

    def _prompt(self, contexto: dict[str, Any]) -> str:
        return (
            "Explique somente os dados do contrato canônico abaixo. "
            "Não invente situação fiscal, dívida, regime ou regularidade. "
            "Quando uma fonte estiver UNKNOWN, unavailable ou disabled, "
            "diga que não foi possível confirmar. "
            "Responda em português do Brasil, de forma breve, sem credenciais "
            "e sem dados além do contexto.\n\n"
            f"CONTRATO_CANONICO={contexto}"
        )
