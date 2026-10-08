# PRD — Sistema Inaptas

**Versão:** 1.1
**Status:** MVP técnico em homologação; produção bloqueada por dependências externas
**Atualizado em:** 08/10/2026
**Fonte:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`

## 1. Resumo do produto

O Inaptas é uma solução de atendimento automatizado para escritórios de contabilidade. O cliente conversa pelo WhatsApp, o Fiscal Gateway valida o evento e o CNPJ, o n8n self-hosted conduz o workflow e o sistema devolve uma resposta estruturada, rastreável e explicada opcionalmente pelo Ollama local.

O Inaptas é o primeiro módulo de uma arquitetura preparada para evoluir ao Regulariza.br.

## 2. Problema e público

Escritórios precisam identificar rapidamente a situação cadastral e alguns indicadores fiscais de empresas, mas as informações estão distribuídas em fontes com contratos, autenticações, formatos e níveis de proteção diferentes.

O público inicial é:

- escritório de contabilidade contratante;
- profissionais autorizados a consultar empresas;
- clientes do escritório que solicitam uma verificação pelo WhatsApp.

No áudio de 19/08/2026, o cliente explicou que o site `inaptas.com.br` capta
leads e que o BotConversa já é usado no atendimento de pré-venda. A necessidade
é ajudar a triagem com dados consultados e explicações, encaminhando os casos
que exigem uma pessoa. Site e BotConversa são ativos externos a este
repositório; a integração ainda precisa de decisão, especificação e
homologação.

## 3. Objetivos e resultado esperado

### Objetivos do MVP

- Automatizar o recebimento de solicitações pelo WhatsApp.
- Apoiar a pré-venda dos leads com consultas autorizadas e encaminhamento humano quando necessário.
- Validar CNPJs numéricos e alfanuméricos.
- Consultar dados cadastrais e indicadores de Simples Nacional/SIMEI quando a fonte fornecer.
- Consultar PGFN quando o conector estiver habilitado e as credenciais forem válidas.
- Entregar um contrato JSON único, independente do fornecedor.
- Registrar auditoria mínima e status de cada conector.
- Evitar que a IA invente dados fiscais ou transforme indisponibilidade em diagnóstico positivo.

### Resultado mínimo de sucesso

Uma POC autorizada deve demonstrar `CNPJ → Fiscal Gateway → fonte disponível → retorno estruturado`, com fonte e horário identificados, antes da segunda parcela do desenvolvimento.

## 4. Escopo do MVP

### Incluído

- WhatsApp Business Cloud API como canal oficial.
- n8n self-hosted como orquestrador conversacional e operacional.
- Ollama local como interpretação opcional, subordinada ao diagnóstico determinístico.
- Backend próprio em Python/FastAPI, chamado Fiscal Gateway.
- Conectores substituíveis para fontes cadastrais e fiscais.
- Normalização de CNPJ, inclusive alfanumérico, sempre como string.
- Dados cadastrais: CNPJ, razão social, situação cadastral, motivo e data da situação quando disponíveis.
- Indicadores atuais de opção pelo Simples Nacional e SIMEI/MEI quando disponíveis.
- Estrutura de PGFN e ativação quando houver contratação/credenciais.
- Preparação para histórico de inclusão/exclusão de Simples Nacional e SIMEI/MEI, sem inferência de datas ausentes.
- Separação explícita entre `source_data`, `system_diagnosis` e `ai_interpretation`.
- Auditoria, correlation ID, cache, rate limit, healthcheck e tratamento seguro de indisponibilidade.
- Consulta opcional de registros CEIS, CNEP e CEPIM pela fonte Portal da Transparência, sempre identificada como compliance e separada de PGFN/CND.
- Docker/Compose, documentação e POC de homologação.

### Preparado, mas fora da implementação completa do MVP

- Integra Contador/SITFIS, incluindo fluxo assíncrono e leitura de PDF.
- Pendências fiscais detalhadas protegidas.
- ADE/Editais por fonte oficial e sustentável. Em 17/09/2026 foi aprovada como direção a importação de publicações estruturadas do DOU/INLABS para localizar ADEs; essa ingestão ainda não foi implementada.
- Integração do site/BotConversa ao Gateway, depois de definir o canal, a passagem de lead e o encaminhamento para atendimento humano.
- Histórico fiscal quando uma fonte autorizada o disponibilizar.

### Fora do escopo

- Scraping como mecanismo principal.
- Bypass ou quebra de CAPTCHA.
- Automação de login no e-CAC como mecanismo principal.
- Inferência de Lucro Real, Lucro Presumido ou outro regime sem fonte oficial/autorizada.
- Garantia de disponibilidade ou funcionamento indefinido de serviços de terceiros.
- Custos de APIs, certificados, hospedagem, Meta/WhatsApp, n8n, Ollama/LLM, domínio, backups e demais serviços externos.
- Construção ou manutenção do site `inaptas.com.br`; o áudio o descreve como canal existente, mas o repositório não contém o site.
- Integração BotConversa: o cliente relata que já usa a plataforma, mas a conexão ao Gateway não existe no código e ainda depende de uma spec e da decisão entre o fluxo atual Meta + n8n e a integração com o BotConversa.

## 5. Fluxo principal

### Caminho que o código implementa

```text
WhatsApp Business Cloud API
  → Fiscal Gateway valida assinatura e idempotência
  → n8n identifica intenção e solicita CNPJ
  → Fiscal Gateway valida e normaliza o CNPJ
  → conectores consultam fontes habilitadas
  → normalizador consolida dados e fontes
  → regras determinísticas produzem diagnóstico
  → Ollama opcional explica somente o que possui evidência
  → resposta retorna ao WhatsApp
```

O backend valida assinatura do webhook, deduplica eventos, aplica rate limit, controla credenciais, registra auditoria e converte retornos externos para um contrato único.

O site e o BotConversa são canais externos ao repositório. O caminho Meta + n8n
é o que está implementado no código; conectar o canal de pré-venda já usado
pelo cliente ainda depende de especificação e homologação.

### Caminho comercial existente e integração desejada

```text
Site inaptas.com.br → BotConversa → pré-venda e, quando necessário, equipe humana
                              └ → Fiscal Gateway (ligação ainda não implementada)
```

## 6. Requisitos funcionais

- **RF01:** receber mensagem por webhook do WhatsApp.
- **RF02:** identificar solicitação de consulta e solicitar CNPJ quando necessário.
- **RF03:** normalizar CNPJ com e sem máscara.
- **RF04:** validar CNPJ numérico e alfanumérico.
- **RF05:** consultar fonte cadastral habilitada.
- **RF06:** devolver situação cadastral, motivo e data quando disponíveis.
- **RF07:** devolver indicadores atuais de Simples Nacional e SIMEI/MEI quando disponíveis.
- **RF08:** consultar PGFN quando habilitado e autorizado.
- **RF09:** manter pontos de extensão para SITFIS e ADE/Editais.
- **RF10:** consolidar dados de múltiplos conectores em JSON único.
- **RF11:** gerar diagnóstico determinístico separado da interpretação da IA.
- **RF12:** informar indisponibilidade sem afirmar ausência de pendência.
- **RF13:** registrar auditoria mínima por consulta e fornecedor.
- **RF14:** impedir exposição de secrets ao frontend, ao n8n, ao Ollama e aos logs.
- **RF15:** aplicar timeout, retry controlado, cache e rate limit.
- **RF16:** tornar webhooks idempotentes e resistentes à duplicidade.
- **RF17:** trocar fornecedor por configuração/conector sem reconstruir a aplicação.
- **RF18:** ativar ou desativar fontes de forma controlada.
- **RF19:** consultar CEIS, CNEP e CEPIM por provider opcional, sem apresentar esses registros como dívida ou certidão fiscal.

## 7. Requisitos não funcionais

- **RNF01:** HTTPS/TLS obrigatório em ambientes expostos.
- **RNF02:** secrets somente no servidor ou secret manager.
- **RNF03:** logs sem tokens e com minimização de dados pessoais.
- **RNF04:** CNPJ persistido como string.
- **RNF05:** timeout configurável por fornecedor.
- **RNF06:** retry com backoff e limites controlados.
- **RNF07:** cache com TTL por natureza da fonte.
- **RNF08:** backup e retenção compatíveis com o ambiente do contratante.
- **RNF09:** healthcheck e correlation ID.
- **RNF10:** rastreabilidade de fonte, status, horário e erro.
- **RNF11:** arquitetura modular e conectores isolados.
- **RNF12:** documentação operacional em pt-BR.
- **RNF13:** testes automatizados para regras, contratos e conectores.
- **RNF14:** tratamento compatível com LGPD e autorizações aplicáveis.
- **RNF15:** idempotência de webhooks.

## 8. Contrato de resposta

O Fiscal Gateway nunca deve enviar ao n8n ou ao Ollama respostas brutas e incompatíveis de cada fornecedor. O formato canônico inicial é:

```json
{
  "cnpj": "12ABC34501DE35",
  "company": {
    "legal_name": "EMPRESA EXEMPLO LTDA",
    "opening_date": "2026-08-01",
    "registration_status": "ATIVA",
    "registration_status_date": "2026-08-01",
    "registration_status_reason": null
  },
  "tax": {
    "simple_national": null,
    "simei": null,
    "declared_tax_regime": null,
    "pending_obligations": []
  },
  "pgfn": {
    "has_active_debt": null,
    "debts": []
  },
  "sources": [
    {
      "provider": "SERPRO_CNPJ",
      "status": "ok"
    }
  ],
  "system_diagnosis": {},
  "ai_interpretation": null,
  "generated_at": "2026-08-20T10:00:00-03:00"
}
```

`null`, `unknown` ou `unavailable` devem representar ausência de evidência conforme o contrato da spec correspondente. Nunca converter erro de consulta em `false` ou em “não existem pendências”.

## 9. Regras de IA e confiabilidade

- `source_data` é retorno objetivo da fonte, preservado e normalizado sem interpretação do LLM.
- `system_diagnosis` é resultado de regras determinísticas, explícitas e testáveis.
- `ai_interpretation` é somente a explicação amigável, subordinada aos dois níveis anteriores.
- O LLM não pode inventar situação, dívida, regime, pendência ou ausência de problema.
- Toda informação fiscal relevante deve indicar fonte e status.
- Se PGFN estiver indisponível, a resposta deve informar a indisponibilidade, não afirmar inexistência de dívida.

## 10. Integrações e fontes

| Integração | Papel | Política |
|---|---|---|
| WhatsApp Business Cloud API | Canal de entrada/saída | Oficial, com webhook validado |
| n8n self-hosted | Workflow, conversa e integração com Gateway/WhatsApp | Sem credenciais fiscais de providers; webhook interno autenticado |
| Ollama local | Interpretação textual opcional | Recebe contrato canônico mínimo; fallback determinístico em indisponibilidade |
| BotConversa | Canal de pré-venda já usado pelo cliente, segundo áudio de 19/08 | Ainda não integrado; especificar sua ligação ao Gateway antes de alterar a arquitetura atual Meta + n8n |
| Minha Receita | Fonte cadastral self-hosted | Snapshot público com atualização periódica; exige carga e cerca de 180 GB na carga inicial |
| ReceitaWS | Fonte cadastral de baixo atrito | Alternativa selecionável; não é fonte oficial e não há confirmação de contratação comercial |
| SERPRO Consulta CNPJ | Cadastro oficial | Preferencial em produção quando contratado |
| SERPRO/PGFN | Dívida Ativa da União | Conector de trial disponível e desativado por padrão; produção depende de contrato e autenticação |
| Portal da Transparência | Registros CEIS, CNEP e CEPIM | Provider separado e opcional; não é dívida PGFN, CND nem prova de regularidade fiscal |
| Integra Contador/SITFIS | Situação fiscal protegida | Extensão futura, depende de autorização |
| DOU/INLABS | Publicações estruturadas como fonte possível para ADE | Direção aprovada em 17/09; ingestão ainda não implementada |

O Dify constava na proposta inicial, mas o repositório atual usa n8n self-hosted
e Ollama local. Essa é a arquitetura documentada e implementada até que o
responsável do produto aprove outra decisão.

O endpoint produtivo do SERPRO deve ser o vigente no contrato/Swagger do cliente. Endpoints de trial ou documentação não devem ser tratados como garantia de produção.

## 11. Arquitetura e dados

Componentes previstos:

- FastAPI, Pydantic v2, HTTPX e Uvicorn/Gunicorn.
- PostgreSQL para consultas e auditoria mínima.
- Redis para cache, tokens, rate limit e futura fila.
- Docker, Docker Compose, Linux Ubuntu LTS e proxy HTTPS.
- PyMuPDF ou pypdf para a futura leitura de relatórios.
- pytest, pytest-asyncio e respx para testes.

Estruturas mínimas preparadas:

- `consultations`: `id`, `correlation_id`, `cnpj`, `source`, `request_type`, `status`, timestamps, hash de resposta, erro e hash de contato.
- `api_audit`: consulta, provedor, alias de endpoint, status HTTP, latência e timestamp.
- `provider_config`: provedor, habilitação, prioridade, timeout, retries e TTL; nunca secrets em texto puro.

## 12. Critérios de aceite do MVP

### Consulta

- CNPJ válido retorna dados normalizados.
- CNPJ inválido é rejeitado com mensagem segura.
- CNPJ alfanumérico é aceito.
- Situação, motivo, data, Simples e SIMEI retornam apenas quando a fonte fornecer evidência.
- Timeout ou falha não gera resposta fiscal falsa.

### WhatsApp, n8n e Ollama

- O webhook recebe mensagem e valida sua assinatura.
- Evento duplicado não gera consulta repetida.
- n8n recebe somente eventos validados pelo Gateway e chama o endpoint protegido do orquestrador.
- Ollama recebe o contrato canônico e pode devolver uma explicação; o workflow bloqueia afirmações sem evidência.
- Resposta segura retorna ao usuário.

### SERPRO/PGFN

- Token é obtido e renovado de forma segura quando a integração estiver habilitada.
- 401, 403, 429 e 5xx têm tratamento definido.
- Cada bloco apresenta fonte e status.

### Segurança

- Nenhuma chave aparece no frontend, logs, spec, PRD, README ou memória.
- `.env` não é versionado.
- Dados sensíveis têm acesso, retenção e auditoria compatíveis com a autorização recebida.

### POC

- Antes da segunda parcela, um CNPJ real autorizado percorre o fluxo `CNPJ → Fiscal Gateway → fonte → retorno estruturado`.
- Na homologação E2E, quando as contas estiverem disponíveis, o fluxo completo `WhatsApp → Gateway → n8n → Gateway → fonte → Ollama opcional → WhatsApp` é demonstrado.

## 13. Riscos e limites comerciais

Os riscos principais são acesso ao SERPRO, procuração fiscal, mudanças de APIs, alucinação do LLM, vazamento de dados, limites da ReceitaWS, CNPJ alfanumérico e mudança do formato SITFIS. A mitigação deve permanecer alinhada ao `ROADMAP.md`.

O valor comercial de R$ 2.500,00 contempla o desenvolvimento do MVP, Fiscal Gateway, workflow WhatsApp/n8n, consulta cadastral, arquitetura modular, normalização, regras determinísticas, preparação para PGFN/SITFIS/ADE, implantação, documentação e POC. Serviços, contratos, credenciais e custos de terceiros ficam fora do desenvolvimento.

### Estimativas SERPRO registradas na conversa

Em 17/09/2026 foram compartilhadas estimativas mensais de consumo, sem proposta
comercial anexada:

| Volume | CNPJ + PGFN + CND | CNPJ + PGFN, sem CND |
|---:|---:|---:|
| 1.000 consultas | ~R$ 1.680/mês | ~R$ 840/mês |
| 10.000 consultas | ~R$ 12.900/mês | ~R$ 5.000/mês |
| 100.000 consultas | ~R$ 88.000/mês | ~R$ 26.000/mês |

São números informais registrados na conversa, não preços confirmados pelo
SERPRO. Devem ser revalidados diretamente no produto e contrato vigentes antes
da compra. A conversa destacou a CND como a maior parcela do custo e sugeriu
consultá-la apenas quando o caso exigir.

## Estado operacional em 08/10/2026 e decisões posteriores

- Em 29/09/2026 a equipe relatou que uma integração de teste SERPRO havia
  funcionado; o registro não identifica o produto, o ambiente ou a evidência.
- Em 06/10/2026 o contratante informou que ainda não havia contratado o
  SERPRO. A integração produtiva permanece pendente.
- O repositório agora contém um conector `serpro_trial` para PGFN. Ele chama um
  documento de teste fixo e **não consulta o CNPJ informado**; o padrão é
  `PGFN_PROVIDER=disabled`. Use somente para homologação, nunca para responder
  sobre dívida de uma empresa real.
- Em 17/09/2026 foi aprovada a direção de usar dados estruturados do DOU/INLABS
  para localizar ADEs. O desenvolvimento e a validação dessa ingestão são
  pendências de roadmap. Não contornar CAPTCHA nem automatizar login no e-CAC.
- O áudio de 19/08 relata que o site da Inaptas capta leads e que o BotConversa
  já conduz a pré-venda. O acesso foi compartilhado em texto em 06/10; a senha
  deve ser trocada e as sessões revogadas. Não foi copiada para este PRD nem
  para o repositório.
- A produção ainda depende de Meta/WhatsApp, n8n, OIDC, fonte cadastral,
  infraestrutura, autorizações e POC com CNPJ autorizado.

## 15. Gestão de mudanças

O PRD representa o escopo fechado do MVP. Qualquer mudança que altere comportamento, contrato, risco, integração ou critério de aceite deve:

1. ser descrita em uma spec;
2. indicar impacto no PRD e no roadmap;
3. ser aprovada antes da implementação;
4. atualizar `MEMORY.md` quando mudar uma decisão ou o estado operacional.

## 16. Documentos relacionados

- [Instruções dos agentes](AGENTS.md)
- [Memória persistida](MEMORY.md)
- [Roadmap](ROADMAP.md)
- [Fluxo de specs](specs/README.md)
- [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)
- [Fluxograma do sistema](FLUXOGRAMA.md)
- [Inventário seguro de acessos](ACESSOS.md)
