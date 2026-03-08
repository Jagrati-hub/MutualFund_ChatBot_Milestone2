# Phase 4: Orchestration & Scheduling

## Purpose
Background job scheduling that runs the daily scrape → ingest pipeline automatically.

## Files in This Phase

### Core Module
- `src/scheduler.py` - APScheduler orchestration

### Shared Utilities
- `src/shared.py` - Shared utilities and constants

## Key Responsibilities
1. Maintain single APScheduler instance
2. Define `run_pipeline_once()` function
3. Schedule daily job (24-hour interval)
4. Ensure idempotent scheduler startup
5. Handle job registration and execution

## Functions
- `start_scheduler_once()` - Idempotent scheduler startup
- `run_pipeline_once()` - Execute scrape → ingest pipeline
- `schedule_daily_job()` - Register daily job

## Features
✅ Idempotent - Safe to call multiple times
✅ Background - Runs without blocking UI
✅ Configurable - 24-hour interval (customizable)
✅ Reliable - Handles errors gracefully

## Status
✅ Complete - Scheduler fully functional and tested
