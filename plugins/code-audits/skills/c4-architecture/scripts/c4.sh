#!/usr/bin/env bash
#
# Validate, inspect and export a Structurizr DSL workspace, without Docker.
# Requires the `structurizr` Homebrew formula (pulls openjdk).
#
# Usage:
#   c4.sh check   <workspace.dsl>                 validate + inspect
#   c4.sh export  <workspace.dsl> [format] [out]  export (default: static -> <dir>/site)
#
# Exit codes: 0 ok, 1 invalid DSL or export failure, 2 inspector findings,
#             3 structurizr not installed, 4 tool error (Java, crash), 5 unsafe output dir.

set -uo pipefail

ACTION="${1:-}"
WORKSPACE="${2:-}"
MARKER=".c4-export"

if [[ -z "$ACTION" || -z "$WORKSPACE" ]]; then
    echo "Usage: c4.sh check|export <workspace.dsl> [format] [output-dir]" >&2
    exit 1
fi

if [[ ! -f "$WORKSPACE" ]]; then
    echo "Workspace not found: $WORKSPACE" >&2
    exit 1
fi

if ! command -v structurizr >/dev/null 2>&1; then
    echo "structurizr is not installed. Install it with: brew install structurizr (or put a structurizr wrapper running java -jar structurizr-<version>.war on PATH)" >&2
    exit 3
fi

# `command grep` bypasses aliases and shell wrappers that rewrite grep output.
cgrep() {
    command grep "$@"
}

LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

tool_error() {
    echo "TOOL ERROR (not a DSL problem)"
    tail -n 15 "$LOG"
    exit 4
}

abs_dir() {
    (cd "$1" 2>/dev/null && pwd -P)
}

case "$ACTION" in
    check)
        if ! structurizr validate -w "$WORKSPACE" >"$LOG" 2>&1; then
            # No parser error line means Java or the tool itself failed.
            cgrep -q 'ERROR' "$LOG" || tool_error
            echo "INVALID"
            cgrep 'ERROR' "$LOG" | sed 's/.*ERROR [^ ]* -- //' | cgrep -v -e '^[[:space:]]*at '
            exit 1
        fi
        echo "VALID"
        # The inspector's exit code counts ignored findings too: parse its lines instead.
        structurizr inspect -w "$WORKSPACE" >"$LOG" 2>&1
        if cgrep -q -e 'Exception' -e 'command\.InspectCommand -- ' "$LOG"; then
            tool_error
        fi
        FINDINGS="$(cgrep -E '^(ERROR|WARNING|INFO) +\|' "$LOG" || true)"
        if [[ -n "$FINDINGS" ]]; then
            echo "INSPECTION"
            echo "$FINDINGS"
            exit 2
        fi
        echo "INSPECTION OK"
        ;;
    export)
        FORMAT="${3:-static}"
        case "$FORMAT" in
            static|mermaid|plantuml|plantuml/structurizr|plantuml/c4plantuml|json) ;;
            *)
                echo "Unsupported format: $FORMAT (static, mermaid, plantuml, plantuml/structurizr, plantuml/c4plantuml, json)" >&2
                exit 1
                ;;
        esac
        DEFAULT_OUT="$(dirname "$WORKSPACE")/site"
        [[ "$FORMAT" != static ]] && DEFAULT_OUT="$(dirname "$WORKSPACE")/diagrams"
        OUT="${4:-$DEFAULT_OUT}"

        # Never wipe a directory that contains the workspace, a home, a git root or tracked files.
        WS_DIR="$(abs_dir "$(dirname "$WORKSPACE")")"
        if [[ -d "$OUT" ]]; then
            OUT_ABS="$(abs_dir "$OUT")"
            case "$WS_DIR/" in
                "$OUT_ABS"/*)
                    echo "Output directory contains the workspace: $OUT" >&2
                    exit 5
                    ;;
            esac
            if [[ "$OUT_ABS" == "/" || "$OUT_ABS" == "$HOME" ]] \
                || [[ "$(git -C "$OUT_ABS" rev-parse --show-toplevel 2>/dev/null)" == "$OUT_ABS" ]] \
                || [[ -n "$(git -C "$OUT_ABS" ls-files 2>/dev/null | head -n 1)" ]]; then
                echo "Refusing to overwrite: $OUT" >&2
                exit 5
            fi
            if [[ -n "$(ls -A "$OUT")" ]]; then
                # Only a directory written by this script carries the marker.
                if [[ ! -f "$OUT/$MARKER" ]]; then
                    echo "Output directory is not empty and is not a previous export: $OUT" >&2
                    exit 5
                fi
                rm -rf "$OUT"
            fi
        fi
        mkdir -p "$OUT"
        if ! structurizr export -w "$WORKSPACE" -f "$FORMAT" -o "$OUT" >"$LOG" 2>&1; then
            cgrep -q 'ERROR' "$LOG" || tool_error
            echo "EXPORT FAILED"
            cgrep 'ERROR' "$LOG" | cgrep -v -e '^[[:space:]]*at '
            exit 1
        fi
        echo "$FORMAT" >"$OUT/$MARKER"
        MSG="EXPORTED $FORMAT -> $OUT"
        if [[ "$FORMAT" == static ]]; then
            MSG+=$'\n'"Open: file://$(abs_dir "$OUT")/index.html"
        fi
        # One write: a reader that closes early (`| head -n 1`) must not cause a broken pipe.
        printf '%s\n' "$MSG" 2>/dev/null || true
        ;;
    *)
        echo "Unknown action: $ACTION (expected check or export)" >&2
        exit 1
        ;;
esac
exit 0
