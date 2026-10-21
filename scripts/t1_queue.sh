#!/usr/bin/env bash
# Usage: scripts/t1_queue.sh <queue_file> [parallel=3]
# queue line: <run_id> <seed> <target> [descriptors...]
# Fits only (no score.py: ledger/results.csv is agent-machine-only). Score with eval/compose_hv.py.
# Fixed settings for every T1 B/k-route arm: L1 loss, --units, niter 22000, maxsize 15, procs 4, 900 s.
cd "$(dirname "$0")/.."
PY="${PY:-$HOME/code/OSI-Hackathon-2026/.venv/bin/python}"
run_one() {
  rid=$1; seed=$2; tgt=$3; shift 3
  [ -e STOP ] && { echo "STOP present, skipping $rid"; exit 0; }
  [ -e "ledger/runs/$rid.csv" ] && { echo "exists, skipping $rid"; exit 0; }
  mkdir -p ledger/logs
  if [ $# -gt 0 ]; then D="--descriptors $*"; else D=""; fi
  "$PY" sr/run_pysr.py $D --run-id "$rid" --seed "$seed" --target "$tgt" --loss L1 --units \
    --niterations 22000 --timeout 900 --procs 4 > "ledger/logs/$rid.log" 2>&1 || { echo "FIT FAILED $rid"; exit 0; }
  echo "$(date +%H:%M) done $rid"
}
export -f run_one
export PY
grep -v '^#' "$1" | grep . | xargs -P "${2:-3}" -L 1 bash -c 'run_one "$@"' _
