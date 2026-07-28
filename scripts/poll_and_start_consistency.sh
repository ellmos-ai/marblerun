#!/bin/bash
# poll_and_start_consistency.sh
# Wartet bis review-only Chain fertig ist, startet dann Konsistenz-Check Opus
# Laeuft im Hintergrund: bash poll_and_start_consistency.sh &

# Set LLMAUTO_DIR to your checkout, or export it before running.
LLMAUTO_DIR="${LLMAUTO_DIR:-$HOME/llmauto}"
PROMPT_FILE="$LLMAUTO_DIR/llmauto/prompts/cfm_cross_reference_check.txt"
POLL_INTERVAL=60  # Sekunden
LOG_FILE="$LLMAUTO_DIR/llmauto/logs/poll_consistency.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Polling gestartet: Warte auf review-only COMPLETED ==="

while true; do
    STATUS=$(cd "$LLMAUTO_DIR" && PYTHONIOENCODING=utf-8 python -m llmauto chain status review-only 2>&1 | grep "Status:" | head -1 | awk '{print $NF}')

    if [ "$STATUS" = "COMPLETED" ]; then
        log "review-only Chain COMPLETED! Starte Konsistenz-Check Opus..."
        break
    elif [ "$STATUS" = "STOPPED" ] || [ "$STATUS" = "FAILED" ]; then
        log "review-only Chain $STATUS -- Konsistenz-Check wird NICHT gestartet."
        exit 1
    fi

    log "Status: $STATUS -- warte ${POLL_INTERVAL}s..."
    sleep $POLL_INTERVAL
done

# Prompt lesen
PROMPT=$(cat "$PROMPT_FILE")

# Claude Opus starten mit dem Konsistenz-Check Prompt
log "Starte claude --model claude-opus-4-6 ..."
# Directory the consistency check should run in. Override via WORK_DIR.
cd "${WORK_DIR:-$HOME/papers}"

claude --model claude-opus-4-6 \
    --permission-mode dontAsk \
    --output-format text \
    -p "$PROMPT" \
    >> "$LLMAUTO_DIR/llmauto/logs/cfm_consistency_check.log" 2>&1

EXIT_CODE=$?
log "Konsistenz-Check beendet (exit=$EXIT_CODE). Log: logs/cfm_consistency_check.log"
