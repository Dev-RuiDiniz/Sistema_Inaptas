from types import SimpleNamespace

from inaptas.interfaces.http.schemas import ComplianceData, FiscalResponse, SanctionRecord
from inaptas.interfaces.panel.templates import renderizar_template


def test_renderiza_pagina_base_com_identidade_do_painel() -> None:
    html = renderizar_template(
        "painel/login.html",
        titulo="Acesso do escritório",
        mensagem="Entre para consultar evidências fiscais.",
    )

    assert "Acesso do escritório" in html
    assert "Entre para consultar evidências fiscais." in html
    assert "Sistema Inaptas" in html


def test_template_nao_renderiza_token_de_contexto() -> None:
    html = renderizar_template(
        "painel/login.html",
        titulo="Acesso",
        mensagem="teste",
        internal_api_token="segredo-que-nao-pode-aparecer",
    )

    assert "segredo-que-nao-pode-aparecer" not in html


def test_detalhe_exibe_registros_e_fonte_indisponivel_sem_regularidade() -> None:
    resposta = FiscalResponse(
        cnpj="11222333000181",
        compliance=ComplianceData(
            sanctions_found=True,
            records=[SanctionRecord(dataset="CEIS", id=1, sanction_type="Impedimento")],
        ),
    )
    consulta = SimpleNamespace(cnpj="11222333000181", id="consulta")

    html = renderizar_template("painel/detalhe_consulta.html", resposta=resposta, consulta=consulta)

    assert "1 registros encontrados" in html
    assert "CEIS" in html
    assert "empresa regular" not in html.lower()
