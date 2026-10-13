# Rotina diária do Banco de Vagas Internacionais

Este arquivo é a instrução que a varredura automática segue. Ela roda nos dias úteis às 6h51 (horário de Brasília), numa sessão nova do Claude Code, a partir deste repositório. Leia tudo antes de começar.

- Página: https://claude.ai/artifact/WDrJso7tYKhUayddT4fV49 (privada, do dono da conta)
- Banco da página: coleções `jobs`, `companies`, `benchmarks`, `meta` (docs `fx`, `termometro`, `coleta`) e `data/users/<id>` (área privada de cada pessoa: nunca leia, escreva ou apague nada ali)
- Especificação completa: `docs/especificacao.md`

## Regras que não mudam

1. Nunca acesse, raspe ou automatize nada no LinkedIn.
2. Nunca invente número. Sem fonte, o card mostra o texto de ausência.
3. Texto em português do Brasil, frases curtas, sem travessão entre frases (use vírgula, dois-pontos ou ponto final), sem "não é X, é Y".
4. Não registre nome de pessoa nenhuma no banco compartilhado.
5. Não mude o HTML da página nem as regras de acesso. Isso só com pedido do dono.
6. Toda escrita em documento que já existe leva `if_version` com a versão lida.

## Passo a passo

### 1. Preparar

```bash
git pull --ff-only
mkdir -p /tmp/banco && rm -rf /tmp/banco/*
```

Exporte as vagas do banco com `ArtifactData` `list`, coleção `jobs`, `query.limit` 1000, `out_dir` `/tmp/banco`. Guarde a lista de versões que a resposta mostra (uma linha por documento, "version N"): você vai precisar dela no passo 5.

### 2. Coletar

```bash
python3 scripts/coletor.py --banco /tmp/banco
```

O coletor lê os quadros oficiais das empresas de `data/empresas.json` (Greenhouse, Lever, Ashby, SmartRecruiters, Recruitee, Teamtailor) e a busca do Himalayas restrita ao Brasil, para as funções de `data/funcoes.json`. Saídas em `out/`:

- `relatorio.txt`: resumo
- `candidatas.json`: vagas que não estão no banco
- `sumidas.json`: vagas do banco que saíram do quadro oficial
- `termometro.json`: vagas abertas ao Brasil por empresa, qualquer área
- `empresas_sem_cadastro.json`: empresas com vaga que não estão na base

### 3. Curar as candidatas

Leia `out/candidatas.json` inteiro. Para cada vaga decida:

- **Fora do escopo** (projeto de construção, clínico, ambiental, RH, vendas, vaga que exige morar fora do Brasil): adicione a chave em `data/ajustes.json` > `excluir`, com `title`, `company` e `motivo`.
- **Duplicata** de vaga que já está no banco (mesma empresa, mesma função, título quase igual, até 15 dias de diferença): exclua do mesmo jeito, com motivo "Duplicata de <id>".
- **Empresa fora da base**: classifique em `data/ajustes.json` > `empresas` com `market` ("intl" ou "br") e `markets` (["EUA"], ["Europa"], ["Global"] ou ["Brasil"]). Empresa brasileira atendendo o mercado local é "br".
- **Ajustes** (`data/ajustes.json` > `editar`, pela chave): título limpo, nota curta com o que muda a decisão (certificação, idioma extra, fuso, viagens, setor regulado), `fit` quando a regra automática errar.

Para vagas de aderência alta vindas de agregador, tente achar o anúncio no site da empresa (no máximo 10 por dia, com `WebFetch`). Achou: troque `url`, ponha `origin` "empresa" e `status` "ativa" no `editar`. Não achou: deixe como está, a página já avisa "Vista em agregador".

### 4. Gravar as vagas novas

```bash
python3 scripts/preparar_lote.py
cat out/lote/resumo.txt
```

Para cada `out/lote/lote-N.json`, chame `ArtifactData` `batch` com aquela lista de writes (são todas criações, sem `if_version`).

### 5. Atualizar status

- Cada item de `out/sumidas.json`: `update` em `jobs/<id>` com `{"status": "encerrada", "checkedAt": "<hoje>"}` e o `if_version` do passo 1.
- Vagas com `status` "conferir" e `origin` "agregador" com mais de 45 dias: abra o link com `WebFetch`. Se a página disser que a vaga fechou ou não existir mais, marque "encerrada". Limite de 15 por dia, as mais antigas primeiro.
- Não precisa marcar "conferir" por idade: a página já mostra "Conferir no site" quando a vaga passa de 30 dias.

### 6. Termômetro e resumo

Monte os dois documentos e grave com `set` e `if_version` (leia antes com `get`):

- `meta/termometro`: use `out/lote/termometro.json` (o `preparar_lote.py` já monta).
- `meta/coleta`: use `out/lote/coleta.json` e acrescente `encerradas` (quantas marcou no passo 5) e `atualizadas`.

### 7. Toda segunda-feira

- **Empresas novas**: olhe `out/empresas_sem_cadastro.json`. Entra na base quem faz outsourcing, nearshore, staffing, consultoria ou rede de talentos para clientes dos EUA ou da Europa e tem pelo menos 2 vagas abertas ao Brasil no Himalayas (`https://himalayas.app/jobs/api/search?company=<slug>&country=BR&exclude_worldwide=true`). Para cada uma: acrescente em `data/empresas.json` (mesmos campos das outras, com `him` e `boards` quando houver quadro público) e grave em `companies/<id>` com os campos que a página usa: `name, category, markets, hq, size, hires, model, roles, careersUrl, why, market`. A frase `why` é factual e cita a evidência com data.
- **Câmbio**: confira o dólar comercial do dia. Se variar mais de 3% contra `meta/fx`, atualize `meta/fx` e `data/meta.json` e avise no relatório que as conversões antigas ficaram defasadas.

### 8. Primeira segunda-feira do mês

Revise as referências salariais (`data/referencias.json` e coleção `benchmarks`) só se achar número novo com fonte, link e quantidade de relatos. RTE, Product Owner, PMO e Product Manager seguem sem referência no Brasil até haver número público com fonte.

### 9. Salvar a curadoria

```bash
git add data/ && git commit -m "Varredura <AAAA-MM-DD>: <n> novas, <m> encerradas" && git push origin HEAD
```

### 10. Relatório final

Termine com um resumo em português, curto:

- quantas vagas entraram (por função e aderência) e as 5 de aderência alta mais recentes, com link
- quantas mudaram de status
- empresas novas na base, se houver
- o que não foi possível conferir e por quê
- fontes usadas, com links

Se algo quebrar (API fora, erro de permissão no banco), não tente contornar mexendo na página: registre o erro no relatório e pare.
