---
title: "D. LeanIX Import UI"
purpose: "Определить UI-флоу импорта SAP LeanIX export в Cockpit (Iteration 2: UI + wiring, без изменения семантики)"
audience: ["Frontend dev", "Tool architect", "Backend dev (ingestion endpoint)"]
language: "RU"
evidence_profile: "Design-spec (UI contract + invariants + failure modes)"
role: "Frontend import flow spec"
status: "ACTIVE"
---

# D. LeanIX Import UI (Iteration 2)

## 0) Контекст и инварианты (binding)

Цель Iteration 2 — добавить в Frontend Tool MVP **полноценный импорт-флоу** для SAP LeanIX:
- ingestion уже существует в backend;
- UI делает upload, показывает факты и делает baseline graph;
- **никакой** интерпретации, BI, рекомендаций, “улучшений”, write-back.

**READ-ONLY / НЕИЗМЕНЯЕМО:**
- CanonicalGraph
- RawSnapshot (LeanIX)
- Determinism & hashing
- SimulationInput / SimulationResult
- Metrics Engine (M1–M4)
- STOP / simLocked семантика

Frontend **НЕ ИМЕЕТ ПРАВА**:
- менять CanonicalGraph;
- “чистить”, “лечить”, нормализовать или “улучшать” данные;
- обходить STOP / simLocked;
- автозапускать симуляции;
- делать write-back в LeanIX;
- генерировать выводы/оценки качества/риски.

---

## 1) UX Entry Point (I1)

В Cockpit появляется точка входа:
- UI элемент **Import LeanIX**
- принимает LeanIX export (MVP: file-based)
- рядом — краткая фиксация: “Поддерживаемый формат: как в backend ingestion”.

В UI явно показывается:
- что загружается **сырой экспорт**;
- что после загрузки строится CanonicalGraph;
- что **baseline** обновится на импортированный граф.

---

## 2) Visibility (I2): факты импорта

После успешного импорта UI должен отобразить **строго факты**:

- `rawHash`
- `contentHash`
- `timestamp`

Формулировка статуса должна быть нейтральной:
- “Данные загружены. Модель построена.”

---

## 3) Baseline Graph (I3)

CanonicalGraph, полученный из LeanIX, становится baseline:

- baselineGraph := imported CanonicalGraph
- resetShock() возвращает именно baselineGraph
- НЕТ авто-шоков, НЕТ авто-симуляций, НЕТ auto-run метрик (кроме существующих ручных триггеров, если они уже есть)

---

## 4) Import Result Surface (I4): facts-only summary

Показывается summary:
- количество `nodes`
- количество `edges`
- типы узлов: `application / interface / dependency` (или то, что реально присутствует в CanonicalGraph)

**Запрещено**:
- любые “оценки качества”
- “слишком сложно”, “рискованно”
- “плохая архитектура” и любые выводы

---

## 5) Failure Modes (I5): честные ошибки

UI должен явно фиксировать (без эвфемизмов):

1) Некорректный файл:
- “Некорректный файл. Backend ingestion отклонил загрузку.”

2) Неподдерживаемая версия:
- “Неподдерживаемая версия export.”

3) Пустые данные:
- “Пустые данные: импорт завершён без объектов.”

Дополнительно:
- показывать техническую строку ошибки (status code / message), если она есть, без интерпретаций.

---

## 6) Wiring contract (frontend ↔ store)

Frontend вызывает строго **действия уровня store**:

- `loadRawSnapshot(file)`  
  Загружает LeanIX export в backend ingestion и получает:
  - `rawSnapshot`
  - `rawHash`
  - `contentHash`
  - `timestamp`

- `buildCanonicalGraph()`  
  Строит CanonicalGraph **по контракту** (используя уже существующую сборку, без “лечения”).

- `setBaselineGraph(graph)`  
  Делает baseline текущим graph.

После этого:
- `resetShock()` возвращает baselineGraph.

---

## 7) Definition of Done (DoD)

- Пользователь может загрузить LeanIX export
- CanonicalGraph строится и становится baseline
- Хеши отображаются как факты
- Reset возвращает LeanIX baseline
- Симуляция и метрики работают поверх импортированных данных
- Ошибки импорта честно показаны
- Никакой запрещённой функциональности не добавлено
- Документация обновлена
- Gates: typecheck + build GREEN
- Commit + push
- Full report в ARCHITECT TOOL HQ
