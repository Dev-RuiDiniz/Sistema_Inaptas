# Implantação do n8n self-hosted em VPS

## Topologia de referência

Use uma VPS Linux com aproximadamente 4 vCPU, 16 GB de RAM e pelo menos 180 GB
de armazenamento dedicado para o Minha Receita, além da margem operacional do
Gateway, n8n, PostgreSQL, Redis e Ollama. A previsão anterior de 80 GB não
atende à carga inicial do snapshot. Dimensione CPU, RAM e armazenamento depois
de medir o modelo local e o tempo da carga mensal. O Compose mantém o
Gateway/painel, PostgreSQL/Redis do Gateway, n8n, PostgreSQL próprio do n8n,
Minha Receita, PostgreSQL dedicado do provider, Ollama e Caddy em serviços
separados.

```text
painel.seudominio
  → Caddy/TLS → Gateway FastAPI + painel

n8n.seudominio
  → Caddy/TLS → n8n administrativo

Rede Docker interna: Gateway ↔ Minha Receita ↔ PostgreSQL do provider
                     Gateway ↔ n8n ↔ Ollama
PostgreSQL, Redis e API do provider sem publicação externa
```

O n8n não é o painel comercial e não deve ser aberto ao cliente final. Use
firewall permitindo apenas SSH restrito, HTTP/HTTPS para o Caddy e, quando
necessário, uma rede privada para administração.

## Preparação segura

1. Instale Docker Engine e Compose em Ubuntu/Debian atualizado.
2. Crie um usuário operacional sem login root e restrinja SSH por chave.
3. Clone o repositório em diretório próprio da aplicação.
4. Crie `.env` a partir de `.env.example` e substitua todos os placeholders por
   secrets fornecidos por secret manager ou mecanismo seguro do provedor.
5. Configure `PANEL_HOST`, `N8N_HOST`, `N8N_EDITOR_BASE_URL` e `WEBHOOK_URL` com
   domínios reais apontando para a VPS.
6. Configure `N8N_ENCRYPTION_KEY` estável; perdê-la impede a leitura das
   credenciais armazenadas pelo n8n.

Não publique PostgreSQL, Redis ou Ollama. Não coloque tokens, certificados,
cookies, CNPJ real ou payload fiscal neste repositório.

## Subida e workflow

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Depois:

1. Acesse o domínio administrativo do n8n somente pela rede autorizada.
2. Crie as credenciais de header para o webhook interno e para o
   `ORCHESTRATOR_API_TOKEN`; os valores vêm do secret manager.
3. Importe `deploy/n8n/workflows/inaptas-whatsapp.json`.
4. Configure a credencial do webhook com o nome usado no workflow e valide o
   endpoint antes de ativar.
5. Configure o token de WhatsApp apenas na credencial/ambiente operacional do
   n8n, sem salvá-lo no JSON exportado.
6. Baixe o modelo local com `docker compose exec ollama ollama pull qwen3:8b`.
7. Fixe `MINHA_RECEITA_IMAGE` em uma versão ou digest validado; `main` é apenas
   um padrão de desenvolvimento e `latest` não é permitido em produção.
8. Carregue os dados mensalmente conforme o [guia oficial de atualização](https://docs.minhareceita.org/servidor/passo-a-passo/), usando o serviço manual
   `minha-receita-sync`. Reserve aproximadamente 180 GB para o processo e
   valide a saúde de `minha-receita` depois da transformação.
9. Ative o workflow somente após testar assinatura, idempotência, consulta e
   fallback.

## Backups, retenção e auditoria

Faça backup criptografado e testado de:

- PostgreSQL do Gateway;
- PostgreSQL do n8n;
- volumes do n8n, quando a política exigir;
- volume do Ollama, se o custo de rebaixar o modelo for relevante;
- `.env` em secret manager, nunca no Git.

Mantenha `N8N_ENCRYPTION_KEY`, pruning de execuções e idade máxima configurados.
Não persista payloads sensíveis em nós de sucesso sem finalidade e retenção
definidas. Execute a auditoria do n8n e corrija webhooks desprotegidos, nós
arriscados, credenciais sem uso e configurações inseguras antes da exposição.

## Saúde e reversão

Verifique `/health` do Gateway, `docker compose ps`, logs redigidos e o healthz
do n8n. Falha do n8n, Ollama ou Minha Receita deve aparecer como
indisponibilidade; nunca como regularidade fiscal. Para reverter, altere
`CADASTRO_PROVIDER` explicitamente para `receitaws` ou mantenha a fonte
indisponível, desative o workflow e não apague volumes antes de confirmar o
backup.

Queue mode, workers adicionais e alta disponibilidade são etapas futuras e
exigem nova spec, dimensionamento e teste de carga.
