import pytest

from inaptas.domain.cnpj import CnpjInvalidoError, normalizar_cnpj, validar_cnpj


def test_normaliza_cnpj_numerico_com_mascara() -> None:
    assert normalizar_cnpj("11.222.333/0001-81") == "11222333000181"


def test_rejeita_cnpj_numerico_com_digito_invalido() -> None:
    with pytest.raises(CnpjInvalidoError):
        normalizar_cnpj("11.222.333/0001-80")


def test_valida_cnpj_alfanumerico_oficial() -> None:
    assert validar_cnpj("12ABC34501DE35") is True
    assert normalizar_cnpj("12abc34501de35") == "12ABC34501DE35"


def test_rejeita_cnpj_alfanumerico_com_digito_invalido() -> None:
    assert validar_cnpj("12ABC34501DE36") is False


@pytest.mark.parametrize("valor", ["", "123", "12ABC34501DE3A", "00000000000000", "12ABC34501DE!5"])
def test_rejeita_formatos_invalidos(valor: str) -> None:
    assert validar_cnpj(valor) is False
