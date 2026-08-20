from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from inaptas.infrastructure.persistence.models import ApiAudit, Consultation


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def criar_consulta(
        self,
        *,
        correlation_id: str,
        cnpj: str,
        request_type: str,
        source: str | None = None,
        whatsapp_contact_hash: str | None = None,
    ) -> Consultation:
        consulta = Consultation(
            correlation_id=correlation_id,
            cnpj=cnpj,
            source=source,
            request_type=request_type,
            whatsapp_contact_hash=whatsapp_contact_hash,
        )
        self.session.add(consulta)
        await self.session.flush()
        await self.session.commit()
        return consulta

    async def finalizar_consulta(
        self,
        consulta: Consultation,
        *,
        status: str,
        response_hash: str | None = None,
        error_code: str | None = None,
        completed_at: datetime | None = None,
    ) -> Consultation:
        consulta.status = status
        consulta.response_hash = response_hash
        consulta.error_code = error_code
        consulta.completed_at = completed_at
        await self.session.flush()
        await self.session.commit()
        return consulta

    async def registrar_api_audit(
        self,
        *,
        consultation_id: str,
        provider: str,
        endpoint_alias: str,
        http_status: int | None,
        latency_ms: int | None,
        error_code: str | None = None,
    ) -> ApiAudit:
        auditoria = ApiAudit(
            consultation_id=consultation_id,
            provider=provider,
            endpoint_alias=endpoint_alias,
            http_status=http_status,
            latency_ms=latency_ms,
            error_code=error_code,
        )
        self.session.add(auditoria)
        await self.session.flush()
        await self.session.commit()
        return auditoria
