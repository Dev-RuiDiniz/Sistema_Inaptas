# Acessos e contas do Sistema Inaptas

**Atualizado em:** 08/10/2026
**Responsável pelas contas de produção:** Inaptas/contratante.
**Este arquivo é um inventário, não um cofre de senhas.**

## Regra de segurança

Não coloque neste repositório senhas, tokens, chaves, certificados, códigos de recuperação, cookies, dados de clientes ou CNPJs reais. O repositório está no GitHub; qualquer segredo incluído em um documento versionado deve ser tratado como exposto.

Guarde credenciais em um gerenciador de senhas da empresa e segredos de execução em um secret manager ou no ambiente protegido do servidor. Compartilhe acesso por convite individual, com o menor nível de permissão necessário. Não envie senhas em grupos, arquivos exportados ou mensagens.

## Inventário

| Sistema/conta | Situação conhecida | O que falta | Onde guardar o acesso |
|---|---|---|---|
| Site `inaptas.com.br` | O áudio de 19/08 descreve o site como origem da captação de leads. O site não está neste repositório. | Confirmar responsável, domínio, formulário e como os leads chegam ao atendimento. Definir se haverá integração com o Gateway. | Acesso individual ao provedor/site; credenciais no cofre da empresa. |
| GitHub — `Dev-RuiDiniz/Sistema_Inaptas` | Repositório existe e contém o código do projeto. | Confirmar que os responsáveis da Inaptas têm acesso administrativo e que a titularidade/continuidade está alinhada com o contrato. | Contas individuais do GitHub; nunca compartilhar senha. |
| Meta Business / WhatsApp Cloud API | A conversa registra que a integração Meta/WhatsApp ainda precisava ser feita e contratada em 29/09/2026. | Confirmar Business Manager, número, aplicativo, WABA ID, Phone Number ID, webhook, permissões e custos vigentes. | Tokens no secret manager do servidor; IDs não secretos podem ser anotados no inventário operacional privado. |
| BotConversa | O áudio de 19/08 relata que já era usado para atendimento pré-venda. O acesso foi compartilhado em texto no grupo em 06/10/2026. | Trocar a senha, revogar sessões antigas, ativar MFA e definir como ligar o atendimento existente ao Gateway. Ainda não há integração BotConversa no código. | Gerenciador de senhas da empresa; acesso individual por convite quando disponível. Não registrar o login nem a senha aqui. |
| n8n | O workflow está versionado, mas inativo; o código prevê n8n self-hosted. | Configurar instância, domínio, usuários e credenciais antes de ativar o fluxo. | Credenciais do n8n e chave de criptografia no ambiente protegido; não no JSON do workflow. |
| Ollama | Previsto em container local para explicação opcional. | Baixar e validar o modelo no ambiente do cliente; sem a IA, manter resposta determinística. | Não exige credencial de API no arranjo local previsto; proteger o acesso de rede. |
| Dify | Aparece no escopo inicial de agosto, mas não é o orquestrador implementado no repositório atual. | Confirmar que a arquitetura vigente permanece Meta + n8n + Ollama. Não criar nova dependência antes dessa decisão. | Não fornecer credenciais até a decisão de arquitetura. |
| SERPRO Consulta CNPJ / PGFN | A equipe reportou um teste de integração bem-sucedido em 29/09, sem identificar no registro qual serviço/ambiente foi testado. Em 06/10, a contratação SERPRO ainda não havia sido feita. | Contratar em nome da Inaptas, confirmar o produto e endpoint do contrato, obter credenciais novas e homologar com autorização. | Consumer Key/Secret ou token no secret manager; e-CNPJ em custódia controlada. |
| SERPRO PGFN trial | Existe conector `serpro_trial`, desativado por padrão. Ele chama um CPF de teste fixo, não o CNPJ informado. | Usar apenas em ambiente de homologação com token de teste novo. Nunca habilitar como consulta de cliente ou produção. | Token temporário no secret manager de homologação; revogar depois do teste. |
| e-CNPJ e procurações | O escopo exige e-CNPJ para determinados serviços e procuração/autorização para dados protegidos. | Confirmar certificado válido, titular, responsável, serviços contratados e CNPJs autorizados. | Certificado e chave privada em cofre/custódia formal; não copiar para o Git, chat ou container sem proteção. |
| ReceitaWS | Provider alternativo existe no código; não há confirmação de contratação comercial no material recebido. | Escolher plano, limites e uso permitido; confirmar se será usado em homologação ou produção. | Token, se contratado, somente no secret manager do Gateway. |
| Minha Receita | Provider cadastral self-hosted previsto, com carga periódica de dados públicos e necessidade aproximada de 180 GB na carga inicial. | Disponibilizar armazenamento, fixar versão da imagem, executar carga e validar atualização mensal. | Acesso de infraestrutura por usuários individuais; sem senha em documentação. |
| Portal da Transparência | Provider CEIS/CNEP/CEPIM existe e fica desativado por padrão. | Solicitar token oficial e homologar somente quando necessário. | Token somente no secret manager do Gateway. |
| DOU / INLABS | Em 17/09/2026 foi aprovada a direção de importar publicações estruturadas para localizar ADE. | Definir ingestão, atualização, matching por CNPJ, rastreabilidade e tratamento de publicações ausentes. A implementação ainda está pendente. | Fonte pública estruturada; qualquer chave de serviço eventualmente exigida ficará no secret manager. |
| VPS, domínio e TLS | Ambiente de produção do cliente não foi confirmado no material disponível. | Escolher provedor, reservar domínio, firewall, backups, monitoramento e ambiente separado de homologação. | Administração por chaves individuais; segredos no cofre do provedor. |
| Login OIDC do painel | O painel requer OIDC, mas não há issuer, client ou grupos reais documentados. | Definir provedor de identidade, usuários autorizados, papéis, callback e política de sessão. | `OIDC_CLIENT_SECRET` no secret manager; IDs e URLs podem ficar na configuração privada do ambiente. |
| CNPJ da POC | Nenhum CNPJ autorizado deve ser armazenado no repositório. | Obter autorização escrita, responsável, finalidade e validade antes de qualquer teste real. | Guardar apenas no ambiente de homologação controlado, com acesso restrito e retenção definida. |

## Ações imediatas

1. **Trocar a senha do BotConversa agora**, encerrar as sessões existentes e ativar MFA. A senha foi compartilhada em texto numa conversa exportada; não a reutilize nem a copie para este arquivo.
2. Criar acessos individuais para cada pessoa da equipe. Evitar uma senha compartilhada entre cliente e fornecedores.
3. Definir se o BotConversa já usado na pré-venda será conectado ao Gateway ou se o atendimento passará pelo fluxo Meta WhatsApp Cloud API + n8n que existe no código. Não configurar as duas rotas em paralelo antes dessa decisão.
4. Contratar SERPRO e e-CNPJ em nome da Inaptas, se o cliente decidir ativar consultas oficiais. Em 06/10/2026, o contrato SERPRO ainda estava pendente.
5. Emitir credenciais novas para homologação. Não reutilizar token que tenha sido enviado em chat ou exposto em documentação.
6. Definir domínio/VPS, OIDC e um CNPJ real autorizado para a POC; registrar somente o status e o responsável neste inventário.

## Como preencher este inventário

Registre apenas: nome do sistema, titular da conta, responsável interno, estado (`pendente`, `configurado`, `homologado`), data da última revisão e próximo passo. Não registre valores de senhas, tokens, certificados, CNPJs de clientes ou respostas fiscais.
