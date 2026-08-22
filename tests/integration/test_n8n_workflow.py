from __future__ import annotations

import json
from pathlib import Path

WORKFLOW = Path("deploy/n8n/workflows/inaptas-whatsapp.json")


def test_workflow_n8n_exportado_tem_fluxo_validado_e_fallback() -> None:
    workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    nomes = {node["name"] for node in workflow["nodes"]}

    assert "Webhook interno validado" in nomes
    assert "Consultar Fiscal Gateway" in nomes
    assert "Interpretação opcional Ollama" in nomes
    assert "Fallback determinístico seguro" in nomes
    webhook = next(node for node in workflow["nodes"] if node["name"] == "Webhook interno validado")
    assert webhook["parameters"]["authentication"] == "headerAuth"
    assert webhook["credentials"]["httpHeaderAuth"]["name"] == "Inaptas Webhook Interno"
    gateway = next(node for node in workflow["nodes"] if node["name"] == "Consultar Fiscal Gateway")
    assert gateway["credentials"]["httpHeaderAuth"]["name"] == "Inaptas Gateway Orquestrador"
    assert "regularidade" in json.dumps(workflow, ensure_ascii=False)
    assert workflow["active"] is False


def test_runtime_e_configuracao_usam_n8n() -> None:
    arquivos = [*Path("src").rglob("*.py"), Path(".env.example")]
    conteudo = "\n".join(arquivo.read_text(encoding="utf-8") for arquivo in arquivos)

    assert "N8nClient" in conteudo
    assert "N8N_INTERNAL_WEBHOOK_URL" in conteudo
    assert "ORCHESTRATOR_API_TOKEN" in conteudo
