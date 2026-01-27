---
title: "D. Determinism"
purpose: "Formale Regeln: kanonische Sortierung/Serialisierung/Hashing"
audience: ["Core dev", "Connector dev", "Audit"]
language: "RU"
evidence_profile: "Design-spec (deterministic rules)"
role: "Determinism contract"
status: "ACTIVE"
---

# D. Детерминизм (backend contract)

## 1) Принцип
Одинаковый входной снимок (RawSnapshot) при одинаковой версии адаптера и нормализатора
должен давать **бит-в-бит одинаковый** CanonicalGraph и одинаковые хэши.

## 2) Канонический порядок

### 2.1 Nodes
Сортировать по:
1) `id` (лексикографически, Unicode code point order)
2) если равны — запрещено (ID обязан быть уникальным)

### 2.2 Edges
Сортировать по tuple:
1) `source`
2) `target`
3) `kind`
4) `id`

## 3) Каноническая сериализация JSON

Требования:
- объектные ключи сериализуются в **лексикографическом порядке**
- числа сериализуются без лишних нулей и экспонент, где возможно (JS JSON стандарт допускает, но мы фиксируем формат на уровне реализации)
- даты только ISO8601 строкой
- запрещены поля, зависящие от времени выполнения (random ids, UI coords, etc.)

Результат сериализации называется `canonicalJson`.

## 4) Хэширование
- `hashAlgo = sha256`
- `contentHash = sha256(canonicalJson)`
- `resultHash = sha256(canonicalResultJson)`

## 5) Нормализация unknown/missing
- отсутствует внешний ID у объекта источника → объект отбрасывается + запись в errors/ledger
- отсутствует name при наличии внешнего ID → name = "<unknown>" + запись об ошибке

## 6) Запреты
- нельзя использовать счётчики в рантайме для генерации ID
- нельзя включать нестабильные поля в attrs (например timestamp “now”)
