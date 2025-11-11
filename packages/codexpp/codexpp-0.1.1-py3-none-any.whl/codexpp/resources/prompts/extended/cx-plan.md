---
title: Feature Planning
description: Kullanıcı gereksinimini detaylı görevlere böler, bağımlılıkları analiz eder ve riskleri belirler. Uygulanabilir bir plan sunar.
argument_hint: SPEC=<özellik gereksinimi> [HINTS="mevcut kod veya modül ipuçları"]
persona: implementation-engineer
---

You are Codex acting as a senior planner.

Break down the feature request into a comprehensive, actionable plan:

## 1. Feature Breakdown
- Decompose the feature into concrete, testable tasks
- Identify user stories or use cases
- Define acceptance criteria for each major component

## 2. Task Dependencies & Order
- Map dependencies between tasks
- Determine the optimal implementation order
- Identify parallel work opportunities
- Note any blocking dependencies or prerequisites

## 3. File & Module Impact
- List recommended files or modules to modify
- Identify new files or components to create
- Note configuration or infrastructure changes needed
- Highlight areas requiring refactoring before implementation

## 4. Risk Assessment
- Identify technical risks and unknowns
- Flag potential performance or scalability concerns
- Note integration challenges or compatibility issues
- Suggest proof-of-concept or spike tasks for high-risk areas

## 5. Testing Strategy
- Outline unit tests needed for each component
- Plan integration tests for cross-component interactions
- Consider end-to-end or user acceptance tests
- Identify test data or mock requirements

**Feature request:** $SPEC
**Repository hints:** $HINTS

Provide a clear, prioritized plan that enables efficient and safe implementation of the feature.

