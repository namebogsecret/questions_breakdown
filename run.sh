#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run-$(date +'%Y%m%d_%H%M%S').log"
touch "$LOG_FILE"

QUIET=0
NO_COLOR=0
PORT=8000

for arg in "$@"; do
  case $arg in
    --quiet) QUIET=1 ;;
    --no-color) NO_COLOR=1 ;;
    --port=*) PORT="${arg#*=}" ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

log() {
  local lvl="$1" step="$2" msg="$3"
  local ts="$(date '+%F %T%z')"
  local color="" reset=""
  if [[ $NO_COLOR -eq 0 ]]; then
    case "$lvl" in
      INFO) color="\e[32m";;
      WARN) color="\e[33m";;
      ERROR) color="\e[31m";;
    esac
    reset="\e[0m"
  fi
  local line="$ts [$lvl] $step – $msg"
  if [[ $QUIET -eq 1 && $lvl == INFO ]]; then
    echo -ne "" # drop INFO when quiet
  else
    printf "%b%s%b\n" "$color" "$line" "$reset" | tee -a "$LOG_FILE"
  fi
}

run_cmd() {
  local step="$1"; shift
  local cmd="$*"
  log INFO "$step" "$cmd"
  bash -c "$cmd" 2>&1 | tee -a "$LOG_FILE"
  local status=${PIPESTATUS[0]}
  if [[ $status -ne 0 ]]; then
    log ERROR "$step" "Exit code $status; see above for stderr"
    exit $status
  fi
}

trap 'log ERROR main "Aborted (signal)"; exit 2' INT TERM

# 1. Git pull
run_cmd git "git pull --ff-only" || {
  log ERROR git "git pull failed"; exit 1; }

# 2. Dependencies
if [[ -f requirements.txt ]]; then
  run_cmd deps "python -m pip install -r requirements.txt"
elif [[ -f package.json ]]; then
  run_cmd deps "npm ci --ignore-scripts"
else
  log INFO deps "no dependency files"
fi

# 3. Start
STARTED=0
if [[ -f start.sh ]]; then
  run_cmd start "bash start.sh" && STARTED=1
elif [[ -f package.json && $(grep -q '"start"' package.json && echo 1) ]]; then
  run_cmd start "npm start" && STARTED=1
elif [[ -f main.py ]]; then
  run_cmd start "python main.py" && STARTED=1
elif [[ -f index.html ]]; then
  if lsof -i tcp:$PORT >/dev/null 2>&1; then
    log WARN start "port $PORT busy; attempting to free"
    lsof -ti tcp:$PORT | xargs -r kill || {
      log ERROR start "cannot free port $PORT"; exit 1; }
  fi
  run_cmd start "python -m http.server $PORT" && STARTED=1
else
  log ERROR start "No start command found"; exit 1
fi

if [[ $STARTED -eq 1 ]]; then
  log INFO main "✓ SUCCESS"
else
  log ERROR main "✗ FAILED"; exit 1
fi
