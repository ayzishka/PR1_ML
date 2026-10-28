
#!/usr/bin/env python3

import os
import time


def main():
    child_pid = os.fork()

    if child_pid == 0:
        time.sleep(2)
        ppid = os.getppid()
        print(f"Дочерний процесс: PID={os.getpid()}, новый PPID={ppid}", flush=True)
        time.sleep(1)
        return

    print(f"Родительский процесс: PID={os.getpid()}", flush=True)
    print(f"Дочерний процесс: PID={child_pid}", flush=True)
    print("Родитель завершится раньше дочернего.", flush=True)
    os._exit(0)


if __name__ == "__main__":
    main()
