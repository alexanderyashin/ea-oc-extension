---
title: "D. Determinism"
purpose: "Формальные правила: каноническая сортировка/сериализация/хэширование"
audience: ["Core dev", "Connector dev", "Audit"]
language: "RU"
evidence_profile: "Design-spec (deterministic rules)"
role: "Determinism contract"
status: "ACTIVE"
---

# D. Детерминизм (backend contract)

## 1) Принцип
Одинаковый входной снимок (RawSnapshot) при одинаковой версии адаптера/нормализатора/engine
должен давать **бит-в-бит одинаковый** CanonicalGraph, SimulationResult и одинаковые хэши.

## 2) Канонический порядок (нормализация)

### 2.1 Nodes
Сортировать `nodes[]` по:
1) `id` (лексикографически, Unicode code point order)
2) если равны — **запрещено** (ID обязан быть уникальным)

### 2.2 Edges
Сортировать `edges[]` по tuple:
1) `source`
2) `target`
3) `kind`
4) `id`

Если `id` равны — **запрещено** (ID ребра обязан быть уникальным).

## 3) Каноническая сериализация JSON (canonicalJson)

### 3.1 Что такое canonicalJson
`canonicalJson` — это **строка JSON**, полученная после:
1) `ConvertFrom-Json` (парсинг в объект),
2) `ConvertTo-Json -Depth 100 -Compress` (обратная сериализация в одну строку).

Это нормативная процедура для MVP, так как именно она используется для вычисления эталонных fixture-хэшей.

### 3.2 Требования к сериализации
- порядок ключей: **лексикографический** (как отдаёт `ConvertTo-Json`; для MVP это считается источником истины)
- даты: только ISO8601 строкой (`YYYY-MM-DDTHH:mm:ssZ`)
- запрещены поля, зависящие от времени выполнения (случайные id, UI coords, now-тimestamps и т.п.)
- числа: реализация должна обеспечивать **стабильную строковую форму** при сериализации (если влияет на hashing)

### 3.3 Запрет на “pretty JSON”
`canonicalJson` в MVP **всегда** считается на `-Compress` (одна строка).
Любые форматированные/pretty варианты JSON не являются canonical и не должны хэшироваться.

## 4) Хэширование (sha256)

### 4.1 Алгоритм
- `hashAlgo = sha256`
- кодировка строки перед хэшированием: **UTF-8**

### 4.2 Формулы
- `contentHash = sha256(canonicalGraphJson)`
- `resultHash  = sha256(canonicalResultJson)`

Где:
- `canonicalGraphJson` = canonicalJson для CanonicalGraph
- `canonicalResultJson` = canonicalJson для SimulationResult

### 4.3 Нормативный PowerShell-референс (MVP)
CanonicalGraph:

```powershell
$canonical = Get-Content docs/architect-tool/backend/fixtures/canonicalgraph.sample.json -Raw |
  ConvertFrom-Json |
  ConvertTo-Json -Depth 100 -Compress

$hash = [System.BitConverter]::ToString(
  [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($canonical)
  )
).Replace("-", "").ToLower()

"sha256:$hash"

SimulationResult:

$resultCanonical = Get-Content docs/architect-tool/backend/fixtures/simulationresult.sample.json -Raw |
  ConvertFrom-Json |
  ConvertTo-Json -Depth 100 -Compress

$rh = [System.BitConverter]::ToString(
  [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($resultCanonical)
  )
).Replace("-", "").ToLower()

"sha256:$rh"


Примечание: это не “пример”, а нормативный эталон для MVP (fixtures обязаны совпадать).

5) Нормализация unknown/missing

отсутствует внешний ID у объекта источника → объект отбрасывается + запись в errors[] (RawSnapshot) и/или ledger[] (SimulationResult)

отсутствует name при наличии внешнего ID → name = "<unknown>" + запись в errors[]/ledger[]

6) Запреты (non-negotiable)

нельзя использовать счётчики/рандом в рантайме для генерации ID

нельзя включать нестабильные поля в attrs (например timestamp "now")

нельзя менять правила сортировки/сериализации без:

обновления этого документа,

пересчёта fixture-хэшей,

фиксации изменения версией схемы/контракта (в соответствующих документах A/E).