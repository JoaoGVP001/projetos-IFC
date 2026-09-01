# Caderno de Notas

Projeto em Python orientado a objetos. O
programa cria, pesquisa e modifica anotações mantidas em memória durante a
execução.

## Estrutura

- `notas.py`: classes `Nota` e `CadernoDeNotas`, sem dependência da interface.
- `menu.py`: interface de linha de comando e opções do menu.
- `tests/test_notas.py`: testes automatizados da lógica de negócio.

## Como executar

É necessário Python 3.10 ou superior. No terminal, dentro desta pasta, execute:

```powershell
python menu.py
```

## Como testar

Os testes usam apenas a biblioteca padrão do Python:

```powershell
python -m unittest discover -s tests -v
```

As notas não são gravadas em disco, pois o estudo de caso especifica um caderno
em memória.
