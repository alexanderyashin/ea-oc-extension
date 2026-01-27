---
title: "C. MVP vs Full Product Scope"
purpose: "Зафиксировать границу: что делаем сейчас (MVP) и что строго позже"
audience: ["Core dev", "Stakeholders", "Engine dev"]
language: "RU"
evidence_profile: "Scope contract"
role: "Scope boundary spec"
status: "ACTIVE"
---

# C. Граница MVP vs Full Product

## 0) Принцип

MVP делает **минимально достаточный** слой:
- чтобы ingest'ить реальную систему (LeanIX)
- привести к CanonicalGraph
- подать в существующий deterministic ESTRA-compatible engine

MVP **не** превращает систему в BI/дашборд/советчика.

---

## 1) MVP (Phase 1): что входит

### 1.1 Ingestion (LeanIX → CanonicalGraph)
- Application Fact Sheets → `application` nodes
- Interface Fact Sheets → `interface` nodes (если доступны)
- Relations → edges:
  - `depends_on`
  - `exposes_interface`
  - `consumes_interface`
- Provenance на каждом узле/ребре
- Детерминированная нормализация (stable sort + stable hash)
- RawSnapshot (опционально, но рекомендовано как артефакт воспроизводимости)

### 1.2 Контракт для симуляции
- SimulationInput = CanonicalGraph + scenario params (без UI)
- SimulationResult = stop/lock + ledger + states (без рекомендаций)

### 1.3 Явные запреты MVP
- нет рекомендаций
- нет “оптимизации портфеля”
- нет оценок зрелости, KPI
- нет экспорта отчётов в PDF/PowerPoint (вообще)
- нет write-back в LeanIX

---

## 2) Full Product (Phase 2+): что позже

### 2.1 Модель (расширение онтологии)
- Business Capabilities
- Business Processes / Value Streams
- Org Units / User Groups / Ownership структурно
- Tech Components / Platforms / Data Objects
- Environments (prod/non-prod), deployment topology
- События/инциденты/изменения как отдельные сущности (если понадобится)

### 2.2 Ingestion (мульти-источники)
- ServiceNow (CMDB, incidents)
- GitHub (repos, dependencies), CI/CD
- Cloud providers (accounts, services, connectivity)
- Финансы/бюджеты (только как факты)

### 2.3 Engine / Simulation
- более сложные сценарии (мульти-шоки, временные окна, неоднородные пороги)
- калибровка параметров на внешних данных
- расширенная ledger-формализация (но всё ещё без рекомендаций)

### 2.4 Контроль доступа / безопасность
- RBAC на уровне ingestion-конфигов и артефактов
- аудит логов
- redaction персональных данных

---

## 3) Граница “инструмент vs демонстратор” (на будущее)

Даже Full Product **не** становится BI-консалтинг-роботом.
Строгая линия:
- можно: показывать структуру, пороги, факты, следствия в смысле модели
- нельзя: говорить “сократите X”, “увеличьте Y”, “нанять людей”, “поменяйте оргструктуру”

Любая формулировка, похожая на рекомендацию, — out of scope.

