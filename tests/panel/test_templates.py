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
