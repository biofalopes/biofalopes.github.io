# Revisão dos posts prioritários

Concluída em 27/10/2026, a partir dos achados P0 da [auditoria inicial](auditoria-2026-10-26.md).

## Alterações aplicadas

| Conteúdo | Correção |
|---|---|
| Loki | Separação entre logs e métricas, diagrama corrigido, autenticação versus tenant, compactor singleton, armazenamento e comandos S3/Helm. Promtail identificado como histórico. |
| Mimir | Chart/release corretos, Secret do usuário Mimir, endpoint Ceph explícito, autenticação e limites das alegações de disponibilidade. |
| IBB Kids | WAL, backup consistente, concorrência, compilação nativa, limites do host único, reinício controlado e invalidação de sessões após restore. Removidas contagens de CI sem evidência vinculada. |
| Previsão Ceph EN/PT | Código compartilhado, projeção pela mediana dos incrementos, tratamento de dados incompletos e limites, TLS e timeout. Amostra sintética e execução offline. |
| Ordenação | Corrigidos MergeSort e SelectionSort; benchmark verifica o resultado antes de medir. Resultados inválidos anteriores removidos. |
| Fibonacci | Caso zero, entradas inválidas, argumento mutável e esclarecimento do limite de recursão. |
| Terraform ASG | Subnets derivadas da VPC, Launch Template, ALB, ingresso das instâncias restrito ao ALB e provider fixado. |

As oito versões de artigos receberam slugs explícitos que preservam suas URLs. Datas originais de publicação foram mantidas; revisões técnicas usam `lastmod`. Alterações iniciadas em 26/10 foram preservadas na retomada de 27/10.

Os exemplos executáveis ficam nos bundles e são renderizados pelo shortcode `code-file`, evitando duplicação entre código publicado e código testado. Downloads compartilhados entre idiomas usam `resource-link`, que resolve a URL do recurso pelo Hugo.

## Verificações

- 14 testes de regressão em `tests/test_post_examples.py`: ordenação com entradas variadas, cinco versões de Fibonacci, projeção, holdout cronológico sintético, dados inválidos e execução CLI offline.
- Benchmark de ordenação executado com 1.000 inteiros, seed 42 e cinco repetições; todos os resultados conferidos com `sorted`.
- Terraform 1.9.8 com provider AWS 6.70.0: `fmt -check` e `validate` em diretório temporário, sem executar `plan`/`apply`.
- Helm 3.17.3: lint e renderização de Loki chart 6.24.0 e Mimir Distributed chart 5.6.0 para Kubernetes 1.30. Esses charts são referências históricas explicitamente identificadas, não uma atualização para releases atuais dos serviços.
- Build Hugo de produção com minificação e avisos tratados como erro.
- Comparação das 44 URLs do inventário e das datas originais de publicação.
- Varredura dos HTMLs gerados em busca de destinos locais e âncoras ausentes, incluindo downloads EN/PT.

Comando para repetir os testes de exemplos:

```powershell
python -m unittest discover -s tests -v
```

## Limites da validação

Não foram acessados clusters, contas AWS, endpoints internos do Mimir ou webhooks do Teams. A renderização de charts não comprova inicialização dos serviços, acesso ao storage ou comportamento sob falha. A validação Terraform verifica o schema local; não confirma AMIs, quotas ou execução em AWS.

Os testes de previsão verificam o cálculo com dados sintéticos, sem alegar precisão no ambiente operacional. A geração opcional de gráficos depende de matplotlib e não faz parte dos testes sem dependências. A configuração e o contrato de autenticação do Workflow do Teams precisam ser conferidos no tenant antes de um envio real.

A modernização de Hugo/Stack, revisão dos achados P1 e validação visual continuam como próximas etapas. As correções desta rodada não foram publicadas por este trabalho.
