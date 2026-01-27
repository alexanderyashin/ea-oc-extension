---
title: "B. Ingestion — SAP LeanIX (MVP)"
purpose: "Определить MVP-адаптер LeanIX → CanonicalGraph и контракт RawSnapshot"
audience: ["Connector dev", "Core dev"]
language: "RU"
evidence_profile: "Doc-driven mapping (LeanIX concepts → CanonicalGraph)"
role: "LeanIX ingestion spec"
status: "ACTIVE"
---

# B. Ingestion — SAP LeanIX (MVP)

## 0) Граница и смысл ingestion (MVP)

Ingestion делает только:
- извлечение фактов из источника,
- нормализацию в **RawSnapshot**,
- преобразование RawSnapshot → **CanonicalGraph** (см. A),
- запись ошибок в `errors[]` (без “умных” выводов).

Ingestion **не делает**:
- никаких рекомендаций / интерпретаций / BI,
- никаких write-back операций в LeanIX (update/patch/import) в MVP,
- никаких UI-полей и представлений,
- никаких “обогащений” из внешних справочников.

---

## 1) Контракт RawSnapshot (до нормализации)

RawSnapshot — артефакт воспроизводимости: “что именно было увидено в LeanIX”.
Он должен быть достаточен, чтобы повторно построить тот же CanonicalGraph при той же версии коннектора.

### 1.1 Структура

```json
{
  "meta": {
    "sourceSystem": "leanix",
    "workspace": "string",
    "capturedAt": "ISO8601",
    "connectorVersion": "semver",
    "queries": ["string", "..."]
  },
  "factsheets": [ { /* minimal fields */ } ],
  "relations":  [ { /* minimal fields */ } ],
  "errors":     [ { "code": "string", "message": "string", "refs": ["string"] } ],
  "rawHash": "sha256:..."
}
1.2 Minimal fields (MVP)
factsheets[] (минимум):

id (externalId в LeanIX)

type (например "Application", "Interface")

name (может отсутствовать — см. политику unknown)

relations[] (минимум):

id (externalId relation)

type (строка — исходный тип связи)

from (factsheet id)

to (factsheet id)

1.3 rawHash (MVP правило)
rawHash — хэш канонически сериализованного RawSnapshot после:

удаления явно нестабильных полей (если источник их добавляет),

сортировки массивов factsheets и relations по стабильному ключу (id),

стабильной JSON-сериализации (ключи объектов по лексикографическому порядку).

rawHash — для трассировки “это тот же вход”.
Детерминизм CanonicalGraph отдельно фиксируется contentHash (см. A/D).

2) Маппинг RawSnapshot → CanonicalGraph
2.1 Fact Sheet → Node
Application Fact Sheet → Node(kind="application")
id:

application:leanix:<workspace>:<factSheetId>

kind: "application"

attrs (MVP):

name: из factsheet.name (если отсутствует → <unknown>, см. 3.3)

externalId: factsheet.id

остальные поля (lifecycle/criticality/owner/tags) — только если явно присутствуют в raw фактах (как факты, без вычислений)

provenance:

sourceSystem: "leanix"

sourceObjectType: "FactSheet"

sourceObjectId: <factSheetId>

ingestedAt: = meta.capturedAt

connectorVersion: = meta.connectorVersion

Interface Fact Sheet → Node(kind="interface")
id:

interface:leanix:<workspace>:<factSheetId>

kind: "interface"

attrs (MVP):

name (или <unknown>)

externalId

category / protocol — только если реально присутствуют в raw фактах (иначе не выдумывать)

provenance: как выше (FactSheet)

В MVP мы не делаем meta-model introspection. Если типы/категории не доступны напрямую — они просто отсутствуют.

2.2 Relation → Edge
Общая форма Edge
id:

edge:<kind>:leanix:<workspace>:<relationId>

kind: выбирается по правилам ниже

source, target: mapped node ids

attrs (MVP):

relationType: raw relation.type

externalId: raw relation.id

иные поля — только если это факты из источника (например strength), без вычислений

provenance:

sourceSystem: "leanix"

sourceObjectType: "Relation"

sourceObjectId: <relationId>

ingestedAt: = meta.capturedAt

connectorVersion: = meta.connectorVersion

Правила выбора kind (MVP)
Мы не интерпретируем семантику глубже MVP. Используем только типы узлов (Application/Interface) и raw relation.type.

Application → Application
Если оба конца — Application, то:

kind = "depends_on"

Application → Interface
Если from — Application, to — Interface, то:

kind = "exposes_interface" или "consumes_interface" — только если raw relation.type однозначно различим по заранее заданному списку (см. 2.3).

Иначе (любая неоднозначность):

связь не включается в CanonicalGraph (MVP),

но фиксируется в errors[] RawSnapshot как code="RELATION_DROPPED".

2.3 Таблица соответствия relation.type → kind (MVP)
Чтобы избежать “магии”, коннектор обязан иметь явную конфигурацию маппинга (в коде или конфиге), например:

dependsTypes = ["depends", "requires", ...]

exposesTypes = ["exposes", "provides", ...]

consumesTypes = ["consumes", "uses", ...]

Если relation.type не попадает ни в один список:

правило 3) — drop + ошибка.

В демо-фикстурах используется:

depends → depends_on

exposes → exposes_interface

consumes → consumes_interface

3) Детерминизм и нормализация (обязательные правила)
3.1 Стабильные ID
ID нельзя генерировать счётчиками/рандомом.
В MVP: <kind>:leanix:<workspace>:<externalId> — единственный допустимый путь.

3.2 Сортировка
Перед вычислением contentHash CanonicalGraph:

nodes сортируются по id

edges сортируются по (source, target, kind, id)

(см. D. Determinism)

3.3 unknown/missing политика (MVP)
отсутствует factsheet.id → объект отбрасывается + errors[] (code="FACTSHEET_DROPPED_NO_ID")

есть id, но отсутствует/пустой name → name = "<unknown>" + errors[] (code="FACTSHEET_UNKNOWN_NAME")

relation без id или без from/to → relation отбрасывается + errors[] (code="RELATION_DROPPED_MISSING_FIELDS")

relation с концами, которые не найдены в factsheets → relation отбрасывается + errors[] (code="RELATION_DROPPED_UNKNOWN_ENDPOINT")

4) Fixtures (демо-артефакты)
MVP должен быть способен воспроизвести следующие фикстуры:

docs/architect-tool/backend/fixtures/rawsnapshot.leanix.sample.json

docs/architect-tool/backend/fixtures/canonicalgraph.sample.json

docs/architect-tool/backend/fixtures/simulationresult.sample.json

5) Точки расширения (вне MVP)
Возможные расширения (не реализуются в MVP, но допускаются архитектурно):

meta-model introspection (типы/подтипы/кастомные relation types),

расширенная онтология (capability/process/org),

import/export processors и write-back,

политика прав/ролей/групп,

частичные снапшоты и диффы.

