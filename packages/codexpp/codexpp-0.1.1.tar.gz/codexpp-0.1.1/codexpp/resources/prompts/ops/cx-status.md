---
title: Operational Status Briefing
description: Sistem durumu, performans metrikleri ve operasyonel riskler için kapsamlı durum raporu hazırlar.
argument_hint: SCOPE=<servis/modül kapsamı> [METRICS="dashboard linkleri veya metrik özetleri"]
persona: system-architect
---

You are Codex compiling an operational status briefing.

Create a comprehensive status report:

## 1. Current Health Status
- Overall system health (healthy/degraded/down)
- Service availability and uptime metrics
- Recent deployment status
- Infrastructure health (servers, databases, networks)

## 2. Key Performance Metrics
- Response times and latency trends
- Throughput and request rates
- Error rates and failure patterns
- Resource utilization (CPU, memory, disk, network)
- Business metrics (if applicable)

## 3. Outstanding Incidents
- Active incidents and their severity
- Incident resolution progress
- Known issues or workarounds
- Scheduled maintenance or planned changes

## 4. Risk Assessment
- Performance degradation trends
- Capacity concerns or scaling needs
- Security vulnerabilities or threats
- Technical debt or maintenance backlog
- Dependency risks or external service issues

## 5. Recommended Actions
- Immediate actions to address critical issues
- Short-term improvements or optimizations
- Long-term strategic recommendations
- Monitoring or alerting enhancements
- Team priorities and focus areas

**Service scope:** $SCOPE
**Latest metrics:** $METRICS

Provide a clear, actionable status report that helps stakeholders understand system health and prioritize operational improvements.

