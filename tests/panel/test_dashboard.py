from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from inaptas.infrastructure.persistence.models import (
    Base,
    Consultation,
    ConsultationResult,
    Organization,
)
from inaptas.interfaces.panel.dashboard import PainelDashboardService


@pytest.mark.asyncio
async def test_dashboard_contabiliza_indisponibilidade_sem_inferir_regularidade() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with fabrica() as session:
        session.add(Organization(id="org", name="Escritório", retention_days=90))
        session.add(
            Consultation(
                id="consulta",
                correlation_id="correlacao",
                cnpj="11222333000181",
                request_type="full-check",
                status="completed",
                requested_at=datetime.now(UTC),
                organization_id="org",
                origin="panel",
            )
        )
        session.add(
            ConsultationResult(
                consultation_id="consulta",
                organization_id="org",
                normalized_response={
                    "system_diagnosis": {"registration": "UNKNOWN"},
                    "sources": [{"provider": "pgfn", "status": "unavailable"}],
                },
            )
        )
        await session.commit()
        resumo = await PainelDashboardService().resumo(session, "org")
    await engine.dispose()

    assert resumo["diagnosticos"] == {"UNKNOWN": 1}
    assert resumo["fontes"] == {"unavailable": 1}
    assert resumo["erros_recentes"][0]["status"] == "unavailable"
