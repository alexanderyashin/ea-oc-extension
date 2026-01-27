---
title: "A. Canonical Model"
purpose: "Определить каноническую headless модель системы для ingestion → simulation"
audience: ["Core dev", "Connector dev", "Simulation dev"]
language: "RU"
evidence_profile: "Design-spec (schema + invariants)"
role: "Canonical data model spec"
status: "ACTIVE"
---

# A. Каноническая модель (Canonical Graph)

## 0) Назначение модели

Каноническая модель отделяет:
- **внешние источники данных** (LeanIX и др.), которые могут быть нестабильны,
- от **внутреннего детерминированного ядра** (CanonicalGraph),
  являющегося единственным контрактом для симуляции.

Модель обязана быть:
- **детерминированной** (см. D_determinism.md)
- **headless** (никаких UI-полей)
- **расширяемой без поломки MVP**
- **без BI / рекомендаций / оптимизаций**

---

## 1) Базовый концепт

Система представляется как **ориентированный мультиграф**:

- `Node` — сущность
- `Edge` — направленное отношение

### 1.1 Общие поля

Каждый `Node` и `Edge` **обязан** содержать:

- `id` — стабильный строковый идентификатор
- `kind` — тип сущности/отношения
- `attrs` — JSON-совместимый словарь атрибутов
- `provenance` — происхождение данных

---

## 2) Структура CanonicalGraph

```text
CanonicalGraph
├─ meta
│  ├─ schemaVersion
│  ├─ sourceSystem
│  ├─ snapshotId
│  ├─ capturedAt
│  └─ determinism
├─ nodes[]
└─ edges[]
2.1 meta
schemaVersion — версия схемы (например CG-0.1)

sourceSystem — основной источник снапшота

snapshotId — идентификатор снапшота

capturedAt — ISO8601 timestamp

determinism

sortOrder

hashAlgo

contentHash

3) MVP-онтология узлов
3.1 Допустимые Node.kind (MVP)
1) application
Смысл: прикладная система или сервис.

Обязательные attrs:

name (string)

externalId (string)

Допустимые attrs (optional):

lifecycle

criticality

owner

tags

2) interface
Смысл: контракт взаимодействия (API / интеграционный объект).

Обязательные attrs:

name

externalId

Допустимые attrs:

category

protocol

3) system (допустим, но не обязателен в MVP)
Нейтральный контейнер, если источник его предоставляет.

Обязательные attrs:

name

externalId

❗ В MVP запрещены другие Node.kind
(capability, process, orgUnit и т.д.).

4) MVP-онтология рёбер
4.1 Допустимые Edge.kind (MVP)
1) depends_on
application → application

2) exposes_interface
application → interface

3) consumes_interface
application → interface

4) connects_to (опционально)
interface → interface

4.2 Атрибуты рёбер
Обязательные attrs:

externalId

relationType (исходный тип из источника)

Допустимые attrs:

strength

❗ Направление связи определяется самой дугой.
Поле direction запрещено.

5) Идентичность и ID-стратегия
5.1 Базовое правило
id должен быть стабилен относительно источника.

Рекомендуемый формат:

<kind>:<source>:<workspace>:<externalId>
5.2 Fallback (крайний случай)
Если externalId отсутствует:

<kind>:<source>:<workspace>:hash(<stableKeyFields>)
stableKeyFields обязаны быть:

перечислены

неизменны

документированы

6) Provenance (обязателен)
Каждый Node и Edge содержит:

sourceSystem

sourceObjectType

sourceObjectId

sourcePath (optional)

ingestedAt

connectorVersion

7) Контракт до симуляции
7.1 SimulationInput
graph — CanonicalGraph или его подграф

scenario

shockType

intensity

targetSelector

seed

options

strictDeterminism (default true)

unknownHandling (drop | keep-as-unknown)

7.2 SimulationResult
stop (bool)

nodeStates (map)

edgeStates (optional)

ledger[]

resultHash

8) Явные запреты
KPI / maturity / recommendations

BI-метрики

UI-поля (layout, coords, colors)

runtime-счётчики

нефиксированные timestamps в attrs

9) Версионирование
CG-0.1 — MVP

расширения:

backward-compatible → minor

breaking → major + миграция

Схема — это контракт.
Контракт важнее удобства.