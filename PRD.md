# PRD — Sistema Inaptas

**Versão:** 1.0
**Status:** aprovado para início do MVP
**Data-base:** 20/08/2026
**Fonte:** `escopo_tecnico_inaptas_regularizabr_atualizado.md`

## 1. Resumo do produto

O Inaptas é uma solução de atendimento automatizado para escritórios de contabilidade. O cliente conversa pelo WhatsApp, o Dify conduz o atendimento, o Fiscal Gateway valida o CNPJ e consulta fontes autorizadas, e o sistema devolve uma resposta estruturada, rastreável e explicada em linguagem natural.

O Inaptas é o primeiro módulo de uma arquitetura preparada para evoluir ao Regulariza.br.

## 2. Problema e público

Escritórios precisam identificar rapidamente a situação cadastral e alguns indicadores fiscais de empresas, mas as informações estão distribuídas em fontes com contratos, autenticações, formatos e níveis de proteção diferentes.

O público inicial é:

- escritório de contabilidade contratante;
- profissionais autorizados a consultar empresas;
- clientes do escritório que solicitam uma verificação pelo WhatsApp.

## 3. Objetivos e resultado esperado

### Objetivos do MVP

- Automatizar o recebimento de solicitações pelo WhatsApp.
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
- Dify como orquestrador conversacional.
- Backend próprio em Python/FastAPI, chamado Fiscal Gateway.
- Conectores substituíveis para fontes cadastrais e fiscais.
- Normalização de CNPJ, inclusive alfanumérico, sempre como string.
- Dados cadastrais: CNPJ, razão social, situação cadastral, motivo e data da situação quando disponíveis.
- Indicadores atuais de opção pelo Simples Nacional e SIMEI/MEI quando disponíveis.
- Estrutura de PGFN e ativação quando houver contratação/credenciais.
- Preparação para histórico de inclusão/exclusão de Simples Nacional e SIMEI/MEI, sem inferência de datas ausentes.
- Separação explícita entre `source_data`, `system_diagnosis` e `ai_interpretation`.
- Auditoria, correlation ID, cache, rate limit, healthcheck e tratamento seguro de indisponibilidade.
- Docker/Compose, documentação e POC de homologação.

### Preparado, mas fora da implementação completa do MVP

- Integra Contador/SITFIS, incluindo fluxo assíncrono e leitura de PDF.
- Pendências fiscais detalhadas protegidas.
- ADE/Editais por fonte oficial e sustentável.
- Histórico fiscal quando uma fonte autorizada o disponibilizar.

### Fora do escopo

- Scraping como mecanismo principal.
- Bypass ou quebra de CAPTCHA.
- Automação de login no e-CAC como mecanismo principal.
- Inferência de Lucro Real, Lucro Presumido ou outro regime sem fonte oficial/autorizada.
- Garantia de disponibilidade ou funcionamento indefinido de serviços de terceiros.
- Custos de APIs, certificados, hospedagem, Meta/WhatsApp, Dify, LLM, domínio, backups e demais serviços externos.

## 5. Fluxo principal

```text
Cliente
  → WhatsApp
  → Dify identifica intenção e solicita CNPJ
  → Fiscal Gateway valida e normaliza o CNPJ
  → conectores consultam fontes habilitadas
  → normalizador consolida dados e fontes
  → regras determinísticas produzem diagnóstico
  → Dify explica somente o que possui evidência
  → resposta retorna ao WhatsApp
```

O backend valida assinatura do webhook, deduplica eventos, aplica rate limit, controla credenciais, registra auditoria e converte retornos externos para um contrato único.

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
- **RF14:** impedir exposição de secrets ao frontend, ao Dify e aos logs.
- **RF15:** aplicar timeout, retry controlado, cache e rate limit.
- **RF16:** tornar webhooks idempotentes e resistentes à duplicidade.
- **RF17:** trocar fornecedor por configuração/conector sem reconstruir a aplicação.
- **RF18:** ativar ou desativar fontes de forma controlada.

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

O Fiscal Gateway nunca deve enviar ao Dify respostas brutas e incompatíveis de cada fornecedor. O formato canônico inicial é:

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
| Dify | Conversa e interpretação | Sem credenciais fiscais diretas |
| ReceitaWS | Fonte cadastral de baixo atrito | Alternativa de MVP; não é fonte oficial |
| SERPRO Consulta CNPJ | Cadastro oficial | Preferencial em produção quando contratado |
| SERPRO/PGFN | Dívida Ativa da União | Depende de contrato e autenticação |
| Integra Contador/SITFIS | Situação fiscal protegida | Extensão futura, depende de autorização |

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

### WhatsApp e Dify

- O webhook recebe mensagem e valida sua assinatura.
- Evento duplicado não gera consulta repetida.
- Dify recebe o contexto estruturado.
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
- Na homologação E2E, quando as contas estiverem disponíveis, o fluxo completo `WhatsApp → Dify → Backend → fonte → WhatsApp` é demonstrado.

## 13. Riscos e limites comerciais

Os riscos principais são acesso ao SERPRO, procuração fiscal, mudanças de APIs, alucinação do LLM, vazamento de dados, limites da ReceitaWS, CNPJ alfanumérico e mudança do formato SITFIS. A mitigação deve permanecer alinhada ao `ROADMAP.md`.

O valor comercial de R$ 2.500,00 contempla o desenvolvimento do MVP, Fiscal Gateway, fluxo WhatsApp/Dify, consulta cadastral, arquitetura modular, normalização, regras determinísticas, preparação para PGFN/SITFIS/ADE, implantação, documentação e POC. Serviços, contratos, credenciais e custos de terceiros ficam fora do desenvolvimento.

## 14. Gestão de mudanças

O PRD representa o escopo fechado do MVP. Qualquer mudança que altere comportamento, contrato, risco, integração ou critério de aceite deve:

1. ser descrita em uma spec;
2. indicar impacto no PRD e no roadmap;
3. ser aprovada antes da implementação;
4. atualizar `MEMORY.md` quando mudar uma decisão ou o estado operacional.

## 15. Documentos relacionados

- [Instruções dos agentes](AGENTS.md)
- [Memória persistida](MEMORY.md)
- [Roadmap](ROADMAP.md)
- [Fluxo de specs](specs/README.md)
- [Escopo técnico de origem](escopo_tecnico_inaptas_regularizabr_atualizado.md)
