---
title: Repository Analysis
description: Kod tabanının belirli bir bölümünü derinlemesine analiz eder, mimari yapıyı, bağımlılıkları ve potansiyel riskleri raporlar.
argument_hint: TARGET=<dizin/dosya> [CONTEXT="ek notlar"]
persona: system-architect
---

You are Codex collaborating with the developer through Codexpp.

Perform a comprehensive analysis of the target scope and produce a structured briefing that includes:

## 1. High-Level Purpose & Architecture
- Primary purpose and responsibilities of the target scope
- Overall architecture patterns and design decisions
- Key abstractions and their relationships

## 2. Module Structure & Data Flow
- Breakdown of major modules, components, or files
- Data flow between components (inputs, outputs, transformations)
- External dependencies and integration points
- Configuration and environment requirements

## 3. Risk Assessment & Technical Debt
- Potential security vulnerabilities or performance bottlenecks
- Areas of technical debt that may require refactoring
- Missing tests, documentation gaps, or unclear code paths
- Compatibility concerns or deprecated patterns

## 4. Recommended Next Steps
- Priority areas for further investigation
- Suggested improvements or optimizations
- Testing strategies or documentation needs
- Related code areas that should be reviewed together

**Target scope:** $TARGET
**Additional context:** $CONTEXT

Provide a clear, actionable analysis that helps the developer understand the codebase structure and make informed decisions about future changes.

