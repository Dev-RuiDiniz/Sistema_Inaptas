from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from inaptas.infrastructure.persistence.models import Consultation, ConsultationResult


class PainelDashboardService:
    async def resumo(self, session: AsyncSession, organization_id: str) -> dict[str, Any]:
        registros_resultado = await session.execute(
            select(ConsultationResult).where(ConsultationResult.organization_id == organization_id)
        )
        registros = list(registros_resultado.scalars())
        ids = [registro.consultation_id for registro in registros]
        consultas_resultado = await session.execute(
            select(Consultation)
            .where(
                Consultation.organization_id == organization_id,
                Consultation.id.in_(ids),
            )
            .order_by(Consultation.requested_at.desc())
        )
        consultas = list(consultas_resultado.scalars())
        por_id = {consulta.id: consulta for consulta in consultas}
        diagnosticos: Counter[str] = Counter()
        fontes: Counter[str] = Counter()
        erros_recentes: list[dict[str, str]] = []
        for registro in registros:
            consulta = por_id.get(registro.consultation_id)
            if consulta is None:
                continue
            dados = registro.normalized_response
            diagnostico = dados.get("system_diagnosis", {})
            if isinstance(diagnostico, dict):
                diagnosticos[str(diagnostico.get("registration", "UNKNOWN"))] += 1
            fontes_data = dados.get("sources", [])
            if isinstance(fontes_data, list):
                for fonte in fontes_data:
                    if isinstance(fonte, dict):
                        status = str(fonte.get("status", "unknown"))
                        fontes[status] += 1
                        if status in {"unavailable", "error"} and len(erros_recentes) < 10:
                            erros_recentes.append(
                                {
                                    "cnpj": consulta.cnpj,
                                    "provider": str(fonte.get("provider", "")),
                                    "status": status,
                                }
                            )
        return {
            "total": len(consultas),
            "diagnosticos": dict(diagnosticos),
            "fontes": dict(fontes),
            "erros_recentes": erros_recentes,
            "ultima_consulta": consultas[0].requested_at if consultas else None,
        }
