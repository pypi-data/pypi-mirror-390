---
title: Refactoring Plan
description: Belirli bir modül için kapsamlı refaktör planı hazırlar. Adım adım yaklaşım ve test stratejisi sunar.
argument_hint: NOTES=<mevcut kod veya sorunlar> [GOALS="hedefler ve kısıtlar"]
persona: implementation-engineer
---

You are Codex designing a refactor.

Create a comprehensive refactoring plan:

## 1. Current State Analysis
- Identify pain points, code smells, or architectural issues
- Document current dependencies and coupling
- Note any technical debt or maintenance challenges

## 2. Refactoring Goals
- Define clear objectives (improve testability, reduce complexity, enhance maintainability)
- Establish success criteria and metrics
- Consider constraints (backward compatibility, performance, migration effort)

## 3. Step-by-Step Refactoring Tasks
- Break down the refactor into small, incremental steps
- Order tasks to minimize risk and maintain functionality
- Identify safe refactoring opportunities first (extract method, rename, etc.)
- Plan for more complex changes (extract class, move functionality, etc.)

## 4. Affected Files & Dependencies
- List all files that will be modified
- Identify dependent code that may need updates
- Note any external dependencies or interfaces that might change

## 5. Testing Strategy
- Plan unit tests for refactored components
- Identify integration tests that need updates
- Suggest regression testing approaches
- Consider test-driven refactoring where applicable

**Current implementation notes:** $NOTES
**Goals and constraints:** $GOALS

Provide a safe, incremental refactoring plan that maintains functionality while improving code quality.

