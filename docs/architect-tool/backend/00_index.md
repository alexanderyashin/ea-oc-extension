---
title: "Architect Tool Backend — Index"
purpose: "Навигация по backend-ядру (модель, ingestion, границы MVP)"
audience: ["Core dev", "Connector dev", "Simulation dev"]
language: "RU"
evidence_profile: "Design-spec (no runtime claims)"
role: "Backend documentation root"
status: "ACTIVE"
---

# Backend ядро Architect Tool — Index

Этот раздел фиксирует **headless backend**: каноническая модель, ingestion-адаптеры, и контракт данных до симуляции.
UI здесь **не предполагается**.

## Документы

1. **A. Каноническая модель**
   - `A_canonical-model.md`
   - Что такое Canonical Graph, какие узлы/рёбра, какие атрибуты, какие инварианты детерминизма.

2. **B. Ingestion: SAP LeanIX (MVP)**
   - `B_ingestion-leanix.md`
   - Как маппим LeanIX Fact Sheets/Relations в Canonical Graph. Как обеспечиваем стабильные id, версионирование снапшотов, ошибки/пропуски.

3. **C. Граница MVP vs Full Product**
   - `C_mvp-vs-full-scope.md`
   - Что считаем в MVP (Applications/Interfaces/Dependencies) и что строго откладываем.

## Непереговорные ограничения (backend)

- Headless & embeddable (модуль/библиотека; без UI-предположений)
- Никакого BI: не строим «дашборды истин»
- Никаких рекомендаций/советов/оптимизаций (backend не говорит “делайте так”)
- Детерминизм: одинаковый вход → одинаковый выход
- Совместимость с существующим ESTRA/engine принципом: **ledger + STOP/LOCK** как факт, не как совет

## Контракт потока данных (кратко)

**Ingestion → Canonical Model → Simulation Input**

- Ingestion читает внешний источник (LeanIX), выдаёт **RawSnapshot**.
- Normalizer приводит RawSnapshot к **CanonicalGraph**.
- Simulation принимает **SimulationInput** (проекция CanonicalGraph + параметры сценария) и выдаёт **SimulationResult** (с ledger).

Детали: см. `A_canonical-model.md` и `B_ingestion-leanix.md`.
