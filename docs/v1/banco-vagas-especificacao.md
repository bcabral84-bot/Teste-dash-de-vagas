# Banco de Vagas Internacionais: prompt e especificação

Versão de 12/10/2026. Documento de referência da interface publicada como "Banco de Vagas Internacionais", usada como material extra de uma consultoria de recolocação profissional. Acompanha dois arquivos: `banco-vagas-internacionais.html` (código da página) e `banco-vagas-dados-2026-10-12.json` (dados atuais).

---

## Parte 1. Prompt pronto para usar

Copie o bloco abaixo inteiro no início de uma conversa com o Claude (ou outra IA) para recriar, manter ou atualizar o banco. Anexe os dois arquivos que acompanham este documento.

```
Você vai manter o "Banco de Vagas Internacionais", uma página web usada como material de apoio
de uma consultoria de recolocação profissional. Anexei o código atual (HTML) e os dados atuais (JSON).
Siga a especificação abaixo à risca.

OBJETIVO
Mostrar a candidatos brasileiros vagas remotas em Projetos, Agilidade e Delivery abertas a quem mora
no Brasil, principalmente para empresas e clientes dos EUA, e as empresas que mais contratam esse
perfil a partir daqui. O candidato precisa entender elegibilidade, contrato e faixa salarial ANTES de
se candidatar.

ESCOPO DE FUNÇÕES (códigos)
SM = Scrum Master | AC = Agile Coach | PM = Project Manager | PGM = Program Manager | DM = Delivery Manager

COMO PESQUISAR VAGAS
1. Fontes: página de vagas da própria empresa (Greenhouse, Lever, Ashby, Workable, Workday, iCIMS),
   agregadores remotos (Remote Rocketship, Himalayas, Jobgether) e o conector do Indeed.
   Nunca raspe o LinkedIn nem use automação dentro dele.
2. Só entra vaga que aceite quem mora no Brasil: Brasil citado, LATAM, ou qualquer país.
   "LATAM" sem citar o Brasil entra com a observação "Brasil não citado".
3. Sempre que possível, o link salvo é o do anúncio original no site da empresa, não o do agregador.
4. Para cada vaga registre: cargo exato, empresa, função (código), mercado (intl ou br), elegibilidade,
   contrato, inglês exigido, senioridade, data de publicação (AAAA-MM-DD), link, observação curta
   com o que a vaga exige de diferente, status e data da conferência.
5. Status: "ativa" quando conferida no site original; "conferir" quando tem mais de 30 dias,
   foi vista só em agregador ou pode ter encerrado; "encerrada" quando o anúncio saiu do ar.
6. Mercado "intl" = empresa estrangeira ou cliente estrangeiro. Mercado "br" = empresa brasileira
   atendendo o mercado local.

REFERÊNCIA SALARIAL (obrigatória em todo card)
Quatro linhas, sempre nesta ordem:
- Anúncio: a faixa declarada pela empresa, convertida para R$/mês. Se não houver: "Faixa não declarada".
- Cargo no Brasil: média do TÍTULO MAIS PRÓXIMO da vaga no Glassdoor Brasil (salário base mensal),
  não da função genérica. Ex.: IT Project Manager usa "Gerente de Projetos de TI".
- Mesma empresa: média da própria empresa para o cargo (Indeed Brasil, Glassdoor ou Indeed EUA,
  dizendo qual). Se não houver dado público: "Sem dados públicos desta empresa".
- Mesmo cargo nos EUA: média do título no Glassdoor EUA, em US$/ano e convertida para R$/mês.
  Para vaga do mercado brasileiro: "Não se aplica, vaga do mercado brasileiro".
Regras: mostre fonte, link e número de relatos de cada valor. Nunca invente ou estime um número
sem fonte. Converta com a cotação do dólar comercial do dia (guardada em meta/fx) e 160 horas por mês
para valores por hora. A linha dos EUA é teto de negociação, não expectativa para quem trabalha
do Brasil. Contrato em dólar não se compara direto com CLT (sem 13º, férias pagas e FGTS).

BANCO DE EMPRESAS
Entra empresa que contrata no Brasil para cliente estrangeiro, com evidência (vaga real) ou presença
conhecida. Campos: nome, categoria, sede, porte, onde contrata, modelo de contratação, funções,
página de vagas, frase curta de por que é ponto de contato. NÃO registre nomes de recrutadores
ou de qualquer pessoa: a página é compartilhada com clientes (LGPD). O contato é feito pelo botão
"Buscar recrutadores", que abre a busca do LinkedIn com o nome da empresa.

PERMISSÕES
Clientes só leem. Só o dono e editores escrevem (adicionar vaga, mudar status).

TEXTO
Português do Brasil, frases curtas e diretas, sem jargão. Nunca use travessão (—) entre frases:
use vírgula, dois-pontos ou ponto final. Não use "não é X, é Y" nem frases de efeito.

ENTREGA DE CADA ATUALIZAÇÃO
Diga: quantas vagas entraram, quantas mudaram de status, quais referências salariais mudaram,
e o que não foi possível conferir. Liste as fontes com links.
```

---

## Parte 2. Especificação completa

### 2.1 Objetivo e público

- **Para que serve:** material extra de uma consultoria de recolocação. Não é produto comercial.
- **Quem lê:** candidatos (clientes da consultoria) que buscam vagas remotas em Projetos, Agilidade e Delivery, pagas em moeda estrangeira ou para clientes estrangeiros.
- **Quem edita:** o consultor (dono da página) e quem ele tornar editor.
- **Pergunta que a página responde:** "Quais vagas eu posso disputar morando no Brasil, quanto elas pagam e quem contrata esse perfil?"

### 2.2 Escopo atual

| Item | Situação em 12/10/2026 |
|---|---|
| Funções | Scrum Master, Agile Coach, Project Manager, Program Manager, Delivery Manager |
| Onde o candidato está | Brasil (todas as vagas aceitam quem mora no Brasil) |
| Modelo | Remoto (uma vaga híbrida em São Paulo) |
| Mercados | Cliente internacional (20 vagas) e mercado Brasil (4 vagas) |
| Volume | 24 vagas, 23 empresas, 5 referências por função |
| Fora do escopo por enquanto | Vagas com relocation, vagas que exigem morar fora, funções RTE, Product Owner e PMO |

### 2.3 Estrutura da página, de cima para baixo

1. **Cabeçalho:** rótulo "Recolocação internacional · Projetos, Agilidade e Delivery", título "Banco de Vagas Internacionais" e uma frase explicando o conteúdo.
2. **Faixa de números:** vagas ativas, vagas para cliente internacional, empresas no banco, data da última conferência.
3. **Abas:** Vagas e Empresas. O link com `#empresas` abre direto na aba Empresas.
4. **Aba Vagas:**
   - Filtro de função em botões: Todas, Scrum Master, Agile Coach, Project Manager, Program Manager, Delivery Manager.
   - Seletor de mercado: Todos, Cliente internacional (padrão), Mercado Brasil.
   - Caixa "Mostrar encerradas" (desmarcada por padrão).
   - Busca por texto no cargo e na empresa.
   - Painel de abrir e fechar "Referências salariais por função (mercado Brasil)", com tabela e nota de método.
   - Lista de cards de vaga.
5. **Aba Empresas:** filtro por categoria, gerado a partir das categorias cadastradas, e grade de cards de empresa.
6. **"Como usar este banco":** quatro orientações fixas (conferir elegibilidade, candidatar-se no site da empresa, adicionar 3 a 6 recrutadores por empresa, priorizar vagas recentes).
7. **Área de edição "Adicionar vaga":** visível só para editores.

### 2.4 Card de vaga

**Ordem dos elementos:**
1. Cargo exato do anúncio, em destaque.
2. Empresa (com "· mercado Brasil" quando for o caso).
3. Etiquetas: função, elegibilidade, contrato, inglês exigido, senioridade. Etiqueta vazia não aparece.
4. Observação curta: o que a vaga exige de diferente (certificação, idioma extra, fuso, viagens).
5. Bloco "Referência salarial", com as quatro linhas descritas na seção 2.6.
6. Lateral: status, data de publicação com dias desde a publicação, botão "Ver vaga".

**Ordenação:** encerradas por último; dentro das demais, as mais recentes primeiro.

**Status:**

| Status | Cor | Quando usar |
|---|---|---|
| Ativa | verde | Conferida no anúncio original |
| Conferir no site | âmbar | Mais de 30 dias, vista só em agregador ou pode ter encerrado |
| Encerrada | cinza, card esmaecido | Anúncio fora do ar. Oculta por padrão |

Editores mudam o status tocando nele (ativa, conferir, encerrada, ativa). A mudança grava a data de conferência do dia.

### 2.5 Card de empresa

- **Topo:** nome e categoria.
- **Texto:** uma frase de por que a empresa é ponto de contato.
- **Lista de dados:** Sede, Porte, Contrata (onde), Modelo (CLT, contractor, contrato), Funções, Vagas no banco (contagem automática das vagas não encerradas ligadas à empresa).
- **Botões:** "Página de vagas" (quando houver) e "Buscar recrutadores", que abre a busca de pessoas do LinkedIn com "nome da empresa + recruiter + LATAM".

**Categorias em uso:** Staffing americano, Nearshore, Consultoria, Consultoria de dados, Consultoria digital, Software (contratação direta), Agência digital americana, Rede de talentos, Serviços de TI.

### 2.6 Regras da referência salarial

**As quatro linhas do card:**

| Linha | Fonte | Regra | Texto quando falta |
|---|---|---|---|
| Anúncio | O próprio anúncio | Valor original e conversão para R$/mês | "Faixa não declarada" |
| Cargo no Brasil | Glassdoor Brasil | Título mais próximo da vaga, salário base mensal (faixa) | "Sem referência pública" |
| Mesma empresa | Indeed Brasil, Glassdoor ou Indeed EUA | Dizer a fonte e o país do dado | "Sem dados públicos desta empresa" |
| Mesmo cargo nos EUA | Glassdoor EUA | US$/ano e conversão para R$/mês | "Sem referência" ou "Não se aplica, vaga do mercado brasileiro" |

**Regras gerais:**
- Todo valor mostra fonte, link e número de relatos.
- Nunca inventar, arredondar para cima ou estimar valor sem fonte. Sem dado, mostrar o texto de ausência.
- Amostras pequenas (menos de 10 relatos) ficam visíveis como estão; o número de relatos ao lado já alerta o leitor.
- **Conversão:** dólar comercial do dia, guardado em `meta/fx`. Por hora vezes 160 horas para chegar ao mês. Por ano dividido por 12.
- **Nota fixa da página:** a linha dos EUA é o que ganha quem mora lá, serve de teto para negociar e não de expectativa. Contrato em dólar não tem 13º, férias pagas nem FGTS, então precisa pagar mais para empatar com CLT.

**Correspondência de títulos usada hoje (Glassdoor Brasil):**

| Título da vaga | Título de referência |
|---|---|
| IT Project Manager, IT Project and Delivery Manager | Gerente de Projetos de TI |
| Technical Project Manager, Project Manager (Software) | Technical Project Manager |
| Senior Project Manager, Senior Digital PM | Senior Project Manager |
| Digital Project Manager | Digital Project Manager |
| Project Manager genérico | Gerente de Projetos |
| Program Manager, Data Program Manager | Program Manager |
| Delivery Manager, Technical Delivery Manager | Delivery Manager |
| Senior Delivery Manager, Senior Engagement Delivery Manager | Senior Delivery Manager |
| Engagement Delivery Director | Engagement Manager |
| Delivery Lead | Delivery Lead |
| Scrum Master | Scrum Master |
| Senior Scrum Master, Agile Delivery Manager/Scrum Master | Scrum Master Sênior |
| Agile Coach, Team Agilist, PMO/Agile Coach | Agile Coach |

**Tabela por função (painel da aba Vagas), Glassdoor Brasil, base mensal, 12/10/2026:**

| Função | Faixa | Média | Variável média |
|---|---|---|---|
| Scrum Master | R$ 6 a 9 mil | R$ 8 mil | R$ 0,9 mil |
| Agile Coach | R$ 10 a 14 mil | R$ 12 mil | R$ 2 mil |
| Project Manager (Gerente de Projetos) | R$ 8 a 17 mil | R$ 12 mil | R$ 2 mil |
| Program Manager | R$ 9 a 17 mil | R$ 14 mil | R$ 2 mil |
| Delivery Manager | R$ 12 a 18 mil | R$ 15 mil | R$ 2 mil |

### 2.7 Regras de pesquisa e curadoria de vagas

- **Fontes permitidas:** página de vagas da empresa; agregadores remotos (Remote Rocketship, Himalayas, Jobgether); conector do Indeed.
- **Fonte proibida:** raspagem ou automação no LinkedIn, que viola os termos de uso e arrisca a conta.
- **Elegibilidade:**
  - Só entram vagas que aceitem quem mora no Brasil.
  - "LATAM" sem citar o Brasil entra com a nota "Brasil não citado".
  - Vaga com fuso de outro continente entra com nota explicando o fuso. Exemplo: CET ±4h deixa o Brasil no limite.
- **Link:** preferir sempre o anúncio original. Quando só existir no agregador, o status é "conferir" e a observação diz "Vista em agregador".
- **Validade:** mais de 30 dias desde a publicação vira "conferir".
- **Observação da vaga:** só o que muda a decisão do candidato. Certificação exigida, idioma além do inglês, fuso, viagens, tamanho de equipe, setor regulado.

### 2.8 Regras do banco de empresas

- Entra empresa com evidência de contratação no Brasil para cliente estrangeiro (vaga real) ou presença conhecida e documentada.
- Uma frase de motivo, factual, sem adjetivo de propaganda.
- Sem nomes de pessoas. Recrutadores ficam fora da página compartilhada; o consultor mantém isso no próprio radar pessoal.

### 2.9 Modelo de dados

O banco tem quatro coleções.

**`jobs/<id>`** (uma vaga)

| Campo | Tipo | Exemplo |
|---|---|---|
| title | texto | "IT Project Manager" |
| company | texto | "Hyland" |
| companyId | texto (id em companies, ou vazio) | "hyland" |
| role | código | "PM" |
| market | "intl" ou "br" | "intl" |
| elig | texto | "Brasil, remoto" |
| contract | texto | "CLT" |
| english | texto | "Inglês C1+" |
| seniority | texto | "Sênior" |
| posted | data AAAA-MM-DD ou vazio | "2026-10-11" |
| url | link do anúncio | |
| note | texto curto | |
| salary | faixa declarada, texto original | "US$ 30 a 37 por hora" |
| salaryBRL | conversão | "cerca de R$ 23,9 a 29,5 mil/mês em contrato" |
| bench.pos / bench.co / bench.us | objeto ou null | ver abaixo |
| status | "ativa", "conferir", "encerrada" | |
| checkedAt | data AAAA-MM-DD | "2026-10-12" |

Objeto de referência (`bench.pos`, `bench.co`, `bench.us`):

```json
{"title": "Gerente de Projetos de TI", "value": "R$ 8 a 15 mil/mês", "brl": "", "src": "Glassdoor Brasil", "n": 50, "url": "https://..."}
```

**`companies/<id>`** (uma empresa): name, category, hq, size (Pequena, Média, Grande), hires, model, roles (lista de códigos), careersUrl, why, order (posição na lista).

**`benchmarks/<código da função>`**: range, avg, variable, source, url, order.

**`meta/fx`**: usdbrl (número), date (AAAA-MM-DD), source.

### 2.10 Permissões e privacidade

- **Leitura:** qualquer pessoa com acesso à página e logada.
- **Escrita:** só o dono e editores. Regra do banco: leitura no nível `view`, escrita no nível `admin`.
- **Teste feito:** com acesso de leitura as vagas aparecem e a edição é recusada.
- **Privacidade:** nenhum dado pessoal de terceiros na página compartilhada.
- **Compartilhamento:** a página nasce privada e é compartilhada pelo menu Compartilhar.

### 2.11 Design

**Direção:** utilitária e limpa, para ser lida rápido.
- Uma coluna de até 1.040 px, margem lateral de 16 px.
- Funciona no celular: as linhas da referência salarial empilham abaixo de 560 px.

**Fontes (Google Fonts):**
- Bricolage Grotesque nos títulos.
- IBM Plex Sans no texto.
- IBM Plex Mono em números, datas e rótulos.

**Cores (tema claro / tema escuro):**

| Papel | Claro | Escuro |
|---|---|---|
| Fundo | #F3F4F2 | #0F171B |
| Superfície dos cards | #FFFFFF | #16222A |
| Texto | #15222A | #E4ECEE |
| Texto secundário | #5B6970 | #93A3AB |
| Linhas | #D8DEDC | #2A3A43 |
| Destaque (petróleo) | #0C6B8A | #5BB8D6 |
| Ativa | #1F7A4D sobre #E2F2E9 | #5FCB92 sobre #163626 |
| Conferir | #A86A00 sobre #FBF0DC | #E7B256 sobre #3A2D14 |
| Encerrada | #7A848A sobre #ECEFF0 | #A3B0B7 sobre #22303A |

**Regras visuais e de acessibilidade:**
- A página segue o tema claro ou escuro de quem lê.
- Números alinhados em colunas (tabular).
- Foco visível no teclado em todos os controles.
- Movimento reduzido respeitado.
- Toda cor sai das variáveis do tema, nunca fixa no componente.

### 2.12 Texto e tom

- **Idioma e estilo:** português do Brasil, frases curtas, voz ativa, nomes que o candidato reconhece.
- **Travessão:** nunca entre frases (preferência do consultor). Usar vírgula, dois-pontos ou ponto final.
- **Evitar:** "não é X, é Y", frases de efeito, adjetivos de propaganda ("incrível", "líder", "robusto").
- **Mensagens de erro:** dizem o que aconteceu e o que fazer. Exemplos: "Não salvou. Tente de novo." e "Você não tem permissão para editar este banco."
- **Estados vazios:** dizem o que falta. Exemplos: "O banco ainda está vazio." e "Nenhuma vaga com esses filtros."

### 2.13 Rotina de atualização (proposta, ainda não ativada)

Uma vez por semana:

1. Buscar vagas novas nas fontes da seção 2.7 para as cinco funções.
2. Abrir o anúncio original de cada vaga "ativa" e "conferir". Saiu do ar: "encerrada". Mais de 30 dias: "conferir".
3. Preencher a referência salarial das vagas novas seguindo a seção 2.6.
4. Atualizar a cotação em `meta/fx`. Recalcular as conversões se a variação passar de 3%.
5. Revisar a tabela por função uma vez por mês.
6. Relatar: vagas novas, mudanças de status, referências alteradas e o que não foi possível conferir, com fontes.

### 2.14 Próximos passos em aberto

**Filtros propostos** (aguardando escolha):
1. Senioridade
2. Onde o candidato pode estar
3. País da empresa ou do cliente
4. Modelo (remoto, híbrido, presencial)
5. Contrato
6. Moeda de pagamento
7. Salário mínimo ou só com faixa declarada
8. Idioma exigido
9. Fuso de trabalho
10. Setor
11. Certificação pedida
12. Recência (7, 15, 30 dias)
13. Origem da vaga (site da empresa ou agregador)

**Decisões pendentes:**
- Incluir vagas com relocation e vagas na Europa?
- Incluir as funções RTE, Product Owner e PMO?

---

## Parte 3. Fontes de dados usadas na versão atual

- **Vagas:**
  - Páginas oficiais das empresas (Greenhouse, Lever, Ashby, Workable, Workday, iCIMS).
  - Remote Rocketship (remoterocketship.com), Himalayas (himalayas.app) e Jobgether (jobgether.com).
- **Salários por título:**
  - Glassdoor Brasil (glassdoor.com.br/Salários).
  - Glassdoor EUA (glassdoor.com/Salaries).
- **Salários por empresa:** Indeed Brasil e EUA, pelo conector do Indeed e pelas páginas br.indeed.com/cmp/(empresa)/salaries.
- **Câmbio:** dólar comercial, Renova Invest, cotação de 11/10/2026 (US$ 1 = R$ 4,98).
