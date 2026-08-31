import re
from pathlib import Path


def test_compose_define_minha_receita_e_banco_dedicado_sem_portas_publicas() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "minha-receita:" in compose
    assert "minha-receita-postgres:" in compose
    assert "minha-receita-sync:" in compose
    assert "minha-receita_data:" in compose
    bloco_provider = re.search(
        r"(?ms)^  minha-receita:\r?\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", compose
    )
    bloco_banco = re.search(
        r"(?ms)^  minha-receita-postgres:\r?\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", compose
    )
    assert bloco_provider is not None
    assert bloco_banco is not None
    assert "ports:" not in bloco_provider.group(1)
    assert "ports:" not in bloco_banco.group(1)
