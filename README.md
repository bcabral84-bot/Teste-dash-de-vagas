# Banco de Vagas Internacionais

Vagas remotas abertas a quem mora no Brasil em empresas e clientes dos EUA e da Europa, para Projetos, Agilidade e Delivery, a base de empresas de outsourcing que contratam daqui e um plano de conexões.

- Página: https://claude.ai/artifact/WDrJso7tYKhUayddT4fV49
- Especificação: [docs/especificacao.md](docs/especificacao.md)
- Rotina da varredura diária: [ROTINA.md](ROTINA.md)

## Estrutura

| Caminho | O que é |
|---|---|
| `site/banco-vagas.html` | Código da página publicada |
| `scripts/coletor.py` | Lê quadros oficiais e Himalayas, filtra por função e elegibilidade, compara com o banco |
| `scripts/preparar_lote.py` | Aplica a curadoria e gera os lotes de gravação no banco |
| `data/empresas.json` | Base de empresas (90 em 13/10/2026) com quadros públicos de vagas |
| `data/funcoes.json` | Regras de função, aderência e termos de busca |
| `data/referencias.json` | Correspondência de títulos para a referência salarial |
| `data/ajustes.json` | Decisões de curadoria (exclusões, mercado de empresas, edições) |
| `data/meta.json` | Câmbio usado nas conversões |
| `docs/v1/` | Especificação, página e dados da versão 1 |

## Rodar o coletor à mão

```bash
python3 scripts/coletor.py            # coleta e grava em out/
python3 scripts/preparar_lote.py      # monta os lotes em out/lote/
```

Só usa a biblioteca padrão do Python 3. Não acessa o LinkedIn.
