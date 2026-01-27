---
title: "E. Simulation Contract (MVP)"
purpose: "Формально зафиксировать вход/выход симуляции и запреты (no BI, no recommendations)"
audience: ["Engine dev", "Core dev", "Audit"]
language: "RU"
evidence_profile: "Design-spec (I/O contract + invariants)"
role: "Simulation interface contract"
status: "ACTIVE"
---

# E. Контракт симуляции (MVP)

## 0) Принцип

Симуляция принимает **канонические факты** (CanonicalGraph) + **параметры сценария**
и возвращает **формальный результат** (states + ledger + stop) **без рекомендаций**.

Симуляция:
- не является BI / дашбордом,
- не является “советчиком”,
- не оптимизирует,
- не генерирует управленческие действия.

---

## 1) Объекты контракта

### 1.1 SimulationInput

`SimulationInput` — единственный допустимый вход в engine.

Состав (MVP):
- `meta` (обяз.)
- `graphRef` (обяз., ссылка на CanonicalGraph)
- `scenario` (обяз.)
- `options` (опц.)

> Важно: в MVP **не передаём граф инлайн**. Engine должен принимать ссылку `graphRef`
> и далее резолвить её к CanonicalGraph (в демо/fixtures — через файловый путь).
> Инлайн-граф допускается только позже (Full Product), отдельным расширением контракта.

#### 1.1.1 meta (обяз.)

- `schemaVersion` (например: `SI-0.1`)
- `capturedAt` (ISO8601; время формирования input)

#### 1.1.2 graphRef (обяз.)

`graphRef` фиксирует *какой именно граф* используется.

Поля:
- `path` (string; относительный путь к файлу CanonicalGraph, например `./canonicalgraph.sample.json`)
- `snapshotId` (строка из `CanonicalGraph.meta.snapshotId`)
- `contentHash` (строка из `CanonicalGraph.meta.determinism.contentHash`)

Инварианты:
- `contentHash` обязателен и должен совпадать с `CanonicalGraph.meta.determinism.contentHash`.
- `contentHash` считается как `sha256(canonicalGraphJson)` по правилам `D_determinism.md`.

#### 1.1.3 scenario (обяз.)

`scenario` задаёт “что именно моделируем”, но **не содержит рекомендаций**.

MVP-поля:
- `shockType` (enum)
- `intensity` (number | enum)
- `targetSelector` (enum: `all` | `selected`)
- `targets` (string[]; обязательны при `selected`)
- `seed` (string | number; фиксирует любые псевдослучайности, если они появятся)

Рекомендованный MVP-набор `shockType`:
- `capacity_drop`
- `node_failure`
- `dependency_disruption`

> Важно: значения и семантика shockType — часть engine, но контракт фиксирует форму.

#### 1.1.4 options (опционально)

- `strictDeterminism` (bool, default true)
- `unknownHandling` (enum: `drop` | `keep-as-unknown`; default `drop`)
- `maxLedgerEntries` (number; optional guard)
- `stopOnThreshold` (bool, default true)

---

### 1.2 SimulationResult

`SimulationResult` — единственный допустимый выход engine.

Состав:
- `meta`
- `stop`
- `nodeStates`
- `edgeStates` (опционально)
- `ledger[]`
- `resultHash`

#### 1.2.1 meta (обяз.)

- `schemaVersion` (например: `SR-0.1`)
- `producedAt` (ISO8601)
- `graphRef`
  - `snapshotId`
  - `contentHash`
- `scenarioRef`
  - `shockType`
  - `intensity`
  - `targetSelector`
  - `seed` (если использовался)
- `determinism`
  - `hashAlgo` (`sha256`)
  - `resultHash` (дублирует верхний `resultHash` для удобства аудита)

#### 1.2.2 stop (обяз.)

- `stop: boolean`

Смысл:
- `stop=false` — симуляция завершилась без “LOCK/STOP” условия
- `stop=true` — достигнут STOP/LOCK (терминальное состояние демонстратора)

STOP/LOCK:
- **не** означает “что делать”
- означает: “в рамках модели достигнут порог, при котором дальнейшая эволюция запрещена/неопределена”

#### 1.2.3 nodeStates (обяз.)

- `nodeStates: { [nodeId: string]: NodeState }`

`NodeState` (MVP enum):
- `OK`
- `WARN`
- `FAIL`
- `STOP` (опционально, если engine различает `FAIL` и `STOP`)

Требование:
- ключи `nodeStates` должны быть подмножеством `graph.nodes[].id`
- порядок ключей при сериализации результата — детерминированный (лексикографический по nodeId)

#### 1.2.4 edgeStates (опционально)

- `edgeStates: { [edgeId: string]: EdgeState }` (если engine считает рёбра)

`EdgeState` (MVP enum):
- `OK`
- `WARN`
- `FAIL`

#### 1.2.5 ledger (обяз.)

`ledger[]` — список **фактов симуляции**. Это “судовой журнал”, а не интерпретация.

Форма записи (MVP):
- `ts` (ISO8601)
- `code` (string; машинный код события)
- `message` (string; человекочитаемая формулировка факта)
- `refs` (string[]; ссылки на сущности/снапшоты/пороговые коды)

Запреты для ledger:
- запрещены рекомендации (“сделайте X”, “нужно увеличить Y”)
- запрещены KPI/планы работ
- запрещён “management advice” любого вида
- разрешены только:
  - фиксация событий,
  - фиксация порогов/условий,
  - фиксация причинно-следственных шагов *в терминах модели*.

#### 1.2.6 resultHash (обяз.)

- `resultHash = sha256(canonicalResultJson)`

`canonicalResultJson`:
- результат, сериализованный детерминированно (см. `D_determinism.md`)
- без нестабильных полей и с фиксированным порядком ключей

---

## 2) Детерминизм и воспроизводимость

MVP-требование:

- один и тот же `CanonicalGraph` (по `contentHash`)
- один и тот же `scenario` (включая `seed`)
- одна и та же версия engine

⇒ должны давать **бит-в-бит одинаковый** `SimulationResult` и `resultHash`.

Любое нарушение считается дефектом детерминизма.

---

## 3) Политика unknown/missing

Симуляция **не должна** “додумывать” отсутствующие данные.

Если вход неполон:
- применяется `options.unknownHandling`:
  - `drop`: объект/связь игнорируется, факт фиксируется в ledger
  - `keep-as-unknown`: объект остаётся, но состояния/логика должны быть строго определены (в MVP не рекомендуется)

---

## 4) Явные запреты (non-negotiable)

Симуляция (и её результат) **не имеет права**:
- выдавать рекомендации, приоритеты, планы действий
- вычислять “score зрелости” или “целевые KPI”
- давать “оптимизацию портфеля”
- предлагать изменения оргструктуры, найм, бюджет
- экспортировать отчёты (PDF/PPT) как часть engine контракта

Разрешено только:
- фиксировать структуру,
- фиксировать пороги,
- фиксировать STOP/LOCK,
- фиксировать фактологический ledger.

---

## 5) Связь с fixtures (MVP)

В репозитории fixtures являются нормативными примерами:
- `fixtures/simulationinput.sample.json` — пример `SimulationInput` (в MVP использует `graphRef`)
- `fixtures/simulationresult.sample.json` — пример `SimulationResult`
- `fixtures/canonicalgraph.sample.json` — пример `CanonicalGraph`

Изменение формы контракта требует синхронного обновления fixtures.
