#!/usr/bin/env bash
set -euo pipefail

while true; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] loop-build: starting run" | tee -a loop.log
  opencode run --command build 2>&1 | tee -a loop.log
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] loop-build: sleeping 60s" | tee -a loop.log
  sleep 60
done
