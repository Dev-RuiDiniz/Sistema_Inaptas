from __future__ import annotations

import csv
from io import BytesIO, StringIO

from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.pdfgen.canvas import Canvas  # type: ignore[import-untyped]

from inaptas.infrastructure.persistence.models import Consultation
from inaptas.interfaces.http.schemas import FiscalResponse


def _linhas(consulta: Consultation, resposta: FiscalResponse) -> list[tuple[str, str]]:
    fontes = "; ".join(
        f"{fonte.provider}: {fonte.status} ({fonte.latency_ms or '—'} ms)"
        for fonte in resposta.sources
    )
    if resposta.compliance.sanctions_found is True:
        resumo_compliance = f"{len(resposta.compliance.records)} registros encontrados"
    elif resposta.compliance.sanctions_found is False:
        resumo_compliance = "Nenhum registro localizado"
    else:
        resumo_compliance = "Fonte indisponível ou consulta inconclusiva"
    linhas = [
        ("CNPJ", resposta.cnpj),
        ("Razão social", resposta.company.legal_name or "Não informado"),
        ("Situação cadastral", resposta.company.registration_status or "Não informado"),
        ("Motivo cadastral", resposta.company.registration_status_reason or "Não informado"),
        ("Diagnóstico cadastral", resposta.system_diagnosis.registration),
        ("Diagnóstico PGFN", resposta.system_diagnosis.pgfn),
        ("Registros de compliance", resumo_compliance),
        ("Fontes", fontes or "Nenhuma fonte registrada"),
        ("Consultada em", str(consulta.completed_at or consulta.requested_at)),
    ]
    campos = (
        ("dataset", "Dataset"),
        ("id", "ID"),
        ("reference_date", "Data de referência"),
        ("start_date", "Início"),
        ("end_date", "Fim"),
        ("publication_date", "Publicação"),
        ("sanction_type", "Tipo de sanção"),
        ("sanctioned_name", "Nome sancionado"),
        ("sanctioned_document", "Documento sancionado"),
        ("authority_name", "Órgão sancionador"),
        ("authority_uf", "UF do órgão"),
        ("process_number", "Processo"),
        ("publication_url", "Publicação oficial"),
        ("fine_amount", "Valor da multa"),
        ("reason", "Motivo"),
    )
    for indice, registro in enumerate(resposta.compliance.records, start=1):
        for campo, rotulo in campos:
            valor = getattr(registro, campo)
            if valor is not None:
                linhas.append((f"Registro {indice} — {rotulo}", str(valor)))
    return linhas


def gerar_csv(consulta: Consultation, resposta: FiscalResponse) -> bytes:
    arquivo = StringIO(newline="")
    escritor = csv.writer(arquivo)
    escritor.writerow(("campo", "valor"))
    escritor.writerows(_linhas(consulta, resposta))
    return ("\ufeff" + arquivo.getvalue()).encode("utf-8")


def gerar_pdf(consulta: Consultation, resposta: FiscalResponse) -> bytes:
    arquivo = BytesIO()
    pdf = Canvas(arquivo, pagesize=A4)
    pdf.setTitle(f"Relatório fiscal {resposta.cnpj}")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(48, 790, "Sistema Inaptas — Relatório fiscal")
    y = 758
    pdf.setFont("Helvetica", 10)
    for nome, valor in _linhas(consulta, resposta):
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(48, y, f"{nome}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(170, y, valor[:105])
        y -= 20
        if y < 60:
            pdf.showPage()
            y = 790
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(
        48,
        42,
        "Relatório baseado no contrato normalizado; indisponibilidades são preservadas.",
    )
    pdf.save()
    return arquivo.getvalue()
