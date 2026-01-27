## RUN-1c — Metrics Engine MVP

Добавлены спецификации Metrics Engine (post-pass overlay поверх SimulationResult):

- F_metrics-engine.md — формальные определения метрик M1–M5, детерминизм, инварианты, запреты.
- G_metric-catalog.md — каталог метрик (MVP + placeholders Full scope).

Границы:
- метрики не влияют на Simulation-0 и STOP,
- не меняют CanonicalGraph/ingestion,
- не являются BI/KPI и не содержат рекомендаций.
