# Fluxograma do Sistema Inaptas

**Atualizado em:** 08/10/2026
**Objetivo:** mostrar o caminho da consulta do início ao fim e deixar visível o que já existe, o que ainda depende de acesso externo e o que é evolução futura.

## Em uma frase

O cliente chega pelo site ou pelo atendimento, informa um CNPJ, e o Fiscal Gateway consulta apenas as fontes habilitadas. O sistema organiza os retornos e explica o que foi confirmado. Se uma fonte falhar, diz que não conseguiu consultar.

## Jornada comercial relatada pelo cliente

No áudio de 19/08, o cliente descreve o site `inaptas.com.br` como origem dos
leads e o BotConversa como ferramenta já usada no atendimento de pré-venda. A
ideia é adicionar consultas e IA para ajudar nesse atendimento e encaminhar os
casos que precisam de uma pessoa. Essa integração ainda não existe no código e
precisa ser detalhada e homologada.

```mermaid
flowchart LR
    LEAD[Pessoa interessada] --> SITE[Site inaptas.com.br<br/>capta o lead]
    SITE --> BOT[BotConversa<br/>atendimento pré-venda existente]
    BOT -.->|integração desejada, pendente| GW[Fiscal Gateway]
    GW --> CONSULTA[Consulta de fontes habilitadas]
    CONSULTA --> BOT
    BOT --> HUMANO[Equipe assume quando necessário]
```

## Fluxo previsto no código atual

O diagrama abaixo representa o caminho que o repositório implementa para
Meta/WhatsApp + n8n e para o painel. O workflow n8n está inativo e os serviços
externos ainda precisam de homologação. BotConversa e o site não estão ligados
ao Gateway neste momento.

```mermaid
flowchart TD
    C[Cliente] --> WA[WhatsApp Business]
    WA --> META[Meta Cloud API]
    META --> WH[Webhook do Fiscal Gateway]
    WH --> SIG{Assinatura válida?}
    SIG -- Não --> REJ[Rejeitar evento]
    SIG -- Sim --> DUP{Evento repetido?}
    DUP -- Sim --> DESC[Descartar duplicata]
    DUP -- Não --> N8N[n8n conduz a conversa<br/>workflow ainda inativo]
    N8N --> CNPJ[Identificar e validar CNPJ]
    CNPJ --> API[POST /v1/orchestrator/company/full-check]

    OP[Operador do escritório] --> OIDC[Login OIDC<br/>aguarda configuração do cliente]
    OIDC --> PAINEL[Painel operacional]
    PAINEL --> MANUAL[Consulta manual de CNPJ]
    MANUAL --> API

    API --> GATE[Regras do Fiscal Gateway]
    GATE --> CAD[Provider cadastral<br/>selecionado explicitamente]
    CAD --> MR[Minha Receita<br/>snapshot local mensal]
    CAD --> RWS[ReceitaWS<br/>API externa]

    GATE --> PGFN[Provider PGFN<br/>desligado por padrão]
    PGFN --> TRIAL[SERPRO trial<br/>CPF de teste fixo]
    PGFN --> OFICIAL[Consulta oficial PGFN<br/>contrato e homologação pendentes]

    GATE --> COMP[Compliance opcional<br/>desligado por padrão]
    COMP --> PT[Portal da Transparência<br/>CEIS, CNEP e CEPIM]

    GATE --> SITFIS[SITFIS<br/>evolução futura]
    GATE --> ADE[ADE: importar dados estruturados<br/>DOU/INLABS — aprovado, ainda não implementado]

    MR --> NORM[Normalizar retornos e status das fontes]
    RWS --> NORM
    TRIAL --> NORM
    OFICIAL --> NORM
    PT --> NORM
    SITFIS --> NORM
    ADE --> NORM
    NORM --> DIAG[Diagnóstico determinístico]
    DIAG --> IA[Ollama opcional explica os dados<br/>sem inventar informações]
    IA --> RES[Resposta e relatório com fonte, status e horário]
    RES --> ENVIA[Enviar resposta pelo canal configurado]
    ENVIA --> WA
    RES --> PAINEL

    NORM --> FALHA{Fonte indisponível ou desligada?}
    FALHA -- Sim --> DESCONHECIDO[Marcar como desconhecido/indisponível<br/>Nunca como “sem dívida”]
    DESCONHECIDO --> RES

    classDef implementado fill:#d9ead3,stroke:#38761d,color:#111;
    classDef pendente fill:#fff2cc,stroke:#bf9000,color:#111;
    classDef futuro fill:#d9eaf7,stroke:#3d85c6,color:#111;
    classDef alerta fill:#f4cccc,stroke:#990000,color:#111;
    class GATE,CAD,MR,RWS,NORM,DIAG,PAINEL,COMP,PT implementado;
    class META,WH,N8N,OIDC,MANUAL,OFICIAL pendente;
    class SITFIS,ADE futuro;
    class TRIAL,DESCONHECIDO alerta;
```

## Como ler as cores

- **Verde:** capacidade implementada no código. Isso não significa que a conta externa esteja configurada ou homologada.
- **Amarelo:** depende de conta, domínio, credencial, contrato ou homologação externa.
- **Azul:** planejado para uma fase posterior.
- **Vermelho:** cuidado especial. O trial PGFN consulta um documento de teste fixo e **não consulta o CNPJ enviado pelo usuário**.

## Regras que valem em todos os caminhos

1. `source_data` registra o que veio da fonte; `system_diagnosis` aplica regras determinísticas; `ai_interpretation` apenas explica o resultado.
2. Um provider desativado, uma falha ou uma resposta incompleta significa **desconhecido**, nunca “regular” ou “sem dívida”.
3. Minha Receita e ReceitaWS são escolhidos por configuração. Não existe troca automática silenciosa entre elas.
4. O provider `serpro_trial` fica desativado por padrão e serve somente para homologação. Nunca habilite esse trial como consulta real de empresas.
5. CEIS/CNEP/CEPIM são registros de sanções e impedimentos; não são PGFN, CND nem prova de regularidade fiscal.
6. SITFIS exige contrato, e-CNPJ e autorização/procuração quando aplicável. Para ADE, a direção aprovada é consumir dados estruturados do DOU/INLABS. CAPTCHA não será contornado.

## Estado de execução

O Gateway e o painel existem no repositório. O workflow do n8n está exportado, mas ainda inativo. A entrada Meta/WhatsApp, o login OIDC, os providers pagos e a consulta oficial SERPRO/PGFN precisam de configuração e homologação do cliente antes da produção. A [matriz de acessos](ACESSOS.md) mostra cada pendência.
