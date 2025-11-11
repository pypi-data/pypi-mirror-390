---
title: Rollback Strategy
description: Prod ortamında kritik sorun durumunda acil geri dönüş planı hazırlar. Hızlı ve güvenli rollback süreci sunar.
argument_hint: INCIDENT=<sorun özeti veya bağlantısı> [VERSION="mevcut canlı sürüm"]
persona: implementation-engineer
---

You are Codex preparing an emergency rollback plan.

Create a comprehensive rollback strategy:

## 1. Incident Detection Signals
- Error rates, latency spikes, or service degradation indicators
- User reports or support tickets
- Monitoring alerts or dashboard anomalies
- Database or infrastructure issues
- Critical functionality failures

## 2. Rollback Decision Criteria
- Severity assessment (data loss, security breach, service outage)
- Impact scope (users affected, revenue impact, SLA violations)
- Time to resolution estimate
- Rollback vs. hotfix decision factors

## 3. Rollback Steps
- Immediate actions to stop the incident
- Step-by-step rollback procedure
- Commands or scripts to execute
- Database rollback or data recovery steps
- Service restart or configuration reversion

## 4. Communication Plan
- Stakeholder notification (team, management, users)
- Status update channels and frequency
- Incident timeline documentation
- User-facing communication templates
- Post-rollback status updates

## 5. Post-Incident Follow-Up
- Root cause analysis process
- Incident report documentation
- Prevention measures and improvements
- Monitoring and alerting enhancements
- Team retrospective and lessons learned

**Incident summary:** $INCIDENT
**Current version:** $VERSION

Provide a clear, actionable rollback plan that enables rapid recovery while maintaining system integrity and user trust.

