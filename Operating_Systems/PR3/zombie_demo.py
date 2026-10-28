
#!/usr/bin/env python3

import os
import time


def main():
    child_pid = os.fork()

    if child_pid == 0:
        print(f"Дочерний процесс PID={os.getpid()} завершился.", flush=True)
        os._exit(0)

    print(f"Родительский процесс PID={os.getpid()}", flush=True)
    print(f"Дочерний процесс PID={child_pid}", flush=True)
    time.sleep(1)

    status = open(f"/proc/{child_pid}/status", encoding="utf-8").read()
    state_line = next(
        (line for line in status.splitlines() if line.startswith("State:")),
        "State: неизвестно",
    )
    print(f"Состояние дочернего процесса: {state_line}", flush=True)
    print("Через 10 секунд родитель вызовет waitpid().", flush=True)

    time.sleep(10)
    os.waitpid(child_pid, 0)
    print("Дочерний процесс собран через waitpid(); zombie устранён.", flush=True)


if __name__ == "__main__":
    main()
