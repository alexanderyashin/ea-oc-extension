<PASTE THE FULL FILE ABOVE>
# C — Functional Core (ESTRA Demo Instrument)
**Project:** EA-OC-EXTENSION / ESTRA  
**Parent:** PRODUCT SYSTEM HQ  
**Child:** CHILD-C (Functional Core)  
**Status:** ACTIVE (Functional Core фиксируется по факту текущего кода, без добавления новых возможностей)  
**Language:** RU  
**Rule:** Diagnostic-only. No prescriptions.

---

## 0. Binding dependencies (source of truth)
Это описание **не переопределяет** и не расширяет:
- `docs/product/A_capability-envelope.md` (capability envelope / границы)
- `docs/product/B_user-ontology.md` (онтология пользователя / ожидания)

**Норма:** при расхождении — A и B сильнее C.  
**Здесь:** зафиксирован минимальный функциональный контракт по факту существующего compute + store.

[ADDED] **Note (repo fact):** `A_capability-envelope.md` сейчас пустой (0 bytes).  
Следовательно, binding на A носит **номинальный** характер до появления содержания;  
все активные семантические ограничения по ролям/ожиданиям — через `B_user-ontology.md`.

---

## 1. Intent: что является “функцией” в этом документе
Функция = **чистое отображение** (input → state → observation) с фиксированными доменами/кодоменами.

- UI не является источником истины.
- UI только формирует входы и визуализирует наблюдения (observation).
- Все «смысловые события» должны быть выражены как элементы Ledger.

---

## 2. Core data model (минимальная модель типов)

### 2.1 Graph (модель предметной сцены)
- `Graph = (Nodes, Edges)`
- `Node.id : string`
- `Node.kind : string` (emap0-kind и т.п.)
- `Node.attrs : JsonObject`
- `Edge.id : string`
- `Edge.kind : string`
- `Edge.from, Edge.to : Node.id`
- `Edge.attrs : JsonObject`

> Важно: Functional Core оперирует **идентификаторами и атрибутами**.  
> Визуальные координаты, layout, drag — вне core.

### 2.2 Simulation input (shock spec)
Минимальный вход, который уже проявляется в демо (по UI и compute-пайплайну):

- `Scope = "ALL_SYSTEMS" | { type: "SELECTED_NODE", nodeId: string }`
- `Intensity = 10 | 30 | 50` (дискретные значения, как в текущем UI)
- `ShockSpec = { scope: Scope, intensity: Intensity, attrs?: JsonObject, mode?: string }`  <!-- [CHANGED] attrs added to match text below -->

Допустимо (как встречается в UI/сценарии демо), но не гарантируется как стабильный контракт:
- дополнительные параметры типа `drop`, `nodeFailureRate` и т.п.  
Если они существуют в коде — они являются расширением `ShockSpec.attrs`.

### 2.3 Threshold model (Θ)
- `Theta = { kind: string, value: number, unit?: string, attrs?: JsonObject }`
- `ThetaSet = Record<string, Theta>`

**Принцип:** Θ — это **не UI-порог**, а вычислительный оператор допустимости переходов.

### 2.4 STOP / Terminal
- `Stop = { stop: true, reason: string, at?: { nodeId?: string, edgeId?: string }, theta?: string }`
- `NoStop = { stop: false }`
- `StopFlag = Stop | NoStop`

STOP — **терминальное состояние вычисления**, не “режим UI”.

### 2.5 Ledger (factual emission)
- `LedgerEvent = { t: number, kind: string, refs?: JsonObject, facts: JsonObject }`
- `Ledger = LedgerEvent[]`

Ledger — **единственный канал объяснимости** демо: факты, а не выводы.

### 2.6 Simulation state (store-level)
Минимально наблюдаемое в store:
- `simLocked : boolean` (true если STOP и дальнейшие запуски запрещены)
- `nodeStates : Record<Node.id, string | JsonObject>` (минимум — статусы/цвета/состояния)
- `ledger : Ledger`
- `nodes : Node[]` (с обновлёнными attrs/флагами состояния, если так сделано в коде)

---

## 3. Base functions F1..Fn (обязательные)

### F1 — NormalizeShockInput (валидировать/нормализовать вход)
**Signature:**  
`F1: (graph: Graph, raw: ShockSpec) -> ShockSpec | Error`

**Назначение:** привести ввод к допустимому набору:
- `scope.nodeId` должен существовать в графе (если SELECTED_NODE)
- `intensity ∈ {10,30,50}`

**Важно:** F1 не имеет права «исправлять смысл», только валидировать и нормализовать.

---

### F2 — ApplyShock (детерминированное возбуждение/удар)
**Signature:**  
`F2: (graph: Graph, spec: ShockSpec) -> ShockEffect`

**Where:**  
`ShockEffect = { impacted: { nodes: string[], edges: string[] }, delta: JsonObject, ledger: Ledger }`

**Семантика:** F2 задаёт исходное возмущение, которое будет «питанием» каскада.  
**Ledger emission:** фиксирует факт удара: scope, intensity, затронутые узлы/рёбра.

---

### F3 — Cascade (распространение эффекта по связности)
**Signature:**  
`F3: (graph: Graph, effect: ShockEffect) -> CascadeResult`

**Where:**  
`CascadeResult = { nodeStates: Record<string, JsonObject>, intermediates?: JsonObject, ledger: Ledger }`

**Семантика:** каскад — это вычисление вторичных изменений состояния узлов/связей.  
**Ledger emission:** факт каскада: какие узлы/связи перешли в какие состояния, без интерпретации.

---

### F4 — EvaluateThresholds (проверка Θ и вычисление STOP)
**Signature:**  
`F4: (graph: Graph, cascade: CascadeResult, thetas: ThetaSet) -> ThresholdResult`

**Where:**  
`ThresholdResult = { stop: StopFlag, violations: { theta: string, at?: JsonObject, facts: JsonObject }[], ledger: Ledger }`

**Семантика:** Θ определяют допустимость текущей конфигурации после каскада.  
Если нарушен Θ_death/Θ_stop (как оно называется в коде) → формируется STOP.

---

### F5 — ReduceToStorePatch (сборка результата в store-патч)
**Signature:**  
`F5: (graph: Graph, cascade: CascadeResult, thr: ThresholdResult) -> StorePatch`

**Where:**  
`StorePatch = { simLocked: boolean, nodeStates: Record<string, JsonObject>, ledgerAppend: Ledger }`

**Семантика:** конвертировать вычисление в атомарное обновление store:
- `simLocked = thr.stop.stop`
- `nodeStates = cascade.nodeStates`
- `ledger += (F2.ledger + F3.ledger + F4.ledger)`

---

### F6 — CommitPatch (единственный разрешённый side-effect)
**Signature:**  
`F6: (store: Store, patch: StorePatch) -> Store`

**Семантика:** применить patch в zustand/store.  
**Норма:** все изменения store должны быть выражены через F6, иначе теряется трассируемость.

---

## 4. Derived functions (производные, не обязательные)

### D1 — RunSimulationOnce
**Signature:**  
`D1: (graph, thetas, rawShock, store) -> Store | Error`

**Definition (composition):**  
`D1 = F6 ∘ F5 ∘ (F2 → F3 → F4) ∘ F1`

Где `→` означает, что результат слева является входом справа.

---

### D2 — ResetSimulation
**Signature:**  
`D2: (seedGraph, store) -> Store`

**Семантика:** возвращение к seed/initial:
- `simLocked = false`
- `nodeStates = initial`
- `ledger = []` (или отдельное событие reset, если так принято)

---

## 5. Composition boundaries (где композиция запрещена)

### 5.1 Terminal boundary: STOP
Если `store.simLocked = true`, то запрещены:
- повторный вызов D1 (любой новый ShockRun)
- любые вычисления, которые меняют `nodeStates`

**Разрешено:**
- чтение (observations)
- reset (D2)

Это не UI-правило. Это **функциональный инвариант**: STOP = терминал.

---

### 5.2 No hidden state mutation
Запрещено изменять:
- `nodeStates`
- `ledger`
- `simLocked`
в обход `StorePatch`/F6.

---

### 5.3 No “healing” / recovery composition
Запрещены функции вида:
- “undo cascade”
- “recommend mitigations”
- “auto-fix graph”
- “optimize to avoid STOP”

Любые такие функции превращают демо в инструмент управления.

---

## 6. Observations (что является наблюдаемым выходом core)

Observation — это **проекция store на видимые данные**, без вычислений рекомендаций.

Минимальные наблюдения:
- `O1: store.simLocked -> bool` (STOP latch)
- `O2: store.nodeStates -> statuses` (визуальная/логическая карта состояний)
- `O3: store.ledger -> chronological facts` (объяснимость)
- `O4: last StopFlag (если присутствует в ledger) -> reason` (почему терминал)

---

## 7. STOP, Θ, Ledger — как они входят в ядро (не UI-эффект)

- Θ входят через **F4** как вычислительный оператор допустимости.
- STOP входит как результат **F4** и как защёлка `simLocked` через **F5/F6**.
- Ledger входит как обязательный выход **F2/F3/F4**, агрегируемый в **F5**.

**Критично:** без ledger система становится «цветным графом без причин».  
Ledger — обязательная часть functional core, а не “панель снизу”.

---

## 8. Minimal Functional Contract (UI-agnostic)
Чтобы считать систему реализацией ESTRA demo core, она обязана:

1) Иметь ShockSpec с дискретной интенсивностью (как минимум текущие значения).  
2) Реализовать цепочку: Shock → Cascade → Thresholds → STOP.  
3) Делать STOP терминальным (simLocked latch).  
4) Эмитить Ledger как factual trace всех фаз.  
5) Иметь Reset, возвращающий к seed.

---

## 9. Non-Functions (что принципиально НЕ является функцией системы)
Запрещено как функциональность (даже если можно “добавить позже”):

- Генерация рекомендаций, планов действий, mitigation-стратегий.
- Оптимизация/подбор параметров для «лучшего результата».
- Вычисление KPI, скоринга зрелости, benchmarking.
- Экспорт отчётов “для внедрения”, “для программы трансформации”.
- Free-form симулятор “что если” без фиксации envelope и без ledger-фактов.
- Пост-STOP “продолжить расчёт”.

Это сохраняет инструмент в режиме **демонстратора технологии**, а не продукта управления.

---

## 10. Traceability hooks (минимум для репозитория)
В ledger событиях должны быть поля:
- `kind` (SHOCK_APPLIED / CASCADE_STEP / THETA_VIOLATION / STOP_ASSERTED / RESET)
- `refs` (nodeId/edgeId если применимо)
- `facts` (числовые/логические значения, без интерпретации)

---
