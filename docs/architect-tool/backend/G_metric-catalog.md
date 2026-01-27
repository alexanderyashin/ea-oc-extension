# G — Metric Catalog (MVP + placeholders)

PROJECT: EA-OC-EXTENSION / ESTRA  
SCOPE: Backend metrics catalog  
STATUS: RUN-1c  
LANG: RU

---

## 0. Правило каталога

Каталог фиксирует:
- какие метрики существуют
- их статус (MVP vs Full)
- их тип (graph-only / scenario-bound / result-bound)
- запреты (no BI, no KPI, no advice)

Каталог **не является** UX/BI документом.

---

## 1. MVP Metrics (обязательные)

### M1 — Dependency Depth (MVP)
- Тип: graph-only (с учетом ActiveEdge)
- Выход: `{ out: int, in: int }`
- Смысл: максимальная глубина зависимостей (direction-aware)
- Запреты: no weights, no probability

### M2 — Blast Radius (MVP)
- Тип: graph-only (с учетом ActiveEdge)
- Выход: `{ out: int, in: int }`
- Смысл: сколько узлов достижимо из узла по каскадной структуре
- Запреты: no scenario ranking, no “impact score”

### M3 — Cascade Susceptibility (MVP)
- Тип: graph-only (с учетом ActiveEdge)
- Выход: `{ inReach: int, inDegree: int }`
- Смысл: входящая структурная чувствительность к отказам
- Запреты: no likelihood, no root cause logic

### M4 — Structural Criticality (MVP)
- Тип: derived aggregate (graph-only)
- Выход: `{ vector: int[], note:"lex" }`
- Смысл: структурная значимость без бизнес-нормализации
- Запреты: no scalar score, no maturity index, no ranking

### M5 — Threshold Proximity (MVP)
- Тип: result-bound (читает SimulationResult/nodeStates)
- Выход: `{ stopMargin?: number, warnMargin?: number, raw?: any }` либо отсутствует
- Смысл: расстояние до Θ/STOP как факт, без советов
- Запреты: no “recommendations”, no “what to do”

---

## 2. Full-scope placeholders (не MVP, не реализовывать здесь)

### F1 — Centrality family (betweenness / closeness / eigenvector)
- Причина не-MVP: требует нормализаций и риск превращения в “рейтинг”
- Возможно позже: только как raw vectors + explicit caveats

### F2 — Cut / bridge / articulation diagnostics
- Смысл: элементы, разрывающие связность
- Риск: может выглядеть как “куда инвестировать”
- Разрешено только как факт topology

### F3 — Multi-edge semantics (typed dependency classes)
- Разделение edges по kind (data/control/run/people)
- Требует контрактной стабильности edge.kind taxonomy

### F4 — Temporal / series metrics
- Метрики по серии симуляций (scenario sweep)
- Требует отдельного контракта запуска и хранения

### F5 — Robustness under perturbations
- чувствительность метрик к локальным изменениям графа
- требует явного perturbation contract

### F6 — Ledger-derived metrics
- агрегации по ledger событий
- опасность BI-восприятия, требует строгих запретов и формата

---

## 3. Правило “не BI”

Ни одна метрика каталога не имеет права:
- выдавать KPI/оценку зрелости
- давать “целевой уровень”
- формировать “план действий”
- интерпретировать бизнес-ценность

Только структурные факты и расстояния до порогов как числа.

---
