
import matplotlib.pyplot as plt

from sched import load_processes, simulate, calculate_metrics


def count_context_switches(timeline):
    switches = 0
    previous_pid = None

    for start, end, pid in timeline:
        if pid is None:
            previous_pid = None
            continue

        if previous_pid is not None and pid != previous_pid:
            switches += 1

        previous_pid = pid

    return switches


processes = load_processes("set2.txt")

quantums = list(range(1, 11))
waiting_times = []
context_switches = []

print("Quantum | Avg waiting | Context switches")
print("------------------------------------------")

for quantum in quantums:
    timeline = simulate(
        processes,
        "rr",
        quantum=quantum
    )

    metrics = calculate_metrics(processes, timeline)
    switches = count_context_switches(timeline)

    waiting_times.append(metrics["avg_waiting"])
    context_switches.append(switches)

    print(
        f"{quantum:7} | "
        f"{metrics['avg_waiting']:11.2f} | "
        f"{switches:16}"
    )

fig, ax1 = plt.subplots()

ax1.plot(
    quantums,
    waiting_times,
    marker="o",
    label="Average waiting time"
)
ax1.set_xlabel("Quantum")
ax1.set_ylabel("Average waiting time")
ax1.set_xticks(quantums)
ax1.grid(True)

ax2 = ax1.twinx()
ax2.plot(
    quantums,
    context_switches,
    marker="s",
    label="Context switches"
)
ax2.set_ylabel("Context switches")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.title("Round Robin: Quantum vs Waiting Time and Context Switches")
plt.tight_layout()
plt.savefig("rr_quantum.png", dpi=150)
plt.show()

print("\nGraph saved as rr_quantum.png")
