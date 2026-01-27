---
title: "A. Canonical Model"
purpose: "Определить каноническую headless модель системы для ingestion→simulation"
audience: ["Core dev", "Connector dev", "Simulation dev"]
language: "RU"
evidence_profile: "Design-spec (schema + invariants)"
role: "Canonical data model spec"
status: "ACTIVE"
---

# A. Каноническая модель (Canonical Graph)

## 0) Зачем нужна каноническая модель

Мы отделяем:
- **внешние источники** (LeanIX, позже другие) — всегда разные по полям/типам/семантике,
- от **внутреннего ядра** (CanonicalGraph) — единый контракт для симуляции и дальнейших вычислений.

Каноническая модель обязана быть:
- **детерминированной**
- **расширяемой** (новые типы узлов/рёбер без поломки MVP)
- **headless** (никаких UI-структур)
- **без BI/рекомендаций** (модель хранит факты, не выводы)

---

## 1) Концепт: Graph + Attributes

### 1.1 Типы сущностей

Модель представляет систему как ориентированный мультиграф:

- `Node` — сущность (приложение, интерфейс, внешний актор и т.д.)
- `Edge` — отношение (зависимость, интеграция, вызов, поток)

Обе сущности имеют:
- стабильный `id`
- `kind` (тип)
- `attrs` (словарь атрибутов, JSON-совместимый)
- `provenance` (откуда взялось)
- `timestamps` (время снапшота/загрузки)

### 1.2 Схема (логическая)

**CanonicalGraph**
- `meta`
- `nodes[]`
- `edges[]`

**meta**
- `schemaVersion` (например: `CG-0.1`)
- `sourceSystem` (например: `leanix`)
- `snapshotId` (строка)
- `capturedAt` (ISO8601)
- `determinism`
  - `sortOrder` (описание сортировки)
  - `hashAlgo` (например: sha256)
  - `contentHash` (хэш нормализованного контента)

---

## 2) MVP-онтология узлов и рёбер

### 2.1 Узлы (MVP)

1) `application`
- смысл: развертываемая или управляемая прикладная система
- минимальные attrs (MVP):
  - `name` (string)
  - `lifecycle` (optional: string)
  - `criticality` (optional: string/number)
  - `owner` (optional: string)
  - `tags` (optional: string[])
  - `externalId` (optional: string; id в источнике)

2) `interface`
- смысл: контракт взаимодействия (API/интерфейс/интеграционный объект)
- минимальные attrs:
  - `name`
  - `category` (optional: e.g. api/logical/other; если доступно)
  - `protocol` (optional)
  - `externalId`

3) `system` (опционально в MVP как "контейнер" или "placeholder")
- если источник даёт «системы/домены», но мы не хотим расширять онтологию — допускается как нейтральный контейнер
- attrs: `name`, `externalId`

> Примечание: в MVP **не вводим** capabilities, business processes, org units как обязательные node kinds.

### 2.2 Рёбра (MVP)

1) `depends_on` (Application → Application)
- смысл: логическая/техническая зависимость

2) `exposes_interface` (Application → Interface)
- смысл: приложение публикует интерфейс

3) `consumes_interface` (Application → Interface)
- смысл: приложение использует интерфейс

4) `connects_to` (Interface → Interface) (опционально)
- смысл: явная связка интерфейсов, если источник так моделирует интеграцию

#### Общие attrs ребра (MVP)
- `strength` (optional: number 0..1 или градация)
- `direction` (optional: string; если требуется зафиксировать семантику)
- `externalId`
- `relationType` (string; исходный тип отношения из источника)

---

## 3) Идентичность и детерминизм

### 3.1 ID-стратегия (строго)

`id` должен быть **стабилен** относительно источника.

Рекомендуемый формат:
- `id = "<kind>:<source>:<workspace>:<externalId>"`

Если `externalId` отсутствует, допускается fallback (только как крайняя мера):
- `id = "<kind>:<source>:<workspace>:hash(<stableKeyFields>)"`

`stableKeyFields` должны быть перечислены и неизменны (например `name + type`), иначе это не ID, а лотерея.

### 3.2 Детерминированная нормализация

Перед вычислением `contentHash`:
- nodes сортируются по `id` (лексикографически)
- edges сортируются по `(sourceId, targetId, kind, id)` (или `(sourceId,targetId,kind,externalId)` если id выводится из внешнего)
- attrs сериализуются с:
  - фиксированным порядком ключей
  - стабильным представлением чисел/дат
  - без случайных полей

---

## 4) Provenance (обязательное поле)

Каждый `Node` и `Edge` содержит `provenance`:

- `sourceSystem` (например: `leanix`)
- `sourceObjectType` (например: `FactSheet`, `Relation`)
- `sourceObjectId` (id из источника)
- `sourcePath` (optional: endpoint/query)
- `ingestedAt` (ISO8601)
- `connectorVersion` (semver; версия ingestion-адаптера)

Это критично для:
- трассировки ошибок
- воспроизводимости
- юридической и научной проверяемости (откуда факт)

---

## 5) Контракт до симуляции

### 5.1 SimulationInput (проекция)

Симуляция **не обязана** принимать весь граф. MVP-контракт:

- `graph`: CanonicalGraph (или subset)
- `scenario`:
  - `shockType` (enum)
  - `intensity` (number or enum)
  - `targetSelector` (enum: all / selected)
  - `seed` (string/number; фиксирует псевдослучайность, если она будет введена)
- `options`:
  - `strictDeterminism` (bool, default true)
  - `unknownHandling` (enum: drop / keep-as-unknown)

### 5.2 SimulationResult

- `stop` (bool) — признак STOP/LOCK
- `nodeStates` (map nodeId → state)
- `edgeStates` (optional)
- `ledger[]` — список фактов (события, причины, пороги), **без рекомендаций**
- `resultHash` (хэш результата)

---

## 6) Явные запреты модели

- Нельзя хранить “оценки зрелости”, “рекомендованные действия”, “приоритеты работ”
- Нельзя включать BI-метрики, которые выглядят как KPI-управление
- Нельзя кодировать UI-поля (layout, coordinates, colors) в CanonicalGraph
  - UI может иметь свой view-model, но **не здесь**

---

## 7) Версионирование схемы

- `CG-0.1` — MVP: applications/interfaces/dependencies
- Любое расширение (новые kinds/attrs) либо:
  - backward-compatible (minor), либо
  - через bump major и миграцию

Схема обязана быть описана как контракт — это важнее, чем удобство.

