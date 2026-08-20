from __future__ import annotations

import re


class CnpjInvalidoError(ValueError):
    """Indica que uma inscrição CNPJ não respeita o formato ou os DVs oficiais."""


_CARACTERES_PERMITIDOS = re.compile(r"^[A-Z0-9]{14}$")
_PESOS_PRIMEIRO_DV = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_SEGUNDO_DV = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def _calcular_digito(base: str, pesos: tuple[int, ...]) -> int:
    soma = sum((ord(caractere) - 48) * peso for caractere, peso in zip(base, pesos, strict=True))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def _validar_digitos(cnpj: str) -> bool:
    base = cnpj[:12]
    primeiro = _calcular_digito(base, _PESOS_PRIMEIRO_DV)
    segundo = _calcular_digito(base + str(primeiro), _PESOS_SEGUNDO_DV)
    return cnpj[-2:] == f"{primeiro}{segundo}"


def normalizar_cnpj(valor: str) -> str:
    if not isinstance(valor, str):
        raise CnpjInvalidoError("O CNPJ deve ser informado como texto.")

    cnpj = valor.strip().upper()
    for separador in (".", "/", "-", " "):
        cnpj = cnpj.replace(separador, "")

    if not _CARACTERES_PERMITIDOS.fullmatch(cnpj):
        raise CnpjInvalidoError("O CNPJ possui caracteres inválidos.")
    if cnpj[:12].isalnum() is False or not cnpj[-2:].isdigit():
        raise CnpjInvalidoError("O CNPJ possui formato inválido.")
    if len(set(cnpj)) == 1:
        raise CnpjInvalidoError("O CNPJ não pode ser uma sequência repetida.")
    if not _validar_digitos(cnpj):
        raise CnpjInvalidoError("Os dígitos verificadores do CNPJ são inválidos.")
    return cnpj


def validar_cnpj(valor: str) -> bool:
    try:
        normalizar_cnpj(valor)
    except CnpjInvalidoError:
        return False
    return True
