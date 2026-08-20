# Memória persistida — Sistema Inaptas

> Este arquivo guarda contexto operacional para que agentes retomem o trabalho sem perder decisões. Não armazene segredos, tokens, certificados, dados fiscais reais ou credenciais aqui.

## Estado atual

- **Data da última atualização:** 20/08/2026.
- **Produto:** Inaptas.
- **Direção futura:** Regulariza.br modular.
- **Fase atual:** bootstrap documental concluído; Fase 0 aguardando validação de acessos externos.
- **Código de aplicação:** ainda não iniciado neste bootstrap.
- **Fonte de escopo:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`.
- **Repositório:** branch principal `main`, remoto `origin`.
- **Idioma obrigatório:** português do Brasil em documentação, specs, comentários, planos e commits.

## Decisões fechadas

1. O projeto usa Spec-Driven Development.
2. O `PRD.md` mantém a visão do produto e cada incremento terá uma spec em `specs/` antes do código.
3. O primeiro commit inclui governança, README, escopo técnico de origem e estrutura mínima de specs; não inclui backend ou infraestrutura de aplicação.
4. O bootstrap inicial será publicado diretamente em `main`, por autorização explícita do usuário.
5. Depois do bootstrap, mudanças de produto devem usar branches de trabalho e revisão antes de retornar a `main`.
6. O núcleo técnico será um Fiscal Gateway próprio, separado do Dify e de cada fornecedor.
7. O MVP precisa aceitar CNPJ numérico e alfanumérico como string.
8. A resposta separa `source_data`, `system_diagnosis` e `ai_interpretation`.
9. A IA não pode inferir situação fiscal, dívida, regime, pendência ou ausência de problema sem evidência válida.
10. SITFIS e ADE/Editais ficam preparados como extensões; bypass de CAPTCHA, scraping agressivo e automação de login no e-CAC não são permitidos.
11. Custos e acessos de SERPRO, APIs, certificado, servidor, WhatsApp, Dify, LLM e demais terceiros são responsabilidade do contratante, conforme o escopo técnico.

## Arquitetura de referência

```text
WhatsApp Business Cloud API
        ↓ webhook
API Gateway / Fiscal Gateway em FastAPI
        ↓
Dify para condução e explicação da conversa
        ↓
Conectores independentes (cadastro, SERPRO, PGFN, SITFIS futuro)
        ↓
Normalização + diagnóstico determinístico
        ↓
PostgreSQL (auditoria) + Redis (cache, tokens, rate limit)
```

O Dify nunca deve possuir diretamente todas as credenciais fiscais. O backend controla autenticação, timeout, retry, cache, rate limit, auditoria, normalização e mensagens seguras de indisponibilidade.

## Dependências externas

| Serviço | Uso | Situação no bootstrap |
|---|---|---|
| WhatsApp Business Cloud API | Recepção e envio de mensagens | A validar |
| Dify | Orquestração conversacional | A validar |
| ReceitaWS | Fonte cadastral alternativa para MVP | A validar |
| SERPRO Consulta CNPJ | Fonte cadastral oficial preferencial | A validar |
| SERPRO/PGFN | Dívida Ativa da União | A validar |
| Integra Contador/SITFIS | Situação fiscal protegida | Futuro, depende de contrato e autorização |

Nenhuma credencial deve ser registrada neste arquivo. O status de acesso deve ser atualizado como “disponível”, “indisponível” ou “bloqueado por terceiro”, sempre com evidência segura fora do Git.

## Próximo passo recomendado

1. Criar uma spec para a Fase 0 de validação dos acessos e do contrato mínimo do Fiscal Gateway.
2. Confirmar contas, responsáveis, titularidade e CNPJ de teste autorizado.
3. Só depois iniciar a primeira implementação de código.

## Regra de manutenção

- Atualizar esta memória ao concluir uma fase, fechar uma decisão, mudar uma dependência ou encontrar um bloqueio relevante.
- Registrar o estado atual e o próximo passo, não um diário de atividades.
- Remover contexto obsoleto ou marcar explicitamente decisões substituídas.
- Manter detalhes funcionais no `PRD.md` e detalhes de implementação na spec correspondente.
- Toda alteração relevante nesta memória deve ter commit em português.
