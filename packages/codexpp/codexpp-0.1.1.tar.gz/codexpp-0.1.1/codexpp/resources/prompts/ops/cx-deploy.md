---
title: Deployment Plan
description: Yeni sürüm dağıtımını güvenli ve sistematik şekilde planlar. Ön kontroller, adımlar ve rollback stratejisi içerir.
argument_hint: NOTES=<sürüm notları veya değişiklik özeti> ENVIRONMENT=<staging/production>
persona: implementation-engineer
---

You are Codex coordinating a deployment.

Create a comprehensive deployment plan:

## 1. Pre-Deployment Checks
- Verify all tests pass (unit, integration, e2e)
- Check database migration status and compatibility
- Confirm environment variables and configuration are set
- Validate dependencies and service health
- Review recent changes and potential conflicts

## 2. Deployment Steps
- Provide step-by-step deployment instructions
- List commands or scripts to execute
- Note any manual steps or approvals required
- Identify deployment order for multi-service systems
- Include database migration steps if applicable

## 3. Verification Commands
- Commands to verify successful deployment
- Health check endpoints or status commands
- Smoke tests to validate critical functionality
- Log monitoring and error detection steps
- Performance baseline checks

## 4. Rollback Preparation
- Document rollback procedure and triggers
- List previous stable version or backup locations
- Provide rollback commands or scripts
- Note data consistency considerations
- Identify rollback time estimates

**Release notes:** $NOTES
**Target environment:** $ENVIRONMENT

Provide a safe, repeatable deployment process that minimizes risk and enables quick recovery if issues arise.

