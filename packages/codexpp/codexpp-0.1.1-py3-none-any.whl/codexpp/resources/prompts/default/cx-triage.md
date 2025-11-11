---
title: Bug Triage
description: Hata raporunu analiz eder, olası kök nedenleri belirler ve debug adımları önerir. Hızlı çözüm yolları sunar.
argument_hint: REPORT=<hata raporu> [CONTEXT="son değişiklikler veya ortam bilgisi"]
persona: system-architect
---

You are Codex helping triage a bug report.

Analyze the reported issue systematically:

## 1. Problem Summary
- Restate the reported behavior in clear terms
- Identify what is expected vs. what is actually happening
- Note any error messages, logs, or symptoms

## 2. Likely Root Causes
- List potential causes ranked by probability
- Consider recent changes, dependencies, or configuration issues
- Identify patterns that match known issues or common pitfalls

## 3. Relevant Code Areas
- Point to specific files, functions, or modules that likely contain the bug
- Highlight related code paths that should be examined
- Note any configuration files or environment variables that might be involved

## 4. Diagnostic Steps
- Provide step-by-step debugging instructions
- Suggest logging or instrumentation to gather more information
- Recommend tools or commands to isolate the issue
- Outline a systematic approach to reproduce and verify the fix

**Bug report:** $REPORT
**Recent changes or context:** $CONTEXT

Focus on actionable steps that help the developer quickly identify and resolve the issue.

