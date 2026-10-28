
#!/usr/bin/env python3

import os
from pathlib import Path


def read_process(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        right = stat.rfind(")")
        fields = stat[right + 2:].split()

        state = fields[0]
        ppid = int(fields[1])

        status = Path(f"/proc/{pid}/status").read_text()
        rss = 0

        for line in status.splitlines():
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1])
                break

        return {
            "pid": pid,
            "ppid": ppid,
            "state": state,
            "rss": rss,
        }
    except (OSError, ValueError, IndexError):
        return None


def main():
    current_uid = os.getuid()
    processes = {}

    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue

        pid = int(entry.name)

        try:
            status = (entry / "status").read_text()
            uid_line = next(
                line for line in status.splitlines()
                if line.startswith("Uid:")
            )
            uid = int(uid_line.split()[1])

            if uid != current_uid:
                continue

            process = read_process(pid)
            if process:
                processes[pid] = process
        except (OSError, StopIteration, ValueError):
            continue

    children = {}

    for pid, process in processes.items():
        children.setdefault(process["ppid"], []).append(pid)

    for pids in children.values():
        pids.sort()

    def print_tree(pid, prefix="", last=True):
        process = processes[pid]
        branch = "└── " if last else "├── "

        print(
            f"{prefix}{branch if prefix else ''}"
            f"PID={pid} STATE={process['state']} "
            f"RSS={process['rss']} kB"
        )

        descendants = children.get(pid, [])
        new_prefix = prefix + ("    " if last else "│   ")

        for index, child_pid in enumerate(descendants):
            print_tree(
                child_pid,
                new_prefix,
                index == len(descendants) - 1,
            )

    roots = [
        pid for pid, process in processes.items()
        if process["ppid"] not in processes
    ]

    for root in sorted(roots):
        print_tree(root)


if __name__ == "__main__":
    main()
