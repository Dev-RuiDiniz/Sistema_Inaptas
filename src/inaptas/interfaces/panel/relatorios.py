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
    return [
        ("CNPJ", resposta.cnpj),
        ("Razão social", resposta.company.legal_name or "Não informado"),
        ("Situação cadastral", resposta.company.registration_status or "Não informado"),
        ("Motivo cadastral", resposta.company.registration_status_reason or "Não informado"),
        ("Diagnóstico cadastral", resposta.system_diagnosis.registration),
        ("Diagnóstico PGFN", resposta.system_diagnosis.pgfn),
        ("Fontes", fontes or "Nenhuma fonte registrada"),
        ("Consultada em", str(consulta.completed_at or consulta.requested_at)),
    ]


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
