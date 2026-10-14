
#!/usr/bin/env bash

set -euo pipefail

show_help() {
    echo "Usage: $0 <directory> <ERROR|WARN> [--top N]"
}

if [[ $# -lt 2 ]]; then
    show_help
    exit 1
fi

directory="$1"
level="$2"
top=""

if [[ ! -d "$directory" ]]; then
    echo "Error: directory '$directory' does not exist." >&2
    exit 1
fi

if [[ "$level" != "ERROR" && "$level" != "WARN" ]]; then
    echo "Error: level must be ERROR or WARN." >&2
    show_help
    exit 1
fi

if [[ $# -gt 2 ]]; then
    if [[ $# -ne 4 || "$3" != "--top" || ! "$4" =~ ^[1-9][0-9]*$ ]]; then
        show_help
        exit 1
    fi
    top="$4"
fi

awk -v level="$level" '
    $3 == level {
        for (i = 1; i <= NF; i++) {
            if ($i ~ /^module=/) {
                module = $i
                sub(/^module=/, "", module)
                count[module]++
            }
        }
    }
    END {
        for (module in count) {
            printf "%s %d\n", module, count[module]
        }
    }
' "$directory"/*.log 2>/dev/null |
    sort -k2,2nr |
    {
        printf "%-15s %s\n" "MODULE" "COUNT"
        if [[ -n "$top" ]]; then
            head -n "$top"
        else
            cat
        fi
    }
