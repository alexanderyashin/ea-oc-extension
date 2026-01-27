# F — Metrics Engine (MVP) — Definitions / Formulas / Invariants

PROJECT: EA-OC-EXTENSION / ESTRA  
SCOPE: Backend ядро (без UI)  
STATUS: MVP metrics spec (RUN-1c)  
LANG: RU  
NON-GOALS: BI, KPI, рекомендации, оптимизация, ранжирование good/bad

---

## 0. Назначение

**Metrics Engine** — детерминированный вычислитель структурных метрик поверх **CanonicalGraph**.

Он:
- читает CanonicalGraph
- (опционально) читает Scenario context из SimulationInput
- вычисляет MetricSet (MVP: M1–M5)
- прикрепляет MetricSet к SimulationResult
- НЕ меняет CanonicalGraph
- НЕ меняет ingestion
- НЕ меняет семантику STOP
- НЕ влияет на исход симуляции (Simulation-0 / cascade / thresholds)

---

## 1. Жёсткие инварианты (non-negotiable)

### 1.1 Determinism
Все результаты метрик обязаны быть:
- **детерминированны** (одинаковый input ⇒ одинаковый output)
- **порядок** элементов фиксирован и воспроизводим
- **hash-covered**: MetricSet входит в resultHash (через SimulationResult)

Запрещено:
- использование Math.random / Date.now
- зависимость от порядка обхода объекта JS без сортировки ключей
- недетерминированные итерации по Map/Set без контроля порядка
- floating-метрики без фиксированного правила округления (MVP: предпочитать integer)

### 1.2 No influence
Metrics Engine **не имеет права**:
- изменять nodeStates, stop, ledger, cascade outcome
- подмешивать собственные условия в cascade/threshold logic
- “компенсировать” STOP или продолжать вычисления “как будто STOP нет”

Правило:
- метрики вычисляются **после** симуляции (post-pass),
- используют только CanonicalGraph + (опц.) SimulationInput + SimulationResult (read-only),
- результаты — **factual overlay**.

### 1.3 No bypass of STOP
Если симуляция вернула `stop=true`:
- Metrics Engine **может** вычислить метрики (они описательные),
- но **не может** создавать новые “выводы” или “планы действий”.
- Threshold proximity (M5) не “лечит” STOP; она только показывает расстояние/маржу, если доступна.

---

## 2. Базовые определения (граф, направления, adjacency)

Пусть CanonicalGraph задаёт:
- множество узлов `V`, каждый узел имеет `id` (строка)
- множество ребер `E`, каждое ребро имеет `from`, `to`, `kind`, `attrs`

### 2.1 Упорядоченность
Везде используем фиксированный порядок:
- узлы сортируются по `id` (лексикографически, Unicode codepoint)
- соседи сортируются по `id` целевого узла
- ребра сортируются по `(from, to, kind, stableStringify(attrs))`

### 2.2 Направление обхода (direction-aware)
Определим два режима:

- `OUT`: движение по направлению ребра `from -> to`
- `IN`: движение против направления ребра `to -> from`

Для любого узла `v` определим:
- `Adj_OUT(v)` = отсортированный список соседей `u`, таких что существует ребро `(v -> u)` в активном подграфе.
- `Adj_IN(v)`  = отсортированный список соседей `u`, таких что существует ребро `(u -> v)` в активном подграфе.

### 2.3 Активный подграф (cascade adjacency)
**MVP правило совместимости с симуляцией:**
метрики M1–M4 обязаны использовать **тот же “cascade adjacency”**, что и Simulation-0 (cascade logic).

То есть вводится функция (логически):
- `ActiveEdge(e, ctx)` → boolean

где `ctx` может включать:
- SimulationInput.scenario (если есть)
- SimulationResult.nodeStates (если симуляция помечает недоступные элементы)

**Требование:**
- Metrics Engine НЕ придумывает собственную фильтрацию ребер.
- В реализации допустимо импортировать/переиспользовать существующий helper из compute/cascade (или вынести общий helper), но **без изменения контрактов**.

Если контекст недоступен:
- активным считается весь граф (все ребра).

---

## 3. Формат выхода (MetricSet)

MetricSet — структура, прикрепляемая к SimulationResult (read-only overlay).

### 3.1 Общая форма
MetricSet содержит:
- `version` (строка, напр. `"metrics-mvp@1"`)
- `nodeMetrics[]` — массив по узлам (детерминированно отсортирован по nodeId)
- `graphMetrics` (опционально; MVP может быть пустым)

Каждый элемент `nodeMetrics`:
- `nodeId: string`
- `m1_dependencyDepth: { out: number, in: number }`
- `m2_blastRadius: { out: number, in: number }`
- `m3_cascadeSusceptibility: { inReach: number, inDegree: number }`
- `m4_structuralCriticality: { vector: number[], note: "lex" }`
- `m5_thresholdProximity?: { stopMargin?: number, warnMargin?: number, raw?: any }`

Примечания:
- Все численные метрики в MVP — целые числа `>=0`.
- Любое “неизвестно / отсутствует поле” выражается через `undefined` (не через NaN).

---

## 4. Метрики MVP (M1–M5)

### M1) Dependency Depth (max depth, direction-aware)

**Смысл:** максимальная длина пути (в ребрах) из узла, учитывая направление.

Определение:
- `Depth_OUT(v)` = максимальная длина простого пути из `v` по `Adj_OUT`.
- `Depth_IN(v)`  = максимальная длина простого пути из `v` по `Adj_IN`.

Циклы:
- граф может быть цикличным;
- используем “simple path” (без повторения узлов в одном пути);
- при DFS держим `onPath` и не углубляемся в вершины, уже находящиеся в текущем пути.

Детерминизм:
- соседи обходятся в отсортированном порядке `id`.

Алгоритм (детерминированный DFS):
- `depth(v) = max_{u in Adj(v)} (1 + depth(u))` при условии `u` не в текущем пути.
- memoization допустима только если учитывается цикл-safe режим (проще: без memo для MVP; либо memo только в DAG-случае после cycle-check).

Результат:
- `m1_dependencyDepth.out = Depth_OUT(v)`
- `m1_dependencyDepth.in  = Depth_IN(v)`

---

### M2) Blast Radius (reachable count, direction-aware)

**Смысл:** сколько узлов достижимо из узла при стандартной каскадной структуре.

Определение:
- `Reach_OUT(v)` = множество узлов, достижимых из `v` по `Adj_OUT`, исключая `v`.
- `Reach_IN(v)`  = множество узлов, достижимых из `v` по `Adj_IN`, исключая `v`.

Результат:
- `m2_blastRadius.out = |Reach_OUT(v)|`
- `m2_blastRadius.in  = |Reach_IN(v)|`

Алгоритм:
- BFS/DFS по отсортированным соседям.
- visited — Set; порядок добавления не влияет на итоговую мощность.
- но для детерминированных “трасс” (если они появятся позже) порядок фиксируется сортировкой.

---

### M3) Cascade Susceptibility (pure graph-based incoming sensitivity)

**Смысл:** структурная “уязвимость” узла к входящим отказам.

MVP определяет два компонента:

1) `inDegree(v)`:
- число активных входящих ребер в `v` (по ActiveEdge).

2) `inReach(v)`:
- количество различных узлов, которые могут достичь `v` по каскадной структуре,
  то есть `|Reach_IN(v)|`.

Результат:
- `m3_cascadeSusceptibility.inDegree = inDegree(v)`
- `m3_cascadeSusceptibility.inReach  = |Reach_IN(v)|`

Запрещено:
- вероятностные модели
- веса “важности” входящих зависимостей
- любые доменные интерпретации

---

### M4) Structural Criticality (aggregate structural significance, no business normalization)

**Смысл:** агрегированная структурная значимость узла как элемента topology/cascade,
без привязки к “бизнес-ценности”.

MVP-правило: **не выдавать single scalar score**, чтобы избежать скрытого ранжирования.
Возвращаем **лексикографический вектор** целых компонент.

Определение вектора (пример MVP):
`C(v) = [
  BR_out(v),        // m2 out
  BR_in(v),         // m2 in
  Depth_out(v),     // m1 out
  Depth_in(v),      // m1 in
  inReach(v),       // m3 inReach
  inDegree(v)       // m3 inDegree
]`

Результат:
- `m4_structuralCriticality.vector = C(v)`
- `m4_structuralCriticality.note = "lex"` (т.е. смысл сравнения — только как частичный порядок при необходимости в будущем, но MVP не сортирует и не ранжирует)

Запрещено:
- нормализация на [0..1]
- агрегирование в “балл зрелости”
- вывод “critical / non-critical”

---

### M5) Threshold Proximity (distance to STOP / Θ, no advice)

**Смысл:** расстояние (маржа) до порогов, уже присутствующих в результате симуляции.

MVP принцип:
- Metrics Engine **не вычисляет Θ сам**, он только читает то, что симуляция уже посчитала.
- Если в SimulationResult нет достаточных численных полей — метрика отсутствует (undefined).

Ожидаемый (но не навязанный) паттерн:
- в `SimulationResult.nodeStates[nodeId]` могут быть поля вроде:
  - `tension` (или аналог)
  - `thetaStop`, `thetaWarn` (или аналог)
  - или `thresholds: { stop: number, warn: number }`

MVP вычисление маржи (если доступно):
- `stopMargin = thetaStop - tension`
- `warnMargin = thetaWarn - tension`
(оба могут быть < 0; это факт, не “оценка”)

Результат:
- `m5_thresholdProximity.stopMargin = stopMargin` (если вычислимо)
- `m5_thresholdProximity.warnMargin = warnMargin` (если вычислимо)
- `m5_thresholdProximity.raw` может содержать маленький read-only фрагмент исходных полей (без копирования больших структур)

Запрещено:
- “что делать”
- “как увеличить маржу”
- “рекомендованные действия”
- “оптимизация порогов”

---

## 5. MVP vs Full scope boundary (явно)

### MVP (в этом документе)
- только M1–M5
- только структурные целочисленные метрики
- только чтение CanonicalGraph + (опц.) SimulationInput/Result
- никаких весов, доменных коэффициентов, ML/вероятностей
- никаких UI-представлений

### Full (зарезервировано, не реализуется здесь)
- центральности (betweenness, eigenvector и т.п.)
- path-based распределения, “distance profiles”
- атрибутивные веса и классы зависимостей
- временные/динамические метрики по серии симуляций
- robust metrics under perturbations
(см. каталог G_metric-catalog.md)

---

## 6. Регистрация в SimulationResult

MetricSet является полем SimulationResult (например `metrics`), которое:
- добавляется **после** ledger/nodeStates/stop
- сериализуется детерминированно (stable stringify)
- входит в итоговый `resultHash`

При этом:
- отсутствие `metrics` в более ранних версиях SimulationResult считается допустимым (backward-compat).
- в MVP запрещено ломать существующий контракт: добавление поля должно быть “append-only”.

---

## 7. Минимальные тест-инварианты (для будущего)

- Перестановка узлов/ребер во входном JSON (при сохранении тех же ids и структур) не меняет результатов.
- Сортировка `nodeMetrics` всегда по nodeId.
- M1/M2/M3/M4 не зависят от времени запуска.
- M5 либо вычислима и корректна, либо отсутствует (undefined), но никогда NaN.
- Метрики не меняют stop/nodeStates/ledger.

---
