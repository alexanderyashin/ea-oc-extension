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

## 0) Источник: что считаем истинной единицей данных

В LeanIX основной объект — **Fact Sheet** и связи между ними (**Relations**). :contentReference[oaicite:0]{index=0}  
В MVP мы извлекаем:
- Application Fact Sheets
- Interface Fact Sheets (если доступны)
- Relations между ними (и/или Application↔Application зависимости)

LeanIX предоставляет API и документацию по аутентификации (через Technical Users / access token). :contentReference[oaicite:1]{index=1}  
Работа с relations описана через операции/мутации (в частности update/patch в их API). :contentReference[oaicite:2]{index=2}

> Важно: ingestion — это **только извлечение + нормализация**. Никакой интерпретации.

---

## 1) Контракт: RawSnapshot (до нормализации)

RawSnapshot фиксирует “что мы видели в LeanIX”:

- `meta`
  - `sourceSystem = "leanix"`
  - `workspace` (string)
  - `capturedAt` (ISO8601)
  - `connectorVersion`
  - `queries[]` (список запросов/эндпойнтов)
- `factsheets[]` (сырой массив объектов)
- `relations[]` (сырой массив отношений)
- `errors[]` (мягкие ошибки: missing fields, partial reads)
- `rawHash` (хэш сырого контента)

RawSnapshot хранится как артефакт воспроизводимости (опционально для MVP, но рекомендовано).

---

## 2) Маппинг LeanIX → CanonicalGraph

### 2.1 Fact Sheet → Node

**Application Fact Sheet → Node(kind="application")**
- `id`: `application:leanix:<workspace>:<factSheetId>`
- attrs:
  - `name`: Fact Sheet name
  - `externalId`: factSheetId
  - `lifecycle`/`criticality`/`owner`/`tags`: только если доступны в фактах

**Interface Fact Sheet → Node(kind="interface")**
- `id`: `interface:leanix:<workspace>:<factSheetId>`
- attrs:
  - `name`
  - `category` (если поле существует; в LeanIX встречается обсуждение категорий интерфейсов) :contentReference[oaicite:3]{index=3}
  - `externalId`

Provenance:
- `sourceObjectType = "FactSheet"`
- `sourceObjectId = factSheetId`

### 2.2 Relations → Edge

В LeanIX есть семантические relation types (например Requires/Required By и др.). :contentReference[oaicite:4]{index=4}  
Мы не навязываем смысл глубже MVP: переносим relation type как `relationType` и выбираем Canonical `kind` по правилам ниже.

#### Правила выбора edge kind (MVP)

1) Application → Application:
- если relationType соответствует “requires/depends” (или workspace-эквивалент) → `depends_on`

2) Application ↔ Interface:
- если relation описывает “provider/exposes” → `exposes_interface`
- если relation описывает “consumer/uses” → `consumes_interface`

3) Иначе:
- relation остаётся **неиспользованной в MVP** (но может быть сохранена в RawSnapshot для будущего Full scope)

Edge fields:
- `id`: `edge:<kind>:leanix:<workspace>:<relationId>` (если relationId доступен)
- `source`, `target`: по mapped node ids
- attrs:
  - `relationType`: исходный тип
  - `externalId`: relationId
  - дополнительные поля — только как факты (например strength), если LeanIX предоставляет

Provenance:
- `sourceObjectType = "Relation"`
- `sourceObjectId = relationId`

---

## 3) Технические принципы адаптера (MVP)

### 3.1 Аутентификация

LeanIX рекомендует технических пользователей и токены доступа для API-запросов. :contentReference[oaicite:5]{index=5}  
В спецификации ingestion:
- секреты не пишутся в repo
- конфиг через env (например `LEANIX_API_TOKEN`, `LEANIX_WORKSPACE`)
- логирование без утечек секретов

### 3.2 Детерминизм

- все выгрузки приводятся к стабильному порядку
- id вычисляются строго по правилам
- `contentHash` считается после нормализации (см. A-док)

### 3.3 Политика unknown/missing

Если не найден обязательный минимум:
- нет `factSheetId` → объект отбрасывается, пишется ошибка в `errors[]`
- есть id, но нет name → допускается, но `name=""` запрещён; ставим `name` как `<unknown>` и фиксируем в errors

---

## 4) MVP-граница ingestion (явно)

MVP ingestion **не делает**:
- загрузку/выгрузку обратно в LeanIX (никаких update/patch в MVP)
  - хотя LeanIX описывает механизмы изменения relations, это не требуется для нашего MVP :contentReference[oaicite:6]{index=6}
- интерпретацию lifecycle/technology/business capability
- правки метамодели, кастомные типы, meta-model configuration

---

## 5) Точки расширения (для Full Product)

- Meta-model introspection (чтение типов, кастомных relation types, subtype management)
- Permissions, user/group mapping
- Import/export processors через Integration REST API (вне MVP) :contentReference[oaicite:7]{index=7}

