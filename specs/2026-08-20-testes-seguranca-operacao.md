# Spec — Testes, segurança e operação pré-credenciais

**Status:** aprovada para implementação.

## Objetivo

Aumentar a confiança no fluxo fiscal sem credenciais externas, cobrindo
contratos, indisponibilidade, idempotência, autenticação, configuração segura,
logs redigidos e operação local reproduzível.

## Não escopo

- Consultar serviços externos reais.
- Homologar contratos SERPRO, PGFN, Meta ou Dify sem documentação e acessos do
  contratante.
- Alterar o contrato público das rotas existentes sem spec adicional.

## Requisitos

- Toda nova mudança comportamental deve seguir ciclo TDD red-green-refactor.
- Provider indisponível não pode produzir diagnóstico de ausência de dívida ou
  pendência.
- PGFN, SITFIS e ADE/Editais permanecem `disabled` sem configuração válida.
- Produção não pode usar token interno padrão, OpenAPI habilitado ou `*` em
  Trusted Hosts.
- Secrets e Authorization não podem aparecer em logs, scripts ou arquivos
  versionados.
- Fixtures devem usar somente dados sintéticos.

## Cenários obrigatórios

- CNPJ numérico, alfanumérico e inválido.
- ReceitaWS com resposta válida, timeout, indisponibilidade e JSON inválido.
- Dify e WhatsApp sem credenciais.
- Assinatura Meta inválida e webhook duplicado.
- Rate limit, autenticação e correlation ID.
- PostgreSQL/Redis disponíveis e indisponíveis.

## Critérios de aceite

- Suíte mockada passa sem rede externa.
- Testes de integração podem ser executados contra Compose local.
- Verificação de segurança não encontra credenciais em arquivos versionados.
- Healthcheck não expõe detalhes de exceções ou URLs sensíveis.
- README e guia operacional permitem que outro desenvolvedor reproduza o
  fluxo local.

## Rollback e publicação

- Cada tarefa possui commit independente em branch de funcionalidade.
- Se uma verificação final falhar, a branch não será publicada.
- O push final será somente para
  `origin/funcionalidade/validacao-pre-credenciais`.

