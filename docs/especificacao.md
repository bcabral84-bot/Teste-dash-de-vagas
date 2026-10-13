# Banco de Vagas Internacionais: prompt e especificação (versão 2)

Versão de 13/10/2026. Substitui a versão 1 (12/10/2026), guardada em `docs/v1/`. A página publicada é https://claude.ai/artifact/WDrJso7tYKhUayddT4fV49 e o código dela está em `site/banco-vagas.html`.

O que mudou da versão 1 para a 2:

- Layout pensado para o celular (barra de abas embaixo, filtros em painel) e com trilho lateral no computador.
- Abas novas: **Rede** (plano de 5 conexões por empresa, privado para cada pessoa) e **Guia** (salários, método e fontes).
- Europa entrou: empresas e vagas de clientes europeus, com filtro de região.
- Funções novas, com aderência ao perfil: RTE, PMO e coordenação, Product Owner e Product Manager.
- Filtros: aderência, região, mercado, data de publicação, modelo, origem do anúncio, faixa declarada, vagas que estou acompanhando.
- Cada pessoa acompanha as próprias vagas (Salva, Candidatura enviada, Em entrevista, Proposta, Descartada), salvo só para ela.
- Base de empresas de outsourcing com 90 empresas e o "termômetro": quantas vagas cada uma tem abertas ao Brasil na última varredura.
- Varredura automática diária nos dias úteis (ver `ROTINA.md`), com coletor em `scripts/`.

---

## Parte 1. Prompt pronto para usar

```
Você vai manter o "Banco de Vagas Internacionais", uma página web usada como material de apoio
de uma consultoria de recolocação profissional. O repositório tem o código da página, o coletor
de vagas, a base de empresas e a rotina. Siga docs/especificacao.md e ROTINA.md à risca.

OBJETIVO
Mostrar a quem mora no Brasil vagas remotas em Projetos, Agilidade e Delivery (e funções vizinhas)
em empresas ou clientes dos EUA e da Europa, as empresas que contratam esse perfil daqui e um plano
para se conectar com 5 pessoas de cada empresa. A pessoa precisa entender elegibilidade, contrato,
faixa salarial e aderência ao perfil ANTES de se candidatar.

FUNÇÕES (código, aderência ao perfil)
SM Scrum Master (alta) | AC Agile Coach (alta) | RTE Release Train Engineer (alta)
PM Project Manager (alta) | PGM Program Manager (alta) | DM Delivery Manager (alta)
PMO PMO e coordenação (média) | PO Product Owner (média) | PRD Product Manager (baixa)
Projetos de marketing, pesquisa, tradução ou criação descem para aderência baixa. Vaga júnior desce um nível.

COMO PESQUISAR VAGAS
1. Fontes: quadro oficial da empresa (Greenhouse, Lever, Ashby, SmartRecruiters, Recruitee,
   Teamtailor, Workable, Workday, iCIMS), busca do Himalayas restrita ao Brasil, Remote Rocketship,
   Jobgether e o conector do Indeed. Nunca raspe o LinkedIn nem use automação dentro dele.
2. Só entra vaga que aceite quem mora no Brasil: Brasil citado, LATAM, Américas ou qualquer país.
   "LATAM" sem citar o Brasil entra com "Brasil não citado". Américas e qualquer país entram com "(conferir)".
3. O link salvo é o do anúncio original sempre que possível.
4. Fora do escopo: projetos de construção, clínicos, ambientais, RH e vendas.
5. Status: "ativa" quando vista no site da empresa; "conferir" quando tem mais de 30 dias, foi vista
   só em agregador ou pode ter encerrado; "encerrada" quando saiu do ar.
6. Mercado "intl" = empresa ou cliente estrangeiro. "br" = empresa brasileira para o mercado local.
   Região: EUA, Europa, Global ou Brasil.

REFERÊNCIA SALARIAL (quatro linhas, nesta ordem)
Anúncio | Cargo no Brasil (Glassdoor Brasil, título mais próximo) | Mesma empresa | Mesmo cargo nos EUA.
Mostre fonte, link e número de relatos. Nunca invente número. Câmbio do dia em meta/fx, 160 horas por mês.

BANCO DE EMPRESAS
Entra empresa de outsourcing, nearshore, staffing, consultoria ou rede de talentos que contrata no
Brasil para clientes dos EUA ou da Europa, com evidência (vaga real ou presença documentada).
Sem nomes de pessoas no banco compartilhado.

REDE
5 pessoas por empresa: recrutamento técnico, liderança de Talent Acquisition, liderança de Delivery,
PMO ou programas, e um par na função. O progresso fica em data/users/<id>, privado para cada pessoa.

PERMISSÕES
Banco compartilhado: todos leem, só o dono e editores escrevem. Área privada: cada pessoa com acesso
de Contribuidor ou mais escreve a sua.

TEXTO
Português do Brasil, frases curtas e diretas. Nunca use travessão (—) entre frases.
Não use "não é X, é Y" nem frases de efeito.

ENTREGA DE CADA ATUALIZAÇÃO
Quantas vagas entraram, quantas mudaram de status, empresas novas, referências alteradas,
o que não foi possível conferir, fontes com links.
```

---

## Parte 2. Especificação

### 2.1 Público e pergunta que a página responde

Material extra de uma consultoria de recolocação. Quem lê: o consultor e clientes que buscam vagas remotas pagas por empresas ou clientes de fora. Pergunta: "Quais vagas eu posso disputar morando no Brasil, quanto pagam, quem contrata esse perfil e com quem eu preciso me conectar?"

### 2.2 Estrutura da página

**Celular**: cabeçalho (rótulo, título, frase, relógios de Nova York, São Paulo, Lisboa e Berlim com ponto verde no horário comercial), conteúdo da aba, barra de abas fixa embaixo. Filtros de vagas abrem num painel de baixo para cima.

**Computador (1024 px ou mais)**: trilho à esquerda com título, relógios, abas e filtros; coluna principal com o conteúdo.

**Aba Vagas**
1. Quatro números: abertas, alta aderência, novas em 7 dias, data da última varredura.
2. Busca por texto (cargo, empresa, nota, elegibilidade) e botão Filtros.
3. Chips de função com contagem, gerados das vagas que passam nos outros filtros.
4. Lista de cards.

Filtros: aderência (alta, média, baixa), região (EUA, Europa, Global, Brasil), mercado (internacional por padrão), publicada (7, 15, 30 dias, qualquer data), modelo (remoto, híbrido ou presencial), origem (site da empresa, agregador), só com faixa declarada, só as que estou acompanhando, mostrar encerradas, ordenar (recentes, aderência, faixa declarada). As escolhas ficam lembradas no aparelho.

**Card de vaga**: cargo; empresa e regiões; status; aderência em três pontos com texto; função; dias desde a publicação; etiquetas (elegibilidade, contrato, inglês, senioridade); nota; referência salarial recolhida com um resumo visível; botão Ver vaga; seletor "Acompanhar esta vaga" (privado); data da última conferência. Editores mudam o status tocando nele.

**Aba Empresas**: busca, ordenação (mais vagas hoje, nome, categoria), chips de região (todas, EUA, Europa, Minha rede) e de categoria. Card: categoria, nome, regiões, barra do termômetro (vagas abertas ao Brasil, qualquer área, na última varredura), frase de motivo, sede, onde contrata, modelo, funções, botões Página de vagas, Vagas no banco (filtra a aba Vagas) e Adicionar à minha rede.

**Aba Rede**: explicação da estratégia; quatro números (empresas na lista, meta de contatos, convites enviados, conectados); um card por empresa da lista com as 5 pessoas, cada uma com link de busca no LinkedIn, status (A buscar, Convite enviado, Conectado, Conversou) e campos opcionais de nome e perfil; modelos de nota de convite com até 200 caracteres, preenchidos com cargo, anos, setor e cidade da pessoa (salvos no aparelho); regras de escolha e ritmo. Lista vazia mostra as 6 empresas que mais abriram vagas ao Brasil.

**Aba Guia**: tabela de salário por função, como ler cada vaga, de onde vêm as vagas e resumo da última varredura, formulário de adicionar vaga (só editores).

Link direto para uma aba: `#vagas`, `#empresas`, `#rede`, `#guia`.

### 2.3 Status

| Status | Cor | Quando |
|---|---|---|
| Ativa | verde | Vista no site da empresa nos últimos 30 dias |
| Conferir no site | âmbar | Mais de 30 dias (a página calcula sozinha), só em agregador ou com sinal de encerramento |
| Encerrada | cinza, card esmaecido | Saiu do ar. Oculta por padrão |

### 2.4 Referência salarial

Mesmas quatro linhas da versão 1. A correspondência de títulos está em `data/referencias.json` (a primeira regra que casar vale). RTE, Product Owner, PMO e Product Manager não têm número público com fonte no Glassdoor Brasil até 13/10/2026: o card mostra "Sem referência pública". Product Owner nos EUA usa o pagamento total médio do Glassdoor EUA (US$ 142,3 mil por ano, 12.903 relatos), identificado como pagamento total.

### 2.5 Aderência

Calculada pelo coletor (`data/funcoes.json`) e ajustável na curadoria (`data/ajustes.json`):

- Alta: SM, AC, RTE, PM, PGM, DM.
- Média: PMO e coordenação, Product Owner.
- Baixa: Product Manager; qualquer função com marketing, criação, pesquisa, tradução, jogos ou e-commerce no título.
- Vaga júnior desce um nível.

### 2.6 Modelo de dados

**`jobs/<id>`**: `title, company, companyId, role, fit, seniority, elig, model, contract, english, market, region[], posted, url, alsoAt, source, origin ("empresa" ou "agregador"), note, salary, salaryBRL, bench{pos,co,us}, status, checkedAt, addedAt, key`. Ids `j01` a `j24` vêm da versão 1; os novos são `j-<key>`, onde `key` é um hash de empresa e título normalizados.

**`companies/<id>`**: `name, category, markets[], hq, size, hires, model, roles[], careersUrl, why, market`.

**`benchmarks/<função>`**: `range, avg, variable, source, url, order`.

**`meta/fx`**: `usdbrl, date, source`. **`meta/termometro`**: `at, companies{<id>: {brJobs, oficial, himalayas}}`. **`meta/coleta`**: `date, novas, vistas, oficial, agregador, encerradas, atualizadas, fontes`. **`meta/ajustes`**: cópia de `data/ajustes.json` (curadoria), para a rotina não depender do push no git.

**`data/users/<id>/job_<jobId>`**: `stage, at`. **`data/users/<id>/co_<companyId>`**: `list, prio ("A" ou "B"), slots{rec,ta,del,pmo,par: {status, name, url, at}}, at`. Ninguém além da própria pessoa lê isso, nem o dono da página.

Base local no repositório: `data/empresas.json` (empresas, com `boards` dos quadros públicos, `him` do Himalayas e `aliases`), `data/funcoes.json`, `data/referencias.json`, `data/meta.json`, `data/ajustes.json` (curadoria).

### 2.7 Permissões e privacidade

Regras do banco: raiz com leitura `view` e escrita `admin`; `data/users/{self}` com escrita `interact`. Na prática:

- Leitor (Viewer): vê vagas e empresas, usa os links de busca, não salva progresso.
- Contribuidor: tudo do leitor, mais o acompanhamento de vagas e o plano de rede, privados.
- Editor e dono: também mudam status e adicionam vagas.

Teste feito em 13/10/2026: leitura com nível `view` funciona; escrita em vaga com nível `interact` é recusada; escrita e exclusão na área privada funcionam.

### 2.8 Design

Mesma família da versão 1: Bricolage Grotesque nos títulos, IBM Plex Sans no texto, IBM Plex Mono em números e rótulos, destaque petróleo (#0C6B8A no claro, #5DB9D7 no escuro), fundo cinza esverdeado. Todas as cores são variáveis de tema, com tema claro, escuro e o do sistema. Foco visível, movimento reduzido respeitado, números tabulares, sem rolagem lateral no celular.

### 2.9 Rotina

Diária nos dias úteis às 6h51 de Brasília, descrita em `ROTINA.md`. Segunda-feira inclui empresas novas e câmbio; a primeira segunda do mês inclui referências salariais.

### 2.10 Pendências

- Referência salarial de RTE, Product Owner, PMO e Product Manager no Brasil.
- Vagas com relocation continuam fora: só entra quem pode trabalhar morando no Brasil.
- Workable bloqueia leitura automática a partir do servidor da rotina; vagas de empresas que usam Workable chegam pelo Himalayas ou pela checagem manual com `WebFetch`.
