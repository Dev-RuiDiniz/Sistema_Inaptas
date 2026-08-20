from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.persistence.models import Base, Organization, PanelUser
from inaptas.interfaces.http.schemas import FiscalResponse, ProviderSource
from inaptas.interfaces.panel.auth import PainelSession
from inaptas.interfaces.panel.consultas import PainelConsultaService


class GatewayFalso:
    async def consulta_completa(self, cnpj: str) -> FiscalResponse:
        return FiscalResponse(
            cnpj=cnpj,
            company={"legal_name": "Empresa Teste", "registration_status": "ATIVA"},
            sources=[ProviderSource(provider="receitaws", status=ProviderStatus.OK)],
            generated_at=datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_consulta_do_painel_persiste_somente_contrato_normalizado() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with fabrica() as session:
        session.add(Organization(id="org", name="Escritório", retention_days=90))
        session.add(
            PanelUser(
                id="user",
                organization_id="org",
                oidc_subject="sub",
                email="contato@exemplo.test",
                name="Contador",
                role="admin",
                status="active",
                email_verified=True,
            )
        )
        await session.commit()
        painel = PainelSession(
            "sessao", "user", "org", "admin", "contato@exemplo.test", "Contador", "csrf"
        )
        consulta, resposta = await PainelConsultaService(GatewayFalso()).consultar(
            session, "11.222.333/0001-81", painel, "correlacao"
        )
        registro = await PainelConsultaService(GatewayFalso()).obter(session, consulta.id, "org")

    assert resposta.company.legal_name == "Empresa Teste"
    assert registro is not None
    assert registro[1].cnpj == "11222333000181"
    await engine.dispose()
