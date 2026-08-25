# Telemetria, retenção e capacidade

## Política padrão

- cada leitura possui UUID e sequência por sensor; duplicatas são ignoradas;
- dados brutos ficam por 90 dias;
- agregados horários preservam mínimo, máximo, média, contagem e qualidade por
  730 dias;
- alarmes e auditorias têm retenção própria e não são removidos junto com a
  telemetria bruta;
- a limpeza recebe `now` explicitamente, tornando o teste determinístico.

## Previsão-base

Para uma estação com 16 sensores, uma amostra por sensor a cada 30 segundos:

| Medida | Previsão |
|---|---:|
| Registros/ano | 16.819.200 |
| Dados primários a 220 bytes/amostra | 3,45 GiB/ano |
| Espaço provisionado a ~550 bytes/amostra | 8,61 GiB/ano |

O provisionamento inclui índices, folga de página, WAL, manutenção e margem de
crescimento. É uma previsão de engenharia, não uma medição do notebook. O
valor real deve ser recalculado após 30 dias de operação e antes de escolher o
armazenamento definitivo.
