# Roadmap — Sistema Inaptas

## Como acompanhar

Este documento acompanha a execução do produto. Cada item deve ser marcado somente depois de validado, e não apenas quando o código for escrito.

- `[ ]` pendente
- `[-]` em andamento
- `[x]` concluído
- `[!]` bloqueado por dependência ou decisão externa

Para cada fase, registre a data de conclusão, a evidência e os bloqueios relevantes. Mudanças de escopo devem passar por uma spec e atualizar o `PRD.md`.

## Visão do produto

O Inaptas é o primeiro módulo de uma arquitetura evolutiva para o Regulariza.br. Seu MVP recebe uma solicitação pelo WhatsApp, usa o Dify para conduzir a conversa, consulta o Fiscal Gateway e devolve dados fiscais/cadastrais normalizados, rastreáveis e sem inferências indevidas da IA.

## Marco 0 — Governança e base SDD

**Status:** concluído em 20/08/2026.

- [x] Criar `AGENTS.md` com regras de SDD, Git, segurança e Definition of Done.
- [x] Criar `PRD.md` com o produto, requisitos e critérios de aceite.
- [x] Criar `ROADMAP.md` com fases, dependências e critérios de aceite.
- [x] Criar `MEMORY.md` com o contexto persistido do projeto.
- [x] Criar `specs/README.md` com o fluxo de especificações.
- [x] Atualizar `README.md` como índice do repositório.
- [x] Versionar o escopo técnico de origem.

**Critérios de aceite:** os documentos existem, estão em pt-BR, apontam uns para os outros, não contêm secrets e definem o fluxo SDD antes do primeiro incremento de código.

## Fase 0 — Validação de acessos e pré-requisitos

**Status:** pendente.

- [ ] Confirmar conta Meta Business e permissões administrativas.
- [ ] Confirmar número e credenciais da WhatsApp Business Cloud API.
- [ ] Confirmar ambiente, projeto e chave da API do Dify.
- [ ] Confirmar fonte cadastral disponível para o MVP, começando por ReceitaWS se contratada.
- [ ] Confirmar e-CNPJ, contrato SERPRO e credenciais de homologação, quando aplicável.
- [ ] Confirmar contratação/permissão da consulta PGFN.
- [ ] Confirmar procurações ou autorizações necessárias para dados fiscais protegidos.
- [ ] Definir CNPJ de teste autorizado para a POC, sem armazená-lo em código ou documentação pública.
- [ ] Registrar titularidade das contas e ativos em nome do contratante.

**Critérios de aceite:** cada dependência possui responsável, status, evidência de acesso ou bloqueio documentado; nenhum secret é colocado no Git; existe um CNPJ real autorizado para demonstrar `CNPJ → Fiscal Gateway → fonte → retorno estruturado`.

## Fase 1 — MVP Inaptas

**Status:** pendente.

- [ ] Criar a base FastAPI do Fiscal Gateway.
- [ ] Definir modelos Pydantic e contrato JSON normalizado.
- [ ] Implementar normalização e validação de CNPJ numérico e alfanumérico.
- [ ] Implementar conector cadastral desacoplado.
- [ ] Retornar situação cadastral, motivo, data, Simples Nacional atual e SIMEI/MEI atual quando disponíveis.
- [ ] Implementar diagnóstico determinístico separado de `source_data` e `ai_interpretation`.
- [ ] Preparar conector/interface de PGFN e ativá-lo quando houver acesso válido.
- [ ] Preparar estrutura para histórico de Simples Nacional e SIMEI/MEI sem inventar dados.
- [ ] Preparar interface futura para SITFIS e ADE/Editais.
- [ ] Implementar `GET /health` e endpoints internos definidos no PRD.
- [ ] Implementar logs estruturados, correlation ID, auditoria mínima, cache e rate limit.
- [ ] Integrar o backend ao Dify sem expor credenciais fiscais.
- [ ] Integrar o webhook da WhatsApp Cloud API com idempotência e deduplicação.
- [ ] Criar Docker/Compose e documentação de configuração segura.
- [ ] Executar POC com CNPJ real autorizado antes da segunda parcela.

**Critérios de aceite:** CNPJ válido retorna JSON normalizado; CNPJ inválido é rejeitado; CNPJ alfanumérico é aceito; indisponibilidade nunca vira resposta fiscal falsa; webhook duplicado não duplica consulta; secrets não aparecem em frontend ou logs; o fluxo WhatsApp → Dify → backend → fonte → resposta é demonstrável quando as contas estiverem disponíveis.

## Fase 2 — Integrações oficiais SERPRO/PGFN

**Status:** pendente.

- [ ] Implementar OAuth2 `client_credentials` para os serviços autorizados.
- [ ] Integrar Consulta CNPJ oficial do SERPRO conforme contrato e Swagger vigente.
- [ ] Integrar Consulta Dívida Ativa da União da PGFN/SERPRO.
- [ ] Implementar renovação de token, retry com backoff, circuit breaker e tratamento de 401, 403, 429 e 5xx.
- [ ] Configurar prioridades e fallback entre SERPRO, fonte alternativa e cache válido.
- [ ] Homologar respostas com credenciais e dados autorizados.

**Critérios de aceite:** tokens não são persistidos em texto puro; 401 renova credencial de forma controlada; 403/429/5xx possuem resposta segura; PGFN indisponível é reportada como indisponibilidade; cada bloco informa sua fonte e status.

## Fase 3 — Fiscal avançado

**Status:** pendente.

- [ ] Integrar Integra Contador quando contrato, certificado e autorização estiverem disponíveis.
- [ ] Implementar fluxo assíncrono do SITFIS: solicitação, protocolo, espera, obtenção e PDF Base64.
- [ ] Implementar extração de texto com PyMuPDF ou pypdf e OCR somente quando necessário.
- [ ] Normalizar pendências e obrigações em JSON com testes de regressão do parser.
- [ ] Implementar autorização/procuração e bloqueio sem vínculo válido.
- [ ] Criar fila assíncrona e observabilidade do processamento.

**Critérios de aceite:** relatório autorizado é processado de ponta a ponta; pendências são rastreáveis à fonte; falha de parser não produz “sem pendências”; documentos e dados sensíveis seguem retenção e acesso compatíveis com LGPD.

## Fase 4 — Regulariza.br e expansão modular

**Status:** futuro.

- [ ] Adicionar observabilidade, alertas, backup, SLA e dashboard operacional.
- [ ] Adicionar relatórios e histórico de consultas conforme base legal e necessidade do produto.
- [ ] Adicionar histórico Simples/MEI quando uma fonte autorizada o disponibilizar.
- [ ] Adicionar módulos trabalhista e previdenciário.
- [ ] Adicionar conectores estaduais, municipais e novas fontes oficiais/autorizadas.

**Critérios de aceite:** novos módulos reutilizam contratos e padrões do Fiscal Gateway, isolam seus fornecedores, possuem spec própria e não alteram o comportamento do MVP sem migração documentada.

## Dependências externas e riscos

| Dependência/risco | Impacto | Mitigação | Status |
|---|---:|---|---|
| Acesso ao SERPRO | Alto | Trial, contrato do cliente e fonte alternativa no MVP | Não validado |
| Procuração/autorização fiscal | Alto | Bloquear consulta sem vínculo válido | Não validado |
| Mudança de API | Médio | Conectores isolados e versionados | Monitorar |
| Alucinação do LLM | Alto | Contrato determinístico e separação de camadas | Mitigado por arquitetura |
| Vazamento de dados | Alto | Secrets server-side, TLS, logs mínimos e LGPD | Obrigatório |
| Limite da ReceitaWS | Médio | Plano comercial, cache ou SERPRO | Não validado |
| CNPJ alfanumérico | Alto | String desde o primeiro modelo | Requisito fechado |
| Mudança do SITFIS/PDF | Médio | Parser desacoplado e testes de regressão | Futuro |

## Registro de marcos

| Data | Marco | Evidência | Observação |
|---|---|---|---|
| 20/08/2026 | Governança documental e SDD | Arquivos de governança versionados | Bootstrap inicial do projeto |
