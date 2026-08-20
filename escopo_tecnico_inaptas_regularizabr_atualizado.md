# Escopo Técnico e Avaliação de Viabilidade
## Integração Dify AI + WhatsApp + Consulta CNPJ + Receita Federal/SERPRO + PGFN

**Documento técnico consolidado - versão final do MVP**  
**Data da atualização:** 20/08/2026  
**Objetivo:** definir o escopo técnico fechado do MVP Inaptas, incluindo arquitetura escalável para futura evolução ao Regulariza.br, fontes de dados, matriz de conectores, regras de IA, segurança, custos externos, propriedade dos ativos, entregáveis e critérios de homologação.

---

## 1. Resumo executivo

O projeto é **tecnicamente viável**, porém há uma distinção fundamental entre três tipos de informação:

1. **Dados cadastrais públicos do CNPJ**  
   Ex.: razão social, abertura, situação cadastral, CNAE, endereço.  
   Podem ser obtidos por ReceitaWS ou pela API oficial Consulta CNPJ do SERPRO.

2. **Dados fiscais protegidos / vinculados ao contribuinte**  
   Ex.: situação fiscal detalhada, omissões, pendências de declarações e determinadas informações acessíveis via e-CAC.  
   O caminho recomendado é o **Integra Contador / SITFIS**, com contratação SERPRO, certificado digital e, quando exigido, procuração/autorização do contribuinte.

3. **Dívida Ativa da União / PGFN**  
   Pode ser consultada por solução oficial do SERPRO/PGFN, mediante contratação e autenticação.

A arquitetura recomendada deve **evitar scraping como mecanismo principal**. O sistema deve trabalhar com APIs oficiais/autorizadas e usar uma camada própria de conectores para que mudanças em um fornecedor não obriguem a reconstrução da aplicação.

### Conclusão de viabilidade

- **MVP com ReceitaWS + WhatsApp + Dify + backend Python:** alta viabilidade.
- **Consulta oficial CNPJ pelo SERPRO:** alta viabilidade, dependendo de contratação/credenciais.
- **Consulta PGFN:** alta viabilidade, dependendo de contratação/credenciais.
- **Pendências fiscais/declarações:** viável com Integra Contador/SITFIS, mas aumenta significativamente a complexidade.
- **Scraping de Receita/e-CAC/PGFN:** não recomendado como arquitetura principal.
- **R$ 2.500,00:** valor compatível com um MVP delimitado, desde que licenças, contratos, certificados, APIs pagas e infraestrutura sejam fornecidos/pagos pelo contratante e que integrações fiscais protegidas mais complexas sejam condicionadas à liberação das credenciais oficiais.

---

# 2. Objetivo do sistema

Criar uma solução de atendimento automatizado para escritório de contabilidade em que:

1. O cliente entra em contato pelo WhatsApp.
2. O Dify conduz o atendimento.
3. O cliente informa o CNPJ.
4. O backend valida o CNPJ.
5. O backend consulta as fontes necessárias.
6. Os dados são normalizados em um formato único.
7. O Dify recebe os dados estruturados.
8. O sistema responde ao cliente pelo WhatsApp.
9. Logs técnicos e auditoria mínima são armazenados para rastreabilidade.

### Dados obrigatórios no MVP

O MVP deve identificar e devolver de forma estruturada, sempre conforme o retorno da fonte utilizada:

- CNPJ consultado;
- Razão Social, quando disponível;
- Situação Cadastral;
- Motivo da Situação Cadastral;
- Data da Situação Cadastral;
- Indicador atual de opção pelo Simples Nacional;
- Indicador atual de opção pelo SIMEI/MEI;
- Dívida Ativa da União / PGFN, quando o conector estiver habilitado e com credenciais válidas;
- Fonte utilizada em cada bloco de informação;
- Data/hora da consulta;
- Status da consulta de cada conector.

### Preparação para histórico Simples/MEI

O modelo de dados e o contrato interno do Fiscal Gateway devem ficar preparados para, futuramente, armazenar e retornar histórico de enquadramento, incluindo:

- data de inclusão no Simples Nacional;
- data de exclusão do Simples Nacional;
- data de inclusão no SIMEI/MEI;
- data de exclusão do SIMEI/MEI;
- períodos de opção;
- fonte e data de referência do histórico.

A disponibilidade desses dados dependerá de fonte oficial/autorizada que os forneça. O MVP não deve inferir datas históricas inexistentes no retorno da fonte.

---

# 3. Ponto crítico: definição de “Regime Tributário”

O termo precisa ser fechado funcionalmente antes da produção.

Há diferença entre:

- Optante pelo Simples Nacional;
- MEI/SIMEI;
- Lucro Presumido;
- Lucro Real;
- outros enquadramentos ou situações especiais.

A simples consulta pública de CNPJ **não deve ser considerada suficiente para identificar com segurança todos os regimes tributários possíveis**.

### Recomendação

No MVP, definir o campo como:

> **Enquadramento conhecido / indicador de Simples Nacional e MEI**, quando disponível pela fonte contratada.

Se o requisito for obrigatoriamente determinar **Lucro Real, Lucro Presumido, Simples ou outro regime com validade fiscal**, isso deve ser tratado como dado fiscal e validado através de fonte oficial/serviço autorizado, e não inferido pela IA.

---

# 4. Ponto crítico: “Declarações Pendentes no ADE”

“ADE” normalmente se refere a **Ato Declaratório Executivo**, podendo estar relacionado, entre outros casos, à inaptidão do CNPJ por omissão de obrigações.

Para automação confiável, não é recomendado tentar extrair essas pendências diretamente de páginas do site da Receita usando scraping.

### Solução recomendada e decisão do MVP

Para informações fiscais protegidas, a solução sustentável recomendada continua sendo o **Integra Contador – SITFIS**.

Entretanto, no MVP a implementação completa do SITFIS não é obrigatória. A arquitetura deve apenas deixar o conector, contrato interno e pontos de extensão preparados para receber futuramente o relatório oficial de Situação Fiscal.

O SITFIS disponibiliza o relatório de situação fiscal do contribuinte no âmbito da Receita Federal e PGFN.

O fluxo oficial é assíncrono:

1. solicitar relatório;
2. receber protocolo;
3. aguardar o tempo indicado;
4. emitir/obter relatório;
5. receber o PDF em Base64;
6. extrair os dados relevantes;
7. normalizar as pendências para JSON;
8. devolver ao Dify.

### Implicação técnica

Será necessário um módulo de leitura do relatório PDF oficial, preferencialmente por:

- PyMuPDF; ou
- pypdf.

OCR só deve ser utilizado se o documento oficial não possuir texto extraível.

### ADE/Editais e CAPTCHA

Para ADE, editais e publicações associadas à Receita Federal, fica estabelecido que:

- não haverá bypass de CAPTCHA;
- não haverá quebra de mecanismos de proteção;
- não haverá scraping agressivo como dependência do MVP;
- não haverá automação de login no e-CAC como mecanismo principal;
- se existir fonte oficial, base autorizada ou API sustentável, um conector poderá ser implementado futuramente;
- se a informação estiver disponível apenas por canal protegido e sem integração oficial, o sistema deverá informar indisponibilidade/necessidade de consulta pelo canal oficial.

O MVP manterá apenas uma interface/conector reservado para futura solução de ADE/Editais.

---

# 5. Fontes e APIs recomendadas

## 5.1 ReceitaWS

**Tipo:** API de terceiro, não oficial da Receita Federal.

### Uso recomendado

Pode ser utilizada no MVP para dados cadastrais simples por possuir integração rápida e baixo atrito operacional.

### API pública

Endpoint conhecido:

```text
GET https://www.receitaws.com.br/v1/cnpj/{cnpj}
```

Características documentadas:

- não exige autenticação;
- limite de aproximadamente 3 consultas por minuto;
- usa CNPJs previamente existentes no cache da ReceitaWS;
- não deve ser considerada fonte oficial da Receita Federal.

### API comercial

A ReceitaWS também possui versão autenticada/comercial.

Na consulta realizada em 19/08/2026, o plano Ouro divulgado estava em:

- R$ 349,00/mês;
- 50 consultas por minuto;
- 600.000 consultas/mês na base;
- 30.000 consultas/mês em tempo real.

O fornecedor deve confirmar preço e condições no momento da contratação.

**Custo equivalente de referência:** se as 30.000 consultas em tempo real forem integralmente utilizadas, R$ 349 / 30.000 ≈ **R$ 0,0116 por consulta em tempo real equivalente**. Isso é apenas uma equivalência matemática; a cobrança comercial é por plano, não necessariamente por chamada individual.

---

## 5.2 API oficial Consulta CNPJ – SERPRO

**Tipo:** API oficial/comercial com dados originados nas bases da Receita Federal.

### Recomendação

Para uma solução de produção que precise de maior confiabilidade e vínculo contratual com uma fonte oficial, esta deve ser a opção preferencial para dados cadastrais.

A documentação oficial informa que a Consulta CNPJ pode ser contratada por empresas privadas e exige e-CNPJ para o fluxo normal de contratação.

### Autenticação

OAuth2 com `client_credentials`.

Endpoint oficial para obtenção de token:

```text
POST https://gateway.apiserpro.serpro.gov.br/token
```

Credenciais:

- Consumer Key
- Consumer Secret

O token Bearer tem validade aproximada de 1 hora.

### Ambiente de demonstração

Exemplo oficial de trial:

```text
GET https://gateway.apiserpro.serpro.gov.br/consulta-cnpj-df-trial/v2/basica/{cnpj}
```

### Produção

A documentação do SERPRO informa que o **endpoint produtivo exato contratado deve ser obtido na Área do Cliente/Swagger do contrato**.

Isso é importante porque não é recomendável prometer como endpoint definitivo do escritório privado o endereço do Conecta gov.br sem antes validar o tipo de habilitação concedida.

### Sobre o endpoint inicialmente citado

Foi citado:

```text
https://apigateway.conectagov.estaleiro.serpro.gov.br/api-cnpj-basica/v2/basica/
```

Esse endpoint pertence ao ecossistema **Conecta gov.br**, voltado à interoperabilidade governamental.

Para um escritório contábil privado, a recomendação é contratar o produto comercial **Consulta CNPJ / SERPRO** e utilizar o endpoint disponibilizado ao contrato no gateway SERPRO.

---

## 5.3 Matriz consolidada de fontes do MVP

| Dado | Fonte preferencial | Fallback / alternativa | Método | Autenticação | Custo de referência | Limites / consumo | Atualização | Risco |
|---|---|---|---|---|---|---|---|---|
| CNPJ / situação cadastral | SERPRO Consulta CNPJ | ReceitaWS | REST/HTTPS | OAuth2 no SERPRO; token no plano comercial ReceitaWS | SERPRO variável por contrato; ReceitaWS gratuita ou comercial | Conforme contrato; ReceitaWS pública ~3/min; plano Ouro 50/min | SERPRO: fonte oficial; ReceitaWS pode usar cache | Baixo/médio |
| Simples Nacional atual | SERPRO Consulta CNPJ, quando disponível no produto contratado | Outra fonte oficial/autorizada futura | REST/HTTPS | OAuth2 | Variável por contrato | Conforme contrato | Conforme fonte | Baixo/médio |
| SIMEI/MEI atual | SERPRO Consulta CNPJ, quando disponível no produto contratado | Outra fonte oficial/autorizada futura | REST/HTTPS | OAuth2 | Variável por contrato | Conforme contrato | Conforme fonte | Baixo/médio |
| Dívida Ativa PGFN | PGFN/SERPRO Consulta Dívida Ativa | Nenhuma inferência como fallback | REST/HTTPS | OAuth2/Bearer | Variável por contrato | Conforme contrato | Base oficial PGFN | Baixo/médio |
| Situação fiscal detalhada | Integra Contador/SITFIS - fase futura | Nenhuma inferência | REST assíncrona + PDF | SERPRO + e-CNPJ + autorização/procuração quando exigida | Variável por consumo | Conforme contrato | Oficial | Médio |
| ADE/Editais | Fonte oficial/API futura, se disponível | Consulta manual pelo canal oficial | Conector futuro | Conforme fonte | A definir | A definir | Conforme fonte | Médio/alto |

### Política de troca de fornecedor

Todos os provedores serão encapsulados em conectores independentes. O restante da aplicação deve consumir interfaces internas padronizadas, de modo que a substituição de uma fonte não exija reescrita do Dify, do WhatsApp ou do núcleo de negócio.

# 6. API PGFN / Dívida Ativa

## 6.1 API oficial Consulta Dívida Ativa da União

**Fonte:** PGFN/SERPRO.

Base de produção publicada no catálogo oficial:

```text
https://gateway.apiserpro.serpro.gov.br/consulta-divida-ativa-df/api
```

A documentação do serviço demonstra a consulta por devedor utilizando o padrão:

```text
GET /v1/devedor/{cpfOuCnpj}
```

Portanto, a chamada lógica esperada é:

```text
GET https://gateway.apiserpro.serpro.gov.br/consulta-divida-ativa-df/api/v1/devedor/{cnpj}
```

A URL final deverá ser confirmada no Swagger/contrato ativo antes da entrada em produção.

### Autenticação

OAuth2 / Bearer Token via SERPRO.

Endpoint de token:

```text
POST https://gateway.apiserpro.serpro.gov.br/token
```

Com:

- Consumer Key;
- Consumer Secret;
- `grant_type=client_credentials`.

### Pré-requisito comercial

A contratação normal requer e-CNPJ da empresa contratante.

### Retornos possíveis

A API pode retornar, conforme o serviço:

- número da inscrição;
- processo;
- situação da inscrição;
- descrição da situação;
- valor consolidado;
- unidade responsável;
- identificação do devedor;
- outros dados da inscrição.

---

# 7. Integra Contador / SITFIS

## 7.1 Quando utilizar

O Integra Contador deve ser utilizado quando o projeto sair da simples consulta cadastral e passar a consultar informações fiscais associadas ao contribuinte.

Exemplos:

- situação fiscal;
- pendências;
- declarações;
- DCTFWeb;
- PGDAS-D;
- DEFIS;
- pagamentos;
- parcelamentos;
- caixa postal;
- outros serviços fiscais.

Base oficial:

```text
https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/
```

Caminhos principais:

```text
/Apoiar
/Consultar
/Declarar
/Emitir
/Monitorar
```

## 7.2 SITFIS

O serviço de maior interesse para este projeto é o **SITFIS – Situação Fiscal**.

Identificadores oficiais observados na documentação:

```text
idSistema: SITFIS
idServico: RELATORIOSITFIS92
versaoSistema: 2.0
```

O retorno de emissão pode conter:

```text
pdf: documento PDF em Base64
tempoEspera: tempo estimado quando processamento ainda estiver em andamento
```

### Requisitos

- contrato Integra Contador;
- Consumer Key;
- Consumer Secret;
- certificado e-CNPJ;
- autenticação exigida pelo SERPRO;
- procuração eletrônica/autorização quando o serviço consultado exigir.

### Atenção

Não é correto afirmar que qualquer CNPJ informado pelo WhatsApp poderá ter suas informações fiscais privadas consultadas apenas por ele ter sido digitado.

Quando o serviço exigir autorização, o escritório deverá possuir vínculo, procuração ou autorização correspondente.

---

# 8. CNPJ alfanumérico — requisito obrigatório em 2026

A partir de 31/07/2026 iniciou-se a implantação progressiva de CNPJs alfanuméricos para novas inscrições.

### Requisitos técnicos

O sistema deve:

- armazenar CNPJ como `VARCHAR`/`TEXT`, nunca como número inteiro;
- aceitar letras de A-Z;
- normalizar letras para maiúsculas;
- preservar 14 posições;
- utilizar o algoritmo atualizado de dígito verificador;
- não usar regex exclusivamente `[0-9]+`;
- não converter CNPJ para `int`, `BIGINT` ou similares;
- validar compatibilidade de todas as APIs utilizadas.

Exemplo de formato válido de teste informado pelo SERPRO:

```text
L9J5BYRT000101
```

---

# 9. Arquitetura recomendada

## 9.1 Visão lógica

```text
Cliente
  │
  ▼
WhatsApp Business Cloud API
  │ webhook
  ▼
API Gateway / Backend FastAPI
  │
  ├── valida assinatura/webhook
  ├── deduplica eventos
  ├── controla rate limit
  └── encaminha contexto
  │
  ▼
Dify
  │
  ├── identifica intenção
  ├── solicita CNPJ
  └── chama Fiscal Gateway
  │
  ▼
Fiscal Gateway - Python/FastAPI
  │
  ├── Connector ReceitaWS
  ├── Connector SERPRO CNPJ
  ├── Connector Simples/MEI
  ├── Connector PGFN
  ├── Connector Integra Contador/SITFIS [prepared/future]
  ├── Connector ADE/Editais [reserved/future]
  └── Normalizador Fiscal
  │
  ├───────────────┐
  ▼               ▼
PostgreSQL       Redis
auditoria        cache/tokens/rate limit
  │
  ▼
Resposta JSON padronizada
  │
  ▼
Dify
  │
  ▼
WhatsApp
```

---

# 10. Princípio arquitetural principal

O Dify **não deve possuir diretamente todas as credenciais fiscais**.

A melhor arquitetura é:

```text
Dify -> API interna do projeto -> conectores fiscais externos
```

O backend próprio funciona como um **Fiscal Gateway**.

### Benefícios

- credenciais ficam fora do prompt e do workflow visual;
- troca de ReceitaWS por SERPRO sem alterar toda a IA;
- centralização de logs;
- controle de erros;
- cache;
- rate limiting;
- auditoria;
- normalização dos retornos;
- bloqueio de consultas indevidas;
- menor risco de vazamento de secrets.

---

# 11. Tecnologias recomendadas

## Backend

- Python 3.12/3.13
- FastAPI
- Pydantic v2
- HTTPX
- Uvicorn/Gunicorn

## Banco de dados

- PostgreSQL

## Cache, tokens e filas

- Redis

## Processamento assíncrono

Para SITFIS e outros serviços com resposta `202`/tempo de espera:

- Celery + Redis; ou
- ARQ/RQ em implementação mais leve.

## Integração PDF

- PyMuPDF;
- pypdf.

## Infraestrutura

- Docker;
- Docker Compose;
- Linux Ubuntu LTS;
- Nginx ou Caddy;
- HTTPS/TLS obrigatório.

## Orquestração de IA

- Dify Cloud; ou
- Dify self-hosted.

## WhatsApp

- WhatsApp Business Platform / Cloud API oficial da Meta.

## Testes

- pytest;
- pytest-asyncio;
- respx para mocks HTTP;
- Postman/Bruno para coleção de homologação.

## Observabilidade

Mínimo:

- logs estruturados;
- request/correlation ID;
- healthcheck;
- rotação de logs;
- alerta de indisponibilidade.

Recomendável:

- Sentry;
- Uptime Kuma;
- Prometheus/Grafana em implantação maior.

---

# 12. Dify: Cloud ou self-hosted?

## Opção A — Dify Cloud

### Vantagens

- menor esforço de infraestrutura;
- atualizações gerenciadas;
- implantação mais rápida.

### Desvantagens

- dados passam por ambiente externo;
- mensalidade/plano;
- menor controle de infraestrutura.

## Opção B — Dify self-hosted

### Vantagens

- dados e workflows em infraestrutura do cliente;
- maior controle;
- melhor isolamento operacional.

### Desvantagens

- exige servidor mais robusto;
- atualizações, backup e segurança ficam sob responsabilidade do projeto/cliente.

A documentação do Dify recomenda no mínimo cerca de **2 vCPU e 8 GiB de RAM** para o ambiente Docker.

Para hospedar **Dify + backend + Redis + PostgreSQL + proxy no mesmo servidor**, recomenda-se, em produção:

- 4 vCPU;
- 16 GB RAM;
- SSD de 100 GB ou superior;
- backup externo.

Para MVP de baixo volume, 4 vCPU / 8 GB pode funcionar, porém com menor margem operacional.

---

# 13. WhatsApp

## Recomendação

Utilizar a **WhatsApp Business Platform / Cloud API oficial da Meta**, evitando automações não oficiais baseadas em WhatsApp Web.

### Fluxo

1. usuário envia mensagem;
2. Meta envia webhook;
3. backend valida webhook;
4. evento é deduplicado;
5. conteúdo vai ao Dify;
6. Dify chama Fiscal Gateway;
7. backend devolve dados;
8. resposta é enviada ao WhatsApp.

### Custos

A Meta utiliza cobrança por mensagem entregue conforme:

- país/mercado;
- categoria da mensagem.

Categorias:

- marketing;
- utility;
- authentication;
- service.

Mensagens de serviço dentro da janela de atendimento iniciada pelo usuário possuem condições gratuitas segundo a política atual da plataforma, enquanto outras categorias podem gerar cobrança.

Os valores devem ser conferidos na tabela da Meta na data da implantação.

---

# 14. Segurança

## 14.1 Credenciais

Todas as credenciais devem permanecer **somente no servidor**.

Nunca armazenar em:

- JavaScript do navegador;
- frontend;
- prompt Dify;
- resposta do bot;
- Git;
- GitHub público;
- banco sem proteção;
- logs.

### Secrets mínimos

- META_ACCESS_TOKEN;
- META_APP_SECRET;
- META_VERIFY_TOKEN;
- DIFY_API_KEY;
- RECEITAWS_TOKEN;
- SERPRO_CONSUMER_KEY;
- SERPRO_CONSUMER_SECRET;
- certificados/chaves relacionadas ao e-CNPJ;
- DATABASE_URL;
- REDIS_URL;
- chave interna Dify → Fiscal Gateway.

## 14.2 Armazenamento

Para MVP:

- variáveis de ambiente;
- arquivo `.env` fora do Git;
- permissões restritas no Linux.

Para produção:

- Docker Secrets;
- AWS Secrets Manager;
- HashiCorp Vault;
- outro cofre de secrets.

## 14.3 Comunicação

- HTTPS obrigatório;
- TLS;
- firewall;
- SSH por chave;
- acesso administrativo limitado;
- fail2ban ou equivalente;
- atualização periódica do SO.

---

# 15. LGPD e governança de dados

Apesar de o CNPJ empresarial conter diversos dados públicos, o fluxo pode envolver:

- nome/telefone do usuário do WhatsApp;
- histórico de conversa;
- dados de sócios;
- informações fiscais;
- informações vinculadas a responsáveis;
- documentos e procurações.

### Requisitos recomendados

- política de privacidade;
- definição da finalidade da consulta;
- base legal definida pelo escritório;
- coleta mínima de dados;
- retenção limitada;
- controle de acesso;
- logs de auditoria;
- política de descarte;
- evitar enviar dados fiscais desnecessários ao modelo de IA;
- mascarar dados sensíveis em logs;
- registro de quem consultou qual CNPJ e quando.

### Regra operacional

A IA não deve decidir se uma pessoa “tem direito” a consultar informações protegidas.

A autorização deve ser validada pelo backend/serviço oficial.

---

# 16. Modelo de dados sugerido

## Tabela `consultations`

```text
id
correlation_id
cnpj
source
request_type
status
requested_at
completed_at
response_hash
error_code
whatsapp_contact_hash
```

## Tabela `api_audit`

```text
id
consultation_id
provider
endpoint_alias
http_status
latency_ms
created_at
```

## Tabela `provider_config`

Não armazenar secrets em texto puro.

```text
id
provider
enabled
priority
timeout
max_retries
cache_ttl
```

## Cache

O cache deve possuir TTL diferente por fonte.

Exemplo:

- dados cadastrais: horas/dias;
- tokens OAuth: até expiração;
- situação fiscal: cache curto ou sem cache, conforme natureza;
- dívida ativa: cache curto, conforme requisito do escritório.

---

# 17. Contrato de resposta entre backend e Dify

O Dify não deve receber respostas brutas diferentes de cada fornecedor.

O backend deve devolver um JSON único.

Exemplo:

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
    "has_active_debt": false,
    "debts": []
  },
  "sources": [
    {
      "provider": "SERPRO_CNPJ",
      "status": "ok"
    },
    {
      "provider": "SERPRO_PGFN",
      "status": "ok"
    }
  ],
  "system_diagnosis": {
    "registration": "ACTIVE",
    "pgfn": "NO_ACTIVE_DEBT_RETURNED_BY_SOURCE"
  },
  "ai_interpretation": null,
  "generated_at": "2026-08-20T10:00:00-03:00"
}
```

---

# 18. Regra de IA

## 18.1 Separação obrigatória entre fonte, diagnóstico e interpretação

O Fiscal Gateway deve manter três níveis logicamente separados:

1. **Dado da fonte (`source_data`)** - retorno objetivo obtido da API/serviço externo, preservado e normalizado sem interpretação do LLM.
2. **Diagnóstico do sistema (`system_diagnosis`)** - conclusão determinística produzida por regras de negócio explícitas a partir de dados válidos.
3. **Interpretação da IA (`ai_interpretation`)** - explicação em linguagem natural para o usuário, sempre subordinada aos dois níveis anteriores.

Regras obrigatórias:

- a IA não pode inventar situação cadastral, dívida, enquadramento ou pendência;
- ausência de resposta de uma fonte não significa ausência de problema fiscal;
- campos sem evidência devem retornar `null`, `unknown`, `unavailable` ou equivalente definido no contrato;
- toda resposta fiscal relevante deve indicar a fonte e o status da consulta;
- diagnósticos determinísticos devem ser testáveis e independentes do modelo de linguagem.


O LLM deve ser usado para:

- entender a pergunta;
- conduzir a conversa;
- explicar os dados;
- produzir uma resposta amigável.

O LLM **não deve**:

- inventar situação fiscal;
- inferir dívida;
- inventar regime tributário;
- concluir que não existem pendências quando a API falhar;
- substituir o retorno oficial.

### Exemplo de comportamento correto

Se PGFN estiver indisponível:

> “Não foi possível consultar a Dívida Ativa neste momento.”

E não:

> “Não existem dívidas.”

---

# 19. Tratamento de indisponibilidade

Cada conector deve possuir:

- timeout;
- retry com backoff;
- circuit breaker;
- tratamento de HTTP 401;
- renovação de token;
- tratamento de 403;
- tratamento de 429;
- tratamento de 5xx;
- mensagem segura para o Dify.

### Prioridade/fallback cadastral

Exemplo:

```text
SERPRO CNPJ
    ↓ indisponível
ReceitaWS comercial
    ↓ indisponível
cache válido
    ↓
informar indisponibilidade
```

Nunca substituir uma consulta fiscal protegida por uma inferência.

---

# 20. Resposta às 12 perguntas do cliente

## 1. Quais APIs/fontes oficiais serão utilizadas para consultar o CNPJ?

Arquitetura recomendada:

- ReceitaWS para MVP/consulta cadastral rápida, caso contratada;
- SERPRO Consulta CNPJ V2 como fonte oficial preferencial para cadastro;
- Integra Contador/SITFIS para situação fiscal e pendências;
- SERPRO/PGFN Consulta Dívida Ativa para dívida ativa;
- WhatsApp Business Platform da Meta;
- Dify para orquestração conversacional.

---

## 2. Para a Receita Federal, qual é exatamente o endpoint/API utilizado?

Para a integração oficial privada, usar **Consulta CNPJ V2 do SERPRO**.

Token:

```text
POST https://gateway.apiserpro.serpro.gov.br/token
```

Trial:

```text
GET https://gateway.apiserpro.serpro.gov.br/consulta-cnpj-df-trial/v2/basica/{cnpj}
```

O endpoint produtivo deve ser o disponibilizado no Swagger/Área do Cliente do contrato SERPRO.

Não é recomendado fixar no contrato do projeto o endpoint do Conecta gov.br como se fosse automaticamente o endpoint de uma empresa privada sem antes validar a habilitação.

---

## 3. Para a PGFN, qual API será utilizada?

API oficial **Consulta Dívida Ativa da União – PGFN/SERPRO**.

Base publicada:

```text
https://gateway.apiserpro.serpro.gov.br/consulta-divida-ativa-df/api
```

Consulta lógica por devedor:

```text
GET /v1/devedor/{cnpj}
```

Com autenticação OAuth2/Bearer.

---

## 4. Será API oficial, base própria, scraping ou terceiro?

Estratégia:

1. API oficial;
2. API autorizada de terceiro;
3. cache/base própria para desempenho;
4. scraping apenas se existir requisito futuro não coberto por API e se juridicamente/tecnicamente permitido.

**Scraping não será utilizado no MVP para burlar CAPTCHA, autenticação, certificado ou controle de acesso.**

---

## 5. Se houver API de terceiro, qual empresa e custo?

Fornecedor inicialmente previsto:

**ReceitaWS.**

API pública:

- gratuita;
- até aproximadamente 3 consultas/min;
- dependente do cache do fornecedor.

Exemplo de plano comercial observado em 19/08/2026:

- Ouro: R$ 349/mês;
- 50 consultas/min;
- 600.000 consultas/mês da base;
- 30.000 consultas/mês em tempo real.

Custos SERPRO devem ser contratados diretamente pelo cliente e variam por serviço/faixa de consumo.

---

## 6. Como será feita a autenticação?

Por camada:

### WhatsApp

- token/app credentials da Meta;
- validação do webhook.

### Dify → Backend

- API Key interna;
- opcionalmente HMAC;
- HTTPS;
- rate limit.

### ReceitaWS

- sem autenticação na API pública;
- credencial/token na versão comercial.

### SERPRO Consulta CNPJ / PGFN

- OAuth2;
- Consumer Key;
- Consumer Secret;
- Bearer Token.

### Integra Contador

- credenciais SERPRO;
- certificado e-CNPJ;
- tokens exigidos pela plataforma;
- procuração/autorização quando exigida.

---

## 7. Credenciais ficam somente no servidor?

**Sim.**

O projeto deve manter secrets apenas no ambiente servidor/cofre de secrets.

O Dify só recebe uma chave interna para conversar com o Fiscal Gateway, reduzindo exposição das credenciais SERPRO/ReceitaWS.

---

## 8. POC/homologação antes da segunda parcela

**Sim. Este requisito passa a integrar o escopo comercial.**

Antes da segunda parcela será apresentado um POC com pelo menos um CNPJ real de teste, demonstrando:

```text
CNPJ real
-> Fiscal Gateway
-> conector habilitado
-> fonte disponível
-> retorno da fonte
-> normalização
-> JSON estruturado
```

A fonte do POC poderá ser ReceitaWS ou outra fonte já operacional durante o desenvolvimento. Se as credenciais produtivas do SERPRO já estiverem liberadas, a homologação poderá incluir SERPRO.

### Dependências externas

A homologação produtiva de serviços que dependam de terceiros continua condicionada a:

- credenciais produtivas;
- contratação da API;
- e-CNPJ;
- procuração/autorização quando exigida;
- disponibilidade do fornecedor.

A apresentação do POC não poderá ficar inviabilizada por atraso exclusivo de terceiros: nesses casos será demonstrado o fluxo com uma fonte real já disponível e/ou ambiente homologável, mantendo documentada a pendência externa.

---

## 9. Código-fonte será entregue integralmente?

**Sim, para o código desenvolvido especificamente no projeto.**

Entregar:

- backend Python;
- conectores;
- testes;
- Dockerfile;
- Docker Compose do backend;
- `.env.example`;
- documentação;
- coleção de testes;
- workflows/configurações próprias exportáveis do Dify quando possível.

Não fazem parte da cessão:

- código proprietário de terceiros;
- tokens;
- senhas;
- licenças;
- credenciais;
- infraestrutura de fornecedores.

---

## 10. Servidor, contas e ativos serão do cliente?

**Sim. É requisito de entrega.**

Devem ficar em titularidade do cliente:

- VPS/cloud;
- domínio;
- Meta Business Manager;
- número do WhatsApp;
- Dify;
- conta SERPRO;
- e-CNPJ;
- ReceitaWS;
- banco/backup;
- contas de LLM;
- repositório de código;
- banco de dados;
- backups configurados;
- credenciais e chaves pertencentes à Inaptas.

Na entrega, o contratante deverá possuir acesso administrativo aos ativos de produção que sejam de sua titularidade. Credenciais de terceiros pertencentes ao desenvolvedor não serão transferidas, mas também não serão utilizadas como dependência permanente do ambiente da Inaptas.

---

## 11. Entregáveis dos R$ 2.500

### Escopo MVP recomendado para R$ 2.500

- backend Python/FastAPI;
- endpoint seguro de consulta;
- validação de CNPJ numérico e alfanumérico;
- integração ReceitaWS;
- estrutura de conector SERPRO;
- integração Dify;
- integração WhatsApp, desde que conta/API esteja liberada;
- consulta cadastral;
- situação cadastral, motivo e data da situação;
- indicador atual de Simples Nacional, quando fornecido pela fonte habilitada;
- indicador atual de SIMEI/MEI, quando fornecido pela fonte habilitada;
- estrutura preparada para histórico de inclusão/exclusão do Simples/MEI;
- estrutura de conector PGFN e integração quando houver credenciais;
- interface de conector SITFIS preparada para evolução;
- interface de conector ADE/Editais reservada para futura fonte sustentável;
- separação entre dado da fonte, diagnóstico do sistema e interpretação da IA;
- normalização do JSON;
- tratamento de erros;
- cache básico;
- logs básicos;
- configuração segura de secrets;
- Docker;
- implantação em VPS do cliente;
- homologação;
- demonstração;
- código-fonte;
- documentação básica.

### Pode ser incluído se as credenciais estiverem disponíveis sem aumento relevante de desenvolvimento

- conector Consulta CNPJ SERPRO;
- conector PGFN simples por CNPJ.

### Deve ser explicitamente tratado como extensão/segunda fase se exigir implementação completa

- Integra Contador;
- fluxo de procurações;
- assinatura/certificado;
- SITFIS assíncrono;
- parser de relatório fiscal;
- normalização extensa de obrigações pendentes;
- painel administrativo;
- múltiplos usuários;
- dashboard;
- SLA;
- monitoramento avançado;
- alta disponibilidade.

### Custos não incluídos e de responsabilidade do contratante

| Item | Responsabilidade | Referência / observação |
|---|---|---|
| SERPRO Consulta CNPJ | Contratante | Cobrança variável conforme produto/faixa de consumo |
| SERPRO/PGFN Dívida Ativa | Contratante | Cobrança variável conforme contratação/consumo |
| Integra Contador/SITFIS | Contratante, quando ativado | Cobrança variável; pode exigir e-CNPJ e procurações |
| ReceitaWS | Contratante, se utilizada comercialmente | API pública gratuita com baixo limite; referência do plano Ouro validada em 19/08/2026: R$ 349/mês |
| Certificado e-CNPJ | Contratante | Necessário para determinados serviços oficiais |
| VPS/servidor | Contratante | Dimensionamento conforme Dify, banco e volume |
| Domínio/DNS | Contratante | Se aplicável |
| WhatsApp Business Platform/Meta | Contratante | Cobrança conforme regras vigentes de mensagens |
| Dify Cloud | Contratante, se escolhido | Pode ser substituído por Dify self-hosted |
| LLM | Contratante | Consumo conforme modelo/provedor |
| Banco/backup externo | Contratante | Conforme infraestrutura escolhida |
| E-mail, observabilidade e licenças adicionais | Contratante | Se contratados |

Os R$ 2.500,00 correspondem ao desenvolvimento do MVP e da infraestrutura de integração descrita, não ao consumo dessas plataformas.

---

## 12. Continuará funcionando se Receita ou PGFN alterarem o site?

Se a integração utilizar API, **mudanças visuais no site não afetam diretamente o sistema**.

Porém não é correto garantir funcionamento eterno sem manutenção.

Podem exigir atualização:

- nova versão da API;
- alteração de endpoint;
- descontinuação;
- novo formato de autenticação;
- novo schema;
- mudança de campos;
- mudança de contrato;
- CNPJ alfanumérico;
- política de acesso.

A arquitetura modular reduz o impacto:

```text
Connector ReceitaWS
Connector SERPRO CNPJ
Connector SERPRO SITFIS
Connector PGFN
```

Se uma fonte mudar, atualiza-se o conector correspondente.

---

# 21. Entregáveis técnicos detalhados

## Código

```text
/app
  /api
  /core
  /models
  /schemas
  /services
  /connectors
      receitaws.py
      serpro_cnpj.py
      serpro_pgfn.py
      serpro_integra_contador.py
  /workers
  /tests
```

## Infra

```text
Dockerfile
docker-compose.yml
.env.example
nginx/caddy config
backup script
```

## Documentação

- README;
- instalação;
- configuração;
- variáveis de ambiente;
- autenticação;
- endpoints;
- troubleshooting;
- procedimento de atualização;
- checklist de produção.

---

# 22. Endpoints internos sugeridos

```text
GET /health
POST /v1/company/lookup
POST /v1/company/fiscal-status
POST /v1/company/pgfn
POST /v1/company/full-check
POST /webhooks/whatsapp
```

Exemplo:

```http
POST /v1/company/full-check
Authorization: Bearer INTERNAL_KEY
Content-Type: application/json
```

```json
{
  "cnpj": "12ABC34501DE35"
}
```

---

# 23. Requisitos funcionais

- RF01 — receber mensagem via WhatsApp;
- RF02 — identificar solicitação de consulta;
- RF03 — solicitar CNPJ;
- RF04 — normalizar CNPJ;
- RF05 — validar CNPJ numérico/alfanumérico;
- RF06 — consultar fonte cadastral;
- RF07 — consultar situação cadastral;
- RF08 — consultar PGFN quando habilitado;
- RF09 — consultar situação fiscal quando autorizado;
- RF10 — consolidar dados;
- RF11 — gerar resposta amigável;
- RF12 — informar indisponibilidade sem inventar dados;
- RF13 — registrar auditoria;
- RF14 — impedir exposição de secrets;
- RF15 — aplicar limites/rate limit;
- RF16 — tratar duplicidade de webhook;
- RF17 — permitir trocar fornecedor por configuração;
- RF18 — permitir ativar/desativar fontes.

---

# 24. Requisitos não funcionais

- RNF01 — HTTPS obrigatório;
- RNF02 — secrets apenas no servidor;
- RNF03 — logs sem tokens;
- RNF04 — CNPJ armazenado como string;
- RNF05 — timeout por fornecedor;
- RNF06 — retry controlado;
- RNF07 — cache;
- RNF08 — backup;
- RNF09 — healthcheck;
- RNF10 — rastreabilidade;
- RNF11 — arquitetura modular;
- RNF12 — documentação;
- RNF13 — testes automatizados;
- RNF14 — conformidade LGPD;
- RNF15 — idempotência dos webhooks.

---

# 25. Critérios de aceite

## Consulta cadastral

- CNPJ válido retorna dados normalizados;
- CNPJ inválido é rejeitado;
- CNPJ alfanumérico é aceito;
- timeout não gera resposta falsa.

## WhatsApp

- mensagem chega ao webhook;
- webhook duplicado não gera consultas repetidas;
- Dify recebe contexto;
- resposta volta ao usuário.

## SERPRO

- token é gerado;
- token é renovado;
- 401 é tratado;
- 403 é tratado;
- 429 é tratado.

## Segurança

- nenhuma chave aparece no frontend;
- nenhuma chave aparece nos logs;
- `.env` não é versionado.

## Demonstração / POC

Antes da segunda parcela deve ser demonstrado pelo menos um CNPJ real de teste no fluxo técnico:

```text
CNPJ real
-> Fiscal Gateway
-> conector
-> fonte disponível
-> retorno estruturado
```

Na homologação E2E final, quando as contas externas necessárias estiverem disponíveis:

```text
WhatsApp
-> Dify
-> Backend/Fiscal Gateway
-> fonte de consulta
-> normalizador
-> Dify
-> WhatsApp
```

---

# 26. Testes necessários

## Unitários

- normalização CNPJ;
- dígito verificador;
- parser ReceitaWS;
- parser SERPRO;
- parser PGFN;
- parser SITFIS;
- erros.

## Integração

- ReceitaWS;
- SERPRO trial;
- PGFN trial;
- Dify;
- WhatsApp test number.

## E2E

- cliente envia CNPJ;
- consulta executa;
- resposta final chega;
- logs são registrados.

## Segurança

- secret scanning;
- headers;
- webhook validation;
- rate limit;
- payload inválido;
- tentativa de prompt injection.

---

# 27. Riscos do projeto

## Risco 1 — acesso ao SERPRO

**Impacto:** alto.  
**Mitigação:** trial + contrato em nome do cliente + ReceitaWS para MVP cadastral.

## Risco 2 — procuração eletrônica

**Impacto:** alto para situação fiscal.  
**Mitigação:** mapear clientes autorizados e bloquear consulta quando não houver vínculo.

## Risco 3 — mudança de API

**Impacto:** médio.  
**Mitigação:** conectores isolados e versionados.

## Risco 4 — Dify/LLM inventar informação

**Impacto:** alto.  
**Mitigação:** JSON determinístico e regras que proíbem inferência fiscal.

## Risco 5 — vazamento de dados

**Impacto:** alto.  
**Mitigação:** secrets server-side, TLS, logs mínimos, ACL, LGPD.

## Risco 6 — limite ReceitaWS

**Impacto:** médio.  
**Mitigação:** plano comercial, cache ou SERPRO.

## Risco 7 — CNPJ alfanumérico

**Impacto:** alto em sistemas antigos.  
**Mitigação:** tratar como string desde o início.

## Risco 8 — relatório SITFIS mudar

**Impacto:** médio.  
**Mitigação:** parser desacoplado, testes de regressão e fallback para retorno bruto controlado.

---

# 28. Roadmap recomendado

## Fase 0 — Validação de acessos

- confirmar Meta Business;
- confirmar número WhatsApp;
- confirmar Dify;
- confirmar ReceitaWS;
- confirmar e-CNPJ;
- confirmar contratação SERPRO;
- confirmar procurações.

## Fase 1 — MVP Inaptas

- FastAPI / Fiscal Gateway;
- conectores desacoplados;
- consulta cadastral;
- situação/motivo/data;
- Simples Nacional atual;
- SIMEI/MEI atual;
- estrutura PGFN;
- integração PGFN quando houver credenciais;
- modelo preparado para histórico Simples/MEI;
- interface preparada para SITFIS;
- interface reservada para ADE/Editais;
- separação source_data / system_diagnosis / ai_interpretation;
- Dify;
- WhatsApp;
- normalização;
- logs/auditoria;
- Docker;
- deploy;
- POC com CNPJ real antes da segunda parcela.

## Fase 2 — SERPRO oficial

- OAuth2;
- Consulta CNPJ;
- PGFN;
- retries;
- cache;
- homologação.

## Fase 3 — Fiscal avançado

- Integra Contador;
- SITFIS;
- fila assíncrona;
- parser PDF;
- pendências;
- autorização/procuração.

## Fase 4 — Regulariza.br / expansão modular

- observabilidade;
- alertas;
- backup;
- dashboard;
- relatórios;
- SLA;
- histórico Simples/MEI, quando disponível;
- módulos trabalhista;
- módulos previdenciário;
- conectores estaduais;
- conectores municipais;
- novas fontes fiscais oficiais/autorizadas.

---

# 29. Recomendação comercial para o escopo de R$ 2.500

O valor de **R$ 2.500,00** deve ser apresentado como desenvolvimento do **MVP e infraestrutura de integração**, e não como garantia de acesso ilimitado a toda informação fiscal existente na Receita/PGFN.

### Formulação recomendada

> O valor de R$ 2.500,00 contempla o desenvolvimento do MVP Inaptas, Fiscal Gateway, fluxo WhatsApp/Dify, consulta cadastral, estrutura modular de conectores, normalização, regras determinísticas, preparação para PGFN/SITFIS/ADE conforme escopo, implantação, documentação e POC de homologação antes da segunda parcela. Integrações produtivas dependentes de contratação, certificado digital, procuração, consumo pago ou liberação por terceiros serão ativadas quando os acessos forem fornecidos. Custos de API, certificado e infraestrutura são de responsabilidade do contratante.

Isso evita que o projeto assuma risco por atrasos ou restrições do SERPRO, Receita, PGFN, Meta ou outros fornecedores.

---

# 30. Manutenção e continuidade

Nenhum sistema dependente de APIs externas deve ser vendido com promessa de funcionamento indefinido sem manutenção.

Recomenda-se manutenção mensal para:

- atualização de APIs;
- alterações de schema;
- renovação de integrações;
- atualização de containers;
- patches de segurança;
- monitoramento;
- correção de mudanças no WhatsApp/Dify;
- testes após atualizações SERPRO.

A manutenção deve ser contratada separadamente do desenvolvimento inicial.

---

# 31. Resposta técnica final de viabilidade

## Viável

- WhatsApp → Dify → Python;
- consulta cadastral;
- ReceitaWS;
- SERPRO Consulta CNPJ;
- PGFN;
- cache;
- normalização;
- deploy no servidor do cliente;
- código-fonte entregue.

## Viável com pré-requisitos

- SITFIS;
- situação fiscal;
- pendências;
- obrigações;
- dados protegidos.

Pré-requisitos:

- e-CNPJ;
- contrato SERPRO;
- autorização/procuração;
- credenciais corretas.

## Não recomendado

- scraping como mecanismo principal;
- automação de login e-CAC;
- quebra/bypass de CAPTCHA;
- guardar certificado em frontend;
- expor Consumer Secret ao Dify;
- inferir dados fiscais pelo LLM.

---

# 32. Fontes técnicas consultadas

## Receita Federal / SERPRO

- Consulta CNPJ — Catálogo gov.br  
  https://www.gov.br/conecta/catalogo/apis/consulta-cnpj

- Documentação API Consulta CNPJ — SERPRO  
  https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-cnpj/

- Guia de autenticação API CNPJ  
  https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-cnpj/pt/quick_start/

- CNPJ alfanumérico — Receita Federal / SERPRO  
  https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/cnpj-alfanumerico

## PGFN

- Consulta Dívida Ativa da União — Catálogo gov.br  
  https://www.gov.br/conecta/catalogo/apis/consulta-divida-ativa-da-uniao

- Documentação Consulta Dívida Ativa — SERPRO  
  https://apicenter.estaleiro.serpro.gov.br/documentacao/consulta-divida-ativa/pt/

## Integra Contador

- Integra Contador — documentação oficial  
  https://apicenter.estaleiro.serpro.gov.br/documentacao/api-integra-contador/

- SITFIS  
  https://apicenter.estaleiro.serpro.gov.br/documentacao/api-integra-contador/pt/solucoes/integra-sitfis/sitfis/

## ReceitaWS

- API  
  https://receitaws.com.br/api

- Site/planos  
  https://www.receitaws.com.br/

## Dify

- API  
  https://docs.dify.ai/en/api-reference/guides/get-started

- Self-host/Docker Compose  
  https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose

## WhatsApp

- WhatsApp Business Platform Pricing  
  https://business.whatsapp.com/products/platform-pricing

## LGPD / compartilhamento fiscal

- Compartilhamento de dados fiscais — gov.br  
  https://www.gov.br/pt-br/servicos/autorizar-o-compartilhamento-de-dados-fiscais

---

# 33. Decisões fechadas para início do desenvolvimento

As decisões abaixo passam a compor o escopo fechado do MVP:

1. O produto inicial será o **Inaptas**, desenvolvido como primeiro módulo de uma arquitetura evolutiva para o **Regulariza.br**.
2. O núcleo será um **Fiscal Gateway próprio**, desacoplado do Dify e dos fornecedores externos.
3. Cada fonte será implementada através de conector independente, substituível sem reconstrução da aplicação.
4. O MVP deverá retornar situação cadastral, motivo, data da situação, Simples Nacional atual, SIMEI/MEI atual e PGFN quando habilitada.
5. O modelo ficará preparado para histórico de inclusão/exclusão do Simples Nacional e SIMEI/MEI, sem inventar dados que a fonte não disponibilize.
6. O Fiscal Gateway separará explicitamente `source_data`, `system_diagnosis` e `ai_interpretation`.
7. A IA não poderá inferir situação fiscal, dívida, regime, pendência ou ausência de problema sem evidência de fonte válida.
8. A implementação completa do SITFIS fica para evolução, mas a arquitetura/conector deve estar preparada desde o MVP.
9. ADE/Editais não utilizará bypass de CAPTCHA, scraping agressivo ou contorno de proteção; ficará como conector futuro se houver fonte oficial/sustentável.
10. Custos de SERPRO, APIs, certificado, servidor, WhatsApp, Dify, LLM e serviços de terceiros são do contratante e ficam fora dos R$ 2.500,00.
11. Código-fonte, repositório, servidor, banco, documentação e credenciais das contas pertencentes à Inaptas deverão ficar acessíveis ao contratante na entrega.
12. Antes da segunda parcela será apresentado POC/homologação com pelo menos um CNPJ real, demonstrando CNPJ -> Fiscal Gateway -> fonte -> retorno estruturado.
13. Se uma fonte produtiva depender de liberação de terceiro ainda não concluída, o POC utilizará outra fonte real já disponível e a dependência será documentada.
14. A arquitetura futura deverá permitir inclusão de módulos Receita, PGFN, trabalhista, previdenciário, estadual e municipal.

---

# 34. Escopo comercial consolidado

## Valor do desenvolvimento

**R$ 2.500,00** pelo desenvolvimento do MVP descrito neste documento.

## Condição de homologação

A apresentação do POC técnico com CNPJ real ocorrerá antes da segunda parcela. A ativação produtiva de serviços dependentes de SERPRO, certificado, procuração ou outras liberações externas ocorrerá conforme disponibilização dos acessos pelo contratante.

## Propriedade e portabilidade

O projeto deverá ser entregue de forma portável, documentada e sem dependência permanente de contas pessoais do desenvolvedor. Os ativos pertencentes à Inaptas devem permanecer sob titularidade e controle do contratante.

## Fora do valor do desenvolvimento

Licenças, consumo de APIs, certificados digitais, hospedagem, Meta/WhatsApp, Dify, LLM, domínios, backups e outros serviços de terceiros.

---

# 35. Status final

**PROJETO APROVADO PARA INÍCIO DO MVP - ESCOPO TÉCNICO FECHADO, COM DEPENDÊNCIAS EXTERNAS FORMALIZADAS E ARQUITETURA PREPARADA PARA EVOLUÇÃO AO REGULARIZA.BR.**
