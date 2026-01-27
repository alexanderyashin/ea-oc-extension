# E — UI System Derivation (Functional Core → Observable UI)

**Project:** EA-OC-EXTENSION / ESTRA  
**Parent:** PRODUCT SYSTEM HQ  
**Child:** CHILD-E (UI System Derivation)  
**Status:** ACTIVE (facts-first; derived from observed repo + binding excerpts)  
**Language:** RU only  
**Rule:** Diagnostic-only. No prescriptions. Repo is SPOT.

---

## 0) Binding basis (что является источником истины)

**Binding (declared):**
- `docs/product/B_user-ontology.md` — **NOT PROVIDED in this run output** → cannot be used as binding evidence here.
- `docs/product/C_functional-core.md` — **PROVIDED (excerpt)** → used as functional contract.
- `docs/product/D_formal-realization.md` — **PROVIDED (partial; encoding artifacts; truncated)** → used only for the declared strata and general mapping intent.

**Observed implementation (repo SPOT):**
- UI:
  - `apps/cockpit/src/ui/TopBar.tsx`
  - `apps/cockpit/src/ui/Inspector.tsx`
  - `apps/cockpit/src/ui/Palette.tsx`
  - `apps/cockpit/src/ui/Ledger.tsx`
  - `apps/cockpit/src/ui/LockedFeatureDialog.tsx`
- Store:
  - `apps/cockpit/src/store/graph.store.ts` (**provided partial; truncated in the pasted output**)

**Norm (operational for this document):**
- We derive *must-be-visible / must-not-exist / conditional* UI statements only from:
  1) the **functional invariants** stated in C (STOP terminal, ledger factual trace, no hidden mutation, no healing),
  2) the **observed UI + store behavior** in the current repo.
- Anything that requires B or full D is explicitly marked as **Not evidenced here**.

---

## 1) Functional outputs that MUST become observable (core → UI)

From C (excerpt) the minimal observation set is:

- **O1:** `store.simLocked -> bool` (STOP latch)
- **O2:** `store.nodeStates -> statuses` (map of states)
- **O3:** `store.ledger -> chronological facts` (explainability)
- **O4:** `last StopFlag (если присутствует в ledger) -> reason`

Additionally, C states:
- STOP is a **terminal functional invariant** (not a UI rule).
- Ledger is **mandatory output** of the Shock→Cascade→Θ→STOP chain.

Therefore UI must act as a **projection** of store state, not a second system.

---

## 2) Functional State → Observable UI State (таблица соответствия)

> Таблица фиксирует **что видно**, а не “что можно сделать”.

| Functional Core State (from C + observed store fields) | Observable UI State (must be visible) | Evidence (repo) |
|---|---|---|
| **S0: Seed / Reset baseline** (`simLocked=false`, `nodeStates={}`, `ledger=[]`) | UI показывает “OK”, STOP не активен; граф в baseline; ledger пустой/“No events yet” | `Ledger.tsx` empty-state text; `TopBar.tsx` shows "OK"; `graph.store.ts` init `ledger: []`, `simLocked: false`, `nodeStates: {}` |
| **S1: Configurable (pre-run)** (shock type/scope/intensity selectable) | Видимая панель конфигурации шока (selects); UI не скрывает что intensity дискретна | `TopBar.tsx` selects: type/scope/intensity (0.1/0.3/0.5) |
| **S2: Shock run executed** (`runShock` calls compute; updates nodeStates + ledger; may set stop) | Видно, что был запуск: ledger имеет события; на графе меняются стили узлов (OK/WARN/RED/STOP) | `graph.store.ts` `runShock()` → `simulateShock` → `set({ nodeStates, ledger, simLocked, nodes: style(...)})`; `stateStyle()` mapping |
| **S3: Threshold crossings (Θ events)** (ledger contains threshold facts) | Ledger показывает события типа `threshold_crossed` с nodeLabel, prev→threshold, scorePrev→scoreNext, step | `Ledger.tsx` render of `"threshold_crossed"` |
| **S4: STOP terminal** (`simLocked=true` latch) | UI обязана показывать STOP как терминальное состояние и запрещать “новый run” на уровне функциональной доступности (disabled) | `TopBar.tsx` disables selects + Run Shock; shows "STOP"; `Ledger.tsx` header shows "STOP locked" |
| **S5: Post-STOP read-only** (observations only) | Разрешено: просмотр ledger и текущих состояний; запрещено: любые мутации core-состояния кроме Reset | C §5.1, §6; observed disabling in `TopBar.tsx` |
| **S6: Reset** (returns to seed; clears stop+ledger+states) | UI обязана иметь Reset и после него возвращаться в S0 | C §8 пункт 5; observed Reset button exists in `TopBar.tsx` but realization mismatch (см. §7) |

---

## 3) Must-be-visible UI elements (O1..On)

UI-элементы, которые **обязаны существовать** как наблюдаемое проявление core:

**O1. STOP latch indicator (global, persistent).**  
- Должно быть видно “OK/STOP” и это должно напрямую соответствовать `store.simLocked`.
- STOP обязан быть **защёлкой** (не мигать, не “разлочиваться сам”).

**Observed:**  
- `TopBar.tsx`: текст `STOP/OK` + disable controls when `simLocked`.  
- `Ledger.tsx`: header shows `STOP locked` when `simLocked`.

---

**O2. Ledger panel as factual trace (observation-only).**  
Минимум: показать события в хронологическом порядке, без интерпретации и советов.  
Ledger обязан быть “why” в виде фактов, иначе система превращается в “цветной граф”.

**Observed:**  
- `Ledger.tsx` показывает список событий (reverse), типы: `threshold_crossed`, `info`, `global_stop`, без рекомендаций.

---

**O3. Node state map must be visually encoded on the graph.**  
`nodeStates` должны проявляться как визуальная/логическая карта состояний.

**Observed:**  
- `graph.store.ts`: `stateStyle()` sets border/background for `OK/WARN/RED/STOP` and applies per node after run.

---

**O4. Discrete ShockSpec must be visible as discrete choice (not a slider).**  
C требует дискретную интенсивность (как минимум текущие значения).  
Следовательно UI не должен “рисовать” непрерывность там, где её нет.

**Observed:**  
- `TopBar.tsx` intensity select: 10/30/50 (0.1/0.3/0.5).

---

**O5. “Demo is partial” + “No control/No optimization/No output” must be explicit.**  
Это не “маркетинг”, а анти-продуктизация: UI не должен выглядеть как BI/контроль.

**Observed:**  
- `TopBar.tsx`: “No control. No optimization. No output.” + DEMO badge.
- `LockedFeatureDialog.tsx`: “diagnostic-only”, gated features, “No hidden exports exist in the demo.”

---

**O6. Reset must exist and be reachable from STOP.**  
Потому что после STOP разрешены только observation + reset (C §5.1).

**Observed:**  
- `TopBar.tsx` has Reset button always enabled; however functional reset is mismatched (см. §7).

---

## 4) Must-not-exist UI elements (Z1..Zm) — запрещённые элементы

Запреты выводятся из C (§5.3, §9) и из общего принципа “UI = observation, not control”.

**Z1. Любые UI-элементы “recommend / mitigate / fix / optimize”.**  
Причина: запрещено “healing”, “recommend mitigations”, “optimize to avoid STOP” — превращает демонстратор в инструмент управления.

**Z2. “Undo cascade”, “continue after STOP”, “resume simulation”.**  
Причина: STOP терминален (C §5.1; STOP latch). Продолжение расчёта после STOP запрещено как функциональность.

**Z3. Любые отчёты/экспорт/печать/генерация документов для внедрения.**  
Причина: C §9 (export/reporting forbidden), плюс анти-продуктизация демо.

**Z4. KPI/scoring/benchmarking dashboards.**  
Причина: C §9; UI не должен обещать “оценку зрелости” или “скоринг”.

**Z5. Free-form “what if” без фиксации envelope и без ledger-фактов.**  
Причина: нарушает контракт traceability и превращает в песочницу оптимизации.

**Z6. Любая скрытая мутация core-состояния из UI.**  
Причина: C §5.2 “No hidden state mutation” и запрет обхода StorePatch/F6 (в терминах C).

---

## 5) Conditional UI elements (условность: STOP / Θ / tier)

### 5.1 STOP-conditional behavior (терминальная граница)
Если `store.simLocked = true`, UI обязана:
- **запретить** любые действия, приводящие к новому run (`runShock`) или мутации `nodeStates` через compute.
- **разрешить** только:
  - наблюдение (ledger + states),
  - reset.

**Observed:**
- `TopBar.tsx` disables selects + Run Shock when `simLocked`.
- Reset button не disabled (OK).

### 5.2 Θ-conditional visibility (threshold crossings)
Если ledger содержит события пересечения порогов, UI должна показывать:
- факт события (step, nodeId/label),
- переход состояния (prev→threshold),
- численные факты (scores).

**Observed:**
- `Ledger.tsx` renders `threshold_crossed` with exactly these fields.

### 5.3 Tier gating (DEMO vs FULL)
- В DEMO можно показывать “locked features”, но **нельзя** симулировать наличие скрытых экспортов/функций.
- Locked feature UI должен:
  - явно сказать “partial demo”,
  - не предлагать обходов,
  - не создавать альтернативных путей “получить результат”.

**Observed:**
- `LockedFeatureDialog.tsx` соответствует (explicit gating; “No hidden exports exist in the demo.”).

---

## 6) STOP & Ledger — как обязаны быть визуально выражены

### 6.1 STOP expression rules (UI has no right to soften STOP)
UI **не имеет права**:
- скрыть STOP,
- “перекрасить” STOP в WARN,
- дать ощущение что STOP “не страшно” или “можно продолжить”.

UI обязана:
- показывать STOP как бинарный latch,
- блокировать run/compute-мутации,
- оставить видимыми факты причин (ledger).

**Observed compliance:**
- STOP shown in `TopBar` and `Ledger` header.
- Controls disabled in `TopBar`.

### 6.2 Ledger expression rules (UI has no right to interpret facts)
UI **не имеет права**:
- заменять ledger “объяснением” своими словами,
- выводить “значит вам надо…”,
- сворачивать причины в итоговый verdict.

UI обязана:
- показывать ledger как factual chronological trace,
- сохранять типы событий и численные поля,
- не удалять “неудобные” события.

**Observed compliance:**
- `Ledger.tsx` renders factual text; no recommendations.

---

## 7) Observed mismatches / violations (на основе текущего repo)

> Это не “предложения улучшить”, а регистрация несоответствий контракту C.

### M1 — Reset does not clear STOP latch / ledger (likely mismatch)
C (excerpt) требует: Reset возвращает к seed и, как минимум, очищает:
- `simLocked=false`
- `nodeStates={}`
- `ledger=[]` (или reset-event)

**Observed in `graph.store.ts` (pasted fragment):**
- `resetShock()` очищает `nodeStates` и styles,
- но **не видно** сброса `simLocked` и **не видно** очистки `ledger`.

⚠️ Примечание: файл `graph.store.ts` в пасте обрезан, поэтому фиксируем формулировку как:
- “в предоставленном фрагменте reset не сбрасывает simLocked/ledger”.

### M2 — UI controls for “Extended (Full build)” выглядят повреждёнными в paste
В `TopBar.tsx` фрагмент “Extended (Full build)” в пасте не оформлен как `<button>...`.
Если это реальный код, это UI-дефект; если обрезка пасты — ignore.
(Не делаем выводов без полного файла.)

### M3 — Palette does not call addNode in pasted fragment
В `Palette.tsx` в пасте кнопка не вызывает `addNode(...)` (button body пустой).
Если это реальный код, то palette не выполняет роль “add nodes”, но C-контракт про это не говорит.
Это скорее “UX shell completeness” issue, не core-invariant.

---

## 8) Non-UI-Claims (что UI НЕ обещает и НЕ объясняет)

UI демонстратора **не обещает**:
- применимость к конкретной организации,
- корректность как “оценка зрелости” или “диагноз предприятия”,
- рекомендаций, планов, mitigation,
- оптимизации и “как избежать STOP”,
- генерации отчётов/документов для внедрения.

UI **не объясняет**:
- “почему это хорошо/плохо”,
- “что делать дальше”,
- “как улучшить показатели”.

UI **показывает только**:
- факт шока (как задан),
- факт каскада и пересечений Θ (как ledger),
- факт STOP (как latch),
- фактическое состояние графа (как statuses).

---

## 9) Minimal UI contract for ESTRA demo (UI-agnostic, but enforceable)

Чтобы UI считался корректной проекцией ESTRA demo core, он должен:

1) Делать видимой дискретность ShockSpec (type/scope/intensity).  
2) Иметь явное выражение STOP latch (O1) и блокировать run при STOP.  
3) Визуализировать `nodeStates` на графе (O3).  
4) Экспонировать ledger как factual trace (O2) и не интерпретировать его.  
5) Иметь Reset, возвращающий в seed (S0) и очищающий STOP+ledger+states (в соответствии с C).  

---

## 10) Traceability hooks (UI projection)

UI должен отображать (как минимум) поля ledger:
- `type` (threshold_crossed / info / global_stop)
- `step`
- `refs` (nodeId/nodeLabel) — где применимо
- `facts` (scorePrev/scoreNext; state prev→threshold; reason)

**Observed:**
- `Ledger.tsx` уже показывает `step`, `nodeId`, `nodeLabel`, `prev`, `threshold`, `scores`, `reason`.

---

END.
