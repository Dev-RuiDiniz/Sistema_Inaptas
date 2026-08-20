import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from inaptas.infrastructure.persistence.models import Base
from inaptas.infrastructure.persistence.repositories import AuditRepository


@pytest.mark.asyncio
async def test_persiste_consulta_e_auditoria() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)

    sessoes = async_sessionmaker(engine, expire_on_commit=False)
    async with sessoes() as sessao:
        repositorio = AuditRepository(sessao)
        consulta = await repositorio.criar_consulta(
            correlation_id="correlacao-teste",
            cnpj="11222333000181",
            request_type="lookup",
        )
        await repositorio.registrar_api_audit(
            consultation_id=consulta.id,
            provider="RECEITAWS",
            endpoint_alias="consulta_cnpj",
            http_status=200,
            latency_ms=42,
        )

    assert consulta.cnpj == "11222333000181"
    assert consulta.requested_at.tzinfo is not None
    await engine.dispose()
