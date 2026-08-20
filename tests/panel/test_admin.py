import pytest
from fastapi import HTTPException

from inaptas.interfaces.panel.admin import validar_ultimo_administrador


def test_bloqueia_remocao_do_ultimo_administrador() -> None:
    with pytest.raises(HTTPException) as erro:
        validar_ultimo_administrador(1)
    assert erro.value.status_code == 409


def test_permite_alteracao_quando_existe_outro_administrador() -> None:
    validar_ultimo_administrador(2)
