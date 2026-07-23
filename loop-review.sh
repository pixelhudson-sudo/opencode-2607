#!/usr/bin/env bash
set -euo pipefail

while true; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] loop-review: starting run" | tee -a loop.log
  opencode run --command review 2>&1 | tee -a loop.log
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] loop-review: sleeping 60s" | tee -a loop.log
  sleep 60
done
