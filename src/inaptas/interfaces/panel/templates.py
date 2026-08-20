from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.templating import Jinja2Templates

_DIRETORIO_TEMPLATES = Path(__file__).parent / "templates"
_CHAVES_SENSIVEIS = {"token", "secret", "password", "api_key", "client_secret"}


def criar_templates() -> Jinja2Templates:
    return Jinja2Templates(directory=str(_DIRETORIO_TEMPLATES))


def renderizar_template(nome: str, **contexto: Any) -> str:
    contexto_seguro = {
        chave: valor
        for chave, valor in contexto.items()
        if not any(palavra in chave.lower() for palavra in _CHAVES_SENSIVEIS)
    }
    return str(criar_templates().get_template(nome).render(**contexto_seguro))
