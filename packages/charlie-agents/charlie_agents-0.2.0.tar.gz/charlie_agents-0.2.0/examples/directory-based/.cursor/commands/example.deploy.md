---
description: Deploy application to specified environment
allowed-tools:
- Bash(docker:*)
- Bash(kubectl:*)
- Bash(helm:*)
tags:
- deployment
- production
category: operations
---

## Deployment Request

$ARGUMENTS

## Safety Checks

Before deploying:
1. Verify target environment
2. Check for breaking changes
3. Ensure tests pass

## Execute Deployment

Run: scripts/deploy.sh