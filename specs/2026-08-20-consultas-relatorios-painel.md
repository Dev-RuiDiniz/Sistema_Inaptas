# Spec — Consultas, histórico e relatórios do painel

**Status:** aprovada para implementação.

## Objetivo

Permitir consulta manual de CNPJ, visualização do histórico do escritório e
exportação segura de resultados normalizados em PDF e CSV.

## Requisitos

- O formulário aceitará CNPJ numérico, mascarado e alfanumérico.
- A consulta usará os casos de uso do Fiscal Gateway diretamente no servidor.
- O navegador nunca receberá o Bearer token interno.
- O resultado armazenado será o contrato normalizado, sem payload bruto de
  fornecedor ou segredo.
- Histórico terá filtros por CNPJ, período, solicitante, diagnóstico e status
  de fonte, com paginação e ordenação recente.
- Todos os operadores visualizarão somente dados da própria organização.
- PDF e CSV conterão fonte, status, horário e diagnóstico.
- Indisponibilidade será preservada como indisponibilidade/desconhecimento.
- A retenção inicial será de 90 dias e configurável pelo administrador.

## Rotas

```text
GET  /painel/consultas
GET  /painel/consultas/nova
POST /painel/consultas/nova
GET  /painel/consultas/{id}
GET  /painel/consultas/{id}/relatorio.pdf
GET  /painel/consultas/{id}/relatorio.csv
GET  /painel/admin/configuracoes
POST /painel/admin/configuracoes/retencao
```

## Dados

- `organizations`: organização e política de retenção.
- `consultations`: consulta, origem, organização e usuário solicitante.
- `consultation_results`: resposta canônica JSONB.
- `panel_audit`: exportações, consultas e alterações administrativas.

## Critérios de aceite

- Consulta válida exibe dados cadastrais, fontes e diagnóstico.
- CNPJ inválido retorna erro seguro sem chamar provider.
- Provider indisponível não vira ausência de dívida ou pendência.
- Consulta de outra organização retorna 404/403 sem revelar existência.
- PDF e CSV não contêm Authorization, tokens, secrets ou `source_data` bruto.
- Dados vencidos pela retenção podem ser removidos pelo comando operacional.

