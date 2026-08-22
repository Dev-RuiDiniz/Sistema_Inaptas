from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from inaptas.application.services import FiscalGatewayService
from inaptas.domain.cnpj import normalizar_cnpj
from inaptas.infrastructure.persistence.models import Consultation, ConsultationResult, Organization
from inaptas.interfaces.http.schemas import FiscalResponse
from inaptas.interfaces.panel.auth import PainelSession


class PainelConsultaService:
    def __init__(self, gateway: FiscalGatewayService) -> None:
        self.gateway = gateway

    async def consultar(
        self, session: AsyncSession, cnpj: str, painel_session: PainelSession, correlation_id: str
    ) -> tuple[Consultation, FiscalResponse]:
        normalizado = normalizar_cnpj(cnpj)
        consulta = Consultation(
            id=str(uuid4()),
            correlation_id=correlation_id,
            cnpj=normalizado,
            request_type="full-check",
            status="started",
            requested_at=datetime.now(UTC),
            organization_id=painel_session.organization_id,
            requested_by_user_id=painel_session.user_id,
            origin="panel",
        )
        session.add(consulta)
        try:
            resposta = await self.gateway.consulta_completa(normalizado)
            dados = resposta.model_dump(mode="json")
            consulta.status = "completed"
            consulta.completed_at = datetime.now(UTC)
            consulta.response_hash = hashlib.sha256(
                json.dumps(dados, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            session.add(
                ConsultationResult(
                    consultation_id=consulta.id,
                    organization_id=painel_session.organization_id,
                    normalized_response=dados,
                )
            )
            await session.commit()
            await session.refresh(consulta)
            return consulta, resposta
        except Exception:
            consulta.status = "error"
            consulta.completed_at = datetime.now(UTC)
            await session.commit()
            raise

    async def obter(
        self, session: AsyncSession, consultation_id: str, organization_id: str
    ) -> tuple[Consultation, FiscalResponse] | None:
        resultado = await session.execute(
            select(Consultation, ConsultationResult)
            .join(ConsultationResult, ConsultationResult.consultation_id == Consultation.id)
            .where(
                Consultation.id == consultation_id,
                Consultation.organization_id == organization_id,
                ConsultationResult.organization_id == organization_id,
            )
        )
        linha = resultado.one_or_none()
        if linha is None:
            return None
        consulta, registro = linha
        return consulta, FiscalResponse.model_validate(registro.normalized_response)

    async def listar(
        self,
        session: AsyncSession,
        organization_id: str,
        cnpj: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Consultation], int]:
        filtros = [Consultation.organization_id == organization_id]
        if cnpj:
            filtros.append(Consultation.cnpj == normalizar_cnpj(cnpj))
        total = int(
            (await session.scalar(select(func.count(Consultation.id)).where(*filtros))) or 0
        )
        resultado = await session.execute(
            select(Consultation)
            .where(*filtros)
            .order_by(Consultation.requested_at.desc())
            .offset(max(page - 1, 0) * page_size)
            .limit(page_size)
        )
        return list(resultado.scalars()), total

    async def garantir_organizacao(
        self, session: AsyncSession, organization_id: str, name: str
    ) -> None:
        if await session.get(Organization, organization_id) is None:
            session.add(Organization(id=organization_id, name=name, retention_days=90))
            await session.commit()

    async def remover_expiradas(self, session: AsyncSession, organization_id: str) -> int:
        organizacao = await session.get(Organization, organization_id)
        if organizacao is None:
            return 0
        limite = datetime.now(UTC) - timedelta(days=organizacao.retention_days)
        resultado = await session.execute(
            delete(Consultation).where(
                Consultation.organization_id == organization_id,
                Consultation.requested_at < limite,
            )
        )
        await session.commit()
        return int(getattr(resultado, "rowcount", 0) or 0)
