
import argparse
from collections import deque


def pid_key(pid):
    """Сортировка PID: P2 идёт раньше P10."""
    return int(pid[1:])


def load_processes(filename):
    processes = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            pid, arrival, burst, priority = line.split()

            processes.append({
                "pid": pid,
                "arrival": int(arrival),
                "burst": int(burst),
                "priority": int(priority),
            })

    return sorted(
        processes,
        key=lambda p: (p["arrival"], pid_key(p["pid"]))
    )


def simulate(processes, algorithm, **params):
    """Возвращает интервалы выполнения: (начало, конец, PID)."""
    if not processes:
        return []

    jobs = {
        p["pid"]: {
            **p,
            "remaining": p["burst"],
        }
        for p in processes
    }

    arrivals = sorted(
        processes,
        key=lambda p: (p["arrival"], pid_key(p["pid"]))
    )

    timeline = []
    time = 0
    completed = set()
    ready = deque()
    added = set()
    waiting_ticks = {p["pid"]: 0 for p in processes}
    current = None

    quantum = params.get("quantum", 3)
    aging_interval = params.get("aging_interval", 5)
    quantum_left = quantum

    def add_interval(start, end, pid):
        if start == end:
            return

        if timeline and timeline[-1][1] == start and timeline[-1][2] == pid:
            old = timeline[-1]
            timeline[-1] = (old[0], end, pid)
        else:
            timeline.append((start, end, pid))

    def add_arrivals(now):
        for p in arrivals:
            pid = p["pid"]
            if p["arrival"] <= now and pid not in added:
                ready.append(pid)
                added.add(pid)

    while len(completed) < len(processes):
        add_arrivals(time)

        available = [pid for pid in ready if pid not in completed]

        if algorithm == "rr":
            if current is None:
                if not available:
                    next_time = min(
                        p["arrival"] for p in arrivals
                        if p["pid"] not in added
                    )
                    add_interval(time, next_time, None)
                    time = next_time
                    continue

                current = ready.popleft()
                quantum_left = quantum

        elif algorithm in ("fcfs", "sjf"):
            if current is None:
                if not available:
                    next_time = min(
                        p["arrival"] for p in arrivals
                        if p["pid"] not in added
                    )
                    add_interval(time, next_time, None)
                    time = next_time
                    continue

                if algorithm == "fcfs":
                    current = ready.popleft()
                else:
                    current = min(
                        available,
                        key=lambda pid: (
                            jobs[pid]["burst"],
                            jobs[pid]["arrival"],
                            pid_key(pid),
                        ),
                    )
                    ready.remove(current)

        elif algorithm in ("srtf", "priority"):
            if not available:
                next_time = min(
                    p["arrival"] for p in arrivals
                    if p["pid"] not in added
                )
                add_interval(time, next_time, None)
                time = next_time
                current = None
                continue

            if current is not None and current in completed:
                current = None

            if current is None:
                if algorithm == "srtf":
                    current = min(
                        available,
                        key=lambda pid: (
                            jobs[pid]["remaining"],
                            jobs[pid]["arrival"],
                            pid_key(pid),
                        ),
                    )
                else:
                    current = min(
                        available,
                        key=lambda pid: (
                            max(
                                1,
                                jobs[pid]["priority"]
                                - waiting_ticks[pid] // aging_interval,
                            ) if params.get("aging", False)
                            else jobs[pid]["priority"],
                            jobs[pid]["arrival"],
                            pid_key(pid),
                        ),
                    )
            else:
                if algorithm == "srtf":
                    best = min(
                        available,
                        key=lambda pid: (
                            jobs[pid]["remaining"],
                            jobs[pid]["arrival"],
                            pid_key(pid),
                        ),
                    )
                    if jobs[best]["remaining"] < jobs[current]["remaining"]:
                        current = best
                else:
                    current_priority = (
                        max(
                            1,
                            jobs[current]["priority"]
                            - waiting_ticks[current] // aging_interval,
                        ) if params.get("aging", False)
                        else jobs[current]["priority"]
                    )
                    best_priority = min(
                        (
                            max(
                                1,
                                jobs[pid]["priority"]
                                - waiting_ticks[pid] // aging_interval,
                            ) if params.get("aging", False)
                            else jobs[pid]["priority"]
                        )
                        for pid in available
                    )
                    if best_priority < current_priority:
                        current = min(
                            (
                                pid for pid in available
                                if (
                                    max(
                                        1,
                                        jobs[pid]["priority"]
                                        - waiting_ticks[pid] // aging_interval,
                                    ) if params.get("aging", False)
                                    else jobs[pid]["priority"]
                                ) == best_priority
                            ),
                            key=lambda pid: (
                                jobs[pid]["arrival"],
                                pid_key(pid),
                            ),
                        )

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        # Execute one time unit.
        for pid in ready:
            if pid != current and pid not in completed:
                waiting_ticks[pid] += 1

        add_interval(time, time + 1, current)
        jobs[current]["remaining"] -= 1
        time += 1

        if algorithm == "rr":
            quantum_left -= 1

        if jobs[current]["remaining"] == 0:
            completed.add(current)
            current = None
        elif algorithm == "rr" and quantum_left == 0:
            # Add new arrivals before re-queueing the interrupted process.
            add_arrivals(time)
            ready.append(current)
            current = None

    return timeline


def calculate_metrics(processes, timeline):
    stats = {
        p["pid"]: {
            "arrival": p["arrival"],
            "burst": p["burst"],
            "first_start": None,
            "completion": None,
        }
        for p in processes
    }

    busy_time = 0

    for start, end, pid in timeline:
        if pid is None:
            continue

        busy_time += end - start
        item = stats[pid]

        if item["first_start"] is None:
            item["first_start"] = start

        item["completion"] = end

    waiting = []
    turnaround = []
    response = []

    for item in stats.values():
        turn = item["completion"] - item["arrival"]
        resp = item["first_start"] - item["arrival"]

        waiting.append(turn - item["burst"])
        turnaround.append(turn)
        response.append(resp)

    start_time = min(p["arrival"] for p in processes)
    end_time = max(item["completion"] for item in stats.values())
    total_time = end_time - start_time

    return {
        "avg_waiting": sum(waiting) / len(waiting),
        "avg_turnaround": sum(turnaround) / len(turnaround),
        "avg_response": sum(response) / len(response),
        "cpu_utilization": (
            busy_time / total_time * 100 if total_time else 0
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="CPU Scheduling Simulator"
    )
    parser.add_argument("file", help="Input process set, e.g. set1.txt")
    parser.add_argument(
        "--algo",
        choices=["fcfs", "sjf", "srtf", "priority", "rr"],
        required=True,
    )
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", action="store_true")
    parser.add_argument("--aging-interval", type=int, default=5)
    args = parser.parse_args()

    if args.quantum < 1 or args.aging_interval < 1:
        parser.error("Quantum and aging interval must be positive.")

    processes = load_processes(args.file)
    timeline = simulate(
        processes,
        args.algo,
        quantum=args.quantum,
        aging=args.aging,
        aging_interval=args.aging_interval,
    )
    metrics = calculate_metrics(processes, timeline)

    print(f"\nAlgorithm: {args.algo.upper()}")
    if args.algo == "rr":
        print(f"Quantum: {args.quantum}")
    if args.algo == "priority":
        print(f"Aging: {'ON' if args.aging else 'OFF'}")

    print("\nSchedule:")
    print(" -> ".join(
        f"{pid or 'IDLE'}[{start}-{end}]"
        for start, end, pid in timeline
    ))

    print("\nAverage metrics:")
    print(f"Waiting time:     {metrics['avg_waiting']:.2f}")
    print(f"Turnaround time:  {metrics['avg_turnaround']:.2f}")
    print(f"Response time:    {metrics['avg_response']:.2f}")
    print(f"CPU utilization:  {metrics['cpu_utilization']:.2f}%")


if __name__ == "__main__":
    main()
