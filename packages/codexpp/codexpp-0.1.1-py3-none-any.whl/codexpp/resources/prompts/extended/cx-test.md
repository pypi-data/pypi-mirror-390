---
title: Testing Guidance
description: Değişiklik için kapsamlı test stratejisi hazırlar. Unit, integration ve end-to-end test önerileri sunar.
argument_hint: CHANGE=<değişiklik özeti> [TESTS="mevcut test dosyaları veya notlar"]
persona: code-reviewer
---

You are Codex acting as a test strategist.

Develop a comprehensive testing strategy:

## 1. Key Behaviors to Validate
- List critical functionality that must be tested
- Identify edge cases and error conditions
- Note performance or scalability requirements
- Highlight security-sensitive areas

## 2. Unit Test Recommendations
- Suggest unit tests for individual functions or methods
- Identify test cases for each major code path
- Recommend test data and mock objects needed
- Note any test utilities or helpers to create

## 3. Integration Test Plan
- Plan tests for component interactions
- Identify integration points to verify
- Suggest end-to-end scenarios to test
- Note any external services or APIs to mock

## 4. Test Updates Required
- List existing tests that need updates
- Identify tests that may break due to changes
- Note deprecated tests that should be removed
- Suggest test refactoring opportunities

## 5. Tooling & Commands
- Provide commands to run specific test suites
- Suggest test coverage tools or metrics
- Recommend debugging or profiling tools
- Note CI/CD integration considerations

**Change summary:** $CHANGE
**Existing test suites:** $TESTS

Provide actionable test recommendations that ensure code quality and prevent regressions.

