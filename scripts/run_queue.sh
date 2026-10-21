#!/usr/bin/env bash
# Usage: scripts/run_queue.sh <queue_file> [parallel=2]
# queue line: <run_id> <seed> <niterations> <timeout_s> <procs> [descriptors...]
# Runs fits P-way parallel (stopping if STOP exists), scores each under a lock (ledger/results.csv is shared).
cd "$(dirname "$0")/.."
run_one() {
  rid=$1; seed=$2; nit=$3; to=$4; procs=$5; shift 5
  [ -e STOP ] && { echo "STOP present, skipping $rid"; exit 0; }
  [ "$(date +%H%M)" \> "0600" ] && [ "$(date +%H%M)" \< "1200" ] && { echo "past 06:00, skipping $rid"; exit 0; }
  mkdir -p ledger/logs
  if [ $# -gt 0 ]; then D="--descriptors $*"; else D=""; fi
  uv run python sr/run_pysr.py $D --run-id "$rid" --seed "$seed" --niterations "$nit" --timeout "$to" --procs "$procs" > "ledger/logs/$rid.log" 2>&1 || { echo "FIT FAILED $rid"; exit 0; }
  while ! mkdir ledger/.score.lock 2>/dev/null; do sleep 2; done
  uv run python eval/score.py --run "$rid" > "ledger/logs/$rid.score.log" 2>&1 || echo "SCORE FAILED $rid"
  rmdir ledger/.score.lock
  echo "done $rid"
}
export -f run_one
grep -v '^#' "$1" | grep . | xargs -P "${2:-2}" -L 1 bash -c 'run_one "$@"' _
