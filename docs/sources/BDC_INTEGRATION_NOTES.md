# Notas de integração das bases de conhecimento

## Fontes identificadas

| Sistema | URL base | Estrutura observada |
|---|---|---|
| Small Commerce | <https://bdc.smallsoft.com.br/> | Categorias, artigos com URL canônica, busca, mais recentes e mais acessados. |
| ZWeb | <https://bdc.zweb.com.br/> | Categorias, artigos com URL canônica, busca, mais recentes e mais acessados. |

## Regra de ativação

O conector automático permanece desativado até confirmar:

1. termos de uso e autorização de indexação;
2. API, exportação ou feed oficial disponível;
3. limites de requisição e autenticação;
4. retenção permitida de texto e imagens;
5. procedimento para atualização e remoção;
6. contato responsável pela fonte.

## Estratégia técnica planejada

- Um conector independente por domínio.
- Prioridade para API/exportação oficial.
- Sincronização incremental por identificador externo, data, ETag ou checksum.
- Preservação da URL de origem e separação rígida do campo `sistema`.
- Relatório de alterações antes de republicar conteúdo relevante.
- Pausa automática quando a estrutura, autenticação ou política mudar.
- Sem contornar login, CAPTCHA, bloqueios ou outras medidas de acesso.

