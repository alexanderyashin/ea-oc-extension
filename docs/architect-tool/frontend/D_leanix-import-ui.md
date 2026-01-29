---
title: "D. LeanIX Import UI (Iteration 2)"
purpose: "Определить UI-флоу импорта SAP LeanIX export в Cockpit (UI + wiring, без изменения семантики симуляции/метрик)"
audience: ["Frontend dev", "Tool architect", "Backend dev (ingestion endpoint)"]
language: "RU"
evidence_profile: "Design-spec (UI contract + invariants + failure modes)"
role: "Frontend import flow spec"
status: "ACTIVE"
---

# D. LeanIX Import UI (Iteration 2)

## 0) Инварианты (binding)

Цель Iteration 2 — добавить в Frontend Tool MVP полноценный **импорт-флоу** для SAP LeanIX:

- ingestion уже существует в backend (`/api/ingest/leanix`);
- UI делает upload, показывает **факты**, и фиксирует **baseline graph**;
- никакой интерпретации, BI, рекомендаций, “улучшений”, авто-фиксов.

Frontend НЕ должен:
- нормализовать данные;
- “лечить” CanonicalGraph;
- автоматически запускать симуляцию;
- делать write-back.

---

## 1) Entry Point (I1)

В Cockpit присутствует точка входа:
- UI элемент **Import LeanIX**
- file-based upload
- явная подпись: **supported format only** (ровно то, что принимает backend ingestion)

---

## 2) Wiring (I2): UI → Store

Frontend вызывает строго действия store:

1) `loadRawSnapshot(file)`
   - отправляет файл в backend ingestion (`/api/ingest/leanix`)
   - получает факт-артефакты:
     - `rawSnapshot` (opaque)
     - `rawHash`
     - `contentHash`
     - `timestamp`
   - может получить `canonicalGraph` (предпочтительно)

2) `buildCanonicalGraph()`
   - строит `CanonicalGraph` по контракту
   - в MVP wiring ожидает `canonicalGraph`, возвращённый backend ingestion
   - без нормализации/лечения

3) `setBaselineGraph(graph)`
   - импортированный CanonicalGraph становится baseline

Важно:
- импорт НЕ запускает симуляцию автоматически.

---

## 3) Import Result Visibility (I3): facts only

UI обязан показывать факты:

- `rawHash`
- `contentHash`
- `timestamp`

А также фактические counts:
- `nodes`
- `edges`
- `node kinds` (по `node.data.kind`)

Без оценок качества и без выводов.

---

## 4) Baseline Semantics (I4)

Инвариант:
- Imported `CanonicalGraph` становится baseline.
- `resetShock()` восстанавливает **ровно baseline**, очищая эпизод симуляции (ledger/nodeStates/metrics).
- Никакой “утечки мутаций”: baseline не должен меняться от runtime-операций.

---

## 5) Honest Failure Modes (I5)

UI обязан показывать явные сообщения (фактуально):

- invalid file / parse / ingestion reject → `import failed: ...` (с текстом ошибки backend, если есть)
- unsupported format → явная ошибка
- empty snapshot / empty canonicalGraph → явная ошибка или notice

Запрещены:
- silent fallbacks
- auto-fix
- “helpful advice”

---

## 6) Definition of Done (DoD)

- Пользователь может загрузить LeanIX export файлом
- CanonicalGraph построен и отображён на canvas (как текущий граф)
- Показаны факты: hashes/timestamp + counts
- Reset возвращает к импортированному baseline
- Симуляция и метрики работают поверх импортированных данных (только при ручном запуске)
- Ошибки честные и явные
- Документация обновлена
- Gates: `typecheck` + `build` GREEN
- Commit + push
- Full report в ARCHITECT TOOL HQ
