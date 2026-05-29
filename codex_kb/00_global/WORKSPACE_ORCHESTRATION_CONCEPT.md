# Workspace Orchestration Concept

Дата: 2026-05-29

This document defines the minimal orchestration standard for E:\Codex_Work.

## Core principles

- Project memory lives in files (not in chat).
- Orchestrator is a dispatcher of task contracts, boundaries and verification.
- Completion event ≠ acceptance: acceptance requires evidence (verify outputs + updated handoff).
- Handoff must be compact; history goes to staged artifacts.
- Streams table is required only for **medium/complex** tasks.

## Manual fallback for subagents

If the environment does not support **visible subagents**, replace subagents with **manual decomposition** into independent steps, each with its own verification, **without nested agents**.

## Standard file formats

- Use .codex/orchestrator.toml (TOML only; do not use yaml/json).

## GitHub sync (required stage)

After normalizing the pilot project and updating registry/docs, perform GitHub sync using E:\Codex_Work\_workspace_docs\GITHUB_SYNC_CHECKLIST.md.

## Explicitly not implemented in v1

- ~/.agents/skills
- template-router
- automatic external template fetching

These may be considered as a future extension.